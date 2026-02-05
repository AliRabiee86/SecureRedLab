"""
SecureRedLab - AI Intelligence Core
هسته مرکزی هوش مصنوعی

این ماژول قلب AI-First SecureRedLab است که:
1. ترکیب VLM + LLM برای تحلیل multimodal
2. تولید payload های هوشمند
3. انتخاب بهترین exploitation strategy
4. یادگیری از نتایج قبلی (RL integration)
5. WAF bypass techniques با AI

Architecture inspired by:
- PwnGPT (ACL 2025)
- PentestGPT (USENIX Security 2024)
- AutoPenGPT (2025)

Legal Warning:
فقط برای تحقیقات آکادمیک با مجوزهای FBI, IRB, Police
"""

import os
import sys
import json
import time
import base64
import hashlib
import threading
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import asyncio

# Core imports - fix import path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))
sys.path.insert(0, str(backend_dir.parent))  # Add SecureRedLab root

try:
    from core.logging_system import get_logger, LogCategory
    from core.exception_handler import (
        handle_exception,
        retry_on_failure,
        log_performance,
        AIException,
        ErrorSeverity,
        RecoveryStrategy
    )
except ImportError:
    # Fallback for testing without full environment
    print("⚠️  Core modules not available - using minimal fallback")
    
    class LogCategory:
        AI = "ai"
        SYSTEM = "system"
    
    def get_logger(category):
        import logging
        logging.basicConfig(level=logging.INFO)
        return logging.getLogger(f"SecureRedLab.{category}")
    
    def handle_exception(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def retry_on_failure(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    def log_performance(*args, **kwargs):
        def decorator(func):
            return func
        return decorator
    
    class AIException(Exception):
        pass
    
    class ErrorSeverity:
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"
        CRITICAL = "critical"
    
    class RecoveryStrategy:
        LOG = "log"
        RETRY = "retry"
        FALLBACK = "fallback"

# AI SDK imports
try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    print("⚠️  httpx not available - AI calls will fail")

# ==============================================================================
# Enums & Data Classes
# ==============================================================================

class AIModelType(Enum):
    """انواع مدل‌های AI"""
    # VLM Models (Vision-Language) - Online + Offline
    QWEN_2_5_VL = "qwen_2_5_vl_72b"           # Best VLM - Alibaba [ONLINE]
    GEMINI_2_FLASH = "gemini_2_0_flash"        # Fast multimodal - Google [ONLINE]
    CLAUDE_3_5_SONNET = "claude_3_5_sonnet"    # Code expert - Anthropic [ONLINE]
    GPT_4_VISION = "gpt_4_vision"              # General VLM - OpenAI [ONLINE]
    LLAVA_1_6_34B = "llava_1_6_34b"            # Open-source VLM 34B [OFFLINE]
    LLAVA_1_6_13B = "llava_1_6_13b"            # Open-source VLM 13B [OFFLINE]
    
    # LLM Models (Text-only) - Online + Offline
    GLM_4_6 = "glm_4_6"                        # Best value - BigModel [ONLINE] ⭐ RE-ADDED!
    DEEPSEEK_CODER_V2 = "deepseek_coder_v2"    # Code specialist - DeepSeek [ONLINE]
    QWEN_2_5_72B = "qwen_2_5_72b"              # General LLM - Alibaba [ONLINE]
    MIXTRAL_8x22B = "mixtral_8x22b"            # MoE model - Mistral [ONLINE]
    LLAMA_3_1_70B = "llama_3_1_70b"            # Open-source 70B [OFFLINE]
    LLAMA_3_1_8B = "llama_3_1_8b"              # Open-source 8B [OFFLINE]


class AnalysisType(Enum):
    """نوع تحلیل"""
    VISUAL_ONLY = "visual"          # فقط تصویر (VLM)
    TEXT_ONLY = "text"              # فقط متن (LLM)
    MULTIMODAL = "multimodal"       # ترکیب (VLM + LLM)
    CODE_ANALYSIS = "code"          # تحلیل کد
    PAYLOAD_GEN = "payload"         # تولید payload
    EVASION_GEN = "evasion"         # تولید evasion


class VulnerabilityType(Enum):
    """انواع آسیب‌پذیری (15 نوع)"""
    SQL_INJECTION = "sql_injection"
    XSS = "xss"
    COMMAND_INJECTION = "command_injection"
    FILE_UPLOAD = "file_upload"
    PATH_TRAVERSAL = "path_traversal"
    SSRF = "ssrf"
    XXE = "xxe"
    DESERIALIZATION = "deserialization"
    AUTH_BYPASS = "auth_bypass"
    BUSINESS_LOGIC = "business_logic"
    INFO_DISCLOSURE = "info_disclosure"
    ACCESS_CONTROL = "access_control"
    RACE_CONDITION = "race_condition"
    API_EXPLOIT = "api_exploit"
    ZERO_DAY = "zero_day"


@dataclass
class AIAnalysisRequest:
    """درخواست تحلیل AI"""
    analysis_type: AnalysisType
    target_url: Optional[str] = None
    target_screenshot: Optional[str] = None  # Base64 encoded
    source_code: Optional[str] = None
    vulnerability_type: Optional[VulnerabilityType] = None
    context: Dict[str, Any] = field(default_factory=dict)
    use_rl: bool = True  # استفاده از RL برای بهبود
    model_preference: Optional[AIModelType] = None


@dataclass
class AIAnalysisResult:
    """نتیجه تحلیل AI"""
    request_id: str
    analysis_type: AnalysisType
    model_used: AIModelType
    confidence: float  # 0.0 - 1.0
    
    # Vulnerability Analysis
    vulnerabilities_found: List[Dict[str, Any]] = field(default_factory=list)
    
    # Exploitation Strategy
    recommended_exploits: List[str] = field(default_factory=list)
    exploitation_steps: List[str] = field(default_factory=list)
    
    # Payload Generation
    generated_payloads: List[str] = field(default_factory=list)
    payload_variations: int = 0
    
    # Evasion Techniques
    waf_detected: bool = False
    evasion_techniques: List[str] = field(default_factory=list)
    
    # Metadata
    processing_time: float = 0.0
    tokens_used: int = 0
    raw_response: str = ""
    timestamp: float = field(default_factory=time.time)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "request_id": self.request_id,
            "analysis_type": self.analysis_type.value,
            "model_used": self.model_used.value,
            "confidence": self.confidence,
            "vulnerabilities_found": self.vulnerabilities_found,
            "recommended_exploits": self.recommended_exploits,
            "exploitation_steps": self.exploitation_steps,
            "generated_payloads": self.generated_payloads,
            "payload_variations": self.payload_variations,
            "waf_detected": self.waf_detected,
            "evasion_techniques": self.evasion_techniques,
            "processing_time": self.processing_time,
            "tokens_used": self.tokens_used,
            "timestamp": self.timestamp
        }


# ==============================================================================
# AI Intelligence Core Class
# ==============================================================================

class AIIntelligenceCore:
    """
    هسته مرکزی هوش مصنوعی SecureRedLab
    
    این کلاس مسئول است برای:
    1. مدیریت چندین مدل AI (VLM + LLM)
    2. تحلیل multimodal (تصویر + متن + کد)
    3. تولید payload های هوشمند
    4. انتخاب بهترین exploitation strategy
    5. یادگیری از نتایج قبلی
    
    Based on PwnGPT architecture:
    VAM → ESG → PCM → EEE → RL Feedback
    """
    
    def __init__(
        self,
        api_keys: Dict[str, str],
        default_vlm: AIModelType = AIModelType.QWEN_2_5_VL,
        default_llm: AIModelType = AIModelType.GLM_4_6,  # ⭐ CHANGED to GLM-4.6!
        enable_rl: bool = True
    ):
        """
        Initialize AI Intelligence Core
        
        Args:
            api_keys: Dictionary of API keys for different models
            default_vlm: Default VLM model
            default_llm: Default LLM model
            enable_rl: Enable Reinforcement Learning integration
        """
        self.api_keys = api_keys
        self.default_vlm = default_vlm
        self.default_llm = default_llm
        self.enable_rl = enable_rl
        
        self.logger = get_logger(LogCategory.AI)
        self._lock = threading.Lock()
        self._request_counter = 0
        
        # Model endpoints (این URLها باید در config باشند)
        self.model_endpoints = {
            # VLM Models (Online)
            AIModelType.QWEN_2_5_VL: "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            AIModelType.GEMINI_2_FLASH: "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            AIModelType.CLAUDE_3_5_SONNET: "https://api.anthropic.com/v1/messages",
            AIModelType.GPT_4_VISION: "https://api.openai.com/v1/chat/completions",
            
            # VLM Models (Offline) - No endpoint, local Ollama
            AIModelType.LLAVA_1_6_34B: "http://localhost:11434/api/generate",  # Ollama
            AIModelType.LLAVA_1_6_13B: "http://localhost:11434/api/generate",  # Ollama
            
            # LLM Models (Online)
            AIModelType.GLM_4_6: "https://open.bigmodel.cn/api/paas/v4/chat/completions",  # ⭐ RE-ADDED!
            AIModelType.DEEPSEEK_CODER_V2: "https://api.deepseek.com/v1/chat/completions",
            AIModelType.QWEN_2_5_72B: "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            AIModelType.MIXTRAL_8x22B: "https://api.mistral.ai/v1/chat/completions",
            
            # LLM Models (Offline) - Local Ollama
            AIModelType.LLAMA_3_1_70B: "http://localhost:11434/api/generate",  # Ollama
            AIModelType.LLAMA_3_1_8B: "http://localhost:11434/api/generate"    # Ollama
        }
        
        self.logger.info("🤖 AI Intelligence Core initialized")
        self.logger.info(f"   Default VLM: {default_vlm.value} (Vision-Language)")
        self.logger.info(f"   Default LLM: {default_llm.value} (Text-only)")
        self.logger.info(f"   Total Models: {len(self.model_endpoints)} (VLM: 6, LLM: 6)")
        self.logger.info(f"   Online Models: 8, Offline Models: 4")
        self.logger.info(f"   RL Enabled: {enable_rl}")
        self.logger.info("   ⭐ GLM-4.6 RE-ADDED: 93.9% AIME, 8x cheaper than Claude!")
    
    def _generate_request_id(self) -> str:
        """Generate unique request ID"""
        with self._lock:
            self._request_counter += 1
            timestamp = int(time.time() * 1000)
            return f"ai_req_{timestamp}_{self._request_counter}"
    
    @log_performance(category="ai")
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        fallback_value=None
    )
    async def analyze(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        """
        تحلیل هوشمند با AI
        
        این متد مرکزی تمام انواع تحلیل را handle می‌کند:
        - Visual analysis (VLM)
        - Code analysis (LLM)
        - Multimodal analysis (VLM + LLM)
        - Payload generation
        - Evasion techniques
        
        Args:
            request: درخواست تحلیل
            
        Returns:
            نتیجه تحلیل
        """
        request_id = self._generate_request_id()
        start_time = time.time()
        
        self.logger.info(f"🔍 Starting AI analysis: {request_id}")
        self.logger.info(f"   Type: {request.analysis_type.value}")
        
        # انتخاب مدل مناسب
        model = self._select_model(request)
        self.logger.info(f"   Model: {model.value}")
        
        try:
            # اجرای تحلیل بر اساس نوع
            if request.analysis_type == AnalysisType.VISUAL_ONLY:
                result = await self._analyze_visual(request, model)
            elif request.analysis_type == AnalysisType.TEXT_ONLY:
                result = await self._analyze_text(request, model)
            elif request.analysis_type == AnalysisType.MULTIMODAL:
                result = await self._analyze_multimodal(request, model)
            elif request.analysis_type == AnalysisType.CODE_ANALYSIS:
                result = await self._analyze_code(request, model)
            elif request.analysis_type == AnalysisType.PAYLOAD_GEN:
                result = await self._generate_payload(request, model)
            elif request.analysis_type == AnalysisType.EVASION_GEN:
                result = await self._generate_evasion(request, model)
            else:
                raise AIException(
                    f"Unknown analysis type: {request.analysis_type}",
                    persian_message=f"نوع تحلیل ناشناخته: {request.analysis_type}"
                )
            
            # اضافه کردن metadata
            result.request_id = request_id
            result.model_used = model
            result.processing_time = time.time() - start_time
            
            self.logger.info(f"✅ AI analysis completed: {request_id} ({result.processing_time:.2f}s)")
            self.logger.info(f"   Confidence: {result.confidence:.2%}")
            self.logger.info(f"   Vulnerabilities: {len(result.vulnerabilities_found)}")
            
            # RL Feedback (اگر فعال باشد)
            if self.enable_rl and request.use_rl:
                await self._send_rl_feedback(request, result)
            
            return result
            
        except Exception as e:
            self.logger.error(f"❌ AI analysis failed: {str(e)}", exc_info=True)
            raise AIException(
                f"AI analysis failed: {str(e)}",
                persian_message=f"تحلیل AI ناموفق بود: {str(e)}",
                context={"request_id": request_id, "analysis_type": request.analysis_type.value}
            )
    
    def _select_model(self, request: AIAnalysisRequest) -> AIModelType:
        """
        انتخاب بهترین مدل بر اساس نوع تحلیل
        
        Strategy:
        - Visual → VLM (Qwen2.5-VL یا Gemini 2.0 Flash)
        - Code → LLM Code Specialist (DeepSeek Coder یا Claude 3.5)
        - Multimodal → Best VLM (Qwen2.5-VL)
        - Payload → LLM با تخصص exploit (DeepSeek یا Mixtral)
        """
        if request.model_preference:
            return request.model_preference
        
        if request.analysis_type == AnalysisType.VISUAL_ONLY:
            return self.default_vlm
        elif request.analysis_type == AnalysisType.CODE_ANALYSIS:
            return AIModelType.CLAUDE_3_5_SONNET  # Best برای code (92% HumanEval)
        elif request.analysis_type == AnalysisType.MULTIMODAL:
            return AIModelType.QWEN_2_5_VL  # Best VLM (86.5% MMLU)
        elif request.analysis_type in [AnalysisType.PAYLOAD_GEN, AnalysisType.EVASION_GEN]:
            # GLM-4.6 بهترین value است: 93.9% AIME، 8x ارزان‌تر از Claude
            return AIModelType.GLM_4_6  # ⭐ CHANGED! Best value برای exploit generation
        else:
            return AIModelType.GLM_4_6  # ⭐ DEFAULT به GLM تغییر کرد
    
    async def _analyze_visual(
        self,
        request: AIAnalysisRequest,
        model: AIModelType
    ) -> AIAnalysisResult:
        """
        تحلیل بصری با VLM
        
        Use cases:
        - تحلیل screenshots از target application
        - شناسایی UI-based vulnerabilities (XSS, Clickjacking)
        - OCR برای استخراج sensitive info
        - تشخیص WAF/security headers از visual indicators
        """
        self.logger.info("🖼️  Visual analysis with VLM...")
        
        if not request.target_screenshot:
            raise AIException("Screenshot is required for visual analysis")
        
        # ساخت prompt برای VLM
        prompt = self._build_visual_analysis_prompt(request)
        
        # TODO: Call actual VLM API
        # For now, return mock result
        return self._mock_visual_analysis(request)
    
    async def _analyze_text(
        self,
        request: AIAnalysisRequest,
        model: AIModelType
    ) -> AIAnalysisResult:
        """
        تحلیل متنی با LLM
        
        Use cases:
        - تحلیل response headers
        - تحلیل error messages
        - fingerprinting از textual clues
        """
        self.logger.info("📝 Text analysis with LLM...")
        
        # TODO: Implement actual LLM call
        return self._mock_text_analysis(request)
    
    async def _analyze_multimodal(
        self,
        request: AIAnalysisRequest,
        model: AIModelType
    ) -> AIAnalysisResult:
        """
        تحلیل multimodal (Visual + Text + Code)
        
        این قدرتمندترین mode است که:
        1. Screenshot را با VLM تحلیل می‌کند
        2. Source code را با LLM تحلیل می‌کند
        3. نتایج را ترکیب می‌کند (Fusion)
        4. Exploitation strategy comprehensive ایجاد می‌کند
        """
        self.logger.info("🔀 Multimodal analysis (VLM + LLM)...")
        
        # TODO: Implement actual multimodal fusion
        return self._mock_multimodal_analysis(request)
    
    async def _analyze_code(
        self,
        request: AIAnalysisRequest,
        model: AIModelType
    ) -> AIAnalysisResult:
        """
        تحلیل کد با LLM متخصص
        
        Use cases:
        - Static code analysis
        - شناسایی SQL Injection, Command Injection, etc.
        - پیدا کردن logic flaws
        - Security misconfigurations
        """
        self.logger.info("💻 Code analysis...")
        
        if not request.source_code:
            raise AIException("Source code is required for code analysis")
        
        # TODO: Implement با Claude 3.5 Sonnet یا DeepSeek Coder
        return self._mock_code_analysis(request)
    
    async def _generate_payload(
        self,
        request: AIAnalysisRequest,
        model: AIModelType
    ) -> AIAnalysisResult:
        """
        تولید payload های هوشمند با AI
        
        Features:
        - Polymorphic payloads (تولید variations زیاد)
        - Context-aware (بر اساس target fingerprint)
        - Evasion-ready (با bypass techniques)
        - RL-optimized (بر اساس تجربیات قبلی)
        """
        self.logger.info("🎯 Payload generation...")
        
        if not request.vulnerability_type:
            raise AIException("Vulnerability type is required for payload generation")
        
        # TODO: Implement actual payload generation
        return self._mock_payload_generation(request)
    
    async def _generate_evasion(
        self,
        request: AIAnalysisRequest,
        model: AIModelType
    ) -> AIAnalysisResult:
        """
        تولید evasion techniques با AI
        
        Features:
        - WAF bypass techniques
        - IDS/IPS evasion
        - Encoding variations
        - Timing attack optimization
        """
        self.logger.info("🥷 Evasion technique generation...")
        
        # TODO: Implement actual evasion generation
        return self._mock_evasion_generation(request)
    
    def _build_visual_analysis_prompt(self, request: AIAnalysisRequest) -> str:
        """ساخت prompt برای VLM"""
        base_prompt = """You are an expert penetration tester analyzing a web application screenshot.

Your task:
1. Identify potential vulnerabilities visible in the UI
2. Detect security indicators (HTTPS, CSP headers, etc.)
3. Find sensitive information exposure
4. Identify WAF/security controls
5. Suggest exploitation strategies

Be thorough and explain your reasoning."""
        
        if request.vulnerability_type:
            base_prompt += f"\n\nFocus on: {request.vulnerability_type.value}"
        
        return base_prompt
    
    async def _send_rl_feedback(
        self,
        request: AIAnalysisRequest,
        result: AIAnalysisResult
    ):
        """ارسال feedback به RL Engine برای یادگیری"""
        self.logger.info("🔄 Sending feedback to RL Engine...")
        # TODO: Integration با RL Engine
        pass
    
    # ==============================================================================
    # Mock Methods (برای تست بدون API های واقعی)
    # ==============================================================================
    
    def _mock_visual_analysis(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        """Mock visual analysis"""
        return AIAnalysisResult(
            request_id="",
            analysis_type=request.analysis_type,
            model_used=self.default_vlm,
            confidence=0.85,
            vulnerabilities_found=[
                {
                    "type": "xss",
                    "location": "search input field",
                    "severity": "high",
                    "evidence": "No input sanitization detected visually"
                }
            ],
            recommended_exploits=["reflected_xss", "stored_xss"],
            exploitation_steps=[
                "Identify input fields",
                "Test with basic XSS payloads",
                "Bypass filters if present",
                "Execute proof-of-concept"
            ],
            waf_detected=False,
            raw_response="[MOCK VLM] Visual analysis completed"
        )
    
    def _mock_text_analysis(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        """Mock text analysis"""
        return AIAnalysisResult(
            request_id="",
            analysis_type=request.analysis_type,
            model_used=self.default_llm,
            confidence=0.90,
            vulnerabilities_found=[],
            recommended_exploits=[],
            raw_response="[MOCK LLM] Text analysis completed"
        )
    
    def _mock_multimodal_analysis(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        """Mock multimodal analysis"""
        return AIAnalysisResult(
            request_id="",
            analysis_type=request.analysis_type,
            model_used=AIModelType.QWEN_2_5_VL,
            confidence=0.92,
            vulnerabilities_found=[
                {
                    "type": "sql_injection",
                    "location": "login form",
                    "severity": "critical"
                }
            ],
            recommended_exploits=["union_based_sqli", "boolean_based_sqli"],
            generated_payloads=["' OR '1'='1", "admin'--", "1' UNION SELECT NULL--"],
            payload_variations=3,
            raw_response="[MOCK MULTIMODAL] Analysis completed"
        )
    
    def _mock_code_analysis(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        """Mock code analysis"""
        return AIAnalysisResult(
            request_id="",
            analysis_type=request.analysis_type,
            model_used=AIModelType.CLAUDE_3_5_SONNET,
            confidence=0.95,
            vulnerabilities_found=[
                {
                    "type": "command_injection",
                    "location": "line 42",
                    "code": "os.system(user_input)",
                    "severity": "critical"
                }
            ],
            exploitation_steps=[
                "Identify command execution point",
                "Test with command injection payloads",
                "Escalate to RCE"
            ],
            raw_response="[MOCK CODE] Analysis completed"
        )
    
    def _mock_payload_generation(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        """Mock payload generation"""
        vuln_type = request.vulnerability_type.value if request.vulnerability_type else "generic"
        
        # تولید payloads بر اساس نوع آسیب‌پذیری
        payloads = {
            "sql_injection": [
                "' OR '1'='1",
                "admin'--",
                "1' UNION SELECT NULL,NULL,NULL--",
                "' AND SLEEP(5)--"
            ],
            "xss": [
                "<script>alert(1)</script>",
                "<img src=x onerror=alert(1)>",
                "javascript:alert(1)",
                "<svg/onload=alert(1)>"
            ],
            "command_injection": [
                "; ls -la",
                "| whoami",
                "`id`",
                "$(cat /etc/passwd)"
            ]
        }
        
        return AIAnalysisResult(
            request_id="",
            analysis_type=request.analysis_type,
            model_used=AIModelType.GLM_4_6,  # ⭐ CHANGED to GLM-4.6!
            confidence=0.94,  # GLM-4.6 has 93.9% AIME score!
            generated_payloads=payloads.get(vuln_type, ["[MOCK] Generic payload"]),
            payload_variations=len(payloads.get(vuln_type, [])),
            raw_response=f"[MOCK GLM-4.6] Generated {len(payloads.get(vuln_type, []))} payloads for {vuln_type} (8x cheaper than Claude!)"
        )
    
    def _mock_evasion_generation(self, request: AIAnalysisRequest) -> AIAnalysisResult:
        """Mock evasion generation"""
        return AIAnalysisResult(
            request_id="",
            analysis_type=request.analysis_type,
            model_used=AIModelType.GLM_4_6,  # ⭐ CHANGED to GLM-4.6!
            confidence=0.92,  # GLM-4.6 is excellent for this!
            waf_detected=True,
            evasion_techniques=[
                "URL encoding variations",
                "Case manipulation",
                "Comment injection",
                "Whitespace obfuscation",
                "Double encoding"
            ],
            raw_response="[MOCK GLM-4.6] Generated 5 evasion techniques (Best value model!)"
        )


# ==============================================================================
# Singleton Instance
# ==============================================================================

_ai_core_instance: Optional[AIIntelligenceCore] = None
_ai_core_lock = threading.Lock()


def get_ai_intelligence_core(
    api_keys: Optional[Dict[str, str]] = None,
    **kwargs
) -> AIIntelligenceCore:
    """
    Get singleton instance of AI Intelligence Core
    
    Args:
        api_keys: API keys for AI models (optional)
        **kwargs: Additional configuration
        
    Returns:
        AIIntelligenceCore instance
    """
    global _ai_core_instance
    
    if _ai_core_instance is None:
        with _ai_core_lock:
            if _ai_core_instance is None:
                if api_keys is None:
                    # Load از environment variables
                    api_keys = {
                        "qwen": os.getenv("QWEN_API_KEY", ""),
                        "gemini": os.getenv("GEMINI_API_KEY", ""),
                        "claude": os.getenv("CLAUDE_API_KEY", ""),
                        "openai": os.getenv("OPENAI_API_KEY", ""),
                        "deepseek": os.getenv("DEEPSEEK_API_KEY", ""),
                        "mistral": os.getenv("MISTRAL_API_KEY", "")
                    }
                
                _ai_core_instance = AIIntelligenceCore(api_keys=api_keys, **kwargs)
    
    return _ai_core_instance


# ==============================================================================
# Test - فقط برای development
# ==============================================================================

if __name__ == "__main__":
    import asyncio
    
    print("=" * 80)
    print("Testing AI Intelligence Core")
    print("=" * 80)
    
    async def test_ai_core():
        # Initialize
        ai_core = get_ai_intelligence_core()
        
        # Test 1: Visual Analysis
        print("\n1. Testing Visual Analysis (VLM)...")
        visual_request = AIAnalysisRequest(
            analysis_type=AnalysisType.VISUAL_ONLY,
            target_screenshot="base64_encoded_screenshot_here",
            vulnerability_type=VulnerabilityType.XSS
        )
        result = await ai_core.analyze(visual_request)
        print(f"✅ Confidence: {result.confidence:.2%}")
        print(f"   Vulnerabilities: {len(result.vulnerabilities_found)}")
        
        # Test 2: Code Analysis
        print("\n2. Testing Code Analysis (LLM)...")
        code_request = AIAnalysisRequest(
            analysis_type=AnalysisType.CODE_ANALYSIS,
            source_code="os.system(request.GET['cmd'])",
            vulnerability_type=VulnerabilityType.COMMAND_INJECTION
        )
        result = await ai_core.analyze(code_request)
        print(f"✅ Confidence: {result.confidence:.2%}")
        print(f"   Vulnerabilities: {len(result.vulnerabilities_found)}")
        
        # Test 3: Payload Generation
        print("\n3. Testing Payload Generation...")
        payload_request = AIAnalysisRequest(
            analysis_type=AnalysisType.PAYLOAD_GEN,
            vulnerability_type=VulnerabilityType.SQL_INJECTION
        )
        result = await ai_core.analyze(payload_request)
        print(f"✅ Generated {result.payload_variations} payload variations")
        print(f"   Payloads: {result.generated_payloads[:3]}")
        
        # Test 4: Evasion Generation
        print("\n4. Testing Evasion Generation...")
        evasion_request = AIAnalysisRequest(
            analysis_type=AnalysisType.EVASION_GEN,
            context={"waf_type": "Cloudflare"}
        )
        result = await ai_core.analyze(evasion_request)
        print(f"✅ Generated {len(result.evasion_techniques)} evasion techniques")
        print(f"   Techniques: {result.evasion_techniques[:3]}")
    
    asyncio.run(test_ai_core())
    print("\n✅ All AI tests completed!")
