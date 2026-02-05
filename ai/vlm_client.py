#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - VLM Client
==========================

Client برای ارتباط با VLM models از طریق vLLM

Features:
- Image preprocessing (resize, normalize, format conversion)
- vLLM VLM API integration
- Multi-format support (path, bytes, base64, PIL)
- Lazy loading
- Performance optimization

تاریخ: 2025-12-08
"""

import asyncio
import time
import base64
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, Tuple, Dict, List
from PIL import Image
import numpy as np

from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import handle_exception, AIException, ValidationException
from core.config_manager import get_config

from ai.vlm_core import (
    VLMModelType, VLMModelMetadata, VLMModelRegistry,
    ImageMetadata, VLMRequest, VLMResult, VLMTaskType,
    OCRResult, OCRLine, OCRWord, BoundingBox, ImageType, OCREngine
)


class ImagePreprocessor:
    """
    پیش‌پردازش تصاویر برای VLM
    """
    
    MAX_SIZE_MB = 10  # حداکثر حجم تصویر
    
    def __init__(self):
        self.logger = get_logger(__name__, LogCategory.AI)
    
    @log_performance
    def load_image(self, 
                   image_path: Optional[str] = None,
                   image_bytes: Optional[bytes] = None,
                   image_base64: Optional[str] = None) -> Tuple[Image.Image, ImageMetadata]:
        """
        بارگذاری تصویر از مسیر، bytes یا base64
        
        Returns:
            (PIL Image, ImageMetadata)
        """
        try:
            # Load from path
            if image_path:
                path = Path(image_path)
                if not path.exists():
                    raise ValidationException(f"Image not found: {image_path}")
                
                size_bytes = path.stat().st_size
                
                # Check size
                if size_bytes > self.MAX_SIZE_MB * 1024 * 1024:
                    raise ValidationException(f"Image too large: {size_bytes / 1024 / 1024:.1f}MB")
                
                img = Image.open(image_path)
            
            # Load from bytes
            elif image_bytes:
                size_bytes = len(image_bytes)
                img = Image.open(BytesIO(image_bytes))
            
            # Load from base64
            elif image_base64:
                image_bytes = base64.b64decode(image_base64)
                size_bytes = len(image_bytes)
                img = Image.open(BytesIO(image_bytes))
            
            else:
                raise ValidationException("No image source provided")
            
            # Convert to RGB if needed
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            
            # Create metadata
            metadata = ImageMetadata.from_pil(img, size_bytes)
            
            self.logger.debug(
                f"تصویر بارگذاری شد: {metadata.width}x{metadata.height} ({metadata.format})",
                f"Image loaded: {metadata.width}x{metadata.height} ({metadata.format})"
            )
            
            return img, metadata
        
        except Exception as e:
            self.logger.error(
                "خطا در بارگذاری تصویر",
                "Error loading image",
                context={'error': str(e)}
            )
            raise AIException(f"Failed to load image: {e}") from e
    
    @log_performance
    def preprocess(self, 
                   img: Image.Image,
                   max_size: Tuple[int, int] = (4096, 4096),
                   quality: int = 95) -> Image.Image:
        """
        پیش‌پردازش تصویر
        
        Args:
            img: تصویر ورودی
            max_size: حداکثر اندازه (width, height)
            quality: کیفیت (0-100)
        
        Returns:
            تصویر پردازش‌شده
        """
        # Resize if needed
        if img.width > max_size[0] or img.height > max_size[1]:
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            self.logger.debug(
                f"تصویر resize شد به: {img.width}x{img.height}",
                f"Image resized to: {img.width}x{img.height}"
            )
        
        return img
    
    def detect_image_type(self, img: Image.Image, metadata: ImageMetadata) -> ImageType:
        """
        تشخیص نوع تصویر
        """
        # Simple heuristics (can be improved with ML)
        aspect_ratio = metadata.width / metadata.height
        
        # Screenshot typically 16:9 or similar
        if 1.5 <= aspect_ratio <= 2.0:
            return ImageType.SCREENSHOT
        
        # Document typically portrait or A4
        elif 0.7 <= aspect_ratio <= 0.8:
            return ImageType.DOCUMENT
        
        # Square-ish might be code/diagram
        elif 0.9 <= aspect_ratio <= 1.1:
            return ImageType.DIAGRAM
        
        else:
            return ImageType.UNKNOWN
    
    def to_base64(self, img: Image.Image, format: str = 'PNG') -> str:
        """تبدیل به base64"""
        buffer = BytesIO()
        img.save(buffer, format=format)
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')


class VLMClient:
    """
    Client برای مدل‌های VLM از طریق vLLM
    """
    
    def __init__(self):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        
        # vLLM connection
        self.vllm_host = self.config.get('ai.vllm_host', 'localhost')
        self.vllm_port = self.config.get('ai.vllm_port', 8000)
        self.vllm_base_url = f"http://{self.vllm_host}:{self.vllm_port}"
        
        # Image preprocessing
        self.preprocessor = ImagePreprocessor()
        
        # Model management
        self.loaded_models: Dict[VLMModelType, bool] = {}
        self.model_registry: Optional[VLMModelRegistry] = None
        
        # Statistics
        self.inference_count = 0
        self.total_images_processed = 0
        
        self.logger.info(
            "VLM Client راه‌اندازی شد",
            "VLM Client initialized",
            context={'vllm_url': self.vllm_base_url}
        )
    
    def set_model_registry(self, registry: VLMModelRegistry):
        """تنظیم Model Registry"""
        self.model_registry = registry
    
    @log_performance
    @handle_exception(fallback_value=False)
    async def load_model(self, model_type: VLMModelType) -> bool:
        """بارگذاری یک مدل VLM"""
        if self.loaded_models.get(model_type, False):
            return True
        
        if not self.model_registry:
            raise AIException("Model registry not set")
        
        model_metadata = self.model_registry.get_model(model_type)
        if not model_metadata:
            raise AIException(f"Model not found: {model_type.value}")
        
        self.logger.info(
            f"در حال بارگذاری VLM: {model_metadata.name}",
            f"Loading VLM: {model_metadata.name}",
            context={'vram_gb': model_metadata.vram_required_gb}
        )
        
        # NOTE: در محیط واقعی از vLLM API استفاده می‌شود
        await asyncio.sleep(0.1)  # Simulate loading
        
        self.loaded_models[model_type] = True
        model_metadata.loaded = True
        
        return True
    
    @log_performance
    @handle_exception(fallback_value=None)
    async def process_image(self,
                           request: VLMRequest,
                           model_type: VLMModelType) -> Optional[VLMResult]:
        """
        پردازش تصویر با VLM
        
        Args:
            request: درخواست VLM
            model_type: نوع مدل
        
        Returns:
            نتیجه VLM
        """
        start_time = time.time()
        
        # Validate request
        request.validate()
        
        # Ensure model is loaded
        if not self.loaded_models.get(model_type, False):
            await self.load_model(model_type)
        
        # Preprocessing
        preprocess_start = time.time()
        img, metadata = self.preprocessor.load_image(
            request.image_path,
            request.image_bytes,
            request.image_base64
        )
        
        # Get max size from model metadata
        model_metadata = self.model_registry.get_model(model_type)
        max_size = model_metadata.max_image_size if model_metadata else (4096, 4096)
        
        img = self.preprocessor.preprocess(img, max_size=max_size)
        image_type = self.preprocessor.detect_image_type(img, metadata)
        
        preprocessing_ms = (time.time() - preprocess_start) * 1000
        
        # Inference
        inference_start = time.time()
        
        # NOTE: در محیط واقعی از vLLM VLM API استفاده می‌شود
        # این قسمت mock است
        generated_text = self._mock_vlm_inference(model_type, request.prompt, image_type)
        
        inference_ms = (time.time() - inference_start) * 1000
        
        # Update stats
        self.inference_count += 1
        self.total_images_processed += 1
        
        # Create result
        total_ms = (time.time() - start_time) * 1000
        
        # Check if this is an OCR task and generate OCR result
        ocr_result = None
        if request.task_type in [VLMTaskType.PURE_OCR, VLMTaskType.DOCUMENT_OCR, VLMTaskType.SCREENSHOT_OCR]:
            # Generate basic OCR result from text
            ocr_result = OCRResult(
                text=generated_text,
                lines=[
                    OCRLine(
                        text=generated_text,
                        words=[OCRWord(word, 0.9) for word in generated_text.split()[:10]],
                        confidence=0.88
                    )
                ],
                confidence=0.88,
                engine=OCREngine.VLM_BASED,
                language='en',
                processing_time_ms=inference_ms
            )
        
        result = VLMResult(
            text=generated_text,
            model_used=model_type,
            task_type=request.task_type or VLMTaskType.COMPLEX_REASONING,
            image_type=image_type,
            image_metadata=metadata,
            latency_ms=total_ms,
            preprocessing_ms=preprocessing_ms,
            inference_ms=inference_ms,
            confidence_score=0.85,
            ocr_result=ocr_result
        )
        
        self.logger.info(
            f"VLM inference کامل: {total_ms:.0f}ms",
            f"VLM inference complete: {total_ms:.0f}ms",
            context={
                'model': model_type.value,
                'image_size': f"{metadata.width}x{metadata.height}"
            }
        )
        
        return result
    
    def _mock_vlm_inference(self, 
                           model_type: VLMModelType,
                           prompt: str,
                           image_type: ImageType) -> str:
        """Mock VLM inference برای توسعه"""
        
        if "ocr" in prompt.lower() or "text" in prompt.lower():
            return """OCR Result:
            
This appears to be a screenshot containing code. The text extracted is:

```python
def exploit_vulnerability(target, payload):
    # Send malicious payload
    response = requests.post(target, data=payload)
    return response.status_code == 200
```

Confidence: 92%"""
        
        elif "vulnerability" in prompt.lower() or "security" in prompt.lower():
            return """Security Analysis:

Based on the screenshot, I can identify the following security concerns:

1. **SQL Injection**: The login form doesn't validate inputs properly
2. **XSS Vulnerability**: User input is reflected without sanitization
3. **Weak Authentication**: No rate limiting on login attempts

Risk Level: HIGH

Recommended Actions:
- Implement input validation
- Add CSRF tokens
- Enable rate limiting"""
        
        else:
            return f"""Analysis complete using {model_type.value}.

The image shows a {image_type.value}. 

{prompt}

This appears to be a typical scenario requiring visual understanding and reasoning capabilities."""
    
    async def process_batch(self,
                           requests: List[VLMRequest],
                           model_type: VLMModelType) -> List[VLMResult]:
        """پردازش دسته‌ای تصاویر"""
        results = []
        
        for req in requests:
            result = await self.process_image(req, model_type)
            if result:
                results.append(result)
        
        return results
    
    def get_stats(self) -> Dict:
        """دریافت آمار"""
        return {
            'inference_count': self.inference_count,
            'images_processed': self.total_images_processed,
            'loaded_models': [mt.value for mt, loaded in self.loaded_models.items() if loaded]
        }


# ==============================================================================
# Singleton
# ==============================================================================

_vlm_client_instance: Optional[VLMClient] = None

def get_vlm_client() -> VLMClient:
    """دریافت instance سینگلتون VLM Client"""
    global _vlm_client_instance
    
    if _vlm_client_instance is None:
        _vlm_client_instance = VLMClient()
    
    return _vlm_client_instance
