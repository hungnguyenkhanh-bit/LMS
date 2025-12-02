from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app import schemas
from app.crud import auth as auth_crud
from app.crud import quizzes as quiz_crud
from app.database import get_db

router = APIRouter(prefix="/quizzes", tags=["quizzes"])


@router.get("", response_model=List[schemas.QuizSummary])
def list_quizzes(
    course_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    """Get all quizzes, optionally filtered by course"""
    return quiz_crud.list_quizzes(db, course_id)


@router.post("", response_model=schemas.QuizSummary, status_code=status.HTTP_201_CREATED)
def create_quiz(
    payload: schemas.QuizCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Create a new quiz (lecturer only)"""
    role = (current_user.role or "").lower()
    if role not in {"lecturer", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can create quizzes")
    return quiz_crud.create_quiz(db, payload)


# ============ Attempt routes (must be before /{quiz_id} to avoid conflicts) ============
@router.post("/attempts/{attempt_id}/submit", response_model=schemas.QuizAttemptResult)
def submit_quiz(
    attempt_id: int,
    payload: schemas.QuizSubmission,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Submit answers for a quiz attempt"""
    result = quiz_crud.submit_quiz_attempt(db, attempt_id, payload)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot submit quiz. Attempt may be already completed or not found."
        )
    return result


@router.get("/attempts/{attempt_id}/detail", response_model=schemas.QuizAttemptDetail)
def get_attempt_detail(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get detailed quiz attempt with all answers for review"""
    result = quiz_crud.get_quiz_attempt_detail(db, attempt_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    return result


@router.get("/attempts/{attempt_id}", response_model=schemas.QuizAttemptResult)
def get_attempt(
    attempt_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get quiz attempt results"""
    result = quiz_crud.get_quiz_attempt(db, attempt_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Attempt not found")
    return result


@router.get("/student/{student_id}/attempts", response_model=List[schemas.QuizAttemptSummary])
def get_student_attempts(
    student_id: int,
    quiz_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get all quiz attempts for a student"""
    role = (current_user.role or "").lower()
    if current_user.user_id != student_id and role not in {"lecturer", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")
    
    return quiz_crud.get_student_quiz_attempts(db, student_id, quiz_id)


# ============ Quiz ID routes (parameterized, must be after specific routes) ============
@router.get("/{quiz_id}", response_model=schemas.QuizDetail)
def get_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Get quiz details with questions (answers hidden for students)"""
    role = (current_user.role or "").lower()
    include_answers = role in {"lecturer", "manager"}
    
    quiz = quiz_crud.get_quiz_detail(db, quiz_id, include_answers=include_answers)
    if not quiz:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return quiz


@router.post("/{quiz_id}/questions", response_model=schemas.QuizQuestion, status_code=status.HTTP_201_CREATED)
def add_question(
    quiz_id: int,
    payload: schemas.QuizQuestionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Add a question to a quiz (lecturer only)"""
    role = (current_user.role or "").lower()
    if role not in {"lecturer", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only lecturers can add questions")
    
    question = quiz_crud.add_question_to_quiz(db, quiz_id, payload)
    if not question:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Quiz not found")
    return question


@router.post("/{quiz_id}/start", response_model=schemas.QuizAttemptResult)
def start_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user)
):
    """Start a quiz attempt (student only)"""
    role = (current_user.role or "").lower()
    if role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only students can take quizzes")
    
    attempt = quiz_crud.start_quiz_attempt(db, quiz_id, current_user.user_id)
    if not attempt:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Cannot start quiz. You may have reached the maximum number of attempts."
        )
    return attempt