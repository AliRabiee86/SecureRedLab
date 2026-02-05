# راهنمای کامل مدل‌های AI در SecureRedLab
# Complete AI Models Guide for SecureRedLab

**نسخه:** 2.0.0  
**تاریخ:** 2025-12-03  
**بر اساس تحقیقات:** PwnGPT, PentestGPT, Latest Benchmarks

---

## 📊 **جدول کامل مدل‌ها (VLM + LLM)**

### **🖼️ Vision-Language Models (VLM)**

| Model | Size | Type | API/Local | Cost | Performance | Best For |
|-------|------|------|-----------|------|-------------|----------|
| **Qwen2.5-VL-72B** | 72B | VLM | ✅ Online API | $3-8/1M tokens | ⭐⭐⭐⭐⭐ | Best overall VLM |
| **Gemini 2.0 Flash** | Unknown | VLM | ✅ Online API | $0.075/1M tokens | ⭐⭐⭐⭐⭐ | Fastest, Cheapest |
| **Claude 3.5 Sonnet** | Unknown | VLM | ✅ Online API | $3/1M input | ⭐⭐⭐⭐⭐ | Code analysis |
| **GPT-4 Vision** | Unknown | VLM | ✅ Online API | $10/1M tokens | ⭐⭐⭐⭐ | General purpose |
| **LLaVA 1.6-34B** | 34B | VLM | 🏠 **Offline** | Free | ⭐⭐⭐⭐ | Privacy, Offline |
| **LLaVA 1.6-13B** | 13B | VLM | 🏠 **Offline** | Free | ⭐⭐⭐ | Resource-limited |
| **SmolVLM** | 2B | VLM | 🏠 **Offline** | Free | ⭐⭐ | Edge devices |

### **💬 Large Language Models (LLM)**

| Model | Size | Type | API/Local | Cost | Performance | Best For |
|-------|------|------|-----------|------|-------------|----------|
| **GLM-4.6** | 6B | LLM | ✅ Online API | $0.3-0.8/1M | ⭐⭐⭐⭐⭐ | **Best value!** |
| **DeepSeek Coder V2** | 236B MoE | LLM | ✅ Online API | $0.14/1M | ⭐⭐⭐⭐⭐ | Code/Exploit gen |
| **Qwen 2.5-72B** | 72B | LLM | ✅ Online + Local | $0.17-0.70/1M | ⭐⭐⭐⭐⭐ | General LLM |
| **Mixtral 8x22B** | 176B MoE | LLM | ✅ Online + Local | $0.9/1M | ⭐⭐⭐⭐ | Multi-expert |
| **LLaMA 3.1-70B** | 70B | LLM | 🏠 **Offline** | Free | ⭐⭐⭐⭐ | Open-source |
| **LLaMA 3.1-8B** | 8B | LLM | 🏠 **Offline** | Free | ⭐⭐⭐ | Resource-limited |

---

## 🌐 **آنلاین (Online API) vs 🏠 آفلاین (Offline Local)**

### **✅ Online API (توصیه برای Production)**

**مزایا:**
- ✅ بدون نیاز به GPU
- ✅ همیشه آخرین نسخه
- ✅ سرعت بالا (distributed infrastructure)
- ✅ هزینه پایین (pay-per-use)
- ✅ مقیاس‌پذیری بی‌نهایت

**معایب:**
- ❌ نیاز به اینترنت
- ❌ داده‌ها به سرور ارسال می‌شود (Privacy concern)
- ❌ محدودیت rate limit

**مدل‌های Online:**
```python
# VLM Models
- Qwen2.5-VL-72B: Alibaba Cloud DashScope API
- Gemini 2.0 Flash: Google AI Studio / Vertex AI
- Claude 3.5 Sonnet: Anthropic API
- GPT-4 Vision: OpenAI API

# LLM Models
- GLM-4.6: BigModel API (zhipuai)
- DeepSeek Coder V2: DeepSeek API
- Qwen 2.5-72B: Alibaba Cloud / HuggingFace
- Mixtral 8x22B: Mistral AI API
```

**نحوه دسترسی:**
```bash
# Qwen2.5-VL (Alibaba Cloud)
curl https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation \
  -H "Authorization: Bearer YOUR_API_KEY"

# GLM-4.6 (BigModel)
curl https://open.bigmodel.cn/api/paas/v4/chat/completions \
  -H "Authorization: Bearer YOUR_API_KEY"

# Gemini 2.0 Flash (Google)
curl https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent \
  -H "x-goog-api-key: YOUR_API_KEY"
```

---

### **🏠 Offline Local (توصیه برای Privacy/Research)**

**مزایا:**
- ✅ کنترل کامل بر داده‌ها (Privacy 100%)
- ✅ بدون محدودیت rate limit
- ✅ بدون هزینه API
- ✅ کار بدون اینترنت

**معایب:**
- ❌ نیاز به GPU قوی (VRAM بالا)
- ❌ هزینه سخت‌افزار بالا
- ❌ نگهداری و به‌روزرسانی
- ❌ سرعت کمتر (بسته به hardware)

**مدل‌های Offline:**
```python
# VLM Models (Offline)
- LLaVA 1.6-34B: 34B params, needs 48GB+ VRAM
- LLaVA 1.6-13B: 13B params, needs 16GB+ VRAM
- SmolVLM: 2B params, needs 4GB+ VRAM

# LLM Models (Offline)
- LLaMA 3.1-70B: needs 80GB+ VRAM (A100)
- LLaMA 3.1-8B: needs 12GB+ VRAM (RTX 3090)
- Qwen 2.5-7B: needs 10GB+ VRAM
```

**نحوه Deploy (Local):**
```bash
# با Ollama (ساده‌ترین راه)
ollama pull llava:34b-v1.6
ollama run llava:34b-v1.6

# با vLLM (Production)
vllm serve liuhaotian/llava-v1.6-34b \
  --trust-remote-code

# با Hugging Face Transformers
python -c "
from transformers import LlavaNextProcessor, LlavaNextForConditionalGeneration
model = LlavaNextForConditionalGeneration.from_pretrained('llava-hf/llava-v1.6-34b-hf')
"
```

---

## 💰 **مقایسه هزینه (Cost Comparison)**

### **Scenario: 1 Million Tokens Processing**

| Model | Type | Online Cost | Offline Cost (VRAM) |
|-------|------|-------------|---------------------|
| **Qwen2.5-VL-72B** | VLM | $3-8 | 80GB VRAM (~$10,000 GPU) |
| **Gemini 2.0 Flash** | VLM | $0.075 | ❌ Not available |
| **Claude 3.5 Sonnet** | VLM | $3 | ❌ Not available |
| **LLaVA 1.6-34B** | VLM | ❌ No API | 48GB VRAM (~$6,000 GPU) |
| **GLM-4.6** | LLM | $0.3-0.8 | ❌ Not available |
| **DeepSeek Coder V2** | LLM | $0.14 | ❌ Not available |
| **LLaMA 3.1-8B** | LLM | Free (via HF) | 12GB VRAM (~$1,000 GPU) |

**💡 نتیجه:**
- **Production → Online API** (هزینه کمتر، مقیاس‌پذیری بهتر)
- **Privacy/Research → Offline Local** (کنترل کامل، بدون اشتراک داده)

---

## 🎯 **پیشنهاد برای SecureRedLab**

### **✅ Strategy 1: Hybrid (توصیه می‌شود)**

```python
# Primary: Online APIs (برای production)
primary_vlm = "qwen_2_5_vl_72b"      # Alibaba Cloud API
primary_llm = "glm_4_6"               # BigModel API
code_specialist = "deepseek_coder_v2" # DeepSeek API

# Fallback: Offline Models (برای privacy/offline scenarios)
fallback_vlm = "llava_1_6_13b"       # Local Ollama
fallback_llm = "llama_3_1_8b"        # Local Ollama
```

**چرا Hybrid؟**
1. ✅ **99% استفاده:** Online APIs (سریع، ارزان، بدون GPU)
2. ✅ **1% استفاده:** Offline (برای test های حساس، بدون اینترنت)
3. ✅ **Flexibility:** می‌توان بین online/offline سوئیچ کرد
4. ✅ **Cost-effective:** فقط برای استفاده واقعی پول می‌دهیم

---

## 🚀 **پیاده‌سازی در SecureRedLab**

### **فایل جدید: `backend/ai_intelligence/model_config.py`**

```python
from enum import Enum
from typing import Dict, Optional
import os

class ModelDeployment(Enum):
    ONLINE_API = "online"
    OFFLINE_LOCAL = "offline"

class AIModelConfig:
    """
    پیکربندی مدل‌های AI
    """
    
    # VLM Models
    VLM_MODELS = {
        "qwen_2_5_vl_72b": {
            "deployment": ModelDeployment.ONLINE_API,
            "api_endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation",
            "api_key_env": "QWEN_API_KEY",
            "cost_per_1m_tokens": 5.0,  # Average $3-8
            "max_tokens": 8192,
            "supports_vision": True
        },
        "gemini_2_flash": {
            "deployment": ModelDeployment.ONLINE_API,
            "api_endpoint": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent",
            "api_key_env": "GEMINI_API_KEY",
            "cost_per_1m_tokens": 0.075,
            "max_tokens": 1000000,  # 1M context!
            "supports_vision": True
        },
        "claude_3_5_sonnet": {
            "deployment": ModelDeployment.ONLINE_API,
            "api_endpoint": "https://api.anthropic.com/v1/messages",
            "api_key_env": "CLAUDE_API_KEY",
            "cost_per_1m_tokens": 3.0,
            "max_tokens": 200000,
            "supports_vision": True
        },
        "llava_1_6_34b": {
            "deployment": ModelDeployment.OFFLINE_LOCAL,
            "model_path": "liuhaotian/llava-v1.6-34b",
            "ollama_name": "llava:34b-v1.6",
            "vram_required_gb": 48,
            "cost_per_1m_tokens": 0.0,
            "max_tokens": 4096,
            "supports_vision": True
        },
        "llava_1_6_13b": {
            "deployment": ModelDeployment.OFFLINE_LOCAL,
            "model_path": "liuhaotian/llava-v1.6-13b",
            "ollama_name": "llava:13b-v1.6",
            "vram_required_gb": 16,
            "cost_per_1m_tokens": 0.0,
            "max_tokens": 4096,
            "supports_vision": True
        }
    }
    
    # LLM Models
    LLM_MODELS = {
        "glm_4_6": {
            "deployment": ModelDeployment.ONLINE_API,
            "api_endpoint": "https://open.bigmodel.cn/api/paas/v4/chat/completions",
            "api_key_env": "GLM_API_KEY",
            "cost_per_1m_tokens": 0.55,  # Average $0.3-0.8
            "max_tokens": 128000,
            "supports_vision": False,
            "note": "Best value - 93.9% AIME vs Claude's 74.3%"
        },
        "deepseek_coder_v2": {
            "deployment": ModelDeployment.ONLINE_API,
            "api_endpoint": "https://api.deepseek.com/v1/chat/completions",
            "api_key_env": "DEEPSEEK_API_KEY",
            "cost_per_1m_tokens": 0.14,
            "max_tokens": 128000,
            "supports_vision": False
        },
        "qwen_2_5_72b": {
            "deployment": ModelDeployment.ONLINE_API,
            "api_endpoint": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            "api_key_env": "QWEN_API_KEY",
            "cost_per_1m_tokens": 0.44,  # Average $0.17-0.70
            "max_tokens": 131072,
            "supports_vision": False
        },
        "mixtral_8x22b": {
            "deployment": ModelDeployment.ONLINE_API,
            "api_endpoint": "https://api.mistral.ai/v1/chat/completions",
            "api_key_env": "MISTRAL_API_KEY",
            "cost_per_1m_tokens": 0.9,
            "max_tokens": 64000,
            "supports_vision": False
        },
        "llama_3_1_70b": {
            "deployment": ModelDeployment.OFFLINE_LOCAL,
            "model_path": "meta-llama/Llama-3.1-70B-Instruct",
            "ollama_name": "llama3.1:70b",
            "vram_required_gb": 80,
            "cost_per_1m_tokens": 0.0,
            "max_tokens": 128000,
            "supports_vision": False
        },
        "llama_3_1_8b": {
            "deployment": ModelDeployment.OFFLINE_LOCAL,
            "model_path": "meta-llama/Llama-3.1-8B-Instruct",
            "ollama_name": "llama3.1:8b",
            "vram_required_gb": 12,
            "cost_per_1m_tokens": 0.0,
            "max_tokens": 128000,
            "supports_vision": False
        }
    }
    
    @classmethod
    def get_model_config(cls, model_name: str) -> Optional[Dict]:
        """Get configuration for a specific model"""
        # Check VLM models
        if model_name in cls.VLM_MODELS:
            return cls.VLM_MODELS[model_name]
        # Check LLM models
        if model_name in cls.LLM_MODELS:
            return cls.LLM_MODELS[model_name]
        return None
    
    @classmethod
    def get_online_models(cls) -> Dict[str, Dict]:
        """Get all online API models"""
        online = {}
        for name, config in {**cls.VLM_MODELS, **cls.LLM_MODELS}.items():
            if config["deployment"] == ModelDeployment.ONLINE_API:
                online[name] = config
        return online
    
    @classmethod
    def get_offline_models(cls) -> Dict[str, Dict]:
        """Get all offline local models"""
        offline = {}
        for name, config in {**cls.VLM_MODELS, **cls.LLM_MODELS}.items():
            if config["deployment"] == ModelDeployment.OFFLINE_LOCAL:
                offline[name] = config
        return offline
```

---

## 📝 **Recommendation Table**

| Use Case | Recommended Models | Reason |
|----------|-------------------|--------|
| **Visual Analysis** | Qwen2.5-VL → Gemini 2.0 Flash | Best VLM, Fastest |
| **Code Analysis** | Claude 3.5 Sonnet → GLM-4.6 | Best for code |
| **Payload Generation** | GLM-4.6 → DeepSeek Coder V2 | Best value, Cheap |
| **Evasion Techniques** | DeepSeek Coder V2 → GLM-4.6 | Exploit specialist |
| **Offline/Privacy** | LLaVA 1.6-13B + LLaMA 3.1-8B | No GPU? Use 13B+8B |
| **Academic/Research** | Offline Models | Full control, No data sharing |

---

## 🔒 **Security & Privacy Notes**

### **Online APIs:**
- ⚠️ داده‌ها به servers ارسال می‌شود
- ✅ استفاده از HTTPS
- ✅ API keys باید encrypted باشند
- ⚠️ نباید sensitive data ارسال شود

### **Offline Models:**
- ✅ 100% Privacy
- ✅ No data leakage
- ✅ Perfect for academic research
- ❌ نیاز به GPU قوی

---

## 📊 **Benchmark Summary (2025)**

| Model | MMLU | HumanEval | MATH | Cost/1M |
|-------|------|-----------|------|---------|
| **GLM-4.6** | 85.5% | 75.2% | 93.9% AIME | $0.55 |
| **Claude 3.5 Sonnet** | 88.3% | 92.0% | 74.3% AIME | $3.00 |
| **DeepSeek Coder V2** | 78.9% | 90.2% | 75.7% | $0.14 |
| **Qwen2.5-VL-72B** | 86.5% | 70.8% | 80.5% | $5.00 |
| **Gemini 2.0 Flash** | 84.0% | 75.0% | 78.0% | $0.075 |

**💡 نتیجه:** GLM-4.6 در MATH بهترین است ولی Claude در code بهتر است.

---

**🚀 ادامه دارد...**
