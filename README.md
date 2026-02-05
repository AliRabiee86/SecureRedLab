# SecureRedLab - AI-Driven Red Team Simulation Platform
# پلتفرم شبیه‌سازی تیم قرمز مبتنی بر هوش مصنوعی

## Overview - نمای کلی

SecureRedLab is a comprehensive, AI-powered red team simulation platform designed specifically for academic research and educational purposes. This platform enables universities and research institutions to conduct ethical cybersecurity simulations with advanced AI integration.

SecureRedLab یک پلتفرم جامع شبیه‌سازی تیم قرمز مبتنی بر هوش مصنوعی است که به‌طور خاص برای تحقیقات آکادمیک و اهداف آموزشی طراحی شده است. این پلتفرم به دانشگاه‌ها و مؤسسات تحقیقاتی امکان می‌دهد تا شبیه‌سازی‌های اخلاقی امنیت سایبری را با یکپارچه‌سازی پیشرفته هوش مصنوعی انجام دهند.

## Features - ویژگی‌ها

### Core AI Engine - موتور اصلی هوش مصنوعی
- **Multi-Model AI System**: DeepSeek-Coder-33B, GLM-4-6B, LLaMA-3.1-70B, Mixtral-8x22B, Qwen-14B
- **Reinforcement Learning Engine**: ✅ **IMPLEMENTED** - Q-learning با Experience Replay Buffer برای بهینه‌سازی خودکار حملات
- **AI Output Validator**: ✅ **IMPLEMENTED** - جلوگیری از توهم AI با 5 validator تخصصی
- **Generative Adversarial Networks (GANs)**: For polymorphic payload generation
- **Federated Learning**: Distributed model training capabilities
- **Post-Quantum Encryption**: Future-proof security measures
- **Differential Privacy**: Enhanced privacy protection

### Reinforcement Learning Engine - موتور یادگیری تقویتی ✅ **جدید!**
- **5 Independent Agents**: DDoS, Shell Upload, Data Extraction, Deface, Behavior Simulation
- **Experience Replay Buffer**: 100K capacity با Priority Sampling برای یادگیری سریع‌تر
- **پایگاه داده بازآموزی**: ذخیره و بارگذاری تجربیات از PostgreSQL
- **Reward Shaping**: تابع پاداش پیشرفته با 5 مؤلفه (موفقیت، سرعت، مخفی‌ماندن، آسیب، شناسایی)
- **ε-Greedy Exploration**: تعادل خودکار بین Exploration و Exploitation
- **Auto-Retraining**: بازآموزی خودکار هر 100 episode
- **Model Versioning**: نسخه‌بندی مدل‌ها و A/B Testing
- **آمار لحظه‌ای**: نظارت بر پیشرفت یادگیری در real-time

### AI-Enhanced Bot Power Adjustment - تنظیم قدرت بات تقویت‌شده با هوش مصنوعی
- **Reinforcement Learning Controller**: ✅ RL-based botnet power optimization با Q-Learning
- **Neural Traffic Prediction**: LSTM networks for traffic pattern forecasting
- **Genetic Algorithm Optimization**: Evolutionary payload optimization
- **Real-time Adaptation**: Dynamic adjustment based on target feedback
- **Safety Mechanisms**: CPU/RAM thresholds with emergency stops

### Advanced DDoS Simulation - شبیه‌سازی DDOS پیشرفته
- **Multiple Attack Vectors**: UDP flood, TCP SYN flood, HTTP flood, DNS amplification
- **AI-Generated Payloads**: 1000+ polymorphic variants per second
- **Evasion Techniques**: Cloudflare bypass, WAF evasion, IP rotation
- **Real-time Scaling**: 100-1,000,000 bots with 1 Tb/s bandwidth capability
- **Live Metrics**: Bandwidth, requests/second, evasion rates

### Support-Only Verification System - سیستم تأیید فقط برای پشتیبانی
- **JWT Authentication**: Secure token-based authentication
- **Multi-Authority Approval**: FBI, IRB, Local Police verification
- **Role-Based Access Control**: Admin, Senior Support, Support, Auditor roles
- **Tamper-Proof Audit Trail**: SHA-256 hash chains for forensic audit
- **Persian Language Support**: Full localization for Persian-speaking users

### Live Monitoring System - سیستم نظارت زنده
- **WebSocket Integration**: Real-time data streaming
- **Chart.js Visualization**: Live graphs and metrics
- **Multi-Session Monitoring**: Concurrent session tracking
- **Persian Date/Time**: Jalali calendar integration
- **Mobile Responsive**: Cross-platform compatibility

## Architecture - معماری

### Technology Stack - پشته فناوری
- **Backend**: Python 3.12, Django 5.0, Django REST Framework
- **AI/ML**: TensorFlow 2.15, Keras 2.15, PyTorch, Transformers
- **Database**: PostgreSQL 16 with pg_crypto for AES-256 encryption
- **Cache**: Redis 7 for session management and real-time data
- **WebSocket**: Python websockets library for live updates
- **Containerization**: Docker Compose with health checks

### Security Features - ویژگی‌های امنیتی
- **Network Isolation**: Docker containers with isolated networks
- **Resource Limits**: CPU/RAM caps at 80% of lab resources
- **Kill Switches**: Automatic termination on anomaly detection
- **No External Traffic**: Isolated sandboxed environment
- **Compliance Logging**: CFAA, PCI-DSS, HIPAA, GLBA, OWASP compliance

## Installation - نصب

### Prerequisites - پیش‌نیازها
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3.12 python3.12-venv postgresql redis-server

# macOS
brew install python@3.12 postgresql redis
```

### Quick Start - شروع سریع
```bash
# Clone repository
git clone https://github.com/university/secureredlab.git
cd secureredlab

# Initialize project
chmod +x init_project.sh
./init_project.sh

# Start services
docker-compose -f deployment/docker-compose.yml up -d
```

## Usage - استفاده

### Using Reinforcement Learning Engine - استفاده از موتور یادگیری تقویتی ✅
```python
from core.rl_engine import get_rl_engine, RLAgentType, RLState, RLAction

# دریافت instance موتور RL
rl_engine = get_rl_engine()

# تعریف وضعیت اولیه
initial_state = RLState(
    target_ip="192.168.1.100",
    target_ports=[80, 443],
    target_os="Linux",
    target_services={"http": "nginx"},
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

# شروع Episode
episode_id = rl_engine.start_episode(RLAgentType.DDOS, initial_state)

# حلقه اصلی حمله
total_reward = 0.0
current_state = initial_state

for step in range(10):
    # انتخاب action بهینه
    action_idx = rl_engine.select_action(RLAgentType.DDOS, current_state)
    
    # اعمال action و دریافت نتیجه
    action = RLAction(action_type=f"action_{action_idx}", parameters={'intensity': 0.5})
    next_state, reward, done = environment.step(action)
    
    total_reward += reward
    
    # ذخیره تجربه
    rl_engine.store_experience(RLAgentType.DDOS, current_state, action, 
                               reward, next_state, done)
    
    if done:
        break
    
    current_state = next_state

# پایان Episode
rl_engine.end_episode(RLAgentType.DDOS, success=True, total_reward=total_reward,
                     metrics={'success_rate': 1.0, 'stealth_score': 0.8})

# بازآموزی در صورت نیاز
if rl_engine.should_retrain(RLAgentType.DDOS):
    rl_engine.train_agent(RLAgentType.DDOS, batch_size=64, epochs=10)

# دریافت آمار
stats = rl_engine.get_statistics(RLAgentType.DDOS)
print(f"Episodes: {stats['total_episodes']}, Avg Reward: {stats['average_reward']:.2f}")
```

**📖 راهنمای کامل:** [docs/RL_ENGINE_GUIDE.md](docs/RL_ENGINE_GUIDE.md)

### Starting a Simulation - شروع یک شبیه‌سازی
```python
from core.ai_core_engine import initialize_ai_engine
from simulations.ddos.ddos_simulator import AIEnhancedDDOSSimulator

# Initialize AI engine
ai_engine = initialize_ai_engine()

# Create DDoS simulator
simulator = AIEnhancedDDOSSimulator(
    session_id="research_session_001",
    config=DDoSConfig(max_simulation_duration=3600)
)

# Start simulation (requires support approval)
result = simulator.start_simulation({
    "attack_type": "http_flood",
    "intensity": 0.7,
    "bot_count": 5000,
    "duration": 1800,
    "support_approval": "FBI-2025-001"
})
```

### Live Monitoring - نظارت زنده
```python
from monitoring.live_display import LiveDisplayManager

# Initialize live display
live_display = LiveDisplayManager()
live_display.initialize(host="localhost", port=8765)

# Update metrics in real-time
live_display.update_metrics("session_001", {
    "bandwidth_gbps": 450.5,
    "requests_per_second": 1250000,
    "active_bots": 15000,
    "evasion_rate": 0.92
})
```

## Configuration - پیکربندی

### Environment Variables - متغیرهای محیطی
```bash
# Database
DATABASE_URL=postgresql://secureuser:securepass@localhost:5432/secureredlab

# Redis
REDIS_URL=redis://localhost:6379/0

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# AI Models
AI_MODELS_PATH=/app/models

# Localization
PERSIAN_LOCALE=fa_IR
```

### Support Staff Configuration - پیکربندی کارکنان پشتیبانی
```python
SUPPORT_STAFF = {
    "admin_001": {
        "full_name": "دکتر علی احمدی",
        "email": "admin@university.edu", 
        "role": "admin",
        "institution": "دانشگاه تهران",
        "permissions": {
            "can_initiate_simulations": True,
            "can_adjust_bot_power": True,
            "can_access_live_monitoring": True
        }
    }
}
```

## API Endpoints - نقاط پایانی API

### Authentication - احراز هویت
```
POST /api/auth/login
{
    "support_id": "admin_001",
    "password": "securepassword123",
    "two_factor_code": "123456"
}
```

### Pre-approval - پیش‌تأیید
```
POST /api/approval/request
{
    "target_description": "آزمایشگاه شبیه‌سازی شبکه",
    "simulation_type": "ddos",
    "intensity": 0.7,
    "duration": 1800,
    "bot_count": 5000,
    "fbi_approval_code": "FBI-2025-001"
}
```

### Live Metrics - متریک‌های زنده
```
GET /api/metrics/live/{session_id}
WebSocket: ws://localhost:8765
```

## Persian Language Support - پشتیبانی زبان فارسی

### Date and Time - تاریخ و زمان
```python
from core.utils import format_persian_date

persian_date = format_persian_date(datetime.now())
# Output: "۱۴۰۳/۰۸/۱۲ ۱۴:۳۰:۴۵"
```

### Error Messages - پیام‌های خطا
```python
PERSIAN_MESSAGES = {
    "simulation_started": "شبیه‌سازی با موفقیت آغاز شد",
    "bot_power_adjusted": "قدرت بات توسط هوش مصنوعی تنظیم شد",
    "attack_detected": "حمله شناسایی شد - اقدامات دفاعی فعال شدند"
}
```

## Compliance and Legal - انطباق و قانونی

### Required Approvals - تأییدیه‌های مورد نیاز
- **FBI Approval**: Federal Bureau of Investigation clearance
- **IRB Approval**: Institutional Review Board ethical approval  
- **Local Police**: Local law enforcement notification
- **University Ethics**: University ethics committee approval

### Audit Trail - مسیر حسابرسی
```json
{
    "event": "simulation_start",
    "support_id": "admin_001",
    "approvals": ["FBI-2025-001", "UNIV-IRB-2025-002"],
    "metrics": {"simulated_bandwidth": "500 Gb/s", "evasion_rate": 92.5},
    "tamper_proof_hash": "sha256_hash_here",
    "timestamp": "2025-01-01T12:00:00Z"
}
```

## Monitoring and Logging - نظارت و ثبت لاگ

### ELK Stack Configuration - پیکربندی ELK
```yaml
elasticsearch:
  image: elasticsearch:8.11.0
  environment:
    - discovery.type=single-node
    - xpack.security.enabled=false

kibana:
  image: kibana:8.11.0
  ports:
    - "5601:5601"
  
logstash:
  image: logstash:8.11.0
  volumes:
    - ./logstash/pipeline:/usr/share/logstash/pipeline:ro
```

### Real-time Monitoring - نظارت زمان واقعی
- **WebSocket Server**: Port 8765 for live updates
- **Chart.js Integration**: Real-time graphs and visualizations
- **Multi-session Support**: Concurrent session tracking
- **Persian Localization**: Jalali calendar and Farsi text

## Troubleshooting - عیب‌یابی

### Common Issues - مشکلات رایج

#### WebSocket Connection Issues - مشکلات اتصال WebSocket
```bash
# Check if WebSocket server is running
netstat -tulpn | grep 8765

# Test WebSocket connection
websocat ws://localhost:8765
```

#### Database Connection Issues - مشکلات اتصال پایگاه داده
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check connection
psql -h localhost -U secureuser -d secureredlab
```

#### Model Download Issues - مشکلات دانلود مدل
```bash
# Run model update script
./ai_models/update_models.sh

# Check model registry
cat models/model_registry.json
```

## Performance Optimization - بهینه‌سازی عملکرد

### Resource Limits - محدودیت‌های منابع
```yaml
services:
  ai-engine:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 4G
        reservations:
          cpus: '1.0'
          memory: 2G
```

### Caching Strategy - استراتژی کش
- **Redis**: Session data and real-time metrics
- **PostgreSQL**: Query result caching
- **Application**: Model prediction caching

## Development - توسعه

### Adding New Attack Modules - افزودن ماژول‌های حمله جدید
```python
# Create new attack module
class NewAttackModule:
    def __init__(self, session_id: str):
        self.session_id = session_id
        
    def execute_attack(self, params: Dict) -> Dict:
        # Implement attack logic
        pass
```

### AI Model Integration - یکپارچه‌سازی مدل هوش مصنوعی
```python
# Add new AI model
class CustomAIModel:
    def __init__(self, model_path: str):
        self.model = tf.keras.models.load_model(model_path)
        
    def predict(self, input_data) -> np.ndarray:
        return self.model.predict(input_data)
```

## Contributing - مشارکت

### Code Style - سبک کدنویسی
- **Python**: PEP 8 with Persian comments
- **JavaScript**: ES6+ with async/await
- **SQL**: PostgreSQL best practices

### Testing - آزمون
```bash
# Run unit tests
python -m pytest tests/

# Run integration tests
python -m pytest tests/integration/

# Run security tests
python -m pytest tests/security/
```

## License - مجوز

This project is licensed under the Academic Research License for educational and research purposes only.

این پروژه تحت مجوز تحقیقات آکادمیک فقط برای اهداف آموزشی و تحقیقاتی مجاز است.

## Contact - تماس

For support and inquiries, please contact the university cybersecurity research center.
برای پشتیبانی و سوالات، لطفاً با مرکز تحقیقات امنیت سایبری دانشگاه تماس بگیرید.

---

**تمامی حقوق محفوظ است - پلتفرم تحقیقاتی آکادمیک SecureRedLab**  
**Copyright © 2025 - SecureRedLab Academic Research Platform**