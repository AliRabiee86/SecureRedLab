#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Offline AI Core Engine
======================================

هسته هوش مصنوعی کاملاً آفلاین با پشتیبانی از:
- مدل‌های Reasoning (Qwen3-235B-A22B, GLM-4.6-Reasoning)
- مدل‌های Non-Reasoning (DeepSeek-V3.2-Exp, Qwen3-Coder-480B)
- VLM Models (Qwen2.5-VL-72B, InternVL2-8B, MiniCPM-V-4.5, Hunyuan-OCR)
- سیستم ضد-Hallucination با 7 Guardrail
- Dual-Track Routing (Reasoning vs Non-Reasoning)
- Model Registry با اولویت‌بندی خودکار
- vLLM Integration برای سرعت بالا
- QLORA Fine-tuning Ready

Architecture:
    ┌──────────────────────────────────────────┐
    │         Offline AI Core                  │
    ├──────────────────────────────────────────┤
    │  1. Model Registry                       │
    │     - 7 مدل (4 LLM + 3 VLM)              │
    │     - Metadata & Capabilities            │
    │     - Priority & Fallback Logic          │
    │                                          │
    │  2. vLLM Client                          │
    │     - Local inference                    │
    │     - Batch processing                   │
    │     - Context management                 │
    │                                          │
    │  3. Dual-Track Router                    │
    │     - Task classification                │
    │     - Reasoning detection                │
    │     - Model selection                    │
    │                                          │
    │  4. Anti-Hallucination System            │
    │     - 7 Guardrails                       │
    │     - Confidence scoring                 │
    │     - Fact verification                  │
    └──────────────────────────────────────────┘

Usage:
    from ai.offline_core import get_offline_ai, TaskType
    
    ai = get_offline_ai()
    
    # Reasoning task
    result = ai.generate(
        prompt="Analyze this SQL injection vulnerability...",
        task_type=TaskType.REASONING,
        max_tokens=2000
    )
    
    # Non-reasoning task (fast)
    result = ai.generate(
        prompt="Generate a Python exploit script for CVE-2024-12345",
        task_type=TaskType.CODE_GENERATION,
        max_tokens=1000
    )

تاریخ: 2025-12-08
نسخه: 1.0.0
"""

import os
import sys
import json
import time
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, field, asdict
from collections import defaultdict

# Core imports
from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import (
    handle_exception, retry_on_failure,
    AIException, ValidationException,
    ErrorSeverity, RecoveryStrategy
)
from core.config_manager import get_config
from core.database_manager import get_db_manager


# ==============================================================================
# Enums & Data Classes
# ==============================================================================

class TaskType(Enum):
    """نوع تسک برای Dual-Track Routing"""
    # Reasoning Track (نیاز به تفکر عمیق)
    REASONING = "reasoning"                  # تحلیل پیچیده
    VULNERABILITY_ANALYSIS = "vuln_analysis"  # تحلیل آسیب‌پذیری
    ATTACK_STRATEGY = "attack_strategy"      # طراحی استراتژی حمله
    SECURITY_AUDIT = "security_audit"        # ممیزی امنیتی
    
    # Non-Reasoning Track (نیاز به سرعت)
    CODE_GENERATION = "code_generation"      # تولید کد
    EXPLOIT_GENERATION = "exploit_generation" # تولید exploit
    PAYLOAD_CRAFTING = "payload_crafting"    # ساخت payload
    FAST_SCAN = "fast_scan"                  # اسکن سریع
    
    # VLM Track
    IMAGE_ANALYSIS = "image_analysis"        # تحلیل تصویر
    SCREENSHOT_OCR = "screenshot_ocr"        # OCR از اسکرین‌شات
    DOCUMENT_PARSING = "document_parsing"    # پارس مستندات


class ModelType(Enum):
    """نوع مدل"""
    # LLM Models - Reasoning
    QWEN3_235B = "qwen3-235b-a22b"          # Primary Reasoning
    GLM_46_REASONING = "glm-4.6-reasoning"   # Fallback Reasoning
    
    # LLM Models - Non-Reasoning
    DEEPSEEK_V32_EXP = "deepseek-v3.2-exp"  # Primary Non-Reasoning
    QWEN3_CODER_480B = "qwen3-coder-480b"   # Secondary Non-Reasoning
    GLM_46 = "glm-4.6"                      # Fallback Non-Reasoning
    
    # VLM Models
    QWEN25_VL_72B = "qwen2.5-vl-72b-awq"    # Primary VLM
    INTERNVL2_8B = "internvl2-8b"           # Fallback VLM
    MINICPM_V45 = "minicpm-v-4.5"           # Budget VLM
    HUNYUAN_OCR = "hunyuan-ocr"             # Pure OCR


class ModelCapability(Enum):
    """قابلیت‌های مدل"""
    REASONING = "reasoning"
    CODE_GENERATION = "code_generation"
    MATH = "math"
    VISION = "vision"
    OCR = "ocr"
    DOCUMENT_UNDERSTANDING = "document_understanding"
    MULTILINGUAL = "multilingual"
    LONG_CONTEXT = "long_context"


@dataclass
class ModelMetadata:
    """اطلاعات متا مدل"""
    name: str
    model_type: ModelType
    path: str                          # مسیر local model
    vram_required_gb: int              # VRAM مورد نیاز (GB)
    max_context_length: int            # حداکثر طول context
    capabilities: List[ModelCapability]
    priority: int                      # 1 = highest priority
    
    # Performance metrics
    avg_latency_ms: float = 2000.0
    tokens_per_second: float = 50.0
    hallucination_rate: float = 0.05   # 5%
    
    # Benchmarks
    mmlu_score: Optional[float] = None
    humaneval_score: Optional[float] = None
    aime_score: Optional[float] = None
    
    loaded: bool = False
    last_used: Optional[datetime] = None


@dataclass
class GenerationConfig:
    """تنظیمات generation"""
    max_tokens: int = 2000
    temperature: float = 0.7
    top_p: float = 0.9
    top_k: int = 40
    repetition_penalty: float = 1.1
    stop_sequences: List[str] = field(default_factory=list)
    
    # Anti-hallucination
    enable_guardrails: bool = True
    min_confidence_score: float = 0.7
    enable_fact_checking: bool = True


@dataclass
class GenerationResult:
    """نتیجه generation"""
    text: str
    model_used: ModelType
    latency_ms: float
    tokens_generated: int
    
    # Anti-hallucination scores
    confidence_score: float = 1.0
    hallucination_detected: bool = False
    guardrails_triggered: List[str] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    task_type: Optional[TaskType] = None


# ==============================================================================
# Model Registry
# ==============================================================================

class ModelRegistry:
    """
    رجیستری مدل‌ها
    
    نگهداری metadata تمام مدل‌ها و مدیریت اولویت‌بندی
    """
    
    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        self.models: Dict[ModelType, ModelMetadata] = {}
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """راه‌اندازی رجیستری مدل‌ها"""
        base_path = Path(self.config.get('ai.models_base_path', '/models'))
        
        # LLM Models - Reasoning
        self.models[ModelType.QWEN3_235B] = ModelMetadata(
            name="Qwen3-235B-A22B-Instruct",
            model_type=ModelType.QWEN3_235B,
            path=str(base_path / "Qwen3-235B-A22B-Instruct"),
            vram_required_gb=59,
            max_context_length=128000,
            capabilities=[
                ModelCapability.REASONING,
                ModelCapability.CODE_GENERATION,
                ModelCapability.MATH,
                ModelCapability.MULTILINGUAL,
                ModelCapability.LONG_CONTEXT
            ],
            priority=1,
            avg_latency_ms=2500,
            tokens_per_second=45,
            hallucination_rate=0.038,
            mmlu_score=88.6,
            humaneval_score=88.4,
            aime_score=88.2
        )
        
        self.models[ModelType.GLM_46_REASONING] = ModelMetadata(
            name="GLM-4.6-Reasoning",
            model_type=ModelType.GLM_46_REASONING,
            path=str(base_path / "GLM-4.6-Reasoning"),
            vram_required_gb=2,
            max_context_length=200000,
            capabilities=[
                ModelCapability.REASONING,
                ModelCapability.CODE_GENERATION,
                ModelCapability.MATH,
                ModelCapability.MULTILINGUAL
            ],
            priority=2,
            avg_latency_ms=1800,
            tokens_per_second=60,
            hallucination_rate=0.042,
            mmlu_score=85.0,
            humaneval_score=82.0,
            aime_score=93.9
        )
        
        # LLM Models - Non-Reasoning
        self.models[ModelType.DEEPSEEK_V32_EXP] = ModelMetadata(
            name="DeepSeek-V3.2-Exp",
            model_type=ModelType.DEEPSEEK_V32_EXP,
            path=str(base_path / "DeepSeek-V3.2-Exp"),
            vram_required_gb=72,
            max_context_length=128000,
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.MULTILINGUAL,
                ModelCapability.LONG_CONTEXT
            ],
            priority=1,
            avg_latency_ms=1500,
            tokens_per_second=120,
            hallucination_rate=0.038,
            mmlu_score=87.0,
            humaneval_score=88.0
        )
        
        self.models[ModelType.GLM_46] = ModelMetadata(
            name="GLM-4.6",
            model_type=ModelType.GLM_46,
            path=str(base_path / "GLM-4.6"),
            vram_required_gb=2,
            max_context_length=200000,
            capabilities=[
                ModelCapability.CODE_GENERATION,
                ModelCapability.MULTILINGUAL
            ],
            priority=3,
            avg_latency_ms=1200,
            tokens_per_second=80,
            hallucination_rate=0.045,
            mmlu_score=84.0,
            humaneval_score=80.0
        )
        
        # VLM Models
        self.models[ModelType.QWEN25_VL_72B] = ModelMetadata(
            name="Qwen2.5-VL-72B-AWQ",
            model_type=ModelType.QWEN25_VL_72B,
            path=str(base_path / "Qwen2.5-VL-72B-AWQ"),
            vram_required_gb=36,
            max_context_length=32768,
            capabilities=[
                ModelCapability.VISION,
                ModelCapability.OCR,
                ModelCapability.DOCUMENT_UNDERSTANDING,
                ModelCapability.MULTILINGUAL
            ],
            priority=1,
            avg_latency_ms=3000,
            tokens_per_second=35,
            hallucination_rate=0.047
        )
        
        self.models[ModelType.HUNYUAN_OCR] = ModelMetadata(
            name="Hunyuan-OCR",
            model_type=ModelType.HUNYUAN_OCR,
            path=str(base_path / "Hunyuan-OCR"),
            vram_required_gb=1,
            max_context_length=8192,
            capabilities=[
                ModelCapability.OCR,
                ModelCapability.MULTILINGUAL
            ],
            priority=1,
            avg_latency_ms=800,
            tokens_per_second=100,
            hallucination_rate=0.020  # Very low hallucination for OCR
        )
        
        self.logger.info(
            f"رجیستری مدل با {len(self.models)} مدل راه‌اندازی شد",
            f"Model registry initialized with {len(self.models)} models"
        )
    
    def get_model(self, model_type: ModelType) -> Optional[ModelMetadata]:
        """دریافت اطلاعات یک مدل"""
        return self.models.get(model_type)
    
    def get_models_by_capability(self, capability: ModelCapability) -> List[ModelMetadata]:
        """دریافت تمام مدل‌هایی که قابلیت مشخص را دارند"""
        return sorted(
            [m for m in self.models.values() if capability in m.capabilities],
            key=lambda m: m.priority
        )
    
    def get_best_model_for_task(self, 
                                 task_type: TaskType,
                                 max_vram_gb: Optional[int] = None) -> Optional[ModelMetadata]:
        """
        انتخاب بهترین مدل برای یک تسک خاص
        
        Args:
            task_type: نوع تسک
            max_vram_gb: حداکثر VRAM در دسترس
        
        Returns:
            بهترین مدل یا None
        """
        # Map task to required capability
        task_capability_map = {
            TaskType.REASONING: ModelCapability.REASONING,
            TaskType.VULNERABILITY_ANALYSIS: ModelCapability.REASONING,
            TaskType.ATTACK_STRATEGY: ModelCapability.REASONING,
            TaskType.SECURITY_AUDIT: ModelCapability.REASONING,
            TaskType.CODE_GENERATION: ModelCapability.CODE_GENERATION,
            TaskType.EXPLOIT_GENERATION: ModelCapability.CODE_GENERATION,
            TaskType.PAYLOAD_CRAFTING: ModelCapability.CODE_GENERATION,
            TaskType.FAST_SCAN: ModelCapability.CODE_GENERATION,
            TaskType.IMAGE_ANALYSIS: ModelCapability.VISION,
            TaskType.SCREENSHOT_OCR: ModelCapability.OCR,
            TaskType.DOCUMENT_PARSING: ModelCapability.DOCUMENT_UNDERSTANDING
        }
        
        required_capability = task_capability_map.get(task_type)
        if not required_capability:
            return None
        
        # Get models with required capability
        candidates = self.get_models_by_capability(required_capability)
        
        # Filter by VRAM if specified
        if max_vram_gb:
            candidates = [m for m in candidates if m.vram_required_gb <= max_vram_gb]
        
        # Return highest priority (lowest number)
        return candidates[0] if candidates else None
    
    def update_model_stats(self, 
                          model_type: ModelType,
                          latency_ms: float,
                          success: bool):
        """بروزرسانی آمار استفاده از مدل"""
        model = self.models.get(model_type)
        if model:
            model.last_used = datetime.now()
            # EMA update for latency
            alpha = 0.1
            model.avg_latency_ms = (alpha * latency_ms + 
                                    (1 - alpha) * model.avg_latency_ms)


# ==============================================================================
# Offline AI Core - Main Class
# ==============================================================================

class OfflineAICore:
    """
    هسته اصلی AI آفلاین
    
    این کلاس تمام کامپوننت‌های AI را یکپارچه می‌کند:
    - Model Registry
    - vLLM Client
    - Dual-Track Router
    - Anti-Hallucination System
    """
    
    def __init__(self):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        
        # Initialize components
        self.model_registry = ModelRegistry(self.config, self.logger)
        
        # Import and initialize other components
        from ai.vllm_client import get_vllm_client
        from ai.dual_track_router import get_dual_track_router
        from ai.anti_hallucination import get_anti_hallucination_system
        
        self.vllm_client = get_vllm_client()
        self.vllm_client.set_model_registry(self.model_registry)
        
        self.router = get_dual_track_router(self.model_registry)
        
        self.anti_hallucination = get_anti_hallucination_system(
            min_confidence=self.config.get('ai.min_confidence', 0.7)
        )
        
        self.logger.info(
            "Offline AI Core راه‌اندازی شد (100% آفلاین)",
            "Offline AI Core initialized (100% offline)",
            context={
                'models_registered': len(self.model_registry.models),
                'anti_hallucination_enabled': True
            }
        )
    
    @log_performance
    @handle_exception(fallback_value=None)
    async def generate(self,
                      prompt: str,
                      task_type: Optional[TaskType] = None,
                      config: Optional[GenerationConfig] = None,
                      prefer_speed: bool = False) -> Optional[GenerationResult]:
        """
        تولید متن با AI آفلاین
        
        Args:
            prompt: متن prompt
            task_type: نوع تسک (اگر None، خودکار تشخیص داده می‌شود)
            config: تنظیمات generation
            prefer_speed: اولویت با سرعت؟
        
        Returns:
            نتیجه generation + hallucination check
        """
        if config is None:
            config = GenerationConfig()
        
        # 1. Route to appropriate track
        if task_type is None:
            task_type, model_type = self.router.route(prompt, prefer_speed=prefer_speed)
        else:
            model_type = self.router._select_model(task_type, prefer_speed)
        
        self.logger.info(
            f"درخواست generation: {task_type.value} → {model_type.value}",
            f"Generation request: {task_type.value} → {model_type.value}",
            context={'prompt_length': len(prompt)}
        )
        
        # 2. Generate with vLLM
        result = await self.vllm_client.generate(model_type, prompt, config)
        
        if not result:
            raise AIException("Generation failed")
        
        # 3. Anti-hallucination check
        if config.enable_guardrails:
            hallucination_report = self.anti_hallucination.check(
                text=result.text,
                model_type=model_type,
                task_prompt=prompt,
                enable_all=True
            )
            
            # Update result with hallucination info
            result.confidence_score = hallucination_report.confidence_score
            result.hallucination_detected = hallucination_report.is_hallucinated
            result.guardrails_triggered = hallucination_report.triggered_guardrails
            
            # Log if hallucination detected
            if hallucination_report.is_hallucinated:
                self.logger.warning(
                    "⚠️ Hallucination شناسایی شد",
                    "Hallucination detected",
                    context={
                        'confidence': hallucination_report.confidence_score,
                        'guardrails': hallucination_report.triggered_guardrails
                    }
                )
        
        result.task_type = task_type
        
        return result
    
    async def generate_stream(self,
                             prompt: str,
                             task_type: Optional[TaskType] = None,
                             config: Optional[GenerationConfig] = None):
        """
        Stream generation (برای UI responsive)
        """
        if config is None:
            config = GenerationConfig()
        
        # Route
        if task_type is None:
            task_type, model_type = self.router.route(prompt)
        else:
            model_type = self.router._select_model(task_type, False)
        
        # Stream from vLLM
        async for chunk in self.vllm_client.generate_stream(model_type, prompt, config):
            yield chunk
    
    def get_statistics(self) -> Dict:
        """دریافت آمار کلی سیستم"""
        return {
            'vllm': self.vllm_client.get_stats(),
            'router': self.router.get_statistics(),
            'anti_hallucination': self.anti_hallucination.get_statistics(),
            'loaded_models': [
                mt.value for mt, meta in self.model_registry.models.items()
                if meta.loaded
            ]
        }


# ==============================================================================
# Singleton Instance
# ==============================================================================

_offline_ai_instance = None
_offline_ai_lock = threading.Lock()

def get_offline_ai():
    """دریافت instance سینگلتون Offline AI Core"""
    global _offline_ai_instance
    
    if _offline_ai_instance is None:
        with _offline_ai_lock:
            if _offline_ai_instance is None:
                _offline_ai_instance = OfflineAICore()
    
    return _offline_ai_instance
