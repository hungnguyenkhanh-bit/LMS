from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import auth as auth_crud
from app.crud import students as student_crud
from app.database import get_db

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{student_id}/profile", response_model=schemas.StudentProfile)
def student_profile(student_id: int, db: Session = Depends(get_db)):
    profile = student_crud.get_student_profile(db, student_id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return profile


@router.get("/{student_id}/dashboard", response_model=schemas.DashboardStats)
def student_dashboard(student_id: int, db: Session = Depends(get_db)):
    stats = student_crud.get_dashboard_stats(db, student_id)
    if not stats:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Student not found")
    return stats


@router.get("/{student_id}/messages", response_model=list[schemas.Message])
def get_messages(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    # Basic guard to ensure the requester is the same user
    role = (current_user.Role or "").lower()
    if current_user.User_id != student_id and role not in {"lecturer", "manager", "admin"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not allowed to view these messages")
    return student_crud.list_messages(db, student_id)


@router.post("/{student_id}/messages", response_model=schemas.Message, status_code=status.HTTP_201_CREATED)
def send_message(
    student_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    from_user_id = current_user.User_id if current_user else student_id
    return student_crud.send_message(db, from_user_id=from_user_id, payload=payload)
