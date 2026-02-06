# راهنمای جامع موتور یادگیری تقویتی (RL Engine)
# Comprehensive Guide to Reinforcement Learning Engine

**SecureRedLab - Academic Research Platform**  
**نسخه:** 1.0.0  
**تاریخ:** 2025-01-15  

---

## 📋 فهرست مطالب

1. [معرفی](#معرفی)
2. [معماری کلی](#معماری-کلی)
3. [مفاهیم پایه RL](#مفاهیم-پایه-rl)
4. [نحوه استفاده](#نحوه-استفاده)
5. [پیکربندی](#پیکربندی)
6. [پایگاه داده](#پایگاه-داده)
7. [الگوریتم‌ها](#الگوریتمها)
8. [بهینه‌سازی](#بهینهسازی)
9. [مثال‌های کاربردی](#مثالهای-کاربردی)
10. [عیب‌یابی](#عیبیابی)

---

## 🎯 معرفی

موتور یادگیری تقویتی (RL Engine) **قلب** سیستم SecureRedLab است که به پلتفرم اجازه می‌دهد:

- 📈 **یادگیری از تجربه**: پس از هر تست، از نتایج یاد بگیرد
- 🎯 **بهبود خودکار**: کیفیت حملات را به صورت خودکار افزایش دهد
- 🧠 **تصمیم‌گیری هوشمند**: بهترین استراتژی را برای هر هدف انتخاب کند
- 💾 **ذخیره تجربیات**: تمام تجربیات را در پایگاه داده نگهداری کند
- 🔄 **بازآموزی مداوم**: مدل‌ها را به صورت دوره‌ای بازآموزی دهد

### ویژگی‌های کلیدی

✅ **5 Agent مستقل**: DDoS, Shell Upload, Data Extraction, Deface, Behavior Simulation  
✅ **4 الگوریتم RL**: Q-Learning, Deep Q-Network (DQN), Policy Gradient, PPO  
✅ **Experience Replay Buffer**: با Priority Sampling برای یادگیری بهتر  
✅ **پایگاه داده بازآموزی**: ذخیره و بارگذاری تجربیات از PostgreSQL  
✅ **Reward Shaping**: تابع پاداش پیشرفته با وزن‌های قابل تنظیم  
✅ **Model Versioning**: نسخه‌بندی مدل‌ها و A/B Testing  
✅ **Multi-threaded Training**: آموزش سریع با استفاده از چند thread  

---

## 🏗️ معماری کلی

```
┌─────────────────────────────────────────────────────────────┐
│  SecureRedLab Reinforcement Learning Engine                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  RLEngineManager (Singleton)                        │   │
│  │  - مدیریت تمام Agentها                             │   │
│  │  - مدیریت Replay Buffers                            │   │
│  │  - مدیریت بازآموزی                                  │   │
│  └───────────┬─────────────────────────────────────────┘   │
│              │                                              │
│              ▼                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  5 Independent RL Agents                            │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐       │   │
│  │  │  DDoS     │  │  Shell    │  │  Extract  │       │   │
│  │  │  Agent    │  │  Agent    │  │  Agent    │       │   │
│  │  └───────────┘  └───────────┘  └───────────┘       │   │
│  │  ┌───────────┐  ┌───────────┐                      │   │
│  │  │  Deface   │  │  Behavior │                      │   │
│  │  │  Agent    │  │  Agent    │                      │   │
│  │  └───────────┘  └───────────┘                      │   │
│  └───────────┬─────────────────────────────────────────┘   │
│              │                                              │
│              ▼                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  Experience Replay Buffers (100K capacity each)     │   │
│  │  - Priority Experience Replay                       │   │
│  │  - Importance Sampling                              │   │
│  │  - Save/Load from Database                          │   │
│  └───────────┬─────────────────────────────────────────┘   │
│              │                                              │
│              ▼                                              │
│  ┌─────────────────────────────────────────────────────┐   │
│  │  PostgreSQL Database                                │   │
│  │  - rl_experiences (تجربیات)                         │   │
│  │  - rl_episodes (نتایج Episode)                      │   │
│  │  - rl_models (مدل‌های آموزش‌دیده)                   │   │
│  │  - rl_agent_stats (آمار)                            │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 مفاهیم پایه RL

### 1. State (وضعیت)

State تمام اطلاعات لازم برای تصمیم‌گیری را شامل می‌شود:

```python
state = RLState(
    target_ip="192.168.1.100",      # IP هدف
    target_ports=[80, 443],          # پورت‌های باز
    target_os="Linux",               # سیستم‌عامل
    target_services={...},           # سرویس‌های در حال اجرا
    network_latency=50.0,            # تأخیر شبکه
    bandwidth=1000.0,                # پهنای باند
    firewall_active=True,            # آیا فایروال فعال است؟
    ids_active=True,                 # آیا IDS فعال است؟
    attack_stage=0,                  # مرحله فعلی حمله
    time_elapsed=0.0,                # زمان سپری شده
    packets_sent=0,                  # تعداد پکت ارسالی
    success_rate=0.0,                # نرخ موفقیت فعلی
    previous_actions=[],             # اقدامات قبلی
    detection_count=0                # دفعات شناسایی
)
```

State به صورت خودکار به یک بردار 13 بعدی تبدیل می‌شود:

```python
state_vector = state.to_vector()
# Output: [0.02, 0.5, 0.06, 0.05, 0.1, 1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
```

### 2. Action (عمل)

Action تصمیمی است که Agent می‌گیرد:

```python
action = RLAction(
    action_type="increase_bot_power",  # نوع عمل
    parameters={                       # پارامترهای عمل
        'intensity': 0.8,
        'target_port': 80,
        'packet_size': 1500
    }
)
```

انواع Action برای هر Agent متفاوت است:

**DDoS Agent:**
- `increase_bot_power`: افزایش قدرت botها
- `decrease_bot_power`: کاهش قدرت botها
- `change_attack_vector`: تغییر بردار حمله
- `add_bots`: افزودن bot جدید
- `wait`: صبر کردن

**Shell Agent:**
- `upload_shell`: آپلود shell
- `exploit_vulnerability`: استفاده از آسیب‌پذیری
- `escalate_privileges`: افزایش سطح دسترسی
- `establish_persistence`: ایجاد پایداری

### 3. Reward (پاداش)

Reward نشان‌دهنده موفقیت یا شکست action است:

```python
R = w1*success + w2*speed + w3*stealth + w4*damage - w5*detection

# مثال:
R = 10.0*(1) + 2.0*(0.8) + 5.0*(0.9) + 3.0*(0.7) - 10.0*(0) = 19.2
```

**مؤلفه‌های Reward:**

| مؤلفه | وزن پیش‌فرض | توضیح |
|------|-------------|--------|
| `success` | 10.0 | آیا حمله موفق بود؟ (0 یا 1) |
| `speed` | 2.0 | سرعت حمله (0-1) |
| `stealth` | 5.0 | میزان مخفی ماندن (0-1) |
| `damage` | 3.0 | میزان آسیب وارد شده (0-1) |
| `detection` | -10.0 | جریمه شناسایی شدن |

### 4. Episode (دوره)

Episode یک دنباله کامل از تعاملات است:

```
Episode = (s₀, a₀, r₀) → (s₁, a₁, r₁) → ... → (sₙ, aₙ, rₙ) → Terminal State
```

مثال:
```python
episode_id = rl_engine.start_episode(RLAgentType.DDOS, initial_state)

for step in range(max_steps):
    action = rl_engine.select_action(RLAgentType.DDOS, current_state)
    next_state, reward, done = environment.step(action)
    rl_engine.store_experience(RLAgentType.DDOS, current_state, action, 
                               reward, next_state, done)
    
    if done:
        break
    
    current_state = next_state

rl_engine.end_episode(RLAgentType.DDOS, success=True, total_reward=27.5, metrics={...})
```

---

## 🚀 نحوه استفاده

### راه‌اندازی اولیه

```python
from core.rl_engine import get_rl_engine, RLAgentType, RLState, RLAction

# دریافت instance موتور RL
rl_engine = get_rl_engine()
```

### سناریوی کامل: حمله DDoS

```python
# 1. تعریف وضعیت اولیه
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

# 2. شروع Episode
episode_id = rl_engine.start_episode(
    agent_type=RLAgentType.DDOS,
    initial_state=initial_state,
    context={'researcher_id': 'RES-001', 'experiment_name': 'DDoS-Test-1'}
)

print(f"Episode شروع شد: {episode_id}")

# 3. حلقه اصلی حمله
total_reward = 0.0
current_state = initial_state

for step in range(10):  # حداکثر 10 گام
    # انتخاب action بهینه
    action_idx = rl_engine.select_action(
        agent_type=RLAgentType.DDOS,
        state=current_state,
        explore=True  # exploration در مراحل اولیه
    )
    
    # تبدیل ایندکس به action واقعی
    action = RLAction(
        action_type=f"action_{action_idx}",
        parameters={'intensity': 0.5 + (action_idx * 0.1)}
    )
    
    # اعمال action در محیط (شبیه‌سازی)
    # در واقعیت، این کد simulation module را فراخوانی می‌کند
    next_state, reward, done = simulate_ddos_step(current_state, action)
    
    total_reward += reward
    
    # ذخیره تجربه
    rl_engine.store_experience(
        agent_type=RLAgentType.DDOS,
        state=current_state,
        action=action,
        reward=reward,
        next_state=next_state,
        done=done,
        priority=abs(reward)  # تجربیات با reward بالا، priority بیشتر
    )
    
    print(f"Step {step+1}: Action={action_idx}, Reward={reward:.2f}, Total={total_reward:.2f}")
    
    if done:
        print("حمله به پایان رسید (موفق یا شکست)")
        break
    
    current_state = next_state

# 4. پایان Episode
rl_engine.end_episode(
    agent_type=RLAgentType.DDOS,
    success=(total_reward > 0),
    total_reward=total_reward,
    metrics={
        'success_rate': 1.0 if total_reward > 0 else 0.0,
        'average_reward': total_reward / max(step + 1, 1),
        'total_damage': 0.8,
        'stealth_score': 0.6
    }
)

print(f"\n✓ Episode پایان یافت - Total Reward: {total_reward:.2f}")

# 5. بررسی نیاز به بازآموزی
if rl_engine.should_retrain(RLAgentType.DDOS):
    print("\n⚠️  نیاز به بازآموزی - شروع training...")
    rl_engine.train_agent(
        agent_type=RLAgentType.DDOS,
        batch_size=64,
        epochs=10
    )
    print("✓ بازآموزی تکمیل شد")

# 6. دریافت آمار
stats = rl_engine.get_statistics(RLAgentType.DDOS)
print(f"\nآمار Agent:")
for key, value in stats.items():
    print(f"  {key}: {value}")
```

### تابع کمکی: شبیه‌سازی (مثال)

```python
def simulate_ddos_step(state: RLState, action: RLAction) -> Tuple[RLState, float, bool]:
    """
    شبیه‌سازی یک گام حمله DDoS
    
    Returns:
        next_state: وضعیت بعدی
        reward: پاداش
        done: آیا حمله تمام شد؟
    """
    # محاسبه reward با استفاده از RewardFunction
    from core.rl_engine import RewardFunction
    
    reward_func = RewardFunction()
    
    # شبیه‌سازی نتیجه action
    success = (action.parameters.get('intensity', 0.5) > 0.7)
    time_taken = 10.0  # ثانیه
    stealth_score = 1.0 - action.parameters.get('intensity', 0.5)
    damage_level = action.parameters.get('intensity', 0.5)
    detected = (action.parameters.get('intensity', 0.5) > 0.9)
    
    reward = reward_func.calculate(
        success=success,
        time_taken=time_taken,
        stealth_score=stealth_score,
        damage_level=damage_level,
        detected=detected
    )
    
    # ایجاد next_state
    next_state = RLState(
        target_ip=state.target_ip,
        target_ports=state.target_ports,
        target_os=state.target_os,
        target_services=state.target_services,
        network_latency=state.network_latency,
        bandwidth=state.bandwidth,
        firewall_active=state.firewall_active,
        ids_active=state.ids_active,
        attack_stage=state.attack_stage + 1,
        time_elapsed=state.time_elapsed + time_taken,
        packets_sent=state.packets_sent + 1000,
        success_rate=0.5 if success else 0.0,
        previous_actions=state.previous_actions + [action.action_type],
        detection_count=state.detection_count + (1 if detected else 0)
    )
    
    # حمله تمام می‌شود اگر:
    # - موفق شد
    # - شناسایی شد
    # - زمان زیادی گذشته
    done = success or detected or (state.attack_stage >= 10)
    
    return next_state, reward, done
```

---

## ⚙️ پیکربندی

### فایل پیکربندی: `config/config.dev.yaml`

```yaml
rl_engine:
  # ابعاد فضای State و Action
  state_dimension: 13          # تعداد ویژگی‌های State
  action_dimension: 10         # تعداد Actionهای ممکن
  
  # پارامترهای یادگیری
  learning_rate: 0.1           # نرخ یادگیری (α)
  discount_factor: 0.99        # ضریب تخفیف (γ)
  
  # استراتژی Exploration
  epsilon_start: 1.0           # مقدار اولیه ε
  epsilon_decay: 0.995         # نرخ کاهش ε
  epsilon_min: 0.01            # حداقل ε
  
  # Experience Replay
  replay_buffer_size: 100000   # ظرفیت buffer
  priority_alpha: 0.6          # میزان اولویت‌دهی
  priority_beta: 0.4           # میزان importance sampling
  
  # بازآموزی
  retrain_interval: 100        # بازآموزی هر N episode
  batch_size: 64               # تعداد sample در هر batch
  training_epochs: 10          # تعداد epoch در هر بازآموزی
  
  # ذخیره‌سازی
  save_episodes_to_db: true    # ذخیره Episodeها در DB
  save_models_to_db: true      # ذخیره مدل‌ها در DB
  model_save_interval: 50      # ذخیره مدل هر N episode
  
  # وزن‌های Reward Function
  reward_success: 10.0         # وزن موفقیت
  reward_speed: 2.0            # وزن سرعت
  reward_stealth: 5.0          # وزن مخفی ماندن
  reward_damage: 3.0           # وزن آسیب
  reward_detection_penalty: -10.0  # جریمه شناسایی
  
  # الگوریتم‌های پشتیبانی شده
  algorithms:
    - q_learning              # Q-Learning کلاسیک
    - deep_q_network          # DQN
    - policy_gradient         # REINFORCE
    - actor_critic            # A2C/A3C
    - ppo                     # Proximal Policy Optimization
```

### تغییر پیکربندی در Runtime

```python
from core.config_manager import get_config

config = get_config()

# خواندن مقدار
learning_rate = config.get('rl_engine.learning_rate', 0.1)

# تغییر موقت (فقط در حافظه)
config.set('rl_engine.epsilon_start', 0.5)

# ذخیره دائمی
config.save()
```

---

## 💾 پایگاه داده

### Schema Overview

RL Engine از 4 جدول اصلی استفاده می‌کند:

#### 1. `rl_experiences` - تجربیات RL

```sql
CREATE TABLE rl_experiences (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    episode_id UUID NOT NULL,
    step_number INTEGER NOT NULL,
    state_json JSONB NOT NULL,
    action_json JSONB NOT NULL,
    reward FLOAT NOT NULL,
    next_state_json JSONB NOT NULL,
    done BOOLEAN DEFAULT FALSE,
    timestamp TIMESTAMP DEFAULT NOW(),
    priority FLOAT DEFAULT 1.0
);
```

**استفاده:**
- ذخیره تمام تجربیات برای بازآموزی
- Sample کردن با priority برای آموزش
- تحلیل رفتار Agent در گذشته

**مثال Query:**
```sql
-- تجربیات با بالاترین priority
SELECT * FROM rl_experiences
WHERE agent_type = 'ddos'
ORDER BY priority DESC
LIMIT 100;
```

#### 2. `rl_episodes` - نتایج Episode

```sql
CREATE TABLE rl_episodes (
    id UUID PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    total_reward FLOAT,
    steps_count INTEGER,
    success BOOLEAN,
    success_rate FLOAT,
    average_reward FLOAT,
    total_damage FLOAT,
    stealth_score FLOAT,
    model_version INTEGER
);
```

**استفاده:**
- ردیابی عملکرد Agent در طول زمان
- مقایسه نسخه‌های مختلف مدل
- تحلیل الگوهای موفقیت

**مثال Query:**
```sql
-- 10 بهترین Episode
SELECT * FROM rl_episodes
WHERE agent_type = 'ddos' AND success = true
ORDER BY total_reward DESC
LIMIT 10;
```

#### 3. `rl_models` - مدل‌های آموزش‌دیده

```sql
CREATE TABLE rl_models (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    version INTEGER NOT NULL,
    model_weights BYTEA NOT NULL,
    training_episodes INTEGER,
    average_reward FLOAT,
    success_rate FLOAT,
    trained_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT FALSE
);
```

**استفاده:**
- نسخه‌بندی مدل‌ها
- A/B Testing
- Rollback در صورت کاهش عملکرد

**مثال Query:**
```sql
-- مدل فعال فعلی
SELECT * FROM rl_models
WHERE agent_type = 'ddos' AND is_active = true;
```

#### 4. `rl_agent_stats` - آمار روزانه

```sql
CREATE TABLE rl_agent_stats (
    id SERIAL PRIMARY KEY,
    agent_type VARCHAR(50) NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    total_episodes INTEGER DEFAULT 0,
    successful_episodes INTEGER DEFAULT 0,
    failed_episodes INTEGER DEFAULT 0,
    total_reward FLOAT DEFAULT 0.0,
    average_reward FLOAT DEFAULT 0.0,
    epsilon FLOAT DEFAULT 1.0,
    training_steps INTEGER DEFAULT 0
);
```

**استفاده:**
- نمایش پیشرفت یادگیری
- Dashboard آماری
- تشخیص مشکلات عملکرد

---

## 🧮 الگوریتم‌ها

### 1. Q-Learning (پیاده‌سازی شده)

**فرمول:**
```
Q(s,a) ← Q(s,a) + α[r + γ max Q(s',a') - Q(s,a)]
```

**مزایا:**
- ✅ ساده و قابل فهم
- ✅ بدون نیاز به شبکه عصبی
- ✅ مناسب برای فضاهای کوچک

**معایب:**
- ❌ برای فضاهای بزرگ مقیاس‌پذیر نیست
- ❌ نمی‌تواند State های پیوسته را مدیریت کند

### 2. Deep Q-Network (DQN) - در حال توسعه

**معماری:**
```
State Vector (13) → Dense(64) → ReLU → Dense(32) → ReLU → Dense(10) → Q-Values
```

**مزایا:**
- ✅ مقیاس‌پذیر به فضاهای بزرگ
- ✅ می‌تواند ویژگی‌ها را خودکار استخراج کند
- ✅ عملکرد بهتر در مسائل پیچیده

### 3. Policy Gradient - در حال توسعه

**فرمول:**
```
∇J(θ) = E[∇log π(a|s) * R]
```

**مزایا:**
- ✅ مناسب برای Actionهای پیوسته
- ✅ می‌تواند سیاست‌های تصادفی یاد بگیرد

### 4. Proximal Policy Optimization (PPO) - در حال توسعه

**بهترین الگوریتم برای SecureRedLab**

**مزایا:**
- ✅ پایدار و قابل اعتماد
- ✅ نیاز به کمترین تنظیم پارامتر
- ✅ عملکرد عالی در مسائل پیچیده

---

## 🎯 بهینه‌سازی

### 1. Priority Experience Replay

به جای Sample کردن تصادفی، تجربیات مهم‌تر بیشتر sample می‌شوند:

```python
# اولویت = |TD Error|
priority = abs(reward + gamma * max_q_next - q_current)

# Sample با احتمال
P(i) = priority_i^α / Σ priority_j^α
```

**تأثیر:** یادگیری 2-3 برابر سریع‌تر

### 2. Importance Sampling

برای جبران bias ناشی از Priority Sampling:

```python
# وزن importance sampling
w_i = (N * P(i))^(-β)
w_i = w_i / max(w)  # Normalize
```

### 3. ε-Greedy Decay

کاهش تدریجی Exploration:

```python
# Epoch 0:   ε = 1.0   (100% exploration)
# Epoch 100: ε = 0.606 (60% exploration)
# Epoch 500: ε = 0.082 (8% exploration)
# Epoch 1000: ε = 0.01 (1% exploration - minimum)
```

### 4. Batch Training

آموزش با batch برای سرعت بیشتر:

```python
# به جای update تک‌تک
for exp in experiences:
    agent.update(exp)

# Batch update
batch = sample(experiences, size=64)
agent.batch_update(batch)
```

**تأثیر:** سرعت آموزش 10-20 برابر بیشتر

---

## 💡 مثال‌های کاربردی

### مثال 1: بهینه‌سازی حمله DDoS

**سناریو:** یافتن بهترین ترکیب تعداد bot و قدرت حمله

```python
# تعریف فضای Action
actions = [
    {'bots': 1000, 'power': 0.1},
    {'bots': 5000, 'power': 0.3},
    {'bots': 10000, 'power': 0.5},
    {'bots': 50000, 'power': 0.7},
    {'bots': 100000, 'power': 0.9}
]

# بعد از 1000 Episode:
# Agent یاد می‌گیرد که:
# - برای اهداف با فایروال ضعیف: بهترین = {bots: 5000, power: 0.3}
# - برای اهداف با IDS قوی: بهترین = {bots: 100000, power: 0.9}
```

### مثال 2: Shell Upload هوشمند

**سناریو:** انتخاب بهترین روش آپلود برای هر سیستم‌عامل

```python
# بعد از 500 Episode:
# Agent یاد می‌گیرد که:
# - Windows + IIS → روش: File upload vulnerability
# - Linux + Apache → روش: Remote code execution
# - با WAF → روش: Obfuscated payload
```

### مثال 3: بازیابی پس از شکست

**سناریو:** Agent یاد می‌گیرد از شکست‌های قبلی درس بگیرد

```python
# Episode 1-100: تلاش مستقیم → شناسایی شده → شکست
# Episode 101-200: Agent می‌آموزد ابتدا reconnaissance انجام دهد
# Episode 201-300: Agent می‌آموزد با سرعت کم شروع کند
# Episode 301+: نرخ موفقیت از 10% به 80% می‌رسد
```

---

## 🐛 عیب‌یابی

### مشکل 1: Agent یاد نمی‌گیرد

**علائم:**
- Reward به صورت ثابت می‌ماند
- Success rate بهبود پیدا نمی‌کند

**راه‌حل:**
```python
# 1. بررسی ε (باید به تدریج کاهش یابد)
stats = rl_engine.get_statistics(RLAgentType.DDOS)
print(f"Epsilon: {stats['epsilon']}")  # باید < 0.5 باشد بعد از 200 episode

# 2. افزایش learning rate
config.set('rl_engine.learning_rate', 0.3)

# 3. بررسی Reward Function
# آیا rewardها معنادار هستند؟
```

### مشکل 2: Agent بیش‌برازش می‌کند

**علائم:**
- عملکرد روی داده‌های تست ضعیف است
- Agent فقط در موقعیت‌های خاص کار می‌کند

**راه‌حل:**
```python
# 1. افزایش Exploration
config.set('rl_engine.epsilon_min', 0.1)  # به جای 0.01

# 2. افزایش تنوع داده
# استفاده از اهداف مختلف در آموزش

# 3. Early stopping
# متوقف کردن آموزش زمانی که validation error افزایش یافت
```

### مشکل 3: Buffer پر است

**علائم:**
```
WARNING: Experience Replay Buffer is full (100000/100000)
```

**راه‌حل:**
```python
# 1. افزایش ظرفیت
config.set('rl_engine.replay_buffer_size', 200000)

# 2. ذخیره در دیتابیس و پاک کردن buffer
buffer = rl_engine.replay_buffers[RLAgentType.DDOS]
buffer.save_to_database(db_manager)
buffer.buffer.clear()

# 3. استفاده از Prioritized Eviction
# تجربیات با priority پایین حذف شوند
```

### مشکل 4: آموزش بسیار کند است

**راه‌حل:**
```python
# 1. کاهش batch size
config.set('rl_engine.batch_size', 32)  # به جای 64

# 2. کاهش frequency بازآموزی
config.set('rl_engine.retrain_interval', 200)  # به جای 100

# 3. استفاده از GPU (اگر DQN استفاده می‌کنید)
# در آینده پیاده‌سازی خواهد شد
```

---

## 📊 نظارت و Monitoring

### Dashboard آماری

```python
# دریافت آمار تمام Agentها
for agent_type in RLAgentType:
    stats = rl_engine.get_statistics(agent_type)
    print(f"\n{agent_type.value}:")
    print(f"  Episodes: {stats['total_episodes']}")
    print(f"  Avg Reward: {stats['average_reward']:.2f}")
    print(f"  Epsilon: {stats['epsilon']:.3f}")
    print(f"  Buffer Size: {stats['buffer_size']}")
```

### نمودار پیشرفت

```sql
-- Query برای نمودار پیشرفت
SELECT 
    date,
    agent_type,
    average_reward,
    average_success_rate,
    epsilon
FROM rl_agent_stats
WHERE agent_type = 'ddos'
ORDER BY date;
```

### هشدارهای خودکار

```python
# بررسی کاهش عملکرد
current_success_rate = get_current_success_rate(agent_type)
if current_success_rate < 0.5:
    logger.warning(f"عملکرد {agent_type} کاهش یافته - نیاز به بررسی")
    # ارسال اعلان
```

---

## 🔬 تحقیق و توسعه

### ایده‌های آینده

1. **Multi-Agent RL**: همکاری بین Agentها
2. **Meta-Learning**: یادگیری نحوه یادگیری
3. **Curriculum Learning**: آموزش تدریجی از ساده به پیچیده
4. **Transfer Learning**: انتقال دانش بین Agentها
5. **Inverse RL**: یادگیری از تخصص‌های انسانی

---

## 📖 منابع

### مقالات علمی

1. Mnih et al. (2015) - Human-level control through deep reinforcement learning
2. Schulman et al. (2017) - Proximal Policy Optimization Algorithms
3. Schaul et al. (2016) - Prioritized Experience Replay

### کتاب‌ها

1. Sutton & Barto - Reinforcement Learning: An Introduction
2. Bertsekas - Dynamic Programming and Optimal Control

---

## 📞 پشتیبانی

برای سوالات و مشکلات:

- **Email**: support@secureredlab.edu
- **Documentation**: `/docs/RL_ENGINE_GUIDE.md`
- **Issues**: داخل سیستم لاگ‌گیری با سطح ERROR

---

**توجه:** این سیستم تنها برای تحقیقات آکادمیک و با مجوزهای قانونی (FBI, IRB, Police, University) قابل استفاده است.

**این سند آخرین بار در 2025-01-15 به‌روز شد.**
