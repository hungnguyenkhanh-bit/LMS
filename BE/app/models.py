from datetime import date, datetime
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "user"

    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=True)
    password_hash = Column(Text, nullable=False)
    role = Column(String(20), nullable=False)
    email = Column(String(100), nullable=False, unique=True)

    student = relationship("Student", back_populates="user", uselist=False)
    lecturer = relationship("Lecturer", back_populates="user", uselist=False)
    manager = relationship("Manager", back_populates="user", uselist=False)
    activities = relationship("ActivityLog", back_populates="user")
    sent_messages = relationship("Message", foreign_keys="Message.sender_id", back_populates="sender")
    received_messages = relationship("Message", foreign_keys="Message.receiver_id", back_populates="receiver")


class Student(Base):
    __tablename__ = "student"

    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True)
    student_id = Column(Integer, unique=True, nullable=False)
    lname = Column(String(50), nullable=False)
    mname = Column(String(50))
    fname = Column(String(50), nullable=False)
    major = Column(String(100), nullable=False)
    dob = Column(Date)
    current_gpa = Column(DECIMAL(3, 2), nullable=False, default=0.00)
    target_gpa = Column(DECIMAL(3, 2))

    user = relationship("User", back_populates="student")
    enrollments = relationship("Enroll", back_populates="student")
    submissions = relationship("Submission", back_populates="student")
    feedbacks = relationship("Feedback", back_populates="student")
    predictions = relationship("Prediction", back_populates="student")
    grades = relationship("Grade", back_populates="student")
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    course_ratings = relationship("CourseRating", back_populates="student")
    attendance_details = relationship("AttendanceDetail", back_populates="student")


class Lecturer(Base):
    __tablename__ = "lecturer"

    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True)
    title = Column(String(100))
    lname = Column(String(50), nullable=False)
    mname = Column(String(50))
    fname = Column(String(50), nullable=False)
    department = Column(String(100), nullable=False)

    user = relationship("User", back_populates="lecturer")
    courses = relationship("Course", back_populates="lecturer")


class Manager(Base):
    __tablename__ = "manager"

    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), primary_key=True)
    name = Column(String(200), nullable=False)
    office = Column(String(100), nullable=False)
    position = Column(String(100))

    user = relationship("User", back_populates="manager")


class Course(Base):
    __tablename__ = "course"

    course_id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String(100), unique=True, nullable=False)
    course_name = Column(String(200), nullable=False)
    credits = Column(Integer, nullable=False)
    capacity = Column(Integer, nullable=False, default=50)
    semester = Column(String(20), nullable=False)
    lecturer_id = Column(Integer, ForeignKey("lecturer.user_id", ondelete="SET NULL"))
    description = Column(Text)

    lecturer = relationship("Lecturer", back_populates="courses")
    materials = relationship("Materials", back_populates="course")
    enrollments = relationship("Enroll", back_populates="course")
    feedbacks = relationship("Feedback", back_populates="course")
    assignments = relationship("Assignment", back_populates="course")
    quizzes = relationship("Quiz", back_populates="course")
    grades = relationship("Grade", back_populates="course")
    course_ratings = relationship("CourseRating", back_populates="course")
    attendance_records = relationship("AttendanceRecord", back_populates="course")


class Enroll(Base):
    __tablename__ = "enroll"

    enroll_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), nullable=False)
    semester = Column(String(20))
    status = Column(String(20), nullable=False, default='active')
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="enrollments")
    student = relationship("Student", back_populates="enrollments")

    __table_args__ = (
        UniqueConstraint('course_id', 'student_id', name='uq_enroll'),
    )


class Materials(Base):
    __tablename__ = "materials"

    materials_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    type = Column(String(50), nullable=False)
    description = Column(Text)
    title = Column(String(200), nullable=False)
    file_path = Column(String(500))
    upload_date = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="materials")


class Assignment(Base):
    __tablename__ = "assignment"

    assignment_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    deadline = Column(DateTime, nullable=False)
    max_score = Column(DECIMAL(5, 2), default=100.00)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="assignments")
    submissions = relationship("Submission", back_populates="assignment")
    grades = relationship("Grade", back_populates="assignment")


class Submission(Base):
    __tablename__ = "submission"

    submission_id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("assignment.assignment_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), nullable=False)
    score = Column(DECIMAL(5, 2))
    file_path = Column(String(500))
    submitted_at = Column(DateTime, default=datetime.utcnow)
    graded_at = Column(DateTime)
    comments = Column(Text)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")

    __table_args__ = (
        UniqueConstraint('assignment_id', 'student_id', name='uq_submission'),
    )


class Quiz(Base):
    __tablename__ = "quiz"

    quiz_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    duration_minutes = Column(Integer, default=30)
    max_attempts = Column(Integer, default=1)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="quizzes")
    questions = relationship("QuizQuestion", back_populates="quiz")
    attempts = relationship("QuizAttempt", back_populates="quiz")
    grades = relationship("Grade", back_populates="quiz")


class QuizQuestion(Base):
    __tablename__ = "quiz_question"

    question_id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.quiz_id", ondelete="CASCADE"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500), nullable=False)
    option_b = Column(String(500), nullable=False)
    option_c = Column(String(500))
    option_d = Column(String(500))
    correct_option = Column(String(1), nullable=False)
    points = Column(DECIMAL(5, 2), default=1.00)

    quiz = relationship("Quiz", back_populates="questions")
    attempt_details = relationship("QuizAttemptDetail", back_populates="question")


class QuizAttempt(Base):
    __tablename__ = "quiz_attempt"

    attempt_id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quiz.quiz_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), nullable=False)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime)
    total_score = Column(DECIMAL(5, 2))
    status = Column(String(20), default='in_progress')

    quiz = relationship("Quiz", back_populates="attempts")
    student = relationship("Student", back_populates="quiz_attempts")
    details = relationship("QuizAttemptDetail", back_populates="attempt")


class QuizAttemptDetail(Base):
    __tablename__ = "quiz_attempt_detail"

    detail_id = Column(Integer, primary_key=True, index=True)
    attempt_id = Column(Integer, ForeignKey("quiz_attempt.attempt_id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("quiz_question.question_id", ondelete="CASCADE"), nullable=False)
    chosen_option = Column(String(1))
    is_correct = Column(Boolean)

    attempt = relationship("QuizAttempt", back_populates="details")
    question = relationship("QuizQuestion", back_populates="attempt_details")

    __table_args__ = (
        UniqueConstraint('attempt_id', 'question_id', name='uq_attempt_question'),
    )


class Grade(Base):
    __tablename__ = "grade"

    grade_id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    assignment_id = Column(Integer, ForeignKey("assignment.assignment_id", ondelete="SET NULL"))
    quiz_id = Column(Integer, ForeignKey("quiz.quiz_id", ondelete="SET NULL"))
    score = Column(DECIMAL(5, 2), nullable=False)
    max_score = Column(DECIMAL(5, 2), default=100.00)
    grade_type = Column(String(20), nullable=False)
    graded_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="grades")
    course = relationship("Course", back_populates="grades")
    assignment = relationship("Assignment", back_populates="grades")
    quiz = relationship("Quiz", back_populates="grades")


class Feedback(Base):
    __tablename__ = "feedback"

    feedback_id = Column(Integer, primary_key=True, index=True)
    content = Column(Text)
    rating = Column(Integer, nullable=False, default=3)
    student_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), nullable=False)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="feedbacks")
    course = relationship("Course", back_populates="feedbacks")


class CourseRating(Base):
    __tablename__ = "course_rating"

    rating_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), nullable=False)
    rating = Column(Integer, nullable=False)
    comment = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="course_ratings")
    student = relationship("Student", back_populates="course_ratings")

    __table_args__ = (
        UniqueConstraint('course_id', 'student_id', name='uq_course_rating'),
    )


class Message(Base):
    __tablename__ = "message"

    message_id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_messages")


class AttendanceRecord(Base):
    __tablename__ = "attendance_record"

    record_id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("course.course_id", ondelete="CASCADE"), nullable=False)
    date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    course = relationship("Course", back_populates="attendance_records")
    details = relationship("AttendanceDetail", back_populates="record")


class AttendanceDetail(Base):
    __tablename__ = "attendance_detail"

    detail_id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("attendance_record.record_id", ondelete="CASCADE"), nullable=False)
    student_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), nullable=False)
    status = Column(String(20), nullable=False, default='present')

    record = relationship("AttendanceRecord", back_populates="details")
    student = relationship("Student", back_populates="attendance_details")

    __table_args__ = (
        UniqueConstraint('record_id', 'student_id', name='uq_attendance_detail'),
    )


class Prediction(Base):
    __tablename__ = "prediction"

    prediction_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("student.user_id", ondelete="CASCADE"), nullable=False)
    predicted_gpa = Column(DECIMAL(3, 2), nullable=False)
    confidence_level = Column(DECIMAL(5, 2), nullable=False)
    model_version = Column(String(20), nullable=False)
    recommendations = Column(Text)
    target_gpa = Column(DECIMAL(3, 2))
    created_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("Student", back_populates="predictions")


class ActivityLog(Base):
    __tablename__ = "activity_log"

    log_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.user_id", ondelete="CASCADE"), nullable=False)
    action = Column(String(100), nullable=False)
    detail = Column(Text)
    ip_address = Column(String(45))
    timestamp = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="activities")
