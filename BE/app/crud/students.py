from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app import models, schemas


def _full_name(student: models.Student) -> str:
    return " ".join(filter(None, [student.fname, student.mname, student.lname]))


def _find_student(db: Session, student_id: int) -> Optional[models.Student]:
    """Find student by student_id or user_id"""
    student = db.query(models.Student).filter(models.Student.student_id == student_id).first()
    if student:
        return student
    return db.query(models.Student).filter(models.Student.user_id == student_id).first()


def get_all_students(db: Session) -> List[schemas.StudentListItem]:
    """Get all students"""
    students = db.query(models.Student).all()
    result = []
    for student in students:
        user = student.user
        result.append(schemas.StudentListItem(
            user_id=student.user_id,
            student_id=student.student_id,
            full_name=_full_name(student),
            major=student.major,
            current_gpa=float(student.current_gpa) if student.current_gpa else 0.0,
            email=user.email if user else None
        ))
    return result


def get_student_profile(db: Session, student_id: int) -> Optional[schemas.StudentProfile]:
    student = _find_student(db, student_id)
    if not student:
        return None
    user = student.user
    return schemas.StudentProfile(
        user_id=student.user_id,
        student_id=student.student_id,
        full_name=_full_name(student),
        major=student.major,
        dob=student.dob,
        current_gpa=float(student.current_gpa) if student.current_gpa is not None else 0.0,
        target_gpa=float(student.target_gpa) if student.target_gpa is not None else None,
        email=user.email if user else None,
    )


def set_target_gpa(db: Session, student_id: int, target_gpa: float) -> Optional[schemas.StudentProfile]:
    """Set target GPA for a student"""
    student = _find_student(db, student_id)
    if not student:
        return None
    
    from decimal import Decimal
    student.target_gpa = Decimal(str(target_gpa))
    db.commit()
    db.refresh(student)
    
    return get_student_profile(db, student_id)


def get_dashboard_stats(db: Session, student_id: int) -> Optional[schemas.DashboardStats]:
    student = _find_student(db, student_id)
    if not student:
        return None
    user_id = student.user_id

    courses_enrolled = db.query(models.Enroll).filter(models.Enroll.student_id == user_id).count()
    submissions = db.query(models.Submission).filter(models.Submission.student_id == user_id).count()
    avg_score = (
        db.query(func.avg(models.Submission.score)).filter(models.Submission.student_id == user_id).scalar()
    )
    avg_score_val = float(avg_score) if avg_score is not None else None

    prediction = (
        db.query(models.Prediction).filter(models.Prediction.user_id == user_id).order_by(models.Prediction.prediction_id.desc()).first()
    )

    return schemas.DashboardStats(
        courses_enrolled=courses_enrolled,
        submissions=submissions,
        average_score=avg_score_val,
        current_gpa=float(student.current_gpa) if student.current_gpa is not None else None,
        predicted_gpa=float(prediction.predicted_gpa) if prediction else None,
        target_gpa=float(student.target_gpa) if student.target_gpa is not None else None,
        recommendations=prediction.recommendations if prediction else None,
    )


def get_student_courses(db: Session, student_id: int) -> List[schemas.CourseSummary]:
    """Get courses enrolled by a student"""
    student = _find_student(db, student_id)
    if not student:
        return []
    
    enrollments = db.query(models.Enroll).filter(models.Enroll.student_id == student.user_id).all()
    result = []
    
    for enroll in enrollments:
        course = enroll.course
        if course:
            lecturer_name = None
            if course.lecturer:
                lecturer_name = " ".join(filter(None, [
                    course.lecturer.title,
                    course.lecturer.fname,
                    course.lecturer.mname,
                    course.lecturer.lname
                ]))
            
            enrolled_count = db.query(models.Enroll).filter(
                models.Enroll.course_id == course.course_id
            ).count()
            
            result.append(schemas.CourseSummary(
                id=course.course_id,
                code=course.course_code,
                name=course.course_name,
                credits=course.credits,
                semester=course.semester,
                capacity=course.capacity,
                lecturer_name=lecturer_name,
                enrolled_count=enrolled_count,
                description=course.description
            ))
    
    return result


def get_student_assignments(db: Session, student_id: int) -> List[schemas.AssignmentWithStatus]:
    """Get all assignments for courses the student is enrolled in"""
    student = _find_student(db, student_id)
    if not student:
        return []
    
    # Get enrolled course IDs
    enrolled_course_ids = db.query(models.Enroll.course_id).filter(
        models.Enroll.student_id == student.user_id
    ).all()
    course_ids = [c[0] for c in enrolled_course_ids]
    
    if not course_ids:
        return []
    
    assignments = db.query(models.Assignment).filter(
        models.Assignment.course_id.in_(course_ids)
    ).order_by(models.Assignment.deadline).all()
    
    result = []
    for assignment in assignments:
        # Check submission status
        submission = db.query(models.Submission).filter(
            models.Submission.assignment_id == assignment.assignment_id,
            models.Submission.student_id == student.user_id
        ).first()
        
        status = "pending"
        score = None
        if submission:
            if submission.score is not None:
                status = "graded"
                score = float(submission.score)
            else:
                status = "submitted"
        
        result.append(schemas.AssignmentWithStatus(
            id=assignment.assignment_id,
            course_id=assignment.course_id,
            title=assignment.title,
            description=assignment.description,
            deadline=assignment.deadline,
            max_score=float(assignment.max_score) if assignment.max_score else 100.0,
            created_at=assignment.created_at,
            submission_status=status,
            score=score
        ))
    
    return result


def get_student_grades(db: Session, student_id: int) -> List[schemas.Grade]:
    """Get all grades for a student"""
    student = _find_student(db, student_id)
    if not student:
        return []
    
    grades = db.query(models.Grade).filter(
        models.Grade.student_id == student.user_id
    ).all()
    
    result = []
    for grade in grades:
        result.append(schemas.Grade(
            id=grade.grade_id,
            student_id=grade.student_id,
            course_id=grade.course_id,
            assignment_id=grade.assignment_id,
            quiz_id=grade.quiz_id,
            score=float(grade.score),
            max_score=float(grade.max_score) if grade.max_score else 100.0,
            grade_type=grade.grade_type,
            graded_at=grade.graded_at
        ))
    
    return result


def submit_assignment(db: Session, student_id: int, payload: schemas.SubmissionCreate) -> Optional[schemas.Submission]:
    """Submit an assignment"""
    student = _find_student(db, student_id)
    if not student:
        return None
    
    # Check if already submitted
    existing = db.query(models.Submission).filter(
        models.Submission.assignment_id == payload.assignment_id,
        models.Submission.student_id == student.user_id
    ).first()
    
    if existing:
        # Update existing submission
        existing.file_path = payload.file_path
        existing.submitted_at = datetime.utcnow()
        db.commit()
        db.refresh(existing)
        submission = existing
    else:
        # Create new submission
        submission = models.Submission(
            assignment_id=payload.assignment_id,
            student_id=student.user_id,
            file_path=payload.file_path,
            submitted_at=datetime.utcnow()
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
    
    return schemas.Submission(
        id=submission.submission_id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        student_name=_full_name(student),
        score=float(submission.score) if submission.score else None,
        file_path=submission.file_path,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
        comments=submission.comments
    )


def enroll_course(db: Session, student_id: int, payload: schemas.EnrollmentCreate) -> Optional[schemas.Enrollment]:
    """Enroll student in a course"""
    student = _find_student(db, student_id)
    if not student:
        return None
    
    # Check if already enrolled
    existing = db.query(models.Enroll).filter(
        models.Enroll.course_id == payload.course_id,
        models.Enroll.student_id == student.user_id
    ).first()
    
    if existing:
        return schemas.Enrollment(
            id=existing.enroll_id,
            course_id=existing.course_id,
            student_id=existing.student_id,
            semester=existing.semester,
            status=existing.status,
            enrolled_at=existing.enrolled_at
        )
    
    # Get course for semester
    course = db.query(models.Course).filter(models.Course.course_id == payload.course_id).first()
    
    enrollment = models.Enroll(
        course_id=payload.course_id,
        student_id=student.user_id,
        semester=course.semester if course else "2024-1",
        status="active",
        enrolled_at=datetime.utcnow()
    )
    db.add(enrollment)
    db.commit()
    db.refresh(enrollment)
    
    return schemas.Enrollment(
        id=enrollment.enroll_id,
        course_id=enrollment.course_id,
        student_id=enrollment.student_id,
        semester=enrollment.semester,
        status=enrollment.status,
        enrolled_at=enrollment.enrolled_at
    )


def get_student_quizzes(db: Session, student_id: int) -> List[schemas.QuizSummary]:
    """Get available quizzes for student's enrolled courses"""
    student = _find_student(db, student_id)
    if not student:
        return []
    
    # Get enrolled course IDs
    enrolled_course_ids = db.query(models.Enroll.course_id).filter(
        models.Enroll.student_id == student.user_id
    ).all()
    course_ids = [c[0] for c in enrolled_course_ids]
    
    if not course_ids:
        return []
    
    quizzes = db.query(models.Quiz).filter(
        models.Quiz.course_id.in_(course_ids)
    ).all()
    
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


def get_student_quiz_attempts(db: Session, student_id: int) -> List[schemas.QuizAttemptSummary]:
    """Get quiz attempts for a student"""
    student = _find_student(db, student_id)
    if not student:
        return []
    
    attempts = db.query(models.QuizAttempt).filter(
        models.QuizAttempt.student_id == student.user_id
    ).order_by(models.QuizAttempt.started_at.desc()).all()
    
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

