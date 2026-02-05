# 🏗️ Plan C: Hybrid Architecture - سیستم هیبریدی SecureRedLab

## 📊 نمای کلی

این سند شامل برنامه‌ی کامل برای ساخت سیستم هیبریدی است که:
- ✅ 95% کد موجود را حفظ می‌کند
- ✅ اجرای واقعی حملات را ممکن می‌سازد
- ✅ قانونی و ایمن است (Docker Isolation)
- ✅ مقیاس‌پذیر و قابل توسعه است

---

## 🎯 معماری پیشنهادی

```
┌─────────────────────────────────────────────────────┐
│                  Cloudflare Pages                   │
│            (Frontend - کد موجود 95%)               │
│  - Dashboard UI                                     │
│  - Live Monitoring (WebSocket)                      │
│  - Auth System ✅                                    │
│  - Report Viewer                                     │
└──────────────┬──────────────────────────────────────┘
               │ HTTPS REST API + WebSocket
               │ JWT Authentication
               ▼
┌─────────────────────────────────────────────────────┐
│              VPS Backend (FastAPI)                  │
│         (کد موجود قابل استفاده 95%)                │
│  ┌──────────────────────────────────────────────┐  │
│  │  Core Modules (کپی مستقیم از Sandbox)       │  │
│  │  - logging_system.py ✅                      │  │
│  │  - exception_handler.py ✅                   │  │
│  │  - config_manager.py ✅                      │  │
│  │  - database_manager.py ✅                    │  │
│  │  - auth_system.py ✅                         │  │
│  │  - ai_output_validator.py ✅                 │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  AI Cores (کپی با تغییرات جزئی)             │  │
│  │  - ai/offline_core.py ✅                     │  │
│  │  - ai/vllm_client.py ✅                      │  │
│  │  - ai/vlm_core.py ✅                         │  │
│  │  - core/rl_engine.py ✅                      │  │
│  │  - core/neural_vuln_scanner.py ✅            │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  New Execution Layer (نیاز به ساخت)         │  │
│  │  - execution/metasploit_executor.py          │  │
│  │  - execution/sqlmap_executor.py              │  │
│  │  - execution/nmap_executor.py                │  │
│  │  - execution/waf_bypass.py                   │  │
│  │  - execution/attack_orchestrator.py          │  │
│  └──────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────┐  │
│  │  Task Queue (Celery + Redis)                 │  │
│  └──────────────────────────────────────────────┘  │
└──────────────┬──────────────────────────────────────┘
               │ Docker Network (Isolated)
               ▼
┌─────────────────────────────────────────────────────┐
│         Docker Containers (Execution Layer)         │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐   │
│  │ Metasploit │  │   SQLMap   │  │    Nmap    │   │
│  │ Container  │  │ Container  │  │ Container  │   │
│  └────────────┘  └────────────┘  └────────────┘   │
│  ┌────────────┐  ┌────────────┐                    │
│  │ AI Payloads│  │   Custom   │                    │
│  │ Container  │  │   Tools    │                    │
│  └────────────┘  └────────────┘                    │
│  - Network Isolation ✅                             │
│  - Resource Limits ✅                               │
│  - Kill Switches ✅                                 │
└─────────────────────────────────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────────────────┐
│     Target Environments (Docker Compose)            │
│  - Vulnerable Web Apps (DVWA, bWAPP)               │
│  - Custom Targets                                   │
│  - WAF Simulation (ModSecurity)                     │
│  - IDS Simulation (Snort)                           │
└─────────────────────────────────────────────────────┘
```

---

## 📦 استفاده از کد موجود

### ✅ فایل‌های قابل استفاده مستقیم (480KB - 95%):

```bash
# Core Modules - کپی مستقیم (Copy-Paste)
core/logging_system.py         # ✅ 800 خط - بدون تغییر
core/exception_handler.py      # ✅ 700 خط - بدون تغییر
core/config_manager.py         # ✅ 600 خط - بدون تغییر
core/database_manager.py       # ✅ 900 خط - بدون تغییر
core/auth_system.py            # ✅ 400 خط - بدون تغییر
core/support_verification.py   # ✅ 600 خط - بدون تغییر
core/ai_output_validator.py    # ✅ 800 خط - بدون تغییر
core/bot_power_controller.py   # ✅ 700 خط - بدون تغییر

# AI Cores - کپی با تغییرات جزئی (<5%)
ai/offline_core.py             # ✅ 1,200 خط - تغییر import ها
ai/vllm_client.py              # ✅ 500 خط - تغییر import ها
ai/dual_track_router.py        # ✅ 400 خط - بدون تغییر
ai/anti_hallucination.py       # ✅ 400 خط - بدون تغییر
ai/vlm_core.py                 # ✅ 700 خط - بدون تغییر
ai/vlm_client.py               # ✅ 400 خط - بدون تغییر
ai/vlm_router.py               # ✅ 300 خط - بدون تغییر
ai/ocr_fallback.py             # ✅ 300 خط - بدون تغییر
ai/vlm_hallucination.py        # ✅ 250 خط - بدون تغییر

# RL Engine - کپی مستقیم
core/rl_engine.py              # ✅ 1,700 خط - بدون تغییر

# Neural Scanner - کپی با تغییرات (10%)
core/neural_vuln_scanner.py    # ✅ 1,300 خط - اضافه Nmap واقعی

# Tests - کپی مستقیم
tests/test_rl_engine.py        # ✅ 400 خط - بدون تغییر
tests/test_vlm_core.py         # ✅ 450 خط - بدون تغییر
tests/test_ai_validator.py     # ✅ 300 خط - بدون تغییر
tests/test_end_to_end.py       # ✅ 365 خط - بدون تغییر
```

**📊 آمار:**
- **کد قابل استفاده:** ~14,000 خط (95%)
- **کد نیاز به تغییر:** ~700 خط (5%)
- **کد جدید مورد نیاز:** ~8,000 خط (35% پروژه)

---

## 🛠️ مراحل پیاده‌سازی (12 Phase)

### **Phase 1: VPS Setup (1 روز)**

**هدف:** راه‌اندازی VPS و نصب ابزارهای پایه

**چک‌لیست:**
- [ ] خرید/راه‌اندازی VPS (Ubuntu 22.04، 4 CPU، 8GB RAM)
- [ ] نصب Docker + Docker Compose
- [ ] نصب Python 3.12
- [ ] نصب PostgreSQL 16
- [ ] نصب Redis 7
- [ ] تنظیم Firewall
- [ ] تنظیم SSH Keys

**دستورات:**
```bash
# به‌روزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# نصب Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# نصب Python 3.12
sudo add-apt-repository ppa:deadsnakes/ppa -y
sudo apt install python3.12 python3.12-venv python3.12-dev -y

# نصب PostgreSQL 16
sudo sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo tee /etc/apt/trusted.gpg.d/pgdg.asc &>/dev/null
sudo apt update
sudo apt install postgresql-16 postgresql-contrib-16 -y

# نصب Redis
sudo apt install redis-server -y

# تنظیم Firewall
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw enable
```

---

### **Phase 2: Core Migration (1-2 روز)**

**هدف:** انتقال ماژول‌های اصلی از Sandbox به VPS

**روش:**
```bash
# در Sandbox:
cd /home/user/webapp/SecureRedLab
git add -A
git commit -m "Prepare for VPS migration"
git push origin main

# در VPS:
cd /home/secureredlab
git clone YOUR_REPO_URL SecureRedLab
cd SecureRedLab

# ساخت Virtual Environment
python3.12 -m venv venv
source venv/bin/activate

# نصب Dependencies
pip install -r requirements.txt
```

**requirements.txt:**
```txt
# Core
fastapi==0.109.0
uvicorn[standard]==0.27.0
pydantic==2.5.0
pydantic-settings==2.1.0

# Database
psycopg2-binary==2.9.9
redis==5.0.1
sqlalchemy==2.0.25

# Security
PyJWT==2.8.0
cryptography==41.0.7
bcrypt==4.1.2

# AI/ML
tensorflow==2.15.0
torch==2.1.2
transformers==4.36.2
numpy==1.26.3
scikit-learn==1.4.0

# Task Queue
celery==5.3.6
flower==2.0.1

# Utils
python-multipart==0.0.6
httpx==0.26.0
pyyaml==6.0.1
python-dotenv==1.0.0
```

---

### **Phase 3: Database Setup (1 روز)**

**هدف:** راه‌اندازی PostgreSQL با Schema کامل

**دستورات:**
```sql
-- ساخت Database و User
sudo -u postgres psql << EOF
CREATE DATABASE secureredlab_production;
CREATE USER secureredlab_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE secureredlab_production TO secureredlab_user;
\q
EOF

-- اجرای Migrations
python manage.py migrate
```

---

### **Phase 4: FastAPI Backend (2 روز)**

**هدف:** ساخت REST API برای ارتباط Frontend-Backend

**ساختار:**
```python
# backend/main.py
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SecureRedLab API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend.pages.dev"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API Routes
@app.post("/api/scans/start")
async def start_scan(target: str, scan_type: str):
    # Call Neural Scanner
    ...

@app.get("/api/scans/{scan_id}/status")
async def get_scan_status(scan_id: str):
    ...

# WebSocket for Live Updates
@app.websocket("/ws/scans/{scan_id}")
async def websocket_scan(websocket: WebSocket, scan_id: str):
    ...
```

---

### **Phase 5: Docker Containers (2-3 روز)**

**هدف:** ساخت Isolated Execution Environment

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  # PostgreSQL
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: secureredlab_production
      POSTGRES_USER: secureredlab_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  # Redis
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  # FastAPI Backend
  backend:
    build: ./backend
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://secureredlab_user:${DB_PASSWORD}@postgres:5432/secureredlab_production
      - REDIS_URL=redis://redis:6379/0
    ports:
      - "8000:8000"

  # Celery Worker
  celery_worker:
    build: ./backend
    command: celery -A tasks worker --loglevel=info
    depends_on:
      - postgres
      - redis

  # Metasploit Container
  metasploit:
    image: metasploitframework/metasploit-framework
    network_mode: "isolated_network"

  # Nmap Container
  nmap:
    build: ./docker/nmap
    network_mode: "isolated_network"

  # SQLMap Container
  sqlmap:
    image: paoloo/sqlmap
    network_mode: "isolated_network"

  # Target: DVWA
  dvwa:
    image: vulnerables/web-dvwa
    network_mode: "isolated_network"

  # Target: bWAPP
  bwapp:
    image: raesene/bwapp
    network_mode: "isolated_network"

networks:
  isolated_network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.25.0.0/16

volumes:
  postgres_data:
```

---

### **Phase 6: Execution Layer (3-4 روز)**

**هدف:** ساخت Wrapper برای Metasploit, Nmap, SQLMap

**مثال:**
```python
# execution/nmap_executor.py
import docker
import json
from typing import Dict, List

class NmapExecutor:
    def __init__(self):
        self.client = docker.from_env()
    
    def scan_port(self, target: str, ports: List[int]) -> Dict:
        """
        اجرای Nmap در Docker Container ایزوله
        """
        # Run Nmap container
        result = self.client.containers.run(
            image="nmap-container",
            command=f"nmap -p {','.join(map(str, ports))} {target}",
            network="isolated_network",
            remove=True,
            stdout=True,
            stderr=True
        )
        
        # Parse output
        return self._parse_nmap_output(result)
```

---

### **Phase 7-12:** (خلاصه)

- **Phase 7:** Integration با AI Cores (1 روز)
- **Phase 8:** WebSocket برای Live Updates (1 روز)
- **Phase 9:** Frontend Update برای VPS API (1 روز)
- **Phase 10:** WAF/IDS Simulation (2 روز)
- **Phase 11:** Testing & Debugging (2-3 روز)
- **Phase 12:** Documentation & Deployment (1 روز)

**جمع کل زمان:** 14-18 روز (2-3 هفته)

---

## 💰 هزینه‌ها

| منبع | مشخصات | هزینه/ماه |
|------|---------|----------|
| **VPS** | 4 CPU, 8GB RAM, 160GB SSD | $20-30 |
| **Cloudflare Pages** | Unlimited (Frontend) | $0 |
| **Domain** | .edu یا .com | $10-15 |
| **Backup Storage** | Optional | $0-10 |
| **جمع کل** | - | **$30-55/ماه** |

---

## 🚀 مزایای Plan C

1. **95% کد موجود قابل استفاده** - کم‌ترین waste
2. **اجرای واقعی حملات** - در isolated environment
3. **Cloudflare Pages حفظ می‌شود** - برای Frontend
4. **مقیاس‌پذیری** - می‌توان target های بیشتری اضافه کرد
5. **ایمن و قانونی** - Docker isolation
6. **تست واقعی** - با ابزارهای واقعی (Nmap, Metasploit)

---

## ⚠️ ملاحظات امنیتی

1. **Network Isolation:** همه containers در شبکه‌ی جدا
2. **Resource Limits:** محدودیت CPU/RAM برای هر container
3. **Kill Switches:** قابلیت متوقف کردن فوری
4. **Audit Trail:** لاگ کامل همه فعالیت‌ها
5. **Legal Compliance:** مطابق با FBI/IRB approvals

---

## 📝 نتیجه‌گیری

**Plan C بهترین انتخاب است چون:**
- ✅ کمترین تغییر در کد موجود (5%)
- ✅ بیشترین قابلیت (اجرای واقعی)
- ✅ هزینه‌ی معقول ($30-55/ماه)
- ✅ زمان معقول (2-3 هفته)
- ✅ مقیاس‌پذیر و قابل توسعه

**آماده برای شروع؟** 🚀
