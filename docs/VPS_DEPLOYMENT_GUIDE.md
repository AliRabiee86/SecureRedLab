# 🚀 SecureRedLab VPS Deployment Guide

**Complete Production Deployment Guide for VPS**

**Target Audience**: System Administrators, DevOps Engineers  
**Estimated Time**: 2-3 hours  
**Difficulty**: Intermediate

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [VPS Requirements](#vps-requirements)
3. [Initial Server Setup](#initial-server-setup)
4. [Docker Installation](#docker-installation)
5. [Application Deployment](#application-deployment)
6. [SSL Configuration](#ssl-configuration)
7. [Monitoring & Maintenance](#monitoring--maintenance)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Prerequisites

### **What You Need**
- [ ] VPS with Ubuntu 22.04 LTS (recommended)
- [ ] Domain name pointed to VPS IP
- [ ] SSH access to VPS
- [ ] Basic Linux command line knowledge

### **Recommended VPS Specifications**

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 2 vCPU | 4 vCPU |
| RAM | 4 GB | 8 GB |
| Storage | 40 GB SSD | 80 GB SSD |
| Bandwidth | 2 TB/month | 4 TB/month |

### **VPS Provider Recommendations**
- ✅ **DigitalOcean** - $24/month (4GB RAM, 2 vCPU)
- ✅ **Linode** - $24/month (4GB RAM, 2 vCPU)
- ✅ **Vultr** - $24/month (4GB RAM, 2 vCPU)
- ✅ **Hetzner** - €9.51/month (4GB RAM, 2 vCPU) - Best value

---

## 🖥️ VPS Requirements

### **Operating System**
```bash
# Recommended
Ubuntu 22.04 LTS (Jammy Jellyfish)

# Also compatible
Ubuntu 20.04 LTS (Focal Fossa)
Debian 11 (Bullseye)
```

### **Open Ports**
```bash
22   - SSH
80   - HTTP
443  - HTTPS
5432 - PostgreSQL (internal only)
6379 - Redis (internal only)
8000 - Backend API (behind Nginx)
```

---

## 🔧 Initial Server Setup

### **1. Connect to VPS**
```bash
# Replace with your VPS IP
ssh root@YOUR_VPS_IP
```

### **2. Create Non-Root User**
```bash
# Create user
adduser securelab

# Add to sudo group
usermod -aG sudo securelab

# Switch to new user
su - securelab
```

### **3. Set Up SSH Key Authentication**
```bash
# On your local machine
ssh-keygen -t ed25519 -C "securelab@yourdomain.com"

# Copy public key to VPS
ssh-copy-id securelab@YOUR_VPS_IP

# Test connection
ssh securelab@YOUR_VPS_IP
```

### **4. Disable Root SSH Login**
```bash
sudo nano /etc/ssh/sshd_config

# Change these lines:
PermitRootLogin no
PasswordAuthentication no
PubkeyAuthentication yes

# Restart SSH
sudo systemctl restart sshd
```

### **5. Configure Firewall (UFW)**
```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status
```

### **6. Update System**
```bash
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y
```

### **7. Install Essential Tools**
```bash
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    net-tools \
    ufw \
    fail2ban
```

### **8. Configure Fail2ban**
```bash
# Install
sudo apt install fail2ban -y

# Configure
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo nano /etc/fail2ban/jail.local

# Add:
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600

# Start fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## 🐳 Docker Installation

### **1. Remove Old Versions**
```bash
sudo apt remove docker docker-engine docker.io containerd runc
```

### **2. Install Docker**
```bash
# Add Docker's official GPG key
sudo apt update
sudo apt install ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

# Add repository
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Install Docker Engine
sudo apt update
sudo apt install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin -y
```

### **3. Configure Docker for Non-Root**
```bash
# Add user to docker group
sudo usermod -aG docker $USER

# Apply changes
newgrp docker

# Test
docker run hello-world
```

### **4. Configure Docker Daemon**
```bash
sudo nano /etc/docker/daemon.json

# Add:
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}

# Restart Docker
sudo systemctl restart docker
```

---

## 📦 Application Deployment

### **1. Clone Repository**
```bash
cd /home/securelab
git clone https://github.com/YOUR_USERNAME/SecureRedLab.git
cd SecureRedLab
```

### **2. Create Environment Files**

**Backend `.env`:**
```bash
cd backend
cp .env.example .env
nano .env

# Configure:
APP_NAME=SecureRedLab
DEBUG=False
SECRET_KEY=GENERATE_STRONG_RANDOM_KEY_HERE
ALGORITHM=HS256

DATABASE_URL=postgresql://securedb:STRONG_PASSWORD@postgres:5432/securedb
POSTGRES_USER=securedb
POSTGRES_PASSWORD=STRONG_PASSWORD_CHANGE_THIS
POSTGRES_DB=securedb

REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

ALLOWED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

LOG_LEVEL=INFO
```

**Frontend `.env.production`:**
```bash
cd ../frontend
nano .env.production

# Configure:
VITE_API_URL=https://api.yourdomain.com
VITE_WS_URL=wss://api.yourdomain.com/ws
```

### **3. Create Docker Compose File**
```bash
cd /home/securelab/SecureRedLab
nano docker-compose.prod.yml
```

```yaml
version: '3.8'

services:
  # PostgreSQL Database
  postgres:
    image: postgres:15-alpine
    container_name: securelab_postgres
    restart: always
    volumes:
      - postgres_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
      - POSTGRES_DB=${POSTGRES_DB}
    networks:
      - securelab_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${POSTGRES_USER}"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: securelab_redis
    restart: always
    networks:
      - securelab_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 3s
      retries: 5

  # Backend API
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: securelab_backend
    restart: always
    ports:
      - "8000:8000"
    env_file:
      - ./backend/.env
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - securelab_network
    volumes:
      - ./backend/logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Celery Worker
  celery_worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: securelab_celery_worker
    restart: always
    command: celery -A app.celery worker -l info
    env_file:
      - ./backend/.env
    depends_on:
      - backend
      - redis
    networks:
      - securelab_network
    volumes:
      - ./backend/logs:/app/logs

  # Celery Beat
  celery_beat:
    build:
      context: ./backend
      dockerfile: Dockerfile.prod
    container_name: securelab_celery_beat
    restart: always
    command: celery -A app.celery beat -l info
    env_file:
      - ./backend/.env
    depends_on:
      - backend
      - redis
    networks:
      - securelab_network
    volumes:
      - ./backend/logs:/app/logs

  # Frontend
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.prod
      args:
        - VITE_API_URL=${VITE_API_URL}
        - VITE_WS_URL=${VITE_WS_URL}
    container_name: securelab_frontend
    restart: always
    ports:
      - "3000:80"
    networks:
      - securelab_network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: securelab_nginx
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/ssl:/etc/nginx/ssl:ro
      - ./nginx/logs:/var/log/nginx
    depends_on:
      - backend
      - frontend
    networks:
      - securelab_network

networks:
  securelab_network:
    driver: bridge

volumes:
  postgres_data:
    driver: local
```

### **4. Create Dockerfiles**

**Backend Dockerfile.prod:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p /app/logs

# Run migrations and start server
CMD alembic upgrade head && \
    uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

**Frontend Dockerfile.prod:**
```dockerfile
FROM node:20-alpine AS build

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy and build
COPY . .
ARG VITE_API_URL
ARG VITE_WS_URL
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy build files
COPY --from=build /app/dist /usr/share/nginx/html

# Copy nginx config
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### **5. Create Nginx Configuration**
```bash
mkdir -p nginx
nano nginx/nginx.conf
```

```nginx
# Main configuration
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';

    access_log /var/log/nginx/access.log main;

    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;

    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=5r/m;

    # Frontend
    server {
        listen 80;
        server_name yourdomain.com www.yourdomain.com;
        
        location / {
            proxy_pass http://frontend:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }

    # Backend API
    server {
        listen 80;
        server_name api.yourdomain.com;
        
        location / {
            limit_req zone=api_limit burst=20 nodelay;
            
            proxy_pass http://backend:8000;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }
        
        location /auth/login {
            limit_req zone=login_limit burst=5 nodelay;
            
            proxy_pass http://backend:8000/auth/login;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

### **6. Build and Start Services**
```bash
cd /home/securelab/SecureRedLab

# Build images
docker compose -f docker-compose.prod.yml build

# Start services
docker compose -f docker-compose.prod.yml up -d

# Check status
docker compose -f docker-compose.prod.yml ps

# View logs
docker compose -f docker-compose.prod.yml logs -f
```

---

## 🔒 SSL Configuration

### **1. Install Certbot**
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### **2. Obtain SSL Certificate**
```bash
# Stop nginx temporarily
docker compose -f docker-compose.prod.yml stop nginx

# Get certificate
sudo certbot certonly --standalone \
    -d yourdomain.com \
    -d www.yourdomain.com \
    -d api.yourdomain.com \
    --email your@email.com \
    --agree-tos \
    --no-eff-email

# Copy certificates to project
sudo cp -r /etc/letsencrypt/live/yourdomain.com /home/securelab/SecureRedLab/nginx/ssl/
sudo chown -R securelab:securelab /home/securelab/SecureRedLab/nginx/ssl/

# Start nginx
docker compose -f docker-compose.prod.yml start nginx
```

### **3. Update Nginx for HTTPS**
```nginx
# Update nginx/nginx.conf

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com api.yourdomain.com;
    return 301 https://$host$request_uri;
}

# Frontend HTTPS
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        proxy_pass http://frontend:80;
        # ... (same as before)
    }
}

# Backend API HTTPS
server {
    listen 443 ssl http2;
    server_name api.yourdomain.com;
    
    ssl_certificate /etc/nginx/ssl/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/yourdomain.com/privkey.pem;
    
    # SSL configuration
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    location / {
        # ... (same as before)
    }
}
```

### **4. Restart Nginx**
```bash
docker compose -f docker-compose.prod.yml restart nginx
```

### **5. Set Up Auto-Renewal**
```bash
# Create renewal script
sudo nano /etc/cron.d/certbot-renewal

# Add:
0 3 * * * certbot renew --quiet --post-hook "docker compose -f /home/securelab/SecureRedLab/docker-compose.prod.yml restart nginx"
```

---

## 📊 Monitoring & Maintenance

### **1. Health Checks**
```bash
# Check all services
docker compose -f docker-compose.prod.yml ps

# Check specific service logs
docker compose -f docker-compose.prod.yml logs backend
docker compose -f docker-compose.prod.yml logs celery_worker

# Follow logs
docker compose -f docker-compose.prod.yml logs -f --tail=100
```

### **2. Database Backup**
```bash
# Create backup script
nano ~/backup_db.sh

#!/bin/bash
BACKUP_DIR="/home/securelab/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

docker exec securelab_postgres pg_dump -U securedb securedb > $BACKUP_DIR/securedb_$DATE.sql

# Keep only last 7 days
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete

# Make executable
chmod +x ~/backup_db.sh

# Add to crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * /home/securelab/backup_db.sh
```

### **3. Log Rotation**
```bash
sudo nano /etc/logrotate.d/securelab

# Add:
/home/securelab/SecureRedLab/nginx/logs/*.log {
    daily
    missingok
    rotate 14
    compress
    delaycompress
    notifempty
    create 0640 www-data adm
    sharedscripts
    postrotate
        docker compose -f /home/securelab/SecureRedLab/docker-compose.prod.yml exec nginx nginx -s reload
    endscript
}
```

### **4. System Monitoring**
```bash
# Install monitoring tools
sudo apt install htop iotop nethogs -y

# Check resource usage
htop

# Check disk usage
df -h

# Check Docker stats
docker stats

# Check network connections
sudo netstat -tulpn | grep LISTEN
```

---

## 🔧 Troubleshooting

### **Common Issues**

**1. Service Won't Start**
```bash
# Check logs
docker compose logs SERVICE_NAME

# Check if port is in use
sudo lsof -i :PORT_NUMBER

# Restart service
docker compose restart SERVICE_NAME
```

**2. Database Connection Issues**
```bash
# Check PostgreSQL
docker exec -it securelab_postgres psql -U securedb

# Check connection from backend
docker exec -it securelab_backend env | grep DATABASE_URL
```

**3. SSL Certificate Issues**
```bash
# Test certificate
sudo certbot certificates

# Renew manually
sudo certbot renew --force-renewal
```

**4. High Resource Usage**
```bash
# Check container resources
docker stats

# Limit container resources
# Add to docker-compose.prod.yml:
deploy:
  resources:
    limits:
      cpus: '2'
      memory: 2G
```

---

## ✅ Post-Deployment Checklist

- [ ] All services running (`docker compose ps`)
- [ ] SSL certificates active
- [ ] HTTPS redirects working
- [ ] API endpoints accessible
- [ ] WebSocket connections working
- [ ] Database migrations applied
- [ ] Backups scheduled
- [ ] Monitoring configured
- [ ] Firewall rules set
- [ ] fail2ban active
- [ ] Log rotation configured
- [ ] Health checks passing

---

## 📞 Support & Resources

- **Project Repository**: https://github.com/YOUR_USERNAME/SecureRedLab
- **Documentation**: `/docs` directory
- **Issues**: GitHub Issues
- **Email**: support@yourdomain.com

---

**Deployment Guide Version**: 1.0  
**Last Updated**: 2026-02-03  
**Maintained By**: SecureRedLab Team

---

## 🎉 Congratulations!

Your SecureRedLab platform is now deployed and running in production! 🚀

For ongoing maintenance and updates, refer to the [Monitoring & Maintenance](#monitoring--maintenance) section.
