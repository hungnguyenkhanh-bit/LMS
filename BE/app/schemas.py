from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


class UserBase(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    User_id: int
    Username: Optional[str]
    Email: EmailStr
    Role: str


class LoginRequest(BaseModel):
    username: str
    password: str


class StudentProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int = Field(..., alias="User_id")
    student_id: int = Field(..., alias="Student_id")
    full_name: str
    major: str
    dob: Optional[date] = Field(None, alias="DOB")
    current_gpa: float
    target_gpa: Optional[float] = None
    email: Optional[EmailStr] = None


class DashboardStats(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    courses_enrolled: int
    submissions: int
    average_score: Optional[float]
    current_gpa: Optional[float]
    predicted_gpa: Optional[float]
    target_gpa: Optional[float]
    recommendations: Optional[str] = None


class Material(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., alias="Materials_id")
    title: Optional[str] = None
    type: str = Field(..., alias="Type")
    description: Optional[str] = Field(None, alias="Description")
    file_path: Optional[str] = Field(None, alias="File_path")
    upload_date: date = Field(..., alias="Upload_date")


class Assignment(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., alias="Assignment_id")
    description: Optional[str] = Field(None, alias="Description")
    deadline: date = Field(..., alias="Deadlines")
    status: Optional[str] = None
    score: Optional[float] = None


class Feedback(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., alias="Feedback_id")
    content: Optional[str] = Field(None, alias="Content")
    rating: int = Field(..., alias="Rating")
    student_id: int = Field(..., alias="Student_id")
    course_id: int = Field(..., alias="Course_id")


class FeedbackCreate(BaseModel):
    content: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)
    student_id: int


class CourseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(..., alias="Course_id")
    code: str = Field(..., alias="Course_code")
    name: str = Field(..., alias="Course_name")
    credits: int = Field(..., alias="Credits")
    semester: str = Field(..., alias="Semester")
    capacity: int = Field(..., alias="Capacity")


class CourseDetail(CourseSummary):
    materials: List[Material] = Field(default_factory=list)
    assignments: List[Assignment] = Field(default_factory=list)
    feedback: List[Feedback] = Field(default_factory=list)


class Message(BaseModel):
    from_user_id: int
    to_user_id: int
    body: str
    timestamp: datetime


class MessageCreate(BaseModel):
    to_user_id: int
    body: str


class QuizQuestion(BaseModel):
    question_id: str
    prompt: str
    options: List[str]
    correct_option: Optional[int] = None


class QuizPayload(BaseModel):
    course_id: int
    questions: List[QuizQuestion]


class QuizSubmission(BaseModel):
    course_id: int
    student_id: Optional[int] = None
    answers: List[int]


class QuizSubmissionResult(BaseModel):
    course_id: int
    total_questions: int
    correct_answers: int
    score: float
    feedback: Optional[str] = None
