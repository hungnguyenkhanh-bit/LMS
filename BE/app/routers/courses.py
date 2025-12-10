from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import auth as auth_crud
from app.crud import courses as course_crud
from app.database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("", response_model=List[schemas.CourseSummary])
def list_courses(db: Session = Depends(get_db)):
    """Get all courses"""
    return course_crud.list_courses(db)


@router.get("/{course_id}", response_model=schemas.CourseDetail)
def course_detail(course_id: int, db: Session = Depends(get_db)):
    """Get detailed course information"""
    course = course_crud.get_course_detail(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.post("", response_model=schemas.CourseSummary, status_code=status.HTTP_201_CREATED)
def create_course(
    payload: schemas.CourseCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Create a new course (manager only)"""
    role = (current_user.role or "").lower()
    if role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only managers can create courses")
    return course_crud.create_course(db, payload)


@router.put("/{course_id}", response_model=schemas.CourseSummary)
def update_course(
    course_id: int,
    payload: schemas.CourseUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Update a course (manager only)"""
    role = (current_user.role or "").lower()
    if role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only managers can update courses")
    
    course = course_crud.update_course(db, course_id, payload)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Delete a course (manager only)"""
    role = (current_user.role or "").lower()
    if role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only managers can delete courses")
    
    if not course_crud.delete_course(db, course_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")


@router.get("/{course_id}/materials", response_model=List[schemas.Material])
def course_materials(course_id: int, db: Session = Depends(get_db)):
    """Get course materials"""
    return course_crud.list_materials(db, course_id)


@router.post("/{course_id}/materials", response_model=schemas.Material, status_code=status.HTTP_201_CREATED)
def create_material(
    course_id: int,
    payload: schemas.MaterialCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Add a material to a course (lecturer only)"""
    role = (current_user.role or "").lower()
    if role not in {"lecturer", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can add materials")
    
    payload.course_id = course_id
    return course_crud.create_material(db, payload)


@router.get("/{course_id}/assignments", response_model=List[schemas.Assignment])
def course_assignments(course_id: int, db: Session = Depends(get_db)):
    """Get course assignments"""
    return course_crud.list_assignments(db, course_id)


@router.post("/{course_id}/assignments", response_model=schemas.Assignment, status_code=status.HTTP_201_CREATED)
def create_assignment(
    course_id: int,
    payload: schemas.AssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Create an assignment for a course (lecturer only)"""
    role = (current_user.role or "").lower()
    if role not in {"lecturer", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can create assignments")
    
    payload.course_id = course_id
    return course_crud.create_assignment(db, payload)


@router.get("/{course_id}/students", response_model=List[schemas.StudentListItem])
def get_enrolled_students(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get students enrolled in a course"""
    role = (current_user.role or "").lower()
    if role not in {"lecturer", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return course_crud.get_enrolled_students(db, course_id)


@router.get("/{course_id}/feedback", response_model=List[schemas.Feedback])
def get_course_feedback(course_id: int, db: Session = Depends(get_db)):
    """Get feedback for a course"""
    return course_crud.get_course_feedback(db, course_id)


@router.post("/{course_id}/feedback", response_model=schemas.Feedback, status_code=status.HTTP_201_CREATED)
def create_feedback(
    course_id: int,
    payload: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Submit feedback for a course (student only)"""
    role = (current_user.role or "").lower()
    if role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can submit feedback")
    
    payload.course_id = course_id
    return course_crud.create_feedback(db, current_user.user_id, payload)


@router.get("/{course_id}/submissions", response_model=List[schemas.SubmissionWithDetails])
def get_course_submissions(
    course_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get all submissions for a course (lecturer/manager only)"""
    role = (current_user.role or "").lower()
    if role not in {"lecturer", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return course_crud.get_course_submissions(db, course_id)


@router.post("/{course_id}/announcements", response_model=schemas.Announcement, status_code=status.HTTP_201_CREATED)
def create_announcement(
    course_id: int,
    payload: schemas.AnnouncementCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Create an announcement for a course (lecturer only)"""
    role = (current_user.role or "").lower()
    if role != "lecturer":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can post announcements")
    return course_crud.create_announcement(db, course_id, payload)
