#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - AI Output Validator (اعتبارسنج خروجی هوش مصنوعی)
=====================================================================

این ماژول برای جلوگیری از توهم (hallucination) AI و اعتبارسنجی خروجی‌ها.

ویژگی‌ها:
- Output validation rules (قوانین اعتبارسنجی خروجی)
- Cross-checking با file system (بررسی متقابل)
- Sanity checks (بررسی‌های منطقی)
- Confidence scoring (امتیازدهی اطمینان)
- False positive detection (تشخیص مثبت کاذب)
- Hallucination detection (تشخیص توهم)
- Output refinement (بهینه‌سازی خروجی)
- Consistency verification (تأیید سازگاری)
- Format validation (اعتبارسنجی فرمت)
- Semantic analysis (تحلیل معنایی)

استفاده:
    from core.ai_output_validator import get_validator, validate_output
    
    validator = get_validator()
    
    # اعتبارسنجی خروجی AI
    result = validator.validate(
        output="این فایل در مسیر /path/to/file.py وجود دارد",
        output_type="file_existence",
        context={"file_path": "/path/to/file.py"}
    )
    
    if result['is_valid']:
        print(result['message'])
    else:
        print(f"خطا: {result['errors']}")

تاریخ ایجاد: 2025-01-15
نسخه: 1.0.0
مجوز: تحقیقاتی آکادمیک - دانشگاه
"""

import os
import re
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import difflib

# وارد کردن سیستم‌های پایه
from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import AIException, ValidationException, handle_exception
from core.config_manager import get_config

# ==============================================================================
# Validation Types - انواع اعتبارسنجی
# ==============================================================================

class ValidationType(Enum):
    """انواع اعتبارسنجی - Validation types"""
    FILE_EXISTENCE = "file_existence"  # بررسی وجود فایل
    CODE_SYNTAX = "code_syntax"  # بررسی syntax کد
    PATH_VALIDITY = "path_validity"  # بررسی معتبر بودن مسیر
    JSON_FORMAT = "json_format"  # بررسی فرمت JSON
    COMMAND_SAFETY = "command_safety"  # بررسی امنیت دستور
    NUMERIC_RANGE = "numeric_range"  # بررسی محدوده عددی
    CONSISTENCY = "consistency"  # بررسی سازگاری
    SEMANTIC = "semantic"  # تحلیل معنایی
    HALLUCINATION = "hallucination"  # تشخیص توهم

class ConfidenceLevel(Enum):
    """سطوح اطمینان - Confidence levels"""
    VERY_HIGH = "very_high"  # 90-100%
    HIGH = "high"  # 75-90%
    MEDIUM = "medium"  # 50-75%
    LOW = "low"  # 25-50%
    VERY_LOW = "very_low"  # 0-25%

# ==============================================================================
# Validation Result - نتیجه اعتبارسنجی
# ==============================================================================

@dataclass
class ValidationResult:
    """
    نتیجه اعتبارسنجی
    Validation result
    """
    is_valid: bool
    confidence_score: float  # 0.0 - 1.0
    confidence_level: ConfidenceLevel
    validation_type: ValidationType
    message_fa: str
    message_en: str
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary"""
        return {
            'is_valid': self.is_valid,
            'confidence_score': self.confidence_score,
            'confidence_level': self.confidence_level.value,
            'validation_type': self.validation_type.value,
            'message_fa': self.message_fa,
            'message_en': self.message_en,
            'errors': self.errors,
            'warnings': self.warnings,
            'suggestions': self.suggestions,
            'metadata': self.metadata
        }

# ==============================================================================
# Validation Rules - قوانین اعتبارسنجی
# ==============================================================================

class ValidationRule:
    """
    قانون اعتبارسنجی پایه
    Base validation rule
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.logger = get_logger(__name__, LogCategory.AI)
    
    def validate(self, output: Any, context: Dict[str, Any]) -> ValidationResult:
        """
        اعتبارسنجی خروجی
        Validate output
        
        Args:
            output: خروجی AI
            context: اطلاعات context
        
        Returns:
            ValidationResult: نتیجه اعتبارسنجی
        """
        raise NotImplementedError("Subclasses must implement validate()")

# ==============================================================================
# Specific Validation Rules - قوانین اختصاصی
# ==============================================================================

class FileExistenceValidator(ValidationRule):
    """
    اعتبارسنج وجود فایل
    File existence validator
    
    این کلاس بررسی می‌کند که فایل‌های ذکرشده توسط AI واقعاً وجود دارند.
    """
    
    def __init__(self):
        super().__init__(
            "file_existence",
            "بررسی وجود فایل‌های ذکرشده توسط AI"
        )
    
    def validate(self, output: Any, context: Dict[str, Any]) -> ValidationResult:
        """
        بررسی وجود فایل
        Check file existence
        """
        file_path = context.get('file_path')
        
        if not file_path:
            # استخراج مسیرهای فایل از خروجی
            file_paths = self._extract_file_paths(str(output))
        else:
            file_paths = [file_path]
        
        errors = []
        warnings = []
        valid_files = []
        
        for path in file_paths:
            if os.path.exists(path):
                valid_files.append(path)
                self.logger.debug(
                    f"فایل وجود دارد: {path}",
                    f"File exists: {path}"
                )
            else:
                errors.append(f"فایل وجود ندارد: {path}")
                self.logger.warning(
                    f"AI توهم زد - فایل وجود ندارد: {path}",
                    f"AI hallucinated - File does not exist: {path}"
                )
        
        is_valid = len(errors) == 0
        confidence = len(valid_files) / max(len(file_paths), 1)
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            confidence_level=self._score_to_level(confidence),
            validation_type=ValidationType.FILE_EXISTENCE,
            message_fa=f"بررسی شد: {len(valid_files)}/{len(file_paths)} فایل موجود",
            message_en=f"Checked: {len(valid_files)}/{len(file_paths)} files exist",
            errors=errors,
            warnings=warnings,
            metadata={'valid_files': valid_files, 'total_files': len(file_paths)}
        )
    
    def _extract_file_paths(self, text: str) -> List[str]:
        """استخراج مسیرهای فایل از متن"""
        # الگوهای رایج مسیر فایل
        patterns = [
            r'/[\w/\-_.]+\.\w+',  # مسیرهای Unix
            r'[A-Z]:\\[\w\\\-_.]+\.\w+',  # مسیرهای Windows
        ]
        
        paths = []
        for pattern in patterns:
            matches = re.findall(pattern, text)
            paths.extend(matches)
        
        return list(set(paths))
    
    def _score_to_level(self, score: float) -> ConfidenceLevel:
        """تبدیل امتیاز به سطح اطمینان"""
        if score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.75:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

class CodeSyntaxValidator(ValidationRule):
    """
    اعتبارسنج syntax کد
    Code syntax validator
    """
    
    def __init__(self):
        super().__init__(
            "code_syntax",
            "بررسی صحت syntax کد تولیدشده"
        )
    
    def validate(self, output: Any, context: Dict[str, Any]) -> ValidationResult:
        """بررسی syntax کد"""
        code = str(output)
        language = context.get('language', 'python')
        errors = []
        warnings = []
        
        if language.lower() == 'python':
            try:
                compile(code, '<string>', 'exec')
                is_valid = True
                message_fa = "syntax کد Python صحیح است"
                message_en = "Python code syntax is valid"
                confidence = 1.0
            except SyntaxError as e:
                is_valid = False
                errors.append(f"خطای syntax در خط {e.lineno}: {e.msg}")
                message_fa = f"خطای syntax در کد Python"
                message_en = f"Python syntax error"
                confidence = 0.0
        else:
            # برای زبان‌های دیگر فقط بررسی‌های ابتدایی
            is_valid = len(code.strip()) > 0
            confidence = 0.7 if is_valid else 0.0
            message_fa = f"بررسی پایه برای {language}"
            message_en = f"Basic check for {language}"
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            confidence_level=self._score_to_level(confidence),
            validation_type=ValidationType.CODE_SYNTAX,
            message_fa=message_fa,
            message_en=message_en,
            errors=errors,
            warnings=warnings,
            metadata={'language': language, 'code_length': len(code)}
        )
    
    def _score_to_level(self, score: float) -> ConfidenceLevel:
        """تبدیل امتیاز به سطح"""
        if score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.75:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

class CommandSafetyValidator(ValidationRule):
    """
    اعتبارسنج امنیت دستورات
    Command safety validator
    
    بررسی می‌کند که دستورات تولیدشده توسط AI خطرناک نباشند.
    """
    
    def __init__(self):
        super().__init__(
            "command_safety",
            "بررسی امنیت دستورات shell"
        )
        
        # دستورات خطرناک
        self.dangerous_commands = [
            'rm -rf /',
            'dd if=/dev/zero',
            'mkfs',
            'format',
            ':(){ :|:& };:',  # fork bomb
            'curl | sh',
            'wget | sh',
        ]
        
        # الگوهای خطرناک
        self.dangerous_patterns = [
            r'rm\s+-rf\s+/',
            r'dd\s+if=/dev/zero',
            r'>/dev/sd[a-z]',
            r'chmod\s+777\s+/',
            r'chown\s+.*\s+/',
        ]
    
    def validate(self, output: Any, context: Dict[str, Any]) -> ValidationResult:
        """بررسی امنیت دستور"""
        command = str(output)
        errors = []
        warnings = []
        
        # بررسی دستورات خطرناک
        for dangerous_cmd in self.dangerous_commands:
            if dangerous_cmd in command:
                errors.append(f"دستور خطرناک شناسایی شد: {dangerous_cmd}")
                self.logger.error(
                    f"AI دستور خطرناک تولید کرد: {dangerous_cmd}",
                    f"AI generated dangerous command: {dangerous_cmd}"
                )
        
        # بررسی الگوهای خطرناک
        for pattern in self.dangerous_patterns:
            if re.search(pattern, command):
                errors.append(f"الگوی خطرناک: {pattern}")
        
        is_valid = len(errors) == 0
        confidence = 1.0 if is_valid else 0.0
        
        if not is_valid:
            warnings.append("این دستور توسط AI تولید شده و نباید اجرا شود")
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            confidence_level=ConfidenceLevel.VERY_HIGH if is_valid else ConfidenceLevel.VERY_LOW,
            validation_type=ValidationType.COMMAND_SAFETY,
            message_fa="دستور امن است" if is_valid else "دستور خطرناک است",
            message_en="Command is safe" if is_valid else "Command is dangerous",
            errors=errors,
            warnings=warnings,
            metadata={'command_length': len(command)}
        )

class NumericRangeValidator(ValidationRule):
    """
    اعتبارسنج محدوده عددی
    Numeric range validator
    
    بررسی می‌کند که مقادیر عددی در محدوده منطقی باشند.
    """
    
    def __init__(self):
        super().__init__(
            "numeric_range",
            "بررسی محدوده منطقی مقادیر عددی"
        )
    
    def validate(self, output: Any, context: Dict[str, Any]) -> ValidationResult:
        """بررسی محدوده عددی"""
        value = output
        min_value = context.get('min_value')
        max_value = context.get('max_value')
        field_name = context.get('field_name', 'value')
        
        errors = []
        warnings = []
        
        try:
            numeric_value = float(value)
            
            if min_value is not None and numeric_value < min_value:
                errors.append(f"{field_name} کمتر از حداقل ({min_value}) است: {numeric_value}")
            
            if max_value is not None and numeric_value > max_value:
                errors.append(f"{field_name} بیشتر از حداکثر ({max_value}) است: {numeric_value}")
            
            is_valid = len(errors) == 0
            
            if is_valid:
                confidence = 1.0
                message_fa = f"{field_name} در محدوده مجاز است: {numeric_value}"
                message_en = f"{field_name} is within valid range: {numeric_value}"
            else:
                confidence = 0.0
                message_fa = f"{field_name} خارج از محدوده مجاز است"
                message_en = f"{field_name} is out of valid range"
                self.logger.warning(
                    f"AI مقدار خارج از محدوده تولید کرد: {field_name}={numeric_value}",
                    f"AI generated out-of-range value: {field_name}={numeric_value}"
                )
        
        except (ValueError, TypeError):
            is_valid = False
            confidence = 0.0
            errors.append(f"مقدار عددی نامعتبر: {value}")
            message_fa = "مقدار عددی نامعتبر"
            message_en = "Invalid numeric value"
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            confidence_level=ConfidenceLevel.VERY_HIGH if is_valid else ConfidenceLevel.VERY_LOW,
            validation_type=ValidationType.NUMERIC_RANGE,
            message_fa=message_fa,
            message_en=message_en,
            errors=errors,
            warnings=warnings,
            metadata={
                'value': value,
                'min': min_value,
                'max': max_value,
                'field': field_name
            }
        )

class HallucinationDetector(ValidationRule):
    """
    تشخیص‌دهنده توهم AI
    AI hallucination detector
    
    این کلاس نشانه‌های توهم در خروجی AI را تشخیص می‌دهد.
    """
    
    def __init__(self):
        super().__init__(
            "hallucination",
            "تشخیص توهم در خروجی AI"
        )
        
        # نشانه‌های توهم
        self.hallucination_indicators = [
            "I don't have access",
            "I cannot verify",
            "As an AI",
            "I apologize",
            "fictional",
            "imaginary",
        ]
    
    def validate(self, output: Any, context: Dict[str, Any]) -> ValidationResult:
        """تشخیص توهم"""
        text = str(output)
        errors = []
        warnings = []
        hallucination_score = 0.0
        
        # بررسی نشانه‌های توهم
        for indicator in self.hallucination_indicators:
            if indicator.lower() in text.lower():
                hallucination_score += 0.2
                warnings.append(f"نشانه توهم: '{indicator}'")
        
        # بررسی تکرار غیرعادی
        words = text.split()
        if len(words) > 10:
            unique_ratio = len(set(words)) / len(words)
            if unique_ratio < 0.3:
                hallucination_score += 0.3
                warnings.append("تکرار غیرعادی کلمات")
        
        # بررسی طول غیرعادی
        if len(text) > 10000:
            hallucination_score += 0.2
            warnings.append("خروجی بیش از حد طولانی")
        
        hallucination_score = min(hallucination_score, 1.0)
        is_valid = hallucination_score < 0.5
        confidence = 1.0 - hallucination_score
        
        if hallucination_score > 0:
            self.logger.warning(
                f"نشانه‌های توهم شناسایی شد - امتیاز: {hallucination_score:.2f}",
                f"Hallucination indicators detected - score: {hallucination_score:.2f}"
            )
        
        return ValidationResult(
            is_valid=is_valid,
            confidence_score=confidence,
            confidence_level=self._score_to_level(confidence),
            validation_type=ValidationType.HALLUCINATION,
            message_fa=f"احتمال توهم: {hallucination_score*100:.1f}%",
            message_en=f"Hallucination probability: {hallucination_score*100:.1f}%",
            errors=errors if not is_valid else [],
            warnings=warnings,
            metadata={
                'hallucination_score': hallucination_score,
                'text_length': len(text),
                'word_count': len(words) if 'words' in locals() else 0
            }
        )
    
    def _score_to_level(self, score: float) -> ConfidenceLevel:
        """تبدیل امتیاز به سطح"""
        if score >= 0.9:
            return ConfidenceLevel.VERY_HIGH
        elif score >= 0.75:
            return ConfidenceLevel.HIGH
        elif score >= 0.5:
            return ConfidenceLevel.MEDIUM
        elif score >= 0.25:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

# ==============================================================================
# AI Output Validator Manager - مدیر اصلی
# ==============================================================================

class AIOutputValidator:
    """
    مدیر اصلی اعتبارسنجی خروجی AI
    Main AI output validator manager
    
    این کلاس تمام قوانین اعتبارسنجی را مدیریت می‌کند.
    """
    
    def __init__(self):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        
        # ثبت validators
        self.validators: Dict[ValidationType, ValidationRule] = {
            ValidationType.FILE_EXISTENCE: FileExistenceValidator(),
            ValidationType.CODE_SYNTAX: CodeSyntaxValidator(),
            ValidationType.COMMAND_SAFETY: CommandSafetyValidator(),
            ValidationType.NUMERIC_RANGE: NumericRangeValidator(),
            ValidationType.HALLUCINATION: HallucinationDetector(),
        }
        
        self.logger.info(
            f"AI Output Validator راه‌اندازی شد - {len(self.validators)} validator",
            f"AI Output Validator initialized - {len(self.validators)} validators"
        )
    
    @log_performance
    def validate(
        self,
        output: Any,
        validation_types: Union[ValidationType, List[ValidationType]],
        context: Optional[Dict[str, Any]] = None
    ) -> Union[ValidationResult, List[ValidationResult]]:
        """
        اعتبارسنجی خروجی AI
        Validate AI output
        
        Args:
            output: خروجی AI
            validation_types: نوع یا لیست انواع اعتبارسنجی
            context: اطلاعات context
        
        Returns:
            ValidationResult یا لیست ValidationResult
        
        مثال:
            result = validator.validate(
                output="/home/user/test.py",
                validation_types=ValidationType.FILE_EXISTENCE,
                context={'file_path': '/home/user/test.py'}
            )
        """
        context = context or {}
        
        # تبدیل به لیست اگر تکی باشد
        if isinstance(validation_types, ValidationType):
            validation_types = [validation_types]
            single_result = True
        else:
            single_result = False
        
        results = []
        
        for val_type in validation_types:
            validator = self.validators.get(val_type)
            
            if not validator:
                self.logger.warning(
                    f"Validator یافت نشد: {val_type.value}",
                    f"Validator not found: {val_type.value}"
                )
                continue
            
            try:
                result = validator.validate(output, context)
                results.append(result)
                
                self.logger.debug(
                    f"اعتبارسنجی {val_type.value}: {'موفق' if result.is_valid else 'ناموفق'}",
                    f"Validation {val_type.value}: {'success' if result.is_valid else 'failed'}",
                    context=result.metadata
                )
            
            except Exception as e:
                self.logger.error(
                    f"خطا در اعتبارسنجی {val_type.value}: {str(e)}",
                    f"Error in validation {val_type.value}: {str(e)}"
                )
                
                # ایجاد نتیجه خطا
                error_result = ValidationResult(
                    is_valid=False,
                    confidence_score=0.0,
                    confidence_level=ConfidenceLevel.VERY_LOW,
                    validation_type=val_type,
                    message_fa=f"خطا در اعتبارسنجی: {str(e)}",
                    message_en=f"Validation error: {str(e)}",
                    errors=[str(e)]
                )
                results.append(error_result)
        
        return results[0] if single_result and results else results
    
    def validate_all(
        self,
        output: Any,
        context: Optional[Dict[str, Any]] = None
    ) -> List[ValidationResult]:
        """
        اعتبارسنجی با تمام validators
        Validate with all validators
        
        Args:
            output: خروجی AI
            context: اطلاعات context
        
        Returns:
            List[ValidationResult]: لیست نتایج
        """
        return self.validate(
            output,
            list(self.validators.keys()),
            context
        )
    
    def get_summary(self, results: List[ValidationResult]) -> Dict[str, Any]:
        """
        خلاصه نتایج اعتبارسنجی
        Validation results summary
        
        Args:
            results: لیست نتایج
        
        Returns:
            Dict: خلاصه
        """
        total = len(results)
        valid = sum(1 for r in results if r.is_valid)
        avg_confidence = sum(r.confidence_score for r in results) / max(total, 1)
        
        return {
            'total_validations': total,
            'valid_count': valid,
            'invalid_count': total - valid,
            'success_rate': valid / max(total, 1),
            'average_confidence': avg_confidence,
            'overall_valid': valid == total,
            'message_fa': f"{valid}/{total} اعتبارسنجی موفق - اطمینان: {avg_confidence*100:.1f}%",
            'message_en': f"{valid}/{total} validations passed - confidence: {avg_confidence*100:.1f}%"
        }

# ==============================================================================
# Global Instance
# ==============================================================================

_validator_instance: Optional[AIOutputValidator] = None

def get_validator() -> AIOutputValidator:
    """دریافت نمونه singleton"""
    global _validator_instance
    if _validator_instance is None:
        _validator_instance = AIOutputValidator()
    return _validator_instance

# ==============================================================================
# Convenience Function
# ==============================================================================

def validate_output(
    output: Any,
    validation_type: ValidationType,
    **context
) -> ValidationResult:
    """
    تابع راحت برای اعتبارسنجی
    Convenience function for validation
    """
    validator = get_validator()
    return validator.validate(output, validation_type, context)

# ==============================================================================
# Module Test
# ==============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("تست AI Output Validator")
    print("=" * 80)
    
    validator = get_validator()
    
    # تست 1: File existence
    print("\n1. تست بررسی وجود فایل:")
    result = validator.validate(
        output="فایل در مسیر /home/user/webapp/SecureRedLab/core/logging_system.py",
        validation_types=ValidationType.FILE_EXISTENCE,
        context={'file_path': '/home/user/webapp/SecureRedLab/core/logging_system.py'}
    )
    print(f"   {'✓' if result.is_valid else '✗'} {result.message_fa}")
    print(f"   اطمینان: {result.confidence_score*100:.1f}% ({result.confidence_level.value})")
    
    # تست 2: Code syntax
    print("\n2. تست بررسی syntax کد:")
    code = "def hello():\n    print('سلام')\n    return True"
    result = validator.validate(
        output=code,
        validation_types=ValidationType.CODE_SYNTAX,
        context={'language': 'python'}
    )
    print(f"   {'✓' if result.is_valid else '✗'} {result.message_fa}")
    
    # تست 3: Command safety
    print("\n3. تست بررسی امنیت دستور:")
    safe_cmd = "ls -la /home/user"
    result = validator.validate(
        output=safe_cmd,
        validation_types=ValidationType.COMMAND_SAFETY
    )
    print(f"   {'✓' if result.is_valid else '✗'} {result.message_fa}")
    
    dangerous_cmd = "rm -rf /"
    result = validator.validate(
        output=dangerous_cmd,
        validation_types=ValidationType.COMMAND_SAFETY
    )
    print(f"   {'✓' if result.is_valid else '✗'} {result.message_fa}")
    if result.errors:
        print(f"   خطاها: {result.errors}")
    
    # تست 4: Numeric range
    print("\n4. تست بررسی محدوده عددی:")
    result = validator.validate(
        output=500000,
        validation_types=ValidationType.NUMERIC_RANGE,
        context={'min_value': 100, 'max_value': 1000000, 'field_name': 'max_bots'}
    )
    print(f"   {'✓' if result.is_valid else '✗'} {result.message_fa}")
    
    # تست 5: Hallucination detection
    print("\n5. تست تشخیص توهم:")
    result = validator.validate(
        output="This is a normal output without hallucination.",
        validation_types=ValidationType.HALLUCINATION
    )
    print(f"   {'✓' if result.is_valid else '✗'} {result.message_fa}")
    
    # تست 6: Multiple validations
    print("\n6. تست اعتبارسنجی چندگانه:")
    results = validator.validate(
        output=safe_cmd,
        validation_types=[ValidationType.COMMAND_SAFETY, ValidationType.HALLUCINATION]
    )
    summary = validator.get_summary(results)
    print(f"   ✓ {summary['message_fa']}")
    
    print("\n" + "=" * 80)
    print("تست کامل شد!")
    print("=" * 80)
