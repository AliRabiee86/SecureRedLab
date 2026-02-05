#!/bin/bash
# SecureRedLab Initialization Script
# Academic Research Platform for AI-Driven Red Team Simulations
# تمامی حقوق محفوظ است - پلتفرم تحقیقاتی آکادمیک برای شبیه‌سازی تیم قرمز مبتنی بر هوش مصنوعی

echo "Initializing SecureRedLab Academic Research Platform..."
echo "پلتفرم تحقیقاتی آکادمیک SecureRedLab در حال راه‌اندازی..."

# Set project root
PROJECT_ROOT="/home/user/webapp/SecureRedLab"
cd $PROJECT_ROOT

# Create virtual environment
echo "Creating Python virtual environment..."
python3.12 -m venv venv
source venv/bin/activate

# Install core dependencies
echo "Installing core dependencies..."
pip install --upgrade pip
pip install tensorflow==2.15.0 keras==2.15.0 scapy==2.5.0 numpy pandas scikit-learn
pip install django==5.0.0 djangorestframework channels==4.1.0 channels-redis
pip install psycopg2-binary celery==5.3.0 redis
pip install torch torchvision transformers
pip install opencv-python pillow matplotlib seaborn plotly
pip install flask flask-socketio python-socketio
pip install requests beautifulsoup4 lxml
pip install pyjwt cryptography
pip install docker-compose

# Create necessary directories for runtime
echo "Creating runtime directories..."
mkdir -p logs/{ai,simulations,monitoring,auth}
mkdir -p data/{models,datasets,logs,backups}
mkdir -p models/{tensorflow,pytorch,huggingface}
mkdir -p temp/{uploads,cache,sessions}
mkdir -p config/{ssl,certs,keys}

# Set permissions
chmod 755 -R $PROJECT_ROOT
chmod 700 config/keys
chmod 600 config/ssl/* 2>/dev/null || true

# Create .env file
cat > .env << 'EOF'
# SecureRedLab Environment Configuration
DEBUG=True
SECRET_KEY=your-secret-key-here
DATABASE_URL=postgresql://secureuser:securepass@localhost:5432/secureredlab
REDIS_URL=redis://localhost:6379/0
AI_MODELS_PATH=/home/user/webapp/SecureRedLab/models
LOG_LEVEL=INFO
MAX_SIMULATION_DURATION=3600
MAX_BOT_COUNT=1000000
DEFAULT_EVASION_RATE=0.9
SUPPORT_ONLY_MODE=True
PERSIAN_LOCALE=fa_IR
EOF

# Initialize git repository
git init
echo "SecureRedLab/" > .gitignore
echo "venv/" >> .gitignore
echo "*.pyc" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.log" >> .gitignore
echo "temp/" >> .gitignore
echo "data/backups/" >> .gitignore
echo ".env" >> .gitignore
echo "config/ssl/" >> .gitignore
echo "config/keys/" >> .gitignore

echo "SecureRedLab initialization completed successfully!"
echo "راه‌اندازی SecureRedLab با موفقیت انجام شد!"
echo "Project structure created at: $PROJECT_ROOT"
echo "Virtual environment created. Activate with: source venv/bin/activate"