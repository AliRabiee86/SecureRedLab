# 🚀 SecureRedLab - راهنمای تست محلی (Local Testing Guide)
## 🇮🇷 نسخه فارسی | Persian Version

---

## 📋 فهرست مطالب

1. [پیش‌نیازها](#پیش‌نیازها)
2. [راه‌اندازی Backend](#راه‌اندازی-backend)
3. [راه‌اندازی Frontend](#راه‌اندازی-frontend)
4. [تست روی کامپیوتر محلی](#تست-روی-کامپیوتر-محلی)
5. [عیب‌یابی](#عیب‌یابی)

---

## 🛠️ پیش‌نیازها

### نرم‌افزارهای مورد نیاز:
1. **Python 3.12+** - برای Backend
2. **Node.js 18+** - برای Frontend
3. **Git** - برای دریافت کد
4. **یک مرورگر مدرن** (Chrome, Firefox, Safari, Edge)

### بررسی نصب:
```bash
# Python
python3 --version
# باید 3.12 یا بالاتر باشد

# Node.js
node --version
# باید 18 یا بالاتر باشد

# npm
npm --version
# باید 9 یا بالاتر باشد

# Git
git --version
```

---

## 🔧 راه‌اندازی Backend

### روش 1: استفاده از Sandbox موجود (پیشنهادی)

اگر Backend در sandbox راه‌اندازی شده، می‌توانید از URL عمومی استفاده کنید:

```
Backend URL: https://5173-ilhm3fa5fq6tbdwrij8ka-2e77fc33.sandbox.novita.ai
```

**این روش نیاز به نصب Backend در کامپیوتر شما ندارد!**

---

### روش 2: نصب Backend در کامپیوتر شخصی

#### گام 1: دریافت کد

```bash
# Clone پروژه
git clone https://github.com/YOUR_USERNAME/SecureRedLab.git
cd SecureRedLab
```

#### گام 2: نصب Dependencies

```bash
# رفتن به پوشه backend
cd backend

# ساخت virtual environment
python3 -m venv venv

# فعال‌سازی virtual environment

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# نصب dependencies
pip install -r requirements.txt
```

#### گام 3: پیکربندی محیط

```bash
# کپی فایل .env.example
cp .env.example .env

# ویرایش .env (اختیاری)
# تنظیمات پیش‌فرض برای development کافی است
```

#### گام 4: راه‌اندازی سرور

```bash
# روش ساده:
python simple_api.py

# یا با uvicorn:
uvicorn simple_api:app --host 0.0.0.0 --port 8000 --reload
```

#### گام 5: تست Backend

باز کردن در مرورگر:
```
http://localhost:8000
```

یا با curl:
```bash
curl http://localhost:8000
```

باید پیامی شبیه این ببینید:
```json
{
  "message": "SecureRedLab API - Development Mode",
  "version": "1.0.0",
  "status": "running"
}
```

#### 🎯 API Documentation

بعد از راه‌اندازی، مستندات API در این آدرس‌ها:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🎨 راه‌اندازی Frontend

### گام 1: رفتن به پوشه Frontend

```bash
# از پوشه اصلی پروژه:
cd SecureRedLab/frontend
```

### گام 2: نصب Dependencies

```bash
npm install
```

این کار چند دقیقه طول می‌کشد (حدود 378 پکیج).

### گام 3: پیکربندی Backend URL

#### الف) استفاده از Backend Sandbox:

فایل `.env.local` بسازید:
```bash
# SecureRedLab/frontend/.env.local
VITE_API_BASE_URL=http://localhost:8000
```

#### ب) استفاده از Backend محلی:

```bash
# SecureRedLab/frontend/.env.local
VITE_API_BASE_URL=http://localhost:8000
```

### گام 4: راه‌اندازی Development Server

```bash
npm run dev
```

خروجی باید شبیه این باشد:
```
VITE v7.3.1  ready in 644 ms

➜  Local:   http://localhost:5173/
➜  Network: http://192.168.1.X:5173/
➜  press h to show help
```

### گام 5: باز کردن در مرورگر

مرورگر خود را باز کنید و به این آدرس بروید:
```
http://localhost:5173
```

---

## 💻 تست روی کامپیوتر محلی

### سناریو 1: هر دو سرویس در کامپیوتر شما

```
Backend:  http://localhost:8000
Frontend: http://localhost:5173
```

#### مراحل:

1. **Terminal 1 - Backend:**
```bash
cd SecureRedLab/backend
source venv/bin/activate  # Windows: venv\Scripts\activate
python simple_api.py
```

2. **Terminal 2 - Frontend:**
```bash
cd SecureRedLab/frontend
npm run dev
```

3. **مرورگر:**
```
http://localhost:5173
```

---

### سناریو 2: Backend در Sandbox، Frontend محلی

```
Backend:  https://sandbox-url...
Frontend: http://localhost:5173
```

#### تنظیمات:

**frontend/.env.local:**
```env
VITE_API_BASE_URL=https://YOUR-SANDBOX-URL
```

---

## 🔍 تست عملکرد

### 1. تست Backend API

```bash
# Health Check
curl http://localhost:8000/health

# Dashboard Stats
curl http://localhost:8000/dashboard/stats

# Scans
curl http://localhost:8000/scans

# Attacks
curl http://localhost:8000/attacks

# Vulnerabilities
curl http://localhost:8000/vulnerabilities
```

### 2. تست Frontend

باز کردن مرورگر و بررسی:

1. **Dashboard** - صفحه اصلی
   - ✅ کارت‌های آماری نمایش داده می‌شوند
   - ✅ نمودارها load می‌شوند
   - ✅ لیست Scans و Attacks نمایش داده می‌شوند

2. **Developer Tools** (F12)
   - بررسی Console → نباید خطا داشته باشد
   - بررسی Network → درخواست‌های API موفق باشند (status 200)

3. **Responsive Design**
   - تست در اندازه‌های مختلف صفحه
   - تست در mobile view (Toggle device toolbar)

---

## 🐛 عیب‌یابی (Troubleshooting)

### مشکل 1: Backend راه‌اندازی نمی‌شود

**خطا:** `ModuleNotFoundError: No module named 'fastapi'`

**راه‌حل:**
```bash
# مطمئن شوید virtual environment فعال است
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# نصب مجدد dependencies
pip install -r requirements.txt
```

---

### مشکل 2: Port 8000 قبلاً استفاده شده

**خطا:** `[Errno 48] Address already in use`

**راه‌حل:**

**Linux/Mac:**
```bash
# پیدا کردن process
lsof -i :8000

# کشتن process
kill -9 PID
```

**Windows:**
```bash
# پیدا کردن process
netstat -ano | findstr :8000

# کشتن process
taskkill /PID <PID> /F
```

**یا استفاده از port دیگر:**
```bash
uvicorn simple_api:app --port 8001
```

---

### مشکل 3: Frontend به Backend متصل نمی‌شود

**خطا در Console:** `Network Error` یا `CORS Error`

**راه‌حل:**

1. **بررسی Backend URL:**
```javascript
// frontend/src/services/api.ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
console.log('API Base URL:', API_BASE_URL);
```

2. **بررسی CORS:**
Backend باید CORS را برای Frontend فعال کرده باشد:
```python
# backend/simple_api.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

3. **تست مستقیم با curl:**
```bash
curl -H "Origin: http://localhost:5173" \
     -H "Access-Control-Request-Method: GET" \
     -X OPTIONS \
     http://localhost:8000/scans
```

---

### مشکل 4: npm install خطا می‌دهد

**خطا:** `npm ERR! code ERESOLVE`

**راه‌حل:**
```bash
# حذف node_modules و package-lock.json
rm -rf node_modules package-lock.json

# نصب مجدد با --legacy-peer-deps
npm install --legacy-peer-deps
```

---

### مشکل 5: صفحه سفید (White Screen)

**راه‌حل:**

1. **بررسی Console (F12):**
```
Look for JavaScript errors
```

2. **بررسی Build:**
```bash
npm run build
# اگر build موفق شد، مشکل در code نیست
```

3. **پاک کردن Cache:**
```bash
# پاک کردن Vite cache
rm -rf node_modules/.vite

# Restart dev server
npm run dev
```

---

## 📱 تست در موبایل

### روش 1: استفاده از Network URL

وقتی `npm run dev` اجرا می‌کنید، Vite یک Network URL هم نمایش می‌دهد:
```
➜  Network: http://192.168.1.100:5173/
```

از این URL در موبایل استفاده کنید (باید در همان شبکه Wi-Fi باشید).

---

### روش 2: استفاده از ngrok

```bash
# نصب ngrok
npm install -g ngrok

# Expose port 5173
ngrok http 5173
```

URL عمومی دریافت می‌کنید که از هر جا قابل دسترسی است.

---

## 🔐 توجهات امنیتی

### برای محیط توسعه (Development):

✅ **OK:**
- استفاده از `localhost`
- CORS برای `localhost:5173`
- Mock data
- Debug mode فعال

❌ **NOT OK for Production:**
- Hardcoded passwords
- Debug mode فعال
- CORS برای `*` (همه origins)
- بدون HTTPS

---

## 📊 معیارهای عملکرد

### Backend:
- ✅ Response Time: < 100ms
- ✅ Memory: < 100MB
- ✅ CPU: < 10%

### Frontend:
- ✅ First Paint: < 1s
- ✅ Interactive: < 2s
- ✅ Bundle Size: < 500KB (gzipped)

---

## 🎯 Checklist نهایی

### Backend:
- [ ] Python 3.12+ نصب شده
- [ ] Virtual environment ساخته شده
- [ ] Dependencies نصب شدند
- [ ] Backend روی port 8000 اجرا می‌شود
- [ ] `/health` endpoint پاسخ می‌دهد
- [ ] `/docs` قابل دسترسی است

### Frontend:
- [ ] Node.js 18+ نصب شده
- [ ] npm dependencies نصب شدند
- [ ] `.env.local` پیکربندی شده
- [ ] Dev server روی port 5173 اجرا می‌شود
- [ ] Dashboard load می‌شود
- [ ] API calls موفق هستند (بررسی در Network tab)

---

## 📧 پشتیبانی

اگر مشکلی داشتید:

1. **بررسی Logs:**
```bash
# Backend logs
tail -f backend/logs/backend-out.log

# Frontend console
F12 → Console tab
```

2. **Issue در GitHub:**
```
https://github.com/YOUR_USERNAME/SecureRedLab/issues
```

3. **Discussion:**
```
https://github.com/YOUR_USERNAME/SecureRedLab/discussions
```

---

## 🎉 موفق باشید!

اگر همه چیز درست کار کرد، باید Dashboard SecureRedLab را ببینید:
- کارت‌های آماری
- نمودارها
- لیست Scans و Attacks
- Theme switcher (Dark/Light)

**Next Steps:**
- تست API endpoints مختلف
- بررسی WebSocket connections
- Customize dashboard
- Add authentication

---

**نسخه:** 1.0.0  
**تاریخ:** 2026-01-31  
**نویسنده:** SecureRedLab Team

---

