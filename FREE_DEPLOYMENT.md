# 🆓 100% Free Cloud Deployment Guide

This guide walks you through deploying your full-stack AI Resume Intelligence application for **$0 / month** using free-tier services.

---

## 🧩 Free Tier Tech Stack Overview

| Component | Free Platform | Free Limits |
| :--- | :--- | :--- |
| **Frontend (Next.js)** | **[Vercel](https://vercel.com)** | 100% Free, Unlimited deployments, Free HTTPS |
| **Backend API (FastAPI)** | **[Render](https://render.com)** | 100% Free Web Service (512MB RAM) |
| **Database (PostgreSQL)** | **[Supabase](https://supabase.com)** or **Render Postgres** | 100% Free PostgreSQL (500MB storage) |
| **Redis Cache (Celery)** | **[Upstash Redis](https://upstash.com)** | 100% Free Serverless Redis (10,000 commands/day) |

---

## 📑 Step-by-Step Instructions

### Step 1: Push Your Project to GitHub
1. Go to [GitHub.com](https://github.com) and create a new public or private repository (e.g. `resume-scanner-app`).
2. Run these commands in your project terminal:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of AI Resume Scanner"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/resume-scanner-app.git
   git push -u origin main
   ```

---

### Step 2: Set Up Free PostgreSQL Database (Supabase)
1. Go to **[Supabase.com](https://supabase.com)** and sign up with GitHub ($0 Free Tier).
2. Click **New Project** -> Name it `resume-scanner` -> Set a password.
3. Once created, click **Project Settings (Gear Icon)** -> **Database**.
4. Copy the **URI Connection String** under *Transaction Pooler* (looks like `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:6543/postgres`).

---

### Step 3: Set Up Free Redis Cache (Upstash)
1. Go to **[Upstash.com](https://upstash.com)** and sign up with GitHub ($0 Free Tier).
2. Click **Create Database** -> Name it `resume-redis` -> Select a region close to you.
3. Under *Details*, copy the **redis:// URL** under `UPSTASH_REDIS_REST_URL` or `Connection String` (format: `redis://default:PASSWORD@endpoint.upstash.io:6379`).

---

### Step 4: Deploy Backend API on Render ($0 Free)
1. Go to **[Render.com](https://render.com)** and log in with GitHub ($0 Free Tier).
2. Click **New +** -> **Web Service**.
3. Select your GitHub repository (`resume-scanner-app`).
4. Configure settings:
   - **Name**: `resume-scanner-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**:
     ```bash
     pip install -r requirements.txt && python -m spacy download en_core_web_sm
     ```
   - **Start Command**:
     ```bash
     uvicorn app.main:app --host 0.0.0.0 --port $PORT
     ```
5. Add **Environment Variables**:
   - `DATABASE_URL`: *(Your Supabase PostgreSQL URI from Step 2)*
   - `REDIS_URL`: *(Your Upstash Redis URL from Step 3)*
   - `CELERY_BROKER_URL`: *(Your Upstash Redis URL from Step 3)*
   - `CELERY_RESULT_BACKEND`: *(Your Upstash Redis URL from Step 3)*
   - `JWT_SECRET_KEY`: *(Create any random 32-character text)*
   - `ENVIRONMENT`: `production`
   - `CORS_ALLOWED_ORIGINS`: `*`
   - `OPENAI_API_KEY`: *(Optional: Your OpenAI key if using LLM features)*
6. Click **Create Web Service**.
7. Once deployed, copy your backend URL (e.g. `https://resume-scanner-backend.onrender.com`).

---

### Step 5: Deploy Frontend on Vercel ($0 Free)
1. Go to **[Vercel.com](https://vercel.com)** and log in with GitHub ($0 Free Tier).
2. Click **Add New...** -> **Project** -> Select your `resume-scanner-app` repo.
3. Configure settings:
   - **Root Directory**: Select `frontend`
   - **Framework Preset**: `Next.js`
4. Expand **Environment Variables** and add:
   - `NEXT_PUBLIC_API_URL`: `https://resume-scanner-backend.onrender.com` *(Your Render backend URL from Step 4)*
5. Click **Deploy**.

---

## 🎉 You're Done!
Vercel will give you a free live URL (e.g., `https://resume-scanner-app.vercel.app`) with SSL HTTPS enabled automatically for **$0 / month**!
