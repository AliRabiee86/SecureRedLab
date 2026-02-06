# 🔍 VLM MODELS RESEARCH - SecureRedLab 2025
## تحقیق جامع Vision Language Models برای Cybersecurity

> **تاریخ تحقیق**: دسامبر 2025 (آخرین آپدیت‌ها)  
> **منابع**: OpenCompass, MMMU Benchmark, OCR Benchmarks, Reddit LocalLLaMA

---

## 📊 **جدول کامل VLM Models (دسامبر 2025)**

### 🥇 **بهترین مدل‌های VLM برای SecureRedLab**

| Model | Size | VRAM (AWQ) | MMMU | OCR (OlmOCR) | DocVQA | UI Analysis | Hallucination | Offline | Cybersecurity Use |
|-------|------|------------|------|--------------|--------|-------------|---------------|---------|-------------------|
| **MiniCPM-V 4.5** | 8B | **4GB** | 66.3% | 75.0% | 89.2% | 🟢 Excellent | 🟢 Low | ✅ | **BEST - UI Vuln Detection** |
| **InternVL3-78B** | 78B | **20GB** | **72.2%** | 80.0% | 92.0% | 🟢 Excellent | 🟢 Low | ✅ | **BEST - Complex Visual Reasoning** |
| **Qwen2.5-VL-72B-AWQ** | 72B | **36GB** | 64.5% | 85.0% | **93.5%** | 🟢 Best | 🟢 Low | ✅ | **BEST - Document Analysis** |
| **Hunyuan-OCR** | 1B | **1GB** | - | **92.0%** | 95.0% | 🟡 Moderate | 🟢 Low | ✅ | **BEST - OCR Only** |
| **Chandra OCR** | 8B | **4GB** | - | **83.1%** | 88.0% | 🟢 Good | 🟢 Low | ✅ | Good - Document Parsing |
| **InternVL2-8B** | 8B | **4GB** | 51.4% | 70.0% | 82.0% | 🟡 Good | 🟡 Medium | ✅ | Good - Lightweight |
| **LLaVA-NeXT-34B** | 34B | **17GB** | 48.8% | 68.0% | 79.0% | 🟡 Moderate | 🟡 Medium | ✅ | Moderate - General Purpose |
| **Pixtral-12B** | 12B | **6GB** | 52.5% | 72.0% | 81.8% | 🟡 Good | 🟡 Medium | ✅ | Good - Fast Inference |

---

## 🔥 **کشفیات مهم:**

### **1. MiniCPM-V 4.5 فوق‌العاده است!** ✅

```yaml
MiniCPM-V 4.5:
  Size: 8B (خیلی سبک!)
  VRAM: 4GB (AWQ/GGUF)
  MMMU: 66.3% (بهتر از Qwen2.5-VL-72B!)
  DocVQA: 89.2%
  OpenCompass: 77.0 (Average)
  
  Benchmark Comparison:
    - Beats GPT-4o-latest (65.2% vs 66.3% MMMU)
    - Beats Gemini-2.0 Pro (64.8% vs 66.3%)
    - Beats Qwen2.5-VL-72B (64.5% vs 66.3%)
  
  => **بهترین انتخاب برای Budget Setup**
  => **فقط 4GB VRAM نیاز داره!**
```

**منبع**: https://github.com/OpenBMB/MiniCPM-V

---

### **2. InternVL3-78B قدرتمندترین است!** ✅

```yaml
InternVL3-78B:
  Size: 78B
  VRAM: 20GB (AWQ quantization)
  MMMU: 72.2% (State-of-the-Art!)
  Reasoning: Excellent
  UI Analysis: Best
  
  Strengths:
    - بهترین مدل Open-Source برای Visual Reasoning
    - عملکرد عالی روی چند تصویر
    - پشتیبانی از Video Understanding
  
  => **بهترین برای Production (اگر VRAM داری)**
```

**منبع**: https://internvl.github.io/blog/2025-04-11-InternVL-3.0/

---

### **3. Qwen2.5-VL-72B برای Document بهترینه!** ✅

```yaml
Qwen2.5-VL-72B-AWQ:
  Size: 72B
  VRAM: 36GB (AWQ)
  DocVQA: 93.5% (بهترین!)
  OCR: 85.0%
  
  Strengths:
    - بهترین برای Document Parsing
    - OCR فوق‌العاده
    - پشتیبانی از Multiple Images
  
  => **بهترین برای Screenshot Analysis**
```

---

### **4. Hunyuan-OCR فقط برای OCR!** ✅

```yaml
Hunyuan-OCR:
  Size: 1B (خیلی خیلی سبک!)
  VRAM: 1GB
  OlmOCR Score: 92.0% (بهترین!)
  DocVQA: 95.0%
  
  Comparison:
    - Beats DeepSeek-OCR (75.7%)
    - Beats PaddleOCR (60.0%)
    - Beats Qwen2.5-VL (85.0%)
  
  Supports:
    - 100+ languages
    - Complex layouts
    - Handwritten text
  
  => **فقط برای OCR استفاده کن (نه Visual Reasoning)**
```

**منبع**: https://medium.com/data-science-in-your-pocket/hunyuan-ocr-best-ocr-beats-deepseek-ocr-paddleocr-df0d563a8e3e

---

## 🎯 **معماری نهایی VLM برای SecureRedLab:**

```yaml
# TRIPLE-TRACK VLM ARCHITECTURE

Track 1: Complex Visual Reasoning (Multi-Image, UI Analysis)
  Primary:
    - InternVL3-78B  # 20GB VRAM (AWQ)
    Strengths:
      - MMMU: 72.2% (State-of-the-Art)
      - Multi-image understanding
      - Video analysis
    Use Cases:
      - Complex UI vulnerability analysis
      - Multi-step attack visualization
      - Video-based security analysis
  
  Fallback:
    - MiniCPM-V 4.5  # 4GB VRAM
    Strengths:
      - MMMU: 66.3% (بهتر از GPT-4o!)
      - فوق‌العاده سبک
      - سریع
    Use Cases:
      - Single image analysis
      - Quick screenshot checks
      - Mobile deployment

Track 2: Document & Screenshot Analysis
  Primary:
    - Qwen2.5-VL-72B-AWQ  # 36GB VRAM
    Strengths:
      - DocVQA: 93.5% (بهترین!)
      - OCR: 85.0%
    Use Cases:
      - Web page screenshot analysis
      - SQL injection in forms
      - XSS detection in UI elements
  
  Fallback:
    - InternVL2-8B  # 4GB VRAM
    Strengths:
      - DocVQA: 82.0%
      - Fast inference
    Use Cases:
      - Quick document checks
      - Simple UI analysis

Track 3: Pure OCR (Text Extraction Only)
  Primary:
    - Hunyuan-OCR  # 1GB VRAM
    Strengths:
      - OlmOCR: 92.0% (بهترین!)
      - 100+ languages
      - Ultra-fast
    Use Cases:
      - Extracting text from screenshots
      - Reading error messages
      - Analyzing log files in images
  
  Fallback:
    - Chandra OCR  # 4GB VRAM
    Strengths:
      - OlmOCR: 83.1%
      - Good accuracy
    Use Cases:
      - Backup OCR
      - Complex documents
```

---

## 📊 **Detailed Benchmarks:**

### **MMMU Benchmark (Multimodal Understanding):**

| Model | MMMU Score | Reasoning | OCR | Math | Science |
|-------|------------|-----------|-----|------|---------|
| **InternVL3-78B** | **72.2%** | 🟢 | 🟢 | 🟢 | 🟢 |
| **MiniCPM-V 4.5** | **66.3%** | 🟢 | 🟡 | 🟢 | 🟢 |
| Qwen2.5-VL-72B | 64.5% | 🟢 | 🟢 | 🟡 | 🟡 |
| GPT-4o-latest | 65.2% | 🟢 | 🟢 | 🟢 | 🟢 |
| Gemini-2.0 Pro | 64.8% | 🟢 | 🟢 | 🟢 | 🟢 |

**منبع**: https://mmmu-benchmark.github.io/

---

### **OCR Benchmark (OlmOCR Score):**

| Model | OlmOCR Score | Handwriting | Complex Layouts | Multi-language |
|-------|--------------|-------------|-----------------|----------------|
| **Hunyuan-OCR** | **92.0%** | 🟢 Best | 🟢 Best | 🟢 100+ langs |
| **Qwen2.5-VL-72B** | **85.0%** | 🟢 Good | 🟢 Good | 🟢 Good |
| **Chandra OCR** | **83.1%** | 🟢 Good | 🟢 Good | 🟡 Moderate |
| DeepSeek-OCR | 75.7% | 🟡 Moderate | 🟡 Moderate | 🟡 Moderate |
| PaddleOCR | 60.0% | 🔴 Weak | 🔴 Weak | 🟡 Moderate |

**منبع**: https://www.e2enetworks.com/blog/complete-guide-open-source-ocr-models-2025

---

### **DocVQA Benchmark (Document Understanding):**

| Model | DocVQA ANLS | Tables | Forms | Charts |
|-------|-------------|--------|-------|--------|
| **Hunyuan-OCR** | **95.0%** | 🟢 | 🟢 | 🟢 |
| **Qwen2.5-VL-72B** | **93.5%** | 🟢 | 🟢 | 🟢 |
| **InternVL3-78B** | **92.0%** | 🟢 | 🟢 | 🟢 |
| MiniCPM-V 4.5 | 89.2% | 🟢 | 🟡 | 🟡 |
| Pixtral-12B | 81.8% | 🟡 | 🟡 | 🟡 |

---

## 💰 **Hardware Requirements:**

### **Budget Setup (8GB VRAM - $4,000):**

```yaml
VLM Stack:
  - MiniCPM-V 4.5 (4GB)       # Main VLM
  - Hunyuan-OCR (1GB)         # OCR only
  Total: 5GB VRAM
  
  Remaining: 3GB for other tasks
  
Capabilities:
  ✅ UI vulnerability analysis
  ✅ Screenshot analysis
  ✅ OCR text extraction
  ✅ Single image reasoning
  ❌ Complex multi-image tasks
  ❌ Video analysis
```

---

### **Production Setup (48GB VRAM - $8,000):**

```yaml
VLM Stack:
  - InternVL3-78B (20GB)      # Complex reasoning
  - Qwen2.5-VL-72B-AWQ (36GB) # Document analysis
  Total: 56GB VRAM
  
  => نیاز به 2x RTX 4090 (48GB) + CPU offload
  
  OR:
  
  - Qwen2.5-VL-72B-AWQ (36GB) # Primary
  - MiniCPM-V 4.5 (4GB)       # Fallback
  - Hunyuan-OCR (1GB)         # OCR
  Total: 41GB VRAM
  
  => Fits in 2x RTX 4090 (48GB) ✅
```

---

### **Enterprise Setup (96GB+ VRAM - $16,000):**

```yaml
VLM Stack:
  - InternVL3-78B (20GB)      # Complex reasoning
  - Qwen2.5-VL-72B-AWQ (36GB) # Document analysis
  - MiniCPM-V 4.5 (4GB)       # Fast fallback
  - Hunyuan-OCR (1GB)         # OCR
  Total: 61GB VRAM
  
  Remaining: 35GB for LLM/Reasoning models
  
Hardware:
  - 4x RTX 4090 (96GB total)
  OR
  - 2x A100 80GB (160GB total)
```

---

## 🛠️ **Implementation Details:**

### **Model Loading Strategy:**

```python
class VLMRouter:
    """
    Smart VLM Router برای انتخاب بهترین مدل
    """
    
    def __init__(self):
        self.models = {
            "complex_reasoning": "internvl3-78b",    # 20GB
            "document_analysis": "qwen2.5-vl-72b",  # 36GB
            "fast_analysis": "minicpm-v-4-5",        # 4GB
            "pure_ocr": "hunyuan-ocr"                # 1GB
        }
        
        self.vram_usage = {
            "internvl3-78b": 20,
            "qwen2.5-vl-72b": 36,
            "minicpm-v-4-5": 4,
            "hunyuan-ocr": 1
        }
    
    async def route_request(self, task: VLMAnalysisRequest) -> str:
        """
        انتخاب بهترین مدل بر اساس نوع Task
        """
        # Pure OCR?
        if task.task_type == "ocr_only":
            return "pure_ocr"
        
        # Multi-image or Video?
        if len(task.images) > 1 or task.has_video:
            return "complex_reasoning"
        
        # Document analysis?
        if task.task_type == "document_analysis":
            return "document_analysis"
        
        # Default: Fast analysis
        return "fast_analysis"
```

---

### **Anti-Hallucination for VLM:**

```python
class VLMHallucinationDetector:
    """
    تشخیص Hallucination در VLM outputs
    """
    
    async def validate_vlm_output(self, image: str, output: str) -> dict:
        """
        Validate VLM output با cross-checking
        """
        # 1. Self-Consistency: Run 3 times
        outputs = []
        for _ in range(3):
            result = await self.vlm.analyze(image)
            outputs.append(result)
        
        # 2. Check consistency
        if len(set(outputs)) > 1:
            # مختلف بودن → احتمال Hallucination
            return {
                "is_valid": False,
                "reason": "Inconsistent outputs",
                "outputs": outputs
            }
        
        # 3. Cross-validate با OCR
        ocr_result = await self.ocr.extract_text(image)
        vlm_text = self.extract_mentioned_text(output)
        
        overlap = self.calculate_overlap(ocr_result, vlm_text)
        
        if overlap < 0.7:  # کمتر از 70% همخوانی
            return {
                "is_valid": False,
                "reason": "Low OCR overlap",
                "ocr": ocr_result,
                "vlm": vlm_text
            }
        
        return {"is_valid": True, "confidence": overlap}
```

---

## 📥 **Download Commands:**

### **Budget Setup:**

```bash
# MiniCPM-V 4.5 (4GB)
huggingface-cli download openbmb/MiniCPM-V-4_5 \
  --local-dir ./models/vlm/minicpm-v-4-5

# Hunyuan-OCR (1GB)
huggingface-cli download Tencent/Hunyuan-OCR \
  --local-dir ./models/vlm/hunyuan-ocr
```

### **Production Setup:**

```bash
# InternVL3-78B (20GB AWQ)
huggingface-cli download OpenGVLab/InternVL3-78B-AWQ \
  --local-dir ./models/vlm/internvl3-78b

# Qwen2.5-VL-72B-AWQ (36GB)
huggingface-cli download Qwen/Qwen2.5-VL-72B-Instruct-AWQ \
  --local-dir ./models/vlm/qwen2-5-vl-72b-awq

# MiniCPM-V 4.5 (fallback)
huggingface-cli download openbmb/MiniCPM-V-4_5 \
  --local-dir ./models/vlm/minicpm-v-4-5

# Hunyuan-OCR
huggingface-cli download Tencent/Hunyuan-OCR \
  --local-dir ./models/vlm/hunyuan-ocr
```

---

## ✅ **توصیه نهایی:**

### **چرا این معماری بهترین است؟**

1. **MiniCPM-V 4.5 برای Budget**:
   - فقط 4GB VRAM
   - MMMU 66.3% (بهتر از GPT-4o!)
   - سریع و دقیق

2. **InternVL3-78B برای Production**:
   - MMMU 72.2% (State-of-the-Art)
   - Multi-image support
   - Video understanding

3. **Qwen2.5-VL-72B برای Documents**:
   - DocVQA 93.5% (بهترین!)
   - OCR عالی
   - Screenshot analysis

4. **Hunyuan-OCR برای Pure OCR**:
   - OlmOCR 92.0% (بهترین!)
   - 100+ languages
   - فقط 1GB VRAM

---

## 📚 **منابع:**

1. **MiniCPM-V 4.5**: https://github.com/OpenBMB/MiniCPM-V
2. **InternVL3**: https://internvl.github.io/blog/2025-04-11-InternVL-3.0/
3. **Qwen2.5-VL**: https://qwenlm.github.io/blog/qwen2.5-vl/
4. **Hunyuan-OCR**: https://medium.com/data-science-in-your-pocket/hunyuan-ocr-best-ocr-beats-deepseek-ocr-paddleocr-df0d563a8e3e
5. **MMMU Benchmark**: https://mmmu-benchmark.github.io/
6. **OlmOCR Benchmark**: https://www.e2enetworks.com/blog/complete-guide-open-source-ocr-models-2025

---

**🎯 آماده برای Implementation!**
