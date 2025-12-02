from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import auth as auth_crud
from app.crud import managers as manager_crud
from app.crud import messages as message_crud
from app.database import get_db

router = APIRouter(prefix="/manager", tags=["manager"])


def require_manager(current_user):
    """Verify user is a manager"""
    role = (current_user.role or "").lower()
    if role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Manager access required")


@router.get("/profile", response_model=schemas.ManagerProfile)
def get_manager_profile(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get manager profile"""
    require_manager(current_user)
    
    profile = manager_crud.get_manager_profile(db, current_user.user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Manager not found")
    return profile


@router.get("/dashboard", response_model=schemas.ManagerDashboardStats)
def get_dashboard(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get manager dashboard statistics"""
    require_manager(current_user)
    return manager_crud.get_dashboard_stats(db)


@router.get("/students", response_model=List[schemas.StudentListItem])
def get_all_students(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get all students"""
    require_manager(current_user)
    return manager_crud.get_all_students(db)


@router.get("/lecturers", response_model=List[schemas.LecturerListItem])
def get_all_lecturers(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get all lecturers"""
    require_manager(current_user)
    return manager_crud.get_all_lecturers(db)


@router.get("/courses", response_model=List[schemas.CourseSummary])
def get_all_courses(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get all courses"""
    require_manager(current_user)
    return manager_crud.get_all_courses(db)


@router.post("/courses", response_model=schemas.CourseSummary, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Create a new course"""
    require_manager(current_user)
    return manager_crud.create_course(db, payload)


@router.put("/courses/{course_id}", response_model=schemas.CourseSummary)
def update_course(
    course_id: int,
    payload: schemas.CourseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Update a course"""
    require_manager(current_user)
    
    course = manager_crud.update_course(db, course_id, payload)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.delete("/courses/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Delete a course"""
    require_manager(current_user)
    
    if not manager_crud.delete_course(db, course_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


@router.put("/courses/{course_id}/assign-lecturer", response_model=schemas.CourseSummary)
def assign_lecturer(
    course_id: int,
    lecturer_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Assign a lecturer to a course"""
    require_manager(current_user)
    
    course = manager_crud.assign_lecturer_to_course(db, course_id, lecturer_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course or lecturer not found")
    return course


@router.get("/feedback", response_model=List[schemas.Feedback])
def get_all_feedback(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get all feedback across all courses"""
    require_manager(current_user)
    return manager_crud.get_all_feedback(db)


@router.get("/statistics/courses")
def get_course_statistics(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get course statistics"""
    require_manager(current_user)
    return manager_crud.get_course_statistics(db)


@router.get("/statistics/gpa")
def get_gpa_distribution(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get GPA distribution"""
    require_manager(current_user)
    return manager_crud.get_gpa_distribution(db)


@router.get("/messages", response_model=List[schemas.Message])
def get_messages(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get messages for manager"""
    require_manager(current_user)
    return message_crud.get_messages(db, current_user.user_id)


@router.post("/messages", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Send a message"""
    require_manager(current_user)
    return message_crud.send_message(db, current_user.user_id, payload)
