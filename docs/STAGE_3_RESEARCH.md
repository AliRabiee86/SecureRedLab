# Stage 3 Research: VLM Core Architecture
## تحقیق عمیق معماری VLM و انتخاب تکنولوژی

**تاریخ**: 2025-12-08  
**مرحله**: Stage 3.0 - Deep Research  
**هدف**: طراحی بهترین معماری VLM آفلاین با بهترین performance

---

## 🔍 سوالات کلیدی تحقیق

### 1️⃣ آیا vLLM از VLM پشتیبانی می‌کند؟
**پاسخ**: ✅ بله، اما محدود

**یافته‌ها**:
- vLLM از v0.9.0 پشتیبانی تجربی از VLM دارد
- مدل‌های پشتیبانی‌شده:
  - ✅ Qwen2-VL
  - ✅ Qwen3-VL (جدیدترین)
  - ✅ InternVL (محدود)
  - ⚠️ فقط image input (video هنوز نه)

**منبع**: 
- https://docs.vllm.ai/en/latest/models/supported_models/
- https://docs.vllm.ai/en/latest/examples/offline_inference/vision_language/

---

### 2️⃣ Python vs Rust برای VLM Inference؟
**تصمیم**: **Python (با Rust extensions)**

**دلایل**:

#### ✅ مزایای Python:
1. **Ecosystem غنی**:
   - vLLM (Python-based)
   - Transformers (Hugging Face)
   - PyTorch/ONNX backends
   
2. **Integration ساده**:
   - کد موجود ما Python است
   - RL Engine (Python)
   - AI Core (Python)
   
3. **Development سریع‌تر**:
   - Debug آسان‌تر
   - Community بزرگ‌تر
   - Documentation بیشتر

4. **VLM Libraries**:
   - تمام VLM implementations در Python هستند
   - Qwen2-VL: Python + Transformers
   - InternVL: Python + PyTorch

#### ⚠️ محدودیت‌های Python:
1. GIL (Global Interpreter Lock)
2. Performance overhead در I/O
3. Memory management کندتر

#### 🔧 راه‌حل: Hybrid Approach
```
Python (High-Level Logic)
    ↓
vLLM (C++/CUDA backend)
    ↓
GPU Inference (Native)
```

**نتیجه**: Python برای orchestration، vLLM برای inference سرعت بالا

**منبع**:
- https://medium.com/@soumyajit.swain/rust-the-performance-edge-for-large-language-model-inference-59528a66ec68
- https://pypi.org/project/vllm-rs/ (Rust binding - اختیاری)

---

### 3️⃣ بهترین کتابخانه OCR؟
**تصمیم**: **3-Tier Strategy**

#### Tier 1: VLM-based OCR (Hunyuan-OCR, Qwen2.5-VL)
**مزایا**:
- Context understanding
- Multi-language support
- Complex layouts
- Low hallucination (2-5%)

**استفاده**: اسناد پیچیده، تصاویر با context

#### Tier 2: PaddleOCR (Production-grade)
**مزایا**:
- سریع‌ترین (GPU-accelerated)
- Multi-language (80+ languages)
- High accuracy
- Open-source

**استفاده**: OCR عمومی، سرعت بالا

#### Tier 3: Tesseract (Fallback)
**مزایا**:
- CPU-only (no GPU needed)
- Mature & stable
- Small footprint

**استفاده**: Fallback اگر GPU نیست

#### ❌ **نتیجه**: EasyOCR (حذف شد)
دلیل: کندتر از PaddleOCR، accuracy مشابه

**منبع**:
- https://unstract.com/blog/best-opensource-ocr-tools-in-2025/
- https://modal.com/blog/8-top-open-source-ocr-models-compared
- https://www.reddit.com/r/LocalLLaMA/comments/1eecto9/best_ocr/

---

## 🏗️ معماری نهایی VLM Core

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│           VLM Core System                   │
├─────────────────────────────────────────────┤
│  Component 1: VLM Client (Python)           │
│    - vLLM backend (Qwen2.5-VL, InternVL)    │
│    - Image preprocessing                    │
│    - Context management                     │
│                                             │
│  Component 2: 3-Track Router                │
│    Track 1: Complex Reasoning (InternVL)    │
│    Track 2: Document/Screenshot (Qwen2-VL)  │
│    Track 3: Pure OCR (Hunyuan-OCR/Paddle)   │
│                                             │
│  Component 3: OCR Fallback Chain            │
│    Primary: Hunyuan-OCR (vLLM)              │
│    Secondary: PaddleOCR (GPU)               │
│    Tertiary: Tesseract (CPU)                │
│                                             │
│  Component 4: VLM Anti-Hallucination        │
│    - Multi-model consensus                  │
│    - OCR confidence scoring                 │
│    - Bounding box verification              │
│    - Text consistency check                 │
└─────────────────────────────────────────────┘
```

---

## 📊 Model Selection Strategy

### Track 1: Complex Visual Reasoning
**Primary**: InternVL3-78B (20GB VRAM)
- MMMU Score: 72.2%
- Best for complex reasoning

**Fallback**: MiniCPM-V 4.5 (4GB VRAM)
- MMMU Score: 66.3%
- Budget option

### Track 2: Document & Screenshot Analysis
**Primary**: Qwen2.5-VL-72B-AWQ (36GB VRAM)
- DocVQA Score: 93.5%
- Best for documents

**Fallback**: InternVL2-8B (4GB VRAM)
- Lightweight alternative

### Track 3: Pure OCR
**Primary**: Hunyuan-OCR (1GB VRAM)
- OlmOCR Score: 92.0%
- 2% hallucination

**Secondary**: PaddleOCR (Python library)
- Fast GPU inference
- 80+ languages

**Tertiary**: Tesseract (CPU-only)
- No GPU required
- Mature & stable

---

## 🔧 Technology Stack

### Core Framework
```python
Language: Python 3.10+
Inference: vLLM v0.9.0+ (VLM support)
Backend: CUDA 12.1+ / PyTorch 2.0+
```

### Image Processing
```python
PIL/Pillow: Image loading & preprocessing
OpenCV: Advanced image operations
NumPy: Array operations
```

### OCR Libraries
```python
Primary: vLLM (Hunyuan-OCR via model)
Secondary: PaddleOCR (pip install paddleocr)
Tertiary: pytesseract (pip install pytesseract)
```

### Integration
```python
Async: asyncio for concurrent processing
Queue: Priority queue for task management
Cache: LRU cache for image preprocessing
```

---

## 📁 File Structure

```
SecureRedLab/
├── ai/
│   ├── offline_core.py        (LLM core - EXISTS)
│   ├── vllm_client.py         (LLM client - EXISTS)
│   ├── dual_track_router.py   (LLM router - EXISTS)
│   ├── anti_hallucination.py  (LLM guardrails - EXISTS)
│   │
│   ├── vlm_core.py           (VLM core - NEW) ← Main orchestrator
│   ├── vlm_client.py         (VLM client - NEW) ← vLLM VLM support
│   ├── vlm_router.py         (VLM 3-track - NEW) ← Track selection
│   ├── vlm_hallucination.py  (VLM guardrails - NEW) ← OCR verification
│   └── ocr_fallback.py       (OCR chain - NEW) ← Multi-tier OCR
```

---

## 🎯 Implementation Phases

### Phase 3.1: Architecture Design
- [ ] Define data classes (VLMTask, VLMResult, OCRResult)
- [ ] Design 3-track routing logic
- [ ] Plan OCR fallback chain
- [ ] Design anti-hallucination for VLM

### Phase 3.2: VLM Client Implementation
- [ ] Integrate with vLLM VLM API
- [ ] Image preprocessing pipeline
- [ ] Model loading (lazy)
- [ ] Inference methods (sync/async)

### Phase 3.3: 3-Track Router
- [ ] Task classification (complexity analysis)
- [ ] Image type detection (document vs screenshot vs photo)
- [ ] Model selection logic
- [ ] Fallback handling

### Phase 3.4: OCR Fallback Chain
- [ ] Hunyuan-OCR integration (vLLM)
- [ ] PaddleOCR integration (library)
- [ ] Tesseract integration (fallback)
- [ ] Confidence scoring
- [ ] Automatic fallback

### Phase 3.5: VLM Anti-Hallucination
- [ ] Multi-model consensus (2+ VLMs)
- [ ] OCR confidence validation
- [ ] Bounding box verification
- [ ] Text consistency check
- [ ] Hallucination detection

### Phase 3.6: Testing & Validation
- [ ] Unit tests
- [ ] Integration tests
- [ ] Performance benchmarks
- [ ] Accuracy validation

---

## ⚡ Performance Targets

### Latency Goals
| Track | Model | Target Latency |
|-------|-------|----------------|
| Complex Reasoning | InternVL3-78B | <5s |
| Document Analysis | Qwen2.5-VL-72B | <3s |
| Pure OCR | Hunyuan-OCR | <1s |
| Pure OCR (PaddleOCR) | N/A | <0.5s |
| Pure OCR (Tesseract) | N/A | <0.3s |

### Accuracy Goals
| Task | Target Accuracy |
|------|-----------------|
| Complex VQA | >70% (MMMU) |
| Document OCR | >90% (DocVQA) |
| Pure OCR | >92% (OlmOCR) |
| Hallucination Rate | <5% |

### Resource Goals
| Config | VRAM | Models Loaded |
|--------|------|---------------|
| Budget | 8GB | MiniCPM-V + Hunyuan-OCR |
| Production | 48GB | Qwen2.5-VL + InternVL2 + Hunyuan |
| Enterprise | 96GB | InternVL3 + Qwen2.5-VL + All OCR |

---

## 🚨 Critical Decisions

### ✅ Decision 1: Python (not Rust)
**Rationale**: 
- Ecosystem compatibility
- vLLM is Python-based
- Faster development
- Better VLM library support

### ✅ Decision 2: vLLM for VLM (not separate library)
**Rationale**:
- Unified inference backend
- Better memory management
- PagedAttention for efficiency
- Consistent API with LLM core

### ✅ Decision 3: 3-Tier OCR Strategy
**Rationale**:
- VLM for complex (context understanding)
- PaddleOCR for speed (GPU-accelerated)
- Tesseract for fallback (CPU-only)

### ✅ Decision 4: Async-first Architecture
**Rationale**:
- Non-blocking image preprocessing
- Concurrent OCR operations
- Better throughput for batches

---

## 📝 Next Steps

1. **Immediate**: Create data classes and enums
2. **Phase 3.1**: Design VLM Core architecture (1-2 hours)
3. **Phase 3.2**: Implement VLM Client (2-3 hours)
4. **Phase 3.3**: Implement 3-Track Router (1-2 hours)
5. **Phase 3.4**: Implement OCR Fallback (2-3 hours)
6. **Phase 3.5**: Implement VLM Anti-Hallucination (2-3 hours)
7. **Phase 3.6**: Testing & Validation (2-3 hours)

**Total Estimated Time**: 10-16 hours

---

**Status**: Research Complete ✅  
**Next**: Stage 3.1 - Design VLM Core Architecture
