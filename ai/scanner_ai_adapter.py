#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Scanner AI Adapter
==================================

Adapter برای اتصال Neural Scanner به Offline AI Core
این adapter interface قدیمی ai_core_engine را به offline_core + vlm_core تبدیل می‌کند

Features:
- Backward compatibility با ai_core_engine
- Automatic routing به LLM یا VLM
- Response format conversion
- Error handling و fallback

تاریخ: 2025-12-08
"""

import asyncio
from typing import Dict, Optional, Any
from enum import Enum

from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import handle_exception, AIException
from core.ai_output_validator import get_validator, ValidationType

# Import offline AI cores
from ai.offline_core import get_offline_ai, TaskType, GenerationConfig
from ai.vlm_core import get_vlm_core, VLMTaskType, VLMRequest


# ==============================================================================
# Enums for Compatibility
# ==============================================================================

class AIModelType(Enum):
    """انواع مدل AI (برای سازگاری با کد قدیمی)"""
    DEEPSEEK_CODER = "deepseek_coder_33b"
    LLAMA_3_1 = "llama_3_1_70b"
    MIXTRAL_8x22B = "mixtral_8x22b"
    QWEN_14B = "qwen_14b"
    GLM_4_6 = "glm_4_6"


# ==============================================================================
# Model Manager (Adapter Pattern)
# ==============================================================================

class OfflineModelManager:
    """
    مدیریت مدل‌های آفلاین
    این کلاس interface قدیمی را حفظ می‌کند اما از offline cores استفاده می‌کند
    """
    
    def __init__(self):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.validator = get_validator()
        
        # Initialize offline cores
        self.llm_core = get_offline_ai()
        self.vlm_core = get_vlm_core()
        
        # Statistics
        self.generation_count = 0
        
        self.logger.info(
            "Offline Model Manager راه‌اندازی شد (LLM + VLM)",
            "Offline Model Manager initialized (LLM + VLM)"
        )
    
    @log_performance
    @handle_exception(fallback_value={'status': 'error', 'output': ''})
    def generate(self,
                prompt: str,
                model_type: AIModelType = AIModelType.QWEN_14B,
                validate_output: bool = True,
                temperature: float = 0.7,
                max_tokens: int = 2048) -> Dict[str, Any]:
        """
        تولید متن با مدل AI (Sync wrapper for async)
        
        Args:
            prompt: متن prompt
            model_type: نوع مدل (برای سازگاری، در واقع TaskType تشخیص می‌شود)
            validate_output: validation خروجی؟
            temperature: دمای تولید
            max_tokens: حداکثر تعداد توکن
        
        Returns:
            Dict شامل:
            - status: 'success' or 'error'
            - output: متن تولید شده
            - model_type: مدل استفاده شده
            - validation: نتیجه validation (اگر validate_output=True)
        """
        try:
            # Run async method in sync context
            result = asyncio.run(self._generate_async(
                prompt,
                model_type,
                validate_output,
                temperature,
                max_tokens
            ))
            
            self.generation_count += 1
            return result
            
        except Exception as e:
            self.logger.error(
                f"خطا در تولید: {e}",
                f"Error in generation: {e}"
            )
            return {
                'status': 'error',
                'output': '',
                'error': str(e)
            }
    
    async def _generate_async(self,
                             prompt: str,
                             model_type: AIModelType,
                             validate_output: bool,
                             temperature: float,
                             max_tokens: int) -> Dict[str, Any]:
        """تولید async واقعی"""
        
        # Detect task type from prompt
        task_type = self._detect_task_type(prompt)
        
        # Configure generation
        config = GenerationConfig(
            temperature=temperature,
            max_tokens=max_tokens,
            top_p=0.9
        )
        
        # Generate with offline LLM
        generation_result = await self.llm_core.generate(
            prompt=prompt,
            task_type=task_type,
            config=config,
            prefer_speed=False
        )
        
        if not generation_result:
            raise AIException("Generation failed")
        
        # Format response
        response = {
            'status': 'success',
            'output': generation_result.text,
            'model_type': generation_result.model_used.value if hasattr(generation_result.model_used, 'value') else str(generation_result.model_used),
            'latency_ms': generation_result.latency_ms,
            'tokens_used': getattr(generation_result, 'tokens', 0)  # fallback to 0 if not present
        }
        
        # Validate if requested
        if validate_output:
            validation_result = self.validator.validate(
                generation_result.text,
                ValidationType.VULNERABILITY_ANALYSIS
            )
            
            response['validation'] = {
                'is_valid': validation_result.is_valid,
                'confidence_score': validation_result.confidence,
                'issues': validation_result.validation_errors
            }
        
        return response
    
    def _detect_task_type(self, prompt: str) -> TaskType:
        """تشخیص نوع تسک از prompt"""
        
        prompt_lower = prompt.lower()
        
        # Vulnerability analysis
        if any(kw in prompt_lower for kw in ['vulnerability', 'exploit', 'cve', 'security']):
            return TaskType.VULNERABILITY_ANALYSIS
        
        # Code generation
        elif any(kw in prompt_lower for kw in ['generate', 'write code', 'implement']):
            return TaskType.CODE_GENERATION
        
        # Analysis (use VULNERABILITY_ANALYSIS as default for security tasks)
        elif any(kw in prompt_lower for kw in ['analyze', 'explain', 'assess']):
            return TaskType.VULNERABILITY_ANALYSIS
        
        # Default: vulnerability analysis (for security scanner)
        return TaskType.VULNERABILITY_ANALYSIS
    
    def get_statistics(self) -> Dict:
        """دریافت آمار"""
        return {
            'generation_count': self.generation_count,
            'llm_stats': self.llm_core.get_statistics(),
            'vlm_stats': self.vlm_core.get_statistics()
        }


# ==============================================================================
# AI Engine (Adapter for Scanner)
# ==============================================================================

class ScannerAIEngine:
    """
    موتور AI برای Scanner
    این کلاس interface قدیمی ai_core_engine را شبیه‌سازی می‌کند
    """
    
    def __init__(self):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.model_manager = OfflineModelManager()
        
        self.logger.info(
            "Scanner AI Engine راه‌اندازی شد (100% آفلاین)",
            "Scanner AI Engine initialized (100% offline)"
        )
    
    def get_statistics(self) -> Dict:
        """دریافت آمار"""
        return self.model_manager.get_statistics()


# ==============================================================================
# Singleton
# ==============================================================================

_scanner_ai_engine_instance: Optional[ScannerAIEngine] = None

def get_scanner_ai_engine() -> ScannerAIEngine:
    """دریافت instance سینگلتون Scanner AI Engine"""
    global _scanner_ai_engine_instance
    
    if _scanner_ai_engine_instance is None:
        _scanner_ai_engine_instance = ScannerAIEngine()
    
    return _scanner_ai_engine_instance


# ==============================================================================
# Backward Compatibility Alias
# ==============================================================================

# برای سازگاری با کد قدیمی که get_ai_engine() صدا می‌زند
def get_ai_engine() -> ScannerAIEngine:
    """
    Alias برای سازگاری با کد قدیمی
    این تابع همان get_scanner_ai_engine است
    """
    return get_scanner_ai_engine()
