import json
from typing import List

from sqlalchemy.orm import Session

from app import models, schemas


def _parse_question_detail(detail: str) -> schemas.QuizQuestion | None:
    try:
        data = json.loads(detail)
        if isinstance(data, dict) and "prompt" in data:
            return schemas.QuizQuestion(
                question_id=str(data.get("question_id", data.get("id", ""))),
                prompt=data["prompt"],
                options=data.get("options", []),
                correct_option=data.get("correct_option"),
            )
    except json.JSONDecodeError:
        pass

    parts = {pair.split(":")[0]: pair.split(":")[1] for pair in detail.split("|") if ":" in pair}
    if "prompt" in parts and "options" in parts:
        opts = parts["options"].split(",")
        correct = int(parts["answer"]) if "answer" in parts and parts["answer"].isdigit() else None
        return schemas.QuizQuestion(
            question_id=parts.get("id", parts.get("question_id", "")),
            prompt=parts["prompt"],
            options=opts,
            correct_option=correct,
        )
    return None


def _fallback_questions(course_id: int) -> List[schemas.QuizQuestion]:
    return [
        schemas.QuizQuestion(
            question_id=f"{course_id}-1",
            prompt="What is the recommended first step when starting a new course?",
            options=["Skim the syllabus", "Start the first assignment", "Email the professor", "Drop the class"],
            correct_option=0,
        ),
        schemas.QuizQuestion(
            question_id=f"{course_id}-2",
            prompt="How many hours per credit should you plan to study each week?",
            options=["1 hour", "2-3 hours", "5 hours", "10 hours"],
            correct_option=1,
        ),
    ]


def get_quiz_questions(db: Session, course_id: int) -> List[schemas.QuizQuestion]:
    logs = (
        db.query(models.ActivityLog)
        .filter(
            models.ActivityLog.Action == "quiz_question",
            models.ActivityLog.Detail.ilike(f"%course:{course_id}%"),
        )
        .all()
    )
    questions: List[schemas.QuizQuestion] = []
    for log in logs:
        parsed = _parse_question_detail(log.Detail or "")
        if parsed:
            questions.append(parsed)
    if not questions:
        questions = _fallback_questions(course_id)
    return questions


def submit_answers(db: Session, course_id: int, submission: schemas.QuizSubmission) -> schemas.QuizSubmissionResult:
    questions = get_quiz_questions(db, course_id)
    correct_answers = 0
    for idx, answer in enumerate(submission.answers):
        if idx < len(questions) and questions[idx].correct_option is not None:
            if answer == questions[idx].correct_option:
                correct_answers += 1
    total = len(questions)
    score = round((correct_answers / total) * 100, 2) if total else 0.0

    # Pick a valid user id for logging
    log_user_id = submission.student_id
    if log_user_id is None:
        sample_user = db.query(models.User).first()
        log_user_id = sample_user.User_id if sample_user else 1

    detail = json.dumps(
        {
            "course": course_id,
            "answers": submission.answers,
            "score": score,
            "correct": correct_answers,
        }
    )
    try:
        log = models.ActivityLog(
            Detail=detail,
            Action="quiz_submission",
            IP_Address="0.0.0.0",
            User_id=log_user_id,
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()

    return schemas.QuizSubmissionResult(
        course_id=course_id,
        total_questions=total,
        correct_answers=correct_answers,
        score=score,
        feedback="Thanks for submitting. Review explanations in your course materials.",
    )
