# 🚀 SecureRedLab Implementation Plan
## نقشه کامل پیاده‌سازی با تمام Sub-steps

> **هدف**: تبدیل SecureRedLab از Online API به **100% Offline Open-Source Architecture**
> **Timeline**: 6-8 Weeks (با تست کامل)
> **Hardware**: 2x RTX 4090 (48GB VRAM) یا 1x A6000 (48GB VRAM)

---

## 📋 Phase 1: Research & Planning ✅ **COMPLETED**

### Sub-steps:
- [x] 1.1: تحقیق مدل‌های VLM (Qwen2.5-VL, LLaVA, InternVL)
- [x] 1.2: تحقیق مدل‌های LLM (Qwen2.5-Coder, DeepSeek-Coder, CodeLlama)
- [x] 1.3: مقایسه Benchmarks (HumanEval, MBPP, Visual Reasoning)
- [x] 1.4: تحقیق Fine-tuning Methods (LORA, QLORA, Full Fine-tune)
- [x] 1.5: تحقیق Deployment Tools (Ollama, vLLM, HuggingFace)
- [x] 1.6: تحقیق Quantization Methods (AWQ, GPTQ, GGUF)
- [x] 1.7: محاسبه VRAM Requirements
- [x] 1.8: ایجاد `OFFLINE_AI_MODELS_RESEARCH.md`

**Output**: `docs/OFFLINE_AI_MODELS_RESEARCH.md` (8.6KB)

**Key Decisions**:
- ✅ Primary VLM: **Qwen2.5-VL-72B-AWQ** (36GB VRAM)
- ✅ Primary LLM: **Qwen2.5-Coder-32B-AWQ** (16GB VRAM)
- ✅ Deployment: **vLLM** (Production) + **Ollama** (Development)
- ✅ Fine-tuning: **QLORA** (VRAM-efficient)

---

## 🏗️ Phase 2: Offline-First Architecture Design 🔄 **IN PROGRESS**

### Sub-steps:
- [ ] 2.1: طراحی جدید `AIIntelligenceCore` برای Local Models
- [ ] 2.2: طراحی Model Registry (versioning, caching)
- [ ] 2.3: طراحی Fallback Strategy (Qwen72B → Qwen7B → Mock)
- [ ] 2.4: طراحی Fine-tuning Pipeline Architecture
- [ ] 2.5: طراحی Model Performance Monitoring
- [ ] 2.6: ایجاد Sequence Diagrams برای Model Loading
- [ ] 2.7: ایجاد API Contract Documents

**Timeline**: 3 days

**Deliverables**:
```
docs/
  ├── ARCHITECTURE_OFFLINE.md        # معماری جدید
  ├── MODEL_REGISTRY_DESIGN.md       # نحوه مدیریت مدل‌ها
  └── FINETUNING_PIPELINE.md         # Pipeline Fine-tuning
backend/ai_intelligence/
  ├── offline_core.py                # AIIntelligenceCore جدید
  ├── model_registry.py              # مدیریت مدل‌ها
  └── vllm_client.py                 # Client برای vLLM
```

**Key Decisions to Make**:
1. چطور مدل‌ها رو cache کنیم؟ (Redis? File system?)
2. چطور model versioning بزنیم؟ (Git? MLflow?)
3. چطور fallback strategy رو پیاده کنیم؟
4. چطور performance رو monitor کنیم؟ (Prometheus? Custom?)

---

## 📥 Phase 3: Model Download & Setup Scripts

### Sub-steps:
- [ ] 3.1: ایجاد `scripts/setup_models.sh`
  - [ ] 3.1.1: Check VRAM availability
  - [ ] 3.1.2: Install dependencies (vLLM, transformers, accelerate)
  - [ ] 3.1.3: Download Qwen2.5-VL-72B-AWQ (36GB)
  - [ ] 3.1.4: Download Qwen2.5-Coder-32B-AWQ (16GB)
  - [ ] 3.1.5: Download Qwen2.5-VL-7B-GGUF (fallback, 4GB)
  - [ ] 3.1.6: Verify model checksums
  - [ ] 3.1.7: Create model registry database

- [ ] 3.2: ایجاد `scripts/start_vllm_servers.sh`
  - [ ] 3.2.1: Start VLM server (port 8001)
  - [ ] 3.2.2: Start LLM server (port 8002)
  - [ ] 3.2.3: Health check endpoints
  - [ ] 3.2.4: Log to `/var/log/secureredlab/vllm.log`

- [ ] 3.3: ایجاد `scripts/test_models.py`
  - [ ] 3.3.1: Test VLM with sample image
  - [ ] 3.3.2: Test LLM with sample code
  - [ ] 3.3.3: Measure inference latency
  - [ ] 3.3.4: Generate benchmark report

- [ ] 3.4: ایجاد `docker-compose.yml` برای vLLM
  - [ ] 3.4.1: VLM container (GPU 0)
  - [ ] 3.4.2: LLM container (GPU 1)
  - [ ] 3.4.3: Redis container (model cache)
  - [ ] 3.4.4: Prometheus container (monitoring)

**Timeline**: 5 days (شامل download time)

**Deliverables**:
```
scripts/
  ├── setup_models.sh                # Download & setup
  ├── start_vllm_servers.sh          # Start inference servers
  ├── stop_vllm_servers.sh           # Stop servers
  └── test_models.py                 # Test & benchmark
docker/
  ├── docker-compose.vllm.yml        # vLLM deployment
  ├── Dockerfile.vllm                # vLLM image
  └── vllm.env                       # Environment variables
```

**Example `setup_models.sh`**:
```bash
#!/bin/bash

# Phase 3.1: Setup Models
echo "[Phase 3.1] Starting Model Setup..."

# 3.1.1: Check VRAM
echo "[3.1.1] Checking VRAM availability..."
nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1
if [ $(nvidia-smi --query-gpu=memory.total --format=csv,noheader | head -1 | sed 's/ MiB//') -lt 24000 ]; then
    echo "❌ ERROR: Need at least 24GB VRAM"
    exit 1
fi

# 3.1.2: Install dependencies
echo "[3.1.2] Installing dependencies..."
pip install vllm==0.4.0 transformers==4.40.0 accelerate torch

# 3.1.3: Download Qwen2.5-VL-72B-AWQ
echo "[3.1.3] Downloading Qwen2.5-VL-72B-AWQ (36GB)..."
huggingface-cli download Qwen/Qwen2.5-VL-72B-Instruct-AWQ --local-dir ./models/qwen2.5-vl-72b

# 3.1.4: Download Qwen2.5-Coder-32B-AWQ
echo "[3.1.4] Downloading Qwen2.5-Coder-32B-AWQ (16GB)..."
huggingface-cli download Qwen/Qwen2.5-Coder-32B-Instruct-AWQ --local-dir ./models/qwen2.5-coder-32b

# 3.1.5: Download fallback model
echo "[3.1.5] Downloading Qwen2.5-VL-7B (fallback, 4GB)..."
ollama pull qwen2.5-vl:7b

# 3.1.6: Verify checksums
echo "[3.1.6] Verifying model checksums..."
sha256sum -c models/checksums.txt

# 3.1.7: Create model registry
echo "[3.1.7] Creating model registry..."
sqlite3 models/registry.db < scripts/create_registry.sql

echo "✅ All models ready!"
```

---

## 🔌 Phase 4: Local Model Loading Implementation

### Sub-steps:
- [ ] 4.1: Refactor `backend/ai_intelligence/offline_core.py`
  - [ ] 4.1.1: Create `OfflineModelManager` class
  - [ ] 4.1.2: Implement model loading from disk
  - [ ] 4.1.3: Implement model caching (LRU cache)
  - [ ] 4.1.4: Implement fallback logic (72B → 7B → Mock)
  - [ ] 4.1.5: Add error handling & retries

- [ ] 4.2: Implement `backend/ai_intelligence/vllm_client.py`
  - [ ] 4.2.1: HTTP client for vLLM API
  - [ ] 4.2.2: Request/response serialization
  - [ ] 4.2.3: Connection pooling
  - [ ] 4.2.4: Timeout handling (30s default)
  - [ ] 4.2.5: Health check endpoint

- [ ] 4.3: Implement `backend/ai_intelligence/model_registry.py`
  - [ ] 4.3.1: Database schema (models, versions, metrics)
  - [ ] 4.3.2: CRUD operations
  - [ ] 4.3.3: Model versioning (v1, v2, ...)
  - [ ] 4.3.4: A/B testing support
  - [ ] 4.3.5: Performance tracking

- [ ] 4.4: Update `backend/ai_intelligence/core.py`
  - [ ] 4.4.1: Replace API calls with local inference
  - [ ] 4.4.2: Update `analyze_visual()` to use local VLM
  - [ ] 4.4.3: Update `analyze_code()` to use local LLM
  - [ ] 4.4.4: Update `generate_payload()` to use local LLM
  - [ ] 4.4.5: Update `generate_evasion()` to use local LLM

- [ ] 4.5: Write unit tests
  - [ ] 4.5.1: Test model loading
  - [ ] 4.5.2: Test fallback logic
  - [ ] 4.5.3: Test error handling
  - [ ] 4.5.4: Test caching
  - [ ] 4.5.5: Test performance (latency < 5s)

**Timeline**: 7 days

**Deliverables**:
```
backend/ai_intelligence/
  ├── offline_core.py                # ✅ Main AI Core (Offline)
  ├── vllm_client.py                 # ✅ vLLM HTTP Client
  ├── model_registry.py              # ✅ Model Management
  └── fallback_strategy.py           # ✅ Fallback Logic
tests/
  └── test_offline_ai_core.py        # ✅ Unit Tests
```

**Example `offline_core.py` (Skeleton)**:
```python
from typing import Optional
import httpx
from .model_registry import ModelRegistry

class OfflineModelManager:
    """Manages offline model loading and inference"""
    
    def __init__(self, registry_path: str = "./models/registry.db"):
        self.registry = ModelRegistry(registry_path)
        self.vllm_vlm_url = "http://localhost:8001/v1/completions"
        self.vllm_llm_url = "http://localhost:8002/v1/completions"
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze_visual(self, image_path: str, prompt: str) -> dict:
        """Analyze image using local VLM (Qwen2.5-VL-72B)"""
        try:
            # Try primary model (72B)
            response = await self._call_vllm(
                self.vllm_vlm_url,
                model="qwen2.5-vl-72b",
                prompt=prompt,
                images=[image_path]
            )
            return response
        except Exception as e:
            # Fallback to lightweight model (7B)
            return await self._fallback_analyze_visual(image_path, prompt)
    
    async def generate_payload(self, vuln_type: str, context: str) -> list:
        """Generate payloads using local LLM (Qwen2.5-Coder-32B)"""
        try:
            response = await self._call_vllm(
                self.vllm_llm_url,
                model="qwen2.5-coder-32b",
                prompt=f"Generate {vuln_type} payloads for: {context}"
            )
            return response["payloads"]
        except Exception as e:
            return await self._fallback_generate_payload(vuln_type, context)
```

---

## 🎓 Phase 5: Fine-tuning Pipeline (QLORA)

### Sub-steps:
- [ ] 5.1: Prepare training dataset
  - [ ] 5.1.1: Collect cybersecurity exploits (1000+ samples)
  - [ ] 5.1.2: Create dataset format (Alpaca/ShareGPT)
  - [ ] 5.1.3: Split train/val/test (80/10/10)
  - [ ] 5.1.4: Upload to `/data/finetuning/`

- [ ] 5.2: Setup fine-tuning environment
  - [ ] 5.2.1: Install dependencies (peft, bitsandbytes, trl)
  - [ ] 5.2.2: Configure QLORA (r=16, alpha=32, 4-bit)
  - [ ] 5.2.3: Setup training script
  - [ ] 5.2.4: Configure hyperparameters

- [ ] 5.3: Fine-tune VLM (Qwen2.5-VL-7B)
  - [ ] 5.3.1: Load base model with 4-bit quantization
  - [ ] 5.3.2: Apply LORA adapters
  - [ ] 5.3.3: Train for 3 epochs (~6 hours)
  - [ ] 5.3.4: Evaluate on validation set
  - [ ] 5.3.5: Save adapter weights

- [ ] 5.4: Fine-tune LLM (Qwen2.5-Coder-32B)
  - [ ] 5.4.1: Load base model with 4-bit quantization
  - [ ] 5.4.2: Apply LORA adapters
  - [ ] 5.4.3: Train for 3 epochs (~8 hours)
  - [ ] 5.4.4: Evaluate on validation set
  - [ ] 5.4.5: Save adapter weights

- [ ] 5.5: Merge adapters & Export
  - [ ] 5.5.1: Merge LORA with base model
  - [ ] 5.5.2: Quantize to AWQ/GPTQ
  - [ ] 5.5.3: Upload to model registry
  - [ ] 5.5.4: Create version tag (v1.0-finetuned)

**Timeline**: 10 days (شامل data collection)

**Deliverables**:
```
data/finetuning/
  ├── train.json                     # Training data
  ├── val.json                       # Validation data
  └── test.json                      # Test data
scripts/finetuning/
  ├── prepare_dataset.py             # Data preparation
  ├── finetune_vlm_qlora.py          # VLM fine-tuning
  ├── finetune_llm_qlora.py          # LLM fine-tuning
  └── merge_adapters.py              # Merge & export
models/finetuned/
  ├── qwen2.5-vl-7b-v1.0/            # Fine-tuned VLM
  └── qwen2.5-coder-32b-v1.0/        # Fine-tuned LLM
```

**Example Training Script**:
```python
from peft import LoraConfig, get_peft_model
from transformers import AutoModelForCausalLM, BitsAndBytesConfig
import torch

# QLORA Config
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# Load model in 4-bit
model = AutoModelForCausalLM.from_pretrained(
    "Qwen/Qwen2.5-Coder-32B-Instruct-AWQ",
    quantization_config=bnb_config,
    device_map="auto"
)

# Apply LORA
lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj", "v_proj", "k_proj", "o_proj"],
    lora_dropout=0.1,
    bias="none",
    task_type="CAUSAL_LM"
)
model = get_peft_model(model, lora_config)

# Train
trainer.train()
```

---

## 🧪 Phase 6: Testing & Validation

### Sub-steps:
- [ ] 6.1: Unit tests
  - [ ] 6.1.1: Test model loading (< 10s)
  - [ ] 6.1.2: Test inference latency (VLM < 5s, LLM < 3s)
  - [ ] 6.1.3: Test fallback logic
  - [ ] 6.1.4: Test error handling
  - [ ] 6.1.5: Test caching (cache hit rate > 80%)

- [ ] 6.2: Integration tests
  - [ ] 6.2.1: Test end-to-end workflow (scan → analyze → exploit)
  - [ ] 6.2.2: Test with real targets (DVWA, Juice Shop)
  - [ ] 6.2.3: Test with SQLMap/Metasploit integration
  - [ ] 6.2.4: Test RL Engine integration

- [ ] 6.3: Performance benchmarks
  - [ ] 6.3.1: Measure inference throughput (req/s)
  - [ ] 6.3.2: Measure memory usage (VRAM < 48GB)
  - [ ] 6.3.3: Measure accuracy (vs baseline)
  - [ ] 6.3.4: Compare with Online Models (GPT-4, Claude)

- [ ] 6.4: Security tests
  - [ ] 6.4.1: Test data privacy (no external API calls)
  - [ ] 6.4.2: Test model robustness (adversarial inputs)
  - [ ] 6.4.3: Test prompt injection attacks
  - [ ] 6.4.4: Test output validation

**Timeline**: 5 days

**Deliverables**:
```
tests/
  ├── test_unit/
  │   ├── test_model_loading.py
  │   ├── test_inference.py
  │   └── test_fallback.py
  ├── test_integration/
  │   ├── test_end_to_end.py
  │   └── test_rl_integration.py
  └── test_performance/
      ├── benchmark_latency.py
      └── benchmark_accuracy.py
docs/
  ├── TEST_REPORT.md                 # نتایج تست
  └── BENCHMARK_RESULTS.md           # نتایج benchmark
```

---

## 📊 Timeline Summary

| Phase | Duration | Dependencies | Status |
|-------|----------|--------------|--------|
| Phase 1: Research | 3 days | - | ✅ Completed |
| Phase 2: Architecture | 3 days | Phase 1 | 🔄 In Progress |
| Phase 3: Model Setup | 5 days | Phase 2 | ⏳ Pending |
| Phase 4: Implementation | 7 days | Phase 3 | ⏳ Pending |
| Phase 5: Fine-tuning | 10 days | Phase 4 | ⏳ Pending |
| Phase 6: Testing | 5 days | Phase 5 | ⏳ Pending |
| **Total** | **33 days (6-7 weeks)** | - | - |

---

## 💰 Hardware & Cost Requirements

### **Minimum Setup (Budget)**
```
Hardware:
  - 1x RTX 4090 (24GB VRAM) - $1,600
  - 64GB RAM - $200
  - 2TB NVMe SSD - $150
  Total: ~$2,000

Limitations:
  - Only one model at a time
  - Slower inference
  - No parallel processing
```

### **Recommended Setup (SecureRedLab)**
```
Hardware:
  - 2x RTX 4090 (48GB VRAM) - $3,200
  - 128GB RAM - $400
  - 4TB NVMe SSD - $300
  Total: ~$4,000

Benefits:
  - VLM + LLM simultaneously
  - Fast inference (10+ req/s)
  - Parallel fine-tuning
```

### **Optimal Setup (Production)**
```
Hardware:
  - 1x A6000 (48GB VRAM) - $4,500
  - 256GB RAM - $800
  - 8TB NVMe SSD - $600
  Total: ~$6,000

Benefits:
  - ECC memory (stability)
  - 24/7 operation
  - Enterprise support
```

---

## ✅ Success Criteria

1. **✅ Offline Operation**: هیچ API call خارجی نداشته باشیم
2. **✅ Fine-tunable**: بتونیم با QLORA مدل‌ها رو tune کنیم
3. **✅ Performance**: Latency < 5s برای VLM, < 3s برای LLM
4. **✅ Accuracy**: Accuracy >= 85% روی benchmark داده‌های cybersecurity
5. **✅ VRAM**: استفاده از VRAM <= 48GB
6. **✅ Reliability**: Uptime > 99% با fallback strategy

---

## 🚨 Risks & Mitigation

### **Risk 1: Model Download Failures**
- **Mitigation**: Use `huggingface-cli` with resume support, backup mirrors

### **Risk 2: VRAM Overflow**
- **Mitigation**: Implement dynamic batch sizing, fallback to smaller models

### **Risk 3: Fine-tuning Quality**
- **Mitigation**: Use diverse training data (1000+ samples), multiple epochs

### **Risk 4: Inference Latency**
- **Mitigation**: Use vLLM optimizations (PagedAttention), caching

---

## 📞 Next Steps (برای User)

### **Option A: شروع Phase 2 (Architecture Design)** ✅ **RECOMMENDED**
- طراحی `OfflineModelManager`
- طراحی Model Registry
- طراحی Fallback Strategy

### **Option B: شروع Phase 3 (Model Setup)**
- اگر VPS آماده است و می‌خواهیم مدل‌ها رو download کنیم

### **Option C: جزئیات بیشتر**
- اگر سوال یا نیاز به توضیح بیشتر داری

**چه option رو انتخاب می‌کنی؟** 🎯
