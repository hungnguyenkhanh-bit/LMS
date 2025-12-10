from datetime import datetime
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


def get_manager_profile(db: Session, user_id: int) -> Optional[schemas.ManagerProfile]:
    """Get manager profile by user ID"""
    manager = db.query(models.Manager).filter(models.Manager.user_id == user_id).first()
    if not manager:
        return None
    
    user = manager.user
    return schemas.ManagerProfile(
        user_id=manager.user_id,
        name=manager.name,
        office=manager.office,
        position=manager.position,
        email=user.email if user else None
    )


def get_dashboard_stats(db: Session) -> schemas.ManagerDashboardStats:
    """Get dashboard statistics for manager"""
    total_students = db.query(models.Student).count()
    total_lecturers = db.query(models.Lecturer).count()
    total_courses = db.query(models.Course).count()
    active_enrollments = db.query(models.Enroll).filter(
        models.Enroll.status == "active"
    ).count()
    
    # Calculate average GPA
    avg_gpa = db.query(func.avg(models.Student.current_gpa)).scalar()
    average_gpa = round(float(avg_gpa), 2) if avg_gpa else None
    
    return schemas.ManagerDashboardStats(
        total_students=total_students,
        total_lecturers=total_lecturers,
        total_courses=total_courses,
        active_enrollments=active_enrollments,
        average_gpa=average_gpa
    )


def get_all_students(db: Session) -> List[schemas.StudentListItem]:
    """Get all students"""
    students = db.query(models.Student).all()
    result = []
    for student in students:
        user = student.user
        result.append(schemas.StudentListItem(
            user_id=student.user_id,
            student_id=student.student_id,
            full_name=" ".join(filter(None, [student.fname, student.lname, student.mname])),
            major=student.major,
            current_gpa=float(student.current_gpa) if student.current_gpa else 0.0,
            email=user.email if user else None
        ))
    return result


def get_all_lecturers(db: Session) -> List[schemas.LecturerListItem]:
    """Get all lecturers with average ratings"""
    lecturers = db.query(models.Lecturer).all()
    result = []
    for lecturer in lecturers:
        user = lecturer.user
        
        # Calculate average rating from course feedback
        courses = db.query(models.Course).filter(
            models.Course.lecturer_id == lecturer.user_id
        ).all()
        
        total_rating = 0.0
        rating_count = 0
        for course in courses:
            feedback_list = db.query(models.Feedback).filter(
                models.Feedback.course_id == course.course_id
            ).all()
            for feedback in feedback_list:
                if feedback.rating:
                    total_rating += feedback.rating
                    rating_count += 1
        
        average_rating = round(total_rating / rating_count, 2) if rating_count > 0 else None
        
        result.append(schemas.LecturerListItem(
            user_id=lecturer.user_id,
            title=lecturer.title,
            full_name=" ".join(filter(None, [
                lecturer.title,
                lecturer.fname,
                lecturer.lname,
                lecturer.mname
            ])),
            department=lecturer.department,
            email=user.email if user else None,
            average_rating=average_rating
        ))
    return result


def get_all_courses(db: Session) -> List[schemas.CourseSummary]:
    """Get all courses with details including average grade"""
    courses = db.query(models.Course).order_by(models.Course.course_name.asc()).all()
    result = []
    
    for course in courses:
        lecturer_name = None
        if course.lecturer:
            lecturer_name = " ".join(filter(None, [
                course.lecturer.title,
                course.lecturer.fname,
                course.lecturer.lname,
                course.lecturer.mname
            ]))
        
        enrolled_count = db.query(models.Enroll).filter(
            models.Enroll.course_id == course.course_id
        ).count()
        
        # Calculate average grade from Grade table for students enrolled in this course
        # Get all students enrolled in this course
        enrolled_students = db.query(models.Enroll.student_id).filter(
            models.Enroll.course_id == course.course_id
        ).all()
        student_ids = [s.student_id for s in enrolled_students]
        
        if student_ids:
            # Get grades for these students in this course
            grades = db.query(models.Grade).filter(
                models.Grade.student_id.in_(student_ids),
                models.Grade.course_id == course.course_id,
                models.Grade.score.isnot(None),
                models.Grade.max_score.isnot(None)
            ).all()
            
            total_percentage = 0.0
            grade_count = 0
            for grade_obj in grades:
                # Convert to percentage
                percentage = (float(grade_obj.score) / float(grade_obj.max_score)) * 100
                total_percentage += percentage
                grade_count += 1
            
            average_grade = round(total_percentage / grade_count, 2) if grade_count > 0 else None
        else:
            average_grade = None
        
        result.append(schemas.CourseSummary(
            id=course.course_id,
            code=course.course_code,
            name=course.course_name,
            credits=course.credits,
            semester=course.semester,
            capacity=course.capacity,
            lecturer_name=lecturer_name,
            enrolled_count=enrolled_count,
            description=course.description,
            average_grade=average_grade
        ))
    
    return result


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
    
    lecturer_name = None
    if course.lecturer:
        lecturer_name = " ".join(filter(None, [
            course.lecturer.title,
            course.lecturer.fname,
            course.lecturer.lname,
            course.lecturer.mname
        ]))
    
    return schemas.CourseSummary(
        id=course.course_id,
        code=course.course_code,
        name=course.course_name,
        credits=course.credits,
        semester=course.semester,
        capacity=course.capacity,
        lecturer_name=lecturer_name,
        enrolled_count=0,
        description=course.description
    )


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
    
    lecturer_name = None
    if course.lecturer:
        lecturer_name = " ".join(filter(None, [
            course.lecturer.title,
            course.lecturer.fname,
            course.lecturer.lname,
            course.lecturer.mname
        ]))
    
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
        description=course.description,
        image_url=getattr(course, "image_url", None)
    )


def delete_course(db: Session, course_id: int) -> bool:
    """Delete a course"""
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        return False
    
    db.delete(course)
    db.commit()
    return True


def assign_lecturer_to_course(db: Session, course_id: int, lecturer_id: int) -> Optional[schemas.CourseSummary]:
    """Assign a lecturer to a course"""
    course = db.query(models.Course).filter(models.Course.course_id == course_id).first()
    if not course:
        return None
    
    # Verify lecturer exists
    lecturer = db.query(models.Lecturer).filter(models.Lecturer.user_id == lecturer_id).first()
    if not lecturer:
        return None
    
    course.lecturer_id = lecturer_id
    db.commit()
    db.refresh(course)
    
    lecturer_name = " ".join(filter(None, [
        lecturer.title,
        lecturer.fname,
        lecturer.lname,
        lecturer.mname
    ]))
    
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


def get_all_feedback(db: Session) -> List[schemas.Feedback]:
    """Get all feedback across all courses"""
    feedbacks = db.query(models.Feedback).order_by(models.Feedback.created_at.desc()).all()
    
    result = []
    for fb in feedbacks:
        student_name = None
        course_name = None
        
        if fb.student:
            student_name = " ".join(filter(None, [
                fb.student.fname,
                fb.student.mname,
                fb.student.lname
            ]))
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


def get_course_statistics(db: Session) -> dict:
    """Get course statistics for manager dashboard"""
    # Courses by semester
    semester_stats = db.query(
        models.Course.semester,
        func.count(models.Course.course_id)
    ).group_by(models.Course.semester).all()
    
    # Average enrollment per course
    avg_enrollment = db.query(
        func.avg(
            db.query(func.count(models.Enroll.enroll_id))
            .filter(models.Enroll.course_id == models.Course.course_id)
            .correlate(models.Course)
            .scalar_subquery()
        )
    ).scalar()
    
    # Courses with low enrollment (< 10 students)
    low_enrollment_courses = []
    courses = db.query(models.Course).all()
    for course in courses:
        enrollment_count = db.query(models.Enroll).filter(
            models.Enroll.course_id == course.course_id
        ).count()
        if enrollment_count < 10:
            low_enrollment_courses.append({
                "course_id": course.course_id,
                "course_name": course.course_name,
                "enrollment_count": enrollment_count
            })
    
    return {
        "courses_by_semester": dict(semester_stats),
        "average_enrollment": float(avg_enrollment) if avg_enrollment else 0,
        "low_enrollment_courses": low_enrollment_courses
    }


def get_gpa_distribution(db: Session) -> dict:
    """Get GPA distribution statistics"""
    # GPA ranges
    ranges = [
        ("0.0-1.0", 0.0, 1.0),
        ("1.0-2.0", 1.0, 2.0),
        ("2.0-2.5", 2.0, 2.5),
        ("2.5-3.0", 2.5, 3.0),
        ("3.0-3.5", 3.0, 3.5),
        ("3.5-4.0", 3.5, 4.0)
    ]
    
    distribution = {}
    for label, low, high in ranges:
        count = db.query(models.Student).filter(
            models.Student.current_gpa >= low,
            models.Student.current_gpa < high
        ).count()
        distribution[label] = count
    
    return distribution
