#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - VLM 3-Track Router
==================================

روتر سه‌مسیره برای انتخاب بهترین مدل VLM

Tracks:
1. Complex Reasoning (InternVL3, MiniCPM-V) - تحلیل پیچیده
2. Document/Screenshot (Qwen2.5-VL, InternVL2) - اسناد و اسکرین‌شات
3. Pure OCR (Hunyuan-OCR) - OCR خالص

تاریخ: 2025-12-08
"""

from typing import Tuple, Optional, Dict
from collections import defaultdict

from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import handle_exception

from ai.vlm_core import (
    VLMTaskType, VLMModelType, ImageType, 
    VLMModelRegistry, VLMRequest, ImageMetadata
)


class VLMRouter:
    """
    روتر 3-Track برای انتخاب مدل VLM
    """
    
    # Keywords for task detection
    REASONING_KEYWORDS = {
        'analyze', 'explain', 'describe', 'what is', 'why',
        'vulnerability', 'security', 'compare', 'evaluate',
        'تحلیل', 'توضیح', 'چیست', 'چرا', 'آسیب‌پذیری'
    }
    
    OCR_KEYWORDS = {
        'ocr', 'text', 'extract', 'read', 'transcribe',
        'متن', 'استخراج', 'بخوان'
    }
    
    DOCUMENT_KEYWORDS = {
        'document', 'pdf', 'table', 'layout', 'screenshot',
        'سند', 'جدول', 'اسکرین‌شات'
    }
    
    def __init__(self, model_registry: VLMModelRegistry):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.model_registry = model_registry
        
        # Statistics
        self.routing_stats: Dict[VLMTaskType, int] = defaultdict(int)
        self.track_usage: Dict[str, int] = defaultdict(int)
        
        self.logger.info(
            "VLM Router راه‌اندازی شد (3 Tracks)",
            "VLM Router initialized (3 Tracks)"
        )
    
    @log_performance
    @handle_exception(fallback_value=(VLMTaskType.PURE_OCR, VLMModelType.HUNYUAN_OCR))
    def route(self,
              request: VLMRequest,
              image_type: Optional[ImageType] = None,
              image_metadata: Optional[ImageMetadata] = None) -> Tuple[VLMTaskType, VLMModelType]:
        """
        مسیریابی به Track مناسب
        
        Args:
            request: درخواست VLM
            image_type: نوع تصویر (اختیاری)
            image_metadata: متادیتای تصویر (اختیاری)
        
        Returns:
            (task_type, model_type)
        """
        # 1. Check if task_type is explicitly provided
        if request.task_type:
            task_type = request.task_type
        else:
            task_type = self._classify_task(request, image_type, image_metadata)
        
        # 2. Select best model for task
        model_type = self._select_model(task_type, request.prefer_speed)
        
        # 3. Update stats
        self.routing_stats[task_type] += 1
        track = self._get_track_name(task_type)
        self.track_usage[track] += 1
        
        self.logger.debug(
            f"مسیریابی VLM: {task_type.value} → {model_type.value} (Track: {track})",
            f"VLM routing: {task_type.value} → {model_type.value} (Track: {track})"
        )
        
        return task_type, model_type
    
    def _classify_task(self,
                      request: VLMRequest,
                      image_type: Optional[ImageType],
                      image_metadata: Optional[ImageMetadata]) -> VLMTaskType:
        """تشخیص نوع تسک"""
        
        prompt_lower = request.prompt.lower() if request.prompt else ""
        
        # Pure OCR detection
        if request.ocr_only or self._has_keywords(prompt_lower, self.OCR_KEYWORDS):
            return VLMTaskType.PURE_OCR
        
        # Document analysis
        if (self._has_keywords(prompt_lower, self.DOCUMENT_KEYWORDS) or
            image_type == ImageType.DOCUMENT or
            request.extract_tables):
            
            if request.extract_tables:
                return VLMTaskType.TABLE_EXTRACTION
            else:
                return VLMTaskType.DOCUMENT_OCR
        
        # Screenshot analysis
        if image_type == ImageType.SCREENSHOT or image_type == ImageType.CODE:
            if "code" in prompt_lower or image_type == ImageType.CODE:
                return VLMTaskType.CODE_SCREENSHOT_ANALYSIS
            elif "vulnerability" in prompt_lower or "security" in prompt_lower:
                return VLMTaskType.VULNERABILITY_SCREENSHOT
            else:
                return VLMTaskType.SCREENSHOT_OCR
        
        # Complex reasoning (default for complex prompts)
        if self._has_keywords(prompt_lower, self.REASONING_KEYWORDS):
            return VLMTaskType.COMPLEX_REASONING
        
        # Visual Question Answering (has a question)
        if "?" in prompt_lower or any(q in prompt_lower for q in ['what', 'why', 'how', 'which']):
            return VLMTaskType.VISUAL_QUESTION_ANSWERING
        
        # Default: complex reasoning
        return VLMTaskType.COMPLEX_REASONING
    
    def _has_keywords(self, text: str, keywords: set) -> bool:
        """بررسی وجود keywords"""
        return any(kw in text for kw in keywords)
    
    def _select_model(self, 
                     task_type: VLMTaskType,
                     prefer_speed: bool) -> VLMModelType:
        """انتخاب مدل مناسب"""
        
        # Get available VRAM (mock - در واقعیت از GPU query می‌شود)
        available_vram_gb = 48 if not prefer_speed else 8
        
        # Use registry to find best model
        best_model = self.model_registry.get_best_for_task(
            task_type,
            max_vram_gb=available_vram_gb
        )
        
        if best_model:
            return best_model.model_type
        
        # Fallback logic by track
        track = self._get_track_name(task_type)
        
        if track == "complex":
            return VLMModelType.MINICPM_V45 if prefer_speed else VLMModelType.INTERNVL3_78B
        
        elif track == "document":
            return VLMModelType.INTERNVL2_8B if prefer_speed else VLMModelType.QWEN25_VL_72B
        
        else:  # ocr
            return VLMModelType.HUNYUAN_OCR
    
    def _get_track_name(self, task_type: VLMTaskType) -> str:
        """دریافت نام Track"""
        if task_type in [VLMTaskType.COMPLEX_REASONING, VLMTaskType.VISUAL_QUESTION_ANSWERING,
                        VLMTaskType.CODE_SCREENSHOT_ANALYSIS, VLMTaskType.VULNERABILITY_SCREENSHOT]:
            return "complex"
        
        elif task_type in [VLMTaskType.DOCUMENT_OCR, VLMTaskType.SCREENSHOT_OCR,
                          VLMTaskType.LAYOUT_ANALYSIS, VLMTaskType.TABLE_EXTRACTION]:
            return "document"
        
        else:
            return "ocr"
    
    def get_statistics(self) -> Dict:
        """دریافت آمار مسیریابی"""
        total_routes = sum(self.routing_stats.values())
        
        return {
            'total_routes': total_routes,
            'task_breakdown': dict(self.routing_stats),
            'track_usage': dict(self.track_usage),
            'track_percentages': {
                track: (count / max(total_routes, 1) * 100)
                for track, count in self.track_usage.items()
            }
        }
    
    def explain_routing(self, 
                       request: VLMRequest,
                       image_type: Optional[ImageType] = None) -> Dict:
        """توضیح چرایی مسیریابی"""
        
        task_type, model_type = self.route(request, image_type)
        track = self._get_track_name(task_type)
        
        # Analyze decision factors
        prompt_lower = request.prompt.lower() if request.prompt else ""
        
        reasoning_score = sum(1 for kw in self.REASONING_KEYWORDS if kw in prompt_lower)
        ocr_score = sum(1 for kw in self.OCR_KEYWORDS if kw in prompt_lower)
        doc_score = sum(1 for kw in self.DOCUMENT_KEYWORDS if kw in prompt_lower)
        
        return {
            'selected_task': task_type.value,
            'selected_model': model_type.value,
            'track': track,
            'scores': {
                'reasoning': reasoning_score,
                'ocr': ocr_score,
                'document': doc_score
            },
            'factors': {
                'ocr_only': request.ocr_only,
                'extract_tables': request.extract_tables,
                'image_type': image_type.value if image_type else None,
                'prefer_speed': request.prefer_speed
            }
        }


# ==============================================================================
# Singleton
# ==============================================================================

_vlm_router_instance: Optional[VLMRouter] = None

def get_vlm_router(model_registry: VLMModelRegistry) -> VLMRouter:
    """دریافت instance سینگلتون VLM Router"""
    global _vlm_router_instance
    
    if _vlm_router_instance is None:
        _vlm_router_instance = VLMRouter(model_registry)
    
    return _vlm_router_instance
