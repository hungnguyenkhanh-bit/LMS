from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app import models, schemas


def list_quizzes(db: Session, course_id: Optional[int] = None) -> List[schemas.QuizSummary]:
    """Get all quizzes, optionally filtered by course"""
    query = db.query(models.Quiz)
    if course_id:
        query = query.filter(models.Quiz.course_id == course_id)
    
    quizzes = query.order_by(models.Quiz.created_at.desc()).all()
    
    result = []
    for quiz in quizzes:
        question_count = db.query(models.QuizQuestion).filter(
            models.QuizQuestion.quiz_id == quiz.quiz_id
        ).count()
        
        result.append(schemas.QuizSummary(
            id=quiz.quiz_id,
            course_id=quiz.course_id,
            title=quiz.title,
            description=quiz.description,
            duration_minutes=quiz.duration_minutes or 30,
            max_attempts=quiz.max_attempts or 1,
            start_time=quiz.start_time,
            end_time=quiz.end_time,
            question_count=question_count
        ))
    
    return result


def get_quiz(db: Session, quiz_id: int) -> Optional[schemas.QuizSummary]:
    """Get a quiz by ID"""
    quiz = db.query(models.Quiz).filter(models.Quiz.quiz_id == quiz_id).first()
    if not quiz:
        return None
    
    question_count = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.quiz_id == quiz.quiz_id
    ).count()
    
    return schemas.QuizSummary(
        id=quiz.quiz_id,
        course_id=quiz.course_id,
        title=quiz.title,
        description=quiz.description,
        duration_minutes=quiz.duration_minutes or 30,
        max_attempts=quiz.max_attempts or 1,
        start_time=quiz.start_time,
        end_time=quiz.end_time,
        question_count=question_count
    )


def get_quiz_detail(db: Session, quiz_id: int, include_answers: bool = False) -> Optional[schemas.QuizDetail]:
    """Get detailed quiz information including questions"""
    quiz = db.query(models.Quiz).filter(models.Quiz.quiz_id == quiz_id).first()
    if not quiz:
        return None
    
    questions = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.quiz_id == quiz_id
    ).all()
    
    question_list = []
    for q in questions:
        question_list.append(schemas.QuizQuestion(
            id=q.question_id,
            question_text=q.question_text,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d,
            points=float(q.points) if q.points else 1.0,
            correct_option=q.correct_option if include_answers else None
        ))
    
    return schemas.QuizDetail(
        id=quiz.quiz_id,
        course_id=quiz.course_id,
        title=quiz.title,
        description=quiz.description,
        duration_minutes=quiz.duration_minutes or 30,
        max_attempts=quiz.max_attempts or 1,
        start_time=quiz.start_time,
        end_time=quiz.end_time,
        question_count=len(questions),
        questions=question_list
    )


def create_quiz(db: Session, payload: schemas.QuizCreate) -> schemas.QuizSummary:
    """Create a new quiz"""
    quiz = models.Quiz(
        course_id=payload.course_id,
        title=payload.title,
        description=payload.description,
        duration_minutes=payload.duration_minutes,
        max_attempts=payload.max_attempts,
        start_time=payload.start_time,
        end_time=payload.end_time,
        created_at=datetime.utcnow()
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    return get_quiz(db, quiz.quiz_id)


def add_question_to_quiz(db: Session, quiz_id: int, payload: schemas.QuizQuestionCreate) -> Optional[schemas.QuizQuestion]:
    """Add a question to a quiz"""
    quiz = db.query(models.Quiz).filter(models.Quiz.quiz_id == quiz_id).first()
    if not quiz:
        return None
    
    question = models.QuizQuestion(
        quiz_id=quiz_id,
        question_text=payload.question_text,
        option_a=payload.option_a,
        option_b=payload.option_b,
        option_c=payload.option_c,
        option_d=payload.option_d,
        correct_option=payload.correct_option,
        points=Decimal(str(payload.points))
    )
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return schemas.QuizQuestion(
        id=question.question_id,
        question_text=question.question_text,
        option_a=question.option_a,
        option_b=question.option_b,
        option_c=question.option_c,
        option_d=question.option_d,
        points=float(question.points) if question.points else 1.0,
        correct_option=question.correct_option
    )


def start_quiz_attempt(db: Session, quiz_id: int, student_id: int) -> Optional[schemas.QuizAttemptResult]:
    """Start a new quiz attempt or resume an existing in-progress attempt"""
    quiz = db.query(models.Quiz).filter(models.Quiz.quiz_id == quiz_id).first()
    if not quiz:
        return None
    
    # Check for existing in-progress attempt
    existing_in_progress = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.quiz_id == quiz_id,
        models.QuizAttempt.student_id == student_id,
        models.QuizAttempt.status == "in_progress"
    ).first()
    
    if existing_in_progress:
        # Resume the existing attempt
        question_count = db.query(models.QuizQuestion).filter(
            models.QuizQuestion.quiz_id == quiz_id
        ).count()
        max_score_result = db.query(models.QuizQuestion).filter(
            models.QuizQuestion.quiz_id == quiz_id
        ).all()
        max_score = sum(float(q.points) if q.points else 1.0 for q in max_score_result)
        
        return schemas.QuizAttemptResult(
            attempt_id=existing_in_progress.attempt_id,
            quiz_id=quiz_id,
            total_questions=question_count,
            correct_answers=0,
            total_score=0.0,
            max_score=max_score,
            percentage=0.0,
            status="in_progress"
        )
    
    # Check if student has remaining attempts (only count completed attempts)
    completed_attempts = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.quiz_id == quiz_id,
        models.QuizAttempt.student_id == student_id,
        models.QuizAttempt.status == "completed"
    ).count()
    
    if completed_attempts >= (quiz.max_attempts or 1):
        return None  # No more attempts allowed
    
    # Create new attempt
    attempt = models.QuizAttempt(
        quiz_id=quiz_id,
        student_id=student_id,
        started_at=datetime.utcnow(),
        status="in_progress"
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    question_count = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.quiz_id == quiz_id
    ).count()
    
    # Calculate max score
    max_score_result = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.quiz_id == quiz_id
    ).all()
    max_score = sum(float(q.points) if q.points else 1.0 for q in max_score_result)
    
    return schemas.QuizAttemptResult(
        attempt_id=attempt.attempt_id,
        quiz_id=quiz_id,
        total_questions=question_count,
        correct_answers=0,
        total_score=0.0,
        max_score=max_score,
        percentage=0.0,
        status="in_progress"
    )


def submit_quiz_attempt(db: Session, attempt_id: int, submission: schemas.QuizSubmission) -> Optional[schemas.QuizAttemptResult]:
    """Submit answers for a quiz attempt"""
    attempt = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.attempt_id == attempt_id
    ).first()
    
    if not attempt or attempt.status == "completed":
        return None
    
    # Get quiz questions
    questions = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.quiz_id == attempt.quiz_id
    ).all()
    
    question_map = {q.question_id: q for q in questions}
    
    total_score = Decimal("0.00")
    correct_answers = 0
    max_score = Decimal("0.00")
    
    # Process each answer
    for answer in submission.answers:
        question = question_map.get(answer.question_id)
        if not question:
            continue
        
        max_score += question.points if question.points else Decimal("1.00")
        is_correct = answer.chosen_option.upper() == question.correct_option.upper()
        
        if is_correct:
            correct_answers += 1
            total_score += question.points if question.points else Decimal("1.00")
        
        # Save answer detail
        detail = models.QuizAttemptDetail(
            attempt_id=attempt_id,
            question_id=answer.question_id,
            chosen_option=answer.chosen_option,
            is_correct=is_correct
        )
        db.add(detail)
    
    # Update attempt
    attempt.total_score = total_score
    attempt.finished_at = datetime.utcnow()
    attempt.status = "completed"
    
    db.commit()
    db.refresh(attempt)
    
    percentage = float(total_score / max_score * 100) if max_score > 0 else 0.0
    
    return schemas.QuizAttemptResult(
        attempt_id=attempt.attempt_id,
        quiz_id=attempt.quiz_id,
        total_questions=len(questions),
        correct_answers=correct_answers,
        total_score=float(total_score),
        max_score=float(max_score),
        percentage=round(percentage, 2),
        status="completed"
    )


def get_quiz_attempt(db: Session, attempt_id: int) -> Optional[schemas.QuizAttemptResult]:
    """Get quiz attempt results"""
    attempt = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.attempt_id == attempt_id
    ).first()
    
    if not attempt:
        return None
    
    questions = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.quiz_id == attempt.quiz_id
    ).all()
    
    max_score = sum(float(q.points) if q.points else 1.0 for q in questions)
    
    # Count correct answers from details
    correct_count = db.query(models.QuizAttemptDetail).filter(
        models.QuizAttemptDetail.attempt_id == attempt_id,
        models.QuizAttemptDetail.is_correct == True
    ).count()
    
    total_score = float(attempt.total_score) if attempt.total_score else 0.0
    percentage = (total_score / max_score * 100) if max_score > 0 else 0.0
    
    return schemas.QuizAttemptResult(
        attempt_id=attempt.attempt_id,
        quiz_id=attempt.quiz_id,
        total_questions=len(questions),
        correct_answers=correct_count,
        total_score=total_score,
        max_score=max_score,
        percentage=round(percentage, 2),
        status=attempt.status or "unknown"
    )


def get_student_quiz_attempts(db: Session, student_id: int, quiz_id: Optional[int] = None) -> List[schemas.QuizAttemptSummary]:
    """Get all quiz attempts for a student"""
    query = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.student_id == student_id
    )
    
    if quiz_id:
        query = query.filter(models.QuizAttempt.quiz_id == quiz_id)
    
    attempts = query.order_by(models.QuizAttempt.started_at.desc()).all()
    
    result = []
    for attempt in attempts:
        quiz = attempt.quiz
        result.append(schemas.QuizAttemptSummary(
            attempt_id=attempt.attempt_id,
            quiz_id=attempt.quiz_id,
            quiz_title=quiz.title if quiz else "Unknown Quiz",
            started_at=attempt.started_at,
            finished_at=attempt.finished_at,
            total_score=float(attempt.total_score) if attempt.total_score else None,
            status=attempt.status or "unknown"
        ))
    
    return result


def get_quiz_attempt_detail(db: Session, attempt_id: int) -> Optional[schemas.QuizAttemptDetail]:
    """Get detailed quiz attempt with all answers for review"""
    attempt = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.attempt_id == attempt_id
    ).first()
    
    if not attempt:
        return None
    
    quiz = attempt.quiz
    if not quiz:
        return None
    
    # Get all questions for the quiz
    questions = db.query(models.QuizQuestion).filter(
        models.QuizQuestion.quiz_id == attempt.quiz_id
    ).all()
    
    question_map = {q.question_id: q for q in questions}
    
    # Get all answer details for this attempt
    answer_details = db.query(models.QuizAttemptDetail).filter(
        models.QuizAttemptDetail.attempt_id == attempt_id
    ).all()
    
    answers = []
    max_score = 0.0
    
    for question in questions:
        points = float(question.points) if question.points else 1.0
        max_score += points
        
        # Find the student's answer for this question
        answer_detail = next(
            (ad for ad in answer_details if ad.question_id == question.question_id),
            None
        )
        
        answers.append(schemas.QuizAttemptAnswerDetail(
            question_id=question.question_id,
            question_text=question.question_text,
            option_a=question.option_a,
            option_b=question.option_b,
            option_c=question.option_c,
            option_d=question.option_d,
            chosen_option=answer_detail.chosen_option if answer_detail else "",
            correct_option=question.correct_option,
            is_correct=answer_detail.is_correct if answer_detail else False,
            points=points
        ))
    
    total_score = float(attempt.total_score) if attempt.total_score else 0.0
    correct_count = sum(1 for a in answers if a.is_correct)
    percentage = (total_score / max_score * 100) if max_score > 0 else 0.0
    
    return schemas.QuizAttemptDetail(
        attempt_id=attempt.attempt_id,
        quiz_id=attempt.quiz_id,
        quiz_title=quiz.title,
        total_questions=len(questions),
        correct_answers=correct_count,
        total_score=total_score,
        max_score=max_score,
        percentage=round(percentage, 2),
        status=attempt.status or "unknown",
        started_at=attempt.started_at,
        finished_at=attempt.finished_at,
        answers=answers
    )
