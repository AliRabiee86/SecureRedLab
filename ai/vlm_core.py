#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - VLM Core (Vision-Language Models)
=================================================

هسته هوش مصنوعی بینایی-زبان کاملاً آفلاین

Features:
- 3-Track Architecture (Complex, Document, Pure OCR)
- Multi-tier OCR (VLM → PaddleOCR → Tesseract)
- VLM Anti-Hallucination System
- Image preprocessing pipeline
- vLLM backend integration

Models:
- Complex: InternVL3-78B → MiniCPM-V-4.5
- Document: Qwen2.5-VL-72B → InternVL2-8B
- OCR: Hunyuan-OCR → PaddleOCR → Tesseract

Architecture:
    ┌──────────────────────────────────────────┐
    │         VLM Core System                  │
    ├──────────────────────────────────────────┤
    │  1. VLM Client (vLLM VLM API)            │
    │     - Image preprocessing                │
    │     - Model loading                      │
    │     - Inference (sync/async)             │
    │                                          │
    │  2. 3-Track Router                       │
    │     - Task classification                │
    │     - Image type detection               │
    │     - Model selection                    │
    │                                          │
    │  3. OCR Fallback Chain                   │
    │     - Tier 1: Hunyuan-OCR (vLLM)         │
    │     - Tier 2: PaddleOCR (GPU)            │
    │     - Tier 3: Tesseract (CPU)            │
    │                                          │
    │  4. VLM Anti-Hallucination               │
    │     - Multi-model consensus              │
    │     - OCR confidence validation          │
    │     - Bounding box verification          │
    └──────────────────────────────────────────┘

Usage:
    from ai.vlm_core import get_vlm_core, VLMTaskType
    
    vlm = get_vlm_core()
    
    # Complex reasoning
    result = await vlm.process(
        image_path="/path/to/screenshot.png",
        prompt="What vulnerabilities do you see in this code?",
        task_type=VLMTaskType.COMPLEX_REASONING
    )
    
    # Document OCR
    result = await vlm.process(
        image_path="/path/to/document.pdf",
        task_type=VLMTaskType.DOCUMENT_OCR
    )
    
    # Pure OCR (fast)
    result = await vlm.ocr(
        image_path="/path/to/text.png"
    )

تاریخ: 2025-12-08
نسخه: 1.0.0
"""

import os
import sys
import asyncio
import threading
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from enum import Enum
from dataclasses import dataclass, field, asdict
from datetime import datetime
from PIL import Image
import io
import base64

# Core imports
from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import (
    handle_exception, retry_on_failure,
    AIException, ValidationException,
    ErrorSeverity
)
from core.config_manager import get_config


# ==============================================================================
# Enums & Constants
# ==============================================================================

class VLMTaskType(Enum):
    """نوع تسک VLM"""
    # Complex reasoning (needs InternVL3 or similar)
    COMPLEX_REASONING = "complex_reasoning"
    VISUAL_QUESTION_ANSWERING = "vqa"
    CODE_SCREENSHOT_ANALYSIS = "code_screenshot"
    VULNERABILITY_SCREENSHOT = "vuln_screenshot"
    
    # Document analysis (needs Qwen2.5-VL)
    DOCUMENT_OCR = "document_ocr"
    SCREENSHOT_OCR = "screenshot_ocr"
    LAYOUT_ANALYSIS = "layout_analysis"
    TABLE_EXTRACTION = "table_extraction"
    
    # Pure OCR (fast, needs Hunyuan-OCR or PaddleOCR)
    PURE_OCR = "pure_ocr"
    TEXT_EXTRACTION = "text_extraction"
    NUMBER_EXTRACTION = "number_extraction"


class VLMModelType(Enum):
    """نوع مدل VLM"""
    # Complex reasoning models
    INTERNVL3_78B = "internvl3-78b"
    MINICPM_V45 = "minicpm-v-4.5"
    
    # Document/Screenshot models
    QWEN25_VL_72B = "qwen2.5-vl-72b-awq"
    INTERNVL2_8B = "internvl2-8b"
    
    # Pure OCR models
    HUNYUAN_OCR = "hunyuan-ocr"


class OCREngine(Enum):
    """موتور OCR"""
    VLM_BASED = "vlm"           # Hunyuan-OCR via vLLM
    PADDLE_OCR = "paddleocr"    # PaddleOCR (GPU)
    TESSERACT = "tesseract"     # Tesseract (CPU fallback)


class ImageType(Enum):
    """نوع تصویر"""
    SCREENSHOT = "screenshot"       # Screenshot از برنامه/وب
    DOCUMENT = "document"          # PDF, اسناد اسکن‌شده
    PHOTO = "photo"                # عکس معمولی
    CODE = "code"                  # اسکرین‌شات کد
    DIAGRAM = "diagram"            # نمودار، چارت
    UNKNOWN = "unknown"


# ==============================================================================
# Data Classes
# ==============================================================================

@dataclass
class BoundingBox:
    """مختصات یک bounding box"""
    x: int
    y: int
    width: int
    height: int
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class OCRWord:
    """یک کلمه شناسایی‌شده"""
    text: str
    confidence: float
    bbox: Optional[BoundingBox] = None
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        if self.bbox:
            data['bbox'] = self.bbox.to_dict()
        return data


@dataclass
class OCRLine:
    """یک خط متن"""
    text: str
    words: List[OCRWord]
    confidence: float
    bbox: Optional[BoundingBox] = None
    
    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'confidence': self.confidence,
            'words': [w.to_dict() for w in self.words],
            'bbox': self.bbox.to_dict() if self.bbox else None
        }


@dataclass
class OCRResult:
    """نتیجه OCR"""
    text: str                           # متن کامل
    lines: List[OCRLine]                # خطوط
    confidence: float                   # اعتماد کلی
    engine: OCREngine                   # موتور استفاده‌شده
    language: str = "en"                # زبان شناسایی‌شده
    processing_time_ms: float = 0.0
    
    def to_dict(self) -> Dict:
        return {
            'text': self.text,
            'lines': [line.to_dict() for line in self.lines],
            'confidence': self.confidence,
            'engine': self.engine.value,
            'language': self.language,
            'processing_time_ms': self.processing_time_ms
        }


@dataclass
class ImageMetadata:
    """اطلاعات متا تصویر"""
    width: int
    height: int
    format: str                         # PNG, JPEG, etc.
    mode: str                           # RGB, RGBA, etc.
    size_bytes: int
    dpi: Optional[Tuple[int, int]] = None
    
    @classmethod
    def from_pil(cls, img: Image.Image, size_bytes: int = 0) -> 'ImageMetadata':
        """ساخت از PIL Image"""
        return cls(
            width=img.width,
            height=img.height,
            format=img.format or "unknown",
            mode=img.mode,
            size_bytes=size_bytes,
            dpi=img.info.get('dpi')
        )


@dataclass
class VLMRequest:
    """درخواست VLM"""
    image_path: Optional[str] = None    # مسیر فایل
    image_bytes: Optional[bytes] = None # یا bytes مستقیم
    image_base64: Optional[str] = None  # یا base64
    
    prompt: str = ""                    # سوال/prompt
    task_type: Optional[VLMTaskType] = None
    
    # تنظیمات
    max_tokens: int = 1000
    temperature: float = 0.7
    prefer_speed: bool = False
    
    # OCR specific
    ocr_only: bool = False
    extract_tables: bool = False
    extract_layout: bool = False
    
    def validate(self) -> bool:
        """اعتبارسنجی درخواست"""
        has_image = any([
            self.image_path,
            self.image_bytes,
            self.image_base64
        ])
        
        if not has_image:
            raise ValidationException("No image provided")
        
        if self.image_path and not Path(self.image_path).exists():
            raise ValidationException(f"Image file not found: {self.image_path}")
        
        return True


@dataclass
class VLMResult:
    """نتیجه VLM"""
    text: str                           # پاسخ اصلی
    model_used: VLMModelType
    task_type: VLMTaskType
    
    # OCR results (if applicable)
    ocr_result: Optional[OCRResult] = None
    
    # Image analysis
    image_type: ImageType = ImageType.UNKNOWN
    image_metadata: Optional[ImageMetadata] = None
    
    # Performance
    latency_ms: float = 0.0
    preprocessing_ms: float = 0.0
    inference_ms: float = 0.0
    
    # Quality metrics
    confidence_score: float = 1.0
    hallucination_detected: bool = False
    guardrails_triggered: List[str] = field(default_factory=list)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['model_used'] = self.model_used.value
        data['task_type'] = self.task_type.value
        data['image_type'] = self.image_type.value
        if self.ocr_result:
            data['ocr_result'] = self.ocr_result.to_dict()
        data['timestamp'] = self.timestamp.isoformat()
        return data


# ==============================================================================
# VLM Model Registry
# ==============================================================================

@dataclass
class VLMModelMetadata:
    """اطلاعات متا مدل VLM"""
    name: str
    model_type: VLMModelType
    path: str
    vram_required_gb: int
    max_image_size: Tuple[int, int]  # (width, height)
    
    # Performance
    avg_latency_ms: float = 3000.0
    supports_batch: bool = False
    
    # Capabilities
    supports_ocr: bool = True
    supports_reasoning: bool = False
    supports_tables: bool = False
    
    # Quality
    mmmu_score: Optional[float] = None
    docvqa_score: Optional[float] = None
    ocr_accuracy: Optional[float] = None
    
    priority: int = 1
    loaded: bool = False
    last_used: Optional[datetime] = None


class VLMModelRegistry:
    """
    رجیستری مدل‌های VLM
    """
    
    def __init__(self, config: Dict[str, Any], logger):
        self.config = config
        self.logger = logger
        self.models: Dict[VLMModelType, VLMModelMetadata] = {}
        
        self._initialize_models()
    
    def _initialize_models(self):
        """راه‌اندازی رجیستری"""
        base_path = Path(self.config.get('ai.models_base_path', '/models'))
        
        # Complex reasoning models
        self.models[VLMModelType.INTERNVL3_78B] = VLMModelMetadata(
            name="InternVL3-78B",
            model_type=VLMModelType.INTERNVL3_78B,
            path=str(base_path / "InternVL3-78B"),
            vram_required_gb=20,
            max_image_size=(4096, 4096),
            avg_latency_ms=5000,
            supports_reasoning=True,
            supports_tables=True,
            mmmu_score=72.2,
            priority=1
        )
        
        self.models[VLMModelType.MINICPM_V45] = VLMModelMetadata(
            name="MiniCPM-V-4.5",
            model_type=VLMModelType.MINICPM_V45,
            path=str(base_path / "MiniCPM-V-4.5"),
            vram_required_gb=4,
            max_image_size=(2048, 2048),
            avg_latency_ms=3000,
            supports_reasoning=True,
            mmmu_score=66.3,
            priority=2
        )
        
        # Document/Screenshot models
        self.models[VLMModelType.QWEN25_VL_72B] = VLMModelMetadata(
            name="Qwen2.5-VL-72B-AWQ",
            model_type=VLMModelType.QWEN25_VL_72B,
            path=str(base_path / "Qwen2.5-VL-72B-AWQ"),
            vram_required_gb=36,
            max_image_size=(4096, 4096),
            avg_latency_ms=3000,
            supports_tables=True,
            docvqa_score=93.5,
            priority=1
        )
        
        self.models[VLMModelType.INTERNVL2_8B] = VLMModelMetadata(
            name="InternVL2-8B",
            model_type=VLMModelType.INTERNVL2_8B,
            path=str(base_path / "InternVL2-8B"),
            vram_required_gb=4,
            max_image_size=(2048, 2048),
            avg_latency_ms=2000,
            docvqa_score=85.0,
            priority=2
        )
        
        # Pure OCR models
        self.models[VLMModelType.HUNYUAN_OCR] = VLMModelMetadata(
            name="Hunyuan-OCR",
            model_type=VLMModelType.HUNYUAN_OCR,
            path=str(base_path / "Hunyuan-OCR"),
            vram_required_gb=1,
            max_image_size=(4096, 4096),
            avg_latency_ms=800,
            supports_reasoning=False,
            ocr_accuracy=92.0,
            priority=1
        )
        
        self.logger.info(
            f"VLM Registry راه‌اندازی شد با {len(self.models)} مدل",
            f"VLM Registry initialized with {len(self.models)} models"
        )
    
    def get_model(self, model_type: VLMModelType) -> Optional[VLMModelMetadata]:
        """دریافت اطلاعات یک مدل"""
        return self.models.get(model_type)
    
    def get_best_for_task(self, 
                          task_type: VLMTaskType,
                          max_vram_gb: Optional[int] = None) -> Optional[VLMModelMetadata]:
        """انتخاب بهترین مدل برای تسک"""
        # Map tasks to required capabilities
        if task_type in [VLMTaskType.COMPLEX_REASONING, VLMTaskType.VISUAL_QUESTION_ANSWERING,
                        VLMTaskType.CODE_SCREENSHOT_ANALYSIS, VLMTaskType.VULNERABILITY_SCREENSHOT]:
            candidates = [
                self.models.get(VLMModelType.INTERNVL3_78B),
                self.models.get(VLMModelType.MINICPM_V45)
            ]
        
        elif task_type in [VLMTaskType.DOCUMENT_OCR, VLMTaskType.SCREENSHOT_OCR,
                          VLMTaskType.LAYOUT_ANALYSIS, VLMTaskType.TABLE_EXTRACTION]:
            candidates = [
                self.models.get(VLMModelType.QWEN25_VL_72B),
                self.models.get(VLMModelType.INTERNVL2_8B)
            ]
        
        else:  # Pure OCR
            candidates = [self.models.get(VLMModelType.HUNYUAN_OCR)]
        
        # Filter by VRAM
        if max_vram_gb:
            candidates = [m for m in candidates if m and m.vram_required_gb <= max_vram_gb]
        
        # Sort by priority
        candidates = sorted([m for m in candidates if m], key=lambda m: m.priority)
        
        return candidates[0] if candidates else None


# ==============================================================================
# VLM Core - Main Class
# ==============================================================================

class VLMCore:
    """
    هسته اصلی VLM - یکپارچه‌سازی تمام کامپوننت‌ها
    """
    
    def __init__(self):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        
        # Initialize components
        self.model_registry = VLMModelRegistry(self.config, self.logger)
        
        # Import and initialize other components
        from ai.vlm_client import get_vlm_client
        from ai.vlm_router import get_vlm_router
        from ai.ocr_fallback import get_ocr_fallback_chain
        from ai.vlm_hallucination import get_vlm_anti_hallucination
        
        self.vlm_client = get_vlm_client()
        self.vlm_client.set_model_registry(self.model_registry)
        
        self.router = get_vlm_router(self.model_registry)
        
        self.ocr_fallback = get_ocr_fallback_chain(
            min_confidence=self.config.get('ai.vlm_min_confidence', 0.7)
        )
        
        self.anti_hallucination = get_vlm_anti_hallucination(
            min_confidence=self.config.get('ai.vlm_min_confidence', 0.7)
        )
        
        self.logger.info(
            "VLM Core راه‌اندازی شد (100% آفلاین)",
            "VLM Core initialized (100% offline)",
            context={
                'models': len(self.model_registry.models),
                'ocr_engines': len(self.ocr_fallback.get_available_engines())
            }
        )
    
    @log_performance
    @handle_exception(fallback_value=None)
    async def process(self, 
                     request: VLMRequest) -> Optional[VLMResult]:
        """
        پردازش تصویر با VLM
        
        Args:
            request: درخواست VLM
        
        Returns:
            نتیجه VLM با anti-hallucination check
        """
        # 1. Route to appropriate model
        task_type, model_type = self.router.route(request)
        
        # Update request task_type
        request.task_type = task_type
        
        self.logger.info(
            f"پردازش VLM: {task_type.value} → {model_type.value}",
            f"VLM processing: {task_type.value} → {model_type.value}"
        )
        
        # 2. Process with VLM
        result = await self.vlm_client.process_image(request, model_type)
        
        if not result:
            raise AIException("VLM processing failed")
        
        # 3. OCR Fallback (if OCR task and low confidence)
        if task_type in [VLMTaskType.PURE_OCR, VLMTaskType.DOCUMENT_OCR, 
                        VLMTaskType.SCREENSHOT_OCR] and result.ocr_result:
            
            # Load image for fallback
            from ai.vlm_client import ImagePreprocessor
            preprocessor = ImagePreprocessor()
            img, _ = preprocessor.load_image(
                request.image_path,
                request.image_bytes,
                request.image_base64
            )
            
            # Try fallback if needed
            improved_ocr = await self.ocr_fallback.extract_text(
                img,
                language='en',
                vlm_result=result.ocr_result
            )
            
            if improved_ocr and improved_ocr.confidence > result.ocr_result.confidence:
                result.ocr_result = improved_ocr
        
        # 4. Anti-hallucination check
        hallucination_report = self.anti_hallucination.check(result)
        
        result.confidence_score = hallucination_report.confidence_score
        result.hallucination_detected = hallucination_report.is_hallucinated
        result.guardrails_triggered = hallucination_report.triggered_guardrails
        
        if hallucination_report.is_hallucinated:
            self.logger.warning(
                "⚠️ VLM Hallucination شناسایی شد",
                "VLM Hallucination detected",
                context={
                    'confidence': hallucination_report.confidence_score,
                    'guardrails': hallucination_report.triggered_guardrails
                }
            )
        
        return result
    
    async def ocr(self,
                 image_path: Optional[str] = None,
                 image_bytes: Optional[bytes] = None,
                 image_base64: Optional[str] = None,
                 language: str = 'en') -> Optional[OCRResult]:
        """
        OCR سریع (مستقیماً به Track 3)
        
        Args:
            image_path/bytes/base64: تصویر
            language: زبان
        
        Returns:
            نتیجه OCR
        """
        request = VLMRequest(
            image_path=image_path,
            image_bytes=image_bytes,
            image_base64=image_base64,
            task_type=VLMTaskType.PURE_OCR,
            ocr_only=True
        )
        
        result = await self.process(request)
        
        return result.ocr_result if result else None
    
    def get_statistics(self) -> Dict:
        """دریافت آمار کلی"""
        return {
            'vlm_client': self.vlm_client.get_stats(),
            'router': self.router.get_statistics(),
            'ocr_fallback': {
                'available_engines': [e.value for e in self.ocr_fallback.get_available_engines()]
            },
            'anti_hallucination': self.anti_hallucination.get_statistics(),
            'loaded_models': [
                mt.value for mt, meta in self.model_registry.models.items()
                if meta.loaded
            ]
        }


# ==============================================================================
# Singleton Instance
# ==============================================================================

_vlm_core_instance = None
_vlm_core_lock = threading.Lock()

def get_vlm_core():
    """دریافت instance سینگلتون VLM Core"""
    global _vlm_core_instance
    
    if _vlm_core_instance is None:
        with _vlm_core_lock:
            if _vlm_core_instance is None:
                _vlm_core_instance = VLMCore()
    
    return _vlm_core_instance
