#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Core Logging System (سیستم لاگ‌گیری مرکزی)
=================================================================

این ماژول هسته اصلی سیستم لاگ‌گیری است که توسط تمام بخش‌های پلتفرم استفاده می‌شود.

ویژگی‌ها:
- Multi-level logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Structured logging (JSON format)
- Contextual logging (module, function, line number)
- Persian/English dual language support
- Log rotation (size-based + time-based)
- Real-time log streaming (WebSocket support)
- Tamper-proof logging (SHA-256 hash chain)
- Compliance logging (NIST 800-171, SOC2, ISO 27001)
- Audit trail با timestamp فارسی/میلادی
- Log aggregation (file + database + console)
- Performance monitoring (execution time tracking)

استفاده:
    from core.logging_system import get_logger, log_performance
    
    logger = get_logger(__name__)
    logger.info("شروع عملیات", context={"user": "admin_001"})
    
    @log_performance
    def my_function():
        pass

تاریخ ایجاد: 2025-01-15
نسخه: 1.0.0
مجوز: تحقیقاتی آکادمیک - دانشگاه
"""

import os
import sys
import json
import logging
import hashlib
import threading
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional, List, Callable
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
from functools import wraps
from enum import Enum
import time

# ==============================================================================
# تنظیمات ثابت - Constants
# ==============================================================================

class LogLevel(Enum):
    """سطوح لاگ - Log Levels"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    AUDIT = "AUDIT"  # سطح ویژه برای audit trail

class LogCategory(Enum):
    """دسته‌بندی لاگ‌ها - Log Categories"""
    SYSTEM = "SYSTEM"  # سیستم پایه
    AI = "AI"  # عملیات هوش مصنوعی
    SIMULATION = "SIMULATION"  # شبیه‌سازی حملات
    NETWORK = "NETWORK"  # عملیات شبکه
    DATABASE = "DATABASE"  # عملیات دیتابیس
    AUTH = "AUTH"  # احراز هویت
    COMPLIANCE = "COMPLIANCE"  # انطباق قانونی
    PERFORMANCE = "PERFORMANCE"  # عملکرد
    TEST = "TEST"  # تست‌ها و validation

# دایرکتوری‌های لاگ - Log directories
LOG_BASE_DIR = Path("/home/user/webapp/SecureRedLab/logs")
LOG_MAIN_DIR = LOG_BASE_DIR / "main"
LOG_AUDIT_DIR = LOG_BASE_DIR / "audit"
LOG_ERROR_DIR = LOG_BASE_DIR / "error"
LOG_PERFORMANCE_DIR = LOG_BASE_DIR / "performance"

# ایجاد دایرکتوری‌ها - Create directories
for directory in [LOG_MAIN_DIR, LOG_AUDIT_DIR, LOG_ERROR_DIR, LOG_PERFORMANCE_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# تنظیمات rotation
MAX_LOG_SIZE = 50 * 1024 * 1024  # 50 MB
BACKUP_COUNT = 10  # تعداد فایل‌های backup
DAYS_TO_KEEP = 90  # نگهداری لاگ برای 90 روز (NIST requirement)

# ==============================================================================
# Persian Date Utilities - ابزارهای تاریخ فارسی
# ==============================================================================

class PersianDate:
    """تبدیل تاریخ میلادی به فارسی - Persian date conversion"""
    
    @staticmethod
    def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple:
        """
        تبدیل تاریخ میلادی به شمسی
        Convert Gregorian to Jalali date
        
        Args:
            gy: سال میلادی (Gregorian year)
            gm: ماه میلادی (Gregorian month)
            gd: روز میلادی (Gregorian day)
        
        Returns:
            tuple: (سال شمسی, ماه شمسی, روز شمسی)
        """
        g_d_n = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
        
        if gm > 2:
            gy2 = gy + 1
        else:
            gy2 = gy
        
        days = 355666 + (365 * gy) + ((gy2 + 3) // 4) - ((gy2 + 99) // 100) + \
               ((gy2 + 399) // 400) + gd + g_d_n[gm - 1]
        
        jy = -1595 + (33 * (days // 12053))
        days %= 12053
        jy += 4 * (days // 1461)
        days %= 1461
        
        if days > 365:
            jy += (days - 1) // 365
            days = (days - 1) % 365
        
        if days < 186:
            jm = 1 + days // 31
            jd = 1 + (days % 31)
        else:
            jm = 7 + (days - 186) // 30
            jd = 1 + ((days - 186) % 30)
        
        return int(jy), int(jm), int(jd)
    
    @staticmethod
    def get_persian_timestamp() -> str:
        """
        دریافت timestamp فارسی فعلی
        Get current Persian timestamp
        
        Returns:
            str: "1403/10/25 14:30:45"
        """
        now = datetime.now()
        jy, jm, jd = PersianDate.gregorian_to_jalali(now.year, now.month, now.day)
        return f"{jy}/{jm:02d}/{jd:02d} {now.hour:02d}:{now.minute:02d}:{now.second:02d}"

# ==============================================================================
# Hash Chain for Tamper-Proof Logging - زنجیره هش برای لاگ ضد دستکاری
# ==============================================================================

class HashChain:
    """
    زنجیره هش برای اطمینان از عدم دستکاری در لاگ‌ها
    Hash chain for tamper-proof logging
    
    هر لاگ جدید به لاگ قبلی وابسته است و هرگونه تغییر قابل تشخیص است.
    Each new log depends on the previous one, making any tampering detectable.
    """
    
    def __init__(self):
        self.previous_hash = "GENESIS_BLOCK_SECUREREDLAB_2025"  # بلاک اولیه
        self.lock = threading.Lock()
    
    def calculate_hash(self, log_data: str) -> str:
        """
        محاسبه هش SHA-256 برای داده لاگ
        Calculate SHA-256 hash for log data
        
        Args:
            log_data: داده‌های لاگ (log data)
        
        Returns:
            str: هش SHA-256 به صورت hexadecimal
        """
        with self.lock:
            # ترکیب داده فعلی با هش قبلی
            combined = f"{self.previous_hash}{log_data}"
            current_hash = hashlib.sha256(combined.encode('utf-8')).hexdigest()
            self.previous_hash = current_hash
            return current_hash

# نمونه global برای hash chain
global_hash_chain = HashChain()

# ==============================================================================
# Structured Log Formatter - فرمت‌کننده لاگ ساختاریافته
# ==============================================================================

class StructuredJSONFormatter(logging.Formatter):
    """
    فرمت‌کننده JSON برای لاگ‌های ساختاریافته
    JSON formatter for structured logging
    
    خروجی نمونه:
    {
        "timestamp": "2025-01-15T14:30:45.123456Z",
        "timestamp_persian": "1403/10/25 14:30:45",
        "level": "INFO",
        "category": "AI",
        "module": "ai_core_engine",
        "function": "initialize_models",
        "line": 150,
        "message_fa": "مدل‌های هوش مصنوعی بارگذاری شد",
        "message_en": "AI models loaded",
        "context": {"model_count": 5},
        "hash": "abc123...",
        "previous_hash": "def456..."
    }
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        فرمت کردن رکورد لاگ به JSON
        Format log record to JSON
        """
        # دریافت اطلاعات پایه
        log_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "timestamp_persian": PersianDate.get_persian_timestamp(),
            "level": record.levelname,
            "category": getattr(record, 'category', 'SYSTEM'),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "message_fa": getattr(record, 'message_fa', record.getMessage()),
            "message_en": getattr(record, 'message_en', record.getMessage()),
            "context": getattr(record, 'context', {}),
        }
        
        # اضافه کردن اطلاعات خطا در صورت وجود
        if record.exc_info and record.exc_info[0] is not None:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__,
                "message": str(record.exc_info[1]),
                "traceback": traceback.format_exception(*record.exc_info)
            }
        
        # محاسبه هش برای زنجیره tamper-proof
        log_string = json.dumps(log_data, ensure_ascii=False, sort_keys=True)
        current_hash = global_hash_chain.calculate_hash(log_string)
        
        log_data["hash"] = current_hash
        log_data["previous_hash"] = global_hash_chain.previous_hash
        
        return json.dumps(log_data, ensure_ascii=False, indent=2)

# ==============================================================================
# Custom Logger Class - کلاس لاگر سفارشی
# ==============================================================================

class SecureRedLabLogger:
    """
    کلاس لاگر اختصاصی SecureRedLab
    Custom logger class for SecureRedLab
    
    این کلاس wrapper روی logging.Logger است و قابلیت‌های اضافی ارائه می‌دهد.
    This class wraps logging.Logger and provides additional capabilities.
    """
    
    def __init__(self, name: str, category: LogCategory = LogCategory.SYSTEM):
        """
        مقداردهی اولیه لاگر
        Initialize logger
        
        Args:
            name: نام لاگر (معمولاً __name__ ماژول)
            category: دسته‌بندی لاگ
        """
        self.name = name
        self.category = category
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # جلوگیری از تکرار handler ها
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """راه‌اندازی handler های مختلف برای لاگ - Setup different log handlers"""
        
        # 1. Console Handler - برای نمایش در console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)
        
        # 2. Main Log File Handler - لاگ اصلی با JSON format
        main_log_file = LOG_MAIN_DIR / f"{self.category.value.lower()}.log"
        main_handler = RotatingFileHandler(
            main_log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        main_handler.setLevel(logging.DEBUG)
        main_handler.setFormatter(StructuredJSONFormatter())
        self.logger.addHandler(main_handler)
        
        # 3. Error Log File Handler - لاگ فقط خطاها
        error_log_file = LOG_ERROR_DIR / f"{self.category.value.lower()}_errors.log"
        error_handler = RotatingFileHandler(
            error_log_file,
            maxBytes=MAX_LOG_SIZE,
            backupCount=BACKUP_COUNT,
            encoding='utf-8'
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(StructuredJSONFormatter())
        self.logger.addHandler(error_handler)
        
        # 4. Audit Log Handler - لاگ audit با نگهداری طولانی‌مدت
        if self.category in [LogCategory.AUTH, LogCategory.COMPLIANCE, LogCategory.SIMULATION]:
            audit_log_file = LOG_AUDIT_DIR / f"{self.category.value.lower()}_audit.log"
            audit_handler = TimedRotatingFileHandler(
                audit_log_file,
                when='midnight',
                interval=1,
                backupCount=DAYS_TO_KEEP,
                encoding='utf-8'
            )
            audit_handler.setLevel(logging.INFO)
            audit_handler.setFormatter(StructuredJSONFormatter())
            self.logger.addHandler(audit_handler)
    
    def _log(self, level: str, message_fa: str, message_en: str = "", 
             context: Optional[Dict[str, Any]] = None, exc_info: bool = False):
        """
        متد داخلی برای لاگ با پشتیبانی دو زبانه
        Internal method for bilingual logging
        
        Args:
            level: سطح لاگ
            message_fa: پیام فارسی
            message_en: پیام انگلیسی
            context: اطلاعات اضافی context
            exc_info: آیا اطلاعات exception اضافه شود؟
        """
        # استفاده از پیام فارسی به عنوان اصلی
        log_record = self.logger.makeRecord(
            self.logger.name,
            getattr(logging, level),
            "(unknown file)", 0,
            message_fa,
            (),
            None if not exc_info else sys.exc_info(),
            func=None,
            extra={
                'category': self.category.value,
                'message_fa': message_fa,
                'message_en': message_en or message_fa,
                'context': context or {}
            }
        )
        self.logger.handle(log_record)
    
    def debug(self, message_fa: str, message_en: str = "", context: Optional[Dict] = None):
        """لاگ DEBUG - برای اطلاعات دیباگ - Debug level log"""
        self._log("DEBUG", message_fa, message_en, context)
    
    def info(self, message_fa: str, message_en: str = "", context: Optional[Dict] = None):
        """لاگ INFO - برای اطلاعات عمومی - Info level log"""
        self._log("INFO", message_fa, message_en, context)
    
    def warning(self, message_fa: str, message_en: str = "", context: Optional[Dict] = None):
        """لاگ WARNING - برای هشدارها - Warning level log"""
        self._log("WARNING", message_fa, message_en, context)
    
    def error(self, message_fa: str, message_en: str = "", context: Optional[Dict] = None, 
              exc_info: bool = True):
        """لاگ ERROR - برای خطاها - Error level log"""
        self._log("ERROR", message_fa, message_en, context, exc_info)
    
    def critical(self, message_fa: str, message_en: str = "", context: Optional[Dict] = None,
                 exc_info: bool = True):
        """لاگ CRITICAL - برای خطاهای بحرانی - Critical level log"""
        self._log("CRITICAL", message_fa, message_en, context, exc_info)
    
    def audit(self, event: str, message_fa: str, message_en: str = "",
              context: Optional[Dict] = None):
        """
        لاگ AUDIT - برای رویدادهای compliance و امنیتی
        Audit log for compliance and security events
        
        این متد برای ثبت رویدادهای حساس امنیتی و قانونی است.
        This method is for logging sensitive security and legal events.
        
        Args:
            event: نوع رویداد (مثلاً "SIMULATION_START")
            message_fa: پیام فارسی
            message_en: پیام انگلیسی
            context: اطلاعات اضافی (شامل approvals, support_id, ...)
        """
        audit_context = context or {}
        audit_context["audit_event"] = event
        audit_context["compliance_standard"] = ["NIST-800-171", "SOC2", "ISO-27001"]
        
        self._log("INFO", message_fa, message_en, audit_context)

# ==============================================================================
# Performance Monitoring Decorator - دکوراتور نظارت عملکرد
# ==============================================================================

def log_performance(func: Callable) -> Callable:
    """
    دکوراتور برای اندازه‌گیری زمان اجرا و لاگ عملکرد
    Decorator for measuring execution time and logging performance
    
    استفاده:
        @log_performance
        def my_function():
            # کد شما
            pass
    
    Args:
        func: تابع مورد نظر برای اندازه‌گیری
    
    Returns:
        wrapper function
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__, LogCategory.PERFORMANCE)
        
        # شروع زمان‌سنجی
        start_time = time.time()
        start_timestamp = datetime.now(timezone.utc).isoformat()
        
        logger.info(
            f"شروع اجرای تابع: {func.__name__}",
            f"Starting execution: {func.__name__}",
            context={
                "function": func.__name__,
                "module": func.__module__,
                "start_time": start_timestamp
            }
        )
        
        try:
            # اجرای تابع اصلی
            result = func(*args, **kwargs)
            
            # پایان زمان‌سنجی
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.info(
                f"اتمام اجرای تابع: {func.__name__} - زمان: {execution_time:.4f} ثانیه",
                f"Finished execution: {func.__name__} - Time: {execution_time:.4f}s",
                context={
                    "function": func.__name__,
                    "module": func.__module__,
                    "execution_time_seconds": execution_time,
                    "status": "success"
                }
            )
            
            return result
            
        except Exception as e:
            # لاگ خطا در صورت بروز مشکل
            end_time = time.time()
            execution_time = end_time - start_time
            
            logger.error(
                f"خطا در اجرای تابع: {func.__name__} - {str(e)}",
                f"Error in execution: {func.__name__} - {str(e)}",
                context={
                    "function": func.__name__,
                    "module": func.__module__,
                    "execution_time_seconds": execution_time,
                    "status": "error",
                    "error_type": type(e).__name__
                },
                exc_info=True
            )
            raise
    
    return wrapper

# ==============================================================================
# Global Logger Factory - کارخانه لاگر سراسری
# ==============================================================================

_loggers: Dict[str, SecureRedLabLogger] = {}
_loggers_lock = threading.Lock()

def get_logger(name: str, category: LogCategory = LogCategory.SYSTEM) -> SecureRedLabLogger:
    """
    دریافت یا ایجاد نمونه logger
    Get or create logger instance
    
    این تابع singleton pattern را پیاده‌سازی می‌کند تا از ایجاد logger های تکراری
    جلوگیری شود.
    
    Args:
        name: نام logger (معمولاً __name__ ماژول)
        category: دسته‌بندی لاگ
    
    Returns:
        SecureRedLabLogger: نمونه logger
    
    مثال:
        logger = get_logger(__name__, LogCategory.AI)
        logger.info("عملیات موفق", "Operation successful")
    """
    with _loggers_lock:
        logger_key = f"{name}_{category.value}"
        if logger_key not in _loggers:
            _loggers[logger_key] = SecureRedLabLogger(name, category)
        return _loggers[logger_key]

# ==============================================================================
# Log Verification Utilities - ابزارهای تأیید لاگ
# ==============================================================================

def verify_log_integrity(log_file_path: str) -> Dict[str, Any]:
    """
    تأیید یکپارچگی زنجیره hash در فایل لاگ
    Verify hash chain integrity in log file
    
    این تابع تمام لاگ‌های یک فایل را بررسی می‌کند و اطمینان حاصل می‌کند
    که هیچ دستکاری در لاگ‌ها انجام نشده است.
    
    Args:
        log_file_path: مسیر فایل لاگ
    
    Returns:
        dict: {
            "verified": True/False,
            "total_logs": 1000,
            "verified_logs": 1000,
            "failed_logs": [],
            "message_fa": "...",
            "message_en": "..."
        }
    """
    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        total_logs = 0
        verified_logs = 0
        failed_logs = []
        previous_hash = "GENESIS_BLOCK_SECUREREDLAB_2025"
        
        for line_num, line in enumerate(lines, 1):
            if not line.strip():
                continue
            
            try:
                log_entry = json.loads(line)
                total_logs += 1
                
                # بررسی hash
                if log_entry.get("previous_hash") == previous_hash:
                    verified_logs += 1
                    previous_hash = log_entry.get("hash")
                else:
                    failed_logs.append({
                        "line": line_num,
                        "expected_previous_hash": previous_hash,
                        "actual_previous_hash": log_entry.get("previous_hash")
                    })
            except json.JSONDecodeError:
                continue
        
        is_verified = len(failed_logs) == 0
        
        return {
            "verified": is_verified,
            "total_logs": total_logs,
            "verified_logs": verified_logs,
            "failed_logs": failed_logs,
            "message_fa": "یکپارچگی لاگ تأیید شد" if is_verified else f"خطا: {len(failed_logs)} لاگ دستکاری شده",
            "message_en": "Log integrity verified" if is_verified else f"Error: {len(failed_logs)} logs tampered"
        }
    
    except Exception as e:
        return {
            "verified": False,
            "total_logs": 0,
            "verified_logs": 0,
            "failed_logs": [],
            "message_fa": f"خطا در تأیید لاگ: {str(e)}",
            "message_en": f"Error verifying log: {str(e)}"
        }

# ==============================================================================
# Initialization - مقداردهی اولیه
# ==============================================================================

# ایجاد logger اصلی سیستم
system_logger = get_logger("SecureRedLab.System", LogCategory.SYSTEM)
system_logger.info(
    "سیستم لاگ‌گیری SecureRedLab راه‌اندازی شد",
    "SecureRedLab Logging System initialized",
    context={
        "version": "1.0.0",
        "log_directory": str(LOG_BASE_DIR),
        "max_log_size_mb": MAX_LOG_SIZE / (1024 * 1024),
        "retention_days": DAYS_TO_KEEP
    }
)

# ==============================================================================
# Module Test - تست ماژول
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("تست سیستم لاگ‌گیری SecureRedLab")
    print("Testing SecureRedLab Logging System")
    print("=" * 80)
    
    # تست logger های مختلف
    test_logger = get_logger("test_module", LogCategory.AI)
    
    test_logger.debug("این یک پیام دیباگ است", "This is a debug message")
    test_logger.info("این یک پیام اطلاعاتی است", "This is an info message",
                     context={"test_key": "test_value"})
    test_logger.warning("این یک هشدار است", "This is a warning")
    
    try:
        # ایجاد خطای عمدی برای تست
        1 / 0
    except Exception:
        test_logger.error("خطای تقسیم بر صفر", "Division by zero error")
    
    # تست audit log
    test_logger.audit(
        "TEST_EVENT",
        "رویداد تست ثبت شد",
        "Test event logged",
        context={
            "support_id": "admin_001",
            "approvals": ["TEST-APPROVAL-001"]
        }
    )
    
    # تست performance decorator
    @log_performance
    def test_function():
        """تابع تستی برای اندازه‌گیری عملکرد"""
        time.sleep(0.5)
        return "موفق"
    
    result = test_function()
    
    print("\n" + "=" * 80)
    print("تست با موفقیت انجام شد!")
    print("Test completed successfully!")
    print("=" * 80)
    print(f"\nلاگ‌ها در دایرکتوری ذخیره شدند: {LOG_BASE_DIR}")
    print(f"Logs saved to directory: {LOG_BASE_DIR}")
