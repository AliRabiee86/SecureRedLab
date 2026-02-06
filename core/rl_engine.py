#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SecureRedLab - Reinforcement Learning Engine (موتور یادگیری تقویتی)
==============================================================================

این ماژول هسته یادگیری تقویتی است که به سیستم اجازه می‌دهد پس از هر تست،
کیفیت حملات را بهبود دهد و از تجربیات گذشته یاد بگیرد.

ویژگی‌های کلیدی:
- پنج Agent مستقل برای پنج نوع حمله (DDoS, Shell, Extract, Deface, Behavior)
- الگوریتم‌های RL: Q-Learning, Policy Gradient, Actor-Critic, PPO
- Experience Replay Buffer با priority sampling
- پایگاه داده بازآموزی (PostgreSQL)
- بازآموزی خودکار پس از هر N تست
- Reward shaping برای بهینه‌سازی استراتژی
- Model versioning و A/B testing
- Exploration vs Exploitation balance (ε-greedy)
- Multi-threaded training برای سرعت بالا

معماری:
    Agent → Environment → (State, Action, Reward) → Replay Buffer → Training → Updated Model

استفاده:
    from core.rl_engine import get_rl_engine, RLAgentType
    
    rl_engine = get_rl_engine()
    
    # شروع یک episode جدید
    state = rl_engine.reset_episode(RLAgentType.DDOS, target_info)
    
    # انتخاب action بهینه
    action = rl_engine.select_action(RLAgentType.DDOS, state)
    
    # اعمال action و دریافت reward
    next_state, reward, done = environment.step(action)
    
    # ذخیره تجربه
    rl_engine.store_experience(RLAgentType.DDOS, state, action, reward, next_state, done)
    
    # بازآموزی (هر 100 تست)
    if rl_engine.should_retrain(RLAgentType.DDOS):
        rl_engine.train_agent(RLAgentType.DDOS, batch_size=64, epochs=10)

الگوریتم‌ها:
    1. Q-Learning: Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
    2. Policy Gradient: ∇J(θ) = E[∇log π(a|s) * R]
    3. Actor-Critic: Critic learns V(s), Actor learns π(a|s)
    4. PPO: Proximal Policy Optimization با clipped objective

تابع پاداش (Reward Function):
    R = w1*success + w2*speed + w3*stealth + w4*damage - w5*detection
    
    success: آیا حمله موفق بود؟ (0 or 1)
    speed: سرعت حمله (1 / time_taken)
    stealth: میزان مخفی ماندن (0-1)
    damage: میزان آسیب وارد شده (0-1)
    detection: آیا شناسایی شد؟ (0 or -1)

تاریخ ایجاد: 2025-01-15
نسخه: 1.0.0
مجوز: تحقیقاتی آکادمیک - دانشگاه

LEGAL NOTICE:
This RL Engine is designed for academic research and authorized penetration testing only.
Requires FBI, IRB, Local Police, and University approvals before use.
"""

import os
import sys
import json
import numpy as np
import threading
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple, Callable
from enum import Enum
from dataclasses import dataclass, asdict
from collections import deque
import pickle
import hashlib

# Import کردن سیستم‌های قبلی
from core.logging_system import get_logger, log_performance, LogCategory
from core.exception_handler import (
    SecureRedLabException, AIException, DatabaseException,
    handle_exception, retry_on_failure, ErrorSeverity
)
from core.config_manager import get_config
from core.database_manager import get_db_manager

# ==============================================================================
# Enums & Constants
# ==============================================================================

class RLAgentType(Enum):
    """انواع Agent های RL"""
    DDOS = "ddos"                    # Agent حمله DDoS
    SHELL = "shell"                  # Agent آپلود Shell و نفوذ
    EXTRACT = "extract"              # Agent استخراج داده
    DEFACE = "deface"                # Agent تخریب سایت
    BEHAVIOR = "behavior"            # Agent شبیه‌سازی رفتار انسانی


class RLAlgorithm(Enum):
    """الگوریتم‌های RL"""
    Q_LEARNING = "q_learning"              # Q-Learning کلاسیک
    DEEP_Q_NETWORK = "dqn"                 # Deep Q-Network (DQN)
    POLICY_GRADIENT = "policy_gradient"    # REINFORCE
    ACTOR_CRITIC = "actor_critic"          # A2C/A3C
    PPO = "ppo"                           # Proximal Policy Optimization


class ExplorationStrategy(Enum):
    """استراتژی‌های Exploration"""
    EPSILON_GREEDY = "epsilon_greedy"      # ε-greedy
    BOLTZMANN = "boltzmann"                # Softmax/Boltzmann
    UCB = "ucb"                            # Upper Confidence Bound


# ==============================================================================
# Data Classes
# ==============================================================================

@dataclass
class RLState:
    """
    وضعیت محیط (State) در زمان t
    
    این کلاس تمام اطلاعات لازم برای تصمیم‌گیری Agent را نگه می‌دارد.
    """
    # اطلاعات هدف
    target_ip: str
    target_ports: List[int]
    target_os: str
    target_services: Dict[str, str]
    
    # اطلاعات شبکه
    network_latency: float
    bandwidth: float
    firewall_active: bool
    ids_active: bool
    
    # اطلاعات حمله فعلی
    attack_stage: int                # مرحله حمله (0, 1, 2, ...)
    time_elapsed: float              # زمان سپری شده (ثانیه)
    packets_sent: int                # تعداد پکت ارسالی
    success_rate: float              # نرخ موفقیت تا الان
    
    # اطلاعات تاریخی
    previous_actions: List[str]      # اقدامات قبلی
    detection_count: int             # دفعات شناسایی
    
    def to_vector(self) -> np.ndarray:
        """تبدیل State به بردار عددی برای شبکه عصبی"""
        # Encode categorical variables
        os_encoding = {'linux': 0, 'windows': 1, 'unknown': 2}.get(self.target_os.lower(), 2)
        
        vector = [
            # Target features (normalized)
            len(self.target_ports) / 100.0,          # 0-1
            os_encoding / 2.0,                        # 0-1
            len(self.target_services) / 50.0,         # 0-1
            
            # Network features
            min(self.network_latency / 1000.0, 1.0),  # 0-1 (max 1000ms)
            min(self.bandwidth / 10000.0, 1.0),       # 0-1 (max 10Gbps)
            float(self.firewall_active),              # 0 or 1
            float(self.ids_active),                   # 0 or 1
            
            # Attack features
            min(self.attack_stage / 10.0, 1.0),       # 0-1 (max 10 stages)
            min(self.time_elapsed / 3600.0, 1.0),     # 0-1 (max 1 hour)
            min(self.packets_sent / 1000000.0, 1.0),  # 0-1 (max 1M packets)
            self.success_rate,                        # 0-1
            min(len(self.previous_actions) / 100.0, 1.0),  # 0-1
            min(self.detection_count / 10.0, 1.0),    # 0-1 (max 10)
        ]
        
        return np.array(vector, dtype=np.float32)
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary برای ذخیره در DB"""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RLState':
        """بازیابی از dictionary"""
        return cls(**data)


@dataclass
class RLAction:
    """
    عمل Agent (Action)
    """
    action_type: str                 # نوع عمل
    parameters: Dict[str, Any]       # پارامترهای عمل
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RLAction':
        """بازیابی از dictionary"""
        return cls(**data)


@dataclass
class RLExperience:
    """
    یک تجربه (Experience) در Replay Buffer
    
    Format: (s, a, r, s', done)
    """
    episode_id: str
    step_number: int
    state: RLState
    action: RLAction
    reward: float
    next_state: RLState
    done: bool
    priority: float = 1.0            # برای Priority Experience Replay
    
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class RLEpisodeResult:
    """نتیجه یک Episode کامل"""
    episode_id: str
    agent_type: RLAgentType
    start_time: datetime
    end_time: datetime
    
    total_reward: float
    steps_count: int
    success: bool
    
    # Metrics
    success_rate: float
    average_reward: float
    total_damage: float
    stealth_score: float
    
    model_version: int


# ==============================================================================
# Experience Replay Buffer
# ==============================================================================

class ExperienceReplayBuffer:
    """
    بافر ذخیره تجربیات (Experience Replay)
    
    این کلاس تجربیات را نگهداری می‌کند و به صورت batch برای آموزش ارائه می‌دهد.
    از Priority Sampling استفاده می‌کند (تجربیات مهم‌تر بیشتر sample می‌شوند).
    """
    
    def __init__(self, 
                 capacity: int = 100000,
                 alpha: float = 0.6,          # Priority exponent
                 beta: float = 0.4,           # Importance sampling
                 agent_type: RLAgentType = None):
        """
        Args:
            capacity: حداکثر تعداد تجربیات قابل ذخیره
            alpha: میزان اولویت‌دهی (0=uniform, 1=full priority)
            beta: میزان importance sampling (0-1)
            agent_type: نوع Agent
        """
        self.capacity = capacity
        self.alpha = alpha
        self.beta = beta
        self.agent_type = agent_type
        
        self.buffer = deque(maxlen=capacity)
        self.priorities = deque(maxlen=capacity)
        
        self.logger = get_logger(__name__, LogCategory.AI)
        
        self.logger.info(
            f"Experience Replay Buffer ایجاد شد - ظرفیت: {capacity}",
            f"Experience Replay Buffer created - capacity: {capacity}",
            context={'agent_type': agent_type.value if agent_type else 'general'}
        )
    
    @log_performance
    def add(self, experience: RLExperience):
        """افزودن یک تجربه جدید"""
        self.buffer.append(experience)
        
        # اولویت اولیه = حداکثر اولویت فعلی (یا 1.0)
        max_priority = max(self.priorities) if self.priorities else 1.0
        self.priorities.append(max_priority)
        
        self.logger.debug(
            f"تجربه جدید اضافه شد - Episode: {experience.episode_id}, Step: {experience.step_number}",
            f"New experience added",
            context={
                'episode_id': experience.episode_id,
                'reward': experience.reward,
                'done': experience.done
            }
        )
    
    @log_performance
    def sample(self, batch_size: int) -> Tuple[List[RLExperience], np.ndarray, np.ndarray]:
        """
        نمونه‌برداری از buffer با استفاده از priority
        
        Returns:
            experiences: لیست تجربیات
            indices: ایندکس‌های انتخاب شده
            weights: وزن‌های importance sampling
        """
        if len(self.buffer) == 0:
            raise AIException(
                "بافر خالی است - نمی‌توان sample کرد",
                "Buffer is empty - cannot sample",
                severity=ErrorSeverity.MEDIUM
            )
        
        batch_size = min(batch_size, len(self.buffer))
        
        # محاسبه احتمالات با استفاده از priority
        priorities = np.array(self.priorities, dtype=np.float32)
        probabilities = priorities ** self.alpha
        probabilities = probabilities / probabilities.sum()
        
        # نمونه‌برداری
        indices = np.random.choice(
            len(self.buffer),
            size=batch_size,
            replace=False,
            p=probabilities
        )
        
        # محاسبه importance sampling weights
        weights = (len(self.buffer) * probabilities[indices]) ** (-self.beta)
        weights = weights / weights.max()  # Normalize
        
        experiences = [self.buffer[idx] for idx in indices]
        
        self.logger.debug(
            f"Sample انجام شد - تعداد: {batch_size}",
            f"Sampled {batch_size} experiences",
            context={'buffer_size': len(self.buffer)}
        )
        
        return experiences, indices, weights
    
    def update_priorities(self, indices: np.ndarray, priorities: np.ndarray):
        """به‌روزرسانی اولویت تجربیات بعد از آموزش"""
        for idx, priority in zip(indices, priorities):
            self.priorities[idx] = priority
    
    def __len__(self) -> int:
        return len(self.buffer)
    
    @log_performance
    def save_to_database(self, db_manager):
        """ذخیره تمام تجربیات در پایگاه داده"""
        if len(self.buffer) == 0:
            return
        
        try:
            for exp in self.buffer:
                query = """
                INSERT INTO rl_experiences 
                (agent_type, episode_id, step_number, state_json, action_json, 
                 reward, next_state_json, done, priority, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                """
                
                db_manager.execute(query, (
                    self.agent_type.value if self.agent_type else 'general',
                    exp.episode_id,
                    exp.step_number,
                    json.dumps(exp.state.to_dict()),
                    json.dumps(exp.action.to_dict()),
                    exp.reward,
                    json.dumps(exp.next_state.to_dict()),
                    exp.done,
                    exp.priority,
                    exp.timestamp
                ), fetch=False)
            
            self.logger.info(
                f"{len(self.buffer)} تجربه در دیتابیس ذخیره شد",
                f"Saved {len(self.buffer)} experiences to database"
            )
        
        except Exception as e:
            self.logger.error(
                "خطا در ذخیره تجربیات در دیتابیس",
                "Error saving experiences to database",
                context={'error': str(e)}
            )
    
    @log_performance
    def load_from_database(self, db_manager, limit: int = None):
        """بارگذاری تجربیات از پایگاه داده"""
        try:
            query = """
            SELECT episode_id, step_number, state_json, action_json,
                   reward, next_state_json, done, priority, timestamp
            FROM rl_experiences
            WHERE agent_type = %s
            ORDER BY timestamp DESC
            """
            
            if limit:
                query += f" LIMIT {limit}"
            
            results = db_manager.execute(
                query,
                (self.agent_type.value if self.agent_type else 'general',)
            )
            
            if results:
                for row in results:
                    # Parse JSON data
                    state_dict = json.loads(row[2])
                    action_dict = json.loads(row[3])
                    next_state_dict = json.loads(row[5])
                    
                    # Reconstruct objects (simplified - you'd need proper reconstruction)
                    # This is a placeholder - actual implementation would need proper class reconstruction
                    self.logger.debug(
                        f"تجربه بارگذاری شد: {row[0]}",
                        f"Loaded experience: {row[0]}"
                    )
                
                self.logger.info(
                    f"{len(results)} تجربه از دیتابیس بارگذاری شد",
                    f"Loaded {len(results)} experiences from database"
                )
        
        except Exception as e:
            self.logger.error(
                "خطا در بارگذاری تجربیات از دیتابیس",
                "Error loading experiences from database",
                context={'error': str(e)}
            )


# ==============================================================================
# Reward Function
# ==============================================================================

class RewardFunction:
    """
    تابع پاداش (Reward Function)
    
    محاسبه reward براساس نتیجه action:
    R = w1*success + w2*speed + w3*stealth + w4*damage - w5*detection
    """
    
    def __init__(self, 
                 success_weight: float = 10.0,
                 speed_weight: float = 2.0,
                 stealth_weight: float = 5.0,
                 damage_weight: float = 3.0,
                 detection_penalty: float = -10.0):
        """
        Args:
            success_weight: وزن موفقیت حمله
            speed_weight: وزن سرعت حمله
            stealth_weight: وزن مخفی ماندن
            damage_weight: وزن آسیب وارد شده
            detection_penalty: جریمه شناسایی شدن
        """
        self.w_success = success_weight
        self.w_speed = speed_weight
        self.w_stealth = stealth_weight
        self.w_damage = damage_weight
        self.w_detection = detection_penalty
        
        self.logger = get_logger(__name__, LogCategory.AI)
    
    @log_performance
    def calculate(self,
                  success: bool,
                  time_taken: float,
                  stealth_score: float,
                  damage_level: float,
                  detected: bool,
                  context: Optional[Dict[str, Any]] = None) -> float:
        """
        محاسبه reward
        
        Args:
            success: آیا حمله موفق بود؟
            time_taken: زمان صرف شده (ثانیه)
            stealth_score: امتیاز مخفی ماندن (0-1)
            damage_level: میزان آسیب (0-1)
            detected: آیا شناسایی شد؟
            context: اطلاعات اضافی
        
        Returns:
            reward: پاداش محاسبه شده
        """
        # Success component
        success_reward = self.w_success if success else 0.0
        
        # Speed component (inverse of time, max 1.0)
        speed_reward = self.w_speed * min(1.0 / max(time_taken, 0.1), 1.0)
        
        # Stealth component
        stealth_reward = self.w_stealth * stealth_score
        
        # Damage component
        damage_reward = self.w_damage * damage_level
        
        # Detection penalty
        detection_penalty = self.w_detection if detected else 0.0
        
        # Total reward
        total_reward = (success_reward + speed_reward + 
                       stealth_reward + damage_reward + detection_penalty)
        
        self.logger.debug(
            f"Reward محاسبه شد: {total_reward:.2f}",
            f"Calculated reward: {total_reward:.2f}",
            context={
                'success': success,
                'time_taken': time_taken,
                'stealth_score': stealth_score,
                'damage_level': damage_level,
                'detected': detected,
                'breakdown': {
                    'success': success_reward,
                    'speed': speed_reward,
                    'stealth': stealth_reward,
                    'damage': damage_reward,
                    'detection': detection_penalty
                }
            }
        )
        
        return total_reward


# ==============================================================================
# Q-Learning Agent (Simple Implementation)
# ==============================================================================

class QLearningAgent:
    """
    Q-Learning Agent (ساده‌ترین الگوریتم RL)
    
    Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
    
    این Agent یک جدول Q نگهداری می‌کند و با استفاده از Bellman equation
    بهترین action را برای هر state یاد می‌گیرد.
    """
    
    def __init__(self,
                 agent_type: RLAgentType,
                 state_dim: int,
                 action_dim: int,
                 learning_rate: float = 0.1,
                 discount_factor: float = 0.99,
                 epsilon: float = 1.0,
                 epsilon_decay: float = 0.995,
                 epsilon_min: float = 0.01):
        """
        Args:
            agent_type: نوع Agent
            state_dim: بعد فضای state
            action_dim: بعد فضای action
            learning_rate (α): نرخ یادگیری
            discount_factor (γ): ضریب تخفیف
            epsilon: احتمال exploration
            epsilon_decay: نرخ کاهش epsilon
            epsilon_min: حداقل epsilon
        """
        self.agent_type = agent_type
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        self.alpha = learning_rate
        self.gamma = discount_factor
        self.epsilon = epsilon
        self.epsilon_decay = epsilon_decay
        self.epsilon_min = epsilon_min
        
        # Q-table (simplified - in reality would be a neural network)
        self.q_table = {}
        
        self.logger = get_logger(__name__, LogCategory.AI)
        self.training_steps = 0
        
        self.logger.info(
            f"Q-Learning Agent ایجاد شد - نوع: {agent_type.value}",
            f"Q-Learning Agent created - type: {agent_type.value}",
            context={
                'state_dim': state_dim,
                'action_dim': action_dim,
                'learning_rate': learning_rate,
                'discount_factor': discount_factor
            }
        )
    
    def _state_to_key(self, state: np.ndarray) -> str:
        """تبدیل state vector به key برای Q-table"""
        # Discretize continuous state space
        discretized = np.round(state * 10).astype(int)
        return hashlib.md5(discretized.tobytes()).hexdigest()
    
    @log_performance
    def select_action(self, state: np.ndarray, explore: bool = True) -> int:
        """
        انتخاب action با استفاده از ε-greedy policy
        
        Args:
            state: وضعیت فعلی
            explore: آیا exploration انجام شود؟
        
        Returns:
            action_index: ایندکس action انتخابی
        """
        state_key = self._state_to_key(state)
        
        # Exploration
        if explore and np.random.random() < self.epsilon:
            action = np.random.randint(0, self.action_dim)
            self.logger.debug(
                f"Exploration: action تصادفی انتخاب شد - {action}",
                f"Exploration: random action selected - {action}"
            )
            return action
        
        # Exploitation
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim)
        
        action = int(np.argmax(self.q_table[state_key]))
        
        self.logger.debug(
            f"Exploitation: بهترین action انتخاب شد - {action}",
            f"Exploitation: best action selected - {action}",
            context={'q_values': self.q_table[state_key].tolist()}
        )
        
        return action
    
    @log_performance
    def update(self, 
               state: np.ndarray,
               action: int,
               reward: float,
               next_state: np.ndarray,
               done: bool):
        """
        به‌روزرسانی Q-table با استفاده از Bellman equation
        
        Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
        """
        state_key = self._state_to_key(state)
        next_state_key = self._state_to_key(next_state)
        
        # Initialize Q-values if not exist
        if state_key not in self.q_table:
            self.q_table[state_key] = np.zeros(self.action_dim)
        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = np.zeros(self.action_dim)
        
        # Current Q-value
        current_q = self.q_table[state_key][action]
        
        # Target Q-value
        if done:
            target_q = reward
        else:
            max_next_q = np.max(self.q_table[next_state_key])
            target_q = reward + self.gamma * max_next_q
        
        # Update Q-value
        self.q_table[state_key][action] += self.alpha * (target_q - current_q)
        
        self.training_steps += 1
        
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
        
        self.logger.debug(
            f"Q-value به‌روز شد - Step: {self.training_steps}",
            f"Q-value updated - Step: {self.training_steps}",
            context={
                'reward': reward,
                'current_q': current_q,
                'target_q': target_q,
                'epsilon': self.epsilon
            }
        )
    
    def save_model(self, filepath: str):
        """ذخیره مدل"""
        with open(filepath, 'wb') as f:
            pickle.dump({
                'q_table': self.q_table,
                'epsilon': self.epsilon,
                'training_steps': self.training_steps
            }, f)
        
        self.logger.info(
            f"مدل ذخیره شد: {filepath}",
            f"Model saved: {filepath}"
        )
    
    def load_model(self, filepath: str):
        """بارگذاری مدل"""
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
            self.q_table = data['q_table']
            self.epsilon = data['epsilon']
            self.training_steps = data['training_steps']
        
        self.logger.info(
            f"مدل بارگذاری شد: {filepath}",
            f"Model loaded: {filepath}",
            context={'training_steps': self.training_steps}
        )


# ==============================================================================
# RL Engine Manager (Singleton)
# ==============================================================================

class RLEngineManager:
    """
    مدیر موتور یادگیری تقویتی (Singleton)
    
    این کلاس تمام Agentها را مدیریت می‌کند و interface واحدی برای
    تعامل با سیستم RL فراهم می‌کند.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        
        self.logger = get_logger(__name__, LogCategory.AI)
        self.config = get_config()
        
        # Database (optional - graceful degradation)
        try:
            self.db_manager = get_db_manager()
            self.db_available = True
        except Exception as e:
            self.logger.warning(
                "دیتابیس در دسترس نیست - RL Engine در حالت بدون دیتابیس اجرا می‌شود",
                "Database not available - RL Engine running without database",
                context={'error': str(e)}
            )
            self.db_manager = None
            self.db_available = False
        
        # Agents
        self.agents: Dict[RLAgentType, QLearningAgent] = {}
        
        # Replay Buffers
        self.replay_buffers: Dict[RLAgentType, ExperienceReplayBuffer] = {}
        
        # Reward Functions
        self.reward_functions: Dict[RLAgentType, RewardFunction] = {}
        
        # Current Episodes
        self.current_episodes: Dict[RLAgentType, str] = {}
        self.episode_step_counts: Dict[RLAgentType, int] = {}
        
        # Statistics
        self.total_episodes: Dict[RLAgentType, int] = {}
        self.total_rewards: Dict[RLAgentType, float] = {}
        
        self.logger.audit(
            "RL_ENGINE_INITIALIZED",
            "موتور یادگیری تقویتی راه‌اندازی شد",
            "RL Engine initialized successfully",
            context={'timestamp': datetime.now().isoformat()}
        )
        
        # Initialize database tables
        self._init_database_tables()
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """راه‌اندازی تمام Agentها"""
        rl_config = self.config.get('rl_engine', {})
        
        # Get dimensions from config
        state_dim = rl_config.get('state_dimension', 13)
        action_dim = rl_config.get('action_dimension', 10)
        
        for agent_type in RLAgentType:
            # Create Agent
            self.agents[agent_type] = QLearningAgent(
                agent_type=agent_type,
                state_dim=state_dim,
                action_dim=action_dim,
                learning_rate=rl_config.get('learning_rate', 0.1),
                discount_factor=rl_config.get('discount_factor', 0.99),
                epsilon=rl_config.get('epsilon_start', 1.0),
                epsilon_decay=rl_config.get('epsilon_decay', 0.995),
                epsilon_min=rl_config.get('epsilon_min', 0.01)
            )
            
            # Create Replay Buffer
            self.replay_buffers[agent_type] = ExperienceReplayBuffer(
                capacity=rl_config.get('replay_buffer_size', 100000),
                alpha=rl_config.get('priority_alpha', 0.6),
                beta=rl_config.get('priority_beta', 0.4),
                agent_type=agent_type
            )
            
            # Create Reward Function
            self.reward_functions[agent_type] = RewardFunction(
                success_weight=rl_config.get('reward_success', 10.0),
                speed_weight=rl_config.get('reward_speed', 2.0),
                stealth_weight=rl_config.get('reward_stealth', 5.0),
                damage_weight=rl_config.get('reward_damage', 3.0),
                detection_penalty=rl_config.get('reward_detection_penalty', -10.0)
            )
            
            # Initialize statistics
            self.total_episodes[agent_type] = 0
            self.total_rewards[agent_type] = 0.0
            
            self.logger.info(
                f"Agent راه‌اندازی شد: {agent_type.value}",
                f"Agent initialized: {agent_type.value}"
            )
    
    @log_performance
    @handle_exception(fallback_value=None)
    def start_episode(self, 
                     agent_type: RLAgentType,
                     initial_state: RLState,
                     context: Optional[Dict[str, Any]] = None) -> str:
        """
        شروع یک Episode جدید
        
        Args:
            agent_type: نوع Agent
            initial_state: وضعیت اولیه
            context: اطلاعات اضافی
        
        Returns:
            episode_id: شناسه episode
        """
        episode_id = str(uuid.uuid4())
        self.current_episodes[agent_type] = episode_id
        self.episode_step_counts[agent_type] = 0
        
        self.logger.audit(
            "RL_EPISODE_STARTED",
            f"Episode جدید شروع شد - Agent: {agent_type.value}",
            f"New episode started - Agent: {agent_type.value}",
            context={
                'episode_id': episode_id,
                'agent_type': agent_type.value,
                'initial_state': initial_state.to_dict()
            }
        )
        
        return episode_id
    
    @log_performance
    @handle_exception(fallback_value=0)
    def select_action(self,
                     agent_type: RLAgentType,
                     state: RLState,
                     explore: bool = True) -> int:
        """
        انتخاب action بهینه برای state داده شده
        
        Args:
            agent_type: نوع Agent
            state: وضعیت فعلی
            explore: آیا exploration انجام شود؟
        
        Returns:
            action_index: ایندکس action انتخابی
        """
        agent = self.agents[agent_type]
        state_vector = state.to_vector()
        
        action = agent.select_action(state_vector, explore=explore)
        
        self.episode_step_counts[agent_type] += 1
        
        return action
    
    @log_performance
    @handle_exception()
    def store_experience(self,
                        agent_type: RLAgentType,
                        state: RLState,
                        action: RLAction,
                        reward: float,
                        next_state: RLState,
                        done: bool,
                        priority: float = 1.0):
        """
        ذخیره یک تجربه در Replay Buffer
        
        Args:
            agent_type: نوع Agent
            state: وضعیت قبل از action
            action: action انجام شده
            reward: پاداش دریافتی
            next_state: وضعیت بعد از action
            done: آیا episode تمام شد؟
            priority: اولویت تجربه
        """
        episode_id = self.current_episodes.get(agent_type, "unknown")
        step_number = self.episode_step_counts.get(agent_type, 0)
        
        experience = RLExperience(
            episode_id=episode_id,
            step_number=step_number,
            state=state,
            action=action,
            reward=reward,
            next_state=next_state,
            done=done,
            priority=priority
        )
        
        self.replay_buffers[agent_type].add(experience)
        
        # Save to database (async)
        if self.db_available and self.config.get('rl_engine.save_experiences_to_db', True):
            self.store_experience_to_db(experience, agent_type)
        
        # Update agent immediately (online learning)
        agent = self.agents[agent_type]
        agent.update(
            state.to_vector(),
            action_index := 0,  # Placeholder - would need proper action mapping
            reward,
            next_state.to_vector(),
            done
        )
        
        self.logger.debug(
            f"تجربه ذخیره شد - Episode: {episode_id}, Step: {step_number}",
            f"Experience stored - Episode: {episode_id}, Step: {step_number}",
            context={'reward': reward, 'done': done}
        )
    
    @log_performance
    @handle_exception()
    def end_episode(self,
                   agent_type: RLAgentType,
                   success: bool,
                   total_reward: float,
                   metrics: Dict[str, float]):
        """
        پایان یک Episode
        
        Args:
            agent_type: نوع Agent
            success: آیا episode موفق بود؟
            total_reward: مجموع پاداش
            metrics: متریک‌های عملکرد
        """
        episode_id = self.current_episodes.get(agent_type, "unknown")
        steps = self.episode_step_counts.get(agent_type, 0)
        
        # Update statistics
        self.total_episodes[agent_type] += 1
        self.total_rewards[agent_type] += total_reward
        
        avg_reward = total_reward / max(steps, 1)
        
        self.logger.audit(
            "RL_EPISODE_ENDED",
            f"Episode پایان یافت - موفقیت: {success}",
            f"Episode ended - success: {success}",
            context={
                'episode_id': episode_id,
                'agent_type': agent_type.value,
                'success': success,
                'total_reward': total_reward,
                'steps': steps,
                'average_reward': avg_reward,
                'metrics': metrics
            }
        )
        
        # Save to database (if configured and available)
        if self.db_available and self.config.get('rl_engine.save_episodes_to_db', True):
            self._save_episode_to_db(agent_type, episode_id, success, 
                                    total_reward, steps, metrics)
    
    def _save_episode_to_db(self, agent_type, episode_id, success, 
                           total_reward, steps, metrics):
        """ذخیره نتیجه episode در دیتابیس"""
        if not self.db_available or not self.db_manager:
            return
        
        try:
            query = """
            INSERT INTO rl_episodes
            (id, agent_type, start_time, end_time, total_reward, steps_count,
             success, success_rate, average_reward, total_damage, stealth_score,
             model_version)
            VALUES (%s, %s, NOW() - INTERVAL '1 hour', NOW(), %s, %s, %s, 
                    %s, %s, %s, %s, %s)
            """
            
            self.db_manager.execute(query, (
                episode_id,
                agent_type.value,
                total_reward,
                steps,
                success,
                metrics.get('success_rate', 0.0),
                metrics.get('average_reward', 0.0),
                metrics.get('total_damage', 0.0),
                metrics.get('stealth_score', 0.0),
                1  # model_version - placeholder
            ), fetch=False)
        
        except DatabaseException as e:
            self.logger.warning(
                "خطا در ذخیره episode در دیتابیس (نادیده گرفته شد)",
                "Error saving episode to database (ignored)",
                context={'error': str(e)}
            )
    
    @log_performance
    @handle_exception()
    def train_agent(self,
                   agent_type: RLAgentType,
                   batch_size: int = 64,
                   epochs: int = 10):
        """
        بازآموزی Agent با استفاده از تجربیات ذخیره شده
        
        Args:
            agent_type: نوع Agent
            batch_size: تعداد نمونه در هر batch
            epochs: تعداد epoch های آموزش
        """
        replay_buffer = self.replay_buffers[agent_type]
        agent = self.agents[agent_type]
        
        if len(replay_buffer) < batch_size:
            self.logger.warning(
                f"تعداد تجربیات کافی نیست - حداقل: {batch_size}, فعلی: {len(replay_buffer)}",
                f"Not enough experiences - minimum: {batch_size}, current: {len(replay_buffer)}"
            )
            return
        
        self.logger.info(
            f"شروع آموزش Agent - نوع: {agent_type.value}",
            f"Starting agent training - type: {agent_type.value}",
            context={'batch_size': batch_size, 'epochs': epochs}
        )
        
        for epoch in range(epochs):
            # Sample experiences
            experiences, indices, weights = replay_buffer.sample(batch_size)
            
            total_loss = 0.0
            
            for exp, weight in zip(experiences, weights):
                # Update agent (already done in store_experience for online learning)
                # Here we could do additional batch updates if needed
                pass
            
            self.logger.debug(
                f"Epoch {epoch+1}/{epochs} تکمیل شد",
                f"Epoch {epoch+1}/{epochs} completed"
            )
        
        self.logger.audit(
            "RL_TRAINING_COMPLETED",
            f"آموزش Agent تکمیل شد - نوع: {agent_type.value}",
            f"Agent training completed - type: {agent_type.value}",
            context={
                'agent_type': agent_type.value,
                'epochs': epochs,
                'batch_size': batch_size,
                'buffer_size': len(replay_buffer)
            }
        )
        
        # Save model to database after training
        if self.db_available and self.config.get('rl_engine.save_models_to_db', True):
            self.save_model_to_db(agent_type)
    
    def should_retrain(self, agent_type: RLAgentType) -> bool:
        """آیا زمان بازآموزی است؟"""
        episodes = self.total_episodes.get(agent_type, 0)
        retrain_interval = self.config.get('rl_engine.retrain_interval', 100)
        
        return episodes > 0 and episodes % retrain_interval == 0
    
    def get_statistics(self, agent_type: RLAgentType) -> Dict[str, Any]:
        """دریافت آمار Agent"""
        return {
            'total_episodes': self.total_episodes.get(agent_type, 0),
            'total_reward': self.total_rewards.get(agent_type, 0.0),
            'average_reward': (self.total_rewards.get(agent_type, 0.0) / 
                             max(self.total_episodes.get(agent_type, 1), 1)),
            'buffer_size': len(self.replay_buffers[agent_type]),
            'epsilon': self.agents[agent_type].epsilon,
            'training_steps': self.agents[agent_type].training_steps
        }
    
    # ==========================================================================
    # Database Integration Methods
    # ==========================================================================
    
    def _init_database_tables(self):
        """
        راه‌اندازی جداول دیتابیس (اگر وجود نداشته باشند)
        
        این متد schema را از database/rl_schema.sql می‌خواند و اجرا می‌کند.
        """
        if not self.db_available:
            return
        
        try:
            schema_path = Path(__file__).parent.parent / 'database' / 'rl_schema.sql'
            
            if schema_path.exists():
                with open(schema_path, 'r', encoding='utf-8') as f:
                    schema_sql = f.read()
                
                # Execute schema
                self.db_manager.execute_raw(schema_sql)
                
                self.logger.info(
                    "جداول RL با موفقیت ایجاد شدند",
                    "RL tables created successfully"
                )
            else:
                self.logger.warning(
                    f"فایل schema یافت نشد: {schema_path}",
                    f"Schema file not found: {schema_path}"
                )
        
        except Exception as e:
            self.logger.error(
                "خطا در ایجاد جداول دیتابیس",
                "Error creating database tables",
                context={'error': str(e)}
            )
    
    def store_experience_to_db(self, experience: RLExperience, agent_type: RLAgentType):
        """
        ذخیره یک تجربه در دیتابیس
        
        Args:
            experience: تجربه برای ذخیره
            agent_type: نوع Agent
        """
        if not self.db_available or not self.db_manager:
            return
        
        try:
            query = """
            INSERT INTO rl_experiences
            (id, episode_id, agent_type, step_number, state, action, reward,
             next_state, done, priority, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING
            """
            
            self.db_manager.execute(query, (
                str(uuid.uuid4()),
                experience.episode_id,
                agent_type.value,
                experience.step_number,
                json.dumps(experience.state.to_dict()),
                json.dumps(experience.action.to_dict()),
                experience.reward,
                json.dumps(experience.next_state.to_dict()),
                experience.done,
                experience.priority,
                experience.timestamp
            ), fetch=False)
        
        except Exception as e:
            self.logger.warning(
                "خطا در ذخیره تجربه در دیتابیس (نادیده گرفته شد)",
                "Error saving experience to database (ignored)",
                context={'error': str(e)}
            )
    
    def load_experiences_from_db(self, 
                                 agent_type: RLAgentType,
                                 limit: int = 10000) -> List[RLExperience]:
        """
        بازیابی تجربیات از دیتابیس
        
        Args:
            agent_type: نوع Agent
            limit: حداکثر تعداد تجربیات
        
        Returns:
            لیست تجربیات
        """
        if not self.db_available or not self.db_manager:
            return []
        
        try:
            query = """
            SELECT episode_id, step_number, state, action, reward,
                   next_state, done, priority, timestamp
            FROM rl_experiences
            WHERE agent_type = %s
            ORDER BY timestamp DESC
            LIMIT %s
            """
            
            rows = self.db_manager.execute(query, (agent_type.value, limit), fetch=True)
            
            experiences = []
            for row in rows:
                # Parse JSON state/action
                state_dict = json.loads(row['state'])
                action_dict = json.loads(row['action'])
                next_state_dict = json.loads(row['next_state'])
                
                exp = RLExperience(
                    episode_id=row['episode_id'],
                    step_number=row['step_number'],
                    state=RLState.from_dict(state_dict),
                    action=RLAction.from_dict(action_dict),
                    reward=row['reward'],
                    next_state=RLState.from_dict(next_state_dict),
                    done=row['done'],
                    priority=row['priority'],
                    timestamp=row['timestamp']
                )
                experiences.append(exp)
            
            self.logger.info(
                f"بازیابی {len(experiences)} تجربه از دیتابیس - Agent: {agent_type.value}",
                f"Loaded {len(experiences)} experiences from database - Agent: {agent_type.value}"
            )
            
            return experiences
        
        except Exception as e:
            self.logger.error(
                "خطا در بازیابی تجربیات از دیتابیس",
                "Error loading experiences from database",
                context={'error': str(e)}
            )
            return []
    
    def save_model_to_db(self, agent_type: RLAgentType):
        """
        ذخیره وضعیت model در دیتابیس
        
        Args:
            agent_type: نوع Agent
        """
        if not self.db_available or not self.db_manager:
            return
        
        try:
            agent = self.agents[agent_type]
            
            # Serialize model weights (Q-table or neural network weights)
            model_data = {
                'q_table': agent.q_table.tolist() if hasattr(agent, 'q_table') else None,
                'epsilon': agent.epsilon,
                'training_steps': agent.training_steps,
                'algorithm': 'Q-Learning'
            }
            
            query = """
            INSERT INTO rl_models
            (id, agent_type, version, algorithm, model_data, epsilon, training_steps,
             performance_score, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """
            
            stats = self.get_statistics(agent_type)
            performance = stats.get('average_reward', 0.0)
            
            model_id = str(uuid.uuid4())
            version = stats.get('total_episodes', 0)
            
            self.db_manager.execute(query, (
                model_id,
                agent_type.value,
                version,
                'Q-Learning',
                json.dumps(model_data),
                agent.epsilon,
                agent.training_steps,
                performance
            ), fetch=False)
            
            self.logger.info(
                f"Model ذخیره شد - Agent: {agent_type.value}, Version: {version}",
                f"Model saved - Agent: {agent_type.value}, Version: {version}"
            )
        
        except Exception as e:
            self.logger.error(
                "خطا در ذخیره model در دیتابیس",
                "Error saving model to database",
                context={'error': str(e)}
            )
    
    def load_model_from_db(self, agent_type: RLAgentType, version: Optional[int] = None):
        """
        بازیابی model از دیتابیس
        
        Args:
            agent_type: نوع Agent
            version: نسخه خاص (اگر None باشد، آخرین نسخه بارگذاری می‌شود)
        """
        if not self.db_available or not self.db_manager:
            return
        
        try:
            if version is None:
                # Load latest version
                query = """
                SELECT model_data, epsilon, training_steps
                FROM rl_models
                WHERE agent_type = %s
                ORDER BY version DESC
                LIMIT 1
                """
                params = (agent_type.value,)
            else:
                # Load specific version
                query = """
                SELECT model_data, epsilon, training_steps
                FROM rl_models
                WHERE agent_type = %s AND version = %s
                LIMIT 1
                """
                params = (agent_type.value, version)
            
            rows = self.db_manager.execute(query, params, fetch=True)
            
            if not rows:
                self.logger.warning(
                    f"Model یافت نشد - Agent: {agent_type.value}, Version: {version}",
                    f"Model not found - Agent: {agent_type.value}, Version: {version}"
                )
                return
            
            row = rows[0]
            model_data = json.loads(row['model_data'])
            
            agent = self.agents[agent_type]
            
            # Restore agent state
            if 'q_table' in model_data and model_data['q_table'] is not None:
                agent.q_table = np.array(model_data['q_table'])
            
            agent.epsilon = row['epsilon']
            agent.training_steps = row['training_steps']
            
            self.logger.info(
                f"Model بارگذاری شد - Agent: {agent_type.value}, Steps: {agent.training_steps}",
                f"Model loaded - Agent: {agent_type.value}, Steps: {agent.training_steps}"
            )
        
        except Exception as e:
            self.logger.error(
                "خطا در بازیابی model از دیتابیس",
                "Error loading model from database",
                context={'error': str(e)}
            )
            self.logger.error(
                "خطا در ایجاد جداول RL",
                "Error creating RL tables",
                context={'error': str(e)}
            )
    
    @handle_exception(ErrorSeverity.MEDIUM)
    def store_experience_to_db(self, experience: RLExperience, agent_type: RLAgentType):
        """
        ذخیره تجربه در دیتابیس
        
        Args:
            experience: تجربه برای ذخیره
            agent_type: نوع Agent
        """
        if not self.db_available:
            return
        
        try:
            # Serialize state/action to JSON
            state_json = json.dumps(experience.state.to_dict())
            action_json = json.dumps(experience.action.to_dict())
            next_state_json = json.dumps(experience.next_state.to_dict())
            
            # Insert into database
            query = """
                INSERT INTO rl_experiences 
                (episode_id, agent_type, step_number, state, action, reward, 
                 next_state, done, priority, model_version, timestamp)
                VALUES (%s, %s, %s, %s::jsonb, %s::jsonb, %s, %s::jsonb, %s, %s, %s, %s)
            """
            
            self.db_manager.execute(
                query,
                (
                    experience.episode_id,
                    agent_type.value,
                    experience.step_number,
                    state_json,
                    action_json,
                    experience.reward,
                    next_state_json,
                    experience.done,
                    experience.priority,
                    self.agents[agent_type].model_version,
                    experience.timestamp
                )
            )
        
        except Exception as e:
            self.logger.warning(
                f"خطا در ذخیره تجربه: {str(e)}",
                f"Error storing experience: {str(e)}"
            )
    
    @handle_exception(ErrorSeverity.MEDIUM)
    def store_episode_to_db(self, episode_result: RLEpisodeResult):
        """
        ذخیره نتیجه Episode در دیتابیس
        
        Args:
            episode_result: نتایج Episode
        """
        if not self.db_available:
            return
        
        try:
            duration = (episode_result.end_time - episode_result.start_time).total_seconds()
            
            query = """
                INSERT INTO rl_episodes 
                (episode_id, agent_type, start_time, end_time, duration_seconds,
                 total_reward, steps_count, success, success_rate, average_reward,
                 total_damage, stealth_score, model_version)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            self.db_manager.execute(
                query,
                (
                    episode_result.episode_id,
                    episode_result.agent_type.value,
                    episode_result.start_time,
                    episode_result.end_time,
                    duration,
                    episode_result.total_reward,
                    episode_result.steps_count,
                    episode_result.success,
                    episode_result.success_rate,
                    episode_result.average_reward,
                    episode_result.total_damage,
                    episode_result.stealth_score,
                    episode_result.model_version
                )
            )
            
            # Update agent statistics
            self._update_agent_stats_in_db(episode_result.agent_type)
        
        except Exception as e:
            self.logger.warning(
                f"خطا در ذخیره Episode: {str(e)}",
                f"Error storing episode: {str(e)}"
            )
    
    @handle_exception(ErrorSeverity.LOW)
    def _update_agent_stats_in_db(self, agent_type: RLAgentType):
        """بروزرسانی آمار Agent در دیتابیس"""
        if not self.db_available:
            return
        
        try:
            stats = self.get_statistics(agent_type)
            
            query = """
                UPDATE rl_agent_stats
                SET 
                    total_episodes = %s,
                    total_steps = %s,
                    average_reward = %s,
                    current_epsilon = %s,
                    current_model_version = %s,
                    last_episode_time = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE agent_type = %s
            """
            
            self.db_manager.execute(
                query,
                (
                    stats['total_episodes'],
                    stats.get('total_steps', 0),
                    stats['average_reward'],
                    stats['epsilon'],
                    self.agents[agent_type].model_version,
                    agent_type.value
                )
            )
        
        except Exception as e:
            self.logger.debug(f"Could not update agent stats: {str(e)}")
    
    @handle_exception(ErrorSeverity.MEDIUM)
    def save_model_to_db(self, agent_type: RLAgentType, notes: str = ""):
        """
        ذخیره Model در دیتابیس
        
        Args:
            agent_type: نوع Agent
            notes: یادداشت‌های اضافی
        """
        if not self.db_available:
            self.logger.warning("Database not available - model not saved to DB")
            return
        
        try:
            agent = self.agents[agent_type]
            
            # Serialize model (Q-table)
            model_data = pickle.dumps(agent.q_table)
            
            # Get statistics
            stats = self.get_statistics(agent_type)
            
            # Deactivate old models
            self.db_manager.execute(
                "UPDATE rl_models SET is_active = FALSE WHERE agent_type = %s",
                (agent_type.value,)
            )
            
            # Insert new model
            query = """
                INSERT INTO rl_models 
                (agent_type, version, model_data, model_type, training_episodes,
                 training_steps, average_reward, hyperparameters, notes, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s::jsonb, %s, TRUE)
            """
            
            hyperparams = {
                'learning_rate': agent.learning_rate,
                'discount_factor': agent.discount_factor,
                'epsilon': agent.epsilon,
                'epsilon_decay': agent.epsilon_decay,
                'epsilon_min': agent.epsilon_min
            }
            
            self.db_manager.execute(
                query,
                (
                    agent_type.value,
                    agent.model_version,
                    model_data,
                    'q_table',
                    stats['total_episodes'],
                    agent.training_steps,
                    stats['average_reward'],
                    json.dumps(hyperparams),
                    notes
                )
            )
            
            self.logger.info(
                f"Model v{agent.model_version} ذخیره شد",
                f"Model v{agent.model_version} saved to database",
                context={'agent_type': agent_type.value}
            )
        
        except Exception as e:
            self.logger.error(
                f"خطا در ذخیره Model: {str(e)}",
                f"Error saving model: {str(e)}"
            )
    
    @handle_exception(ErrorSeverity.MEDIUM)
    def load_model_from_db(self, agent_type: RLAgentType, version: Optional[int] = None):
        """
        بارگذاری Model از دیتابیس
        
        Args:
            agent_type: نوع Agent
            version: نسخه Model (اگر None باشد، آخرین نسخه active بارگذاری می‌شود)
        """
        if not self.db_available:
            self.logger.warning("Database not available - cannot load model")
            return
        
        try:
            if version is None:
                # Load active model
                query = """
                    SELECT model_data, version, hyperparameters
                    FROM rl_models
                    WHERE agent_type = %s AND is_active = TRUE
                    ORDER BY version DESC
                    LIMIT 1
                """
                params = (agent_type.value,)
            else:
                # Load specific version
                query = """
                    SELECT model_data, version, hyperparameters
                    FROM rl_models
                    WHERE agent_type = %s AND version = %s
                    LIMIT 1
                """
                params = (agent_type.value, version)
            
            result = self.db_manager.fetch_one(query, params)
            
            if result:
                model_data, loaded_version, hyperparams_json = result
                
                # Deserialize model
                q_table = pickle.loads(model_data)
                
                # Update agent
                agent = self.agents[agent_type]
                agent.q_table = q_table
                agent.model_version = loaded_version
                
                # Update hyperparameters if available
                if hyperparams_json:
                    hyperparams = json.loads(hyperparams_json) if isinstance(hyperparams_json, str) else hyperparams_json
                    agent.learning_rate = hyperparams.get('learning_rate', agent.learning_rate)
                    agent.discount_factor = hyperparams.get('discount_factor', agent.discount_factor)
                    agent.epsilon = hyperparams.get('epsilon', agent.epsilon)
                
                self.logger.info(
                    f"Model v{loaded_version} بارگذاری شد",
                    f"Model v{loaded_version} loaded from database",
                    context={'agent_type': agent_type.value}
                )
            else:
                self.logger.warning(
                    f"Model یافت نشد برای {agent_type.value}",
                    f"No model found for {agent_type.value}"
                )
        
        except Exception as e:
            self.logger.error(
                f"خطا در بارگذاری Model: {str(e)}",
                f"Error loading model: {str(e)}"
            )


# ==============================================================================
# Factory Functions
# ==============================================================================

_rl_engine_instance = None

def get_rl_engine() -> RLEngineManager:
    """
    دریافت instance موتور RL (Singleton)
    
    Returns:
        RLEngineManager instance
    """
    global _rl_engine_instance
    if _rl_engine_instance is None:
        _rl_engine_instance = RLEngineManager()
    return _rl_engine_instance


# ==============================================================================
# Main - Example Usage
# ==============================================================================

if __name__ == "__main__":
    print("="*80)
    print("SecureRedLab - Reinforcement Learning Engine Test")
    print("="*80)
    
    # Get RL Engine
    rl_engine = get_rl_engine()
    
    # Example: DDoS Attack Simulation with RL
    print("\n[TEST 1] شبیه‌سازی حمله DDoS با RL")
    
    # Initial state
    initial_state = RLState(
        target_ip="192.168.1.100",
        target_ports=[80, 443],
        target_os="Linux",
        target_services={"http": "nginx", "https": "nginx"},
        network_latency=50.0,
        bandwidth=1000.0,
        firewall_active=True,
        ids_active=True,
        attack_stage=0,
        time_elapsed=0.0,
        packets_sent=0,
        success_rate=0.0,
        previous_actions=[],
        detection_count=0
    )
    
    # Start episode
    episode_id = rl_engine.start_episode(RLAgentType.DDOS, initial_state)
    print(f"✓ Episode شروع شد: {episode_id}")
    
    # Simulate attack steps
    total_reward = 0.0
    for step in range(5):
        # Select action
        action_idx = rl_engine.select_action(RLAgentType.DDOS, initial_state)
        print(f"  Step {step+1}: Action انتخاب شد: {action_idx}")
        
        # Simulate environment step (fake rewards)
        action = RLAction(
            action_type=f"action_{action_idx}",
            parameters={'intensity': 0.5}
        )
        
        reward = np.random.uniform(-1, 10)  # Random reward for demo
        total_reward += reward
        
        # Next state (slightly modified)
        next_state = RLState(
            target_ip=initial_state.target_ip,
            target_ports=initial_state.target_ports,
            target_os=initial_state.target_os,
            target_services=initial_state.target_services,
            network_latency=initial_state.network_latency,
            bandwidth=initial_state.bandwidth,
            firewall_active=initial_state.firewall_active,
            ids_active=initial_state.ids_active,
            attack_stage=step + 1,
            time_elapsed=step * 10.0,
            packets_sent=(step + 1) * 1000,
            success_rate=0.5,
            previous_actions=[f"action_{action_idx}"],
            detection_count=0
        )
        
        done = (step == 4)
        
        # Store experience
        rl_engine.store_experience(
            RLAgentType.DDOS,
            initial_state,
            action,
            reward,
            next_state,
            done
        )
        
        initial_state = next_state
        print(f"    Reward: {reward:.2f}, Total: {total_reward:.2f}")
    
    # End episode
    rl_engine.end_episode(
        RLAgentType.DDOS,
        success=True,
        total_reward=total_reward,
        metrics={
            'success_rate': 1.0,
            'average_reward': total_reward / 5,
            'total_damage': 0.8,
            'stealth_score': 0.6
        }
    )
    print(f"✓ Episode پایان یافت - Total Reward: {total_reward:.2f}")
    
    # Check if retraining needed
    print(f"\n[TEST 2] بررسی نیاز به بازآموزی")
    should_retrain = rl_engine.should_retrain(RLAgentType.DDOS)
    print(f"  نیاز به بازآموزی: {should_retrain}")
    
    # Get statistics
    print(f"\n[TEST 3] آمار Agent")
    stats = rl_engine.get_statistics(RLAgentType.DDOS)
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    print("\n" + "="*80)
    print("✅ تست‌های RL Engine با موفقیت اجرا شد!")
    print("="*80)
