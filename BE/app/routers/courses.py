from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import courses as course_crud
from app.database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])


@router.get("/", response_model=list[schemas.CourseSummary])
def list_courses(db: Session = Depends(get_db)):
    return course_crud.list_courses(db)


@router.get("/{course_id}", response_model=schemas.CourseDetail)
def course_detail(course_id: int, db: Session = Depends(get_db)):
    course = course_crud.get_course_detail(db, course_id)
    if not course:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Course not found")
    return course


@router.get("/{course_id}/materials", response_model=list[schemas.Material])
def course_materials(course_id: int, db: Session = Depends(get_db)):
    return course_crud.list_materials(db, course_id)


@router.get("/{course_id}/assignments", response_model=list[schemas.Assignment])
def course_assignments(course_id: int, db: Session = Depends(get_db)):
    return course_crud.list_assignments(db, course_id)


@router.post("/{course_id}/feedback", response_model=schemas.Feedback, status_code=status.HTTP_201_CREATED)
def create_feedback(course_id: int, payload: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    return course_crud.create_feedback(db, course_id, payload)

