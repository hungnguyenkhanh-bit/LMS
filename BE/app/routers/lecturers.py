from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import auth as auth_crud
from app.crud import lecturers as lecturer_crud
from app.crud import courses as course_crud
from app.crud import messages as message_crud
from app.database import get_db

router = APIRouter(prefix="/lecturers", tags=["lecturers"])


@router.get("", response_model=List[schemas.LecturerListItem])
def get_all_lecturers(db: Session = Depends(get_db)):
    """Get all lecturers"""
    return lecturer_crud.get_all_lecturers(db)


@router.get("/{user_id}/profile", response_model=schemas.LecturerProfile)
def get_lecturer_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get lecturer profile"""
    profile = lecturer_crud.get_lecturer_profile(db, user_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")
    return profile


@router.get("/{user_id}/dashboard", response_model=schemas.LecturerDashboardStats)
def get_lecturer_dashboard(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get lecturer dashboard statistics"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    stats = lecturer_crud.get_dashboard_stats(db, user_id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lecturer not found")
    return stats


@router.get("/{user_id}/courses", response_model=List[schemas.CourseSummary])
def get_lecturer_courses(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get courses taught by a lecturer"""
    role = (current_user.role or "").lower()
    if current_user.user_id != user_id and role != "manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return lecturer_crud.get_lecturer_courses(db, user_id)


@router.get("/{user_id}/pending-submissions", response_model=List[schemas.Submission])
def get_pending_submissions(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get pending submissions for lecturer's courses"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return lecturer_crud.get_pending_submissions(db, user_id)


@router.get("/{user_id}/feedback", response_model=List[schemas.Feedback])
def get_lecturer_feedback(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get all feedback for lecturer's courses"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return lecturer_crud.get_course_feedback(db, user_id)


@router.post("/{user_id}/assignments", response_model=schemas.Assignment, status_code=status.HTTP_201_CREATED)
def create_assignment(
    user_id: int,
    payload: schemas.AssignmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Create an assignment"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return lecturer_crud.create_assignment(db, payload)


@router.put("/submissions/{submission_id}/grade", response_model=schemas.Submission)
def grade_submission(
    submission_id: int,
    payload: schemas.SubmissionGrade,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Grade a student submission"""
    role = (current_user.role or "").lower()
    if role not in {"lecturer", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    submission = lecturer_crud.grade_submission(db, submission_id, payload)
    if not submission:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Submission not found")
    return submission


@router.get("/{user_id}/messages", response_model=List[schemas.Message])
def get_messages(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get messages for a lecturer"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return message_crud.get_messages(db, user_id)


@router.post("/{user_id}/messages", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(
    user_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Send a message"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return message_crud.send_message(db, user_id, payload)


@router.get("/{user_id}/at-risk-students", response_model=List[schemas.AtRiskStudent])
def get_at_risk_students(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get at-risk students for lecturer's courses"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return lecturer_crud.get_at_risk_students(db, user_id)


@router.get("/{user_id}/attendance-stats", response_model=List[schemas.CourseAttendanceStat])
def get_attendance_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get attendance statistics for lecturer's courses"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return lecturer_crud.get_course_attendance_stats(db, user_id)


@router.get("/{user_id}/score-stats", response_model=List[schemas.CourseScoreStat])
def get_score_stats(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get quiz and assignment score statistics for lecturer's courses"""
    if current_user.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    return lecturer_crud.get_course_score_stats(db, user_id)
