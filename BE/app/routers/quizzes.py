from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.crud import quizzes as quiz_crud
from app.database import get_db

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("/course/{course_id}", response_model=schemas.QuizPayload)
def get_quiz(course_id: int, db: Session = Depends(get_db)):
    questions = quiz_crud.get_quiz_questions(db, course_id)
    return schemas.QuizPayload(course_id=course_id, questions=questions)


@router.post("/course/{course_id}/submit", response_model=schemas.QuizSubmissionResult)
def submit_quiz(course_id: int, payload: schemas.QuizSubmission, db: Session = Depends(get_db)):
    return quiz_crud.submit_answers(db, course_id, payload)

