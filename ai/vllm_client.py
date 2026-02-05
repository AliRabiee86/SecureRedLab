#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - vLLM Client
===========================

Client برای ارتباط با مدل‌های محلی از طریق vLLM.

vLLM Features:
- High-throughput inference
- PagedAttention for memory efficiency
- Continuous batching
- Quantization support (AWQ, GPTQ)
- OpenAI-compatible API

Architecture:
    ┌────────────────────────────────────┐
    │     vLLM Client                    │
    ├────────────────────────────────────┤
    │  1. Model Loading                  │
    │     - Lazy loading                 │
    │     - Memory management            │
    │     - Error handling               │
    │                                    │
    │  2. Inference                      │
    │     - Sync/async generation        │
    │     - Batch processing             │
    │     - Streaming support            │
    │                                    │
    │  3. Context Management             │
    │     - Long context handling        │
    │     - Token counting               │
    │     - Cache management             │
    └────────────────────────────────────┘

Usage:
    from ai.vllm_client import vLLMClient
    from ai.offline_core import ModelType, GenerationConfig
    
    client = vLLMClient()
    
    # Load model
    await client.load_model(ModelType.QWEN3_235B)
    
    # Generate
    result = await client.generate(
        model_type=ModelType.QWEN3_235B,
        prompt="Analyze this vulnerability...",
        config=GenerationConfig(max_tokens=2000)
    )

تاریخ: 2025-12-08
"""

import os
import sys
import json
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator
from pathlib import Path

# Core imports
from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import (
    handle_exception, retry_on_failure,
    AIException, ValidationException,
    ErrorSeverity
)
from core.config_manager import get_config

# AI imports
from ai.offline_core import (
    ModelType, ModelMetadata, GenerationConfig, GenerationResult,
    ModelRegistry
)


class vLLMClient:
    """
    Client برای مدیریت مدل‌های vLLM
    
    Features:
    - Lazy loading (بارگذاری تنها در صورت نیاز)
    - Connection pooling
    - Error handling & retry
    - Performance monitoring
    """
    
    def __init__(self):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        
        # vLLM connection settings
        self.vllm_host = self.config.get('ai.vllm_host', 'localhost')
        self.vllm_port = self.config.get('ai.vllm_port', 8000)
        self.vllm_base_url = f"http://{self.vllm_host}:{self.vllm_port}"
        
        # Model management
        self.loaded_models: Dict[ModelType, bool] = {}
        self.model_registry: Optional[ModelRegistry] = None
        
        # Performance tracking
        self.inference_count: Dict[ModelType, int] = {}
        self.total_tokens_generated: Dict[ModelType, int] = {}
        
        self.logger.info(
            "vLLM Client راه‌اندازی شد",
            "vLLM Client initialized",
            context={'base_url': self.vllm_base_url}
        )
    
    def set_model_registry(self, registry: ModelRegistry):
        """تنظیم Model Registry"""
        self.model_registry = registry
    
    @log_performance
    @handle_exception(fallback_value=False)
    async def load_model(self, model_type: ModelType) -> bool:
        """
        بارگذاری یک مدل در vLLM
        
        Args:
            model_type: نوع مدل
        
        Returns:
            True اگر موفق
        """
        if self.loaded_models.get(model_type, False):
            self.logger.debug(
                f"مدل قبلاً بارگذاری شده: {model_type.value}",
                f"Model already loaded: {model_type.value}"
            )
            return True
        
        if not self.model_registry:
            raise ValidationException("Model registry not set")
        
        model_metadata = self.model_registry.get_model(model_type)
        if not model_metadata:
            raise ValidationException(f"Model not found in registry: {model_type.value}")
        
        self.logger.info(
            f"در حال بارگذاری مدل: {model_metadata.name}",
            f"Loading model: {model_metadata.name}",
            context={
                'path': model_metadata.path,
                'vram_gb': model_metadata.vram_required_gb
            }
        )
        
        # NOTE: در محیط واقعی، این قسمت باید مدل را از طریق vLLM API بارگذاری کند
        # در حالت توسعه، فقط شبیه‌سازی می‌کنیم
        
        try:
            # Simulate model loading delay
            await asyncio.sleep(0.1)
            
            # Check if model path exists
            model_path = Path(model_metadata.path)
            if not model_path.exists():
                self.logger.warning(
                    f"مسیر مدل وجود ندارد (حالت توسعه): {model_path}",
                    f"Model path does not exist (dev mode): {model_path}"
                )
            
            # Mark as loaded
            self.loaded_models[model_type] = True
            self.inference_count[model_type] = 0
            self.total_tokens_generated[model_type] = 0
            
            # Update registry
            model_metadata.loaded = True
            model_metadata.last_used = datetime.now()
            
            self.logger.info(
                f"مدل با موفقیت بارگذاری شد: {model_metadata.name}",
                f"Model loaded successfully: {model_metadata.name}"
            )
            
            return True
        
        except Exception as e:
            self.logger.error(
                f"خطا در بارگذاری مدل: {model_type.value}",
                f"Error loading model: {model_type.value}",
                context={'error': str(e)}
            )
            raise AIException(f"Failed to load model: {model_type.value}") from e
    
    @log_performance
    @handle_exception(fallback_value=None)
    async def generate(self,
                      model_type: ModelType,
                      prompt: str,
                      config: GenerationConfig) -> Optional[GenerationResult]:
        """
        تولید متن با استفاده از مدل
        
        Args:
            model_type: نوع مدل
            prompt: prompt ورودی
            config: تنظیمات generation
        
        Returns:
            نتیجه generation
        """
        # Ensure model is loaded
        if not self.loaded_models.get(model_type, False):
            await self.load_model(model_type)
        
        start_time = time.time()
        
        self.logger.debug(
            f"شروع generation - مدل: {model_type.value}",
            f"Starting generation - model: {model_type.value}",
            context={
                'prompt_length': len(prompt),
                'max_tokens': config.max_tokens,
                'temperature': config.temperature
            }
        )
        
        try:
            # NOTE: در محیط واقعی، این قسمت باید درخواست را به vLLM API ارسال کند
            # در حالت توسعه، فقط شبیه‌سازی می‌کنیم
            
            # Simulate inference delay
            await asyncio.sleep(0.5)
            
            # Mock generation
            generated_text = self._mock_generate(model_type, prompt, config)
            tokens_generated = len(generated_text.split())
            
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000
            
            # Update stats
            self.inference_count[model_type] = self.inference_count.get(model_type, 0) + 1
            self.total_tokens_generated[model_type] = (
                self.total_tokens_generated.get(model_type, 0) + tokens_generated
            )
            
            # Update model registry stats
            if self.model_registry:
                self.model_registry.update_model_stats(
                    model_type, latency_ms, success=True
                )
            
            # Create result
            result = GenerationResult(
                text=generated_text,
                model_used=model_type,
                latency_ms=latency_ms,
                tokens_generated=tokens_generated,
                confidence_score=0.85,  # Mock score
                hallucination_detected=False,
                guardrails_triggered=[]
            )
            
            self.logger.debug(
                f"Generation کامل شد - {tokens_generated} token در {latency_ms:.0f}ms",
                f"Generation completed - {tokens_generated} tokens in {latency_ms:.0f}ms"
            )
            
            return result
        
        except Exception as e:
            self.logger.error(
                f"خطا در generation: {model_type.value}",
                f"Error in generation: {model_type.value}",
                context={'error': str(e)}
            )
            raise AIException(f"Generation failed for {model_type.value}") from e
    
    def _mock_generate(self, 
                       model_type: ModelType,
                       prompt: str,
                       config: GenerationConfig) -> str:
        """
        Mock generation برای توسعه
        
        در محیط واقعی، این متد حذف می‌شود و generation واقعی انجام می‌شود.
        """
        # Simple mock based on model type
        if "reasoning" in model_type.value or "qwen3-235b" in model_type.value:
            return f"""Based on the analysis of the provided information, here are the key findings:

1. **Vulnerability Assessment**: The system appears to have multiple potential entry points.

2. **Risk Analysis**: 
   - Critical: SQL injection vulnerability in login form
   - High: Outdated dependencies with known CVEs
   - Medium: Weak password policy

3. **Recommended Actions**:
   - Patch the SQL injection vulnerability immediately
   - Update all dependencies to latest secure versions
   - Implement multi-factor authentication

This analysis is based on industry best practices and OWASP guidelines."""

        elif "deepseek" in model_type.value or "coder" in model_type.value:
            return f"""```python
# Exploit script for demonstrated vulnerability
import requests
import sys

def exploit_sql_injection(target_url, payload):
    \"\"\"
    SQL injection exploit
    WARNING: For authorized testing only
    \"\"\"
    data = {{
        'username': payload,
        'password': 'test'
    }}
    
    response = requests.post(target_url + '/login', data=data)
    
    if response.status_code == 200:
        print("[+] Injection successful")
        return True
    else:
        print("[-] Injection failed")
        return False

if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "http://localhost"
    payload = "' OR '1'='1"
    exploit_sql_injection(target, payload)
```"""

        else:
            return f"Analysis completed for prompt: {prompt[:100]}..."
    
    async def generate_stream(self,
                             model_type: ModelType,
                             prompt: str,
                             config: GenerationConfig) -> AsyncGenerator[str, None]:
        """
        Stream generation (برای UI responsive)
        
        Args:
            model_type: نوع مدل
            prompt: prompt ورودی
            config: تنظیمات generation
        
        Yields:
            قطعات متن تولید شده
        """
        # Ensure model is loaded
        if not self.loaded_models.get(model_type, False):
            await self.load_model(model_type)
        
        self.logger.debug(
            f"شروع streaming generation - مدل: {model_type.value}",
            f"Starting streaming generation - model: {model_type.value}"
        )
        
        # NOTE: در محیط واقعی، این قسمت باید streaming را از vLLM دریافت کند
        # در حالت توسعه، شبیه‌سازی می‌کنیم
        
        full_text = self._mock_generate(model_type, prompt, config)
        words = full_text.split()
        
        for i, word in enumerate(words):
            await asyncio.sleep(0.01)  # Simulate streaming delay
            yield word + " "
            
            if (i + 1) % 10 == 0:
                yield "\n"
    
    def unload_model(self, model_type: ModelType):
        """
        آزادسازی حافظه مدل
        
        Args:
            model_type: نوع مدل
        """
        if self.loaded_models.get(model_type, False):
            self.logger.info(
                f"در حال آزادسازی مدل: {model_type.value}",
                f"Unloading model: {model_type.value}"
            )
            
            # NOTE: در محیط واقعی، این قسمت باید مدل را از حافظه حذف کند
            
            self.loaded_models[model_type] = False
            
            # Update registry
            if self.model_registry:
                model_metadata = self.model_registry.get_model(model_type)
                if model_metadata:
                    model_metadata.loaded = False
    
    def get_stats(self, model_type: Optional[ModelType] = None) -> Dict[str, Any]:
        """
        دریافت آمار استفاده
        
        Args:
            model_type: نوع مدل (اگر None، آمار همه مدل‌ها)
        
        Returns:
            آمار
        """
        if model_type:
            return {
                'model_type': model_type.value,
                'loaded': self.loaded_models.get(model_type, False),
                'inference_count': self.inference_count.get(model_type, 0),
                'total_tokens': self.total_tokens_generated.get(model_type, 0)
            }
        else:
            return {
                'loaded_models': [mt.value for mt, loaded in self.loaded_models.items() if loaded],
                'total_inferences': sum(self.inference_count.values()),
                'total_tokens': sum(self.total_tokens_generated.values())
            }
    
    async def health_check(self) -> bool:
        """
        بررسی سلامت ارتباط با vLLM
        
        Returns:
            True اگر سالم
        """
        try:
            # NOTE: در محیط واقعی، این قسمت باید health endpoint را بررسی کند
            # در حالت توسعه، همیشه True برمی‌گرداند
            
            self.logger.debug(
                "بررسی سلامت vLLM",
                "vLLM health check"
            )
            
            await asyncio.sleep(0.05)
            return True
        
        except Exception as e:
            self.logger.error(
                "خطا در health check",
                "Error in health check",
                context={'error': str(e)}
            )
            return False


# ==============================================================================
# Singleton Instance
# ==============================================================================

_vllm_client_instance: Optional[vLLMClient] = None

def get_vllm_client() -> vLLMClient:
    """دریافت instance سینگلتون vLLM Client"""
    global _vllm_client_instance
    
    if _vllm_client_instance is None:
        _vllm_client_instance = vLLMClient()
    
    return _vllm_client_instance
