# Al-Hikmah Academy - Live Deployment Guide

## 🚀 Deploy to Railway (Recommended - 2 minutes)

Railway is the fastest way to deploy both frontend and backend.

### Step 1: Connect Your Repository
```bash
npm install -g @railway/cli
railway login
railway link
```

### Step 2: Configure Environment Variables
```bash
railway variables set GOOGLE_API_KEY=your-google-api-key
railway variables set CHROMA_DB_PATH=/app/chroma_db
```

### Step 3: Deploy
```bash
railway up
```

**Your app will be live at:** `https://your-project.railway.app`

---

## 🐳 Deploy with Docker (Your Machine)

### Quick Start:
```bash
# Clone repository
git clone https://github.com/HikmahAcademy/HikmahAcademy.git
cd HikmahAcademy

# Create .env file
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Deploy
docker-compose up --build
```

**Access:**
- Frontend: http://localhost
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## ☁️ Deploy to Heroku

### Prerequisites:
- Heroku account & CLI installed
- Docker support enabled

### Deployment:
```bash
heroku login
heroku create alhikmah-academy
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set GOOGLE_API_KEY=your-key

# Deploy backend
git subtree push --prefix backend heroku main

# Deploy frontend separately or use monorepo setup
```

---

## 🚀 Deploy to Render

### Step 1: Connect GitHub
- Go to https://render.com
- New → Web Service
- Connect your GitHub repo

### Step 2: Configure Build & Start Commands
```
Build Command: npm install && npm run build
Start Command: npm run preview
```

### Step 3: Set Environment Variables
```
GOOGLE_API_KEY = your-google-api-key
VITE_API_URL = https://your-backend.onrender.com
```

---

## ☁️ Deploy to AWS (ECS)

### Backend Deployment:
```bash
# Push Docker image to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t alhikmah-backend ./backend
docker tag alhikmah-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/alhikmah-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/alhikmah-backend:latest
```

### Frontend Deployment:
```bash
# Build and deploy to S3 + CloudFront
npm run build
aws s3 sync dist/ s3://your-bucket/
```

---

## 📊 Monitoring & Logging

### View Logs:
```bash
# Docker Compose
docker-compose logs -f backend
docker-compose logs -f frontend

# Railway
railway logs

# Heroku
heroku logs --tail
```

### Health Check:
```bash
curl http://localhost:8000/api/health
```

---

## ✅ Verification Checklist

- [ ] Frontend loads at deployment URL
- [ ] Chat API responds at `/api/chat`
- [ ] Curriculum database ingested in ChromaDB
- [ ] Google API key configured
- [ ] CORS enabled for frontend domain
- [ ] Environment variables set
- [ ] SSL/TLS certificate active

---

## 🎯 Recommended: Railway + GitHub Actions

This `.github/workflows/deploy.yml` automates deployment on every push to main:

```bash
# Set GitHub secrets:
# - RAILWAY_TOKEN
# - DOCKER_USERNAME
# - DOCKER_PASSWORD

git add .
git commit -m "Deploy to production"
git push origin main
# ✅ Automatic deployment triggered!
```

---

## 📞 Support

For deployment issues:
- Check logs: `docker-compose logs`
- Verify API: `curl http://localhost:8000/docs`
- Check environment: `docker-compose exec backend env | grep GOOGLE`

**You're live! 🎉**
