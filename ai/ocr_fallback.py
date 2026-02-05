#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - OCR Fallback Chain
==================================

زنجیره سه‌لایه OCR با fallback خودکار

Tiers:
1. Hunyuan-OCR (VLM-based via vLLM) - 92% accuracy, 2% hallucination
2. PaddleOCR (GPU-accelerated) - Fast, multi-language
3. Tesseract (CPU fallback) - Universal fallback

Strategy:
- Try Tier 1 (Hunyuan) first
- If confidence < threshold → Tier 2 (PaddleOCR)
- If still fails → Tier 3 (Tesseract)

تاریخ: 2025-12-08
"""

import time
from typing import Optional, List, Tuple
from PIL import Image

from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import handle_exception, AIException

from ai.vlm_core import (
    OCREngine, OCRResult, OCRLine, OCRWord, BoundingBox
)


class OCRFallbackChain:
    """
    زنجیره OCR با fallback خودکار
    """
    
    def __init__(self, 
                 min_confidence: float = 0.7,
                 enable_paddleocr: bool = True,
                 enable_tesseract: bool = True):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.min_confidence = min_confidence
        
        # Initialize OCR engines
        self.paddleocr_available = False
        self.tesseract_available = False
        
        if enable_paddleocr:
            self.paddleocr_available = self._init_paddleocr()
        
        if enable_tesseract:
            self.tesseract_available = self._init_tesseract()
        
        self.logger.info(
            f"OCR Fallback Chain راه‌اندازی شد (PaddleOCR: {self.paddleocr_available}, Tesseract: {self.tesseract_available})",
            f"OCR Fallback Chain initialized (PaddleOCR: {self.paddleocr_available}, Tesseract: {self.tesseract_available})"
        )
    
    def _init_paddleocr(self) -> bool:
        """راه‌اندازی PaddleOCR"""
        try:
            # NOTE: در محیط واقعی باید PaddleOCR import شود
            # from paddleocr import PaddleOCR
            # self.paddle_ocr = PaddleOCR(use_angle_cls=True, lang='en')
            
            self.logger.info("PaddleOCR initialized (mock)")
            return True
        
        except Exception as e:
            self.logger.warning(
                f"PaddleOCR در دسترس نیست: {e}",
                f"PaddleOCR not available: {e}"
            )
            return False
    
    def _init_tesseract(self) -> bool:
        """راه‌اندازی Tesseract"""
        try:
            # NOTE: در محیط واقعی باید pytesseract import شود
            # import pytesseract
            # pytesseract.get_tesseract_version()
            
            self.logger.info("Tesseract initialized (mock)")
            return True
        
        except Exception as e:
            self.logger.warning(
                f"Tesseract در دسترس نیست: {e}",
                f"Tesseract not available: {e}"
            )
            return False
    
    @log_performance
    @handle_exception(fallback_value=None)
    async def extract_text(self,
                          image: Image.Image,
                          language: str = 'en',
                          vlm_result: Optional[OCRResult] = None) -> Optional[OCRResult]:
        """
        استخراج متن با استفاده از fallback chain
        
        Args:
            image: تصویر PIL
            language: زبان ('en', 'fa', 'ch', etc.)
            vlm_result: نتیجه VLM (Tier 1) اگر قبلاً اجرا شده
        
        Returns:
            بهترین نتیجه OCR
        """
        # Tier 1: VLM-based (Hunyuan-OCR) - if provided
        if vlm_result and vlm_result.confidence >= self.min_confidence:
            self.logger.info(
                f"✅ Tier 1 (VLM): Confidence {vlm_result.confidence:.2f} - استفاده شد",
                f"✅ Tier 1 (VLM): Confidence {vlm_result.confidence:.2f} - Used"
            )
            return vlm_result
        
        # Tier 2: PaddleOCR (GPU)
        if self.paddleocr_available:
            result = await self._ocr_with_paddleocr(image, language)
            if result and result.confidence >= self.min_confidence:
                self.logger.info(
                    f"✅ Tier 2 (PaddleOCR): Confidence {result.confidence:.2f}",
                    f"✅ Tier 2 (PaddleOCR): Confidence {result.confidence:.2f}"
                )
                return result
        
        # Tier 3: Tesseract (CPU fallback)
        if self.tesseract_available:
            result = await self._ocr_with_tesseract(image, language)
            if result:
                self.logger.info(
                    f"⚠️ Tier 3 (Tesseract): Fallback استفاده شد",
                    f"⚠️ Tier 3 (Tesseract): Fallback used"
                )
                return result
        
        # No OCR succeeded
        self.logger.error(
            "❌ همه OCR engines ناموفق بودند",
            "❌ All OCR engines failed"
        )
        
        return vlm_result  # Return VLM result even if low confidence
    
    async def _ocr_with_paddleocr(self,
                                   image: Image.Image,
                                   language: str) -> Optional[OCRResult]:
        """OCR با PaddleOCR"""
        start_time = time.time()
        
        try:
            # NOTE: در محیط واقعی از PaddleOCR استفاده می‌شود
            # result = self.paddle_ocr.ocr(np.array(image), cls=True)
            
            # Mock result
            await self._simulate_ocr_delay(0.3)
            
            lines = [
                OCRLine(
                    text="Sample text extracted by PaddleOCR",
                    words=[
                        OCRWord("Sample", 0.95),
                        OCRWord("text", 0.93),
                        OCRWord("extracted", 0.90),
                        OCRWord("by", 0.96),
                        OCRWord("PaddleOCR", 0.92)
                    ],
                    confidence=0.93
                )
            ]
            
            full_text = " ".join(line.text for line in lines)
            avg_confidence = sum(line.confidence for line in lines) / len(lines)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return OCRResult(
                text=full_text,
                lines=lines,
                confidence=avg_confidence,
                engine=OCREngine.PADDLE_OCR,
                language=language,
                processing_time_ms=processing_time_ms
            )
        
        except Exception as e:
            self.logger.error(
                f"خطا در PaddleOCR: {e}",
                f"Error in PaddleOCR: {e}"
            )
            return None
    
    async def _ocr_with_tesseract(self,
                                   image: Image.Image,
                                   language: str) -> Optional[OCRResult]:
        """OCR با Tesseract"""
        start_time = time.time()
        
        try:
            # NOTE: در محیط واقعی از Tesseract استفاده می‌شود
            # import pytesseract
            # text = pytesseract.image_to_string(image, lang=language)
            # data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            # Mock result
            await self._simulate_ocr_delay(0.2)
            
            lines = [
                OCRLine(
                    text="Text extracted by Tesseract OCR",
                    words=[
                        OCRWord("Text", 0.85),
                        OCRWord("extracted", 0.82),
                        OCRWord("by", 0.88),
                        OCRWord("Tesseract", 0.80),
                        OCRWord("OCR", 0.86)
                    ],
                    confidence=0.84
                )
            ]
            
            full_text = " ".join(line.text for line in lines)
            avg_confidence = sum(line.confidence for line in lines) / len(lines)
            
            processing_time_ms = (time.time() - start_time) * 1000
            
            return OCRResult(
                text=full_text,
                lines=lines,
                confidence=avg_confidence,
                engine=OCREngine.TESSERACT,
                language=language,
                processing_time_ms=processing_time_ms
            )
        
        except Exception as e:
            self.logger.error(
                f"خطا در Tesseract: {e}",
                f"Error in Tesseract: {e}"
            )
            return None
    
    async def _simulate_ocr_delay(self, seconds: float):
        """شبیه‌سازی تاخیر OCR"""
        import asyncio
        await asyncio.sleep(seconds)
    
    def get_available_engines(self) -> List[OCREngine]:
        """دریافت لیست موتورهای در دسترس"""
        engines = [OCREngine.VLM_BASED]  # VLM همیشه در دسترس
        
        if self.paddleocr_available:
            engines.append(OCREngine.PADDLE_OCR)
        
        if self.tesseract_available:
            engines.append(OCREngine.TESSERACT)
        
        return engines


# ==============================================================================
# Singleton
# ==============================================================================

_ocr_fallback_instance: Optional[OCRFallbackChain] = None

def get_ocr_fallback_chain(min_confidence: float = 0.7) -> OCRFallbackChain:
    """دریافت instance سینگلتون OCR Fallback Chain"""
    global _ocr_fallback_instance
    
    if _ocr_fallback_instance is None:
        _ocr_fallback_instance = OCRFallbackChain(min_confidence)
    
    return _ocr_fallback_instance
