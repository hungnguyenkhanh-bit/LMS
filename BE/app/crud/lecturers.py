from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


def _full_name(lecturer: models.Lecturer) -> str:
    return " ".join(filter(None, [
        lecturer.title,
        lecturer.fname,
        lecturer.lname,
        lecturer.mname
    ]))


def _student_full_name(student: models.Student) -> str:
    return " ".join(filter(None, [student.fname, student.lname, student.mname]))


def get_all_lecturers(db: Session) -> List[schemas.LecturerListItem]:
    """Get all lecturers"""
    lecturers = db.query(models.Lecturer).all()
    result = []
    for lecturer in lecturers:
        user = lecturer.user
        result.append(schemas.LecturerListItem(
            user_id=lecturer.user_id,
            title=lecturer.title,
            full_name=_full_name(lecturer),
            department=lecturer.department,
            email=user.email if user else None
        ))
    return result


def get_lecturer_profile(db: Session, user_id: int) -> Optional[schemas.LecturerProfile]:
    """Get lecturer profile by user ID"""
    lecturer = db.query(models.Lecturer).filter(models.Lecturer.user_id == user_id).first()
    if not lecturer:
        return None
    
    user = lecturer.user
    return schemas.LecturerProfile(
        user_id=lecturer.user_id,
        title=lecturer.title,
        full_name=_full_name(lecturer),
        department=lecturer.department,
        email=user.email if user else None
    )


def get_dashboard_stats(db: Session, user_id: int) -> Optional[schemas.LecturerDashboardStats]:
    """Get dashboard statistics for a lecturer"""
    lecturer = db.query(models.Lecturer).filter(models.Lecturer.user_id == user_id).first()
    if not lecturer:
        return None
    
    # Count courses teaching
    courses_teaching = db.query(models.Course).filter(
        models.Course.lecturer_id == user_id
    ).count()
    
    # Get course IDs for this lecturer
    course_ids = [c.course_id for c in db.query(models.Course).filter(
        models.Course.lecturer_id == user_id
    ).all()]
    
    # Count total students enrolled in lecturer's courses
    total_students = 0
    if course_ids:
        total_students = db.query(models.Enroll.student_id).filter(
            models.Enroll.course_id.in_(course_ids)
        ).distinct().count()
    
    # Count pending submissions (submissions without scores)
    pending_submissions = 0
    if course_ids:
        assignment_ids = [a.assignment_id for a in db.query(models.Assignment).filter(
            models.Assignment.course_id.in_(course_ids)
        ).all()]
        
        if assignment_ids:
            pending_submissions = db.query(models.Submission).filter(
                models.Submission.assignment_id.in_(assignment_ids),
                models.Submission.score == None
            ).count()
    
    # Calculate average rating from course feedback
    average_rating = None
    if course_ids:
        avg = db.query(func.avg(models.Feedback.rating)).filter(
            models.Feedback.course_id.in_(course_ids)
        ).scalar()
        if avg:
            average_rating = round(float(avg), 2)
    
    return schemas.LecturerDashboardStats(
        courses_teaching=courses_teaching,
        total_students=total_students,
        pending_submissions=pending_submissions,
        average_rating=average_rating
    )


def get_lecturer_courses(db: Session, user_id: int) -> List[schemas.CourseSummary]:
    """Get all courses taught by a lecturer"""
    courses = db.query(models.Course).filter(
        models.Course.lecturer_id == user_id
    ).all()
    
    result = []
    for course in courses:
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
            lecturer_name=_full_name(db.query(models.Lecturer).filter(
                models.Lecturer.user_id == user_id
            ).first()),
            enrolled_count=enrolled_count,
            description=course.description
        ))
    
    return result


def get_course_students(db: Session, course_id: int) -> List[schemas.StudentListItem]:
    """Get all students enrolled in a course"""
    enrollments = db.query(models.Enroll).filter(
        models.Enroll.course_id == course_id
    ).all()
    
    result = []
    for enroll in enrollments:
        if enroll.student:
            student = enroll.student
            result.append(schemas.StudentListItem(
                user_id=student.user_id,
                student_id=student.student_id,
                full_name=_student_full_name(student),
                major=student.major,
                current_gpa=float(student.current_gpa) if student.current_gpa else 0.0,
                email=student.user.email if student.user else None
            ))
    
    return result


def get_pending_submissions(db: Session, user_id: int) -> List[schemas.Submission]:
    """Get all pending submissions for courses taught by a lecturer"""
    # Get course IDs
    course_ids = [c.course_id for c in db.query(models.Course).filter(
        models.Course.lecturer_id == user_id
    ).all()]
    
    if not course_ids:
        return []
    
    # Get assignment IDs
    assignment_ids = [a.assignment_id for a in db.query(models.Assignment).filter(
        models.Assignment.course_id.in_(course_ids)
    ).all()]
    
    if not assignment_ids:
        return []
    
    # Get pending submissions
    submissions = db.query(models.Submission).filter(
        models.Submission.assignment_id.in_(assignment_ids),
        models.Submission.score == None
    ).order_by(models.Submission.submitted_at.desc()).all()
    
    result = []
    for sub in submissions:
        student_name = None
        if sub.student:
            student_name = _student_full_name(sub.student)
        
        result.append(schemas.Submission(
            id=sub.submission_id,
            assignment_id=sub.assignment_id,
            student_id=sub.student_id,
            student_name=student_name,
            score=float(sub.score) if sub.score else None,
            file_path=sub.file_path,
            submitted_at=sub.submitted_at,
            graded_at=sub.graded_at,
            comments=sub.comments
        ))
    
    return result


def get_course_feedback(db: Session, user_id: int) -> List[schemas.Feedback]:
    """Get all feedback for courses taught by a lecturer"""
    # Get course IDs
    course_ids = [c.course_id for c in db.query(models.Course).filter(
        models.Course.lecturer_id == user_id
    ).all()]
    
    if not course_ids:
        return []
    
    feedbacks = db.query(models.Feedback).filter(
        models.Feedback.course_id.in_(course_ids)
    ).order_by(models.Feedback.created_at.desc()).all()
    
    result = []
    for fb in feedbacks:
        student_name = None
        course_name = None
        
        if fb.student:
            student_name = _student_full_name(fb.student)
        if fb.course:
            course_name = fb.course.course_name
        
        result.append(schemas.Feedback(
            id=fb.feedback_id,
            content=fb.content,
            rating=fb.rating,
            student_id=fb.student_id,
            student_name=student_name,
            course_id=fb.course_id,
            course_name=course_name,
            created_at=fb.created_at
        ))
    
    return result


def create_assignment(db: Session, payload: schemas.AssignmentCreate) -> schemas.Assignment:
    """Create a new assignment for a course"""
    assignment = models.Assignment(
        course_id=payload.course_id,
        title=payload.title,
        description=payload.description,
        deadline=payload.deadline,
        max_score=payload.max_score,
        created_at=datetime.utcnow()
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return schemas.Assignment(
        id=assignment.assignment_id,
        course_id=assignment.course_id,
        title=assignment.title,
        description=assignment.description,
        deadline=assignment.deadline,
        max_score=float(assignment.max_score) if assignment.max_score else 100.0,
        created_at=assignment.created_at
    )


def grade_submission(db: Session, submission_id: int, payload: schemas.SubmissionGrade) -> Optional[schemas.Submission]:
    """Grade a student submission"""
    submission = db.query(models.Submission).filter(
        models.Submission.submission_id == submission_id
    ).first()
    
    if not submission:
        return None
    
    submission.score = payload.score
    submission.comments = payload.comments
    submission.graded_at = datetime.utcnow()
    
    db.commit()
    db.refresh(submission)
    
    student_name = None
    if submission.student:
        student_name = _student_full_name(submission.student)
    
    return schemas.Submission(
        id=submission.submission_id,
        assignment_id=submission.assignment_id,
        student_id=submission.student_id,
        student_name=student_name,
        score=float(submission.score) if submission.score else None,
        file_path=submission.file_path,
        submitted_at=submission.submitted_at,
        graded_at=submission.graded_at,
        comments=submission.comments
    )


def get_at_risk_students(db: Session, user_id: int) -> List[schemas.AtRiskStudent]:
    """Get students at risk (GPA < 2.0 or low quiz/assignment performance) for lecturer's courses"""
    # Get course IDs for this lecturer
    course_ids = [c.course_id for c in db.query(models.Course).filter(
        models.Course.lecturer_id == user_id
    ).all()]
    
    if not course_ids:
        return []
    
    # Get all students enrolled in lecturer's courses
    enrollments = db.query(models.Enroll).filter(
        models.Enroll.course_id.in_(course_ids)
    ).all()
    
    student_ids = list(set(e.student_id for e in enrollments))
    if not student_ids:
        return []
    
    students = db.query(models.Student).filter(
        models.Student.user_id.in_(student_ids)
    ).all()
    
    result = []
    for student in students:
        # Calculate risk factors
        risk_factors = []
        
        # Check GPA
        gpa = float(student.current_gpa) if student.current_gpa else 0.0
        if gpa < 2.0:
            risk_factors.append(f"Low GPA ({gpa:.2f})")
        
        # Check quiz performance
        quiz_attempts = db.query(models.QuizAttempt).filter(
            models.QuizAttempt.student_id == student.user_id,
            models.QuizAttempt.status == 'completed'
        ).all()
        
        if quiz_attempts:
            avg_quiz_score = 0
            total_quizzes = 0
            for attempt in quiz_attempts:
                if attempt.quiz and attempt.quiz.course_id in course_ids:
                    if attempt.total_score is not None:
                        # Calculate percentage
                        max_score = sum(float(q.points or 1) for q in attempt.quiz.questions)
                        if max_score > 0:
                            pct = (float(attempt.total_score) / max_score) * 100
                            avg_quiz_score += pct
                            total_quizzes += 1
            
            if total_quizzes > 0:
                avg_quiz_score = avg_quiz_score / total_quizzes
                if avg_quiz_score < 60:
                    risk_factors.append(f"Low quiz avg ({avg_quiz_score:.1f}%)")
        
        # Check assignment submissions
        submissions = db.query(models.Submission).filter(
            models.Submission.student_id == student.user_id
        ).all()
        
        late_submissions = 0
        graded_submissions = 0
        total_score_pct = 0
        
        for sub in submissions:
            if sub.assignment and sub.assignment.course_id in course_ids:
                # Check if late
                if sub.submitted_at and sub.assignment.deadline:
                    if sub.submitted_at > sub.assignment.deadline:
                        late_submissions += 1
                
                # Check score
                if sub.score is not None and sub.assignment.max_score:
                    pct = (float(sub.score) / float(sub.assignment.max_score)) * 100
                    total_score_pct += pct
                    graded_submissions += 1
        
        if graded_submissions > 0:
            avg_assignment_score = total_score_pct / graded_submissions
            if avg_assignment_score < 60:
                risk_factors.append(f"Low assignment avg ({avg_assignment_score:.1f}%)")
        
        if late_submissions >= 2:
            risk_factors.append(f"{late_submissions} late submissions")
        
        # Check attendance
        total_classes = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.course_id.in_(course_ids)
        ).count()
        
        if total_classes > 0:
            attended = db.query(models.AttendanceDetail).join(models.AttendanceRecord).filter(
                models.AttendanceRecord.course_id.in_(course_ids),
                models.AttendanceDetail.student_id == student.user_id,
                models.AttendanceDetail.status == 'present'
            ).count()
            
            attendance_rate = (attended / total_classes) * 100
            if attendance_rate < 70:
                risk_factors.append(f"Low attendance ({attendance_rate:.1f}%)")
        
        # Only include if there are risk factors
        if risk_factors:
            # Get courses the student is enrolled in (for this lecturer)
            student_courses = db.query(models.Course).join(models.Enroll).filter(
                models.Enroll.student_id == student.user_id,
                models.Course.course_id.in_(course_ids)
            ).all()
            
            course_names = [c.course_name for c in student_courses]
            
            result.append(schemas.AtRiskStudent(
                user_id=student.user_id,
                student_id=student.student_id,
                full_name=_student_full_name(student),
                current_gpa=gpa,
                risk_factors=risk_factors,
                courses=course_names,
                email=student.user.email if student.user else None
            ))
    
    # Sort by number of risk factors (most at risk first)
    result.sort(key=lambda x: len(x.risk_factors), reverse=True)
    
    return result


def get_course_attendance_stats(db: Session, user_id: int) -> List[schemas.CourseAttendanceStat]:
    """Get attendance statistics for each course taught by a lecturer"""
    courses = db.query(models.Course).filter(
        models.Course.lecturer_id == user_id
    ).all()
    
    result = []
    for course in courses:
        # Count total attendance records
        total_records = db.query(models.AttendanceRecord).filter(
            models.AttendanceRecord.course_id == course.course_id
        ).count()
        
        if total_records == 0:
            attendance_rate = 0
        else:
            # Count total possible attendances (records * enrolled students)
            enrolled_count = db.query(models.Enroll).filter(
                models.Enroll.course_id == course.course_id
            ).count()
            
            total_possible = total_records * enrolled_count
            
            # Count actual attendances
            present_count = db.query(models.AttendanceDetail).join(models.AttendanceRecord).filter(
                models.AttendanceRecord.course_id == course.course_id,
                models.AttendanceDetail.status == 'present'
            ).count()
            
            attendance_rate = (present_count / total_possible * 100) if total_possible > 0 else 0
        
        result.append(schemas.CourseAttendanceStat(
            course_id=course.course_id,
            course_code=course.course_code,
            course_name=course.course_name,
            attendance_rate=round(attendance_rate, 1)
        ))
    
    return result


def get_course_score_stats(db: Session, user_id: int) -> List[schemas.CourseScoreStat]:
    """Get average quiz and assignment scores for each course taught by a lecturer"""
    courses = db.query(models.Course).filter(
        models.Course.lecturer_id == user_id
    ).all()
    
    result = []
    for course in courses:
        # Calculate average quiz score
        quiz_attempts = db.query(models.QuizAttempt).join(models.Quiz).filter(
            models.Quiz.course_id == course.course_id,
            models.QuizAttempt.status == 'completed'
        ).all()
        
        avg_quiz_score = 0
        if quiz_attempts:
            total_pct = 0
            count = 0
            for attempt in quiz_attempts:
                if attempt.total_score is not None and attempt.quiz:
                    max_score = sum(float(q.points or 1) for q in attempt.quiz.questions)
                    if max_score > 0:
                        pct = (float(attempt.total_score) / max_score) * 100
                        total_pct += pct
                        count += 1
            if count > 0:
                avg_quiz_score = total_pct / count
        
        # Calculate average assignment score
        submissions = db.query(models.Submission).join(models.Assignment).filter(
            models.Assignment.course_id == course.course_id,
            models.Submission.score != None
        ).all()
        
        avg_assignment_score = 0
        if submissions:
            total_pct = 0
            count = 0
            for sub in submissions:
                if sub.score is not None and sub.assignment.max_score:
                    pct = (float(sub.score) / float(sub.assignment.max_score)) * 100
                    total_pct += pct
                    count += 1
            if count > 0:
                avg_assignment_score = total_pct / count
        
        result.append(schemas.CourseScoreStat(
            course_id=course.course_id,
            course_code=course.course_code,
            course_name=course.course_name,
            avg_quiz_score=round(avg_quiz_score, 1),
            avg_assignment_score=round(avg_assignment_score, 1)
        ))
    
    return result
