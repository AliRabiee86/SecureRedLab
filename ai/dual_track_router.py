#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Dual-Track Router
=================================

روتر هوشمند برای انتخاب مسیر Reasoning یا Non-Reasoning

Architecture:
    ┌────────────────────────────────────────┐
    │      Dual-Track Router                 │
    ├────────────────────────────────────────┤
    │  1. Task Classification                │
    │     - Complexity analysis              │
    │     - Keyword detection                │
    │     - Pattern matching                 │
    │                                        │
    │  2. Model Selection                    │
    │     - Reasoning: Qwen3/GLM-4.6-R       │
    │     - Non-Reasoning: DeepSeek/GLM-4.6  │
    │     - Fallback logic                   │
    │                                        │
    │  3. Performance Optimization           │
    │     - Cache frequently used routes     │
    │     - Load balancing                   │
    │     - Latency tracking                 │
    └────────────────────────────────────────┘

Decision Logic:
    Reasoning Track IF:
    - Contains analysis keywords
    - Requires multi-step thinking
    - Needs strategic planning
    - Security audit/assessment
    
    Non-Reasoning Track IF:
    - Code generation request
    - Quick exploit generation
    - Fast scanning
    - Payload crafting

تاریخ: 2025-12-08
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from collections import defaultdict

from core.logging_system import get_logger, LogCategory, log_performance
from core.exception_handler import handle_exception, AIException

from ai.offline_core import TaskType, ModelType, ModelCapability
from ai.offline_core import ModelRegistry


class DualTrackRouter:
    """
    روتر دو مسیره برای تشخیص نوع تسک و انتخاب مدل مناسب
    """
    
    # Keywords for reasoning tasks
    REASONING_KEYWORDS = {
        'analyze', 'assessment', 'evaluate', 'compare', 'strategy',
        'planning', 'audit', 'review', 'investigate', 'explain',
        'reasoning', 'think', 'consider', 'pros and cons',
        'تحلیل', 'ارزیابی', 'بررسی', 'مقایسه', 'استراتژی',
        'برنامه‌ریزی', 'ممیزی', 'بازبینی', 'تحقیق', 'توضیح'
    }
    
    # Keywords for code generation
    CODE_GEN_KEYWORDS = {
        'generate', 'create', 'write', 'code', 'script', 'exploit',
        'payload', 'shellcode', 'implement', 'build',
        'تولید', 'ایجاد', 'بنویس', 'کد', 'اسکریپت'
    }
    
    # Keywords for fast tasks
    FAST_KEYWORDS = {
        'quick', 'fast', 'scan', 'check', 'list', 'show',
        'سریع', 'اسکن', 'چک', 'لیست', 'نمایش'
    }
    
    def __init__(self, model_registry: ModelRegistry):
        self.logger = get_logger(__name__, LogCategory.AI)
        self.model_registry = model_registry
        
        # Performance tracking
        self.routing_stats: Dict[TaskType, int] = defaultdict(int)
        self.model_usage: Dict[ModelType, int] = defaultdict(int)
        
        self.logger.info(
            "Dual-Track Router راه‌اندازی شد",
            "Dual-Track Router initialized"
        )
    
    @log_performance
    @handle_exception(fallback_value=(TaskType.CODE_GENERATION, ModelType.GLM_46))
    def route(self, 
              prompt: str,
              context: Optional[Dict] = None,
              prefer_speed: bool = False) -> Tuple[TaskType, ModelType]:
        """
        مسیریابی درخواست به Track مناسب
        
        Args:
            prompt: متن prompt
            context: context اضافی
            prefer_speed: اولویت با سرعت؟
        
        Returns:
            (task_type, model_type)
        """
        # 1. Classify task
        task_type = self._classify_task(prompt, context)
        
        # 2. Select best model
        model_type = self._select_model(task_type, prefer_speed)
        
        # 3. Update stats
        self.routing_stats[task_type] += 1
        self.model_usage[model_type] += 1
        
        self.logger.debug(
            f"مسیریابی: {task_type.value} → {model_type.value}",
            f"Routing: {task_type.value} → {model_type.value}",
            context={
                'prompt_length': len(prompt),
                'prefer_speed': prefer_speed
            }
        )
        
        return task_type, model_type
    
    def _classify_task(self, 
                       prompt: str,
                       context: Optional[Dict] = None) -> TaskType:
        """
        تشخیص نوع تسک از روی prompt
        
        Args:
            prompt: متن prompt
            context: context اضافی
        
        Returns:
            نوع تسک
        """
        prompt_lower = prompt.lower()
        
        # Check for explicit task type in context
        if context and 'task_type' in context:
            return TaskType(context['task_type'])
        
        # Calculate scores for each category
        reasoning_score = self._calculate_keyword_score(
            prompt_lower, self.REASONING_KEYWORDS
        )
        code_gen_score = self._calculate_keyword_score(
            prompt_lower, self.CODE_GEN_KEYWORDS
        )
        fast_score = self._calculate_keyword_score(
            prompt_lower, self.FAST_KEYWORDS
        )
        
        # Check for complexity indicators
        complexity_score = self._calculate_complexity(prompt)
        
        # Decision logic
        if complexity_score > 0.7 or reasoning_score > 2:
            # High complexity → Reasoning track
            if 'vulnerability' in prompt_lower or 'vuln' in prompt_lower:
                return TaskType.VULNERABILITY_ANALYSIS
            elif 'strategy' in prompt_lower or 'plan' in prompt_lower:
                return TaskType.ATTACK_STRATEGY
            elif 'audit' in prompt_lower or 'review' in prompt_lower:
                return TaskType.SECURITY_AUDIT
            else:
                return TaskType.REASONING
        
        elif code_gen_score > 1 or 'code' in prompt_lower or 'script' in prompt_lower:
            # Code generation needed
            if 'exploit' in prompt_lower:
                return TaskType.EXPLOIT_GENERATION
            elif 'payload' in prompt_lower:
                return TaskType.PAYLOAD_CRAFTING
            else:
                return TaskType.CODE_GENERATION
        
        elif fast_score > 1:
            return TaskType.FAST_SCAN
        
        else:
            # Default: code generation (most common in pentesting)
            return TaskType.CODE_GENERATION
    
    def _calculate_keyword_score(self, text: str, keywords: set) -> int:
        """محاسبه امتیاز keyword"""
        return sum(1 for keyword in keywords if keyword in text)
    
    def _calculate_complexity(self, prompt: str) -> float:
        """
        محاسبه پیچیدگی prompt
        
        Indicators:
        - Length
        - Number of questions
        - Multi-step phrases
        - Technical depth
        
        Returns:
            0.0-1.0 (0=simple, 1=complex)
        """
        score = 0.0
        
        # Length factor (longer prompts often need more reasoning)
        if len(prompt) > 500:
            score += 0.3
        elif len(prompt) > 200:
            score += 0.1
        
        # Question marks (multiple questions = complex)
        question_count = prompt.count('?')
        score += min(question_count * 0.15, 0.3)
        
        # Multi-step indicators
        multi_step_patterns = [
            r'\b(first|second|third|finally)\b',
            r'\b(step \d+)\b',
            r'\b(then|after that|next)\b'
        ]
        for pattern in multi_step_patterns:
            if re.search(pattern, prompt, re.IGNORECASE):
                score += 0.2
                break
        
        # Technical depth keywords
        technical_keywords = {
            'architecture', 'design', 'framework', 'methodology',
            'معماری', 'طراحی', 'فریمورک', 'روش‌شناسی'
        }
        if any(kw in prompt.lower() for kw in technical_keywords):
            score += 0.2
        
        return min(score, 1.0)
    
    def _select_model(self, 
                     task_type: TaskType,
                     prefer_speed: bool) -> ModelType:
        """
        انتخاب بهترین مدل برای تسک
        
        Args:
            task_type: نوع تسک
            prefer_speed: اولویت با سرعت؟
        
        Returns:
            نوع مدل
        """
        # Get available VRAM (mock - در واقعیت از GPU query می‌شود)
        available_vram_gb = 96  # فرض: 2x RTX 4090 = 48GB x 2
        
        # Get best model from registry
        best_model = self.model_registry.get_best_model_for_task(
            task_type, 
            max_vram_gb=available_vram_gb if not prefer_speed else 10
        )
        
        if best_model:
            return best_model.model_type
        
        # Fallback logic
        if task_type in [TaskType.REASONING, TaskType.VULNERABILITY_ANALYSIS,
                        TaskType.ATTACK_STRATEGY, TaskType.SECURITY_AUDIT]:
            # Reasoning tasks
            if available_vram_gb >= 59:
                return ModelType.QWEN3_235B
            else:
                return ModelType.GLM_46_REASONING
        else:
            # Non-reasoning tasks
            if prefer_speed or available_vram_gb < 20:
                return ModelType.GLM_46
            elif available_vram_gb >= 72:
                return ModelType.DEEPSEEK_V32_EXP
            else:
                return ModelType.GLM_46
    
    def get_statistics(self) -> Dict:
        """دریافت آمار مسیریابی"""
        total_routes = sum(self.routing_stats.values())
        
        return {
            'total_routes': total_routes,
            'routing_breakdown': dict(self.routing_stats),
            'model_usage': dict(self.model_usage),
            'reasoning_percentage': (
                (self.routing_stats.get(TaskType.REASONING, 0) +
                 self.routing_stats.get(TaskType.VULNERABILITY_ANALYSIS, 0) +
                 self.routing_stats.get(TaskType.ATTACK_STRATEGY, 0) +
                 self.routing_stats.get(TaskType.SECURITY_AUDIT, 0)) / 
                max(total_routes, 1) * 100
            )
        }
    
    def explain_routing(self, prompt: str) -> Dict:
        """
        توضیح چرایی انتخاب مسیر (برای debugging)
        
        Args:
            prompt: متن prompt
        
        Returns:
            توضیحات
        """
        prompt_lower = prompt.lower()
        
        reasoning_score = self._calculate_keyword_score(
            prompt_lower, self.REASONING_KEYWORDS
        )
        code_gen_score = self._calculate_keyword_score(
            prompt_lower, self.CODE_GEN_KEYWORDS
        )
        fast_score = self._calculate_keyword_score(
            prompt_lower, self.FAST_KEYWORDS
        )
        complexity_score = self._calculate_complexity(prompt)
        
        task_type, model_type = self.route(prompt)
        
        return {
            'selected_task': task_type.value,
            'selected_model': model_type.value,
            'scores': {
                'reasoning': reasoning_score,
                'code_generation': code_gen_score,
                'fast': fast_score,
                'complexity': complexity_score
            },
            'reasoning': self._generate_explanation(
                task_type, reasoning_score, code_gen_score, 
                fast_score, complexity_score
            )
        }
    
    def _generate_explanation(self, 
                             task_type: TaskType,
                             reasoning_score: int,
                             code_gen_score: int,
                             fast_score: int,
                             complexity_score: float) -> str:
        """تولید توضیح انسان‌خوان"""
        if complexity_score > 0.7:
            return f"Selected {task_type.value} due to high complexity ({complexity_score:.2f})"
        elif reasoning_score > 2:
            return f"Selected {task_type.value} due to reasoning keywords (score: {reasoning_score})"
        elif code_gen_score > 1:
            return f"Selected {task_type.value} due to code generation keywords (score: {code_gen_score})"
        elif fast_score > 1:
            return f"Selected {task_type.value} due to fast task keywords (score: {fast_score})"
        else:
            return f"Selected {task_type.value} as default choice"


# ==============================================================================
# Singleton Instance
# ==============================================================================

_router_instance: Optional[DualTrackRouter] = None

def get_dual_track_router(model_registry: ModelRegistry) -> DualTrackRouter:
    """دریافت instance سینگلتون Router"""
    global _router_instance
    
    if _router_instance is None:
        _router_instance = DualTrackRouter(model_registry)
    
    return _router_instance
