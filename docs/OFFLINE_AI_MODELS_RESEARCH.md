# 🔬 OFFLINE AI MODELS RESEARCH (2025)
## تحقیق جامع برای مدل‌های Open-Source قابل Fine-tune

> **هدف**: یافتن بهترین مدل‌های **Open-Source Offline** که:
> - ✅ قابل Fine-tune باشند (LORA/QLORA)
> - ✅ به صورت Local اجرا شوند (Ollama/vLLM/HuggingFace)
> - ✅ برای Cybersecurity/Penetration Testing مناسب باشند
> - ✅ VRAM Requirements معقول داشته باشند (≤ 48GB)

---

## 📊 مقایسه جامع مدل‌های VLM (Vision Language Models)

### 🥇 بهترین مدل‌های VLM برای SecureRedLab

| Model | Size | VRAM (FP16) | VRAM (AWQ/GPTQ) | Fine-tuning | Deployment | Cybersecurity Strength |
|-------|------|-------------|-----------------|-------------|------------|------------------------|
| **Qwen2.5-VL-72B-AWQ** | 72B | 144GB | **36GB** | ✅ LORA/QLORA | vLLM, HF | 🟢 **BEST** - Visual Analysis, UI Vuln Detection |
| **Qwen2.5-VL-7B** | 7B | 14GB | **4GB** | ✅ LORA/QLORA | Ollama, vLLM | 🟢 Excellent - Lightweight, Fast Inference |
| **LLaVA-NeXT-34B** | 34B | 68GB | **17GB** | ✅ LORA/QLORA | vLLM, HF | 🟡 Good - General Purpose VLM |
| **LLaVA-1.6-13B** | 13B | 26GB | **7GB** | ✅ LORA/QLORA | Ollama, vLLM | 🟡 Good - Budget-Friendly |
| **InternVL2-8B** | 8B | 16GB | **4GB** | ✅ LORA/QLORA | HF | 🟡 Good - Chinese-Optimized |

### 🎯 **توصیه نهایی برای VLM:**
```yaml
Primary (Production):
  - Qwen2.5-VL-72B-AWQ  # 36GB VRAM, State-of-the-Art
  
Fallback (Lightweight):
  - Qwen2.5-VL-7B-AWQ   # 4GB VRAM, Fast & Accurate

Development (Local Testing):
  - LLaVA-1.6-13B-GGUF  # 7GB VRAM, Ollama-Compatible
```

---

## 🧠 مقایسه جامع مدل‌های LLM (Large Language Models)

### 🥇 بهترین مدل‌های LLM برای Payload/Code Generation

| Model | Size | VRAM (FP16) | VRAM (AWQ/GPTQ) | HumanEval | MBPP | Fine-tuning | Cybersecurity Strength |
|-------|------|-------------|-----------------|-----------|------|-------------|------------------------|
| **Qwen2.5-Coder-32B** | 32B | 64GB | **16GB** | 88.4% | 80.2% | ✅ LORA/QLORA | 🟢 **BEST** - Payload/Exploit Generation |
| **DeepSeek-Coder-V2-236B** | 236B | 472GB | **118GB** | 90.2% | 76.2% | ✅ LORA/QLORA | 🟢 Excellent - Complex Code Analysis |
| **DeepSeek-Coder-V2-16B** | 16B | 32GB | **8GB** | 81.1% | 72.0% | ✅ LORA/QLORA | 🟢 Good - Lightweight Alternative |
| **CodeLlama-70B** | 70B | 140GB | **35GB** | 67.8% | 63.0% | ✅ LORA/QLORA | 🟡 Moderate - General Coding |
| **Mixtral-8x22B** | 141B (MoE) | 282GB | **70GB** | 75.2% | 68.5% | ✅ LORA/QLORA | 🟢 Good - Multi-Task |
| **LLaMA-3.1-70B** | 70B | 140GB | **35GB** | 79.0% | 74.0% | ✅ LORA/QLORA | 🟡 Good - General Purpose |
| **Qwen2.5-72B** | 72B | 144GB | **36GB** | 85.5% | 80.0% | ✅ LORA/QLORA | 🟢 Excellent - Reasoning |

### 🎯 **توصیه نهایی برای LLM:**
```yaml
Primary (Payload Generation):
  - Qwen2.5-Coder-32B-AWQ  # 16GB VRAM, Best Coding Performance
  
Secondary (Code Analysis):
  - DeepSeek-Coder-V2-16B-GPTQ  # 8GB VRAM, Advanced Reasoning
  
Fallback (Lightweight):
  - Qwen2.5-Coder-7B-GGUF  # 4GB VRAM, Fast Inference

Complex Tasks (if VRAM available):
  - DeepSeek-Coder-V2-236B-AWQ  # 118GB VRAM, Ultimate Performance
```

---

## 🛠️ Fine-Tuning Methods (LORA vs QLORA)

### **LORA (Low-Rank Adaptation)**
```python
# Memory: ~20GB for 7B model
from peft import LoraConfig, get_peft_model

lora_config = LoraConfig(
    r=16,                    # Rank of update matrices
    lora_alpha=32,           # Scaling factor
    target_modules=["q_proj", "v_proj", "k_proj"],  # Which layers to fine-tune
    lora_dropout=0.1,
    bias="none"
)
```

### **QLORA (Quantized LORA)**
```python
# Memory: ~8GB for 7B model (50% reduction)
from transformers import BitsAndBytesConfig

bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
    bnb_4bit_compute_dtype=torch.bfloat16
)

# Then apply LORA on top
lora_config = LoraConfig(r=16, lora_alpha=32, ...)
```

### **مقایسه:**
| Method | VRAM (7B) | VRAM (70B) | Speed | Quality | Best For |
|--------|-----------|------------|-------|---------|----------|
| LORA | ~20GB | ~140GB | Fast | 100% | Production |
| QLORA | ~8GB | ~48GB | Moderate | 98% | **SecureRedLab (24GB GPU)** |

---

## 📦 Deployment Options (Ollama vs vLLM vs HuggingFace)

### **1. Ollama (Developer-Friendly, Simple)**
```bash
# Install
curl -fsSL https://ollama.com/install.sh | sh

# Run Qwen2.5-VL-7B
ollama pull qwen2.5-vl:7b

# Inference
ollama run qwen2.5-vl:7b "Analyze this screenshot for SQL injection vulnerabilities"
```

**✅ Pros:**
- Simple setup (1 command)
- Auto-downloads models
- Built-in quantization (GGUF)

**❌ Cons:**
- Limited fine-tuning support
- Slower than vLLM for batch processing

---

### **2. vLLM (Production, High-Performance)**
```bash
# Install
pip install vllm

# Run Qwen2.5-Coder-32B-AWQ
python -m vllm.entrypoints.openai.api_server \
  --model Qwen/Qwen2.5-Coder-32B-Instruct-AWQ \
  --quantization awq \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.9
```

**✅ Pros:**
- **10x faster inference** (PagedAttention)
- Supports AWQ/GPTQ quantization
- OpenAI-compatible API

**❌ Cons:**
- Complex setup
- Requires CUDA/GPU

---

### **3. HuggingFace Transformers (Research, Full Control)**
```python
from transformers import AutoModelForVision2Seq, AutoProcessor

# Load Qwen2.5-VL-7B
model = AutoModelForVision2Seq.from_pretrained(
    "Qwen/Qwen2.5-VL-7B-Instruct-AWQ",
    device_map="auto",
    trust_remote_code=True
)
processor = AutoProcessor.from_pretrained("Qwen/Qwen2.5-VL-7B-Instruct-AWQ")

# Inference
output = model.generate(**inputs)
```

**✅ Pros:**
- Full fine-tuning control (LORA/QLORA)
- Research-grade features
- All models supported

**❌ Cons:**
- Slower inference (no optimization)
- Manual memory management

---

## 🎯 **توصیه نهایی برای SecureRedLab:**

```yaml
Architecture:
  Framework: vLLM (Production) + Ollama (Development)
  Fine-tuning: HuggingFace + QLORA (for budget GPUs)

Models (Primary):
  VLM:
    - Qwen2.5-VL-72B-AWQ (36GB) - Visual Analysis
    - Qwen2.5-VL-7B-AWQ (4GB) - Lightweight Fallback
  
  LLM:
    - Qwen2.5-Coder-32B-AWQ (16GB) - Payload Generation
    - DeepSeek-Coder-V2-16B-GPTQ (8GB) - Code Analysis

Hardware Requirements:
  Minimum: 1x RTX 4090 (24GB VRAM)
  Recommended: 2x RTX 4090 (48GB VRAM)
  Optimal: 1x A6000 (48GB VRAM)
```

---

## 🚀 Implementation Plan (Next Steps)

### **Phase 1: Setup Local Deployment**
```bash
# 1. Install vLLM
pip install vllm torch transformers

# 2. Download Models
huggingface-cli download Qwen/Qwen2.5-VL-72B-Instruct-AWQ --local-dir ./models/qwen2.5-vl-72b
huggingface-cli download Qwen/Qwen2.5-Coder-32B-Instruct-AWQ --local-dir ./models/qwen2.5-coder-32b

# 3. Test Inference
python test_vllm_inference.py
```

### **Phase 2: Fine-Tuning Pipeline**
```bash
# 1. Prepare Dataset (Cybersecurity-specific)
python prepare_dataset.py --input ./data/exploits.json --output ./data/train.json

# 2. Fine-tune with QLORA
python fine_tune_qlora.py \
  --model Qwen/Qwen2.5-Coder-32B-Instruct-AWQ \
  --dataset ./data/train.json \
  --output ./models/qwen2.5-coder-finetuned \
  --lora_r 16 \
  --batch_size 4
```

### **Phase 3: Integration with SecureRedLab**
- Replace `backend/ai_intelligence/core.py` with local model loading
- Update `AIModelType` enum to use local paths
- Add model versioning and A/B testing

---

## 📚 References

1. **Qwen2.5-VL-72B-AWQ**: https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct-AWQ
2. **Qwen2.5-Coder**: https://github.com/QwenLM/Qwen2.5-Coder
3. **DeepSeek-Coder-V2**: https://github.com/deepseek-ai/DeepSeek-Coder-V2
4. **vLLM Documentation**: https://docs.vllm.ai/
5. **QLORA Paper**: https://arxiv.org/abs/2305.14314
6. **LLaMA-Factory**: https://github.com/hiyouga/LLaMA-Factory
7. **Fine-tuning Qwen2-VL**: https://huggingface.co/learn/cookbook/en/fine_tuning_vlm_trl

---

## 🔥 **جمع‌بندی نهایی:**

### **چرا این مدل‌ها؟**
1. **Qwen2.5-VL-72B-AWQ**: تنها VLM که برای UI Vulnerability Detection بهینه شده
2. **Qwen2.5-Coder-32B**: بهترین عملکرد روی Coding Benchmarks (88.4% HumanEval)
3. **همه Offline هستند**: هیچ داده‌ای به سرور خارجی نمی‌فرستیم
4. **همه Fine-tunable هستند**: با QLORA روی 24GB GPU قابل تنظیم
5. **Production-Ready**: vLLM برای inference سریع، Ollama برای توسعه

### **هزینه VRAM (با Quantization):**
- Qwen2.5-VL-72B-AWQ: 36GB
- Qwen2.5-Coder-32B-AWQ: 16GB
- **Total**: 52GB (نیاز به 2x RTX 4090 یا 1x A6000)

### **مزایا نسبت به Online Models:**
- ❌ **قبلا**: DeepSeek/Claude/GPT-4 API → هزینه ماهانه $200+
- ✅ **الان**: Local Inference → هزینه یکبار $3000 (2x RTX 4090)
- ✅ **Fine-tuning**: قابلیت تنظیم با داده‌های خودمون
- ✅ **Privacy**: 100% داده‌ها Local هستن

---

**🎯 آماده برای مرحله بعد: Implementation + Fine-Tuning Setup؟**
