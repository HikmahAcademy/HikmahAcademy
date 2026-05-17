import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict
from pydantic import BaseModel
import os

# Analytics data models
class InteractionLog(BaseModel):
    student_id: str
    subject: str
    lesson: str
    message: str
    response: str
    timestamp: datetime
    response_time_ms: float
    curriculum_grounded: bool
    safety_filters_active: bool

class StudentProgress(BaseModel):
    student_id: str
    total_interactions: int = 0
    total_learning_hours: float = 0.0
    subjects_studied: List[str] = []
    last_activity: Optional[datetime] = None
    average_response_time_ms: float = 0.0
    mastery_levels: Dict[str, float] = {}

class SystemMetrics(BaseModel):
    active_students: int = 0
    active_sessions: int = 0
    total_interactions_today: int = 0
    average_response_time_ms: float = 0.0
    vector_db_query_time_ms: float = 0.0
    ai_response_time_ms: float = 0.0
    uptime_percentage: float = 99.9
    collections_available: int = 0

class DailyReport(BaseModel):
    date: str
    total_students: int
    new_registrations: int
    total_interactions: int
    average_session_duration_minutes: float
    most_popular_subject: str
    top_performing_students: List[str]
    system_uptime_percentage: float

# Analytics database (in-memory, use real DB in production)
analytics_db = {
    "interactions": [],
    "student_progress": {},
    "system_metrics": {},
    "daily_reports": []
}

# File-based persistence
ANALYTICS_FILE = os.getenv("ANALYTICS_FILE", "./analytics_data.json")

def load_analytics():
    """Load analytics from file"""
    global analytics_db
    if os.path.exists(ANALYTICS_FILE):
        try:
            with open(ANALYTICS_FILE, 'r') as f:
                analytics_db = json.load(f)
        except:
            pass

def save_analytics():
    """Save analytics to file"""
    try:
        with open(ANALYTICS_FILE, 'w') as f:
            json.dump(analytics_db, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving analytics: {e}")

def log_interaction(interaction: InteractionLog):
    """Log a student-AI interaction"""
    analytics_db["interactions"].append(interaction.dict())
    
    # Update student progress
    student_id = interaction.student_id
    if student_id not in analytics_db["student_progress"]:
        analytics_db["student_progress"][student_id] = {
            "total_interactions": 0,
            "total_learning_hours": 0.0,
            "subjects_studied": [],
            "last_activity": None,
            "average_response_time_ms": 0.0,
            "mastery_levels": {}
        }
    
    progress = analytics_db["student_progress"][student_id]
    progress["total_interactions"] += 1
    progress["last_activity"] = interaction.timestamp.isoformat()
    
    # Track learning hours (approximate: 1 interaction ≈ 5 minutes)
    progress["total_learning_hours"] += 0.083
    
    # Track subjects
    if interaction.subject not in progress["subjects_studied"]:
        progress["subjects_studied"].append(interaction.subject)
    
    # Update average response time
    if progress["average_response_time_ms"] == 0:
        progress["average_response_time_ms"] = interaction.response_time_ms
    else:
        count = progress["total_interactions"]
        progress["average_response_time_ms"] = (
            (progress["average_response_time_ms"] * (count - 1) + interaction.response_time_ms) / count
        )
    
    save_analytics()

def get_student_progress(student_id: str) -> StudentProgress:
    """Get student learning progress"""
    if student_id not in analytics_db["student_progress"]:
        return StudentProgress(student_id=student_id)
    
    data = analytics_db["student_progress"][student_id]
    return StudentProgress(**data, student_id=student_id)

def get_system_metrics() -> SystemMetrics:
    """Get current system metrics"""
    interactions = analytics_db["interactions"]
    
    # Calculate metrics
    unique_students = len(analytics_db["student_progress"])
    
    # Interactions today
    today = datetime.utcnow().date()
    today_interactions = sum(
        1 for i in interactions 
        if datetime.fromisoformat(i["timestamp"]).date() == today
    )
    
    # Average response times
    avg_response_time = 0
    if interactions:
        avg_response_time = sum(i["response_time_ms"] for i in interactions) / len(interactions)
    
    return SystemMetrics(
        active_students=unique_students,
        active_sessions=0,  # Would need session tracking
        total_interactions_today=today_interactions,
        average_response_time_ms=avg_response_time,
        vector_db_query_time_ms=45.0,  # Sample
        ai_response_time_ms=3200.0,  # Sample
        uptime_percentage=99.9,
        collections_available=4
    )

def get_daily_report(days_back: int = 0) -> DailyReport:
    """Get daily analytics report"""
    target_date = (datetime.utcnow() - timedelta(days=days_back)).date()
    target_date_str = target_date.isoformat()
    
    interactions = [
        i for i in analytics_db["interactions"]
        if datetime.fromisoformat(i["timestamp"]).date() == target_date
    ]
    
    # Count new registrations (would need tracking in auth module)
    new_registrations = 0
    
    # Most popular subject
    subjects = {}
    for i in interactions:
        subject = i.get("subject", "Unknown")
        subjects[subject] = subjects.get(subject, 0) + 1
    most_popular = max(subjects.keys()) if subjects else "N/A"
    
    # Top performing students
    top_students = sorted(
        analytics_db["student_progress"].keys(),
        key=lambda s: analytics_db["student_progress"][s]["total_interactions"],
        reverse=True
    )[:5]
    
    return DailyReport(
        date=target_date_str,
        total_students=len(analytics_db["student_progress"]),
        new_registrations=new_registrations,
        total_interactions=len(interactions),
        average_session_duration_minutes=5.0,
        most_popular_subject=most_popular,
        top_performing_students=top_students,
        system_uptime_percentage=99.9
    )

def get_weekly_report() -> List[DailyReport]:
    """Get weekly analytics report"""
    reports = []
    for i in range(7):
        reports.append(get_daily_report(days_back=i))
    return reports[::-1]  # Reverse to show oldest first

# Load analytics on module import
load_analytics()
