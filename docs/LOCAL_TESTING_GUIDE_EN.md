# 🚀 SecureRedLab - Local Testing Guide (Quick Start)
## 🇬🇧 English Version

---

## ⚡ Quick Start (5 Minutes)

### Prerequisites
- Python 3.12+
- Node.js 18+
- Git

---

## 🔧 Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/YOUR_USERNAME/SecureRedLab.git
cd SecureRedLab/backend

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start backend
python simple_api.py
```

**Backend running at:** http://localhost:8000

---

## 🎨 Frontend Setup

```bash
# 1. Navigate to frontend
cd ../frontend

# 2. Install dependencies
npm install

# 3. Create .env.local
echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local

# 4. Start dev server
npm run dev
```

**Frontend running at:** http://localhost:5173

---

## ✅ Verify

1. **Backend:** http://localhost:8000/docs
2. **Frontend:** http://localhost:5173
3. **Dashboard should display:**
   - Stats cards
   - Charts
   - Scan/Attack lists

---

## 🐛 Common Issues

### Port 8000 already in use
```bash
# Kill process
lsof -i :8000  # Find PID
kill -9 <PID>  # Kill it
```

### CORS Error
Check `backend/simple_api.py`:
```python
allow_origins=["http://localhost:5173"]
```

### Frontend can't connect
Check `.env.local`:
```
VITE_API_BASE_URL=http://localhost:8000
```

---

## 📱 Mobile Testing

Use Network URL from Vite output:
```
http://192.168.1.X:5173
```

Or use ngrok:
```bash
ngrok http 5173
```

---

## 🎯 Checklist

- [ ] Backend responds at `/health`
- [ ] Frontend loads dashboard
- [ ] API calls succeed (check Network tab)
- [ ] No console errors

---

**Version:** 1.0.0  
**Date:** 2026-01-31  
**Author:** SecureRedLab Team
