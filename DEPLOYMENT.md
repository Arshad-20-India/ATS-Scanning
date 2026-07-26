# 🚀 AI Resume Intelligence — Deployment Guide

This guide covers deploying the entire full-stack application (FastAPI backend + Next.js frontend + Postgres + Redis + Celery worker) to production.

---

## 🛠️ Prerequisites
- **Git** installed on your server or machine.
- **Docker** & **Docker Compose v2** installed.
- A domain name (e.g., `resume.yourdomain.com`) pointing to your server's IP address.
- An **OpenAI API Key** (or preferred LLM provider) if utilizing live LLM bullet enhancements.

---

## 📦 Option 1: Docker Compose VPS Deployment (Recommended)
*Best for DigitalOcean Droplets, AWS EC2, Hetzner, Linode, or any Ubuntu/Debian Linux Server.*

### Step 1: Clone Repository on Server
Connect to your remote Linux server via SSH and clone your project:
```bash
ssh user@your-server-ip
git clone https://github.com/your-username/resume-scanner-COMPLETE.git
cd resume-scanner-COMPLETE
```

### Step 2: Configure Production Environment Variables
Copy `.env.example` to `.env` and set secure production secrets:
```bash
cp .env.example .env
nano .env
```

Update the following keys in `.env`:
```env
ENVIRONMENT=production
POSTGRES_USER=resume_admin
POSTGRES_PASSWORD=Use_A_Strong_Random_Password_Here_123!
POSTGRES_DB=resume_scanner_db

# Generate a strong JWT secret (e.g., via `openssl rand -hex 32`)
JWT_SECRET_KEY=e83a9f1b2c...your_strong_secret

# Set your public domain API URL for the Next.js frontend
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# LLM Config
LLM_PROVIDER=openai
LLM_MODEL_NAME=gpt-4o-mini
OPENAI_API_KEY=sk-proj-...your-actual-openai-key
```

### Step 3: Build & Launch All 5 Containers
Run Docker Compose in detached mode:
```bash
docker compose up -d --build
```

Verify that all containers are healthy:
```bash
docker compose ps
```
You will see 5 running containers:
- `postgres-1` (Port 5432)
- `redis-1` (Port 6379)
- `backend-1` (Port 8000)
- `celery-worker-1`
- `frontend-1` (Port 3000)

### Step 4: Set Up Nginx Reverse Proxy & SSL (HTTPS)
Install Nginx and Certbot on your server:
```bash
sudo apt update
sudo apt install nginx certbot python3-certbot-nginx -y
```

Create Nginx site configuration:
```bash
sudo nano /etc/nginx/sites-available/resume-scanner
```

Paste the following config (replace `yourdomain.com` with your actual domain):
```nginx
server {
    server_name yourdomain.com www.yourdomain.com;

    # Frontend Next.js app
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend FastAPI REST API
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable configuration and issue free SSL certificate via Let's Encrypt:
```bash
sudo ln -s /etc/nginx/sites-available/resume-scanner /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

🎉 **Your application is live with free HTTPS SSL at `https://yourdomain.com`!**

---

## 🌐 Option 2: Render.com / Cloud PaaS Deployment

If you prefer zero-server-maintenance hosting:

1. **Database**: Create a free PostgreSQL instance on Render or Supabase and copy the connection URI string.
2. **Redis**: Create a free Redis instance on Upstash or Render.
3. **Backend Service**:
   - Create a **Web Service** on Render pointing to your Github repo.
   - Set Build Command: `pip install -r requirements.txt && python -m spacy download en_core_web_sm`
   - Set Start Command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
   - Add Environment Variables: `DATABASE_URL`, `REDIS_URL`, `JWT_SECRET_KEY`, `OPENAI_API_KEY`.
4. **Frontend Service**:
   - Deploy `frontend/` directory to **Vercel** or **Render Static Site**.
   - Set Environment Variable: `NEXT_PUBLIC_API_URL=https://your-backend.onrender.com`.

---

## 🔒 Security Best Practices
- Keep `JWT_SECRET_KEY` secret and never commit `.env` to Git.
- Configure `CORS_ALLOWED_ORIGINS` in `.env` to restrict requests to your domain only.
- Set up automatic database backup cron jobs for PostgreSQL data volume `postgres_data`.
