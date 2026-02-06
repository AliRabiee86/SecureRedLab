#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Exception Handling System (سیستم مدیریت خطا)
==================================================================

این ماژول سیستم جامع مدیریت خطا را پیاده‌سازی می‌کند که با logging system یکپارچه است.

ویژگی‌ها:
- Custom exception hierarchy (سلسله‌مراتب خطای سفارشی)
- Automatic error recovery (بازیابی خودکار خطا)
- Stack trace با ترجمه فارسی
- Error categorization (دسته‌بندی خطاها)
- Graceful degradation (کاهش تدریجی قابلیت‌ها)
- Error notification system (سیستم اطلاع‌رسانی خطا)
- Debug mode با اطلاعات کامل
- Production mode با اطلاعات محدود
- Integration با logging system
- Recovery strategies (استراتژی‌های بازیابی)

استفاده:
    from core.exception_handler import (
        handle_exception, retry_on_failure,
        SecureRedLabException, NetworkException
    )
    
    @handle_exception(recovery_strategy="log_and_continue")
    def my_function():
        raise NetworkException("خطای شبکه")
    
    @retry_on_failure(max_retries=3, delay=1.0)
    def unstable_function():
        # کد ناپایدار
        pass

تاریخ ایجاد: 2025-01-15
نسخه: 1.0.0
مجوز: تحقیقاتی آکادمیک - دانشگاه
"""

import sys
import traceback
import functools
import time
from typing import Any, Callable, Optional, Type, Union, List, Dict
from enum import Enum
from dataclasses import dataclass
from datetime import datetime

# وارد کردن سیستم لاگ‌گیری
from core.logging_system import get_logger, LogCategory

# ==============================================================================
# Exception Categories - دسته‌بندی خطاها
# ==============================================================================

class ErrorCategory(Enum):
    """دسته‌بندی خطاها - Error Categories"""
    SYSTEM = "SYSTEM"  # خطاهای سیستمی
    NETWORK = "NETWORK"  # خطاهای شبکه
    DATABASE = "DATABASE"  # خطاهای دیتابیس
    AI = "AI"  # خطاهای هوش مصنوعی
    SIMULATION = "SIMULATION"  # خطاهای شبیه‌سازی
    AUTH = "AUTH"  # خطاهای احراز هویت
    CONFIG = "CONFIG"  # خطاهای پیکربندی
    VALIDATION = "VALIDATION"  # خطاهای اعتبارسنجی
    PERMISSION = "PERMISSION"  # خطاهای مجوز
    RESOURCE = "RESOURCE"  # خطاهای منابع (CPU, RAM, Disk)

class ErrorSeverity(Enum):
    """شدت خطا - Error Severity"""
    LOW = "LOW"  # کم - قابل نادیده‌گیری
    MEDIUM = "MEDIUM"  # متوسط - نیاز به بررسی
    HIGH = "HIGH"  # بالا - نیاز به توجه فوری
    CRITICAL = "CRITICAL"  # بحرانی - نیاز به توقف عملیات

class RecoveryStrategy(Enum):
    """استراتژی بازیابی - Recovery Strategy"""
    IGNORE = "IGNORE"  # نادیده گرفتن
    LOG = "LOG"  # فقط لاگ کردن
    RETRY = "RETRY"  # تلاش مجدد
    FALLBACK = "FALLBACK"  # استفاده از جایگزین
    NOTIFY = "NOTIFY"  # اطلاع‌رسانی به ادمین
    ABORT = "ABORT"  # توقف عملیات
    GRACEFUL_DEGRADATION = "GRACEFUL_DEGRADATION"  # کاهش تدریجی قابلیت‌ها

# ==============================================================================
# Base Exception Classes - کلاس‌های پایه خطا
# ==============================================================================

@dataclass
class ErrorContext:
    """
    Context اضافی برای خطا
    Additional context for errors
    """
    timestamp: str
    module: str
    function: str
    category: ErrorCategory
    severity: ErrorSeverity
    recovery_strategy: RecoveryStrategy
    additional_info: Dict[str, Any]

class SecureRedLabException(Exception):
    """
    کلاس پایه برای تمام خطاهای سفارشی SecureRedLab
    Base class for all custom SecureRedLab exceptions
    
    این کلاس پایه برای تمام خطاهای سفارشی سیستم است و قابلیت‌های اضافی
    مانند دسته‌بندی، شدت، و استراتژی بازیابی را فراهم می‌کند.
    """
    
    def __init__(
        self,
        message_fa: str,
        message_en: str = "",
        category: ErrorCategory = ErrorCategory.SYSTEM,
        severity: ErrorSeverity = ErrorSeverity.MEDIUM,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.LOG,
        context: Optional[Dict[str, Any]] = None
    ):
        """
        مقداردهی اولیه خطا
        Initialize exception
        
        Args:
            message_fa: پیام خطا به فارسی
            message_en: پیام خطا به انگلیسی
            category: دسته‌بندی خطا
            severity: شدت خطا
            recovery_strategy: استراتژی بازیابی
            context: اطلاعات اضافی
        """
        self.message_fa = message_fa
        self.message_en = message_en or message_fa
        self.category = category
        self.severity = severity
        self.recovery_strategy = recovery_strategy
        self.context = context or {}
        
        # ذخیره stack trace
        self.stack_trace = traceback.format_exc()
        
        # ایجاد error context
        self.error_context = ErrorContext(
            timestamp=datetime.utcnow().isoformat(),
            module=self.__class__.__module__,
            function="",  # خواهد شد پر در handle_exception
            category=category,
            severity=severity,
            recovery_strategy=recovery_strategy,
            additional_info=self.context
        )
        
        # فراخوانی constructor پایه
        super().__init__(self.message_fa)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        تبدیل خطا به dictionary برای لاگ
        Convert exception to dictionary for logging
        """
        return {
            "type": self.__class__.__name__,
            "message_fa": self.message_fa,
            "message_en": self.message_en,
            "category": self.category.value,
            "severity": self.severity.value,
            "recovery_strategy": self.recovery_strategy.value,
            "context": self.context,
            "timestamp": self.error_context.timestamp,
            "stack_trace": self.stack_trace.split('\n') if self.stack_trace != "NoneType: None\n" else []
        }
    
    def get_persian_message(self) -> str:
        """دریافت پیام فارسی - Get Persian message"""
        return self.message_fa
    
    def get_english_message(self) -> str:
        """دریافت پیام انگلیسی - Get English message"""
        return self.message_en

# ==============================================================================
# Specialized Exception Classes - کلاس‌های تخصصی خطا
# ==============================================================================

class NetworkException(SecureRedLabException):
    """خطاهای مرتبط با شبکه - Network-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.NETWORK,
            severity=kwargs.get('severity', ErrorSeverity.HIGH),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.RETRY),
            context=kwargs.get('context', {})
        )

class DatabaseException(SecureRedLabException):
    """خطاهای مرتبط با دیتابیس - Database-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.DATABASE,
            severity=kwargs.get('severity', ErrorSeverity.HIGH),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.RETRY),
            context=kwargs.get('context', {})
        )

class AIException(SecureRedLabException):
    """خطاهای مرتبط با هوش مصنوعی - AI-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.AI,
            severity=kwargs.get('severity', ErrorSeverity.MEDIUM),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.FALLBACK),
            context=kwargs.get('context', {})
        )

class SimulationException(SecureRedLabException):
    """خطاهای مرتبط با شبیه‌سازی - Simulation-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.SIMULATION,
            severity=kwargs.get('severity', ErrorSeverity.HIGH),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.ABORT),
            context=kwargs.get('context', {})
        )

class AuthenticationException(SecureRedLabException):
    """خطاهای مرتبط با احراز هویت - Authentication-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.AUTH,
            severity=kwargs.get('severity', ErrorSeverity.CRITICAL),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.ABORT),
            context=kwargs.get('context', {})
        )

class ConfigurationException(SecureRedLabException):
    """خطاهای مرتبط با پیکربندی - Configuration-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.CONFIG,
            severity=kwargs.get('severity', ErrorSeverity.HIGH),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.ABORT),
            context=kwargs.get('context', {})
        )

class ValidationException(SecureRedLabException):
    """خطاهای مرتبط با اعتبارسنجی - Validation-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.VALIDATION,
            severity=kwargs.get('severity', ErrorSeverity.MEDIUM),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.LOG),
            context=kwargs.get('context', {})
        )

class PermissionException(SecureRedLabException):
    """خطاهای مرتبط با مجوز - Permission-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.PERMISSION,
            severity=kwargs.get('severity', ErrorSeverity.CRITICAL),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.ABORT),
            context=kwargs.get('context', {})
        )

class ResourceException(SecureRedLabException):
    """خطاهای مرتبط با منابع - Resource-related exceptions"""
    
    def __init__(self, message_fa: str, message_en: str = "", **kwargs):
        super().__init__(
            message_fa,
            message_en,
            category=ErrorCategory.RESOURCE,
            severity=kwargs.get('severity', ErrorSeverity.HIGH),
            recovery_strategy=kwargs.get('recovery_strategy', RecoveryStrategy.GRACEFUL_DEGRADATION),
            context=kwargs.get('context', {})
        )

# ==============================================================================
# Exception Handler Decorator - دکوراتور مدیریت خطا
# ==============================================================================

def handle_exception(
    recovery_strategy: Union[str, RecoveryStrategy] = RecoveryStrategy.LOG,
    fallback_value: Any = None,
    logger_category: LogCategory = LogCategory.SYSTEM,
    raise_on_critical: bool = True
) -> Callable:
    """
    دکوراتور برای مدیریت خودکار خطاها
    Decorator for automatic exception handling
    
    این دکوراتور به صورت خودکار خطاها را مدیریت می‌کند و بر اساس استراتژی
    تعیین شده، بازیابی انجام می‌دهد.
    
    Args:
        recovery_strategy: استراتژی بازیابی
        fallback_value: مقدار جایگزین در صورت خطا
        logger_category: دسته‌بندی logger
        raise_on_critical: آیا در خطاهای critical مجدداً raise شود؟
    
    استفاده:
        @handle_exception(recovery_strategy="RETRY", fallback_value=[])
        def my_function():
            # کد شما
            pass
    """
    # تبدیل string به enum
    if isinstance(recovery_strategy, str):
        recovery_strategy = RecoveryStrategy[recovery_strategy]
    
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__, logger_category)
            
            try:
                return func(*args, **kwargs)
            
            except SecureRedLabException as e:
                # خطای سفارشی SecureRedLab
                e.error_context.function = func.__name__
                
                # لاگ خطا
                logger.error(
                    f"خطا در تابع {func.__name__}: {e.get_persian_message()}",
                    f"Error in function {func.__name__}: {e.get_english_message()}",
                    context=e.to_dict()
                )
                
                # اعمال استراتژی بازیابی
                if e.severity == ErrorSeverity.CRITICAL and raise_on_critical:
                    raise
                
                if e.recovery_strategy == RecoveryStrategy.ABORT:
                    raise
                elif e.recovery_strategy == RecoveryStrategy.FALLBACK:
                    return fallback_value
                elif e.recovery_strategy == RecoveryStrategy.IGNORE:
                    return fallback_value
                else:
                    return fallback_value
            
            except Exception as e:
                # خطای استاندارد Python
                logger.error(
                    f"خطای غیرمنتظره در تابع {func.__name__}: {str(e)}",
                    f"Unexpected error in function {func.__name__}: {str(e)}",
                    context={
                        "function": func.__name__,
                        "module": func.__module__,
                        "error_type": type(e).__name__,
                        "args": str(args),
                        "kwargs": str(kwargs)
                    },
                    exc_info=True
                )
                
                if recovery_strategy == RecoveryStrategy.ABORT:
                    raise
                else:
                    return fallback_value
        
        return wrapper
    return decorator

# ==============================================================================
# Retry Decorator - دکوراتور تلاش مجدد
# ==============================================================================

def retry_on_failure(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple = (Exception,),
    logger_category: LogCategory = LogCategory.SYSTEM
) -> Callable:
    """
    دکوراتور برای تلاش مجدد در صورت خطا
    Decorator for retrying on failure
    
    این دکوراتور در صورت بروز خطا، تابع را چندین بار مجدداً اجرا می‌کند
    با تأخیر exponential backoff.
    
    Args:
        max_retries: حداکثر تعداد تلاش مجدد
        delay: تأخیر اولیه (ثانیه)
        backoff: ضریب افزایش تأخیر
        exceptions: tuple از exception هایی که باید retry شوند
        logger_category: دسته‌بندی logger
    
    استفاده:
        @retry_on_failure(max_retries=5, delay=2.0)
        def unstable_network_call():
            # کد ناپایدار
            pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger = get_logger(func.__module__, logger_category)
            
            current_delay = delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    if attempt > 0:
                        logger.warning(
                            f"تلاش مجدد {attempt}/{max_retries} برای تابع {func.__name__}",
                            f"Retry attempt {attempt}/{max_retries} for function {func.__name__}",
                            context={
                                "function": func.__name__,
                                "attempt": attempt,
                                "max_retries": max_retries,
                                "delay": current_delay
                            }
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    
                    return func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        logger.error(
                            f"تمام تلاش‌های مجدد برای تابع {func.__name__} شکست خورد",
                            f"All retry attempts failed for function {func.__name__}",
                            context={
                                "function": func.__name__,
                                "attempts": max_retries + 1,
                                "final_error": str(e)
                            },
                            exc_info=True
                        )
                        raise
                    
                    logger.info(
                        f"خطا در تلاش {attempt + 1}: {str(e)}",
                        f"Error in attempt {attempt + 1}: {str(e)}",
                        context={"attempt": attempt + 1, "error": str(e)}
                    )
            
            # اگر به اینجا رسید یعنی همه تلاش‌ها شکست خورده
            raise last_exception
        
        return wrapper
    return decorator

# ==============================================================================
# Error Recovery Strategies - استراتژی‌های بازیابی خطا
# ==============================================================================

class ErrorRecoveryManager:
    """
    مدیر استراتژی‌های بازیابی خطا
    Manager for error recovery strategies
    
    این کلاس استراتژی‌های مختلف بازیابی را پیاده‌سازی می‌کند.
    """
    
    @staticmethod
    def graceful_degradation(
        primary_function: Callable,
        fallback_functions: List[Callable],
        *args,
        **kwargs
    ) -> Any:
        """
        کاهش تدریجی قابلیت‌ها - تلاش با توابع جایگزین
        Graceful degradation - try fallback functions
        
        این متد ابتدا تابع اصلی را اجرا می‌کند و در صورت خطا،
        به ترتیب توابع جایگزین را امتحان می‌کند.
        
        Args:
            primary_function: تابع اصلی
            fallback_functions: لیست توابع جایگزین
            *args, **kwargs: آرگومان‌های تابع
        
        Returns:
            نتیجه اولین تابع موفق
        """
        logger = get_logger(__name__, LogCategory.SYSTEM)
        
        # تلاش با تابع اصلی
        try:
            return primary_function(*args, **kwargs)
        except Exception as e:
            logger.warning(
                f"تابع اصلی شکست خورد: {primary_function.__name__}",
                f"Primary function failed: {primary_function.__name__}",
                context={"error": str(e)}
            )
        
        # تلاش با توابع جایگزین
        for i, fallback in enumerate(fallback_functions, 1):
            try:
                logger.info(
                    f"تلاش با تابع جایگزین {i}: {fallback.__name__}",
                    f"Trying fallback function {i}: {fallback.__name__}"
                )
                return fallback(*args, **kwargs)
            except Exception as e:
                logger.warning(
                    f"تابع جایگزین {i} شکست خورد: {fallback.__name__}",
                    f"Fallback function {i} failed: {fallback.__name__}",
                    context={"error": str(e)}
                )
        
        # اگر همه شکست خوردند
        raise SecureRedLabException(
            "تمام توابع (اصلی و جایگزین) شکست خوردند",
            "All functions (primary and fallbacks) failed",
            category=ErrorCategory.SYSTEM,
            severity=ErrorSeverity.HIGH
        )

# ==============================================================================
# Global Exception Handler - مدیر سراسری خطا
# ==============================================================================

def setup_global_exception_handler():
    """
    راه‌اندازی مدیر سراسری برای خطاهای unhandled
    Setup global handler for unhandled exceptions
    
    این تابع یک handler سراسری برای خطاهای unhandled نصب می‌کند
    تا هیچ خطایی بدون لاگ نماند.
    """
    logger = get_logger("GlobalExceptionHandler", LogCategory.SYSTEM)
    
    def global_exception_handler(exc_type, exc_value, exc_traceback):
        """Handler سراسری برای exception های unhandled"""
        if issubclass(exc_type, KeyboardInterrupt):
            # اجازه بده KeyboardInterrupt عادی کار کند
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical(
            f"خطای unhandled: {exc_type.__name__}: {str(exc_value)}",
            f"Unhandled exception: {exc_type.__name__}: {str(exc_value)}",
            context={
                "type": exc_type.__name__,
                "value": str(exc_value),
                "traceback": traceback.format_exception(exc_type, exc_value, exc_traceback)
            }
        )
    
    # نصب handler
    sys.excepthook = global_exception_handler
    
    logger.info(
        "مدیر سراسری خطا نصب شد",
        "Global exception handler installed"
    )

# ==============================================================================
# Initialization - مقداردهی اولیه
# ==============================================================================

# نصب global exception handler
setup_global_exception_handler()

# ==============================================================================
# Module Test - تست ماژول
# ==============================================================================
# Performance Monitoring Decorator - مانیتورینگ عملکرد
# ==============================================================================

def log_performance(func: Callable) -> Callable:
    """
    Decorator برای لاگ کردن زمان اجرای توابع
    
    این decorator زمان اجرای تابع را اندازه‌گیری کرده و لاگ می‌کند.
    
    استفاده:
        @log_performance
        def slow_function():
            time.sleep(1)
    
    Args:
        func: تابعی که باید زمان‌سنجی شود
    
    Returns:
        تابع wrapper شده
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = get_logger(func.__module__, LogCategory.PERFORMANCE)
        
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            logger.debug(
                f"⏱️  {func.__name__} اجرا شد در {elapsed:.3f} ثانیه",
                f"⏱️  {func.__name__} executed in {elapsed:.3f} seconds",
                context={
                    'function': func.__name__,
                    'module': func.__module__,
                    'execution_time_seconds': elapsed,
                    'execution_time_ms': elapsed * 1000
                }
            )
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            
            logger.warning(
                f"⏱️  {func.__name__} با خطا مواجه شد بعد از {elapsed:.3f} ثانیه",
                f"⏱️  {func.__name__} failed after {elapsed:.3f} seconds",
                context={
                    'function': func.__name__,
                    'module': func.__module__,
                    'execution_time_seconds': elapsed,
                    'error': str(e)
                }
            )
            
            raise
    
    return wrapper


# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("تست سیستم مدیریت خطا SecureRedLab")
    print("Testing SecureRedLab Exception Handling System")
    print("=" * 80)
    
    # تست 1: خطای سفارشی
    print("\n1. تست خطای سفارشی (Custom Exception):")
    try:
        raise NetworkException(
            "خطای اتصال به شبکه",
            "Network connection error",
            context={"ip": "192.168.1.1", "port": 8080}
        )
    except SecureRedLabException as e:
        print(f"   ✓ خطا دریافت شد: {e.get_persian_message()}")
        print(f"   ✓ دسته‌بندی: {e.category.value}")
        print(f"   ✓ شدت: {e.severity.value}")
    
    # تست 2: handle_exception decorator
    print("\n2. تست handle_exception decorator:")
    
    @handle_exception(recovery_strategy="FALLBACK", fallback_value="مقدار پیش‌فرض")
    def test_function_with_error():
        raise ValidationException("خطای اعتبارسنجی", "Validation error")
    
    result = test_function_with_error()
    print(f"   ✓ نتیجه بازیابی: {result}")
    
    # تست 3: retry_on_failure decorator
    print("\n3. تست retry_on_failure decorator:")
    
    attempt_count = 0
    
    @retry_on_failure(max_retries=3, delay=0.1, backoff=1.5)
    def unstable_function():
        global attempt_count
        attempt_count += 1
        if attempt_count < 3:
            raise NetworkException("اتصال ناموفق", "Connection failed")
        return "موفق در تلاش سوم"
    
    result = unstable_function()
    print(f"   ✓ نتیجه: {result}")
    print(f"   ✓ تعداد تلاش‌ها: {attempt_count}")
    
    # تست 4: graceful degradation
    print("\n4. تست graceful degradation:")
    
    def primary_func():
        raise Exception("تابع اصلی شکست خورد")
    
    def fallback1():
        raise Exception("جایگزین 1 شکست خورد")
    
    def fallback2():
        return "جایگزین 2 موفق بود"
    
    result = ErrorRecoveryManager.graceful_degradation(
        primary_func,
        [fallback1, fallback2]
    )
    print(f"   ✓ نتیجه: {result}")
    
    print("\n" + "=" * 80)
    print("تست با موفقیت انجام شد!")
    print("Test completed successfully!")
    print("=" * 80)
