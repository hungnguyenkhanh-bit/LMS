"""
Sample Data Generation Script for LMS Database
Generates: 10 students, 5 lecturers, 1 manager, 8 courses, 20 assignments,
30 submissions, 50 quiz questions, 15 quiz attempts, 100 messages, 
50 feedback entries, 20 ratings
"""

import sys
import os
from datetime import datetime, timedelta, date
from decimal import Decimal
import random
from faker import Faker
from pathlib import Path
import csv
import calendar

faker = Faker("vi_VN")  # Vietnamese name for random user generation

# Add BE/app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'BE', 'app'))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import (
    Base, User, Student, Lecturer, Manager, Course, Enroll, Materials,
    Assignment, Submission, Quiz, QuizQuestion, QuizAttempt, QuizAttemptDetail,
    Grade, Feedback, CourseRating, Message, AttendanceRecord, AttendanceDetail,
    Prediction, ActivityLog
)

# Database connection
DATABASE_URL = "postgresql://postgres:hung@localhost:5432/LMS"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Password hashing - use bcrypt directly to avoid passlib compatibility issues
import bcrypt

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

DEFAULT_PASSWORD = hash_password("password123")

# Sample data
STUDENT_DATA = [
    {"lname": "Nguyen", "mname": "Van", "fname": "An", "major": "Computer Science", "dob": date(2002, 5, 15), "gpa": 3.45},
    {"lname": "Tran", "mname": "Thi", "fname": "Binh", "major": "Information Technology", "dob": date(2001, 8, 20), "gpa": 3.72},
    {"lname": "Le", "mname": "Hoang", "fname": "Cuong", "major": "Computer Science", "dob": date(2002, 3, 10), "gpa": 3.15},
    {"lname": "Pham", "mname": "Minh", "fname": "Dung", "major": "Software Engineering", "dob": date(2001, 11, 5), "gpa": 3.88},
    {"lname": "Hoang", "mname": "Thi", "fname": "Em", "major": "Data Science", "dob": date(2002, 7, 25), "gpa": 3.55},
    {"lname": "Vo", "mname": "Van", "fname": "Phuc", "major": "Computer Science", "dob": date(2001, 1, 30), "gpa": 2.95},
    {"lname": "Dang", "mname": "Quoc", "fname": "Gia", "major": "Information Technology", "dob": date(2002, 9, 12), "gpa": 3.62},
    {"lname": "Bui", "mname": "Thi", "fname": "Huong", "major": "Software Engineering", "dob": date(2001, 4, 18), "gpa": 3.33},
    {"lname": "Do", "mname": "Anh", "fname": "Khoa", "major": "Artificial Intelligence", "dob": date(2002, 6, 8), "gpa": 3.91},
    {"lname": "Ngo", "mname": "Van", "fname": "Long", "major": "Data Science", "dob": date(2001, 12, 22), "gpa": 3.48},
]

LECTURER_DATA = [
    {"title": "Dr.", "lname": "Nguyen", "mname": "Quang", "fname": "Hieu", "department": "Computer Science"},
    {"title": "Prof.", "lname": "Tran", "mname": "Thi", "fname": "Mai", "department": "Information Technology"},
    {"title": "Dr.", "lname": "Le", "mname": "Van", "fname": "Nam", "department": "Software Engineering"},
    {"title": "Assoc. Prof.", "lname": "Pham", "mname": "Hoang", "fname": "Oanh", "department": "Data Science"},
    {"title": "Dr.", "lname": "Hoang", "mname": "Minh", "fname": "Phuong", "department": "Artificial Intelligence"},
]

MANAGER_DATA = {"name": "Admin Manager", "office": "Building A, Room 101", "position": "Academic Director"}

COURSE_DATA = [
    {"code": "CS101", "name": "Introduction to Programming", "credits": 3, "capacity": 40, "semester": "2024-1"},
    {"code": "CS201", "name": "Data Structures and Algorithms", "credits": 4, "capacity": 35, "semester": "2024-1"},
    {"code": "IT301", "name": "Database Management Systems", "credits": 3, "capacity": 30, "semester": "2024-1"},
    {"code": "SE401", "name": "Software Engineering Principles", "credits": 4, "capacity": 25, "semester": "2024-1"},
    {"code": "DS201", "name": "Introduction to Data Science", "credits": 3, "capacity": 30, "semester": "2024-2"},
    {"code": "AI101", "name": "Fundamentals of AI", "credits": 3, "capacity": 30, "semester": "2024-2"},
    {"code": "CS301", "name": "Operating Systems", "credits": 4, "capacity": 35, "semester": "2024-2"},
    {"code": "IT401", "name": "Web Development", "credits": 3, "capacity": 40, "semester": "2024-2"},
]

QUIZ_QUESTIONS_TEMPLATES = [
    {
        "question": "What is the time complexity of binary search?",
        "options": ["O(n)", "O(log n)", "O(n^2)", "O(1)"],
        "correct": "B"
    },
    {
        "question": "Which data structure uses LIFO principle?",
        "options": ["Queue", "Stack", "Array", "Linked List"],
        "correct": "B"
    },
    {
        "question": "What does SQL stand for?",
        "options": ["Structured Query Language", "Simple Query Language", "Standard Query Language", "System Query Language"],
        "correct": "A"
    },
    {
        "question": "Which of the following is not a programming paradigm?",
        "options": ["Object-Oriented", "Functional", "Procedural", "Sequential"],
        "correct": "D"
    },
    {
        "question": "What is the main purpose of an operating system?",
        "options": ["Run applications", "Manage hardware resources", "Provide security", "All of the above"],
        "correct": "D"
    },
]

# Total users by roles
NUM_STUDENTS_TOTAL = 10
NUM_LECTURERS_TOTAL = 5
NUM_MANAGERS_TOTAL = 1

FIXED_STUDENTS = STUDENT_DATA[:2]
FIXED_LECTURERS = LECTURER_DATA[:2]
FIXED_MANAGERS = MANAGER_DATA

def clear_data(session):
    """Clear existing data in reverse dependency order"""
    print("Clearing existing data...")
    session.query(ActivityLog).delete()
    session.query(Prediction).delete()
    session.query(AttendanceDetail).delete()
    session.query(AttendanceRecord).delete()
    session.query(Message).delete()
    session.query(CourseRating).delete()
    session.query(Feedback).delete()
    session.query(Grade).delete()
    session.query(QuizAttemptDetail).delete()
    session.query(QuizAttempt).delete()
    session.query(QuizQuestion).delete()
    session.query(Quiz).delete()
    session.query(Submission).delete()
    session.query(Assignment).delete()
    session.query(Materials).delete()
    session.query(Enroll).delete()
    session.query(Course).delete()
    session.query(Manager).delete()
    session.query(Lecturer).delete()
    session.query(Student).delete()
    session.query(User).delete()
    session.commit()
    print("Data cleared successfully!")

def create_student_id() -> int:
    enroll_year = faker.random_element(elements=(2020, 2021, 2022, 2023, 2024, 2025))
    id_prefix = f"{enroll_year % 100}5"          # ví dụ: 205, 215, 225, ...
    id_suffix = faker.numerify(text="####")      # ví dụ: 1234
    student_id_str = f"{id_prefix}{id_suffix}"   # ví dụ: "2051234"
    return int(student_id_str)

def generate_unique_student_id(used_ids: set[int]) -> int:
    while True:
        sid = create_student_id()
        if sid not in used_ids:
            used_ids.add(sid)
            return sid

def generate_users(session):
    """Generate users, students, lecturers, and manager (fixed + random mix)"""
    print("Generating users...")
    
    student_user_ids = []
    lecturer_user_ids = []
    manager_user_id = None
    
    user_id_counter = 1
    used_student_ids: set[int] = set()
    
    # ========= 1) 2 STUDENT CỐ ĐỊNH =========
    for i, data in enumerate(FIXED_STUDENTS):
        # MSSV unique, giống Populate_data.py
        student_id = generate_unique_student_id(used_student_ids)
        email = f"{data['fname'].lower()}.{data['lname'].lower()}{student_id}@student.university.edu"
        
        # username: student1, student2
        user = User(
            user_id=user_id_counter,
            username=f"student{i+1}",
            password_hash=DEFAULT_PASSWORD,
            role="student",
            email=email,
        )
        session.add(user)
        session.flush()
        
        student = Student(
            user_id=user_id_counter,
            student_id=student_id,
            lname=data["lname"],
            mname=data["mname"],
            fname=data["fname"],
            major=data["major"],
            dob=data["dob"],
            current_gpa=Decimal(str(data["gpa"])),
            target_gpa=Decimal("3.50"),
        )
        session.add(student)
        student_user_ids.append(user_id_counter)
        
        user_id_counter += 1
    
    # ========= 2) STUDENT RANDOM BẰNG FAKER =========
    num_random_students = max(0, NUM_STUDENTS_TOTAL - len(FIXED_STUDENTS))
    majors = [
        "Computer Science",
        "Information Technology",
        "Software Engineering",
        "Data Science",
        "Artificial Intelligence",
    ]
    
    for j in range(num_random_students):
        idx = len(FIXED_STUDENTS) + j + 1  # student3, student4, ...
        
        gender = random.choice(["male", "female"])
        lname = faker.last_name()
        mname = faker.middle_name()
        fname = faker.first_name_male() if gender == "male" else faker.first_name_female()
        major = random.choice(majors)
        dob = faker.date_of_birth(minimum_age=18, maximum_age=22)
        gpa = round(random.uniform(2.0, 4.0), 2)
        
        # MSSV unique
        student_id = generate_unique_student_id(used_student_ids)
        email = f"{fname.lower()}.{lname.lower()}{student_id}@student.university.edu"
        
        user = User(
            user_id=user_id_counter,
            username=f"student{idx}",       # student3..student10
            password_hash=DEFAULT_PASSWORD,
            role="student",
            email=email,
        )
        session.add(user)
        session.flush()
        
        student = Student(
            user_id=user_id_counter,
            student_id=student_id,
            lname=lname,
            mname=mname,
            fname=fname,
            major=major,
            dob=dob,
            current_gpa=Decimal(str(gpa)),
            target_gpa=Decimal("3.50"),
        )
        session.add(student)
        student_user_ids.append(user_id_counter)
        
        user_id_counter += 1
    
    # ========= 3) 2 LECTURER CỐ ĐỊNH =========
    for i, data in enumerate(FIXED_LECTURERS):
        email = f"{data['fname'].lower()}.{data['lname'].lower()}@university.edu"
        
        user = User(
            user_id=user_id_counter,
            username=f"lecturer{i+1}",
            password_hash=DEFAULT_PASSWORD,
            role="lecturer",
            email=email,
        )
        session.add(user)
        session.flush()
        
        lecturer = Lecturer(
            user_id=user_id_counter,
            title=data["title"],
            lname=data["lname"],
            mname=data["mname"],
            fname=data["fname"],
            department=data["department"],
        )
        session.add(lecturer)
        lecturer_user_ids.append(user_id_counter)
        user_id_counter += 1
    
    # ========= 4) LECTURER RANDOM =========
    num_random_lecturers = max(0, NUM_LECTURERS_TOTAL - len(FIXED_LECTURERS))
    departments = [
        "Computer Science",
        "Information Technology",
        "Software Engineering",
        "Data Science",
        "Artificial Intelligence",
    ]
    titles = ["Dr.", "Prof.", "Assoc. Prof."]

    for j in range(num_random_lecturers):
        idx = len(FIXED_LECTURERS) + j + 1  # lecturer3, lecturer4, ...
        
        gender = random.choice(["male", "female"])
        lname = faker.last_name()
        mname = faker.middle_name()
        fname = faker.first_name_male() if gender == "male" else faker.first_name_female()
        dept = random.choice(departments)
        title = random.choice(titles)
        
        email = f"{fname.lower()}.{lname.lower()}@university.edu"
        
        user = User(
            user_id=user_id_counter,
            username=f"lecturer{idx}",
            password_hash=DEFAULT_PASSWORD,
            role="lecturer",
            email=email,
        )
        session.add(user)
        session.flush()
        
        lecturer = Lecturer(
            user_id=user_id_counter,
            title=title,
            lname=lname,
            mname=mname,
            fname=fname,
            department=dept,
        )
        session.add(lecturer)
        lecturer_user_ids.append(user_id_counter)
        user_id_counter += 1
    
    # ========= 5) MANAGER CỐ ĐỊNH =========
    user = User(
        user_id=user_id_counter,
        username="manager1",
        password_hash=DEFAULT_PASSWORD,
        role="manager",
        email="admin.manager@university.edu",
    )
    session.add(user)
    session.flush()
    
    manager = Manager(
        user_id=user_id_counter,
        name=MANAGER_DATA["name"],
        office=MANAGER_DATA["office"],
        position=MANAGER_DATA["position"],
    )
    session.add(manager)
    manager_user_id = user_id_counter
    
    session.commit()
    print(
        f"Created {len(student_user_ids)} students, "
        f"{len(lecturer_user_ids)} lecturers, 1 manager"
    )
    
    return student_user_ids, lecturer_user_ids, manager_user_id

# Thư mục chứa file sample_data.py (tức là thư mục DB/)
BASE_DIR = Path(__file__).resolve().parent

def load_course_data_from_csv(path: Path | None = None):
    """
    Đọc file mon_all.csv (được scrape từ web) và trả về list dict
    có dạng giống COURSE_DATA: [{code, name, credits, capacity, semester}, ...]
    """
    if path is None:
        path = BASE_DIR / "mon_all.csv"

    if not path.exists():
        print(f"[load_course_data_from_csv] File '{path}' không tồn tại.")
        return []

    courses = []
    with path.open(mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                # Các cột theo file scrape: "Mã MH", "Tên MH", "Tín chỉ"
                raw_code = row.get("Mã MH", "").strip()
                raw_name = row.get("Tên MH", "").strip()
                raw_credits = row.get("Tín chỉ", "").strip()

                if not raw_code or not raw_name:
                    continue

                # Lấy số tín chỉ: có thể là "3" hoặc "3(3,0,0)" nên tách phần số đầu tiên
                digits = "".join(ch for ch in raw_credits if ch.isdigit())
                credits = int(digits) if digits else 3
            except Exception as e:
                print(f"  -> Bỏ qua 1 dòng do lỗi: {e} | row = {row}")
                continue

            # Gán capacity + semester "giả" vì CSV không có hai cột này
            capacity = random.choice([30, 40, 50, 60, 70, 80])
            semester = random.choice(["2024-1", "2024-2", "2025-1"])

            courses.append(
                {
                    "code": raw_code,
                    "name": raw_name,
                    "credits": credits,
                    "capacity": capacity,
                    "semester": semester,
                }
            )

    print(f"[load_course_data_from_csv] Đã load {len(courses)} môn từ '{path}'.")
    return courses


def generate_courses(session, lecturer_user_ids):
    """Generate courses from mon_all.csv and assign to lecturers"""
    print("Generating courses...")

    # 1. Load dữ liệu course từ CSV
    course_data = load_course_data_from_csv()

    # 2. Nếu CSV rỗng / lỗi -> fallback về COURSE_DATA (để script vẫn chạy)
    if not course_data:
        print("Không load được course từ CSV, dùng COURSE_DATA mặc định.")
        course_data = COURSE_DATA

    course_ids = []
    for i, data in enumerate(course_data):
        # Assign lecturers in round-robin
        lecturer_id = lecturer_user_ids[i % len(lecturer_user_ids)]

        course = Course(
            course_id=i + 1,
            course_code=data["code"],
            course_name=data["name"],
            credits=data["credits"],
            capacity=data["capacity"],
            semester=data["semester"],
            lecturer_id=lecturer_id,
            description=f"This course covers {data['name'].lower()} concepts and practical applications.",
        )
        session.add(course)
        course_ids.append(i + 1)

    session.commit()
    print(f"Created {len(course_ids)} courses")
    return course_ids

def enrolled_at_from_semester(semester_str: str) -> datetime:
    """
    Tính thời điểm enrolled_at dựa trên mã học kỳ của course.
    semester_str dạng 'YYYY-1/2/3':
      - 'YYYY-1' -> tháng 9 của YYYY
      - 'YYYY-2' -> tháng 1 của YYYY+1
      - 'YYYY-3' -> tháng 6 của YYYY+1
    """
    try:
        year_str, term_str = semester_str.split("-")
        academic_year = int(year_str)
        term = int(term_str)
    except Exception:
        # fallback an toàn nếu format lạ
        academic_year = 2024
        term = 1

    if term == 1:
        year_full = academic_year
        month = 9
    elif term == 2:
        year_full = academic_year + 1
        month = 1
    else:  # term == 3
        year_full = academic_year + 1
        month = 6

    last_day = calendar.monthrange(year_full, month)[1]
    day = random.randint(1, last_day)

    return datetime(
        year_full,
        month,
        day,
        random.randint(7, 18),
        random.randint(0, 59),
    )

def generate_enrollments(session, student_user_ids, course_ids):
    """Generate enrollments - each student enrolls in 4-6 courses"""
    print("Generating enrollments...")

    if not course_ids:
        print("Không có course_ids nào, bỏ qua generate_enrollments.")
        return []

    enroll_id = 1
    enrollments = []

    # Map course_id -> semester của course (đã lưu trong DB)
    courses = (
        session.query(Course)
        .filter(Course.course_id.in_(course_ids))
        .all()
    )
    course_semesters = {c.course_id: c.semester for c in courses}

    for student_id in student_user_ids:
        # Mỗi sinh viên học 4-6 môn
        num_courses = random.randint(4, 6)
        num_courses = min(num_courses, len(course_ids))  # tránh sample > số course

        selected_courses = random.sample(course_ids, num_courses)

        for course_id in selected_courses:
            # Lấy đúng semester mà course đó mở
            semester_str = course_semesters.get(course_id, "2024-1")
            enrolled_at = enrolled_at_from_semester(semester_str)

            enroll = Enroll(
                enroll_id=enroll_id,   # nếu model là Enroll_id thì chỉnh lại tên field
                course_id=course_id,   # tương tự: Course_id, Student_id nếu model dùng camel case
                student_id=student_id,
                semester=semester_str,
                status=random.choice(["active", "active", "active", "completed"]),
                enrolled_at=enrolled_at,
            )
            session.add(enroll)
            enrollments.append((student_id, course_id))
            enroll_id += 1

    session.commit()
    print(f"Created {enroll_id - 1} enrollments")
    return enrollments


def generate_assignments(session, course_ids):
    """Generate 20 assignments across courses"""
    print("Generating assignments...")
    
    assignment_data = []
    assignment_id = 1
    
    assignment_titles = [
        "Homework 1", "Homework 2", "Lab Exercise 1", "Lab Exercise 2",
        "Project Milestone 1", "Project Milestone 2", "Final Project",
        "Quiz Preparation", "Code Review", "Research Paper"
    ]
    
    for course_id in course_ids:
        # 2-3 assignments per course
        num_assignments = random.randint(2, 3)
        selected_titles = random.sample(assignment_titles, num_assignments)
        
        for title in selected_titles:
            deadline = datetime.now() + timedelta(days=random.randint(7, 60))
            assignment = Assignment(
                assignment_id=assignment_id,
                course_id=course_id,
                title=title,
                description=f"Complete the {title.lower()} for this course. Follow the guidelines provided in class.",
                deadline=deadline,
                max_score=Decimal("100.00"),
                created_at=datetime.now() - timedelta(days=random.randint(1, 30))
            )
            session.add(assignment)
            assignment_data.append((assignment_id, course_id))
            assignment_id += 1
            
            if assignment_id > 20:
                break
        if assignment_id > 20:
            break
    
    session.commit()
    print(f"Created {len(assignment_data)} assignments")
    return assignment_data


def generate_submissions(session, assignment_data, enrollments):
    """Generate 30 submissions"""
    print("Generating submissions...")
    
    submission_id = 1
    submissions_created = 0
    
    # Create a mapping of course_id to enrolled students
    course_students = {}
    for student_id, course_id in enrollments:
        if course_id not in course_students:
            course_students[course_id] = []
        course_students[course_id].append(student_id)
    
    for assignment_id, course_id in assignment_data:
        if course_id not in course_students:
            continue
            
        # Random subset of enrolled students submit
        students = course_students[course_id]
        num_submissions = min(len(students), random.randint(2, 4))
        submitting_students = random.sample(students, num_submissions)
        
        for student_id in submitting_students:
            score = Decimal(str(round(random.uniform(60, 100), 2))) if random.random() > 0.2 else None
            
            submission = Submission(
                submission_id=submission_id,
                assignment_id=assignment_id,
                student_id=student_id,
                score=score,
                file_path=f"/uploads/submissions/{submission_id}_assignment_{assignment_id}.pdf",
                submitted_at=datetime.now() - timedelta(days=random.randint(1, 20)),
                graded_at=datetime.now() - timedelta(days=random.randint(0, 5)) if score else None,
                comments="Good work!" if score and score > 80 else "Needs improvement" if score else None
            )
            session.add(submission)
            submission_id += 1
            submissions_created += 1
            
            if submissions_created >= 30:
                break
        if submissions_created >= 30:
            break
    
    session.commit()
    print(f"Created {submissions_created} submissions")


def generate_quizzes_and_questions(session, course_ids):
    """Generate quizzes with 50 questions total"""
    print("Generating quizzes and questions...")
    
    quiz_ids = []
    quiz_id = 1
    question_id = 1
    questions_created = 0
    
    for course_id in course_ids[:5]:  # Create quizzes for 5 courses
        for quiz_num in range(1, 3):  # 2 quizzes per course
            quiz = Quiz(
                quiz_id=quiz_id,
                course_id=course_id,
                title=f"Quiz {quiz_num}",
                description=f"Assessment quiz {quiz_num} for this course.",
                duration_minutes=random.choice([15, 20, 30]),
                max_attempts=random.choice([1, 2, 3]),
                start_time=datetime.now() - timedelta(days=random.randint(1, 30)),
                end_time=datetime.now() + timedelta(days=random.randint(7, 30)),
                created_at=datetime.now() - timedelta(days=random.randint(30, 60))
            )
            session.add(quiz)
            quiz_ids.append(quiz_id)
            
            # 5-7 questions per quiz
            num_questions = random.randint(5, 7)
            for q in range(num_questions):
                template = random.choice(QUIZ_QUESTIONS_TEMPLATES)
                question = QuizQuestion(
                    question_id=question_id,
                    quiz_id=quiz_id,
                    question_text=f"{template['question']} (Q{question_id})",
                    option_a=template['options'][0],
                    option_b=template['options'][1],
                    option_c=template['options'][2] if len(template['options']) > 2 else None,
                    option_d=template['options'][3] if len(template['options']) > 3 else None,
                    correct_option=template['correct'],
                    points=Decimal("1.00")
                )
                session.add(question)
                question_id += 1
                questions_created += 1
                
                if questions_created >= 50:
                    break
            
            quiz_id += 1
            if questions_created >= 50:
                break
        if questions_created >= 50:
            break
    
    session.commit()
    print(f"Created {len(quiz_ids)} quizzes with {questions_created} questions")
    return quiz_ids


def generate_quiz_attempts(session, quiz_ids, student_user_ids):
    """Generate 15 quiz attempts"""
    print("Generating quiz attempts...")
    
    attempt_id = 1
    detail_id = 1
    attempts_created = 0
    
    for quiz_id in quiz_ids:
        # Get questions for this quiz
        questions = session.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
        if not questions:
            continue
        
        # 2-3 students attempt each quiz
        num_attempts = min(len(student_user_ids), random.randint(2, 3))
        attempting_students = random.sample(student_user_ids, num_attempts)
        
        for student_id in attempting_students:
            total_score = Decimal("0.00")
            status = random.choice(["completed", "completed", "completed", "in_progress"])
            
            attempt = QuizAttempt(
                attempt_id=attempt_id,
                quiz_id=quiz_id,
                student_id=student_id,
                started_at=datetime.now() - timedelta(hours=random.randint(1, 100)),
                finished_at=datetime.now() - timedelta(hours=random.randint(0, 50)) if status == "completed" else None,
                total_score=None,
                status=status
            )
            session.add(attempt)
            session.flush()
            
            # Create attempt details for each question
            for question in questions:
                is_correct = random.random() > 0.3  # 70% chance of correct answer
                chosen = question.correct_option if is_correct else random.choice(['A', 'B', 'C', 'D'])
                
                detail = QuizAttemptDetail(
                    detail_id=detail_id,
                    attempt_id=attempt_id,
                    question_id=question.question_id,
                    chosen_option=chosen,
                    is_correct=is_correct
                )
                session.add(detail)
                detail_id += 1
                
                if is_correct:
                    total_score += question.points
            
            # Update total score if completed
            if status == "completed":
                attempt.total_score = total_score
            
            attempt_id += 1
            attempts_created += 1
            
            if attempts_created >= 15:
                break
        if attempts_created >= 15:
            break
    
    session.commit()
    print(f"Created {attempts_created} quiz attempts")


def generate_messages(session, student_user_ids, lecturer_user_ids, manager_user_id):
    """Generate 100 messages"""
    print("Generating messages...")
    
    all_user_ids = student_user_ids + lecturer_user_ids + [manager_user_id]
    
    message_templates = [
        "Hello! I have a question about the recent assignment.",
        "Thank you for your feedback on my submission.",
        "When is the next deadline for the project?",
        "Can you please clarify the grading criteria?",
        "I need help understanding the course material.",
        "The lecture was very helpful, thank you!",
        "Is there any additional reading material available?",
        "I will be absent for the next class due to a medical appointment.",
        "Can we schedule a meeting to discuss my progress?",
        "Thank you for the extension on the assignment.",
        "I have submitted my work, please review when possible.",
        "The study group session was very productive.",
    ]
    
    for msg_id in range(1, 101):
        sender_id = random.choice(all_user_ids)
        # Ensure receiver is different from sender
        receiver_id = random.choice([uid for uid in all_user_ids if uid != sender_id])
        
        message = Message(
            message_id=msg_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=random.choice(message_templates),
            is_read=random.choice([True, True, False]),
            created_at=datetime.now() - timedelta(hours=random.randint(1, 500))
        )
        session.add(message)
    
    session.commit()
    print("Created 100 messages")


def generate_feedback(session, enrollments):
    print("Generating feedback...")

    feedback_templates = [
        "Excellent course! The professor explains concepts very clearly.",
        "Good course content but could use more practical examples.",
        "The assignments were challenging but helped me learn a lot.",
        "Would appreciate more interactive sessions.",
        "Great learning experience, highly recommend this course.",
        "The pace was a bit fast, but overall good content.",
        "Very informative lectures with good supporting materials.",
        "Could benefit from more group projects.",
    ]

    # Lấy các cặp (student_id, course_id) unique
    unique_enrollments = list(set(enrollments))
    random.shuffle(unique_enrollments)

    # Số feedback tối đa có thể tạo
    max_feedback = min(50, len(unique_enrollments))

    for feedback_id in range(1, max_feedback + 1):
        student_id, course_id = unique_enrollments[feedback_id - 1]

        feedback = Feedback(
            feedback_id=feedback_id,
            content=random.choice(feedback_templates),
            rating=random.randint(3, 5),
            student_id=student_id,
            course_id=course_id,
            created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
        )
        session.add(feedback)

    session.commit()
    print(f"Created {max_feedback} feedback entries")

def generate_course_ratings(session, enrollments):
    print("Generating course ratings...")

    rating_comments = [
        "Loved this course!",
        "Very helpful for my career.",
        "Great instructor.",
        "Well-structured curriculum.",
        "Challenging but rewarding.",
    ]

    unique_enrollments = list(set(enrollments))
    random.shuffle(unique_enrollments)

    max_ratings = min(20, len(unique_enrollments))

    for rating_id in range(1, max_ratings + 1):
        student_id, course_id = unique_enrollments[rating_id - 1]

        rating = CourseRating(
            rating_id=rating_id,
            student_id=student_id,
            course_id=course_id,
            rating=random.randint(3, 5),
            comment=random.choice(rating_comments) if random.random() > 0.3 else None,
            created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
        )
        session.add(rating)

    session.commit()
    print(f"Created {max_ratings} course ratings")

def generate_materials(session, course_ids):
    """Generate course materials"""
    print("Generating course materials...")
    
    material_types = ["lecture", "document", "video", "quiz"]
    material_id = 1
    
    for course_id in course_ids:
        for i in range(random.randint(2, 4)):
            mat_type = random.choice(material_types)
            material = Materials(
                materials_id=material_id,
                course_id=course_id,
                type=mat_type,
                title=f"Course Material {material_id}: {mat_type.capitalize()}",
                description=f"This is a {mat_type} resource for the course.",
                file_path=f"/uploads/materials/{course_id}_{material_id}.pdf",
                upload_date=datetime.now() - timedelta(days=random.randint(1, 90))
            )
            session.add(material)
            material_id += 1
    
    session.commit()
    print(f"Created {material_id - 1} course materials")


def main():
    print("=" * 50)
    print("LMS Sample Data Generation Script")
    print("=" * 50)
    
    # Create session
    session = SessionLocal()
    
    try:
        # Clear existing data
        clear_data(session)
        
        # Generate data in order
        student_user_ids, lecturer_user_ids, manager_user_id = generate_users(session)
        course_ids = generate_courses(session, lecturer_user_ids)
        enrollments = generate_enrollments(session, student_user_ids, course_ids)
        assignment_data = generate_assignments(session, course_ids)
        generate_submissions(session, assignment_data, enrollments)
        quiz_ids = generate_quizzes_and_questions(session, course_ids)
        generate_quiz_attempts(session, quiz_ids, student_user_ids)
        generate_messages(session, student_user_ids, lecturer_user_ids, manager_user_id)
        generate_feedback(session, enrollments)
        generate_course_ratings(session, enrollments)
        generate_materials(session, course_ids)
        
        print("\n" + "=" * 50)
        print("Sample data generation completed successfully!")
        print("=" * 50)
        print("\nLogin credentials:")
        print("  Students: student1 to student10")
        print("  Lecturers: lecturer1 to lecturer5")
        print("  Manager: manager1")
        print("  Password for all: password123")
        
    except Exception as e:
        session.rollback()
        print(f"Error: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
