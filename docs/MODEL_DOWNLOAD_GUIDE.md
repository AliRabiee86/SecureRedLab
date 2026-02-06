# 📥 MODEL DOWNLOAD GUIDE - SecureRedLab
## راهنمای کامل دانلود و نصب مدل‌های هوش مصنوعی

> **مهم**: این مدل‌ها رو **بعد از آماده شدن VPS** دانلود کنید.
> **حجم کل**: ~400GB (بسته به انتخاب شما)

---

## 📁 **ساختار پوشه‌ها**

```
/home/secureredlab/SecureRedLab/
├── models/                          # پوشه اصلی مدل‌ها
│   ├── reasoning/                   # Reasoning Models
│   │   ├── qwen3-235b-a22b/        # 59GB
│   │   └── glm-4-6-reasoning/      # 2GB
│   ├── non-reasoning/               # Non-Reasoning Models
│   │   ├── deepseek-v3-2-exp/      # 172GB (کوانتیزه شده)
│   │   ├── qwen3-coder-480b/       # 120GB
│   │   └── glm-4-6/                # 2GB
│   ├── vlm/                         # Vision Language Models
│   │   ├── qwen2-5-vl-72b-awq/     # 36GB
│   │   └── internvl2-8b/           # 4GB
│   ├── registry.db                  # Database برای Model Registry
│   └── checksums.txt                # SHA256 checksums
├── data/
│   └── finetuning/                  # داده‌های Fine-tuning
├── scripts/
│   ├── download_models.sh           # Script دانلود
│   ├── verify_models.sh             # بررسی Checksum
│   └── start_vllm_servers.sh        # راه‌اندازی سرورها
└── backend/
    └── ai_intelligence/
        ├── offline_core.py
        ├── anti_hallucination.py
        └── model_registry.py
```

---

## 🚀 **راهنمای دانلود (Step-by-Step)**

### **مرحله 1: نصب Dependencies**

```bash
# 1.1: نصب Python و pip
sudo apt update
sudo apt install -y python3.12 python3-pip git

# 1.2: نصب HuggingFace CLI
pip install --upgrade huggingface-hub

# 1.3: نصب vLLM و Dependencies
pip install vllm==0.6.0 torch==2.5.0 transformers==4.46.0 accelerate

# 1.4: تست نصب
huggingface-cli --version
python3 -c "import vllm; print(vllm.__version__)"
```

---

### **مرحله 2: ایجاد ساختار پوشه‌ها**

```bash
cd /home/secureredlab/SecureRedLab

# ایجاد پوشه‌ها
mkdir -p models/reasoning
mkdir -p models/non-reasoning
mkdir -p models/vlm
mkdir -p data/finetuning
mkdir -p scripts

# تنظیم Permissions
chmod 755 models
chmod 755 data
```

---

### **مرحله 3: دانلود مدل‌ها**

#### **گزینه A: Budget Setup (8GB VRAM - $4,000)**

```bash
# Reasoning Track (2GB)
echo "Downloading GLM-4.6-Reasoning..."
huggingface-cli download THUDM/glm-4-6-reasoning \
  --local-dir ./models/reasoning/glm-4-6-reasoning

# Non-Reasoning Track (2GB)
echo "Downloading GLM-4.6..."
huggingface-cli download THUDM/glm-4-6 \
  --local-dir ./models/non-reasoning/glm-4-6

# VLM Track (4GB)
echo "Downloading InternVL2-8B..."
huggingface-cli download OpenGVLab/InternVL2-8B \
  --local-dir ./models/vlm/internvl2-8b

# Total: 8GB VRAM
echo "✅ Budget setup complete! Total: ~8GB"
```

**منابع دانلود:**
- GLM-4.6-Reasoning: https://huggingface.co/THUDM/glm-4-6-reasoning
- GLM-4.6: https://huggingface.co/THUDM/glm-4-6
- InternVL2-8B: https://huggingface.co/OpenGVLab/InternVL2-8B

---

#### **گزینه B: Production Setup (96GB VRAM - $8,000)**

```bash
# Reasoning Track (59GB)
echo "Downloading Qwen3-235B-A22B-Reasoning..."
huggingface-cli download Qwen/Qwen3-235B-A22B-Instruct-2507-Reasoning \
  --local-dir ./models/reasoning/qwen3-235b-a22b \
  --local-dir-use-symlinks False

# Fallback Reasoning (2GB)
echo "Downloading GLM-4.6-Reasoning (fallback)..."
huggingface-cli download THUDM/glm-4-6-reasoning \
  --local-dir ./models/reasoning/glm-4-6-reasoning

# Non-Reasoning Track (quantized to 72GB)
echo "Downloading DeepSeek-V3.2-Exp (AWQ)..."
huggingface-cli download deepseek-ai/DeepSeek-V3.2-Exp-AWQ \
  --local-dir ./models/non-reasoning/deepseek-v3-2-exp

# Secondary Non-Reasoning (120GB - optional)
echo "Downloading Qwen3-Coder-480B-A35B..."
huggingface-cli download Qwen/Qwen3-Coder-480B-A35B-Instruct \
  --local-dir ./models/non-reasoning/qwen3-coder-480b

# VLM Track (36GB)
echo "Downloading Qwen2.5-VL-72B-AWQ..."
huggingface-cli download Qwen/Qwen2.5-VL-72B-Instruct-AWQ \
  --local-dir ./models/vlm/qwen2-5-vl-72b-awq

# Total: ~300GB storage, 96GB VRAM
echo "✅ Production setup complete!"
```

**منابع دانلود:**
- Qwen3-235B-A22B: https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507-Reasoning
- DeepSeek-V3.2-Exp-AWQ: https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp-AWQ
- Qwen3-Coder-480B: https://huggingface.co/Qwen/Qwen3-Coder-480B-A35B-Instruct
- Qwen2.5-VL-72B-AWQ: https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct-AWQ

---

### **مرحله 4: بررسی Checksums (مهم!)**

```bash
cd /home/secureredlab/SecureRedLab

# Generate checksums
find models/ -type f -name "*.safetensors" -o -name "*.bin" | \
  xargs sha256sum > models/checksums.txt

# Verify checksums
sha256sum -c models/checksums.txt

# اگر همه OK بودن:
echo "✅ All models verified successfully!"
```

---

### **مرحله 5: ایجاد Model Registry Database**

```bash
cd /home/secureredlab/SecureRedLab

# Create registry schema
cat > scripts/create_registry.sql << 'EOF'
CREATE TABLE IF NOT EXISTS models (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    type TEXT NOT NULL,  -- 'reasoning', 'non-reasoning', 'vlm'
    size_gb INTEGER,
    vram_gb INTEGER,
    path TEXT NOT NULL,
    version TEXT DEFAULT 'v1.0',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME,
    usage_count INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS model_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_id TEXT NOT NULL,
    latency_ms REAL,
    confidence REAL,
    hallucination_detected BOOLEAN,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (model_id) REFERENCES models(id)
);

-- Insert models
INSERT INTO models (id, name, type, size_gb, vram_gb, path) VALUES
    ('qwen3-235b-reasoning', 'Qwen3-235B-A22B-Reasoning', 'reasoning', 59, 59, './models/reasoning/qwen3-235b-a22b'),
    ('glm-4-6-reasoning', 'GLM-4.6-Reasoning', 'reasoning', 2, 2, './models/reasoning/glm-4-6-reasoning'),
    ('deepseek-v3-2-exp', 'DeepSeek-V3.2-Exp', 'non-reasoning', 172, 72, './models/non-reasoning/deepseek-v3-2-exp'),
    ('qwen3-coder-480b', 'Qwen3-Coder-480B', 'non-reasoning', 120, 120, './models/non-reasoning/qwen3-coder-480b'),
    ('glm-4-6', 'GLM-4.6', 'non-reasoning', 2, 2, './models/non-reasoning/glm-4-6'),
    ('qwen2-5-vl-72b', 'Qwen2.5-VL-72B-AWQ', 'vlm', 36, 36, './models/vlm/qwen2-5-vl-72b-awq'),
    ('internvl2-8b', 'InternVL2-8B', 'vlm', 4, 4, './models/vlm/internvl2-8b');
EOF

# Create database
sqlite3 models/registry.db < scripts/create_registry.sql

echo "✅ Model registry created!"
```

---

### **مرحله 6: راه‌اندازی vLLM Servers**

```bash
cd /home/secureredlab/SecureRedLab

# Create startup script
cat > scripts/start_vllm_servers.sh << 'EOF'
#!/bin/bash

# Stop existing servers
pkill -f "vllm.entrypoints"

# Start Reasoning Server (Qwen3-235B-A22B)
echo "Starting Reasoning Server..."
nohup python -m vllm.entrypoints.openai.api_server \
  --model ./models/reasoning/qwen3-235b-a22b \
  --quantization awq \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.9 \
  --port 8001 \
  > logs/reasoning-server.log 2>&1 &

# Start Non-Reasoning Server (DeepSeek-V3.2-Exp)
echo "Starting Non-Reasoning Server..."
nohup python -m vllm.entrypoints.openai.api_server \
  --model ./models/non-reasoning/deepseek-v3-2-exp \
  --quantization awq \
  --max-model-len 8192 \
  --gpu-memory-utilization 0.9 \
  --port 8002 \
  > logs/non-reasoning-server.log 2>&1 &

# Start VLM Server (Qwen2.5-VL-72B)
echo "Starting VLM Server..."
nohup python -m vllm.entrypoints.openai.api_server \
  --model ./models/vlm/qwen2-5-vl-72b-awq \
  --quantization awq \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.9 \
  --port 8003 \
  > logs/vlm-server.log 2>&1 &

echo "✅ All servers started!"
echo "Reasoning: http://localhost:8001"
echo "Non-Reasoning: http://localhost:8002"
echo "VLM: http://localhost:8003"
EOF

chmod +x scripts/start_vllm_servers.sh

# Run servers
./scripts/start_vllm_servers.sh
```

---

### **مرحله 7: تست مدل‌ها**

```bash
# Test Reasoning Server
curl http://localhost:8001/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen3-235b-reasoning",
    "prompt": "Generate SQL injection payload for admin login",
    "max_tokens": 512
  }'

# Test Non-Reasoning Server
curl http://localhost:8002/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v3-2-exp",
    "prompt": "Analyze this PHP code for vulnerabilities: <?php echo $_GET['id']; ?>",
    "max_tokens": 256
  }'

# Test VLM Server
curl http://localhost:8003/v1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "qwen2-5-vl-72b",
    "prompt": "Analyze this screenshot for SQL injection vulnerabilities",
    "images": ["data:image/png;base64,..."],
    "max_tokens": 512
  }'
```

---

## 📊 **جدول خلاصه دانلود**

### **Budget Setup (8GB VRAM):**

| Model | Size | VRAM | Download URL | Use Case |
|-------|------|------|--------------|----------|
| GLM-4.6-Reasoning | 2GB | 2GB | https://huggingface.co/THUDM/glm-4-6-reasoning | Reasoning |
| GLM-4.6 | 2GB | 2GB | https://huggingface.co/THUDM/glm-4-6 | Fast inference |
| InternVL2-8B | 4GB | 4GB | https://huggingface.co/OpenGVLab/InternVL2-8B | VLM |
| **Total** | **8GB** | **8GB** | - | - |

### **Production Setup (96GB VRAM):**

| Model | Size | VRAM | Download URL | Use Case |
|-------|------|------|--------------|----------|
| Qwen3-235B-A22B | 59GB | 59GB | https://huggingface.co/Qwen/Qwen3-235B-A22B-Instruct-2507-Reasoning | Reasoning |
| DeepSeek-V3.2-Exp-AWQ | 172GB | 72GB | https://huggingface.co/deepseek-ai/DeepSeek-V3.2-Exp-AWQ | Non-Reasoning |
| Qwen2.5-VL-72B-AWQ | 36GB | 36GB | https://huggingface.co/Qwen/Qwen2.5-VL-72B-Instruct-AWQ | VLM |
| **Total** | **267GB** | **167GB** (با quantization: 96GB) | - | - |

---

## ⚠️ **نکات مهم**

### **1. فضای Disk:**
- Budget: حداقل 20GB
- Production: حداقل 400GB
- بهتر: 1TB SSD NVMe

### **2. Internet:**
- سرعت: حداقل 100 Mbps
- Unlimited bandwidth (300GB+ download)

### **3. Memory:**
- Budget: 32GB RAM
- Production: 128GB RAM

### **4. Backup:**
- بعد از دانلود حتما Backup بگیرید
- Checksum ها رو ذخیره کنید

---

## 🔧 **Script کامل دانلود (یکجا)**

```bash
#!/bin/bash

cat > download_all_models.sh << 'EOF'
#!/bin/bash

# Configuration
SETUP_TYPE="production"  # or "budget"
BASE_DIR="/home/secureredlab/SecureRedLab"
MODEL_DIR="$BASE_DIR/models"

echo "🚀 Starting SecureRedLab Model Download..."
echo "Setup Type: $SETUP_TYPE"

# Create directories
mkdir -p $MODEL_DIR/{reasoning,non-reasoning,vlm}

cd $BASE_DIR

if [ "$SETUP_TYPE" == "budget" ]; then
    echo "📥 Downloading Budget Setup (8GB)..."
    
    huggingface-cli download THUDM/glm-4-6-reasoning \
      --local-dir $MODEL_DIR/reasoning/glm-4-6-reasoning
    
    huggingface-cli download THUDM/glm-4-6 \
      --local-dir $MODEL_DIR/non-reasoning/glm-4-6
    
    huggingface-cli download OpenGVLab/InternVL2-8B \
      --local-dir $MODEL_DIR/vlm/internvl2-8b
    
    echo "✅ Budget setup complete! (8GB)"
else
    echo "📥 Downloading Production Setup (300GB)..."
    
    huggingface-cli download Qwen/Qwen3-235B-A22B-Instruct-2507-Reasoning \
      --local-dir $MODEL_DIR/reasoning/qwen3-235b-a22b
    
    huggingface-cli download deepseek-ai/DeepSeek-V3.2-Exp-AWQ \
      --local-dir $MODEL_DIR/non-reasoning/deepseek-v3-2-exp
    
    huggingface-cli download Qwen/Qwen2.5-VL-72B-Instruct-AWQ \
      --local-dir $MODEL_DIR/vlm/qwen2-5-vl-72b-awq
    
    echo "✅ Production setup complete! (300GB)"
fi

# Generate checksums
echo "🔒 Generating checksums..."
find $MODEL_DIR -type f \( -name "*.safetensors" -o -name "*.bin" \) | \
  xargs sha256sum > $MODEL_DIR/checksums.txt

echo "✅ All done! Models downloaded to: $MODEL_DIR"
EOF

chmod +x download_all_models.sh
./download_all_models.sh
```

---

## 📞 **پشتیبانی**

اگر در دانلود مشکلی پیش اومد:

1. **Network Error**: استفاده از Resume:
   ```bash
   huggingface-cli download MODEL_ID --local-dir ./path --resume-download
   ```

2. **Storage Full**: پاک کردن Cache:
   ```bash
   rm -rf ~/.cache/huggingface/
   ```

3. **Slow Download**: استفاده از Mirror:
   ```bash
   # Export mirror URL
   export HF_ENDPOINT=https://hf-mirror.com
   ```

---

**🎯 آماده برای Implementation Phase بعدی!**
