# 🎯 Plan C: نقشه‌ی جامع و دقیق هیبریدسازی SecureRedLab
## **مرحله‌بندی کامل با توجه به کدهای موجود**

تاریخ: 2025-12-21
وضعیت فعلی: ~95% کد آماده، آماده برای Migration به VPS

---

## 📊 بخش 1: تحلیل وضعیت فعلی

### **1.1. فایل‌های موجود و قابل استفاده (✅ = آماده)**

#### **Core Modules (100% آماده)**
```
core/
├── ✅ logging_system.py           (~800 خط) - استفاده مستقیم
├── ✅ exception_handler.py        (~700 خط) - استفاده مستقیم
├── ✅ config_manager.py           (~600 خط) - استفاده مستقیم
├── ✅ database_manager.py         (~900 خط) - استفاده مستقیم
├── ✅ auth_system.py              (~400 خط) - استفاده مستقیم
├── ✅ support_verification.py    (~600 خط) - استفاده مستقیم
├── ✅ bot_power_controller.py    (~700 خط) - استفاده مستقیم
├── ✅ ai_output_validator.py     (~800 خط) - استفاده مستقیم
├── ✅ rl_engine.py                (~1,700 خط) - استفاده مستقیم
├── 🟡 neural_vuln_scanner.py     (~1,300 خط) - نیاز به تغییرات جزئی
└── 🔴 ai_core_engine.py          (~1,500 خط) - DEPRECATED (جایگزین با offline_core)
```

#### **AI Modules (100% آماده)**
```
ai/
├── ✅ offline_core.py             (~1,200 خط) - استفاده مستقیم
├── ✅ vllm_client.py              (~500 خط) - استفاده مستقیم
├── ✅ dual_track_router.py        (~400 خط) - استفاده مستقیم
├── ✅ anti_hallucination.py       (~400 خط) - استفاده مستقیم
├── ✅ vlm_core.py                 (~700 خط) - استفاده مستقیم
├── ✅ vlm_client.py               (~400 خط) - استفاده مستقیم
├── ✅ vlm_router.py               (~300 خط) - استفاده مستقیم
├── ✅ ocr_fallback.py             (~300 خط) - استفاده مستقیم
├── ✅ vlm_hallucination.py        (~250 خط) - استفاده مستقیم
└── ✅ scanner_ai_adapter.py       (~200 خط) - استفاده مستقیم
```

#### **Tests (100% آماده)**
```
tests/
├── ✅ test_rl_engine.py           (~400 خط) - استفاده مستقیم
├── ✅ test_vlm_core.py            (~450 خط) - استفاده مستقیم
├── ✅ test_ai_validator.py        (~300 خط) - استفاده مستقیم
├── ✅ test_scanner_integration.py (~350 خط) - استفاده مستقیم
├── ✅ test_end_to_end.py          (~365 خط) - استفاده مستقیم
└── 🔴 test_neural_scanner.py     (~250 خط) - نیاز به تغییرات
```

#### **Simulations (50% آماده - نیاز به بازسازی)**
```
simulations/
├── 🟡 ddos/ddos_simulator.py      (~1,400 خط) - نیاز به refactor
├── 🟡 shell_upload/shell_penetration.py (~1,500 خط) - نیاز به refactor
└── 🟡 data_extraction/data_extractor.py (~1,300 خط) - نیاز به refactor
```

#### **Backend Skeleton (30% آماده)**
```
backend/
├── 🟡 main.py                     (~100 خط) - نیاز به توسعه
├── 🟡 api/routes/                 (خالی) - نیاز به ساخت
├── 🟡 execution/metasploit_wrapper.py (~50 خط) - نیاز به توسعه
└── 🟡 ai_intelligence/core.py     (~50 خط) - نیاز به توسعه
```

#### **Documentation (100% آماده)**
```
docs/
├── ✅ ARCHITECTURE_COMPARISON.md
├── ✅ HYBRID_SYSTEM_PLAN.md
├── ✅ RL_ENGINE_GUIDE.md
├── ✅ VLM_MODELS_RESEARCH_2025.md
└── ... (12 فایل مستندات)
```

### **1.2. آمار کلی**

| دسته | فایل‌ها | خطوط کد | وضعیت |
|------|---------|---------|--------|
| **Core Modules** | 11 | ~9,500 | ✅ 91% آماده |
| **AI Modules** | 10 | ~5,150 | ✅ 100% آماده |
| **Tests** | 8 | ~2,565 | ✅ 95% آماده |
| **Simulations** | 3 | ~4,200 | 🟡 50% آماده |
| **Backend** | 5 | ~200 | 🔴 30% آماده |
| **جمع کل** | **37** | **~21,615** | **~75% آماده** |

---

## 🗺️ بخش 2: نقشه‌ی کامل مراحل (10 Phases)

---

## **Phase 0: آماده‌سازی و تحلیل (1 روز)** 📋

**هدف:** تحلیل دقیق، برنامه‌ریزی، و آماده‌سازی

**زبان:** Markdown + Bash

### **زیرمراحل:**

#### **Phase 0.1: تحلیل فایل‌های موجود** ✅ (انجام شد)
- [x] لیست تمام فایل‌های Python
- [x] تحلیل وابستگی‌ها
- [x] شناسایی فایل‌های قابل استفاده
- [x] شناسایی فایل‌های نیازمند تغییر

#### **Phase 0.2: طراحی ساختار دایرکتوری جدید**
- [ ] طراحی ساختار `backend/`
- [ ] طراحی ساختار `deployment/`
- [ ] طراحی ساختار `docker/`
- [ ] مستندسازی تصمیمات

**خروجی:**
```
📄 docs/PLAN_C_DETAILED_ROADMAP.md      (این فایل)
📄 docs/DIRECTORY_STRUCTURE.md          (نیاز به ساخت)
📄 docs/MIGRATION_GUIDE.md              (نیاز به ساخت)
```

#### **Phase 0.3: ساخت Checklist اجرایی**
- [ ] Checklist Phase 1
- [ ] Checklist Phase 2
- [ ] ...
- [ ] Checklist Phase 10

**خروجی:**
```
📄 docs/IMPLEMENTATION_CHECKLIST.md     (نیاز به ساخت)
```

**زمان تخمینی:** 4-6 ساعت

---

## **Phase 1: Backend Core Setup (2 روز)** 🏗️

**هدف:** ساخت Backend FastAPI + Migration کد موجود

**زبان:** Python 3.12

### **ساختار دایرکتوری هدف:**

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # 🔴 NEW - FastAPI entry point
│   ├── config.py                  # 🔴 NEW - Pydantic settings
│   ├── dependencies.py            # 🔴 NEW - Dependency injection
│   │
│   ├── core/                      # ✅ COPY از ./core
│   │   ├── __init__.py
│   │   ├── logging_system.py      # ✅ کپی مستقیم
│   │   ├── exception_handler.py   # ✅ کپی مستقیم
│   │   ├── config_manager.py      # ✅ کپی مستقیم
│   │   ├── database_manager.py    # ✅ کپی مستقیم
│   │   ├── auth_system.py         # ✅ کپی مستقیم
│   │   ├── support_verification.py # ✅ کپی مستقیم
│   │   ├── bot_power_controller.py # ✅ کپی مستقیم
│   │   ├── ai_output_validator.py # ✅ کپی مستقیم
│   │   ├── rl_engine.py           # ✅ کپی مستقیم
│   │   └── neural_vuln_scanner.py # 🟡 کپی + تغییرات
│   │
│   ├── ai/                        # ✅ COPY از ./ai
│   │   ├── __init__.py
│   │   ├── offline_core.py        # ✅ کپی مستقیم
│   │   ├── vllm_client.py         # ✅ کپی مستقیم
│   │   ├── dual_track_router.py   # ✅ کپی مستقیم
│   │   ├── anti_hallucination.py  # ✅ کپی مستقیم
│   │   ├── vlm_core.py            # ✅ کپی مستقیم
│   │   ├── vlm_client.py          # ✅ کپی مستقیم
│   │   ├── vlm_router.py          # ✅ کپی مستقیم
│   │   ├── ocr_fallback.py        # ✅ کپی مستقیم
│   │   ├── vlm_hallucination.py   # ✅ کپی مستقیم
│   │   └── scanner_ai_adapter.py  # ✅ کپی مستقیم
│   │
│   ├── api/                       # 🔴 NEW - API Layer
│   │   ├── __init__.py
│   │   ├── router.py              # Main API router
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── endpoints/
│   │       │   ├── __init__.py
│   │       │   ├── auth.py        # POST /api/v1/auth/login
│   │       │   ├── scans.py       # GET/POST /api/v1/scans
│   │       │   ├── attacks.py     # GET/POST /api/v1/attacks
│   │       │   ├── rl.py          # GET/POST /api/v1/rl
│   │       │   ├── ai.py          # POST /api/v1/ai/generate
│   │       │   └── vlm.py         # POST /api/v1/vlm/process
│   │       └── websocket.py       # WebSocket /ws/scans/{id}
│   │
│   ├── schemas/                   # 🔴 NEW - Pydantic models
│   │   ├── __init__.py
│   │   ├── common.py              # Base schemas
│   │   ├── auth.py
│   │   ├── scan.py
│   │   ├── attack.py
│   │   ├── rl.py
│   │   └── ai.py
│   │
│   ├── models/                    # 🔴 NEW - SQLAlchemy models
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── scan.py
│   │   ├── attack.py
│   │   └── rl_episode.py
│   │
│   ├── services/                  # 🔴 NEW - Business logic
│   │   ├── __init__.py
│   │   ├── scan_service.py
│   │   ├── attack_service.py
│   │   ├── rl_service.py
│   │   └── ai_service.py
│   │
│   └── utils/                     # 🔴 NEW - Utilities
│       ├── __init__.py
│       ├── security.py
│       └── helpers.py
│
├── tests/                         # ✅ COPY از ./tests
│   ├── __init__.py
│   ├── conftest.py                # 🔴 NEW - pytest fixtures
│   ├── test_rl_engine.py          # ✅ کپی مستقیم
│   ├── test_vlm_core.py           # ✅ کپی مستقیم
│   ├── test_ai_validator.py       # ✅ کپی مستقیم
│   ├── test_scanner_integration.py # ✅ کپی مستقیم
│   ├── test_end_to_end.py         # ✅ کپی مستقیم
│   └── test_api/                  # 🔴 NEW - API tests
│       ├── __init__.py
│       ├── test_auth.py
│       ├── test_scans.py
│       └── test_attacks.py
│
├── alembic/                       # 🔴 NEW - Database migrations
│   ├── versions/
│   ├── env.py
│   └── script.py.mako
│
├── requirements.txt               # 🔴 NEW
├── requirements-dev.txt           # 🔴 NEW
├── Dockerfile                     # 🔴 NEW
├── .dockerignore                  # 🔴 NEW
├── pytest.ini                     # 🔴 NEW
└── README.md                      # 🔴 NEW
```

### **زیرمراحل:**

#### **Phase 1.1: ساخت ساختار Backend (2 ساعت)**
- [ ] ایجاد دایرکتوری‌ها
- [ ] ساخت `__init__.py` ها
- [ ] ساخت `main.py` (FastAPI app)
- [ ] ساخت `config.py` (Pydantic settings)
- [ ] ساخت `dependencies.py`

#### **Phase 1.2: Migration Core Modules (3 ساعت)**
- [ ] کپی `core/logging_system.py` → `backend/app/core/`
- [ ] کپی `core/exception_handler.py`
- [ ] کپی `core/config_manager.py`
- [ ] کپی `core/database_manager.py`
- [ ] کپی `core/auth_system.py`
- [ ] کپی `core/support_verification.py`
- [ ] کپی `core/bot_power_controller.py`
- [ ] کپی `core/ai_output_validator.py`
- [ ] کپی `core/rl_engine.py`
- [ ] کپی + تغییر `core/neural_vuln_scanner.py`

**تغییرات مورد نیاز:**
```python
# در neural_vuln_scanner.py
# قبل:
from core.ai_core_engine import get_ai_engine

# بعد:
from app.ai.scanner_ai_adapter import get_scanner_ai_engine
```

#### **Phase 1.3: Migration AI Modules (2 ساعت)**
- [ ] کپی تمام فایل‌های `ai/` → `backend/app/ai/`
- [ ] بررسی import ها
- [ ] تست import ها

#### **Phase 1.4: ساخت API Endpoints (4 ساعت)**
- [ ] ساخت `api/v1/endpoints/auth.py`
- [ ] ساخت `api/v1/endpoints/scans.py`
- [ ] ساخت `api/v1/endpoints/attacks.py`
- [ ] ساخت `api/v1/endpoints/rl.py`
- [ ] ساخت `api/v1/endpoints/ai.py`
- [ ] ساخت `api/v1/endpoints/vlm.py`

#### **Phase 1.5: ساخت Pydantic Schemas (2 ساعت)**
- [ ] ساخت `schemas/common.py`
- [ ] ساخت `schemas/auth.py`
- [ ] ساخت `schemas/scan.py`
- [ ] ساخت `schemas/attack.py`
- [ ] ساخت `schemas/rl.py`
- [ ] ساخت `schemas/ai.py`

#### **Phase 1.6: ساخت SQLAlchemy Models (2 ساعت)**
- [ ] ساخت `models/base.py`
- [ ] ساخت `models/user.py`
- [ ] ساخت `models/scan.py`
- [ ] ساخت `models/attack.py`
- [ ] ساخت `models/rl_episode.py`

#### **Phase 1.7: Migration Tests (1 ساعت)**
- [ ] کپی تمام فایل‌های `tests/` → `backend/tests/`
- [ ] ساخت `conftest.py`
- [ ] تست pytest

#### **Phase 1.8: ساخت Requirements (1 ساعت)**
- [ ] ساخت `requirements.txt`
- [ ] ساخت `requirements-dev.txt`
- [ ] ساخت `Dockerfile`
- [ ] ساخت `.dockerignore`

**زمان تخمینی:** 17 ساعت (2 روز)

---

## **Phase 2: Database Layer (1 روز)** 💾

**هدف:** راه‌اندازی PostgreSQL + Alembic Migrations

**زبان:** Python (SQLAlchemy + Alembic)

### **زیرمراحل:**

#### **Phase 2.1: تنظیم Alembic (1 ساعت)**
- [ ] نصب Alembic
- [ ] `alembic init alembic`
- [ ] تنظیم `alembic.ini`
- [ ] تنظیم `alembic/env.py`

#### **Phase 2.2: ساخت Migration اولیه (2 ساعت)**
```bash
alembic revision -m "initial schema"
```

**جداول:**
- [ ] `users` (احراز هویت)
- [ ] `approvals` (تأییدیه‌های چندمرجعی)
- [ ] `audit_trail` (تاریخچه تغییرات)

#### **Phase 2.3: ساخت RL Migrations (2 ساعت)**
```bash
alembic revision -m "rl engine tables"
```

**جداول:**
- [ ] `rl_experiences` (تجربیات RL)
- [ ] `rl_episodes` (Episode ها)
- [ ] `rl_models` (مدل‌های RL)
- [ ] `retraining_history` (تاریخچه بازآموزی)

#### **Phase 2.4: ساخت Scanner Migrations (2 ساعت)**
```bash
alembic revision -m "scanner tables"
```

**جداول:**
- [ ] `scan_results` (نتایج اسکن)
- [ ] `vulnerabilities` (آسیب‌پذیری‌ها)
- [ ] `ports` (پورت‌های اسکن شده)

#### **Phase 2.5: ساخت Attack Migrations (1 ساعت)**
```bash
alembic revision -m "attack execution tables"
```

**جداول:**
- [ ] `attack_executions` (اجرای حملات)
- [ ] `attack_results` (نتایج حملات)

#### **Phase 2.6: تست Migrations (1 ساعت)**
- [ ] `alembic upgrade head`
- [ ] بررسی Schema
- [ ] `alembic downgrade -1`
- [ ] `alembic upgrade head`

**زمان تخمینی:** 9 ساعت (1 روز)

---

## **Phase 3: Celery Task Queue (1 روز)** 🔄

**هدف:** راه‌اندازی Celery + Redis + Workers

**زبان:** Python (Celery)

### **ساختار:**

```
backend/app/tasks/
├── __init__.py
├── celery_app.py              # 🔴 NEW - Celery config
├── execution_tasks.py         # 🔴 NEW - Execution tasks
├── ai_tasks.py                # 🔴 NEW - AI tasks
├── rl_tasks.py                # 🔴 NEW - RL tasks
└── report_tasks.py            # 🔴 NEW - Report tasks
```

### **زیرمراحل:**

#### **Phase 3.1: تنظیم Celery (2 ساعت)**
- [ ] نصب Celery + Redis
- [ ] ساخت `celery_app.py`
- [ ] تنظیم Broker (Redis)
- [ ] تنظیم Result Backend (Redis)

#### **Phase 3.2: ساخت Execution Tasks (3 ساعت)**
```python
# tasks/execution_tasks.py

@celery_app.task(bind=True, max_retries=3)
def run_nmap_scan(self, target: str, ports: str) -> dict:
    """اجرای Nmap scan"""
    pass

@celery_app.task(bind=True, max_retries=3)
def run_metasploit_exploit(self, module: str, target: str) -> dict:
    """اجرای Metasploit exploit"""
    pass
```

- [ ] `run_nmap_scan`
- [ ] `run_metasploit_exploit`
- [ ] `run_sqlmap_injection`
- [ ] `run_nuclei_scan`

#### **Phase 3.3: ساخت AI Tasks (2 ساعت)**
```python
# tasks/ai_tasks.py

@celery_app.task(bind=True)
def generate_with_llm(self, prompt: str, task_type: str) -> dict:
    """تولید با LLM"""
    pass

@celery_app.task(bind=True)
def process_with_vlm(self, image_path: str, task_type: str) -> dict:
    """پردازش با VLM"""
    pass
```

- [ ] `generate_with_llm`
- [ ] `process_with_vlm`
- [ ] `train_rl_agent`
- [ ] `validate_output`

#### **Phase 3.4: ساخت Report Tasks (1 ساعت)**
- [ ] `generate_pdf_report`
- [ ] `generate_html_report`
- [ ] `aggregate_scan_results`

#### **Phase 3.5: تنظیم Task Routing (1 ساعت)**
```python
# celery_app.py

task_routes = {
    'app.tasks.execution_tasks.*': {'queue': 'execution'},
    'app.tasks.ai_tasks.*': {'queue': 'ai'},
    'app.tasks.rl_tasks.*': {'queue': 'rl'},
    'app.tasks.report_tasks.*': {'queue': 'reports'},
}
```

#### **Phase 3.6: تست Celery (1 ساعت)**
- [ ] شروع Celery Worker
- [ ] تست Task Submission
- [ ] بررسی Result Backend

**زمان تخمینی:** 10 ساعت (1 روز)

---

## **Phase 4: Execution Layer - Part 1 (2 روز)** ⚠️

**⚠️ توجه:** در این مرحله **فقط ساختار و Mock** می‌سازیم. **تحقیق ابزارها بعداً.**

**هدف:** ساخت BaseExecutor + Mock Executors

**زبان:** Python (Docker SDK)

### **ساختار:**

```
backend/app/execution/
├── __init__.py
├── base_executor.py           # 🔴 NEW - Abstract base
├── docker_manager.py          # 🔴 NEW - Docker helper
├── nmap_executor.py           # 🔴 NEW - Mock
├── metasploit_executor.py     # 🔴 NEW - Mock
├── sqlmap_executor.py         # 🔴 NEW - Mock
└── nuclei_executor.py         # 🔴 NEW - Mock
```

### **زیرمراحل:**

#### **Phase 4.1: ساخت BaseExecutor (4 ساعت)**
```python
# execution/base_executor.py

from abc import ABC, abstractmethod
import docker

class BaseExecutor(ABC):
    """کلاس پایه برای تمام Executor ها"""
    
    def __init__(self):
        self.docker_client = docker.from_env()
        self.logger = ...
    
    @abstractmethod
    async def execute(self, **kwargs) -> dict:
        """اجرای command"""
        pass
    
    async def _run_container(self, image, command, timeout=300):
        """اجرا در Docker Container"""
        # TODO: پیاده‌سازی کامل در Phase 7
        pass
    
    @abstractmethod
    def parse_output(self, raw_output: dict) -> dict:
        """Parse خروجی"""
        pass
```

- [ ] ساخت Abstract Methods
- [ ] ساخت `_run_container` (Mock)
- [ ] ساخت Timeout Logic
- [ ] ساخت Kill Switch
- [ ] ساخت Error Handling

#### **Phase 4.2: ساخت Docker Manager (2 ساعت)**
```python
# execution/docker_manager.py

class DockerManager:
    """مدیریت Docker Containers"""
    
    def __init__(self):
        self.client = docker.from_env()
    
    def create_network(self, name: str):
        """ساخت isolated network"""
        pass
    
    def start_container(self, image, command, network):
        """شروع container"""
        pass
    
    def stop_container(self, container_id):
        """توقف container"""
        pass
    
    def kill_container(self, container_id):
        """Kill container"""
        pass
```

- [ ] ساخت Network Manager
- [ ] ساخت Container Lifecycle
- [ ] ساخت Resource Limits

#### **Phase 4.3: ساخت Mock Executors (6 ساعت)**

**هر Executor شامل:**
- [ ] `execute()` method (Mock response)
- [ ] `parse_output()` method (Mock parsing)
- [ ] Unit Tests

**Mock Response Example:**
```python
# nmap_executor.py

class NmapExecutor(BaseExecutor):
    async def execute(self, target, ports):
        # TODO: پیاده‌سازی واقعی در Phase 7
        return {
            'status': 'success',
            'target': target,
            'open_ports': [22, 80, 443],  # Mock data
            'os_detection': 'Linux 5.x',  # Mock data
        }
```

**Executors:**
1. [ ] `NmapExecutor` (Mock)
2. [ ] `MetasploitExecutor` (Mock)
3. [ ] `SQLMapExecutor` (Mock)
4. [ ] `NucleiExecutor` (Mock)

#### **Phase 4.4: تست Mock Executors (2 ساعت)**
- [ ] تست `NmapExecutor`
- [ ] تست `MetasploitExecutor`
- [ ] تست `SQLMapExecutor`
- [ ] تست `NucleiExecutor`

**زمان تخمینی:** 14 ساعت (2 روز)

---

## **Phase 5: Docker Compose Setup (1 روز)** 🐳

**هدف:** ساخت `docker-compose.yml` کامل

**زبان:** YAML + Dockerfile

### **زیرمراحل:**

#### **Phase 5.1: ساخت Dockerfile ها (3 ساعت)**

**1. Backend Dockerfile:**
```dockerfile
# backend/Dockerfile

FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**2. Nmap Dockerfile:**
```dockerfile
# docker/nmap/Dockerfile

FROM alpine:latest

RUN apk add --no-cache nmap nmap-scripts

CMD ["tail", "-f", "/dev/null"]
```

- [ ] Backend Dockerfile
- [ ] Nmap Dockerfile
- [ ] Nuclei Dockerfile (optional)

#### **Phase 5.2: ساخت docker-compose.yml (4 ساعت)**

```yaml
version: '3.8'

services:
  # Infrastructure
  postgres: ...
  redis: ...
  
  # Backend
  fastapi: ...
  
  # Celery Workers
  celery_worker_execution: ...
  celery_worker_ai: ...
  celery_flower: ...
  
  # Execution Containers (با Mock)
  metasploit: ...
  nmap: ...
  sqlmap: ...
  nuclei: ...
  
  # Target Environments (بعداً)
  # dvwa: ...
  # bwapp: ...

networks:
  backend_network:
    driver: bridge
  isolated_pentest:
    driver: bridge

volumes:
  postgres_data:
  redis_data:
  ai_models:
```

- [ ] Infrastructure Services
- [ ] Backend Services
- [ ] Celery Workers
- [ ] Execution Containers (Mock)
- [ ] Networks
- [ ] Volumes

#### **Phase 5.3: تنظیم Environment Variables (1 ساعت)**
```bash
# .env.example

DATABASE_URL=postgresql://...
REDIS_URL=redis://...
SECRET_KEY=...
```

- [ ] `.env.example`
- [ ] `.env.dev`
- [ ] `.env.prod` (template)

#### **Phase 5.4: تست Docker Compose (2 ساعت)**
```bash
docker-compose up -d
docker-compose ps
docker-compose logs
docker-compose down
```

**زمان تخمینی:** 10 ساعت (1 روز)

---

## **Phase 6: WebSocket Real-time (1 روز)** 🔴

**هدف:** پیاده‌سازی Real-time Updates

**زبان:** Python (FastAPI WebSocket)

### **زیرمراحل:**

#### **Phase 6.1: ساخت ConnectionManager (2 ساعت)**
```python
# api/v1/websocket.py

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
    
    async def connect(self, websocket, scan_id):
        ...
    
    async def send_progress(self, scan_id, message):
        ...
```

- [ ] ساخت Connection Pool
- [ ] ساخت Subscribe/Unsubscribe
- [ ] ساخت Broadcast

#### **Phase 6.2: تنظیم Redis Pub/Sub (2 ساعت)**
```python
# utils/pubsub.py

import aioredis

class RedisPubSub:
    async def publish(self, channel, message):
        ...
    
    async def subscribe(self, channel, callback):
        ...
```

- [ ] Redis Client
- [ ] Publish method
- [ ] Subscribe method

#### **Phase 6.3: ساخت WebSocket Endpoints (2 ساعت)**
```python
@router.websocket("/ws/scans/{scan_id}")
async def websocket_scan_updates(websocket, scan_id):
    await manager.connect(websocket, scan_id)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, scan_id)
```

- [ ] `/ws/scans/{scan_id}`
- [ ] `/ws/attacks/{attack_id}`
- [ ] `/ws/rl/{episode_id}`

#### **Phase 6.4: تست WebSocket (2 ساعت)**
- [ ] تست با wscat
- [ ] تست با Python client
- [ ] تست Multiple Connections

**زمان تخمینی:** 8 ساعت (1 روز)

---

## **Phase 7: Execution Layer - Part 2 (3 روز)** 🎯

**⚠️ در این مرحله تحقیق عمیق ابزارها انجام می‌شود.**

**هدف:** پیاده‌سازی واقعی Executors

**زبان:** Python + Docker + Bash

### **زیرمراحل:**

#### **Phase 7.1: تحقیق ابزار Nmap (0.5 روز)**
- [ ] تحقیق Nmap CLI options
- [ ] تحقیق XML output parsing
- [ ] تحقیق Docker image
- [ ] طراحی interface

#### **Phase 7.2: پیاده‌سازی NmapExecutor (1 روز)**
- [ ] پیاده‌سازی `execute()`
- [ ] پیاده‌سازی `parse_output()`
- [ ] تست واقعی با DVWA
- [ ] مستندسازی

#### **Phase 7.3: تحقیق ابزار Metasploit (0.5 روز)**
- [ ] تحقیق Metasploit RC scripts
- [ ] تحقیق msf modules
- [ ] تحقیق Docker image
- [ ] طراحی interface

#### **Phase 7.4: پیاده‌سازی MetasploitExecutor (1 روز)**
- [ ] پیاده‌سازی `execute()`
- [ ] پیاده‌سازی `parse_output()`
- [ ] تست واقعی با DVWA
- [ ] مستندسازی

#### **Phase 7.5: تحقیق ابزارهای دیگر (بقیه)**
- [ ] SQLMap
- [ ] Nuclei
- [ ] ... (به تدریج)

**⚠️ این Phase طولانی‌ترین مرحله است.**

**زمان تخمینی:** 24+ ساعت (3+ روز)

---

## **Phase 8: Frontend Integration (1 روز)** 🎨

**هدف:** اتصال Cloudflare Pages به VPS

**زبان:** TypeScript/JavaScript

### **زیرمراحل:**

#### **Phase 8.1: تغییر API Client (2 ساعت)**
```typescript
// src/config.ts
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  wsURL: import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws',
}
```

- [ ] تغییر base URL
- [ ] تنظیم Environment Variables
- [ ] تنظیم CORS

#### **Phase 8.2: ساخت WebSocket Client (2 ساعت)**
```typescript
// src/services/websocket.ts

class WebSocketClient {
  connect(scanId: string) {
    this.ws = new WebSocket(`${API_CONFIG.wsURL}/scans/${scanId}`)
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      this.onProgress(data)
    }
  }
}
```

- [ ] ساخت WebSocket wrapper
- [ ] ساخت Auto-reconnect
- [ ] ساخت Event Handlers

#### **Phase 8.3: تست Integration (2 ساعت)**
- [ ] تست Login
- [ ] تست Scan API
- [ ] تست WebSocket
- [ ] تست Error Handling

#### **Phase 8.4: Deploy به Cloudflare (2 ساعت)**
```bash
npm run build
wrangler pages deploy dist
```

- [ ] Build
- [ ] Deploy
- [ ] تست Production URL

**زمان تخمینی:** 8 ساعت (1 روز)

---

## **Phase 9: Testing & Debugging (2 روز)** 🐛

**هدف:** تست کامل سیستم

**زبان:** Python (pytest) + Bash

### **زیرمراحل:**

#### **Phase 9.1: Unit Tests (0.5 روز)**
- [ ] تست Core Modules
- [ ] تست AI Modules
- [ ] تست API Endpoints
- [ ] تست Executors

#### **Phase 9.2: Integration Tests (0.5 روز)**
- [ ] تست Database
- [ ] تست Celery
- [ ] تست WebSocket
- [ ] تست Docker

#### **Phase 9.3: E2E Tests (0.5 روز)**
- [ ] تست Full Scan Workflow
- [ ] تست Full Attack Workflow
- [ ] تست RL Workflow

#### **Phase 9.4: Bug Fixes (0.5 روز)**
- [ ] جمع‌آوری Bugs
- [ ] اولویت‌بندی
- [ ] فیکس کردن

**زمان تخمینی:** 16 ساعت (2 روز)

---

## **Phase 10: Documentation & Deployment (1 روز)** 📚

**هدف:** مستندسازی کامل + Production Deployment

**زبان:** Markdown + Bash

### **زیرمراحل:**

#### **Phase 10.1: مستندسازی (4 ساعت)**
- [ ] `docs/VPS_DEPLOYMENT_GUIDE.md`
- [ ] `docs/API_DOCUMENTATION.md`
- [ ] `docs/TROUBLESHOOTING.md`
- [ ] `docs/UPGRADE_GUIDE.md`

#### **Phase 10.2: Production Deployment (4 ساعت)**
- [ ] تنظیم VPS
- [ ] Deploy Docker Compose
- [ ] تنظیم SSL
- [ ] تنظیم Monitoring

**زمان تخمینی:** 8 ساعت (1 روز)

---

## 📊 بخش 3: خلاصه زمان‌بندی

| Phase | عنوان | زمان | وضعیت |
|-------|-------|------|--------|
| 0 | آماده‌سازی | 6h | 🔴 Not Started |
| 1 | Backend Core | 17h | 🔴 Not Started |
| 2 | Database | 9h | 🔴 Not Started |
| 3 | Celery | 10h | 🔴 Not Started |
| 4 | Execution Mock | 14h | 🔴 Not Started |
| 5 | Docker Compose | 10h | 🔴 Not Started |
| 6 | WebSocket | 8h | 🔴 Not Started |
| 7 | Execution Real | 24h+ | ⏸️ Pending Research |
| 8 | Frontend | 8h | 🔴 Not Started |
| 9 | Testing | 16h | 🔴 Not Started |
| 10 | Deployment | 8h | 🔴 Not Started |
| **جمع** | | **~130h** | **~16-18 روز** |

---

## 🎯 بخش 4: تصمیم نهایی - از کجا شروع کنیم؟

### **پیشنهاد من (معلم سختگیر):**

**شروع با Phase 1: Backend Core Setup** ✅

**چرا؟**
1. ✅ 95% کد آماده است - فقط کپی می‌کنیم
2. ✅ بدون Backend هیچ چیز کار نمی‌کند
3. ✅ می‌توانیم بلافاصله تست کنیم
4. ✅ می‌توانیم موازی کار کنیم (من کد، شما VPS)

### **Plan اجرایی:**

**امروز (روز 1):**
- من: Phase 1.1 + 1.2 می‌سازم (ساختار + Migration Core)
- شما: هیچ کاری نکنید، فقط نگاه کنید

**فردا (روز 2):**
- من: Phase 1.3 + 1.4 می‌سازم (AI Modules + API)
- شما: شروع به خرید/تنظیم VPS

**روز 3:**
- من: Phase 1.5 + 1.6 + 1.7 (Schemas + Models + Tests)
- شما: نصب Docker + PostgreSQL + Redis در VPS

**روز 4:**
- من: Phase 2 (Database Migrations)
- شما: تست اتصال به VPS

**روز 5+:**
- من: Phase 3, 4, 5, ...
- شما: همکاری در تست و Deploy

---

## 📝 بخش 5: چک‌لیست اجرایی Phase 1

### **Phase 1.1: ساخت ساختار Backend**

```bash
# Step 1: ساخت دایرکتوری‌ها
mkdir -p backend/app/{core,ai,api/v1/endpoints,schemas,models,services,tasks,execution,utils}
mkdir -p backend/tests/test_api
mkdir -p backend/alembic/versions

# Step 2: ساخت __init__.py ها
touch backend/app/__init__.py
touch backend/app/core/__init__.py
touch backend/app/ai/__init__.py
touch backend/app/api/__init__.py
touch backend/app/api/v1/__init__.py
touch backend/app/api/v1/endpoints/__init__.py
touch backend/app/schemas/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/tasks/__init__.py
touch backend/app/execution/__init__.py
touch backend/app/utils/__init__.py
touch backend/tests/__init__.py
touch backend/tests/test_api/__init__.py

# Step 3: کپی Core Modules
cp -r core/*.py backend/app/core/

# Step 4: کپی AI Modules
cp -r ai/*.py backend/app/ai/

# Step 5: کپی Tests
cp -r tests/*.py backend/tests/
```

- [ ] اجرا شد
- [ ] تست شد
- [ ] کامیت شد

---

## 🚀 آماده شروع؟

**داداش، الان چه کار کنیم؟**

**گزینه A:** بگو "شروع کن Phase 1.1" تا فوراً شروع کنم ✅

**گزینه B:** بگو "اول VPS setup کن" تا Phase 0 را بسازم

**گزینه C:** سوال دیگری داری؟

**من آماده‌ام! منتظر دستور تو هستم!** 🔥
