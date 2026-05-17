# 📚 Student Authentication & Progress Setup Guide

## 1. Deploy to Production (Railway)

### Step 1: Go to Railway.app
```
https://railway.app
```

### Step 2: Login with GitHub
- Click "Login with GitHub"
- Authorize Railway access to your account

### Step 3: Create New Project
```
1. Click "New Project"
2. Select "Deploy from GitHub Repo"
3. Choose: HikmahAcademy/HikmahAcademy
4. Click "Deploy Now"
```

### Step 4: Configure Environment Variables
In Railway dashboard, set these variables:

```
GOOGLE_API_KEY = [Your API key from aistudio.google.com/apikey]
CHROMA_DB_PATH = /app/chroma_db
SECRET_KEY = [Generate secure key: python -c "import secrets; print(secrets.token_hex(32))"]
VITE_API_URL = https://[your-railway-domain].railway.app
```

### Step 5: Monitor Deployment
- Watch build progress in Railway dashboard
- Wait 3-5 minutes for full deployment
- Get your live URL when ready

---

## 2. Add Curriculum Materials

### Create Directory Structure
```bash
mkdir -p backend/data/curriculum/{mathematics,english,science}
mkdir -p backend/data/islamic_reference
```

### Add PDF/Text Files
```bash
# Mathematics curriculum
cp cambridge_math_y4_textbook.pdf backend/data/curriculum/mathematics/
cp fractions_decimals_guide.pdf backend/data/curriculum/mathematics/

# English curriculum
cp english_comprehension.pdf backend/data/curriculum/english/
cp reading_strategies.txt backend/data/curriculum/english/

# Islamic reference
cp quran_tajweed_guide.pdf backend/data/islamic_reference/
cp islamic_studies_notes.txt backend/data/islamic_reference/
```

### Ingest Curriculum into ChromaDB
```bash
# SSH into your Railway backend or run locally
cd backend
python ingest.py
```

**Output:**
```
============================================================
🎓 AL-HIKMAH ACADEMY - CURRICULUM INGESTION
============================================================

📚 Processing cambridge_math_y4...
   Found 5 files
   ➜ Ingesting: cambridge_math_y4_textbook.pdf ✅ (24 chunks)
   ➜ Ingesting: fractions_decimals_guide.pdf ✅ (8 chunks)
   ...
📚 Processing islamic_studies_verified...
   ...

✅ INGESTION COMPLETE
   Total files processed: 12
   Collections created: 4

📊 COLLECTION SUMMARY:
   • cambridge_math_y4: 542 documents
   • islamic_studies_verified: 287 documents
   • cambridge_english_y4: 421 documents
   • science_y4: 356 documents
```

---

## 3. Student Authentication

### Register New Student
```bash
curl -X POST https://your-railway-domain.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "student_id": "STU-001",
    "email": "student@example.com",
    "password": "secure_password",
    "full_name": "Ahmed Hassan"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "student_id": "STU-001",
  "expires_in": 1800
}
```

### Student Login
```bash
curl -X POST https://your-railway-domain.railway.app/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student@example.com",
    "password": "secure_password"
  }'
```

### Get Student Profile
```bash
curl -X GET https://your-railway-domain.railway.app/api/auth/profile \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## 4. Custom Domain Setup (Optional)

### In Railway Dashboard:
```
1. Go to your project
2. Click "Domains" tab
3. Click "Add Domain"
4. Enter your custom domain: academy.yourdomain.com
5. Follow DNS instructions (CNAME record)
6. Wait for SSL certificate (auto-provisioned)
```

### Your Academy URLs:
```
🖥️  https://academy.yourdomain.com
🔗 https://academy.yourdomain.com/api/docs
📚 https://academy.yourdomain.com/api/subjects
```

---

## 5. Monitoring & Analytics

### View System Metrics
```bash
curl https://your-railway-domain.railway.app/api/analytics/system/metrics
```

### Get Student Progress
```bash
curl https://your-railway-domain.railway.app/api/analytics/student/STU-001/progress \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Daily Analytics Report
```bash
curl https://your-railway-domain.railway.app/api/analytics/report/daily
```

### View Backend Logs
In Railway Dashboard:
```
1. Click your project
2. Select "Backend" service
3. Click "Logs" tab
4. View real-time logs
```

---

## 6. Local Testing Before Production

### Setup Local Environment
```bash
git clone https://github.com/HikmahAcademy/HikmahAcademy.git
cd HikmahAcademy

# Create environment
cp .env.example .env
# Edit .env with your GOOGLE_API_KEY

# Install dependencies
cd backend
pip install -r requirements.txt
cd ..

cd frontend
npm install
cd ..
```

### Run Docker Compose Locally
```bash
docker-compose up --build

# In another terminal, ingest curriculum
docker-compose exec backend python ingest.py

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:8000/api/subjects
```

### Access Local Dashboard
```
http://localhost          # Frontend
http://localhost:8000     # Backend API
http://localhost:8000/docs  # Interactive API Docs
```

---

## 7. Production Checklist

- [ ] ✅ Repository pushed to GitHub
- [ ] ✅ Railway project created
- [ ] ✅ Environment variables configured
- [ ] ✅ Google API key set
- [ ] ✅ Curriculum PDFs added and ingested
- [ ] ✅ Authentication tested
- [ ] ✅ API endpoints verified
- [ ] ✅ Custom domain configured (optional)
- [ ] ✅ SSL certificate active
- [ ] ✅ Monitoring dashboard checked
- [ ] ✅ Daily analytics report generated

---

## 8. Student Onboarding

### Share With Students
```
Academy Portal: https://your-domain.railway.app
Support Email: support@alhikmahacademy.com
API Docs: https://your-domain.railway.app/api/docs
```

### First-Time Setup
1. Visit academy portal
2. Click "Register"
3. Enter email and create password
4. Complete profile
5. Select courses
6. Start learning!

---

## 📞 Support & Troubleshooting

### Common Issues

**1. API Key Not Working**
```bash
# Check env variables in Railway
railway variables list
```

**2. ChromaDB Not Initialized**
```bash
# SSH into backend and run ingestion
cd backend && python ingest.py
```

**3. Students Can't Login**
- Check JWT SECRET_KEY is set
- Verify email/password are correct
- Check token expiration

**4. AI Response Slow**
- Check Google API quota
- Verify ChromaDB query performance
- Monitor Railway CPU/Memory usage

---

**✅ Your Al-Hikmah Academy is now fully operational!**

🎓 Ready to serve students!
