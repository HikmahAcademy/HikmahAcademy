import os
import jwt
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthCredentials

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Pydantic models
class StudentRegister(BaseModel):
    student_id: str
    email: EmailStr
    password: str
    full_name: str

class StudentLogin(BaseModel):
    email: EmailStr
    password: str

class StudentProfile(BaseModel):
    student_id: str
    email: str
    full_name: str
    created_at: datetime
    total_learning_hours: float = 0.0
    current_courses: list = []

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    student_id: str

# In-memory student database (Replace with real DB in production)
students_db = {}

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(student_id: str, email: str) -> tuple[str, int]:
    expires = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "student_id": student_id,
        "email": email,
        "exp": expires,
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token, ACCESS_TOKEN_EXPIRE_MINUTES * 60

def verify_token(credentials: HTTPAuthCredentials) -> dict:
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        student_id: str = payload.get("student_id")
        if student_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

def get_current_student(credentials: HTTPAuthCredentials = Depends(security)) -> dict:
    return verify_token(credentials)
