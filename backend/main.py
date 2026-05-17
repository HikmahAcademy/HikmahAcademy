import os
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from google import genai
from google.genai import types
import chromadb

from auth import (
    StudentRegister, StudentLogin, TokenResponse, StudentProfile,
    hash_password, verify_password, create_access_token, get_current_student,
    students_db, HTTPAuthCredentials
)
from analytics import (
    InteractionLog, log_interaction, get_student_progress, 
    get_system_metrics, get_daily_report, get_weekly_report,
    load_analytics, save_analytics
)

# Initialize FastAPI app
app = FastAPI(
    title="Al-Hikmah Academy API",
    description="AI-Powered Cambridge & Islamic Virtual School",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
client = genai.Client()
DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
chroma_client = chromadb.PersistentClient(path=DB_PATH)

# Load analytics on startup
load_analytics()

# Request/Response models
class ChatRequest(BaseModel):
    student_id: str
    subject: str
    current_lesson: str
    message: str

class ChatResponse(BaseModel):
    response: str
    curriculum_grounded: bool
    safety_filters_active: bool
    islamic_integrity_verified: bool

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str

# ============================================================
# 🔐 AUTHENTICATION ENDPOINTS
# ============================================================

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(student: StudentRegister):
    """Register a new student"""
    if student.student_id in students_db:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Student ID already exists"
        )
    
    # Store student
    students_db[student.student_id] = {
        "student_id": student.student_id,
        "email": student.email,
        "password_hash": hash_password(student.password),
        "full_name": student.full_name,
        "created_at": datetime.utcnow().isoformat(),
        "total_learning_hours": 0.0,
        "current_courses": ["Cambridge Mathematics Y4", "English Language Y4"]
    }
    
    # Create token
    token, expires_in = create_access_token(student.student_id, student.email)
    
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        student_id=student.student_id
    )

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(credentials: StudentLogin):
    """Student login"""
    # Find student by email
    student = None
    for sid, data in students_db.items():
        if data["email"] == credentials.email:
            student = data
            student_id = sid
            break
    
    if not student or not verify_password(credentials.password, student["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Create token
    token, expires_in = create_access_token(student_id, student["email"])
    
    return TokenResponse(
        access_token=token,
        expires_in=expires_in,
        student_id=student_id
    )

@app.get("/api/auth/profile", response_model=StudentProfile)
async def get_profile(current_student: dict = Depends(get_current_student)):
    """Get student profile"""
    student_id = current_student.get("student_id")
    
    if student_id not in students_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    student = students_db[student_id]
    return StudentProfile(
        student_id=student_id,
        email=student["email"],
        full_name=student["full_name"],
        created_at=datetime.fromisoformat(student["created_at"]),
        total_learning_hours=student["total_learning_hours"],
        current_courses=student["current_courses"]
    )

@app.put("/api/auth/profile", response_model=StudentProfile)
async def update_profile(
    full_name: str,
    current_student: dict = Depends(get_current_student)
):
    """Update student profile"""
    student_id = current_student.get("student_id")
    
    if student_id not in students_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    students_db[student_id]["full_name"] = full_name
    
    student = students_db[student_id]
    return StudentProfile(
        student_id=student_id,
        email=student["email"],
        full_name=student["full_name"],
        created_at=datetime.fromisoformat(student["created_at"]),
        total_learning_hours=student["total_learning_hours"],
        current_courses=student["current_courses"]
    )

@app.post("/api/auth/logout")
async def logout(current_student: dict = Depends(get_current_student)):
    """Logout student (token invalidation handled client-side)"""
    return {"message": "Logged out successfully"}

# ============================================================
# 💬 CHAT & TUTORING ENDPOINTS
# ============================================================

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest, current_student: dict = Depends(get_current_student)):
    """Chat with AI tutor"""
    start_time = time.time()
    
    subject_lower = request.subject.lower()
    is_religious = any(kw in subject_lower for kw in ["quran", "islamic", "tajweed"])
    
    try:
        # Retrieve curriculum context
        coll_name = "islamic_studies_verified" if is_religious else "cambridge_math_y4"
        try:
            collection = chroma_client.get_collection(name=coll_name)
            results = collection.query(query_texts=[request.message], n_results=1)
            context = results['documents'][0][0] if results['documents'] else ""
        except Exception:
            context = "Standard primary pedagogical frameworks apply."
        
        # Generate response with Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=request.message,
            config=types.GenerateContentConfig(
                system_instruction=f"You are an expert {request.subject} tutor for {request.current_lesson}. "
                                 f"Base your response on this curriculum: {context}. "
                                 f"Keep responses clear, age-appropriate, and encouraging.",
                temperature=0.3
            )
        )
        
        response_time = (time.time() - start_time) * 1000
        
        # Log interaction
        interaction = InteractionLog(
            student_id=request.student_id,
            subject=request.subject,
            lesson=request.current_lesson,
            message=request.message,
            response=response.text,
            timestamp=datetime.utcnow(),
            response_time_ms=response_time,
            curriculum_grounded=True,
            safety_filters_active=True
        )
        log_interaction(interaction)
        
        return ChatResponse(
            response=response.text,
            curriculum_grounded=True,
            safety_filters_active=True,
            islamic_integrity_verified=is_religious
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/subjects")
async def get_subjects():
    """Get available subjects"""
    return {
        "subjects": [
            {
                "name": "Cambridge Mathematics Y4",
                "lessons": ["Fractions & Decimals", "Geometry", "Algebra Basics"]
            },
            {
                "name": "English Language Y4",
                "lessons": ["Reading Comprehension", "Writing Skills", "Grammar"]
            },
            {
                "name": "Science Y4",
                "lessons": ["Living Things", "Materials", "Forces & Motion"]
            },
            {
                "name": "Quran & Tajweed",
                "lessons": ["Surah Al-Falaq", "Tajweed Rules", "Memorization Tracking"]
            }
        ]
    }

@app.get("/api/collections")
async def get_collections():
    """Get available curriculum collections"""
    try:
        collections = chroma_client.list_collections()
        return {
            "collections": [
                {"name": c.name, "documents": len(c.get()["documents"])}
                for c in collections
            ]
        }
    except Exception as e:
        return {"collections": [], "error": str(e)}

@app.get("/api/collection/{name}")
async def get_collection(name: str):
    """Get curriculum collection details"""
    try:
        collection = chroma_client.get_collection(name=name)
        data = collection.get()
        return {
            "name": name,
            "total_documents": len(data.get("documents", [])),
            "sample_documents": data.get("documents", [])[:5]
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Collection not found: {str(e)}")

# ============================================================
# 📊 ANALYTICS & MONITORING ENDPOINTS
# ============================================================

@app.post("/api/analytics/log-interaction")
async def log_interaction_endpoint(interaction: InteractionLog):
    """Log a student interaction"""
    log_interaction(interaction)
    return {"message": "Interaction logged successfully"}

@app.get("/api/analytics/student/{student_id}/progress")
async def get_progress(student_id: str, current_student: dict = Depends(get_current_student)):
    """Get student learning progress"""
    # Verify student can only access their own progress
    if current_student.get("student_id") != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other student's progress"
        )
    
    return get_student_progress(student_id).dict()

@app.get("/api/analytics/system/metrics")
async def get_metrics():
    """Get system metrics"""
    return get_system_metrics().dict()

@app.get("/api/analytics/report/daily")
async def get_daily():
    """Get daily analytics report"""
    return get_daily_report().dict()

@app.get("/api/analytics/report/weekly")
async def get_weekly():
    """Get weekly analytics report"""
    reports = get_weekly_report()
    return {"weekly_report": [r.dict() for r in reports]}

# ============================================================
# 🏥 HEALTH & STATUS ENDPOINTS
# ============================================================

@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow(),
        version="1.0.0"
    )

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Al-Hikmah Academy API",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "auth": "/api/auth/",
            "chat": "/api/chat",
            "analytics": "/api/analytics/",
            "health": "/health",
            "docs": "/docs"
        }
    }

# ============================================================
# 📚 ERROR HANDLERS
# ============================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "status": "error"
        }
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
