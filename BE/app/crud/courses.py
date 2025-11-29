from datetime import date
from typing import List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app import models, schemas


def list_courses(db: Session) -> List[schemas.CourseSummary]:
    courses = db.query(models.Course).order_by(models.Course.Course_name.asc()).all()
    return [
        schemas.CourseSummary(
            Course_id=course.Course_id,
            Course_code=course.Course_code,
            Course_name=course.Course_name,
            Credits=course.Credits,
            Semester=course.Semester,
            Capacity=course.Capacity,
        )
        for course in courses
    ]


def _materials_for_course(db: Session, course_id: int) -> List[schemas.Material]:
    materials = (
        db.query(models.Materials)
        .filter(models.Materials.Course_id == course_id)
        .order_by(models.Materials.Upload_date.desc())
        .all()
    )
    return [schemas.Material.model_validate(material) for material in materials]


def _assignments_from_materials(materials: List[models.Materials]) -> List[schemas.Assignment]:
    items: List[schemas.Assignment] = []
    for mat in materials:
        if mat.Type and (mat.Type.lower().startswith("assignment") or "assign" in mat.Type.lower()):
            # Treat materials of type "assignment" as assignment placeholders
            items.append(
                schemas.Assignment(
                    Assignment_id=mat.Materials_id,
                    Description=mat.Description or mat.Title or "Assignment",
                    Deadlines=mat.Upload_date,
                    status="available",
                    score=None,
                )
            )
    return items


def _assignments_fallback(db: Session) -> List[schemas.Assignment]:
    assignments = db.query(models.Assignment).order_by(models.Assignment.Deadlines.asc()).all()
    items: List[schemas.Assignment] = []
    for assignment in assignments:
        status = "overdue" if assignment.Deadlines < date.today() else "open"
        items.append(
            schemas.Assignment(
                Assignment_id=assignment.Assignment_id,
                Description=assignment.Description,
                Deadlines=assignment.Deadlines,
                status=status,
            )
        )
    return items


def get_course_detail(db: Session, course_id: int) -> Optional[schemas.CourseDetail]:
    course = db.get(models.Course, course_id)
    if not course:
        return None

    material_models = (
        db.query(models.Materials)
        .filter(models.Materials.Course_id == course_id)
        .order_by(models.Materials.Upload_date.desc())
        .all()
    )
    materials = [schemas.Material.model_validate(mat) for mat in material_models]
    assignments = _assignments_from_materials(material_models)
    if not assignments:
        assignments = _assignments_fallback(db)

    feedback = db.query(models.Feedback).filter(models.Feedback.Course_id == course_id).all()

    return schemas.CourseDetail(
        Course_id=course.Course_id,
        Course_code=course.Course_code,
        Course_name=course.Course_name,
        Credits=course.Credits,
        Semester=course.Semester,
        Capacity=course.Capacity,
        materials=materials,
        assignments=assignments,
        feedback=[schemas.Feedback.model_validate(item) for item in feedback],
    )


def list_materials(db: Session, course_id: int) -> List[schemas.Material]:
    return _materials_for_course(db, course_id)


def list_assignments(db: Session, course_id: int) -> List[schemas.Assignment]:
    materials = db.query(models.Materials).filter(models.Materials.Course_id == course_id).all()
    assignments = _assignments_from_materials(materials)
    if assignments:
        return assignments
    return _assignments_fallback(db)


def create_feedback(db: Session, course_id: int, payload: schemas.FeedbackCreate) -> schemas.Feedback:
    feedback = models.Feedback(
        Content=payload.content,
        Rating=payload.rating,
        Student_id=payload.student_id,
        Course_id=course_id,
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    return schemas.Feedback.model_validate(feedback)
