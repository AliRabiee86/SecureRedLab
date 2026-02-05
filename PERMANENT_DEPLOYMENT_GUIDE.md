# راهنمای استقرار دائمی پروژه SecureRedLab v2.0
# Permanent Deployment Guide for SecureRedLab v2.0

داداش، برای اینکه این پروژه رو برای همیشه آنلاین نگه داری، این نقشه راه توئه:

## ۱. استقرار فرانت‌بند (Frontend Deployment)
بهترین گزینه برای فرانت‌بند استفاده از **Vercel** یا **Netlify** هست (رایگان و دائمی).

1. پوشه `frontend` رو در یک مخزن GitHub جدید آپلود کن.
2. در سایت [Vercel](https://vercel.com)، پروژه رو Import کن.
3. تنظیمات بیلد:
   - **Framework Preset:** Vite
   - **Build Command:** `pnpm build` یا `npm run build`
   - **Output Directory:** `dist`
4. متغیرهای محیطی (Environment Variables) رو در پنل Vercel ست کن:
   - `VITE_API_BASE_URL`: آدرس بک‌بند تو (مثلاً `https://api.yourdomain.com`)
   - `VITE_WS_URL`: آدرس WebSocket تو (مثلاً `wss://api.yourdomain.com/ws`)

## ۲. استقرار بک‌بند (Backend Deployment)
بک‌بند چون نیاز به پردازش و دیتابیس داره، باید روی یک **VPS** (سرور مجازی) نصب بشه.

1. یک VPS تهیه کن (Ubuntu پیشنهاد میشه).
2. Docker و Docker Compose رو نصب کن.
3. فایل‌های پروژه رو روی سرور کپی کن.
4. از فایل `docker-compose.prod.yml` که برات ساختم استفاده کن:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d
   ```
5. از یک Reverse Proxy مثل **Nginx** برای هندل کردن HTTPS و دامنه استفاده کن.

## ۳. نکات مهم برای ارائه دانشگاهی
- **دامنه:** اگر می‌خوای خیلی حرفه‌ای باشه، یک دامنه `.ir` یا `.com` بخر و به Vercel وصل کن.
- **SSL:** حتماً از HTTPS استفاده کن (Vercel خودش خودکار انجام میده).
- **دیتابیس:** در فایل `.env` پسوردهای پیش‌فرض رو عوض کن تا امنیت رعایت بشه.

---

## Technical Summary (English)
- **Frontend:** React + Vite, ready for Vercel/Netlify with `vercel.json` provided.
- **Backend:** FastAPI, containerized with Docker. Use `Dockerfile.prod` and `docker-compose.prod.yml`.
- **Database:** PostgreSQL 16 (managed via Docker).
- **Real-time:** WebSocket enabled for live monitoring.

**داداش، فایل‌های پیکربندی رو توی پوشه پروژه برات گذاشتم. با اینا سایتت برای همیشه زنده می‌مونه!**
