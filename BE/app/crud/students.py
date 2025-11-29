from datetime import datetime
from typing import List, Optional

from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app import models, schemas


def _full_name(student: models.Student) -> str:
    return " ".join(filter(None, [student.FName, student.MName, student.LName]))


def _find_student(db: Session, student_id: int) -> Optional[models.Student]:
    student = db.query(models.Student).filter(models.Student.Student_id == student_id).first()
    if student:
        return student
    return db.query(models.Student).filter(models.Student.User_id == student_id).first()


def get_student_profile(db: Session, student_id: int) -> Optional[schemas.StudentProfile]:
    student = _find_student(db, student_id)
    if not student:
        return None
    user = student.user
    return schemas.StudentProfile(
        User_id=student.User_id,
        Student_id=student.Student_id,
        full_name=_full_name(student),
        major=student.Major,
        DOB=student.DOB,
        current_gpa=float(student.Current_GPA) if student.Current_GPA is not None else None,
        target_gpa=float(student.Target_GPA) if student.Target_GPA is not None else None,
        email=user.Email if user else None,
    )


def get_dashboard_stats(db: Session, student_id: int) -> Optional[schemas.DashboardStats]:
    student = _find_student(db, student_id)
    if not student:
        return None
    user_id = student.User_id

    courses_enrolled = db.query(models.Enroll).filter(models.Enroll.Student_id == user_id).count()
    submissions = db.query(models.Submission).filter(models.Submission.Student_id == user_id).count()
    avg_score = (
        db.query(func.avg(models.Submission.Score)).filter(models.Submission.Student_id == user_id).scalar()
    )
    avg_score_val = float(avg_score) if avg_score is not None else None

    prediction = (
        db.query(models.Prediction).filter(models.Prediction.User_id == user_id).order_by(models.Prediction.Prediction_id.desc()).first()
    )

    return schemas.DashboardStats(
        courses_enrolled=courses_enrolled,
        submissions=submissions,
        average_score=avg_score_val,
        current_gpa=float(student.Current_GPA) if student.Current_GPA is not None else None,
        predicted_gpa=float(prediction.Predicted_GPA) if prediction else None,
        target_gpa=float(student.Target_GPA) if student.Target_GPA is not None else None,
        recommendations=prediction.Recommendations if prediction else None,
    )


def _parse_message_detail(detail: str) -> dict:
    parsed = {}
    for part in detail.split("|"):
        if ":" in part:
            key, value = part.split(":", 1)
            parsed[key] = value
    return parsed


def list_messages(db: Session, user_id: int) -> List[schemas.Message]:
    logs = (
        db.query(models.ActivityLog)
        .filter(
            models.ActivityLog.Action == "message",
            or_(
                models.ActivityLog.User_id == user_id,
                models.ActivityLog.Detail.ilike(f"%to:{user_id}%"),
                models.ActivityLog.Detail.ilike(f"%from:{user_id}%"),
            ),
        )
        .order_by(models.ActivityLog.Timestamp.desc())
        .all()
    )

    messages: List[schemas.Message] = []
    for log in logs:
        detail = _parse_message_detail(log.Detail or "")
        messages.append(
            schemas.Message(
                from_user_id=int(detail.get("from", log.User_id)),
                to_user_id=int(detail.get("to", log.User_id)),
                body=detail.get("body", log.Detail or ""),
                timestamp=log.Timestamp or datetime.utcnow(),
            )
        )
    return messages


def send_message(db: Session, from_user_id: int, payload: schemas.MessageCreate) -> schemas.Message:
    detail = f"from:{from_user_id}|to:{payload.to_user_id}|body:{payload.body}"
    log = models.ActivityLog(
        Detail=detail,
        Action="message",
        IP_Address="0.0.0.0",
        User_id=from_user_id,
        Timestamp=datetime.utcnow(),
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    parsed = _parse_message_detail(log.Detail or "")
    return schemas.Message(
        from_user_id=int(parsed.get("from", from_user_id)),
        to_user_id=int(parsed.get("to", payload.to_user_id)),
        body=parsed.get("body", payload.body),
        timestamp=log.Timestamp,
    )

