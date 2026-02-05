# 🚀 راهنمای کامل راه‌اندازی SecureRedLab - Plan C (Hybrid Architecture)

**نویسنده:** معلم سختگیر (AI Assistant)  
**تاریخ:** 2025-12-21  
**نسخه:** 1.0.0  
**وضعیت:** در حال توسعه

---

## 📋 فهرست مطالب

1. [معرفی سیستم](#1-معرفی-سیستم)
2. [معماری کلی](#2-معماری-کلی)
3. [پیش‌نیازها](#3-پیش-نیازها)
4. [راه‌اندازی VPS](#4-راه-اندازی-vps)
5. [نصب Backend](#5-نصب-backend)
6. [نصب Docker Services](#6-نصب-docker-services)
7. [راه‌اندازی Frontend](#7-راه-اندازی-frontend)
8. [تنظیمات امنیتی](#8-تنظیمات-امنیتی)
9. [Troubleshooting](#9-troubleshooting)

---

## 1. معرفی سیستم

### 🎯 **SecureRedLab چیست؟**

SecureRedLab یک **سیستم هوشمند تست نفوذ** است که با ترکیب **Reinforcement Learning (RL)** و **هوش مصنوعی آفلاین (Offline AI)** قادر به:
- شبیه‌سازی حملات DDoS
- تست آسیب‌پذیری‌های وب
- آپلود Shell و کنترل سیستم
- استخراج اطلاعات حساس
- تحلیل تصویر با VLM (Vision Language Models)

### 🏗️ **معماری سیستم**

```
┌──────────────────────────────────────────────────────┐
│          Cloudflare Pages (Frontend)                 │
│  - React/Vue/Vanilla JS                             │
│  - Static Hosting                                    │
└─────────────────┬────────────────────────────────────┘
                  │ HTTPS API Calls
                  │
┌─────────────────▼────────────────────────────────────┐
│                   VPS Backend                        │
│  ┌────────────────────────────────────────────────┐  │
│  │  FastAPI (Python 3.12)                        │  │
│  │  - REST API                                    │  │
│  │  - WebSocket Real-time                        │  │
│  │  - JWT Authentication                         │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  Celery Workers                                │  │
│  │  - Execution Queue (Nmap, Metasploit)        │  │
│  │  - AI Queue (LLM, VLM)                        │  │
│  │  - RL Queue (Training)                        │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  Offline AI Core                               │  │
│  │  - 4 LLM Models (Qwen, GLM, DeepSeek)        │  │
│  │  - 5 VLM Models (InternVL, Qwen2.5-VL)       │  │
│  │  - 3-Tier OCR Fallback                        │  │
│  │  - Anti-Hallucination System (<5%)           │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  RL Engine                                     │  │
│  │  - 5 Independent Agents                       │  │
│  │  - Q-Learning                                  │  │
│  │  - Auto-Retraining                            │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  Docker Containers (Isolated)                  │  │
│  │  - Metasploit Framework                       │  │
│  │  - Nmap                                        │  │
│  │  - SQLMap                                      │  │
│  │  - Nuclei                                      │  │
│  └────────────────────────────────────────────────┘  │
│                                                       │
│  ┌────────────────────────────────────────────────┐  │
│  │  Databases                                     │  │
│  │  - PostgreSQL (Main DB)                       │  │
│  │  - Redis (Cache + Celery)                     │  │
│  └────────────────────────────────────────────────┘  │
└───────────────────────────────────────────────────────┘
```

---

## 2. معماری کلی

### **🔧 Stack تکنولوژی**

#### **Backend:**
- **FastAPI** (Python 3.12): Framework اصلی
- **Celery**: Task Queue برای اجرای async
- **Redis**: Broker + Result Backend
- **PostgreSQL**: Database اصلی
- **SQLAlchemy**: ORM
- **Alembic**: Database Migrations
- **Uvicorn**: ASGI Server
- **Docker SDK**: کنترل Containers

#### **AI Stack:**
- **vLLM**: Inference Engine برای LLM/VLM
- **4 LLM Models:**
  - Qwen3-235B-A22B (Reasoning)
  - GLM-4.6-Reasoning (Reasoning)
  - DeepSeek-V3.2-Exp (Non-Reasoning)
  - GLM-4.6 (Non-Reasoning)
- **5 VLM Models:**
  - InternVL3-78B (Complex)
  - Qwen2.5-VL-72B-AWQ (Complex)
  - Hunyuan-OCR (Document)
  - MiniCPM-V-4.5 (OCR)
  - InternVL2-8B (Light)

#### **Tools:**
- **Metasploit Framework**: Exploitation
- **Nmap**: Port Scanning
- **SQLMap**: SQL Injection
- **Nuclei**: Vulnerability Scanner

---

## 3. پیش‌نیازها

### **🖥️ سخت‌افزار VPS:**

| مورد | حداقل | پیشنهادی | عالی |
|------|-------|----------|------|
| **CPU** | 4 Core | 8 Core | 16 Core |
| **RAM** | 8 GB | 16 GB | 32 GB |
| **Storage** | 80 GB | 160 GB | 320 GB |
| **GPU** | - | - | 2× RTX 4090 (48GB VRAM) |
| **Bandwidth** | Unlimited | Unlimited | Unlimited |

**⚠️ توجه:** برای استفاده از AI Offline، حداقل **2× RTX 4090** لازم است.

### **💰 هزینه‌های ماهانه:**

| سرویس | حداقل | پیشنهادی |
|-------|-------|----------|
| **VPS** | $30-40/mo | $50-100/mo |
| **Domain + SSL** | $0 (Cloudflare Free) | $0 |
| **Cloudflare Pages** | $0 (Free) | $0 |
| **GPU Server** (اختیاری) | - | $200-500/mo |
| **جمع** | **$30-40/mo** | **$50-600/mo** |

### **📦 نرم‌افزارهای لازم:**

```bash
- Ubuntu 22.04 LTS (VPS)
- Docker 24.x
- Docker Compose 2.x
- Python 3.12
- Git
- curl, wget
```

---

## 4. راه‌اندازی VPS

### **Step 1: خرید و راه‌اندازی VPS**

**پیشنهاد سرویس‌ها:**
1. **Hetzner** (آلمان) - $30-50/mo
2. **DigitalOcean** (USA) - $40-80/mo
3. **Linode** (USA) - $40-80/mo
4. **Contabo** (آلمان) - $20-30/mo (ارزان اما کندتر)

**توصیه:** Hetzner (قیمت/کیفیت عالی)

### **Step 2: اتصال به VPS**

```bash
# اتصال SSH
ssh root@YOUR_VPS_IP

# بروزرسانی سیستم
apt update && apt upgrade -y

# نصب ابزارهای ضروری
apt install -y curl wget git vim htop net-tools ufw
```

### **Step 3: تنظیم Firewall**

```bash
# فعال‌سازی UFW
ufw default deny incoming
ufw default allow outgoing

# اجازه SSH
ufw allow 22/tcp

# اجازه HTTP/HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# فعال‌سازی
ufw enable
ufw status
```

### **Step 4: نصب Docker**

```bash
# نصب Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# اضافه کردن user به گروه docker
usermod -aG docker $USER

# نصب Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# بررسی نصب
docker --version
docker-compose --version
```

### **Step 5: ساخت User اختصاصی**

```bash
# ساخت user
adduser securedredlab

# اضافه کردن به گروه sudo و docker
usermod -aG sudo securedredlab
usermod -aG docker securedredlab

# تغییر به user جدید
su - securedredlab
```

---

## 5. نصب Backend

### **Step 1: Clone کردن کد**

```bash
# انتقال کد از Sandbox به VPS
# روش 1: از طریق Git (پیشنهادی)
git clone https://github.com/YOUR_USERNAME/SecureRedLab.git
cd SecureRedLab/backend

# روش 2: از طریق SCP (اگر Git ندارید)
# از local machine:
scp -r ./SecureRedLab securedredlab@YOUR_VPS_IP:~/
```

### **Step 2: تنظیم Environment Variables**

```bash
# کپی .env.example
cp .env.example .env

# ویرایش .env
nano .env
```

**محتوای `.env`:**
```bash
# Database
DATABASE_URL=postgresql://securedb:STRONG_PASSWORD@postgres:5432/securedb
POSTGRES_USER=securedb
POSTGRES_PASSWORD=STRONG_PASSWORD_HERE
POSTGRES_DB=securedb

# Redis
REDIS_URL=redis://redis:6379/0

# FastAPI
SECRET_KEY=GENERATE_RANDOM_SECRET_KEY_HERE
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Celery
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# AI Models
VLLM_BASE_URL=http://localhost:8001
AI_MODELS_PATH=/app/models

# CORS
ALLOWED_ORIGINS=https://your-frontend.pages.dev,http://localhost:3000
```

**تولید SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### **Step 3: Build Docker Images**

```bash
# Build backend image
docker build -t securedredlab-backend:latest .
```

---

## 6. نصب Docker Services

### **Step 1: راه‌اندازی Docker Compose**

```bash
# شروع تمام services
docker-compose up -d

# بررسی وضعیت
docker-compose ps

# بررسی logs
docker-compose logs -f
```

### **Step 2: راه‌اندازی Database**

```bash
# اجرای migrations
docker-compose exec fastapi alembic upgrade head

# ساخت admin user
docker-compose exec fastapi python -c "
from app.core.auth_system import AuthSystem
auth = AuthSystem()
user = auth.create_user('admin', 'admin@securedredlab.com', 'STRONG_PASSWORD')
print(f'Admin user created: {user}')
"
```

### **Step 3: بررسی سلامت Services**

```bash
# FastAPI Health Check
curl http://localhost:8000/health

# Celery Workers
docker-compose exec celery_worker_execution celery -A app.tasks.celery_app inspect active

# PostgreSQL
docker-compose exec postgres psql -U securedb -c "SELECT 1;"

# Redis
docker-compose exec redis redis-cli PING
```

---

## 7. راه‌اندازی Frontend

### **Step 1: تنظیم Cloudflare Pages**

1. ورود به Cloudflare Dashboard
2. رفتن به `Pages` > `Create a project`
3. اتصال به GitHub repository
4. تنظیمات Build:
   ```
   Build command: npm run build
   Build output directory: dist
   Root directory: frontend
   ```

### **Step 2: تنظیم Environment Variables (Cloudflare)**

```bash
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
```

### **Step 3: تنظیم Custom Domain**

1. در Cloudflare Pages > `Custom domains`
2. اضافه کردن `yourdomain.com`
3. تنظیم DNS Records:
   ```
   Type: CNAME
   Name: @
   Content: your-project.pages.dev
   Proxy: Enabled (Orange Cloud)
   ```

---

## 8. تنظیمات امنیتی

### **🔒 لیست امنیتی:**

#### **1. تنظیم SSL/TLS**

```bash
# نصب Certbot
apt install certbot python3-certbot-nginx

# دریافت SSL Certificate
certbot certonly --standalone -d api.yourdomain.com

# Auto-renewal
certbot renew --dry-run
```

#### **2. تنظیم Nginx Reverse Proxy**

```bash
# نصب Nginx
apt install nginx

# تنظیم config
nano /etc/nginx/sites-available/securedredlab
```

**محتوای Config:**
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

```bash
# فعال‌سازی
ln -s /etc/nginx/sites-available/securedredlab /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

#### **3. تنظیم Rate Limiting**

در `app/main.py`:
```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

@app.post("/api/v1/attacks")
@limiter.limit("5/minute")
async def create_attack(request: Request, ...):
    ...
```

#### **4. تنظیم Fail2Ban**

```bash
# نصب Fail2Ban
apt install fail2ban

# تنظیم jail
nano /etc/fail2ban/jail.local
```

```ini
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5

[sshd]
enabled = true
```

```bash
# شروع Fail2Ban
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 9. Troubleshooting

### **❌ مشکل: Backend راه‌اندازی نمی‌شود**

```bash
# بررسی logs
docker-compose logs fastapi

# بررسی environment variables
docker-compose exec fastapi env | grep DATABASE_URL

# Restart
docker-compose restart fastapi
```

### **❌ مشکل: Database اتصال ندارد**

```bash
# بررسی PostgreSQL
docker-compose exec postgres psql -U securedb

# بررسی connection string
echo $DATABASE_URL

# Restart
docker-compose restart postgres
```

### **❌ مشکل: Celery Worker کار نمی‌کند**

```bash
# بررسی logs
docker-compose logs celery_worker_execution

# بررسی Redis
docker-compose exec redis redis-cli PING

# Restart
docker-compose restart celery_worker_execution
```

### **❌ مشکل: Frontend به Backend متصل نمی‌شود**

1. بررسی CORS در `app/main.py`
2. بررسی `ALLOWED_ORIGINS` در `.env`
3. بررسی SSL Certificate
4. بررسی Nginx logs: `tail -f /var/log/nginx/error.log`

---

## 📞 پشتیبانی

**سوالات؟**
- GitHub Issues: `https://github.com/YOUR_USERNAME/SecureRedLab/issues`
- Email: `your-email@example.com`

---

## 🎉 پایان

**تبریک! سیستم SecureRedLab شما آماده است!** 🚀

**URLs:**
- Frontend: `https://yourdomain.com`
- Backend API: `https://api.yourdomain.com`
- Flower (Celery Monitor): `http://api.yourdomain.com:5555`

**Next Steps:**
1. ساخت اولین User از Dashboard
2. شروع اولین Scan
3. تست حملات در محیط ایمن (DVWA)

---

**ساخته شده با ❤️ توسط معلم سختگیر**
