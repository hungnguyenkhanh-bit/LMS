from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# ============ Auth Schemas ============
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


class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    username: Optional[str] = None
    email: EmailStr
    role: str  # "student", "lecturer", or "manager"
    full_name: str
    # Student-specific fields
    student_id: Optional[int] = None
    major: Optional[str] = None
    current_gpa: Optional[float] = None
    # Lecturer-specific fields
    title: Optional[str] = None
    department: Optional[str] = None
    # Manager-specific fields
    office: Optional[str] = None
    position: Optional[str] = None


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class LoginRequest(BaseModel):
    username: str
    password: str


# ============ Student Schemas ============
class StudentProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    student_id: int
    full_name: str
    major: str
    dob: Optional[date] = None
    current_gpa: float
    target_gpa: Optional[float] = None
    email: Optional[EmailStr] = None


class TargetGPAUpdate(BaseModel):
    target_gpa: float = Field(..., ge=0.0, le=4.0)


class StudentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    student_id: int
    full_name: str
    major: str
    current_gpa: float
    email: Optional[EmailStr] = None


class DashboardStats(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    courses_enrolled: int
    submissions: int
    average_score: Optional[float] = None
    current_gpa: Optional[float] = None
    predicted_gpa: Optional[float] = None
    target_gpa: Optional[float] = None
    recommendations: Optional[str] = None

# GPA history cho từng kỳ
class GPAHistoryPoint(BaseModel):
    semester: str          # "2022-1"
    semester_gpa: float    # GPA của kỳ đó
    overall_gpa: float     # GPA tích lũy tới kỳ đó

class GPAHistoryResponse(BaseModel):
    entrance_year: int
    points: list[GPAHistoryPoint]

# ============ Lecturer Schemas ============
class LecturerProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    title: Optional[str] = None
    full_name: str
    department: str
    email: Optional[EmailStr] = None


class LecturerListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    title: Optional[str] = None
    full_name: str
    department: str
    email: Optional[EmailStr] = None


class LecturerDashboardStats(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    courses_teaching: int
    total_students: int
    pending_submissions: int
    average_rating: Optional[float] = None


# ============ Manager Schemas ============
class ManagerProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    name: str
    office: str
    position: Optional[str] = None
    email: Optional[EmailStr] = None


class ManagerDashboardStats(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    total_students: int
    total_lecturers: int
    total_courses: int
    active_enrollments: int
    average_gpa: Optional[float] = None


# ============ Course Schemas ============
class CourseSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    code: str
    name: str
    credits: int
    semester: str
    capacity: int
    lecturer_name: Optional[str] = None
    enrolled_count: Optional[int] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


class CourseCreate(BaseModel):
    code: str
    name: str
    credits: int = 3
    capacity: int = 40
    semester: str
    lecturer_id: Optional[int] = None
    description: Optional[str] = None


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    credits: Optional[int] = None
    capacity: Optional[int] = None
    semester: Optional[str] = None
    lecturer_id: Optional[int] = None
    description: Optional[str] = None


# ============ Material Schemas ============
class Material(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    course_id: int
    title: str
    type: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    upload_date: Optional[datetime] = None


class MaterialCreate(BaseModel):
    course_id: int
    title: str
    type: str
    description: Optional[str] = None
    file_path: Optional[str] = None


# ============ Assignment Schemas ============
class Assignment(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    deadline: datetime
    max_score: float = 100.0
    created_at: Optional[datetime] = None


class AssignmentCreate(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None
    deadline: datetime
    max_score: float = 100.0


class AssignmentWithStatus(Assignment):
    submission_status: Optional[str] = None  # "submitted", "graded", "pending"
    score: Optional[float] = None


# ============ Submission Schemas ============
class Submission(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    assignment_id: int
    student_id: int
    student_name: Optional[str] = None
    score: Optional[float] = None
    file_path: Optional[str] = None
    submitted_at: Optional[datetime] = None
    graded_at: Optional[datetime] = None
    comments: Optional[str] = None


class SubmissionWithDetails(Submission):
    """Submission with additional assignment details"""
    assignment_title: Optional[str] = None
    assignment_deadline: Optional[datetime] = None
    max_score: float = 100.0
    is_late: bool = False


class SubmissionCreate(BaseModel):
    assignment_id: int
    file_path: Optional[str] = None


class SubmissionGrade(BaseModel):
    score: float
    comments: Optional[str] = None


# ============ Quiz Schemas ============
class QuizSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    course_id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int = 30
    max_attempts: int = 1
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    question_count: Optional[int] = None


class QuizQuestion(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    points: float = 1.0
    # Only returned for lecturers
    correct_option: Optional[str] = None


class QuizDetail(QuizSummary):
    questions: List[QuizQuestion] = []


class QuizCreate(BaseModel):
    course_id: int
    title: str
    description: Optional[str] = None
    duration_minutes: int = 30
    max_attempts: int = 1
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class QuizQuestionCreate(BaseModel):
    question_text: str
    option_a: str
    option_b: str
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    correct_option: str
    points: float = 1.0


class QuizAnswer(BaseModel):
    question_id: int
    chosen_option: str


class QuizSubmission(BaseModel):
    quiz_id: Optional[int] = None
    answers: List[QuizAnswer]


class QuizAttemptResult(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    attempt_id: int
    quiz_id: int
    total_questions: int
    correct_answers: int
    total_score: float
    max_score: float
    percentage: float
    status: str


class QuizAttemptSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    attempt_id: int
    quiz_id: int
    quiz_title: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    total_score: Optional[float] = None
    status: str


class QuizAttemptAnswerDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    question_id: int
    question_text: str
    option_a: str
    option_b: str
    option_c: Optional[str] = None
    option_d: Optional[str] = None
    chosen_option: str
    correct_option: str
    is_correct: bool
    points: float


class QuizAttemptDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    attempt_id: int
    quiz_id: int
    quiz_title: str
    total_questions: int
    correct_answers: int
    total_score: float
    max_score: float
    percentage: float
    status: str
    started_at: datetime
    finished_at: Optional[datetime] = None
    answers: List[QuizAttemptAnswerDetail]


# ============ Feedback Schemas ============
class Feedback(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    content: Optional[str] = None
    rating: int
    student_id: int
    student_name: Optional[str] = None
    course_id: int
    course_name: Optional[str] = None
    created_at: Optional[datetime] = None


class FeedbackCreate(BaseModel):
    course_id: int
    content: Optional[str] = None
    rating: int = Field(..., ge=1, le=5)


class FeedbackUpdate(BaseModel):
    content: Optional[str] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


# ============ Course Rating Schemas ============
class CourseRating(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    course_id: int
    student_id: int
    rating: int
    comment: Optional[str] = None
    created_at: Optional[datetime] = None


class CourseRatingCreate(BaseModel):
    course_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


# ============ Message Schemas ============
class Message(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    sender_id: int
    sender_name: Optional[str] = None
    receiver_id: int
    receiver_name: Optional[str] = None
    content: str
    is_read: bool = False
    created_at: datetime


class MessageCreate(BaseModel):
    receiver_id: int
    content: str


class Conversation(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    user_name: str
    last_message: str
    last_message_time: datetime
    unread_count: int = 0


# ============ Grade Schemas ============
class Grade(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    student_id: int
    course_id: int
    assignment_id: Optional[int] = None
    quiz_id: Optional[int] = None
    score: float
    max_score: float = 100.0
    grade_type: str  # "assignment", "quiz", "midterm", "final"
    graded_at: Optional[datetime] = None


class GradeCreate(BaseModel):
    student_id: int
    course_id: int
    assignment_id: Optional[int] = None
    quiz_id: Optional[int] = None
    score: float
    max_score: float = 100.0
    grade_type: str


# ============ Enrollment Schemas ============
class Enrollment(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    course_id: int
    student_id: int
    semester: Optional[str] = None
    status: str = "active"
    enrolled_at: Optional[datetime] = None


class EnrollmentCreate(BaseModel):
    course_id: int


class EnrollmentWithCourse(Enrollment):
    course_name: str
    course_code: str
    lecturer_name: Optional[str] = None


class EnrollmentWithStudent(Enrollment):
    student_name: str
    student_email: Optional[str] = None


# ============ Course Detail Schema ============
class CourseDetail(CourseSummary):
    materials: List[Material] = []
    assignments: List[Assignment] = []
    quizzes: List[QuizSummary] = []
    feedback: List[Feedback] = []
    students: List[StudentListItem] = []


# ============ Prediction Schemas ============
class Prediction(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    user_id: int
    predicted_gpa: float
    confidence_level: float
    model_version: str
    recommendations: Optional[str] = None
    target_gpa: Optional[float] = None
    created_at: Optional[datetime] = None


# ============ User List Schemas (for messages, etc.) ============
class UserListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    username: Optional[str] = None
    email: str
    role: str
    full_name: str


# ============ At-Risk Student Schemas ============
class AtRiskStudent(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    user_id: int
    student_id: int
    full_name: str
    current_gpa: float
    risk_factors: List[str]
    courses: List[str]
    email: Optional[str] = None


# ============ Course Statistics Schemas ============
class CourseAttendanceStat(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    course_id: int
    course_code: str
    course_name: str
    attendance_rate: float


class CourseScoreStat(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    course_id: int
    course_code: str
    course_name: str
    avg_quiz_score: float
    avg_assignment_score: float
