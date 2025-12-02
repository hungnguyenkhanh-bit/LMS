from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


def _lecturer_full_name(lecturer: models.Lecturer) -> str:
    """Build full name from lecturer model"""
    return " ".join(filter(None, [
        lecturer.title,
        lecturer.fname,
        lecturer.mname,
        lecturer.lname
    ]))


def _student_full_name(student: models.Student) -> str:
    """Build full name from student model"""
    return " ".join(filter(None, [student.fname, student.mname, student.lname]))


def list_courses(db: Session) -> List[schemas.CourseSummary]:
    """Get all courses"""
    courses = db.query(models.Course).order_by(models.Course.course_name.asc()).all()
    result = []
    
    for course in courses:
        lecturer_name = None
        if course.lecturer:
            lecturer_name = _lecturer_full_name(course.lecturer)
        
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


def get_course(db: Session, course_id: int) -> Optional[schemas.CourseSummary]:
    """Get a single course by ID"""
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        return None
    
    lecturer_name = None
    if course.lecturer:
        lecturer_name = _lecturer_full_name(course.lecturer)
    
    enrolled_count = db.query(models.Enroll).filter(
        models.Enroll.course_id == course.course_id
    ).count()
    
    return schemas.CourseSummary(
        id=course.course_id,
        code=course.course_code,
        name=course.course_name,
        credits=course.credits,
        semester=course.semester,
        capacity=course.capacity,
        lecturer_name=lecturer_name,
        enrolled_count=enrolled_count,
        description=course.description
    )


def create_course(db: Session, payload: schemas.CourseCreate) -> schemas.CourseSummary:
    """Create a new course"""
    course = models.Course(
        course_code=payload.code,
        course_name=payload.name,
        credits=payload.credits,
        capacity=payload.capacity,
        semester=payload.semester,
        lecturer_id=payload.lecturer_id,
        description=payload.description
    )
    db.add(course)
    db.commit()
    db.refresh(course)
    
    return get_course(db, course.course_id)


def update_course(db: Session, course_id: int, payload: schemas.CourseUpdate) -> Optional[schemas.CourseSummary]:
    """Update a course"""
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        return None
    
    if payload.name is not None:
        course.course_name = payload.name
    if payload.credits is not None:
        course.credits = payload.credits
    if payload.capacity is not None:
        course.capacity = payload.capacity
    if payload.semester is not None:
        course.semester = payload.semester
    if payload.lecturer_id is not None:
        course.lecturer_id = payload.lecturer_id
    if payload.description is not None:
        course.description = payload.description
    
    db.commit()
    db.refresh(course)
    
    return get_course(db, course.course_id)


def delete_course(db: Session, course_id: int) -> bool:
    """Delete a course"""
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        return False
    
    db.delete(course)
    db.commit()
    return True


def get_course_detail(db: Session, course_id: int) -> Optional[schemas.CourseDetail]:
    """Get detailed course information including materials, assignments, quizzes, feedback, and enrolled students"""
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        return None
    
    lecturer_name = None
    if course.lecturer:
        lecturer_name = _lecturer_full_name(course.lecturer)
    
    # Get materials
    materials = []
    for mat in course.materials:
        materials.append(schemas.Material(
            id=mat.materials_id,
            course_id=mat.course_id,
            title=mat.title,
            type=mat.type,
            description=mat.description,
            file_path=mat.file_path,
            upload_date=mat.upload_date
        ))
    
    # Get assignments
    assignments = []
    for assignment in course.assignments:
        assignments.append(schemas.Assignment(
            id=assignment.assignment_id,
            course_id=assignment.course_id,
            title=assignment.title,
            description=assignment.description,
            deadline=assignment.deadline,
            max_score=float(assignment.max_score) if assignment.max_score else 100.0,
            created_at=assignment.created_at
        ))
    
    # Get quizzes
    quizzes = []
    for quiz in course.quizzes:
        question_count = db.query(models.QuizQuestion).filter(
            models.QuizQuestion.quiz_id == quiz.quiz_id
        ).count()
        quizzes.append(schemas.QuizSummary(
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
    
    # Get feedback
    feedback = []
    for fb in course.feedbacks:
        student_name = None
        if fb.student:
            student_name = _student_full_name(fb.student)
        feedback.append(schemas.Feedback(
            id=fb.feedback_id,
            content=fb.content,
            rating=fb.rating,
            student_id=fb.student_id,
            student_name=student_name,
            course_id=fb.course_id,
            course_name=course.course_name,
            created_at=fb.created_at
        ))
    
    # Get enrolled students
    students = []
    for enroll in course.enrollments:
        if enroll.student:
            student = enroll.student
            students.append(schemas.StudentListItem(
                user_id=student.user_id,
                student_id=student.student_id,
                full_name=_student_full_name(student),
                major=student.major,
                current_gpa=float(student.current_gpa) if student.current_gpa else 0.0,
                email=student.user.email if student.user else None
            ))
    
    enrolled_count = len(students)
    
    return schemas.CourseDetail(
        id=course.course_id,
        code=course.course_code,
        name=course.course_name,
        credits=course.credits,
        semester=course.semester,
        capacity=course.capacity,
        lecturer_name=lecturer_name,
        enrolled_count=enrolled_count,
        description=course.description,
        materials=materials,
        assignments=assignments,
        quizzes=quizzes,
        feedback=feedback,
        students=students
    )


def list_materials(db: Session, course_id: int) -> List[schemas.Material]:
    """Get all materials for a course"""
    materials = db.query(models.Materials).filter(
        models.Materials.course_id == course_id
    ).order_by(models.Materials.upload_date.desc()).all()
    
    return [
        schemas.Material(
            id=mat.materials_id,
            course_id=mat.course_id,
            title=mat.title,
            type=mat.type,
            description=mat.description,
            file_path=mat.file_path,
            upload_date=mat.upload_date
        )
        for mat in materials
    ]


def create_material(db: Session, payload: schemas.MaterialCreate) -> schemas.Material:
    """Create a new course material"""
    material = models.Materials(
        course_id=payload.course_id,
        title=payload.title,
        type=payload.type,
        description=payload.description,
        file_path=payload.file_path,
        upload_date=datetime.utcnow()
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    
    return schemas.Material(
        id=material.materials_id,
        course_id=material.course_id,
        title=material.title,
        type=material.type,
        description=material.description,
        file_path=material.file_path,
        upload_date=material.upload_date
    )


def list_assignments(db: Session, course_id: int) -> List[schemas.Assignment]:
    """Get all assignments for a course"""
    assignments = db.query(models.Assignment).filter(
        models.Assignment.course_id == course_id
    ).order_by(models.Assignment.deadline.asc()).all()
    
    return [
        schemas.Assignment(
            id=a.assignment_id,
            course_id=a.course_id,
            title=a.title,
            description=a.description,
            deadline=a.deadline,
            max_score=float(a.max_score) if a.max_score else 100.0,
            created_at=a.created_at
        )
        for a in assignments
    ]


def create_assignment(db: Session, payload: schemas.AssignmentCreate) -> schemas.Assignment:
    """Create a new assignment"""
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


def get_assignment_submissions(db: Session, assignment_id: int) -> List[schemas.Submission]:
    """Get all submissions for an assignment"""
    submissions = db.query(models.Submission).filter(
        models.Submission.assignment_id == assignment_id
    ).all()
    
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


def grade_submission(db: Session, submission_id: int, payload: schemas.SubmissionGrade) -> Optional[schemas.Submission]:
    """Grade a submission"""
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


def create_feedback(db: Session, student_id: int, payload: schemas.FeedbackCreate) -> schemas.Feedback:
    """Create feedback for a course"""
    feedback = models.Feedback(
        content=payload.content,
        rating=payload.rating,
        student_id=student_id,
        course_id=payload.course_id,
        created_at=datetime.utcnow()
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    student_name = None
    course_name = None
    
    if feedback.student:
        student_name = _student_full_name(feedback.student)
    if feedback.course:
        course_name = feedback.course.course_name
    
    return schemas.Feedback(
        id=feedback.feedback_id,
        content=feedback.content,
        rating=feedback.rating,
        student_id=feedback.student_id,
        student_name=student_name,
        course_id=feedback.course_id,
        course_name=course_name,
        created_at=feedback.created_at
    )


def get_course_feedback(db: Session, course_id: int) -> List[schemas.Feedback]:
    """Get all feedback for a course"""
    feedbacks = db.query(models.Feedback).filter(
        models.Feedback.course_id == course_id
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


def get_enrolled_students(db: Session, course_id: int) -> List[schemas.StudentListItem]:
    """Get all students enrolled in a course"""
    enrollments = db.query(models.Enroll).filter(
        models.Enroll.course_id == course_id
    ).all()
    
    students = []
    for enroll in enrollments:
        if enroll.student:
            student = enroll.student
            students.append(schemas.StudentListItem(
                user_id=student.user_id,
                student_id=student.student_id,
                full_name=_student_full_name(student),
                major=student.major,
                current_gpa=float(student.current_gpa) if student.current_gpa else 0.0,
                email=student.user.email if student.user else None
            ))
    
    return students


def get_course_submissions(db: Session, course_id: int) -> List[schemas.SubmissionWithDetails]:
    """Get all submissions for assignments in a course with detailed information"""
    # Get all assignments for this course
    assignments = db.query(models.Assignment).filter(
        models.Assignment.course_id == course_id
    ).all()
    
    if not assignments:
        return []
    
    assignment_map = {a.assignment_id: a for a in assignments}
    assignment_ids = list(assignment_map.keys())
    
    # Get submissions for these assignments
    submissions = db.query(models.Submission).filter(
        models.Submission.assignment_id.in_(assignment_ids)
    ).order_by(models.Submission.submitted_at.desc()).all()
    
    result = []
    for sub in submissions:
        student_name = None
        if sub.student:
            student_name = _student_full_name(sub.student)
        
        assignment = assignment_map.get(sub.assignment_id)
        is_late = False
        assignment_title = None
        assignment_deadline = None
        max_score = 100.0
        
        if assignment:
            assignment_title = assignment.title
            assignment_deadline = assignment.deadline
            max_score = float(assignment.max_score) if assignment.max_score else 100.0
            if sub.submitted_at and assignment.deadline:
                is_late = sub.submitted_at > assignment.deadline
        
        result.append(schemas.SubmissionWithDetails(
            id=sub.submission_id,
            assignment_id=sub.assignment_id,
            student_id=sub.student_id,
            student_name=student_name,
            score=float(sub.score) if sub.score else None,
            file_path=sub.file_path,
            submitted_at=sub.submitted_at,
            graded_at=sub.graded_at,
            comments=sub.comments,
            assignment_title=assignment_title,
            assignment_deadline=assignment_deadline,
            max_score=max_score,
            is_late=is_late
        ))
    
    return result


def get_student_feedbacks(db: Session, student_id: int) -> List[schemas.Feedback]:
    """Get all feedback submitted by a student"""
    feedbacks = db.query(models.Feedback).filter(
        models.Feedback.student_id == student_id
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


def update_feedback(db: Session, feedback_id: int, student_id: int, payload: schemas.FeedbackUpdate) -> Optional[schemas.Feedback]:
    """Update an existing feedback"""
    feedback = db.query(models.Feedback).filter(
        models.Feedback.feedback_id == feedback_id,
        models.Feedback.student_id == student_id
    ).first()
    
    if not feedback:
        return None
    
    if payload.content is not None:
        feedback.content = payload.content
    if payload.rating is not None:
        feedback.rating = payload.rating
    
    db.commit()
    db.refresh(feedback)
    
    student_name = None
    course_name = None
    
    if feedback.student:
        student_name = _student_full_name(feedback.student)
    if feedback.course:
        course_name = feedback.course.course_name
    
    return schemas.Feedback(
        id=feedback.feedback_id,
        content=feedback.content,
        rating=feedback.rating,
        student_id=feedback.student_id,
        student_name=student_name,
        course_id=feedback.course_id,
        course_name=course_name,
        created_at=feedback.created_at
    )
