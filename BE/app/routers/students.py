from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.crud import auth as auth_crud
from app.crud import students as student_crud
from app.crud import messages as message_crud
from app.database import get_db

router = APIRouter(prefix="/students", tags=["students"])


@router.get("/{student_id}/gpa-history", response_model=schemas.GPAHistoryResponse)
def get_student_gpa_history(
    student_id: int,
    db: Session = Depends(get_db),
):
    history = student_crud.get_gpa_history(db, student_id)
    if not history:
        raise HTTPException(status_code=404, detail="GPA history not found")
    return history


@router.get("", response_model=List[schemas.StudentListItem])
def get_all_students(
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Get all students (for managers/lecturers)"""
    role = (current_user.role or "").lower()
    if role not in {"lecturer", "manager", "admin"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return student_crud.get_all_students(db)


@router.get("/{student_id}/profile", response_model=schemas.StudentProfile)
def student_profile(student_id: int, db: Session = Depends(get_db)):
    profile = student_crud.get_student_profile(db, student_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    return profile


@router.get("/{student_id}/dashboard", response_model=schemas.DashboardStats)
def student_dashboard(student_id: int, db: Session = Depends(get_db)):
    stats = student_crud.get_dashboard_stats(db, student_id)
    if not stats:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    return stats


@router.get("/{student_id}/courses", response_model=List[schemas.CourseSummary])
def get_student_courses(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Get courses the student is enrolled in"""
    # Verify access
    role = (current_user.role or "").lower()
    if current_user.user_id != student_id and role not in {
        "lecturer",
        "manager",
        "admin",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return student_crud.get_student_courses(db, student_id)


@router.get(
    "/{student_id}/assignments", response_model=List[schemas.AssignmentWithStatus]
)
def get_student_assignments(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Get all assignments for the student with submission status"""
    if current_user.user_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return student_crud.get_student_assignments(db, student_id)


@router.get("/{student_id}/grades", response_model=List[schemas.Grade])
def get_student_grades(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Get all grades for a student"""
    role = (current_user.role or "").lower()
    if current_user.user_id != student_id and role not in {
        "lecturer",
        "manager",
        "admin",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return student_crud.get_student_grades(db, student_id)


@router.post(
    "/{student_id}/submissions",
    response_model=schemas.Submission,
    status_code=status.HTTP_201_CREATED,
)
def submit_assignment(
    student_id: int,
    payload: schemas.SubmissionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Submit an assignment"""
    if current_user.user_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    submission = student_crud.submit_assignment(db, student_id, payload)
    if not submission:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to submit assignment",
        )
    return submission


@router.post(
    "/{student_id}/enroll",
    response_model=schemas.Enrollment,
    status_code=status.HTTP_201_CREATED,
)
def enroll_in_course(
    student_id: int,
    payload: schemas.EnrollmentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Enroll in a course"""
    if current_user.user_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    enrollment = student_crud.enroll_course(db, student_id, payload)
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to enroll in course"
        )
    return enrollment


@router.get("/{student_id}/quizzes", response_model=List[schemas.QuizSummary])
def get_student_quizzes(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Get available quizzes for enrolled courses"""
    if current_user.user_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return student_crud.get_student_quizzes(db, student_id)


@router.get(
    "/{student_id}/quiz-attempts", response_model=List[schemas.QuizAttemptSummary]
)
def get_quiz_attempts(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Get quiz attempts for a student"""
    role = (current_user.role or "").lower()
    if current_user.user_id != student_id and role not in {
        "lecturer",
        "manager",
        "admin",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return student_crud.get_student_quiz_attempts(db, student_id)


@router.get("/{student_id}/messages", response_model=List[schemas.Message])
def get_messages(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Get messages for a student"""
    role = (current_user.role or "").lower()
    if current_user.user_id != student_id and role not in {
        "lecturer",
        "manager",
        "admin",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed to view these messages",
        )
    return message_crud.get_messages(db, student_id)


@router.post(
    "/{student_id}/messages",
    response_model=schemas.Message,
    status_code=status.HTTP_201_CREATED,
)
def send_message(
    student_id: int,
    payload: schemas.MessageCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Send a message"""
    if current_user.user_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )
    return message_crud.send_message(db, current_user.user_id, payload)


@router.post(
    "/{student_id}/feedback",
    response_model=schemas.Feedback,
    status_code=status.HTTP_201_CREATED,
)
def submit_feedback(
    student_id: int,
    payload: schemas.FeedbackCreate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Submit feedback for a course"""
    if current_user.user_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    from app.crud import courses as course_crud

    return course_crud.create_feedback(db, student_id, payload)


@router.get("/{student_id}/feedback", response_model=List[schemas.Feedback])
def get_student_feedbacks(
    student_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Get all feedback submitted by a student"""
    role = (current_user.role or "").lower()
    if current_user.user_id != student_id and role not in {
        "lecturer",
        "manager",
        "admin",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    from app.crud import courses as course_crud

    return course_crud.get_student_feedbacks(db, student_id)


@router.put("/{student_id}/feedback/{feedback_id}", response_model=schemas.Feedback)
def update_feedback(
    student_id: int,
    feedback_id: int,
    payload: schemas.FeedbackUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Update an existing feedback"""
    if current_user.user_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    from app.crud import courses as course_crud

    feedback = course_crud.update_feedback(db, feedback_id, student_id, payload)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Feedback not found"
        )
    return feedback


@router.put("/{student_id}/target-gpa", response_model=schemas.StudentProfile)
def set_target_gpa(
    student_id: int,
    payload: schemas.TargetGPAUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """Set target GPA for a student"""
    if current_user.user_id != student_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized"
        )

    profile = student_crud.set_target_gpa(db, student_id, payload.target_gpa)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
        )
    return profile


@router.post(
    "/{student_id}/predict",
    response_model=schemas.PredictionResult,
    status_code=status.HTTP_200_OK,
)
def predict_pass_fail(
    student_id: int,
    payload: schemas.PredictionInput,
    db: Session = Depends(get_db),
    current_user=Depends(auth_crud.get_current_active_user),
):
    """
    Generate a pass/fail prediction for a student based on academic performance metrics.

    This endpoint allows students to receive ML-based predictions about their
    academic outcomes. The prediction is based on multiple factors including
    attendance, quiz/assignment scores, and study habits.

    **Authorization Rules:**
    - Students can only predict for themselves
    - Lecturers and managers can predict for any student

    **How it works:**
    1. User submits performance metrics through the frontend form
    2. Backend validates the input data
    3. ML model processes the features and predicts GPA
    4. System determines pass/fail based on threshold (2.0)
    5. Personalized recommendations are generated
    6. Prediction is saved to database for tracking
    7. Results are returned to the frontend

    **Pass/Fail Rule:**
    - Pass: predicted_gpa >= 2.0
    - Fail: predicted_gpa < 2.0

    **Example Request:**
    ```json
    {
        "current_gpa": 3.0,
        "attendance_rate": 0.85,
        "avg_quiz_score": 75.0,
        "avg_assignment_score": 80.0,
        "late_submissions": 2,
        "courses_enrolled": 5,
        "study_hours_per_week": 12.0
    }
    ```

    **Example Response:**
    ```json
    {
        "predicted_gpa": 3.25,
        "confidence": 0.85,
        "pass_fail": "pass",
        "threshold": 2.0,
        "recommendations": "✅ You're on track to pass...",
        "model_version": "v1.0"
    }
    ```

    Args:
        student_id: The user_id of the student (from URL path)
        payload: PredictionInput with 7 required performance metrics
        db: Database session (injected)
        current_user: Authenticated user (injected)

    Returns:
        PredictionResult with predicted GPA, pass/fail status, and recommendations

    Raises:
        HTTPException 403: User not authorized to predict for this student
        HTTPException 404: Student not found
        HTTPException 422: Invalid input data (validation failed)
        HTTPException 500: Prediction service error (model loading/prediction failure)
    """
    # Authorization check: Only allow self or elevated roles
    role = (current_user.role or "").lower()
    if current_user.user_id != student_id and role not in {
        "lecturer",
        "manager",
        "admin",
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to generate predictions for this student",
        )

    # Call CRUD layer to execute prediction logic
    try:
        result = student_crud.create_prediction_for_student(db, student_id, payload)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Student not found"
            )

        return result

    except ValueError as e:
        # Input validation errors from prediction service
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}",
        )

    except RuntimeError as e:
        # Model loading or prediction errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Prediction service error: {str(e)}",
        )

    except Exception:
        # Catch-all for unexpected errors
        import logging

        logging.exception(
            f"Unexpected error in prediction endpoint for student {student_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during prediction",
        )
