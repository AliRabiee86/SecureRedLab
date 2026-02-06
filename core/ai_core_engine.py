"""
SecureRedLab - Central AI Engine with Reinforcement Learning & Experience Database
موتور مرکزی هوش مصنوعی با یادگیری تقویتی و پایگاه داده تجربیات

این ماژول هسته اصلی هوش مصنوعی SecureRedLab است که شامل:
- مدیریت 5 مدل بزرگ زبانی (DeepSeek, LLaMA, Mixtral, Qwen, GLM)
- یادگیری تقویتی (RL) برای بهبود مداوم
- پایگاه داده تجربیات برای ذخیره نتایج تست‌ها
- باز آموزی خودکار بعد از هر تست
- استفاده از AI در ابزار تست نفوذ
- اعتبارسنجی خودکار خروجی‌های AI

Legal Requirements:
- FBI Clearance
- IRB Ethics Committee Approval
- Local Police Department Authorization
- University Research Committee Approval

ONLY FOR ACADEMIC RESEARCH - تنها برای تحقیقات آکادمیک
"""

import os
import sys
import json
import time
import pickle
import hashlib
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from abc import ABC, abstractmethod

# Third-party imports (these will be installed in production)
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    print("⚠️  NumPy not available - using fallback mode")

try:
    import tensorflow as tf
    TF_AVAILABLE = True
except ImportError:
    TF_AVAILABLE = False
    print("⚠️  TensorFlow not available - using fallback mode")

# Import our core systems
from core.logging_system import get_logger, LogCategory
from core.exception_handler import (
    handle_exception, retry_on_failure, log_performance,
    AIException, DatabaseException, NetworkException,
    ErrorSeverity, RecoveryStrategy
)
from core.config_manager import get_config
from core.database_manager import get_db_manager
from core.ai_output_validator import get_validator, ValidationType


# ============================================================================
# Enums و Data Classes
# ============================================================================

class AIModelType(Enum):
    """انواع مدل‌های هوش مصنوعی"""
    DEEPSEEK_CODER = "deepseek_coder_33b"  # Priority 1 - تولید کد
    LLAMA_3_1 = "llama_3_1_70b"            # Priority 2 - هوش عمومی
    MIXTRAL_8x22B = "mixtral_8x22b"        # Priority 3 - چند متخصص
    QWEN_14B = "qwen_14b"                  # Priority 4 - تحلیل آسیب‌پذیری
    GLM_4 = "glm_4_6b"                     # Priority 5 - استراتژی حمله


class ModelStatus(Enum):
    """وضعیت مدل"""
    UNLOADED = "unloaded"          # بارگذاری نشده
    LOADING = "loading"            # در حال بارگذاری
    READY = "ready"                # آماده
    BUSY = "busy"                  # مشغول
    ERROR = "error"                # خطا
    UPDATING = "updating"          # در حال به‌روزرسانی


class ActionType(Enum):
    """انواع اقدامات یادگیری تقویتی"""
    INCREASE_INTENSITY = "increase_intensity"      # افزایش شدت
    DECREASE_INTENSITY = "decrease_intensity"      # کاهش شدت
    CHANGE_STRATEGY = "change_strategy"            # تغییر استراتژی
    ADD_EVASION = "add_evasion"                    # افزودن تکنیک فرار
    OPTIMIZE_TIMING = "optimize_timing"            # بهینه‌سازی زمان‌بندی
    STOP_ATTACK = "stop_attack"                    # توقف حمله


class SimulationType(Enum):
    """انواع شبیه‌سازی"""
    DDOS = "ddos"                          # حمله انکار سرویس
    SHELL_UPLOAD = "shell_upload"          # آپلود شل
    DATA_EXTRACTION = "data_extraction"    # استخراج داده
    VULNERABILITY_SCAN = "vuln_scan"       # اسکن آسیب‌پذیری
    PENETRATION_TEST = "pentest"           # تست نفوذ
    DEFACE = "deface"                      # دیفیس
    HUMAN_BEHAVIOR = "human_behavior"      # رفتار انسانی


@dataclass
class AIModelConfig:
    """پیکربندی مدل AI"""
    model_type: AIModelType
    model_path: str
    priority: int
    max_tokens: int = 4096
    temperature: float = 0.7
    top_p: float = 0.9
    enabled: bool = True
    gpu_id: Optional[int] = None
    memory_limit_mb: int = 8192
    quantization: str = "int8"  # int8, int4, fp16, fp32
    
    def to_dict(self) -> Dict:
        """تبدیل به دیکشنری"""
        d = asdict(self)
        d['model_type'] = self.model_type.value
        return d


@dataclass
class Experience:
    """تجربه یادگیری تقویتی - برای ذخیره در پایگاه داده"""
    # فیلدهای بدون default - اجباری
    simulation_type: SimulationType
    state: Dict[str, Any]                    # وضعیت قبل از اقدام
    action: ActionType                       # اقدام انجام‌شده
    reward: float                            # پاداش دریافتی
    next_state: Dict[str, Any]               # وضعیت بعد از اقدام
    done: bool                               # آیا شبیه‌سازی تمام شد؟
    
    # فیلدهای با default - اختیاری
    experience_id: str = field(default_factory=lambda: hashlib.sha256(
        f"{datetime.now().isoformat()}{time.time()}".encode()
    ).hexdigest()[:16])
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = False
    
    def to_dict(self) -> Dict:
        """تبدیل به دیکشنری برای ذخیره در DB"""
        return {
            'experience_id': self.experience_id,
            'simulation_type': self.simulation_type.value,
            'state': json.dumps(self.state),
            'action': self.action.value,
            'reward': self.reward,
            'next_state': json.dumps(self.next_state),
            'done': self.done,
            'metadata': json.dumps(self.metadata),
            'timestamp': self.timestamp.isoformat(),
            'success': self.success
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Experience':
        """ساخت از دیکشنری"""
        return cls(
            experience_id=data['experience_id'],
            simulation_type=SimulationType(data['simulation_type']),
            state=json.loads(data['state']),
            action=ActionType(data['action']),
            reward=data['reward'],
            next_state=json.loads(data['next_state']),
            done=data['done'],
            metadata=json.loads(data['metadata']),
            timestamp=datetime.fromisoformat(data['timestamp']),
            success=data['success']
        )


@dataclass
class ModelPerformanceMetrics:
    """معیارهای عملکرد مدل"""
    model_type: AIModelType
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_latency_ms: float = 0.0
    avg_confidence: float = 0.0
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update(self, latency_ms: float, confidence: float, success: bool):
        """به‌روزرسانی معیارها"""
        self.total_requests += 1
        if success:
            self.successful_requests += 1
        else:
            self.failed_requests += 1
        
        # Exponential moving average
        alpha = 0.1
        self.avg_latency_ms = alpha * latency_ms + (1 - alpha) * self.avg_latency_ms
        self.avg_confidence = alpha * confidence + (1 - alpha) * self.avg_confidence
        self.last_updated = datetime.now()
    
    def get_success_rate(self) -> float:
        """محاسبه نرخ موفقیت"""
        if self.total_requests == 0:
            return 0.0
        return self.successful_requests / self.total_requests


# ============================================================================
# Experience Database Manager
# ============================================================================

class ExperienceDatabase:
    """
    پایگاه داده تجربیات - ذخیره و مدیریت تجربیات یادگیری تقویتی
    
    این کلاس مسئول ذخیره تمام تجربیات یادگیری تقویتی است که
    بعداً برای باز آموزی و بهبود مدل‌ها استفاده می‌شود.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """سازنده"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        self.db_manager = get_db_manager()
        
        self._create_tables()
        self._initialized = True
        
        self.logger.info(
            "پایگاه داده تجربیات راه‌اندازی شد",
            "Experience database initialized"
        )
    
    @handle_exception(
        fallback_value=None,
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.DATABASE
    )
    def _create_tables(self):
        """ساخت جداول پایگاه داده"""
        # جدول تجربیات
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS rl_experiences (
                experience_id TEXT PRIMARY KEY,
                simulation_type TEXT NOT NULL,
                state TEXT NOT NULL,
                action TEXT NOT NULL,
                reward REAL NOT NULL,
                next_state TEXT NOT NULL,
                done BOOLEAN NOT NULL,
                metadata TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                success BOOLEAN DEFAULT FALSE
            )
        """, fetch=False)
        
        # جدول معیارهای مدل
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS model_metrics (
                model_type TEXT PRIMARY KEY,
                total_requests INTEGER DEFAULT 0,
                successful_requests INTEGER DEFAULT 0,
                failed_requests INTEGER DEFAULT 0,
                avg_latency_ms REAL DEFAULT 0.0,
                avg_confidence REAL DEFAULT 0.0,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """, fetch=False)
        
        # جدول تاریخچه باز آموزی
        self.db_manager.execute("""
            CREATE TABLE IF NOT EXISTS retraining_history (
                retrain_id TEXT PRIMARY KEY,
                model_type TEXT NOT NULL,
                experiences_count INTEGER NOT NULL,
                performance_before REAL,
                performance_after REAL,
                improvement_percent REAL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """, fetch=False)
        
        self.logger.audit(
            "DB_TABLES_CREATED",
            "جداول پایگاه داده تجربیات ساخته شد",
            "Experience database tables created",
            context={'tables': ['rl_experiences', 'model_metrics', 'retraining_history']}
        )
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.DATABASE
    )
    @log_performance
    def store_experience(self, experience: Experience) -> bool:
        """
        ذخیره تجربه در پایگاه داده
        
        Args:
            experience: تجربه برای ذخیره
        
        Returns:
            True اگر موفق، False اگر خطا
        """
        exp_dict = experience.to_dict()
        
        self.db_manager.execute("""
            INSERT INTO rl_experiences (
                experience_id, simulation_type, state, action, reward,
                next_state, done, metadata, timestamp, success
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            exp_dict['experience_id'],
            exp_dict['simulation_type'],
            exp_dict['state'],
            exp_dict['action'],
            exp_dict['reward'],
            exp_dict['next_state'],
            exp_dict['done'],
            exp_dict['metadata'],
            exp_dict['timestamp'],
            exp_dict['success']
        ), fetch=False)
        
        self.logger.debug(
            f"تجربه ذخیره شد: {experience.experience_id}",
            f"Experience stored: {experience.experience_id}",
            context={'simulation_type': experience.simulation_type.value}
        )
        
        return True
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.DATABASE
    )
    def get_experiences(self, 
                       simulation_type: Optional[SimulationType] = None,
                       limit: int = 1000,
                       successful_only: bool = False) -> List[Experience]:
        """
        دریافت تجربیات از پایگاه داده
        
        Args:
            simulation_type: نوع شبیه‌سازی (اختیاری)
            limit: تعداد حداکثر تجربیات
            successful_only: فقط تجربیات موفق
        
        Returns:
            لیست تجربیات
        """
        query = "SELECT * FROM rl_experiences WHERE 1=1"
        params = []
        
        if simulation_type:
            query += " AND simulation_type = ?"
            params.append(simulation_type.value)
        
        if successful_only:
            query += " AND success = TRUE"
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        rows = self.db_manager.execute(query, tuple(params))
        
        experiences = []
        for row in rows:
            exp_dict = {
                'experience_id': row[0],
                'simulation_type': row[1],
                'state': row[2],
                'action': row[3],
                'reward': row[4],
                'next_state': row[5],
                'done': row[6],
                'metadata': row[7] or '{}',
                'timestamp': row[8],
                'success': row[9]
            }
            experiences.append(Experience.from_dict(exp_dict))
        
        self.logger.debug(
            f"{len(experiences)} تجربه از پایگاه داده بارگذاری شد",
            f"Loaded {len(experiences)} experiences from database"
        )
        
        return experiences
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.DATABASE
    )
    def get_statistics(self) -> Dict[str, Any]:
        """دریافت آمار پایگاه داده تجربیات"""
        total = self.db_manager.execute(
            "SELECT COUNT(*) FROM rl_experiences"
        )[0][0]
        
        successful = self.db_manager.execute(
            "SELECT COUNT(*) FROM rl_experiences WHERE success = TRUE"
        )[0][0]
        
        by_type = {}
        types_result = self.db_manager.execute("""
            SELECT simulation_type, COUNT(*) 
            FROM rl_experiences 
            GROUP BY simulation_type
        """)
        
        for row in types_result:
            by_type[row[0]] = row[1]
        
        return {
            'total_experiences': total,
            'successful_experiences': successful,
            'success_rate': successful / max(total, 1),
            'by_simulation_type': by_type,
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# Reinforcement Learning Core
# ============================================================================

class ReinforcementLearningCore:
    """
    هسته یادگیری تقویتی - استفاده از Q-Learning برای بهینه‌سازی
    
    این کلاس مسئول یادگیری از تجربیات و بهینه‌سازی استراتژی‌های حمله است.
    بعد از هر تست، نتایج را ذخیره کرده و مدل را باز آموزی می‌دهد.
    """
    
    def __init__(self):
        """سازنده"""
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        self.exp_db = ExperienceDatabase()
        
        # Q-Learning hyperparameters
        self.learning_rate = self.config.get('ai.rl.learning_rate', 0.001)
        self.discount_factor = self.config.get('ai.rl.discount_factor', 0.95)
        self.epsilon = self.config.get('ai.rl.epsilon', 0.1)  # Exploration rate
        self.epsilon_decay = self.config.get('ai.rl.epsilon_decay', 0.995)
        self.epsilon_min = self.config.get('ai.rl.epsilon_min', 0.01)
        
        # Q-Table (state-action values)
        # در نسخه ساده از dictionary استفاده می‌کنیم
        # در نسخه پیشرفته از Neural Network استفاده می‌شود
        self.q_table: Dict[str, Dict[str, float]] = {}
        
        # Load existing Q-table if available
        self._load_q_table()
        
        self.logger.info(
            "هسته یادگیری تقویتی راه‌اندازی شد",
            "Reinforcement Learning Core initialized",
            context={
                'learning_rate': self.learning_rate,
                'discount_factor': self.discount_factor,
                'epsilon': self.epsilon
            }
        )
    
    def _load_q_table(self):
        """بارگذاری Q-Table از فایل"""
        q_table_path = self.config.get('ai.rl.q_table_path', 
                                      '/home/user/webapp/SecureRedLab/data/q_table.pkl')
        
        if os.path.exists(q_table_path):
            try:
                with open(q_table_path, 'rb') as f:
                    self.q_table = pickle.load(f)
                self.logger.info(
                    f"Q-Table بارگذاری شد: {len(self.q_table)} وضعیت",
                    f"Q-Table loaded: {len(self.q_table)} states"
                )
            except Exception as e:
                self.logger.warning(
                    f"خطا در بارگذاری Q-Table: {e}",
                    f"Error loading Q-Table: {e}"
                )
    
    def _save_q_table(self):
        """ذخیره Q-Table در فایل"""
        q_table_path = self.config.get('ai.rl.q_table_path',
                                      '/home/user/webapp/SecureRedLab/data/q_table.pkl')
        
        os.makedirs(os.path.dirname(q_table_path), exist_ok=True)
        
        try:
            with open(q_table_path, 'wb') as f:
                pickle.dump(self.q_table, f)
            self.logger.debug(
                "Q-Table ذخیره شد",
                "Q-Table saved"
            )
        except Exception as e:
            self.logger.error(
                f"خطا در ذخیره Q-Table: {e}",
                f"Error saving Q-Table: {e}"
            )
    
    def _state_to_key(self, state: Dict[str, Any]) -> str:
        """تبدیل وضعیت به کلید رشته‌ای"""
        # برای سادگی، از JSON استفاده می‌کنیم
        # در نسخه پیشرفته، از feature encoding استفاده می‌شود
        return json.dumps(state, sort_keys=True)
    
    def _get_q_value(self, state: Dict[str, Any], action: ActionType) -> float:
        """دریافت Q-value برای یک state-action"""
        state_key = self._state_to_key(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {action.value: 0.0 for action in ActionType}
        return self.q_table[state_key].get(action.value, 0.0)
    
    def _set_q_value(self, state: Dict[str, Any], action: ActionType, value: float):
        """تنظیم Q-value برای یک state-action"""
        state_key = self._state_to_key(state)
        if state_key not in self.q_table:
            self.q_table[state_key] = {action.value: 0.0 for action in ActionType}
        self.q_table[state_key][action.value] = value
    
    @log_performance
    def select_action(self, state: Dict[str, Any], 
                     available_actions: Optional[List[ActionType]] = None) -> ActionType:
        """
        انتخاب اقدام بهینه با استفاده از epsilon-greedy
        
        Args:
            state: وضعیت فعلی
            available_actions: اقدامات مجاز (اختیاری)
        
        Returns:
            اقدام انتخاب‌شده
        """
        if available_actions is None:
            available_actions = list(ActionType)
        
        # Epsilon-greedy exploration
        if NUMPY_AVAILABLE:
            explore = np.random.random() < self.epsilon
        else:
            import random
            explore = random.random() < self.epsilon
        
        if explore:
            # Exploration - اقدام تصادفی
            if NUMPY_AVAILABLE:
                action = available_actions[np.random.randint(0, len(available_actions))]
            else:
                import random
                action = random.choice(available_actions)
            
            self.logger.debug(
                f"Exploration - اقدام تصادفی: {action.value}",
                f"Exploration - random action: {action.value}"
            )
        else:
            # Exploitation - بهترین اقدام
            q_values = {action: self._get_q_value(state, action) 
                       for action in available_actions}
            action = max(q_values, key=q_values.get)
            
            self.logger.debug(
                f"Exploitation - بهترین اقدام: {action.value} (Q={q_values[action]:.3f})",
                f"Exploitation - best action: {action.value} (Q={q_values[action]:.3f})"
            )
        
        return action
    
    @log_performance
    def update_q_value(self, experience: Experience):
        """
        به‌روزرسانی Q-value با استفاده از تجربه جدید
        
        Q-Learning Update Rule:
        Q(s,a) = Q(s,a) + α * [r + γ * max(Q(s',a')) - Q(s,a)]
        
        Args:
            experience: تجربه یادگیری
        """
        state = experience.state
        action = experience.action
        reward = experience.reward
        next_state = experience.next_state
        done = experience.done
        
        # فعلی Q-value
        current_q = self._get_q_value(state, action)
        
        # بهترین Q-value برای وضعیت بعدی
        if done:
            max_next_q = 0.0  # اگر تمام شد، ارزش آینده صفر است
        else:
            next_q_values = [self._get_q_value(next_state, a) for a in ActionType]
            max_next_q = max(next_q_values)
        
        # محاسبه Q-value جدید
        new_q = current_q + self.learning_rate * (
            reward + self.discount_factor * max_next_q - current_q
        )
        
        # به‌روزرسانی
        self._set_q_value(state, action, new_q)
        
        self.logger.debug(
            f"Q-value به‌روز شد: {action.value} = {new_q:.3f} (قبلی: {current_q:.3f})",
            f"Q-value updated: {action.value} = {new_q:.3f} (previous: {current_q:.3f})",
            context={'reward': reward, 'improvement': new_q - current_q}
        )
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.AI
    )
    @log_performance
    def retrain_from_experiences(self, 
                                simulation_type: Optional[SimulationType] = None,
                                min_experiences: int = 100) -> Dict[str, Any]:
        """
        باز آموزی از تجربیات ذخیره‌شده
        
        این متد تمام تجربیات را از پایگاه داده می‌خواند و
        Q-values را به‌روز می‌کند.
        
        Args:
            simulation_type: نوع شبیه‌سازی (None = همه)
            min_experiences: حداقل تعداد تجربیات برای باز آموزی
        
        Returns:
            آمار باز آموزی
        """
        self.logger.info(
            "شروع باز آموزی از تجربیات...",
            "Starting retraining from experiences..."
        )
        
        # دریافت تجربیات
        experiences = self.exp_db.get_experiences(
            simulation_type=simulation_type,
            limit=10000,
            successful_only=False  # از همه تجربیات یاد بگیر
        )
        
        if len(experiences) < min_experiences:
            self.logger.warning(
                f"تجربیات کافی نیست: {len(experiences)} < {min_experiences}",
                f"Insufficient experiences: {len(experiences)} < {min_experiences}"
            )
            return {
                'status': 'skipped',
                'reason': 'insufficient_experiences',
                'experiences_count': len(experiences)
            }
        
        # ذخیره عملکرد قبل از باز آموزی
        q_table_before = len(self.q_table)
        
        # به‌روزرسانی Q-values
        updated_count = 0
        for exp in experiences:
            self.update_q_value(exp)
            updated_count += 1
        
        # ذخیره Q-Table
        self._save_q_table()
        
        # ذخیره عملکرد بعد از باز آموزی
        q_table_after = len(self.q_table)
        
        result = {
            'status': 'success',
            'experiences_count': len(experiences),
            'updated_count': updated_count,
            'q_table_states_before': q_table_before,
            'q_table_states_after': q_table_after,
            'new_states_learned': q_table_after - q_table_before,
            'epsilon': self.epsilon,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.audit(
            "RL_RETRAIN_COMPLETE",
            f"باز آموزی کامل شد: {updated_count} تجربه پردازش شد",
            f"Retraining completed: {updated_count} experiences processed",
            context=result
        )
        
        return result


# ============================================================================
# AI Model Manager
# ============================================================================

class AIModelManager:
    """
    مدیریت مدل‌های بزرگ زبانی
    
    این کلاس مسئول بارگذاری، مدیریت و استفاده از 5 مدل AI است:
    - DeepSeek-Coder-33B (Priority 1)
    - LLaMA-3.1-70B (Priority 2)
    - Mixtral-8x22B (Priority 3)
    - Qwen-14B (Priority 4)
    - GLM-4-6B (Priority 5)
    """
    
    def __init__(self):
        """سازنده"""
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        self.validator = get_validator()
        
        self.models: Dict[AIModelType, Dict[str, Any]] = {}
        self.model_configs: Dict[AIModelType, AIModelConfig] = {}
        self.model_metrics: Dict[AIModelType, ModelPerformanceMetrics] = {}
        
        self._lock = threading.Lock()
        
        self._initialize_model_configs()
        
        self.logger.info(
            "مدیریت مدل‌های AI راه‌اندازی شد",
            "AI Model Manager initialized",
            context={'models_count': len(self.model_configs)}
        )
    
    def _initialize_model_configs(self):
        """راه‌اندازی پیکربندی مدل‌ها از config"""
        models_config = self.config.get('ai_models', {})
        
        for model_name, model_data in models_config.items():
            try:
                model_type = AIModelType(model_name)
                
                self.model_configs[model_type] = AIModelConfig(
                    model_type=model_type,
                    model_path=model_data.get('path', ''),
                    priority=model_data.get('priority', 999),
                    enabled=model_data.get('enabled', True),
                    max_tokens=model_data.get('max_tokens', 4096),
                    temperature=model_data.get('temperature', 0.7),
                    quantization=model_data.get('quantization', 'int8')
                )
                
                self.model_metrics[model_type] = ModelPerformanceMetrics(
                    model_type=model_type
                )
                
                self.logger.debug(
                    f"مدل پیکربندی شد: {model_name} (اولویت {model_data.get('priority')})",
                    f"Model configured: {model_name} (priority {model_data.get('priority')})"
                )
                
            except ValueError as e:
                self.logger.warning(
                    f"مدل نامعتبر در config: {model_name}",
                    f"Invalid model in config: {model_name}"
                )
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.AI
    )
    def load_model(self, model_type: AIModelType) -> bool:
        """
        بارگذاری مدل (mock در حالت توسعه)
        
        در محیط production، این متد مدل واقعی را از دیسک بارگذاری می‌کند.
        در حالت توسعه، یک mock model ساده می‌سازد.
        
        Args:
            model_type: نوع مدل
        
        Returns:
            True اگر موفق
        """
        with self._lock:
            if model_type in self.models:
                self.logger.info(
                    f"مدل قبلاً بارگذاری شده: {model_type.value}",
                    f"Model already loaded: {model_type.value}"
                )
                return True
            
            config = self.model_configs.get(model_type)
            if not config or not config.enabled:
                raise AIException(
                    f"مدل غیرفعال یا پیکربندی نشده: {model_type.value}",
                    f"Model disabled or not configured: {model_type.value}",
                    severity=ErrorSeverity.MEDIUM
                )
            
            self.logger.info(
                f"در حال بارگذاری مدل: {model_type.value}...",
                f"Loading model: {model_type.value}..."
            )
            
            # در محیط توسعه، mock model می‌سازیم
            # در production، از HuggingFace Transformers استفاده می‌شود
            self.models[model_type] = {
                'type': model_type,
                'status': ModelStatus.READY,
                'config': config,
                'loaded_at': datetime.now(),
                'mock': True  # Flag for mock model
            }
            
            self.logger.audit(
                "AI_MODEL_LOADED",
                f"مدل بارگذاری شد: {model_type.value}",
                f"Model loaded: {model_type.value}",
                context={'model_type': model_type.value, 'priority': config.priority}
            )
            
            return True
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.AI
    )
    @log_performance
    def generate(self, 
                prompt: str,
                model_type: Optional[AIModelType] = None,
                validate_output: bool = True,
                max_retries: int = 3) -> Dict[str, Any]:
        """
        تولید متن با استفاده از مدل AI
        
        این متد:
        1. مدل مناسب را انتخاب می‌کند (بر اساس priority)
        2. prompt را به مدل می‌دهد
        3. خروجی را validate می‌کند
        4. در صورت خطا، به مدل بعدی fallback می‌کند
        
        Args:
            prompt: متن ورودی
            model_type: نوع مدل (None = بهترین مدل موجود)
            validate_output: اعتبارسنجی خروجی
            max_retries: تعداد تلاش مجدد
        
        Returns:
            نتیجه تولید شده
        """
        start_time = time.time()
        
        # انتخاب مدل
        if model_type is None:
            # انتخاب بهترین مدل موجود بر اساس priority
            available_models = [
                (m, c) for m, c in self.model_configs.items() 
                if c.enabled
            ]
            if not available_models:
                raise AIException(
                    "هیچ مدل فعالی موجود نیست",
                    "No active models available",
                    severity=ErrorSeverity.CRITICAL
                )
            
            available_models.sort(key=lambda x: x[1].priority)
            model_type = available_models[0][0]
        
        # بارگذاری مدل اگر بارگذاری نشده
        if model_type not in self.models:
            self.load_model(model_type)
        
        model = self.models[model_type]
        model['status'] = ModelStatus.BUSY
        
        try:
            # تولید متن (mock در حالت توسعه)
            if model.get('mock', False):
                # Mock response for development
                output = self._generate_mock_response(prompt, model_type)
            else:
                # Real model inference (در production)
                output = self._generate_real_response(prompt, model_type)
            
            latency_ms = (time.time() - start_time) * 1000
            
            # اعتبارسنجی خروجی
            validation_result = None
            if validate_output:
                validation_result = self.validator.validate(
                    output,
                    [
                        ValidationType.HALLUCINATION,
                        ValidationType.COMMAND_SAFETY
                    ]
                )
                
                if not validation_result.is_valid:
                    self.logger.warning(
                        f"خروجی AI نامعتبر از {model_type.value}: {validation_result.errors}",
                        f"Invalid AI output from {model_type.value}: {validation_result.errors}"
                    )
                    
                    # Fallback to next priority model
                    if max_retries > 0:
                        next_models = [
                            m for m, c in sorted(self.model_configs.items(), 
                                               key=lambda x: x[1].priority)
                            if m != model_type and c.enabled
                        ]
                        
                        if next_models:
                            self.logger.info(
                                f"Fallback به مدل {next_models[0].value}",
                                f"Falling back to model {next_models[0].value}"
                            )
                            return self.generate(
                                prompt, 
                                model_type=next_models[0],
                                validate_output=validate_output,
                                max_retries=max_retries - 1
                            )
            
            # به‌روزرسانی metrics
            confidence = validation_result.confidence_score if validation_result else 1.0
            self.model_metrics[model_type].update(
                latency_ms=latency_ms,
                confidence=confidence,
                success=validation_result.is_valid if validation_result else True
            )
            
            result = {
                'status': 'success',
                'model_type': model_type.value,
                'output': output,
                'latency_ms': latency_ms,
                'validation': validation_result.to_dict() if validation_result else None,
                'timestamp': datetime.now().isoformat()
            }
            
            self.logger.debug(
                f"تولید موفق از {model_type.value} ({latency_ms:.0f}ms)",
                f"Generated successfully from {model_type.value} ({latency_ms:.0f}ms)"
            )
            
            return result
            
        finally:
            model['status'] = ModelStatus.READY
    
    def _generate_mock_response(self, prompt: str, model_type: AIModelType) -> str:
        """تولید پاسخ mock برای توسعه"""
        responses = {
            AIModelType.DEEPSEEK_CODER: f"""```python
# Generated by {model_type.value}
# Analysis of: {prompt[:50]}...

def exploit_vulnerability(target):
    # Step 1: Reconnaissance
    info = scan_target(target)
    
    # Step 2: Identify vulnerabilities
    vulns = analyze_vulnerabilities(info)
    
    # Step 3: Exploit
    for vuln in vulns:
        if exploit(vuln):
            return True
    
    return False
```""",
            AIModelType.LLAMA_3_1: f"Based on my analysis of '{prompt[:50]}...', here are the key findings:\n1. Target appears vulnerable to SQL injection\n2. Port 22 (SSH) is open but secured\n3. Recommend testing XSS vectors\n4. Firewall rules seem misconfigured",
            AIModelType.MIXTRAL_8x22B: f"Multi-expert analysis for: {prompt[:50]}...\n\nExpert 1 (Security): High-risk target, proceed with caution\nExpert 2 (Network): Multiple entry points detected\nExpert 3 (Web): Application layer vulnerabilities present\nExpert 4 (Database): SQL injection likely possible",
            AIModelType.QWEN_14B: f"Vulnerability Assessment:\n- Target: {prompt[:30]}...\n- Risk Level: HIGH\n- CVE Matches: CVE-2024-1234, CVE-2024-5678\n- Recommended Actions: Patch immediately, enable WAF",
            AIModelType.GLM_4: f"Attack Strategy for: {prompt[:50]}...\n\nPhase 1: Stealth reconnaissance\nPhase 2: Exploit identified weaknesses\nPhase 3: Establish persistence\nPhase 4: Data exfiltration\nPhase 5: Cover tracks"
        }
        
        return responses.get(model_type, f"Mock response from {model_type.value}: {prompt[:100]}...")
    
    def _generate_real_response(self, prompt: str, model_type: AIModelType) -> str:
        """تولید پاسخ واقعی از مدل (در production)"""
        # این قسمت در production با HuggingFace Transformers پیاده می‌شود
        # from transformers import AutoModelForCausalLM, AutoTokenizer
        # model = self.models[model_type]['model']
        # tokenizer = self.models[model_type]['tokenizer']
        # ...
        raise NotImplementedError("Real model inference not implemented in development mode")
    
    def get_model_status(self, model_type: Optional[AIModelType] = None) -> Dict[str, Any]:
        """دریافت وضعیت مدل(ها)"""
        if model_type:
            model = self.models.get(model_type)
            metrics = self.model_metrics.get(model_type)
            
            if not model:
                return {'status': 'not_loaded'}
            
            return {
                'model_type': model_type.value,
                'status': model['status'].value,
                'loaded_at': model['loaded_at'].isoformat(),
                'metrics': {
                    'total_requests': metrics.total_requests,
                    'success_rate': metrics.get_success_rate(),
                    'avg_latency_ms': metrics.avg_latency_ms,
                    'avg_confidence': metrics.avg_confidence
                }
            }
        else:
            return {
                model_type.value: self.get_model_status(model_type)
                for model_type in self.model_configs.keys()
            }


# ============================================================================
# Central AI Engine - Main Class
# ============================================================================

class CentralAIEngine:
    """
    موتور مرکزی هوش مصنوعی SecureRedLab
    
    این کلاس اصلی‌ترین بخش سیستم AI است که:
    - مدیریت 5 مدل بزرگ زبانی
    - یادگیری تقویتی برای بهینه‌سازی
    - پایگاه داده تجربیات
    - باز آموزی خودکار
    - استفاده از AI در تست نفوذ
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        """Singleton pattern"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """سازنده"""
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        self.validator = get_validator()
        
        # Core components
        self.model_manager = AIModelManager()
        self.rl_core = ReinforcementLearningCore()
        self.exp_db = ExperienceDatabase()
        
        self._initialized = True
        
        self.logger.audit(
            "AI_ENGINE_INITIALIZED",
            "موتور مرکزی هوش مصنوعی راه‌اندازی شد",
            "Central AI Engine initialized",
            context={
                'models_count': len(self.model_manager.model_configs),
                'rl_enabled': True,
                'exp_db_enabled': True
            }
        )
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.AI
    )
    @log_performance
    def run_simulation(self,
                      simulation_type: SimulationType,
                      target_info: Dict[str, Any],
                      use_rl: bool = True) -> Dict[str, Any]:
        """
        اجرای شبیه‌سازی تست نفوذ با AI
        
        این متد:
        1. از RL برای انتخاب بهترین استراتژی استفاده می‌کند
        2. از AI برای تولید payload استفاده می‌کند
        3. نتایج را ذخیره می‌کند
        4. مدل را باز آموزی می‌کند
        
        Args:
            simulation_type: نوع شبیه‌سازی
            target_info: اطلاعات هدف
            use_rl: استفاده از یادگیری تقویتی
        
        Returns:
            نتیجه شبیه‌سازی
        """
        self.logger.info(
            f"شروع شبیه‌سازی: {simulation_type.value}",
            f"Starting simulation: {simulation_type.value}",
            context={'target': target_info.get('target', 'unknown')}
        )
        
        # مرحله 1: انتخاب استراتژی با RL
        state = self._extract_state(target_info, simulation_type)
        
        if use_rl:
            action = self.rl_core.select_action(state)
            self.logger.debug(
                f"RL اقدام انتخاب کرد: {action.value}",
                f"RL selected action: {action.value}"
            )
        else:
            # استراتژی پیش‌فرض
            action = ActionType.INCREASE_INTENSITY
        
        # مرحله 2: تولید payload با AI
        prompt = self._create_prompt(simulation_type, target_info, action)
        ai_response = self.model_manager.generate(
            prompt=prompt,
            validate_output=True
        )
        
        if ai_response['status'] != 'success':
            raise AIException(
                "خطا در تولید payload توسط AI",
                "Error generating payload with AI",
                severity=ErrorSeverity.HIGH
            )
        
        # مرحله 3: اجرای شبیه‌سازی (mock در حالت توسعه)
        sim_result = self._execute_simulation(
            simulation_type=simulation_type,
            action=action,
            ai_payload=ai_response['output'],
            target_info=target_info
        )
        
        # مرحله 4: ذخیره تجربه
        next_state = self._extract_state(target_info, simulation_type, after_action=True)
        
        experience = Experience(
            simulation_type=simulation_type,
            state=state,
            action=action,
            reward=sim_result['reward'],
            next_state=next_state,
            done=sim_result['done'],
            metadata={
                'target': target_info.get('target', 'unknown'),
                'ai_model': ai_response['model_type'],
                'validation_confidence': ai_response['validation']['confidence_score']
                    if ai_response['validation'] else 1.0
            },
            success=sim_result['success']
        )
        
        self.exp_db.store_experience(experience)
        
        # مرحله 5: به‌روزرسانی RL
        if use_rl:
            self.rl_core.update_q_value(experience)
        
        # مرحله 6: باز آموزی خودکار (هر 100 تجربه)
        exp_stats = self.exp_db.get_statistics()
        if exp_stats['total_experiences'] % 100 == 0:
            self.logger.info(
                "شروع باز آموزی خودکار (100 تجربه جدید)",
                "Starting automatic retraining (100 new experiences)"
            )
            self.rl_core.retrain_from_experiences(simulation_type=simulation_type)
        
        result = {
            'status': 'success',
            'simulation_type': simulation_type.value,
            'action_taken': action.value,
            'ai_model_used': ai_response['model_type'],
            'reward': sim_result['reward'],
            'success': sim_result['success'],
            'experience_id': experience.experience_id,
            'details': sim_result['details'],
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.audit(
            "SIMULATION_COMPLETE",
            f"شبیه‌سازی کامل شد: {simulation_type.value} ({'موفق' if sim_result['success'] else 'ناموفق'})",
            f"Simulation completed: {simulation_type.value} ({'success' if sim_result['success'] else 'failed'})",
            context=result
        )
        
        return result
    
    def _extract_state(self, 
                      target_info: Dict[str, Any],
                      simulation_type: SimulationType,
                      after_action: bool = False) -> Dict[str, Any]:
        """استخراج وضعیت از اطلاعات هدف"""
        state = {
            'simulation_type': simulation_type.value,
            'target_ip': target_info.get('target', '0.0.0.0'),
            'open_ports': len(target_info.get('open_ports', [])),
            'services_count': len(target_info.get('services', [])),
            'os_type': target_info.get('os_type', 'unknown'),
            'firewall_detected': target_info.get('firewall', False),
            'waf_detected': target_info.get('waf', False),
            'timestamp': datetime.now().isoformat(),
            'after_action': after_action
        }
        return state
    
    def _create_prompt(self,
                      simulation_type: SimulationType,
                      target_info: Dict[str, Any],
                      action: ActionType) -> str:
        """ساخت prompt برای مدل AI"""
        prompts = {
            SimulationType.DDOS: f"""Generate a DDoS attack strategy for target {target_info.get('target', 'unknown')}.
Action: {action.value}
Target Info: {json.dumps(target_info, indent=2)}

Provide:
1. Bot count recommendation
2. Attack duration
3. Traffic pattern
4. Evasion techniques""",
            
            SimulationType.SHELL_UPLOAD: f"""Generate a shell upload strategy for target {target_info.get('target', 'unknown')}.
Action: {action.value}
Target Info: {json.dumps(target_info, indent=2)}

Provide:
1. Upload method (POST, WebDAV, FTP)
2. Shell code (PHP, JSP, ASPX)
3. Bypass techniques
4. Post-exploitation commands""",
            
            SimulationType.VULNERABILITY_SCAN: f"""Generate a vulnerability scanning strategy for target {target_info.get('target', 'unknown')}.
Action: {action.value}
Target Info: {json.dumps(target_info, indent=2)}

Provide:
1. Scan methodology
2. Target ports and services
3. CVE database queries
4. Exploitation recommendations"""
        }
        
        return prompts.get(simulation_type, f"Analyze target: {target_info}")
    
    def _execute_simulation(self,
                           simulation_type: SimulationType,
                           action: ActionType,
                           ai_payload: str,
                           target_info: Dict[str, Any]) -> Dict[str, Any]:
        """اجرای شبیه‌سازی (mock در حالت توسعه)"""
        # در محیط توسعه، نتیجه mock می‌سازیم
        # در production، واقعاً شبیه‌سازی اجرا می‌شود
        
        import random
        success = random.random() > 0.3  # 70% success rate for testing
        
        if success:
            reward = random.uniform(0.5, 1.0)
            details = "Simulation executed successfully"
        else:
            reward = random.uniform(-1.0, 0.0)
            details = "Simulation failed - target defended successfully"
        
        return {
            'success': success,
            'reward': reward,
            'done': True,
            'details': details,
            'execution_time': random.uniform(1.0, 5.0)
        }
    
    @handle_exception(
        recovery_strategy=RecoveryStrategy.LOG,
        logger_category=LogCategory.AI
    )
    def get_system_status(self) -> Dict[str, Any]:
        """دریافت وضعیت کلی سیستم AI"""
        exp_stats = self.exp_db.get_statistics()
        model_status = self.model_manager.get_model_status()
        
        return {
            'engine_status': 'active',
            'models': model_status,
            'reinforcement_learning': {
                'epsilon': self.rl_core.epsilon,
                'q_table_size': len(self.rl_core.q_table),
                'learning_rate': self.rl_core.learning_rate
            },
            'experience_database': exp_stats,
            'timestamp': datetime.now().isoformat()
        }


# ============================================================================
# Global Singleton Functions
# ============================================================================

_ai_engine_instance = None

def get_ai_engine() -> CentralAIEngine:
    """
    دریافت instance موتور AI (Singleton)
    
    Returns:
        CentralAIEngine instance
    """
    global _ai_engine_instance
    if _ai_engine_instance is None:
        _ai_engine_instance = CentralAIEngine()
    return _ai_engine_instance


# ============================================================================
# Main - برای تست
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("SecureRedLab - Central AI Engine Test")
    print("موتور مرکزی هوش مصنوعی - تست")
    print("=" * 70)
    
    # راه‌اندازی موتور
    engine = get_ai_engine()
    
    # نمایش وضعیت
    status = engine.get_system_status()
    print("\n✅ وضعیت سیستم:")
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 70)
    print("✅ موتور مرکزی AI با موفقیت راه‌اندازی شد!")
    print("=" * 70)
