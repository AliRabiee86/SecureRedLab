#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - VLM Anti-Hallucination System
=============================================

سیستم تشخیص Hallucination برای VLM

Guardrails:
1. Multi-model Consensus (2+ VLMs)
2. OCR Confidence Validation
3. Bounding Box Verification
4. Text Consistency Check

تاریخ: 2025-12-08
"""

from typing import List, Optional, Dict
from dataclasses import dataclass, field
from datetime import datetime

from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import handle_exception

from ai.vlm_core import VLMResult, OCRResult, VLMModelType


@dataclass
class VLMHallucinationReport:
    """گزارش تشخیص Hallucination برای VLM"""
    is_hallucinated: bool
    confidence_score: float
    triggered_guardrails: List[str]
    
    # VLM-specific scores
    ocr_confidence_score: float = 1.0
    consensus_score: float = 1.0
    bbox_verification_score: float = 1.0
    text_consistency_score: float = 1.0
    
    details: Dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class VLMAntiHallucinationSystem:
    """
    سیستم ضد-Hallucination برای VLM
    """
    
    def __init__(self, min_confidence: float = 0.7):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.min_confidence = min_confidence
        
        # Statistics
        self.total_checks = 0
        self.hallucinations_detected = 0
        
        self.logger.info(
            "VLM Anti-Hallucination System راه‌اندازی شد",
            "VLM Anti-Hallucination System initialized",
            context={'min_confidence': min_confidence}
        )
    
    @log_performance
    @handle_exception(fallback_value=None)
    def check(self,
              primary_result: VLMResult,
              secondary_results: Optional[List[VLMResult]] = None) -> VLMHallucinationReport:
        """
        بررسی VLM result برای Hallucination
        
        Args:
            primary_result: نتیجه اصلی VLM
            secondary_results: نتایج مدل‌های دیگر (برای consensus)
        
        Returns:
            گزارش Hallucination
        """
        self.total_checks += 1
        
        report = VLMHallucinationReport(
            is_hallucinated=False,
            confidence_score=primary_result.confidence_score,
            triggered_guardrails=[]
        )
        
        # Guardrail 1: OCR Confidence Validation
        if primary_result.ocr_result:
            ocr_score = self._check_ocr_confidence(primary_result.ocr_result)
            report.ocr_confidence_score = ocr_score
            
            if ocr_score < 0.7:
                report.triggered_guardrails.append("low_ocr_confidence")
        
        # Guardrail 2: Multi-model Consensus
        if secondary_results and len(secondary_results) > 0:
            consensus_score = self._check_consensus(primary_result, secondary_results)
            report.consensus_score = consensus_score
            
            if consensus_score < 0.6:
                report.triggered_guardrails.append("low_consensus")
        
        # Guardrail 3: Bounding Box Verification
        if primary_result.ocr_result:
            bbox_score = self._verify_bounding_boxes(primary_result.ocr_result)
            report.bbox_verification_score = bbox_score
            
            if bbox_score < 0.8:
                report.triggered_guardrails.append("bbox_issues")
        
        # Guardrail 4: Text Consistency
        consistency_score = self._check_text_consistency(primary_result)
        report.text_consistency_score = consistency_score
        
        if consistency_score < 0.7:
            report.triggered_guardrails.append("text_inconsistency")
        
        # Final decision
        avg_score = (
            report.ocr_confidence_score +
            report.consensus_score +
            report.bbox_verification_score +
            report.text_consistency_score
        ) / 4.0
        
        report.confidence_score = avg_score
        report.is_hallucinated = (
            len(report.triggered_guardrails) >= 2 or
            avg_score < self.min_confidence
        )
        
        if report.is_hallucinated:
            self.hallucinations_detected += 1
        
        self.logger.debug(
            f"VLM Hallucination check: {'❌ DETECTED' if report.is_hallucinated else '✅ CLEAN'}",
            f"VLM Hallucination check: {'DETECTED' if report.is_hallucinated else 'CLEAN'}",
            context={
                'confidence': report.confidence_score,
                'guardrails': report.triggered_guardrails
            }
        )
        
        return report
    
    def _check_ocr_confidence(self, ocr_result: OCRResult) -> float:
        """بررسی confidence OCR"""
        return ocr_result.confidence
    
    def _check_consensus(self,
                        primary: VLMResult,
                        secondary_list: List[VLMResult]) -> float:
        """بررسی consensus بین مدل‌ها"""
        if not secondary_list:
            return 1.0
        
        # Simple text similarity (در واقعیت از embeddings استفاده می‌شود)
        primary_words = set(primary.text.lower().split())
        
        similarities = []
        for secondary in secondary_list:
            secondary_words = set(secondary.text.lower().split())
            
            if not primary_words or not secondary_words:
                continue
            
            # Jaccard similarity
            intersection = primary_words & secondary_words
            union = primary_words | secondary_words
            
            similarity = len(intersection) / len(union) if union else 0.0
            similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 1.0
    
    def _verify_bounding_boxes(self, ocr_result: OCRResult) -> float:
        """بررسی صحت bounding boxes"""
        if not ocr_result.lines:
            return 1.0
        
        # Check if boxes are reasonable
        valid_boxes = 0
        total_boxes = 0
        
        for line in ocr_result.lines:
            if line.bbox:
                total_boxes += 1
                
                # Check if box dimensions are reasonable
                if (line.bbox.width > 0 and line.bbox.height > 0 and
                    line.bbox.width < 10000 and line.bbox.height < 10000):
                    valid_boxes += 1
        
        return valid_boxes / total_boxes if total_boxes > 0 else 1.0
    
    def _check_text_consistency(self, result: VLMResult) -> float:
        """بررسی consistency متن"""
        text = result.text
        
        # Check for obvious hallucination patterns
        hallucination_indicators = [
            "i think", "probably", "maybe", "might be",
            "not sure", "unclear", "difficult to see",
            "فکر می‌کنم", "احتمالاً", "شاید"
        ]
        
        text_lower = text.lower()
        indicator_count = sum(1 for ind in hallucination_indicators if ind in text_lower)
        
        # More indicators = lower confidence
        consistency = max(0.0, 1.0 - (indicator_count * 0.2))
        
        return consistency
    
    def get_statistics(self) -> Dict:
        """دریافت آمار"""
        hallucination_rate = (
            self.hallucinations_detected / max(self.total_checks, 1)
        )
        
        return {
            'total_checks': self.total_checks,
            'hallucinations_detected': self.hallucinations_detected,
            'hallucination_rate': hallucination_rate
        }


# ==============================================================================
# Singleton
# ==============================================================================

_vlm_hallucination_instance: Optional[VLMAntiHallucinationSystem] = None

def get_vlm_anti_hallucination(min_confidence: float = 0.7) -> VLMAntiHallucinationSystem:
    """دریافت instance سینگلتون VLM Anti-Hallucination"""
    global _vlm_hallucination_instance
    
    if _vlm_hallucination_instance is None:
        _vlm_hallucination_instance = VLMAntiHallucinationSystem(min_confidence)
    
    return _vlm_hallucination_instance
