from datetime import date, datetime
from sqlalchemy import (
    CheckConstraint,
    Column,
    Date,
    DateTime,
    DECIMAL,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = "User"
    __table_args__ = {"quote": True}

    User_id = Column(Integer, primary_key=True, index=True)
    Username = Column(String(20), unique=True, nullable=True)
    Password_Hash = Column(Text, nullable=False)
    Role = Column(String(20), nullable=False)
    Email = Column(String(50), nullable=False)

    student = relationship("Student", back_populates="user", uselist=False)
    lecturer = relationship("Lecturer", back_populates="user", uselist=False)
    manager = relationship("Manager", back_populates="user", uselist=False)
    activities = relationship("ActivityLog", back_populates="user")


class Student(Base):
    __tablename__ = "Student"
    __table_args__ = {"quote": True}

    User_id = Column(Integer, ForeignKey('"User"."User_id"', ondelete="CASCADE"), primary_key=True)
    Student_id = Column(Integer, unique=True, nullable=False)
    LName = Column(String(20), nullable=False)
    MName = Column(String(20), nullable=False)
    FName = Column(String(20), nullable=False)
    Major = Column(String(50), nullable=False)
    DOB = Column(Date)
    Current_GPA = Column(DECIMAL(2, 1), nullable=False)
    Target_GPA = Column(DECIMAL(2, 1))

    user = relationship("User", back_populates="student")
    enrollments = relationship("Enroll", back_populates="student")
    submissions = relationship("Submission", back_populates="student")
    feedbacks = relationship("Feedback", back_populates="student")
    predictions = relationship("Prediction", back_populates="student")


class Lecturer(Base):
    __tablename__ = "Lecturer"
    __table_args__ = {"quote": True}

    User_id = Column(Integer, ForeignKey('"User"."User_id"', ondelete="CASCADE"), primary_key=True)
    Title = Column(String(100))
    LName = Column(String(20), nullable=False)
    MName = Column(String(20), nullable=False)
    FName = Column(String(20), nullable=False)
    Department = Column(String(100), nullable=False)

    user = relationship("User", back_populates="lecturer")


class Manager(Base):
    __tablename__ = "Manager"
    __table_args__ = {"quote": True}

    User_id = Column(Integer, ForeignKey('"User"."User_id"', ondelete="CASCADE"), primary_key=True)
    Name = Column(String(200), nullable=False)
    Office = Column(String(100), nullable=False)
    Position = Column(String(100))

    user = relationship("User", back_populates="manager")


class Prediction(Base):
    __tablename__ = "Prediction"
    __table_args__ = {"quote": True}

    Prediction_id = Column(Integer, primary_key=True, index=True)
    User_id = Column(Integer, ForeignKey('"Student"."User_id"', ondelete="CASCADE"), nullable=False)
    Predicted_GPA = Column(DECIMAL(2, 1), nullable=False)
    Confidence_level = Column(DECIMAL(5, 2), nullable=False)
    Model_version = Column(String(20), nullable=False)
    Recommendations = Column(Text)
    Target_GPA = Column(DECIMAL(2, 1))

    student = relationship("Student", back_populates="predictions")


class AttendanceRecord(Base):
    __tablename__ = "Attendance_Record"
    __table_args__ = {"quote": True}

    Record_id = Column(Integer, primary_key=True, index=True)
    Date = Column(Date, nullable=False)
    Status = Column(String(20), nullable=False)

    details = relationship("AttendanceDetail", back_populates="record")


class Course(Base):
    __tablename__ = "Course"
    __table_args__ = (CheckConstraint("Capacity < 100", name="ck_capacity"), {"quote": True})

    Course_id = Column(Integer, primary_key=True, index=True)
    Course_code = Column(String(100), unique=True, nullable=False)
    Course_name = Column(String(100), nullable=False)
    Credits = Column(Integer, nullable=False)
    Capacity = Column(Integer, nullable=False)
    Semester = Column(String(20), nullable=False)

    materials = relationship("Materials", back_populates="course")
    enrollments = relationship("Enroll", back_populates="course")
    feedbacks = relationship("Feedback", back_populates="course")
    attendance_details = relationship("AttendanceDetail", back_populates="course")


class Feedback(Base):
    __tablename__ = "Feedback"
    __table_args__ = (
        CheckConstraint("Rating >= 1 AND Rating <= 5", name="ck_feedback_rating"),
        {"quote": True},
    )

    Feedback_id = Column(Integer, primary_key=True, index=True)
    Content = Column(String(500))
    Rating = Column(Integer, nullable=False, default=1)
    Student_id = Column(Integer, ForeignKey('"Student"."User_id"', ondelete="CASCADE"), nullable=False)
    Course_id = Column(Integer, ForeignKey('"Course"."Course_id"', ondelete="CASCADE"), nullable=False)

    student = relationship("Student", back_populates="feedbacks")
    course = relationship("Course", back_populates="feedbacks")


class AttendanceDetail(Base):
    __tablename__ = "Attendance_Detail"
    __table_args__ = (
        PrimaryKeyConstraint("Course_id", "Record_id", "Student_id"),
        {"quote": True},
    )

    Course_id = Column(Integer, ForeignKey('"Course"."Course_id"', ondelete="CASCADE", onupdate="CASCADE"))
    Record_id = Column(Integer, ForeignKey('"Attendance_Record"."Record_id"', ondelete="CASCADE", onupdate="CASCADE"))
    Student_id = Column(Integer, ForeignKey('"Student"."User_id"', ondelete="CASCADE", onupdate="CASCADE"))

    course = relationship("Course", back_populates="attendance_details")
    record = relationship("AttendanceRecord", back_populates="details")
    student = relationship("Student")


class Materials(Base):
    __tablename__ = "Materials"
    __table_args__ = {"quote": True}

    Materials_id = Column(Integer, primary_key=True, index=True)
    Course_id = Column(Integer, ForeignKey('"Course"."Course_id"', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Type = Column(String(50), nullable=False)
    Description = Column(String(200))
    Title = Column(String(100), unique=True)
    File_path = Column(String(200), unique=True)
    Upload_date = Column(Date, nullable=False)

    course = relationship("Course", back_populates="materials")


class Enroll(Base):
    __tablename__ = "Enroll"
    __table_args__ = (
        PrimaryKeyConstraint("Course_id", "Student_id"),
        {"quote": True},
    )

    Course_id = Column(Integer, ForeignKey('"Course"."Course_id"', ondelete="CASCADE", onupdate="CASCADE"))
    Student_id = Column(Integer, ForeignKey('"Student"."User_id"', ondelete="CASCADE", onupdate="CASCADE"))

    course = relationship("Course", back_populates="enrollments")
    student = relationship("Student", back_populates="enrollments")


class Assignment(Base):
    __tablename__ = "Assignment"
    __table_args__ = {"quote": True}

    Assignment_id = Column(Integer, primary_key=True, index=True)
    Description = Column(String(200))
    Deadlines = Column(Date, nullable=False)

    submissions = relationship("Submission", back_populates="assignment")


class Submission(Base):
    __tablename__ = "Submission"
    __table_args__ = (
        UniqueConstraint("Assignment_id", "Student_id", name="uq_submission"),
        {"quote": True},
    )

    Submission_id = Column(Integer, primary_key=True, index=True)
    Assignment_id = Column(Integer, ForeignKey('"Assignment"."Assignment_id"', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Student_id = Column(Integer, ForeignKey('"Student"."User_id"', ondelete="CASCADE", onupdate="CASCADE"), nullable=False)
    Score = Column(DECIMAL(5, 2))
    File_path = Column(String(200), unique=True)

    assignment = relationship("Assignment", back_populates="submissions")
    student = relationship("Student", back_populates="submissions")


class ActivityLog(Base):
    __tablename__ = "Activity_Log"
    __table_args__ = {"quote": True}

    Log_id = Column(Integer, primary_key=True, index=True)
    Detail = Column(String(100))
    Action = Column(String(50), nullable=False)
    Timestamp = Column(DateTime, default=datetime.utcnow)
    IP_Address = Column(String(45), nullable=False)
    User_id = Column(Integer, ForeignKey('"User"."User_id"', ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="activities")
