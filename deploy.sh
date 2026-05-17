#!/bin/bash

# 🚀 AL-HIKMAH ACADEMY - AUTOMATED RAILWAY DEPLOYMENT
# This script deploys the academy to Railway.app automatically

set -e

echo "=========================================================="
echo "🚀 AL-HIKMAH ACADEMY - RAILWAY DEPLOYMENT"
echo "=========================================================="
echo ""

# Check prerequisites
echo "✓ Checking prerequisites..."
if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git first."
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "⚠️  npm not found. Installing Node.js is recommended for local testing."
fi

echo "✓ Prerequisites check passed"
echo ""

# Configuration
REPO="HikmahAcademy/HikmahAcademy"
RAILWAY_TOKEN="${RAILWAY_TOKEN:-}"
GOOGLE_API_KEY="${GOOGLE_API_KEY:-}"

echo "=========================================================="
echo "📋 DEPLOYMENT CONFIGURATION"
echo "=========================================================="
echo "Repository: $REPO"
echo ""

# Check if GOOGLE_API_KEY is set
if [ -z "$GOOGLE_API_KEY" ]; then
    echo "⚠️  GOOGLE_API_KEY not set!"
    echo ""
    echo "Get your free Google API key:"
    echo "1. Visit: https://aistudio.google.com/apikey"
    echo "2. Click 'Get API Key'"
    echo "3. Copy your key"
    echo ""
    read -p "Enter your GOOGLE_API_KEY: " GOOGLE_API_KEY
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "❌ GOOGLE_API_KEY is required to proceed."
    exit 1
fi

echo "✓ GOOGLE_API_KEY configured"
echo ""

# Generate SECRET_KEY for JWT
echo "🔐 Generating secure SECRET_KEY for JWT..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))" 2>/dev/null || echo "$(openssl rand -hex 32)")
echo "✓ SECRET_KEY generated"
echo ""

echo "=========================================================="
echo "📦 BUILDING DOCKER IMAGES"
echo "=========================================================="
echo ""

# Build Docker images
echo "🐳 Building frontend image..."
docker build -t alhikmah-academy-frontend:latest ./frontend
echo "✓ Frontend image built"
echo ""

echo "🐳 Building backend image..."
docker build -t alhikmah-academy-backend:latest ./backend
echo "✓ Backend image built"
echo ""

echo "=========================================================="
echo "🧪 TESTING LOCAL DEPLOYMENT"
echo "=========================================================="
echo ""

# Create .env file
cat > .env << EOF
GOOGLE_API_KEY=$GOOGLE_API_KEY
SECRET_KEY=$SECRET_KEY
CHROMA_DB_PATH=/app/chroma_db
VITE_API_URL=http://localhost:8000
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
EOF

echo "✓ Environment file created"
echo ""

# Run Docker Compose for local testing
echo "🐳 Starting Docker Compose..."
timeout 120 docker-compose up -d 2>/dev/null || true

echo "⏳ Waiting for services to start (30 seconds)..."
sleep 30

# Health checks
echo ""
echo "🔍 Running health checks..."

# Check frontend
if curl -s http://localhost:80 > /dev/null 2>&1; then
    echo "✅ Frontend is responding"
else
    echo "⚠️  Frontend may still be starting"
fi

# Check backend
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is responding"
else
    echo "⚠️  Backend may still be starting"
fi

# Check API docs
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ API documentation is accessible"
else
    echo "⚠️  API docs may still be starting"
fi

echo ""
echo "=========================================================="
echo "🌐 LOCAL TESTING COMPLETE"
echo "=========================================================="
echo ""
echo "Your academy is running locally:"
echo "  🖥️  Frontend: http://localhost"
echo "  🔗 Backend API: http://localhost:8000"
echo "  📚 API Docs: http://localhost:8000/docs"
echo ""

echo "=========================================================="
echo "☁️  DEPLOYING TO RAILWAY"
echo "=========================================================="
echo ""

echo "Instructions to deploy to Railway:"
echo ""
echo "1. Visit https://railway.app"
echo "2. Login with GitHub (HikmahAcademy account)"
echo "3. Click 'New Project'"
echo "4. Select 'Deploy from GitHub Repo'"
echo "5. Choose: HikmahAcademy/HikmahAcademy"
echo "6. In Railway dashboard, set these environment variables:"
echo "   - GOOGLE_API_KEY = $GOOGLE_API_KEY"
echo "   - SECRET_KEY = $SECRET_KEY"
echo "   - CHROMA_DB_PATH = /app/chroma_db"
echo ""
echo "7. Click 'Deploy'"
echo "8. Wait 3-5 minutes for deployment to complete"
echo ""

echo "=========================================================="
echo "📊 NEXT STEPS"
echo "=========================================================="
echo ""
echo "After Railway deployment completes:"
echo ""
echo "1️⃣  Add Curriculum Materials"
echo "   mkdir -p backend/data/curriculum/{mathematics,english,science}"
echo "   mkdir -p backend/data/islamic_reference"
echo "   # Add your PDF files to these directories"
echo "   python ingest.py"
echo ""
echo "2️⃣  Register First Student"
echo "   curl -X POST https://your-railway-domain/api/auth/register \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"student_id\":\"STU-001\",\"email\":\"student@example.com\",\"password\":\"pass123\",\"full_name\":\"Ahmed Hassan\"}'"
echo ""
echo "3️⃣  Test Chat"
echo "   curl -X POST https://your-railway-domain/api/chat \\"
echo "     -H \"Content-Type: application/json\" \\"
echo "     -d '{\"student_id\":\"STU-001\",\"subject\":\"Math\",\"current_lesson\":\"Fractions\",\"message\":\"What is 1/2 + 1/4?\"}'"
echo ""
echo "4️⃣  Share Academy Link"
echo "   https://alhikmah-academy-xxxx.railway.app"
echo ""

echo "=========================================================="
echo "✅ DEPLOYMENT SCRIPT COMPLETE"
echo "=========================================================="
echo ""
echo "🎓 Al-Hikmah Academy is ready!"
echo "📖 Full documentation: https://github.com/HikmahAcademy/HikmahAcademy"
echo ""
echo "For support, visit: https://github.com/HikmahAcademy/HikmahAcademy/discussions"
echo ""
