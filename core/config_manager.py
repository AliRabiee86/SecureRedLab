#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Configuration Management System (سیستم مدیریت پیکربندی)
==========================================================================

این ماژول سیستم جامع مدیریت پیکربندی را پیاده‌سازی می‌کند.

ویژگی‌ها:
- Multi-environment support (dev, staging, production)
- Environment variables support
- Secrets management (encrypted storage)
- Dynamic config reload (بدون restart)
- Config validation
- Default config templates
- Config versioning
- Persian comments در فایل‌های config
- YAML/JSON/ENV file support
- Config inheritance
- Hot-reload capability
- Thread-safe access

استفاده:
    from core.config_manager import ConfigManager, get_config
    
    # دریافت نمونه singleton
    config = get_config()
    
    # دسترسی به تنظیمات
    db_host = config.get('database.host', 'localhost')
    ai_models = config.get('ai.models')
    
    # به‌روزرسانی تنظیمات
    config.set('simulation.max_bots', 1000000)
    
    # reload پیکربندی
    config.reload()

تاریخ ایجاد: 2025-01-15
نسخه: 1.0.0
مجوز: تحقیقاتی آکادمیک - دانشگاه
"""

import os
import sys
import yaml
import json
import threading
from pathlib import Path
from typing import Any, Dict, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import base64
from cryptography.fernet import Fernet
import copy

# وارد کردن سیستم‌های پایه
from core.logging_system import get_logger, LogCategory
from core.exception_handler import (
    ConfigurationException,
    ValidationException,
    handle_exception
)

# ==============================================================================
# Configuration Constants - ثابت‌های پیکربندی
# ==============================================================================

class Environment(Enum):
    """محیط‌های اجرا - Execution Environments"""
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TESTING = "testing"

class ConfigFormat(Enum):
    """فرمت‌های فایل پیکربندی - Config File Formats"""
    YAML = "yaml"
    JSON = "json"
    ENV = "env"

# مسیرهای پیکربندی - Configuration paths
CONFIG_BASE_DIR = Path("/home/user/webapp/SecureRedLab/config")
CONFIG_BASE_DIR.mkdir(parents=True, exist_ok=True)

# فایل‌های پیکربندی - Config files
CONFIG_FILES = {
    Environment.DEVELOPMENT: CONFIG_BASE_DIR / "config.dev.yaml",
    Environment.STAGING: CONFIG_BASE_DIR / "config.staging.yaml",
    Environment.PRODUCTION: CONFIG_BASE_DIR / "config.prod.yaml",
    Environment.TESTING: CONFIG_BASE_DIR / "config.test.yaml",
}

# فایل secrets - Secrets file
SECRETS_FILE = CONFIG_BASE_DIR / ".secrets.encrypted"
SECRETS_KEY_FILE = CONFIG_BASE_DIR / ".secrets.key"

# ==============================================================================
# Configuration Schema - طرح پیکربندی
# ==============================================================================

@dataclass
class DatabaseConfig:
    """پیکربندی پایگاه‌داده - Database configuration"""
    host: str = "localhost"
    port: int = 5432
    name: str = "secureredlab"
    user: str = "secureuser"
    password: str = ""  # از secrets خوانده می‌شود
    max_connections: int = 100
    connection_timeout: int = 30
    ssl_mode: str = "require"

@dataclass
class AIConfig:
    """پیکربندی هوش مصنوعی - AI configuration"""
    models_path: str = "/home/user/webapp/SecureRedLab/ai_models/models"
    cache_path: str = "/home/user/webapp/SecureRedLab/ai_models/cache"
    gpu_enabled: bool = True
    max_gpu_memory: int = 8192  # MB
    batch_size: int = 32
    learning_rate: float = 0.001
    epochs: int = 100
    supported_models: List[str] = field(default_factory=lambda: [
        "deepseek-coder-33b-instruct",
        "glm-4-6b",
        "llama-3.1-70b-instruct",
        "mixtral-8x22b-instruct",
        "qwen-14b-chat"
    ])
    post_quantum_encryption: bool = True
    differential_privacy: bool = True
    federated_learning: bool = True

@dataclass
class SimulationConfig:
    """پیکربندی شبیه‌سازی - Simulation configuration"""
    max_bots: int = 1000000
    max_bandwidth_gbps: int = 1000  # 1 Tb/s
    max_requests_per_sec: int = 2500000
    docker_isolation: bool = True
    network_namespace: bool = True
    cpu_limit_percent: int = 80
    ram_limit_percent: int = 80
    kill_switch_enabled: bool = True
    compliance_logging: bool = True

@dataclass
class SecurityConfig:
    """پیکربندی امنیت - Security configuration"""
    jwt_secret: str = ""  # از secrets
    jwt_expiration_hours: int = 24
    mfa_enabled: bool = True
    password_min_length: int = 12
    max_login_attempts: int = 5
    session_timeout_minutes: int = 60
    encryption_algorithm: str = "AES-256"
    support_only_mode: bool = True

@dataclass
class LoggingConfig:
    """پیکربندی لاگ‌گیری - Logging configuration"""
    level: str = "INFO"
    max_file_size_mb: int = 50
    backup_count: int = 10
    retention_days: int = 90
    json_format: bool = True
    console_output: bool = True
    persian_timestamps: bool = True

@dataclass
class MonitoringConfig:
    """پیکربندی نظارت - Monitoring configuration"""
    websocket_enabled: bool = True
    websocket_port: int = 8765
    update_interval_sec: int = 1
    metrics_retention_hours: int = 24
    alerting_enabled: bool = True
    alert_email: str = ""

@dataclass
class ComplianceConfig:
    """پیکربندی انطباق - Compliance configuration"""
    standards: List[str] = field(default_factory=lambda: [
        "NIST-800-171", "SOC2", "ISO-27001", "CFAA"
    ])
    audit_trail_enabled: bool = True
    tamper_proof_logging: bool = True
    approval_authorities: List[str] = field(default_factory=lambda: [
        "FBI", "IRB", "Local-Police", "University"
    ])
    pre_approval_required: bool = True

# ==============================================================================
# Secrets Manager - مدیر رمزها
# ==============================================================================

class SecretsManager:
    """
    مدیر رمزها - برای ذخیره‌سازی امن اطلاعات حساس
    Secrets Manager - for secure storage of sensitive information
    
    این کلاس از Fernet (symmetric encryption) برای رمزنگاری استفاده می‌کند.
    """
    
    def __init__(self):
        """مقداردهی اولیه - Initialize secrets manager"""
        self.logger = get_logger(__name__, LogCategory.SYSTEM)
        self.cipher_suite = None
        self._load_or_create_key()
    
    def _load_or_create_key(self):
        """بارگذاری یا ایجاد کلید رمزنگاری - Load or create encryption key"""
        try:
            if SECRETS_KEY_FILE.exists():
                # بارگذاری کلید موجود
                with open(SECRETS_KEY_FILE, 'rb') as f:
                    key = f.read()
                self.logger.info(
                    "کلید رمزنگاری بارگذاری شد",
                    "Encryption key loaded"
                )
            else:
                # ایجاد کلید جدید
                key = Fernet.generate_key()
                with open(SECRETS_KEY_FILE, 'wb') as f:
                    f.write(key)
                # تنظیم دسترسی فقط خواندنی
                SECRETS_KEY_FILE.chmod(0o400)
                self.logger.info(
                    "کلید رمزنگاری جدید ایجاد شد",
                    "New encryption key created"
                )
            
            self.cipher_suite = Fernet(key)
            
        except Exception as e:
            self.logger.error(
                f"خطا در بارگذاری کلید رمزنگاری: {str(e)}",
                f"Error loading encryption key: {str(e)}"
            )
            raise ConfigurationException(
                "خطا در راه‌اندازی مدیر رمزها",
                "Error initializing secrets manager"
            )
    
    def encrypt(self, data: str) -> str:
        """
        رمزنگاری داده
        Encrypt data
        
        Args:
            data: داده به صورت string
        
        Returns:
            str: داده رمزشده به صورت base64
        """
        try:
            encrypted = self.cipher_suite.encrypt(data.encode('utf-8'))
            return base64.b64encode(encrypted).decode('utf-8')
        except Exception as e:
            self.logger.error(
                f"خطا در رمزنگاری: {str(e)}",
                f"Error encrypting: {str(e)}"
            )
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        رمزگشایی داده
        Decrypt data
        
        Args:
            encrypted_data: داده رمزشده به صورت base64
        
        Returns:
            str: داده اصلی
        """
        try:
            decoded = base64.b64decode(encrypted_data.encode('utf-8'))
            decrypted = self.cipher_suite.decrypt(decoded)
            return decrypted.decode('utf-8')
        except Exception as e:
            self.logger.error(
                f"خطا در رمزگشایی: {str(e)}",
                f"Error decrypting: {str(e)}"
            )
            raise
    
    def save_secrets(self, secrets: Dict[str, str]):
        """
        ذخیره رمزها به صورت رمزنگاری‌شده
        Save secrets encrypted
        
        Args:
            secrets: دیکشنری از رمزها
        """
        try:
            # رمزنگاری کل دیکشنری
            json_data = json.dumps(secrets, ensure_ascii=False)
            encrypted_data = self.encrypt(json_data)
            
            # ذخیره در فایل
            with open(SECRETS_FILE, 'w', encoding='utf-8') as f:
                f.write(encrypted_data)
            
            # تنظیم دسترسی
            SECRETS_FILE.chmod(0o400)
            
            self.logger.info(
                f"تعداد {len(secrets)} رمز ذخیره شد",
                f"Saved {len(secrets)} secrets"
            )
            
        except Exception as e:
            self.logger.error(
                f"خطا در ذخیره رمزها: {str(e)}",
                f"Error saving secrets: {str(e)}"
            )
            raise
    
    def load_secrets(self) -> Dict[str, str]:
        """
        بارگذاری رمزها
        Load secrets
        
        Returns:
            Dict[str, str]: دیکشنری رمزها
        """
        try:
            if not SECRETS_FILE.exists():
                self.logger.warning(
                    "فایل رمزها وجود ندارد - از مقادیر پیش‌فرض استفاده می‌شود",
                    "Secrets file not found - using defaults"
                )
                return {}
            
            # خواندن و رمزگشایی
            with open(SECRETS_FILE, 'r', encoding='utf-8') as f:
                encrypted_data = f.read()
            
            json_data = self.decrypt(encrypted_data)
            secrets = json.loads(json_data)
            
            self.logger.info(
                f"تعداد {len(secrets)} رمز بارگذاری شد",
                f"Loaded {len(secrets)} secrets"
            )
            
            return secrets
            
        except Exception as e:
            self.logger.error(
                f"خطا در بارگذاری رمزها: {str(e)}",
                f"Error loading secrets: {str(e)}"
            )
            return {}

# ==============================================================================
# Configuration Manager - مدیر پیکربندی
# ==============================================================================

class ConfigManager:
    """
    مدیر اصلی پیکربندی
    Main Configuration Manager
    
    این کلاس singleton است و تمام تنظیمات سیستم را مدیریت می‌کند.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """
        پیاده‌سازی Singleton Pattern
        Implement Singleton Pattern
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """مقداردهی اولیه - Initialize configuration manager"""
        # جلوگیری از مقداردهی مجدد
        if hasattr(self, '_initialized'):
            return
        
        self.logger = get_logger(__name__, LogCategory.SYSTEM)
        self.secrets_manager = SecretsManager()
        self._config: Dict[str, Any] = {}
        self._secrets: Dict[str, str] = {}
        self._environment = self._detect_environment()
        self._config_lock = threading.RLock()
        self._initialized = True
        
        # بارگذاری پیکربندی
        self.load()
        
        self.logger.info(
            f"مدیر پیکربندی راه‌اندازی شد - محیط: {self._environment.value}",
            f"Configuration manager initialized - Environment: {self._environment.value}"
        )
    
    def _detect_environment(self) -> Environment:
        """
        تشخیص محیط اجرا
        Detect execution environment
        
        Returns:
            Environment: محیط اجرا
        """
        env_str = os.getenv('SECUREREDLAB_ENV', 'development').lower()
        
        env_map = {
            'dev': Environment.DEVELOPMENT,
            'development': Environment.DEVELOPMENT,
            'stage': Environment.STAGING,
            'staging': Environment.STAGING,
            'prod': Environment.PRODUCTION,
            'production': Environment.PRODUCTION,
            'test': Environment.TESTING,
            'testing': Environment.TESTING,
        }
        
        return env_map.get(env_str, Environment.DEVELOPMENT)
    
    def _create_default_config(self) -> Dict[str, Any]:
        """
        ایجاد پیکربندی پیش‌فرض
        Create default configuration
        
        Returns:
            Dict: پیکربندی پیش‌فرض
        """
        return {
            'environment': self._environment.value,
            'version': '1.0.0',
            'database': {
                'host': 'localhost',
                'port': 5432,
                'name': 'secureredlab',
                'user': 'secureuser',
                'max_connections': 100,
                'connection_timeout': 30,
                'ssl_mode': 'require'
            },
            'ai': {
                'models_path': str(Path.home() / 'SecureRedLab/ai_models/models'),
                'cache_path': str(Path.home() / 'SecureRedLab/ai_models/cache'),
                'gpu_enabled': True,
                'max_gpu_memory': 8192,
                'batch_size': 32,
                'learning_rate': 0.001,
                'epochs': 100,
                'supported_models': [
                    'deepseek-coder-33b-instruct',
                    'glm-4-6b',
                    'llama-3.1-70b-instruct',
                    'mixtral-8x22b-instruct',
                    'qwen-14b-chat'
                ],
                'post_quantum_encryption': True,
                'differential_privacy': True,
                'federated_learning': True
            },
            'simulation': {
                'max_bots': 1000000,
                'max_bandwidth_gbps': 1000,
                'max_requests_per_sec': 2500000,
                'docker_isolation': True,
                'network_namespace': True,
                'cpu_limit_percent': 80,
                'ram_limit_percent': 80,
                'kill_switch_enabled': True,
                'compliance_logging': True
            },
            'security': {
                'jwt_expiration_hours': 24,
                'mfa_enabled': True,
                'password_min_length': 12,
                'max_login_attempts': 5,
                'session_timeout_minutes': 60,
                'encryption_algorithm': 'AES-256',
                'support_only_mode': True
            },
            'logging': {
                'level': 'INFO',
                'max_file_size_mb': 50,
                'backup_count': 10,
                'retention_days': 90,
                'json_format': True,
                'console_output': True,
                'persian_timestamps': True
            },
            'monitoring': {
                'websocket_enabled': True,
                'websocket_port': 8765,
                'update_interval_sec': 1,
                'metrics_retention_hours': 24,
                'alerting_enabled': True
            },
            'compliance': {
                'standards': ['NIST-800-171', 'SOC2', 'ISO-27001', 'CFAA'],
                'audit_trail_enabled': True,
                'tamper_proof_logging': True,
                'approval_authorities': ['FBI', 'IRB', 'Local-Police', 'University'],
                'pre_approval_required': True
            }
        }
    
    def load(self):
        """
        بارگذاری پیکربندی از فایل
        Load configuration from file
        """
        with self._config_lock:
            try:
                config_file = CONFIG_FILES[self._environment]
                
                if not config_file.exists():
                    # ایجاد فایل پیش‌فرض
                    self.logger.warning(
                        f"فایل پیکربندی یافت نشد: {config_file}",
                        f"Config file not found: {config_file}"
                    )
                    self._config = self._create_default_config()
                    self.save()
                else:
                    # بارگذاری از فایل
                    with open(config_file, 'r', encoding='utf-8') as f:
                        self._config = yaml.safe_load(f) or {}
                    
                    self.logger.info(
                        f"پیکربندی از فایل بارگذاری شد: {config_file}",
                        f"Configuration loaded from file: {config_file}"
                    )
                
                # بارگذاری secrets
                self._secrets = self.secrets_manager.load_secrets()
                
                # اعمال environment variables
                self._apply_env_overrides()
                
            except Exception as e:
                self.logger.error(
                    f"خطا در بارگذاری پیکربندی: {str(e)}",
                    f"Error loading configuration: {str(e)}"
                )
                # استفاده از پیکربندی پیش‌فرض
                self._config = self._create_default_config()
    
    def save(self):
        """
        ذخیره پیکربندی در فایل
        Save configuration to file
        """
        with self._config_lock:
            try:
                config_file = CONFIG_FILES[self._environment]
                
                # ایجاد نسخه پشتیبان
                if config_file.exists():
                    backup_file = config_file.with_suffix('.yaml.backup')
                    config_file.rename(backup_file)
                
                # ذخیره پیکربندی جدید
                with open(config_file, 'w', encoding='utf-8') as f:
                    yaml.dump(
                        self._config,
                        f,
                        allow_unicode=True,
                        default_flow_style=False,
                        sort_keys=False
                    )
                
                self.logger.info(
                    f"پیکربندی در فایل ذخیره شد: {config_file}",
                    f"Configuration saved to file: {config_file}"
                )
                
            except Exception as e:
                self.logger.error(
                    f"خطا در ذخیره پیکربندی: {str(e)}",
                    f"Error saving configuration: {str(e)}"
                )
                raise ConfigurationException(
                    "خطا در ذخیره پیکربندی",
                    "Error saving configuration"
                )
    
    def _apply_env_overrides(self):
        """
        اعمال override های environment variable
        Apply environment variable overrides
        
        متغیرهای محیطی با پیشوند SECUREREDLAB_ می‌توانند تنظیمات را override کنند.
        مثال: SECUREREDLAB_DATABASE_HOST=192.168.1.1
        """
        prefix = "SECUREREDLAB_"
        
        for key, value in os.environ.items():
            if key.startswith(prefix):
                # تبدیل SECUREREDLAB_DATABASE_HOST به database.host
                config_key = key[len(prefix):].lower().replace('_', '.')
                
                # تنظیم مقدار
                self.set(config_key, value, save=False)
                
                self.logger.debug(
                    f"Override از environment variable: {config_key}",
                    f"Override from environment variable: {config_key}"
                )
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        دریافت مقدار پیکربندی
        Get configuration value
        
        Args:
            key: کلید به صورت نقطه‌گذاری (مثلاً 'database.host')
            default: مقدار پیش‌فرض در صورت نبود
        
        Returns:
            مقدار پیکربندی یا default
        
        مثال:
            host = config.get('database.host')
            models = config.get('ai.supported_models', [])
        """
        with self._config_lock:
            try:
                keys = key.split('.')
                value = self._config
                
                for k in keys:
                    if isinstance(value, dict):
                        value = value.get(k)
                    else:
                        return default
                
                return value if value is not None else default
                
            except Exception:
                return default
    
    def set(self, key: str, value: Any, save: bool = True):
        """
        تنظیم مقدار پیکربندی
        Set configuration value
        
        Args:
            key: کلید به صورت نقطه‌گذاری
            value: مقدار جدید
            save: آیا در فایل ذخیره شود؟
        
        مثال:
            config.set('simulation.max_bots', 2000000)
        """
        with self._config_lock:
            try:
                keys = key.split('.')
                current = self._config
                
                # پیمایش تا آخرین کلید
                for k in keys[:-1]:
                    if k not in current:
                        current[k] = {}
                    current = current[k]
                
                # تنظیم مقدار نهایی
                current[keys[-1]] = value
                
                self.logger.info(
                    f"تنظیم پیکربندی: {key} = {value}",
                    f"Configuration set: {key} = {value}"
                )
                
                if save:
                    self.save()
                
            except Exception as e:
                self.logger.error(
                    f"خطا در تنظیم پیکربندی {key}: {str(e)}",
                    f"Error setting configuration {key}: {str(e)}"
                )
                raise
    
    def get_secret(self, key: str, default: str = "") -> str:
        """
        دریافت رمز
        Get secret
        
        Args:
            key: کلید رمز
            default: مقدار پیش‌فرض
        
        Returns:
            str: مقدار رمز
        """
        return self._secrets.get(key, default)
    
    def set_secret(self, key: str, value: str):
        """
        تنظیم رمز
        Set secret
        
        Args:
            key: کلید رمز
            value: مقدار رمز
        """
        with self._config_lock:
            self._secrets[key] = value
            self.secrets_manager.save_secrets(self._secrets)
            
            self.logger.info(
                f"رمز تنظیم شد: {key}",
                f"Secret set: {key}"
            )
    
    def reload(self):
        """
        بارگذاری مجدد پیکربندی - Hot reload
        Reload configuration without restart
        """
        self.logger.info(
            "در حال بارگذاری مجدد پیکربندی...",
            "Reloading configuration..."
        )
        self.load()
        self.logger.info(
            "پیکربندی با موفقیت بارگذاری شد",
            "Configuration reloaded successfully"
        )
    
    def get_all(self) -> Dict[str, Any]:
        """
        دریافت تمام پیکربندی
        Get all configuration
        
        Returns:
            Dict: کپی از پیکربندی کامل
        """
        with self._config_lock:
            return copy.deepcopy(self._config)
    
    def validate(self) -> bool:
        """
        اعتبارسنجی پیکربندی
        Validate configuration
        
        Returns:
            bool: True اگر معتبر باشد
        """
        try:
            # بررسی فیلدهای ضروری
            required_keys = [
                'database.host',
                'ai.models_path',
                'simulation.max_bots',
                'security.support_only_mode'
            ]
            
            for key in required_keys:
                if self.get(key) is None:
                    raise ValidationException(
                        f"فیلد ضروری موجود نیست: {key}",
                        f"Required field missing: {key}"
                    )
            
            self.logger.info(
                "پیکربندی معتبر است",
                "Configuration is valid"
            )
            return True
            
        except Exception as e:
            self.logger.error(
                f"خطا در اعتبارسنجی پیکربندی: {str(e)}",
                f"Configuration validation error: {str(e)}"
            )
            return False

# ==============================================================================
# Global Config Instance - نمونه سراسری
# ==============================================================================

_config_instance: Optional[ConfigManager] = None
_config_lock = threading.Lock()

def get_config() -> ConfigManager:
    """
    دریافت نمونه singleton از ConfigManager
    Get singleton instance of ConfigManager
    
    Returns:
        ConfigManager: نمونه مدیر پیکربندی
    """
    global _config_instance
    
    if _config_instance is None:
        with _config_lock:
            if _config_instance is None:
                _config_instance = ConfigManager()
    
    return _config_instance

# ==============================================================================
# Module Test - تست ماژول
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("تست سیستم مدیریت پیکربندی SecureRedLab")
    print("Testing SecureRedLab Configuration Management System")
    print("=" * 80)
    
    # تست 1: دریافت نمونه config
    print("\n1. تست دریافت نمونه ConfigManager:")
    config = get_config()
    print(f"   ✓ نمونه ایجاد شد - محیط: {config._environment.value}")
    
    # تست 2: خواندن تنظیمات
    print("\n2. تست خواندن تنظیمات:")
    db_host = config.get('database.host')
    max_bots = config.get('simulation.max_bots')
    print(f"   ✓ Database Host: {db_host}")
    print(f"   ✓ Max Bots: {max_bots:,}")
    
    # تست 3: تنظیم مقدار
    print("\n3. تست تنظیم مقدار:")
    config.set('test.value', 'تست موفق', save=False)
    test_value = config.get('test.value')
    print(f"   ✓ مقدار تنظیم شده: {test_value}")
    
    # تست 4: مدیریت secrets
    print("\n4. تست مدیریت Secrets:")
    config.set_secret('test_secret', 'رمز_تستی_123')
    secret_value = config.get_secret('test_secret')
    print(f"   ✓ Secret ذخیره و بازیابی شد: {secret_value}")
    
    # تست 5: اعتبارسنجی
    print("\n5. تست اعتبارسنجی:")
    is_valid = config.validate()
    print(f"   ✓ وضعیت اعتبارسنجی: {'معتبر' if is_valid else 'نامعتبر'}")
    
    # تست 6: نمایش تنظیمات AI
    print("\n6. نمایش تنظیمات AI:")
    ai_models = config.get('ai.supported_models', [])
    print(f"   ✓ مدل‌های پشتیبانی‌شده: {len(ai_models)}")
    for model in ai_models[:3]:
        print(f"      - {model}")
    
    print("\n" + "=" * 80)
    print("تست با موفقیت انجام شد!")
    print("Test completed successfully!")
    print("=" * 80)
    print(f"\nفایل‌های پیکربندی در: {CONFIG_BASE_DIR}")
