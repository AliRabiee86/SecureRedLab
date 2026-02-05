#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Anti-Hallucination System
=========================================

سیستم 7-لایه برای جلوگیری از Hallucination و اطمینان از صحت خروجی AI

7 Guardrails:
1. Self-Consistency Check
2. Fact Verification
3. Confidence Scoring
4. Cross-Model Validation
5. RAG Integration (Retrieval-Augmented Generation)
6. Output Filtering
7. Human-in-the-Loop (optional)

Architecture:
    ┌────────────────────────────────────────┐
    │   Anti-Hallucination System            │
    ├────────────────────────────────────────┤
    │  Input: Generated Text                 │
    │  ↓                                     │
    │  1. Self-Consistency (3 generations)   │
    │  2. Fact Verification (KB lookup)      │
    │  3. Confidence Scoring (uncertainty)   │
    │  4. Cross-Model (2+ models)            │
    │  5. RAG (retrieve + verify)            │
    │  6. Output Filtering (dangerous)       │
    │  7. HITL (manual review if low score)  │
    │  ↓                                     │
    │  Output: Verified + Score              │
    └────────────────────────────────────────┘

Hallucination Detection Strategies:
- Consistency: Multiple generations should agree
- Uncertainty: Model should express confidence
- Facts: Cross-reference with known data
- Filtering: Block obviously false/dangerous outputs

تاریخ: 2025-12-08
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import Counter

from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import handle_exception, AIException

from ai.offline_core import GenerationResult, ModelType


@dataclass
class HallucinationReport:
    """گزارش تشخیص Hallucination"""
    is_hallucinated: bool
    confidence_score: float          # 0.0-1.0 (0=very uncertain, 1=very confident)
    triggered_guardrails: List[str]
    details: Dict[str, any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    
    # Detailed scores per guardrail
    self_consistency_score: float = 1.0
    fact_verification_score: float = 1.0
    cross_model_agreement: float = 1.0
    rag_verification_score: float = 1.0
    output_safety_score: float = 1.0


class AntiHallucinationSystem:
    """
    سیستم ضد-Hallucination با 7 Guardrail
    """
    
    # Dangerous patterns to filter
    DANGEROUS_PATTERNS = [
        r'rm -rf /',
        r'format c:',
        r'dd if=/dev/zero',
        r':(){ :|:& };:',  # fork bomb
        r'sudo rm',
        # Add more as needed
    ]
    
    # Uncertainty phrases (indicates hallucination risk)
    UNCERTAINTY_PHRASES = {
        'i think', 'probably', 'maybe', 'might be', 'could be',
        'not sure', 'possibly', 'perhaps', 'seems like',
        'فکر می‌کنم', 'احتمالاً', 'شاید', 'ممکنه'
    }
    
    def __init__(self, min_confidence: float = 0.7):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.min_confidence = min_confidence
        
        # Statistics
        self.total_checks = 0
        self.hallucinations_detected = 0
        self.guardrail_triggers: Dict[str, int] = Counter()
        
        self.logger.info(
            "Anti-Hallucination System راه‌اندازی شد (7 Guardrails)",
            "Anti-Hallucination System initialized (7 Guardrails)",
            context={'min_confidence': min_confidence}
        )
    
    @log_performance
    @handle_exception(fallback_value=None)
    def check(self,
              text: str,
              model_type: ModelType,
              task_prompt: Optional[str] = None,
              enable_all: bool = True) -> HallucinationReport:
        """
        بررسی متن تولید‌شده برای Hallucination
        
        Args:
            text: متن تولید‌شده
            model_type: مدل استفاده‌شده
            task_prompt: prompt اصلی (برای context)
            enable_all: فعال‌سازی همه guardrails؟
        
        Returns:
            گزارش تشخیص
        """
        self.total_checks += 1
        
        report = HallucinationReport(
            is_hallucinated=False,
            confidence_score=1.0,
            triggered_guardrails=[]
        )
        
        # Guardrail 1: Self-Consistency Check
        if enable_all:
            consistency_score = self._check_self_consistency(text, model_type)
            report.self_consistency_score = consistency_score
            if consistency_score < 0.6:
                report.triggered_guardrails.append("self_consistency")
                self.guardrail_triggers['self_consistency'] += 1
        
        # Guardrail 2: Fact Verification
        if enable_all and task_prompt:
            fact_score = self._verify_facts(text, task_prompt)
            report.fact_verification_score = fact_score
            if fact_score < 0.7:
                report.triggered_guardrails.append("fact_verification")
                self.guardrail_triggers['fact_verification'] += 1
        
        # Guardrail 3: Confidence Scoring
        confidence_score = self._score_confidence(text)
        report.confidence_score = confidence_score
        if confidence_score < self.min_confidence:
            report.triggered_guardrails.append("low_confidence")
            self.guardrail_triggers['low_confidence'] += 1
        
        # Guardrail 4: Cross-Model Validation (skip in dev mode)
        # if enable_all:
        #     cross_model_score = self._cross_model_validate(text, model_type, task_prompt)
        #     report.cross_model_agreement = cross_model_score
        #     if cross_model_score < 0.6:
        #         report.triggered_guardrails.append("cross_model_disagreement")
        
        # Guardrail 5: RAG Verification (skip in dev mode)
        # if enable_all and task_prompt:
        #     rag_score = self._rag_verify(text, task_prompt)
        #     report.rag_verification_score = rag_score
        #     if rag_score < 0.7:
        #         report.triggered_guardrails.append("rag_mismatch")
        
        # Guardrail 6: Output Filtering
        safety_score, dangerous_patterns = self._filter_dangerous_output(text)
        report.output_safety_score = safety_score
        if safety_score < 1.0:
            report.triggered_guardrails.append("dangerous_output")
            report.details['dangerous_patterns'] = dangerous_patterns
            self.guardrail_triggers['dangerous_output'] += 1
        
        # Guardrail 7: Human-in-the-Loop (optional - manual trigger)
        # This is handled by the calling code
        
        # Final decision
        avg_score = (
            report.self_consistency_score +
            report.fact_verification_score +
            report.confidence_score +
            report.cross_model_agreement +
            report.rag_verification_score +
            report.output_safety_score
        ) / 6.0
        
        report.is_hallucinated = (
            len(report.triggered_guardrails) >= 2 or
            avg_score < 0.6
        )
        
        if report.is_hallucinated:
            self.hallucinations_detected += 1
        
        self.logger.debug(
            f"Hallucination check: {'❌ DETECTED' if report.is_hallucinated else '✅ CLEAN'}",
            f"Hallucination check: {'DETECTED' if report.is_hallucinated else 'CLEAN'}",
            context={
                'confidence': report.confidence_score,
                'triggered': report.triggered_guardrails,
                'avg_score': avg_score
            }
        )
        
        return report
    
    def _check_self_consistency(self, text: str, model_type: ModelType) -> float:
        """
        Guardrail 1: Self-Consistency Check
        
        If we generate the same prompt multiple times, outputs should be consistent.
        
        Note: در محیط واقعی، باید prompt را 3 بار generate کنیم و similarity بسنجیم.
        در حالت توسعه، mock می‌کنیم.
        """
        # Mock: در واقعیت باید similarity بین 3 generation را محاسبه کنیم
        # استفاده از embeddings و cosine similarity
        
        # For now, assume high consistency (this should be replaced with real logic)
        return 0.85
    
    def _verify_facts(self, text: str, task_prompt: str) -> float:
        """
        Guardrail 2: Fact Verification
        
        Cross-reference facts with known databases (CVE, CWE, etc.)
        
        Note: در محیط واقعی، باید از knowledge base استفاده کنیم.
        """
        # Mock: بررسی اینکه آیا اعداد/نام‌های CVE معتبر هستند
        
        # Extract CVE mentions
        cve_pattern = r'CVE-\d{4}-\d{4,7}'
        cves = re.findall(cve_pattern, text, re.IGNORECASE)
        
        # Mock validation (در واقعیت باید از NVD API استفاده کنیم)
        valid_cves = []
        for cve in cves:
            # فرض: CVE-2024-* معتبر هستند
            if '2024' in cve or '2023' in cve:
                valid_cves.append(cve)
        
        if cves:
            return len(valid_cves) / len(cves)
        
        return 0.8  # Default: mostly valid
    
    def _score_confidence(self, text: str) -> float:
        """
        Guardrail 3: Confidence Scoring
        
        Detect uncertainty phrases that indicate hallucination risk.
        """
        text_lower = text.lower()
        
        # Count uncertainty phrases
        uncertainty_count = sum(
            1 for phrase in self.UNCERTAINTY_PHRASES
            if phrase in text_lower
        )
        
        # Penalize based on frequency
        total_sentences = len(re.split(r'[.!?]', text))
        if total_sentences == 0:
            return 1.0
        
        uncertainty_ratio = uncertainty_count / total_sentences
        
        # Convert to confidence score (0-1)
        confidence = max(0.0, 1.0 - (uncertainty_ratio * 2.0))
        
        return confidence
    
    def _cross_model_validate(self,
                              text: str,
                              model_type: ModelType,
                              task_prompt: Optional[str]) -> float:
        """
        Guardrail 4: Cross-Model Validation
        
        Generate with 2+ different models and check agreement.
        
        Note: این روش expensive است، فقط برای تسک‌های critical.
        """
        # Mock: در واقعیت باید با مدل دیگر نیز generate کنیم
        # و similarity را بسنجیم
        
        # For now, assume moderate agreement
        return 0.75
    
    def _rag_verify(self, text: str, task_prompt: str) -> float:
        """
        Guardrail 5: RAG Verification
        
        Retrieve relevant documents and verify consistency.
        
        Note: نیاز به vector database و embedding model دارد.
        """
        # Mock: در واقعیت باید:
        # 1. Query را به embedding تبدیل کنیم
        # 2. از vector DB اسناد مرتبط را retrieve کنیم
        # 3. Consistency بین generated text و retrieved docs را بسنجیم
        
        # For now, assume good RAG alignment
        return 0.80
    
    def _filter_dangerous_output(self, text: str) -> Tuple[float, List[str]]:
        """
        Guardrail 6: Output Filtering
        
        Detect obviously dangerous/destructive commands.
        """
        found_patterns = []
        
        for pattern in self.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                found_patterns.append(pattern)
        
        if found_patterns:
            # Dangerous output detected
            safety_score = max(0.0, 1.0 - (len(found_patterns) * 0.3))
            return safety_score, found_patterns
        
        return 1.0, []
    
    def enable_human_review(self, 
                           text: str,
                           report: HallucinationReport) -> bool:
        """
        Guardrail 7: Human-in-the-Loop
        
        Should this output be manually reviewed?
        
        Args:
            text: generated text
            report: hallucination report
        
        Returns:
            True if manual review recommended
        """
        # Recommend human review if:
        # 1. Multiple guardrails triggered
        # 2. Very low confidence
        # 3. Dangerous patterns detected
        
        if len(report.triggered_guardrails) >= 3:
            return True
        
        if report.confidence_score < 0.5:
            return True
        
        if 'dangerous_output' in report.triggered_guardrails:
            return True
        
        return False
    
    def get_statistics(self) -> Dict:
        """دریافت آمار سیستم"""
        hallucination_rate = (
            self.hallucinations_detected / max(self.total_checks, 1)
        )
        
        return {
            'total_checks': self.total_checks,
            'hallucinations_detected': self.hallucinations_detected,
            'hallucination_rate': hallucination_rate,
            'guardrail_triggers': dict(self.guardrail_triggers),
            'most_triggered': (
                self.guardrail_triggers.most_common(1)[0]
                if self.guardrail_triggers else None
            )
        }
    
    def reset_statistics(self):
        """ریست آمار"""
        self.total_checks = 0
        self.hallucinations_detected = 0
        self.guardrail_triggers.clear()


# ==============================================================================
# Singleton Instance
# ==============================================================================

_anti_hallucination_instance: Optional[AntiHallucinationSystem] = None

def get_anti_hallucination_system(min_confidence: float = 0.7) -> AntiHallucinationSystem:
    """دریافت instance سینگلتون Anti-Hallucination System"""
    global _anti_hallucination_instance
    
    if _anti_hallucination_instance is None:
        _anti_hallucination_instance = AntiHallucinationSystem(min_confidence)
    
    return _anti_hallucination_instance
