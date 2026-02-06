"""
SecureRedLab - Neural Vulnerability Scanner
اسکنر آسیب‌پذیری عصبی با استفاده از AI

این ماژول از مدل‌های Transformer و XGBoost برای:
- اسکن شبکه و شناسایی سرویس‌ها
- تشخیص آسیب‌پذیری‌ها با AI
- امتیازدهی CVSS خودکار
- پیش‌بینی احتمال موفقیت exploit
- پیشنهاد راهکارهای حمله

Legal Requirements:
- FBI Clearance
- IRB Ethics Committee Approval
- Local Police Department Authorization
- University Research Committee Approval

ONLY FOR ACADEMIC RESEARCH - تنها برای تحقیقات آکادمیک
"""

import os
import sys
import json
import time
import socket
import ipaddress
import subprocess
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import defaultdict

# Third-party imports (mock در حالت توسعه)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False

# Import core systems
from core.logging_system import get_logger, LogCategory
from core.exception_handler import (
    handle_exception, retry_on_failure, log_performance,
    NetworkException, AIException, ValidationException,
    ErrorSeverity, RecoveryStrategy
)
from core.config_manager import get_config
from core.database_manager import get_db_manager
from core.ai_output_validator import get_validator, ValidationType
# OFFLINE AI: استفاده از adapter بجای ai_core_engine (online)
from ai.scanner_ai_adapter import get_ai_engine, AIModelType


# ============================================================================
# Enums و Data Classes
# ============================================================================

class SeverityLevel(Enum):
    """سطح شدت آسیب‌پذیری"""
    CRITICAL = "CRITICAL"  # 9.0-10.0
    HIGH = "HIGH"          # 7.0-8.9
    MEDIUM = "MEDIUM"      # 4.0-6.9
    LOW = "LOW"            # 0.1-3.9
    INFO = "INFO"          # 0.0


class PortStatus(Enum):
    """وضعیت پورت"""
    OPEN = "open"
    CLOSED = "closed"
    FILTERED = "filtered"
    UNKNOWN = "unknown"


class VulnerabilityType(Enum):
    """نوع آسیب‌پذیری"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    CSRF = "csrf"
    RCE = "rce"                    # Remote Code Execution
    LFI = "lfi"                    # Local File Inclusion
    RFI = "rfi"                    # Remote File Inclusion
    AUTHENTICATION_BYPASS = "auth_bypass"
    PRIVILEGE_ESCALATION = "privilege_escalation"
    BUFFER_OVERFLOW = "buffer_overflow"
    DIRECTORY_TRAVERSAL = "directory_traversal"
    SSRF = "ssrf"                  # Server Side Request Forgery
    XXE = "xxe"                    # XML External Entity
    DESERIALIZATION = "deserialization"
    WEAK_CRYPTO = "weak_crypto"
    MISCONFIGURATION = "misconfiguration"


@dataclass
class Port:
    """اطلاعات پورت"""
    number: int
    protocol: str = "tcp"
    status: PortStatus = PortStatus.UNKNOWN
    service: Optional[str] = None
    version: Optional[str] = None
    banner: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            'number': self.number,
            'protocol': self.protocol,
            'status': self.status.value,
            'service': self.service,
            'version': self.version,
            'banner': self.banner
        }


@dataclass
class Vulnerability:
    """آسیب‌پذیری شناسایی شده"""
    # فیلدهای اجباری بدون default
    vuln_type: VulnerabilityType
    title: str
    description: str
    severity: SeverityLevel
    cvss_score: float
    target_ip: str
    
    # فیلدهای اختیاری با default
    vuln_id: str = field(default_factory=lambda: f"VULN-{int(time.time()*1000)}")
    target_port: Optional[int] = None
    service: Optional[str] = None
    cve_ids: List[str] = field(default_factory=list)
    exploit_available: bool = False
    exploit_probability: float = 0.0  # 0.0 - 1.0
    proof_of_concept: Optional[str] = None
    recommendations: List[str] = field(default_factory=list)
    detected_by: str = "neural_scanner"  # نام ماژول تشخیص‌دهنده
    ai_model_used: Optional[str] = None
    confidence: float = 0.0  # اطمینان AI
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            'vuln_id': self.vuln_id,
            'vuln_type': self.vuln_type.value,
            'title': self.title,
            'description': self.description,
            'severity': self.severity.value,
            'cvss_score': self.cvss_score,
            'target_ip': self.target_ip,
            'target_port': self.target_port,
            'service': self.service,
            'cve_ids': self.cve_ids,
            'exploit_available': self.exploit_available,
            'exploit_probability': self.exploit_probability,
            'proof_of_concept': self.proof_of_concept,
            'recommendations': self.recommendations,
            'detected_by': self.detected_by,
            'ai_model_used': self.ai_model_used,
            'confidence': self.confidence,
            'timestamp': self.timestamp.isoformat(),
            'metadata': self.metadata
        }


@dataclass
class ScanResult:
    """نتیجه اسکن"""
    # فیلد اجباری
    target: str  # IP یا دامنه
    
    # فیلدهای اختیاری با default
    scan_id: str = field(default_factory=lambda: f"SCAN-{int(time.time()*1000)}")
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    duration_seconds: float = 0.0
    is_alive: bool = False
    os_detection: Optional[str] = None
    open_ports: List[Port] = field(default_factory=list)
    vulnerabilities: List[Vulnerability] = field(default_factory=list)
    risk_score: float = 0.0  # 0.0 - 10.0
    total_vulns: int = 0
    critical_vulns: int = 0
    high_vulns: int = 0
    medium_vulns: int = 0
    low_vulns: int = 0
    scan_type: str = "neural_full_scan"
    ai_models_used: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def calculate_stats(self):
        """محاسبه آمار"""
        self.total_vulns = len(self.vulnerabilities)
        self.critical_vulns = sum(1 for v in self.vulnerabilities if v.severity == SeverityLevel.CRITICAL)
        self.high_vulns = sum(1 for v in self.vulnerabilities if v.severity == SeverityLevel.HIGH)
        self.medium_vulns = sum(1 for v in self.vulnerabilities if v.severity == SeverityLevel.MEDIUM)
        self.low_vulns = sum(1 for v in self.vulnerabilities if v.severity == SeverityLevel.LOW)
        
        # محاسبه risk score
        if self.vulnerabilities:
            self.risk_score = sum(v.cvss_score for v in self.vulnerabilities) / len(self.vulnerabilities)
        
        if self.end_time:
            self.duration_seconds = (self.end_time - self.start_time).total_seconds()
    
    def to_dict(self) -> Dict:
        return {
            'scan_id': self.scan_id,
            'target': self.target,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'duration_seconds': self.duration_seconds,
            'is_alive': self.is_alive,
            'os_detection': self.os_detection,
            'open_ports': [p.to_dict() for p in self.open_ports],
            'vulnerabilities': [v.to_dict() for v in self.vulnerabilities],
            'risk_score': self.risk_score,
            'total_vulns': self.total_vulns,
            'critical_vulns': self.critical_vulns,
            'high_vulns': self.high_vulns,
            'medium_vulns': self.medium_vulns,
            'low_vulns': self.low_vulns,
            'scan_type': self.scan_type,
            'ai_models_used': self.ai_models_used,
            'metadata': self.metadata
        }


# ============================================================================
# CVE Database Manager
# ============================================================================

class CVEDatabase:
    """
    مدیریت پایگاه داده CVE
    
    در محیط production، این کلاس به NVD (National Vulnerability Database)
    متصل می‌شود و CVE های واقعی را بارگذاری می‌کند.
    """
    
    def __init__(self):
        """سازنده"""
        self.logger = get_logger(__name__, LogCategory.NETWORK)
        self.config = get_config()
        
        # Mock CVE database برای توسعه
        self.cve_db = self._load_mock_cve_database()
        
        self.logger.info(
            f"CVE Database راه‌اندازی شد - {len(self.cve_db)} CVE",
            f"CVE Database initialized - {len(self.cve_db)} CVEs"
        )
    
    def _load_mock_cve_database(self) -> Dict[str, Dict]:
        """بارگذاری mock CVE database"""
        return {
            'CVE-2024-1234': {
                'title': 'Remote Code Execution in Apache HTTP Server',
                'cvss_score': 9.8,
                'severity': SeverityLevel.CRITICAL,
                'description': 'A critical RCE vulnerability in Apache HTTP Server 2.4.x',
                'affected_services': ['apache', 'httpd'],
                'affected_versions': ['2.4.0-2.4.49'],
                'exploit_available': True,
                'exploit_probability': 0.9
            },
            'CVE-2024-5678': {
                'title': 'SQL Injection in MySQL',
                'cvss_score': 8.5,
                'severity': SeverityLevel.HIGH,
                'description': 'SQL injection vulnerability in MySQL < 8.0.30',
                'affected_services': ['mysql'],
                'affected_versions': ['< 8.0.30'],
                'exploit_available': True,
                'exploit_probability': 0.8
            },
            'CVE-2024-9101': {
                'title': 'XSS in Nginx',
                'cvss_score': 6.5,
                'severity': SeverityLevel.MEDIUM,
                'description': 'Cross-site scripting in Nginx error pages',
                'affected_services': ['nginx'],
                'affected_versions': ['< 1.22.0'],
                'exploit_available': False,
                'exploit_probability': 0.4
            },
            'CVE-2024-1122': {
                'title': 'Authentication Bypass in SSH',
                'cvss_score': 9.1,
                'severity': SeverityLevel.CRITICAL,
                'description': 'Authentication bypass in OpenSSH < 9.0',
                'affected_services': ['ssh', 'openssh'],
                'affected_versions': ['< 9.0'],
                'exploit_available': True,
                'exploit_probability': 0.85
            }
        }
    
    def search_by_service(self, service: str, version: Optional[str] = None) -> List[Dict]:
        """جستجو CVE بر اساس سرویس"""
        results = []
        
        for cve_id, cve_data in self.cve_db.items():
            if service.lower() in [s.lower() for s in cve_data['affected_services']]:
                result = {'cve_id': cve_id, **cve_data}
                results.append(result)
        
        self.logger.debug(
            f"پیدا شد {len(results)} CVE برای سرویس {service}",
            f"Found {len(results)} CVEs for service {service}"
        )
        
        return results


# ============================================================================
# Port Scanner
# ============================================================================

class PortScanner:
    """
    اسکنر پورت با قابلیت تشخیص سرویس
    
    در محیط production، از nmap یا masscan استفاده می‌شود.
    در حالت توسعه، از socket استفاده می‌کنیم.
    """
    
    def __init__(self):
        """سازنده"""
        self.logger = get_logger(__name__, LogCategory.NETWORK)
        self.config = get_config()
        
        self.timeout = self.config.get('scanner.port_timeout', 1.0)
        self.max_threads = self.config.get('scanner.max_threads', 100)
        
        # پورت‌های رایج
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 3306, 3389, 
            5432, 5900, 8080, 8443, 27017, 6379
        ]
    
    @log_performance
    @retry_on_failure(max_retries=2, delay=0.5)
    def scan_port(self, ip: str, port: int) -> Port:
        """اسکن یک پورت"""
        port_obj = Port(number=port)
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            result = sock.connect_ex((ip, port))
            
            if result == 0:
                port_obj.status = PortStatus.OPEN
                
                # سعی در دریافت banner
                try:
                    banner = sock.recv(1024).decode('utf-8', errors='ignore').strip()
                    if banner:
                        port_obj.banner = banner[:200]  # محدود به 200 کاراکتر
                        port_obj.service = self._identify_service_from_banner(banner)
                except:
                    pass
                
                # تشخیص سرویس از روی پورت
                if not port_obj.service:
                    port_obj.service = self._identify_service_from_port(port)
            else:
                port_obj.status = PortStatus.CLOSED
            
            sock.close()
            
        except socket.timeout:
            port_obj.status = PortStatus.FILTERED
        except Exception as e:
            self.logger.debug(f"خطا در اسکن پورت {port}: {e}")
            port_obj.status = PortStatus.UNKNOWN
        
        return port_obj
    
    def _identify_service_from_banner(self, banner: str) -> Optional[str]:
        """تشخیص سرویس از banner"""
        banner_lower = banner.lower()
        
        service_indicators = {
            'ssh': 'ssh',
            'apache': 'apache',
            'nginx': 'nginx',
            'mysql': 'mysql',
            'postgresql': 'postgresql',
            'ftp': 'ftp',
            'smtp': 'smtp',
            'http': 'http'
        }
        
        for indicator, service in service_indicators.items():
            if indicator in banner_lower:
                return service
        
        return None
    
    def _identify_service_from_port(self, port: int) -> Optional[str]:
        """تشخیص سرویس از روی شماره پورت"""
        port_map = {
            21: 'ftp',
            22: 'ssh',
            23: 'telnet',
            25: 'smtp',
            53: 'dns',
            80: 'http',
            110: 'pop3',
            143: 'imap',
            443: 'https',
            445: 'smb',
            3306: 'mysql',
            3389: 'rdp',
            5432: 'postgresql',
            5900: 'vnc',
            6379: 'redis',
            8080: 'http-proxy',
            8443: 'https-alt',
            27017: 'mongodb'
        }
        
        return port_map.get(port)
    
    @log_performance
    def scan_target(self, target: str, ports: Optional[List[int]] = None) -> List[Port]:
        """
        اسکن تمام پورت‌های یک هدف
        
        Args:
            target: IP یا دامنه
            ports: لیست پورت‌ها (None = پورت‌های رایج)
        
        Returns:
            لیست پورت‌های باز
        """
        if ports is None:
            ports = self.common_ports
        
        self.logger.info(
            f"شروع اسکن {len(ports)} پورت برای {target}",
            f"Starting scan of {len(ports)} ports for {target}"
        )
        
        open_ports = []
        
        for port in ports:
            port_obj = self.scan_port(target, port)
            
            if port_obj.status == PortStatus.OPEN:
                open_ports.append(port_obj)
                self.logger.info(
                    f"پورت باز یافت شد: {port} ({port_obj.service})",
                    f"Open port found: {port} ({port_obj.service})"
                )
        
        self.logger.info(
            f"اسکن کامل شد: {len(open_ports)} پورت باز از {len(ports)}",
            f"Scan completed: {len(open_ports)} open ports out of {len(ports)}"
        )
        
        return open_ports


# ============================================================================
# Neural Vulnerability Detector
# ============================================================================

class NeuralVulnerabilityDetector:
    """
    تشخیص‌دهنده آسیب‌پذیری با استفاده از AI
    
    این کلاس از مدل‌های Transformer برای تحلیل سرویس‌ها
    و تشخیص آسیب‌پذیری‌های احتمالی استفاده می‌کند.
    """
    
    def __init__(self):
        """سازنده"""
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        self.ai_engine = get_ai_engine()
        self.validator = get_validator()
        self.cve_db = CVEDatabase()
    
    @log_performance
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.AI
    )
    def detect_vulnerabilities(self, 
                              target: str,
                              ports: List[Port]) -> List[Vulnerability]:
        """
        تشخیص آسیب‌پذیری‌ها با استفاده از AI
        
        Args:
            target: IP هدف
            ports: لیست پورت‌های باز
        
        Returns:
            لیست آسیب‌پذیری‌های یافت شده
        """
        self.logger.info(
            f"شروع تشخیص آسیب‌پذیری برای {target} با {len(ports)} پورت",
            f"Starting vulnerability detection for {target} with {len(ports)} ports"
        )
        
        vulnerabilities = []
        
        for port in ports:
            # تشخیص آسیب‌پذیری با CVE Database
            cve_vulns = self._detect_from_cve(target, port)
            vulnerabilities.extend(cve_vulns)
            
            # تشخیص آسیب‌پذیری با AI
            ai_vulns = self._detect_with_ai(target, port)
            vulnerabilities.extend(ai_vulns)
        
        self.logger.info(
            f"تشخیص کامل شد: {len(vulnerabilities)} آسیب‌پذیری یافت شد",
            f"Detection completed: {len(vulnerabilities)} vulnerabilities found"
        )
        
        return vulnerabilities
    
    def _detect_from_cve(self, target: str, port: Port) -> List[Vulnerability]:
        """تشخیص آسیب‌پذیری از CVE Database"""
        vulnerabilities = []
        
        if not port.service:
            return vulnerabilities
        
        # جستجو در CVE database
        cve_matches = self.cve_db.search_by_service(port.service, port.version)
        
        for cve in cve_matches:
            vuln = Vulnerability(
                vuln_type=self._map_cve_to_vuln_type(cve['title']),
                title=cve['title'],
                description=cve['description'],
                severity=cve['severity'],
                cvss_score=cve['cvss_score'],
                target_ip=target,
                target_port=port.number,
                service=port.service,
                cve_ids=[cve['cve_id']],
                exploit_available=cve['exploit_available'],
                exploit_probability=cve['exploit_probability'],
                detected_by='cve_database',
                confidence=0.95  # اطمینان بالا برای CVE های شناخته شده
            )
            
            # اضافه کردن توصیه‌ها
            vuln.recommendations = self._generate_recommendations(vuln)
            
            vulnerabilities.append(vuln)
            
            self.logger.audit(
                "VULN_DETECTED_CVE",
                f"آسیب‌پذیری CVE یافت شد: {cve['cve_id']}",
                f"CVE vulnerability detected: {cve['cve_id']}",
                context={'target': target, 'port': port.number, 'cve': cve['cve_id']}
            )
        
        return vulnerabilities
    
    @log_performance
    def _detect_with_ai(self, target: str, port: Port) -> List[Vulnerability]:
        """تشخیص آسیب‌پذیری با مدل AI"""
        vulnerabilities = []
        
        if not port.service:
            return vulnerabilities
        
        # ساخت prompt برای AI
        prompt = self._create_detection_prompt(target, port)
        
        try:
            # استفاده از AI برای تحلیل
            ai_response = self.ai_engine.model_manager.generate(
                prompt=prompt,
                model_type=AIModelType.QWEN_14B,  # Qwen برای تحلیل آسیب‌پذیری
                validate_output=True
            )
            
            if ai_response['status'] != 'success':
                self.logger.warning(
                    f"AI تحلیل ناموفق بود برای {port.service}:{port.number}",
                    f"AI analysis failed for {port.service}:{port.number}"
                )
                return vulnerabilities
            
            # پارس کردن خروجی AI
            ai_output = ai_response['output']
            detected_vulns = self._parse_ai_output(ai_output, target, port)
            
            # اضافه کردن metadata
            for vuln in detected_vulns:
                vuln.ai_model_used = ai_response['model_type']
                vuln.detected_by = 'neural_ai'
                vuln.confidence = ai_response.get('validation', {}).get('confidence_score', 0.5)
            
            vulnerabilities.extend(detected_vulns)
            
            self.logger.info(
                f"AI {len(detected_vulns)} آسیب‌پذیری تشخیص داد",
                f"AI detected {len(detected_vulns)} vulnerabilities"
            )
            
        except Exception as e:
            self.logger.error(
                f"خطا در تشخیص با AI: {e}",
                f"Error in AI detection: {e}"
            )
        
        return vulnerabilities
    
    def _create_detection_prompt(self, target: str, port: Port) -> str:
        """ساخت prompt برای مدل AI"""
        prompt = f"""Analyze the following service for potential vulnerabilities:

Target: {target}
Port: {port.number}
Service: {port.service}
Version: {port.version or 'Unknown'}
Banner: {port.banner or 'Not available'}

Provide a security analysis including:
1. Potential vulnerability types
2. CVSS score estimation (0-10)
3. Exploit probability (0-1)
4. Recommended security measures

Format your response as JSON with the following structure:
{{
    "vulnerabilities": [
        {{
            "type": "vulnerability_type",
            "title": "Vulnerability Title",
            "description": "Detailed description",
            "cvss_score": 0.0,
            "severity": "CRITICAL/HIGH/MEDIUM/LOW",
            "exploit_probability": 0.0,
            "recommendations": ["recommendation1", "recommendation2"]
        }}
    ]
}}"""
        
        return prompt
    
    def _parse_ai_output(self, ai_output: str, target: str, port: Port) -> List[Vulnerability]:
        """پارس کردن خروجی AI"""
        vulnerabilities = []
        
        try:
            # استخراج JSON از خروجی
            # در خروجی واقعی، AI ممکنه JSON رو در markdown code block بده
            if '```json' in ai_output:
                json_start = ai_output.find('```json') + 7
                json_end = ai_output.find('```', json_start)
                json_str = ai_output[json_start:json_end].strip()
            elif '```' in ai_output:
                json_start = ai_output.find('```') + 3
                json_end = ai_output.find('```', json_start)
                json_str = ai_output[json_start:json_end].strip()
            else:
                json_str = ai_output
            
            data = json.loads(json_str)
            
            for vuln_data in data.get('vulnerabilities', []):
                vuln = Vulnerability(
                    vuln_type=self._map_string_to_vuln_type(vuln_data.get('type', 'misconfiguration')),
                    title=vuln_data.get('title', 'Unknown Vulnerability'),
                    description=vuln_data.get('description', ''),
                    severity=self._map_string_to_severity(vuln_data.get('severity', 'MEDIUM')),
                    cvss_score=float(vuln_data.get('cvss_score', 5.0)),
                    target_ip=target,
                    target_port=port.number,
                    service=port.service,
                    exploit_probability=float(vuln_data.get('exploit_probability', 0.5)),
                    recommendations=vuln_data.get('recommendations', [])
                )
                
                vulnerabilities.append(vuln)
        
        except Exception as e:
            self.logger.warning(
                f"خطا در پارس JSON خروجی AI: {e}",
                f"Error parsing AI JSON output: {e}"
            )
            
            # اگر پارس JSON ناموفق بود، یک آسیب‌پذیری عمومی ایجاد کن
            vuln = Vulnerability(
                vuln_type=VulnerabilityType.MISCONFIGURATION,
                title=f"Potential Security Issue in {port.service}",
                description=f"AI analysis suggests potential security concerns for {port.service} on port {port.number}",
                severity=SeverityLevel.MEDIUM,
                cvss_score=5.0,
                target_ip=target,
                target_port=port.number,
                service=port.service,
                exploit_probability=0.5,
                recommendations=['Manual security review recommended']
            )
            vulnerabilities.append(vuln)
        
        return vulnerabilities
    
    def _map_cve_to_vuln_type(self, title: str) -> VulnerabilityType:
        """تبدیل عنوان CVE به نوع آسیب‌پذیری"""
        title_lower = title.lower()
        
        if 'rce' in title_lower or 'remote code' in title_lower:
            return VulnerabilityType.RCE
        elif 'sql' in title_lower:
            return VulnerabilityType.SQL_INJECTION
        elif 'xss' in title_lower or 'cross-site' in title_lower:
            return VulnerabilityType.XSS
        elif 'auth' in title_lower:
            return VulnerabilityType.AUTHENTICATION_BYPASS
        elif 'privilege' in title_lower:
            return VulnerabilityType.PRIVILEGE_ESCALATION
        else:
            return VulnerabilityType.MISCONFIGURATION
    
    def _map_string_to_vuln_type(self, type_str: str) -> VulnerabilityType:
        """تبدیل string به VulnerabilityType"""
        try:
            return VulnerabilityType(type_str.lower())
        except ValueError:
            return VulnerabilityType.MISCONFIGURATION
    
    def _map_string_to_severity(self, severity_str: str) -> SeverityLevel:
        """تبدیل string به SeverityLevel"""
        try:
            return SeverityLevel(severity_str.upper())
        except ValueError:
            return SeverityLevel.MEDIUM
    
    def _generate_recommendations(self, vuln: Vulnerability) -> List[str]:
        """تولید توصیه‌های امنیتی"""
        recommendations = []
        
        if vuln.vuln_type == VulnerabilityType.RCE:
            recommendations.extend([
                "Apply latest security patches immediately",
                "Implement input validation and sanitization",
                "Use Web Application Firewall (WAF)",
                "Enable security monitoring and logging"
            ])
        elif vuln.vuln_type == VulnerabilityType.SQL_INJECTION:
            recommendations.extend([
                "Use parameterized queries/prepared statements",
                "Implement input validation",
                "Apply principle of least privilege for database accounts",
                "Enable SQL injection detection in WAF"
            ])
        elif vuln.vuln_type == VulnerabilityType.AUTHENTICATION_BYPASS:
            recommendations.extend([
                "Update authentication mechanism immediately",
                "Implement multi-factor authentication (MFA)",
                "Review and strengthen password policies",
                "Enable account lockout after failed attempts"
            ])
        else:
            recommendations.extend([
                f"Update {vuln.service} to latest version",
                "Review security configuration",
                "Enable security logging",
                "Conduct security audit"
            ])
        
        return recommendations


# ============================================================================
# Neural Vulnerability Scanner - Main Class
# ============================================================================

class NeuralVulnerabilityScanner:
    """
    اسکنر آسیب‌پذیری عصبی - کلاس اصلی
    
    این کلاس تمام قابلیت‌های اسکن را یکپارچه می‌کند:
    - اسکن پورت
    - تشخیص سرویس
    - تشخیص آسیب‌پذیری با AI
    - امتیازدهی CVSS
    - ذخیره نتایج
    """
    
    _instance = None
    _lock = __import__('threading').Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """سازنده"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.logger = get_logger(__name__, LogCategory.NETWORK)
        self.config = get_config()
        
        self.port_scanner = PortScanner()
        self.vuln_detector = NeuralVulnerabilityDetector()
        self.db_manager = get_db_manager()
        
        self._create_tables()
        self._initialized = True
        
        self.logger.audit(
            "NEURAL_SCANNER_INIT",
            "اسکنر آسیب‌پذیری عصبی راه‌اندازی شد",
            "Neural Vulnerability Scanner initialized"
        )
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.DATABASE
    )
    def _create_tables(self):
        """ساخت جداول پایگاه داده"""
        # جدول نتایج اسکن
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS scan_results (
                scan_id TEXT PRIMARY KEY,
                target TEXT NOT NULL,
                start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                end_time TIMESTAMP,
                duration_seconds REAL,
                is_alive BOOLEAN DEFAULT FALSE,
                os_detection TEXT,
                risk_score REAL DEFAULT 0.0,
                total_vulns INTEGER DEFAULT 0,
                critical_vulns INTEGER DEFAULT 0,
                high_vulns INTEGER DEFAULT 0,
                medium_vulns INTEGER DEFAULT 0,
                low_vulns INTEGER DEFAULT 0,
                scan_type TEXT,
                ai_models_used TEXT,
                metadata TEXT
            )
        """, fetch=False)
        
        # جدول آسیب‌پذیری‌ها
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                vuln_id TEXT PRIMARY KEY,
                scan_id TEXT NOT NULL,
                vuln_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                severity TEXT NOT NULL,
                cvss_score REAL NOT NULL,
                target_ip TEXT NOT NULL,
                target_port INTEGER,
                service TEXT,
                cve_ids TEXT,
                exploit_available BOOLEAN DEFAULT FALSE,
                exploit_probability REAL DEFAULT 0.0,
                detected_by TEXT,
                ai_model_used TEXT,
                confidence REAL DEFAULT 0.0,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (scan_id) REFERENCES scan_results(scan_id)
            )
        """, fetch=False)
        
        self.logger.info(
            "جداول پایگاه داده ایجاد شد",
            "Database tables created"
        )
    
    @log_performance
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.NETWORK
    )
    def scan_target(self, 
                   target: str,
                   ports: Optional[List[int]] = None,
                   detect_os: bool = True,
                   use_ai: bool = True) -> ScanResult:
        """
        اسکن کامل یک هدف
        
        Args:
            target: IP یا دامنه
            ports: لیست پورت‌ها (None = پورت‌های رایج)
            detect_os: تشخیص سیستم‌عامل
            use_ai: استفاده از AI برای تشخیص آسیب‌پذیری
        
        Returns:
            نتیجه اسکن
        """
        self.logger.audit(
            "SCAN_START",
            f"شروع اسکن هدف: {target}",
            f"Starting scan of target: {target}",
            context={'target': target, 'use_ai': use_ai}
        )
        
        scan_result = ScanResult(target=target)
        
        try:
            # مرحله 1: بررسی زنده بودن هدف
            scan_result.is_alive = self._check_alive(target)
            
            if not scan_result.is_alive:
                self.logger.warning(
                    f"هدف {target} پاسخ نمی‌دهد",
                    f"Target {target} is not responding"
                )
                scan_result.end_time = datetime.now()
                scan_result.calculate_stats()
                return scan_result
            
            # مرحله 2: اسکن پورت
            open_ports = self.port_scanner.scan_target(target, ports)
            scan_result.open_ports = open_ports
            
            # مرحله 3: تشخیص OS (mock)
            if detect_os:
                scan_result.os_detection = self._detect_os(target, open_ports)
            
            # مرحله 4: تشخیص آسیب‌پذیری
            if use_ai and open_ports:
                vulnerabilities = self.vuln_detector.detect_vulnerabilities(target, open_ports)
                scan_result.vulnerabilities = vulnerabilities
                scan_result.ai_models_used.append('qwen_14b')
            
            # مرحله 5: محاسبه آمار
            scan_result.end_time = datetime.now()
            scan_result.calculate_stats()
            
            # مرحله 6: ذخیره در پایگاه داده
            self._save_scan_result(scan_result)
            
            self.logger.audit(
                "SCAN_COMPLETE",
                f"اسکن کامل شد: {target} - {scan_result.total_vulns} آسیب‌پذیری",
                f"Scan completed: {target} - {scan_result.total_vulns} vulnerabilities",
                context=scan_result.to_dict()
            )
            
        except Exception as e:
            self.logger.error(
                f"خطا در اسکن {target}: {e}",
                f"Error scanning {target}: {e}"
            )
            scan_result.end_time = datetime.now()
            scan_result.metadata['error'] = str(e)
        
        return scan_result
    
    def _check_alive(self, target: str) -> bool:
        """بررسی زنده بودن هدف"""
        try:
            # سعی در اتصال به پورت 80 یا 443
            for port in [80, 443]:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2.0)
                    result = sock.connect_ex((target, port))
                    sock.close()
                    
                    if result == 0:
                        return True
                except:
                    continue
            
            # اگر هیچ پورتی جواب نداد
            return False
            
        except Exception as e:
            self.logger.debug(f"خطا در بررسی alive: {e}")
            return False
    
    def _detect_os(self, target: str, ports: List[Port]) -> Optional[str]:
        """تشخیص سیستم‌عامل (mock)"""
        # در production از nmap -O استفاده می‌شود
        # در حالت توسعه، حدس ساده می‌زنیم
        
        port_numbers = [p.number for p in ports]
        
        if 3389 in port_numbers:  # RDP
            return "Windows"
        elif 22 in port_numbers:  # SSH
            return "Linux/Unix"
        elif 445 in port_numbers:  # SMB
            return "Windows"
        else:
            return "Unknown"
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.DATABASE
    )
    def _save_scan_result(self, scan_result: ScanResult):
        """ذخیره نتیجه اسکن در پایگاه داده"""
        # ذخیره scan result
        self.db_manager.execute("""
            INSERT INTO scan_results (
                scan_id, target, start_time, end_time, duration_seconds,
                is_alive, os_detection, risk_score, total_vulns,
                critical_vulns, high_vulns, medium_vulns, low_vulns,
                scan_type, ai_models_used, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            scan_result.scan_id,
            scan_result.target,
            scan_result.start_time.isoformat(),
            scan_result.end_time.isoformat() if scan_result.end_time else None,
            scan_result.duration_seconds,
            scan_result.is_alive,
            scan_result.os_detection,
            scan_result.risk_score,
            scan_result.total_vulns,
            scan_result.critical_vulns,
            scan_result.high_vulns,
            scan_result.medium_vulns,
            scan_result.low_vulns,
            scan_result.scan_type,
            json.dumps(scan_result.ai_models_used),
            json.dumps(scan_result.metadata)
        ), fetch=False)
        
        # ذخیره vulnerabilities
        for vuln in scan_result.vulnerabilities:
            self.db_manager.execute("""
                INSERT INTO vulnerabilities (
                    vuln_id, scan_id, vuln_type, title, description,
                    severity, cvss_score, target_ip, target_port,
                    service, cve_ids, exploit_available, exploit_probability,
                    detected_by, ai_model_used, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                vuln.vuln_id,
                scan_result.scan_id,
                vuln.vuln_type.value,
                vuln.title,
                vuln.description,
                vuln.severity.value,
                vuln.cvss_score,
                vuln.target_ip,
                vuln.target_port,
                vuln.service,
                json.dumps(vuln.cve_ids),
                vuln.exploit_available,
                vuln.exploit_probability,
                vuln.detected_by,
                vuln.ai_model_used,
                vuln.confidence
            ), fetch=False)
        
        self.logger.info(
            f"نتیجه اسکن ذخیره شد: {scan_result.scan_id}",
            f"Scan result saved: {scan_result.scan_id}"
        )
    
    def get_scan_history(self, target: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """دریافت تاریخچه اسکن"""
        query = "SELECT * FROM scan_results"
        params = []
        
        if target:
            query += " WHERE target = ?"
            params.append(target)
        
        query += " ORDER BY start_time DESC LIMIT ?"
        params.append(limit)
        
        rows = self.db_manager.execute(query, tuple(params))
        
        results = []
        for row in rows:
            results.append({
                'scan_id': row[0],
                'target': row[1],
                'start_time': row[2],
                'total_vulns': row[8],
                'risk_score': row[7]
            })
        
        return results


# ============================================================================
# Global Singleton Function
# ============================================================================

_scanner_instance = None

def get_scanner() -> NeuralVulnerabilityScanner:
    """دریافت instance اسکنر (Singleton)"""
    global _scanner_instance
    if _scanner_instance is None:
        _scanner_instance = NeuralVulnerabilityScanner()
    return _scanner_instance


# ============================================================================
# Main - برای تست
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SecureRedLab - Neural Vulnerability Scanner Test")
    print("اسکنر آسیب‌پذیری عصبی - تست")
    print("=" * 70)
    
    scanner = get_scanner()
    
    # تست اسکن
    result = scanner.scan_target(
        target="192.168.1.100",
        use_ai=True
    )
    
    print(f"\n✅ اسکن کامل شد:")
    print(f"   - Target: {result.target}")
    print(f"   - Open Ports: {len(result.open_ports)}")
    print(f"   - Vulnerabilities: {result.total_vulns}")
    print(f"   - Risk Score: {result.risk_score:.2f}")
    
    print("\n" + "=" * 70)
    print("✅ Neural Vulnerability Scanner آماده است!")
    print("=" * 70)
