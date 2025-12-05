import os
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password using bcrypt."""
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        # If stored password is plain text, compare directly
        return plain_password == hashed_password


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def get_user_by_username(db: Session, username: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.username == username).first()


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email).first()


def authenticate_user(db: Session, username: str, password: str) -> Optional[models.User]:
    # Try to find user by username first
    user = get_user_by_username(db, username)
    # If not found, try by email
    if not user:
        user = get_user_by_email(db, username)
    if not user:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


def get_user_role(db: Session, user: models.User) -> str:
    """Determine user role by checking which table (Student, Lecturer, Manager) they belong to."""
    # Check if user is a student
    student = db.query(models.Student).filter(models.Student.user_id == user.user_id).first()
    if student:
        return "student"
    
    # Check if user is a lecturer
    lecturer = db.query(models.Lecturer).filter(models.Lecturer.user_id == user.user_id).first()
    if lecturer:
        return "lecturer"
    
    # Check if user is a manager
    manager = db.query(models.Manager).filter(models.Manager.user_id == user.user_id).first()
    if manager:
        return "manager"
    
    # Default to the role stored in User table
    return (user.role or "").lower()


def get_user_profile(db: Session, user: models.User) -> schemas.UserProfile:
    """Get full user profile including role-specific information."""
    role = get_user_role(db, user)
    
    profile_data = {
        "user_id": user.user_id,
        "username": user.username,
        "email": user.email,
        "role": role,
        "full_name": "",
    }
    
    if role == "student":
        student = db.query(models.Student).filter(models.Student.user_id == user.user_id).first()
        if student:
            profile_data["full_name"] = " ".join(filter(None, [student.fname, student.lname, student.mname]))
            profile_data["student_id"] = student.student_id
            profile_data["major"] = student.major
            profile_data["current_gpa"] = float(student.current_gpa) if student.current_gpa else None
    
    elif role == "lecturer":
        lecturer = db.query(models.Lecturer).filter(models.Lecturer.user_id == user.user_id).first()
        if lecturer:
            profile_data["full_name"] = " ".join(filter(None, [lecturer.fname, lecturer.lname, lecturer.mname]))
            profile_data["title"] = lecturer.title
            profile_data["department"] = lecturer.department
    
    elif role == "manager":
        manager = db.query(models.Manager).filter(models.Manager.user_id == user.user_id).first()
        if manager:
            profile_data["full_name"] = manager.name
            profile_data["office"] = manager.office
            profile_data["position"] = manager.position
    
    return schemas.UserProfile(**profile_data)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user_by_username(db, username=username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    # Hook for future activation logic
    return current_user

