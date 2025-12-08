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
import unicodedata
import json

faker = Faker("vi_VN")  # Vietnamese name for random user generation

# Add BE/app to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'BE', 'app'))

from requests import session
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
    {"lname": "Nguyễn", "mname": "Văn", "fname": "An", "major": "Computer Science", "dob": date(2005, 5, 15), "gpa": 3.45},
    {"lname": "Trần", "mname": "Thị", "fname": "Bình", "major": "Information Technology", "dob": date(2004, 8, 20), "gpa": 3.72},
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
    {"title": "Dr.", "lname": "Nguyễn", "mname": "Quang", "fname": "Hiếu", "department": "Computer Science"},
    {"title": "Prof.", "lname": "Trần", "mname": "Thị", "fname": "Mai", "department": "Information Technology"},
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
NUM_STUDENTS_TOTAL = 1000
NUM_LECTURERS_TOTAL = 50
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

def create_student_id_from_entrance_year(entrance_year: int) -> int:
    """
    Tạo MSSV từ năm nhập học.

    Ví dụ:
      entrance_year = 2023 -> prefix = '23' + '5' = '235' -> MSSV: 235xxxx
    """
    year_suffix = entrance_year % 100          # 2023 -> 23
    id_prefix = f"{year_suffix}5"              # '235'
    id_suffix = faker.numerify(text="####")    # '1234'
    student_id_str = f"{id_prefix}{id_suffix}" # '2351234'
    return int(student_id_str)

def enumerate_semesters(entrance_year: int, last_year: int = 2025, last_term: int = 1) -> list[str]:
    """
    Sinh danh sách học kỳ từ entrance_year-1 đến last_year-last_term.
    Giả định 1 năm có 3 kỳ: 1, 2, 3 (YYYY-1/2/3).

    VD: entrance_year = 2022, last_year=2025, last_term=1
      -> ['2022-1', '2022-2', '2022-3', '2023-1', ..., '2025-1']
    """
    semesters: list[str] = []

    if entrance_year > last_year:
        return semesters

    for year in range(entrance_year, last_year + 1):
        for term in (1, 2, 3):
            if year == last_year and term > last_term:
                break
            semesters.append(f"{year}-{term}")

    return semesters


def _generate_gpa_series(num_semesters: int, current_gpa: float, target_gpa: float) -> list[float]:
    """
    Sinh list GPA cho num_semesters kỳ:
      - GPA dao động nhẹ quanh target/current
      - Xu hướng tăng hoặc ổn định dần về current_gpa
    """
    if num_semesters <= 0:
        return []

    # GPA bắt đầu hơi thấp hơn hiện tại một chút
    g = max(1.0, min(3.5, current_gpa - random.uniform(0.3, 0.8)))
    series: list[float] = []

    for i in range(num_semesters):
        progress = (i + 1) / num_semesters  # 0..1

        # đầu giai đoạn kéo về target, cuối giai đoạn kéo về current
        desired = target_gpa if progress < 0.5 else current_gpa

        drift = (desired - g) * 0.35          # lực kéo về desired
        noise = random.uniform(-0.25, 0.25)   # nhiễu nhỏ

        g = g + drift + noise
        g = max(1.0, min(4.0, g))            # clamp trong [1, 4]

        series.append(round(g, 2))

    return series

def generate_unique_student_id(used_ids: set[int], entrance_year: int) -> int:
    """
    Sinh MSSV unique cho một entrance_year nhất định.
    """
    while True:
        sid = create_student_id_from_entrance_year(entrance_year)
        if sid not in used_ids:
            used_ids.add(sid)
            return sid



def _sanitize_email_local(local_part: str) -> str:
    normalized = unicodedata.normalize("NFKD", local_part)
    ascii_local = normalized.encode("ascii", "ignore").decode("ascii")
    cleaned = "".join(ch if ch.isalnum() else "." for ch in ascii_local.lower())
    cleaned = cleaned.strip(".")
    return cleaned or "user"


def generate_unique_email(local_part: str, domain: str, used_emails: set[str]) -> str:
    base_local = _sanitize_email_local(local_part)
    candidate = f"{base_local}@{domain}"
    counter = 1
    while candidate in used_emails:
        candidate = f"{base_local}{counter}@{domain}"
        counter += 1
    used_emails.add(candidate)
    return candidate

def generate_users(session):
    """Generate users, students, lecturers, and manager (fixed + random mix)"""
    print("Generating users...")
    
    student_user_ids = []
    lecturer_user_ids = []
    manager_user_id = None
    
    user_id_counter = 1
    used_student_ids: set[int] = set()
    used_emails: set[str] = set()
    
    # ========= 1) 2 STUDENT CỐ ĐỊNH =========
    for i, data in enumerate(FIXED_STUDENTS):
        dob: date = data["dob"]
        # Giả định vào đại học năm 18 tuổi
        entrance_year = dob.year + 18

        # MSSV unique theo entrance_year
        student_id = generate_unique_student_id(used_student_ids, entrance_year)

        email_local = f"{data['fname']}.{data['lname']}{student_id}"
        email = generate_unique_email(email_local, "student.university.edu", used_emails)
        
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
            dob=dob,
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
        
        ## Năm nhập học = năm sinh + 18
        entrance_year = dob.year + 18

        # MSSV unique theo entrance_year
        student_id = generate_unique_student_id(used_student_ids, entrance_year)
        email_local = f"{fname}.{lname}{student_id}"
        email = generate_unique_email(email_local, "student.university.edu", used_emails)
        
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
        email_local = f"{data['fname']}.{data['lname']}"
        email = generate_unique_email(email_local, "university.edu", used_emails)
        
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
        
        email_local = f"{fname}.{lname}"
        email = generate_unique_email(email_local, "university.edu", used_emails)
        
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
    manager_email = generate_unique_email("admin.manager", "university.edu", used_emails)
    user = User(
        user_id=user_id_counter,
        username="manager1",
        password_hash=DEFAULT_PASSWORD,
        role="manager",
        email=manager_email,
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

def generate_student_gpa_history(session, student_user_ids, last_year: int = 2025, last_term: int = 1):
    """
    Sinh lịch sử GPA theo từng kỳ cho các student và lưu vào
    cột gpa_history của bảng Student.

    Format JSON lưu trong student.gpa_history:

    {
      "entrance_year": 2022,
      "semesters": [
        {"semester": "2022-1", "gpa": 3.2, "overall_gpa": 3.2},
        {"semester": "2022-2", "gpa": 3.0, "overall_gpa": 3.1},
        ...
      ]
    }
    """
    print("Generating GPA history (Student.gpa_history)...")

    # Lấy các Student object tương ứng danh sách user_id
    students = (
        session.query(Student)
        .filter(Student.user_id.in_(student_user_ids))
        .all()
    )

    if not students:
        print("Không tìm thấy student nào, bỏ qua generate_student_gpa_history.")
        return

    updated = 0

    for stu in students:
        if not stu.student_id:
            continue

        # 1) Năm nhập học từ MSSV (vd: 235xxxx -> 23 -> 2023)
        entrance_year = entrance_year_from_student_id(stu.student_id)
        if entrance_year is None:
            entrance_year = 2022  # fallback an toàn

        # 2) Danh sách các kỳ từ entrance_year -> last_year-last_term (vd 2025-1)
        semesters = enumerate_semesters(entrance_year, last_year, last_term)
        if not semesters:
            continue

        # 3) current_gpa & target_gpa làm mốc
        try:
            current_gpa_val = float(stu.current_gpa) if stu.current_gpa is not None else random.uniform(2.0, 3.5)
        except Exception:
            current_gpa_val = random.uniform(2.0, 3.5)

        try:
            target_gpa_val = float(stu.target_gpa) if stu.target_gpa is not None else current_gpa_val
        except Exception:
            target_gpa_val = current_gpa_val

        # 4) Sinh dãy GPA cho từng kỳ (GPA của từng kỳ)
        term_gpas = _generate_gpa_series(len(semesters), current_gpa_val, target_gpa_val)

        # 5) Tính overall GPA tích luỹ cho từng kỳ
        semester_entries = []
        cum_sum = 0.0

        for idx, (sem, g) in enumerate(zip(semesters, term_gpas), start=1):
            cum_sum += g
            overall = round(cum_sum / idx, 2)  # average từ kỳ 1 -> kỳ hiện tại

            semester_entries.append(
                {
                    "semester": sem,
                    "gpa": g,              # GPA của kỳ đó
                    "overall_gpa": overall # GPA tích lũy tới kỳ đó
                }
            )

        history = {
            "entrance_year": entrance_year,
            "semesters": semester_entries,
        }

        # 6) Lưu vào cột gpa_history của Student (TEXT → JSON string)
        stu.gpa_history = json.dumps(history, ensure_ascii=False)

        # 7) Cập nhật current_gpa = overall GPA mới nhất
        if semester_entries:
            last_overall = semester_entries[-1]["overall_gpa"]
            stu.current_gpa = Decimal(str(last_overall))

        updated += 1

    session.commit()
    print(f"Generated GPA history for {updated} students.")


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

def entrance_year_from_student_id(student_id: int) -> int:
    s = str(student_id)
    if len(s) < 3:
        # fallback an toàn
        return 2023
    yy = int(s[:2])      # lấy 2 số đầu
    return 2000 + yy     # giả định nằm trong thế kỷ 21

def get_course_image_url(course_code: str) -> str:
    """
    Tạo URL ảnh từ web (Picsum) dựa trên course_code.
    Mỗi course_code sẽ có một ảnh khác nhau nhưng cố định.
    """
    # seed không được có dấu cách, nên thay bằng '-'
    safe_code = course_code.replace(" ", "-")
    # 800x400 tuỳ bạn chỉnh
    return f"https://picsum.photos/seed/{safe_code}/800/400"

def generate_courses(session, lecturer_user_ids):
    print("Generating courses...")

    course_ids = []
    course_data = load_course_data_from_csv()
    if not course_data:
        print("Không load được course từ CSV, dùng COURSE_DATA mặc định.")
        course_data = COURSE_DATA

    for i, data in enumerate(course_data):
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
            image_url=get_course_image_url(data["code"]),
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

def generate_enrollments(session, student_user_ids, course_ids, fixed_ids=None):
    """Generate enrollments:
       - student1 & student2 có kịch bản riêng
       - các student khác random 4-6 môn
    """
    print("Generating enrollments...")

    if not course_ids:
        print("Không có course_ids nào, bỏ qua generate_enrollments.")
        return []

    enrollments: list[tuple[int, int]] = []

    # Lấy info course từ DB để biết semester + lecturer_id
    courses = session.query(Course).filter(Course.course_id.in_(course_ids)).all()
    course_by_id = {c.course_id: c for c in courses}

    # Nếu không truyền fixed_ids thì fallback random toàn bộ như cũ
    if fixed_ids is None:
        for student_id in student_user_ids:
            num_courses = random.randint(4, 6)
            num_courses = min(num_courses, len(course_ids))
            selected_courses = random.sample(course_ids, num_courses)

            for course_id in selected_courses:
                semester_str = course_by_id[course_id].semester
                enrolled_at = enrolled_at_from_semester(semester_str)

                enroll = Enroll(
                    # KHÔNG set enroll_id nữa → để DB tự tăng
                    course_id=course_id,
                    student_id=student_id,
                    semester=semester_str,
                    status=random.choice(["active", "active", "active", "completed"]),
                    enrolled_at=enrolled_at,
                )
                session.add(enroll)
                enrollments.append((student_id, course_id))

        session.commit()
        print(f"Created {len(enrollments)} enrollments")
        return enrollments

    # === Kịch bản cho user cố định ===
    student1_id = fixed_ids["student1"]
    student2_id = fixed_ids["student2"]
    lecturer1_id = fixed_ids["lecturer1"]
    lecturer2_id = fixed_ids["lecturer2"]

    # Các course do lecturer1 & lecturer2 dạy
    courses_l1 = [c.course_id for c in courses if c.lecturer_id == lecturer1_id]
    courses_l2 = [c.course_id for c in courses if c.lecturer_id == lecturer2_id]

    other_courses = [
        c_id for c_id in course_ids if c_id not in set(courses_l1 + courses_l2)
    ]

    # Helper chọn môn cho 1 student
    def choose_courses(core_list, backup_list, min_n=4, max_n=6):
        chosen = []

        # Lấy ưu tiên từ core_list
        core_copy = list(core_list)
        random.shuffle(core_copy)
        for c_id in core_copy:
            if len(chosen) >= max_n:
                break
            chosen.append(c_id)

        # Nếu còn thiếu so với min_n thì bổ sung từ backup
        remaining = min_n - len(chosen)
        if remaining > 0:
            backup_candidates = [c for c in backup_list if c not in chosen]
            extra = random.sample(
                backup_candidates, k=min(remaining, len(backup_candidates))
            )
            chosen.extend(extra)

        return chosen

    # --- student1: ưu tiên học các môn của lecturer1 ---
    s1_courses = choose_courses(courses_l1, other_courses, min_n=4, max_n=6)
    for course_id in s1_courses:
        semester_str = course_by_id[course_id].semester
        enrolled_at = enrolled_at_from_semester(semester_str)
        enroll = Enroll(
            course_id=course_id,
            student_id=student1_id,
            semester=semester_str,
            status="active",
            enrolled_at=enrolled_at,
        )
        session.add(enroll)
        enrollments.append((student1_id, course_id))

    # --- student2: ưu tiên học các môn của lecturer2 ---
    s2_courses = choose_courses(courses_l2, other_courses, min_n=4, max_n=6)
    for course_id in s2_courses:
        semester_str = course_by_id[course_id].semester
        enrolled_at = enrolled_at_from_semester(semester_str)
        enroll = Enroll(
            course_id=course_id,
            student_id=student2_id,
            semester=semester_str,
            status=random.choice(["active", "completed"]),
            enrolled_at=enrolled_at,
        )
        session.add(enroll)
        enrollments.append((student2_id, course_id))

    # --- Các student còn lại: random như cũ ---
    other_students = [sid for sid in student_user_ids if sid not in (student1_id, student2_id)]

    for student_id in other_students:
        num_courses = random.randint(4, 6)
        num_courses = min(num_courses, len(course_ids))
        selected_courses = random.sample(course_ids, num_courses)

        for course_id in selected_courses:
            semester_str = course_by_id[course_id].semester
            enrolled_at = enrolled_at_from_semester(semester_str)
            enroll = Enroll(
                course_id=course_id,
                student_id=student_id,
                semester=semester_str,
                status=random.choice(["active", "active", "completed"]),
                enrolled_at=enrolled_at,
            )
            session.add(enroll)
            enrollments.append((student_id, course_id))

    session.commit()
    print(f"Created {len(enrollments)} enrollments (with fixed-user scenario)")
    return enrollments



# add status field to Assignment model before using this function
def generate_assignments(session, course_ids):
    """Generate 200 assignments across courses"""
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
            
            if assignment_id > 200:
                break
        if assignment_id > 200:
            break
    
    session.commit()
    print(f"Created {len(assignment_data)} assignments")
    return assignment_data


def generate_submissions(session, assignment_data, enrollments, fixed_ids=None, max_submissions=500):
    """Generate submissions.
       - student1: luôn nộp, điểm cao, đúng/sớm hạn
       - student2: nộp phần lớn, điểm trung bình-khá, đôi khi trễ hoặc không nộp
       - các student khác: random như cũ
    """
    print("Generating submissions...")

    submission_id = 1
    submissions_created = 0

    # Map course_id -> list student_id đã enroll
    course_students: dict[int, list[int]] = {}
    for student_id, course_id in enrollments:
        course_students.setdefault(course_id, []).append(student_id)

    # Map assignment_id -> object Assignment (để lấy deadline)
    assignment_ids = [aid for aid, _ in assignment_data]
    assignments = (
        session.query(Assignment)
        .filter(Assignment.assignment_id.in_(assignment_ids))
        .all()
    )
    assignment_by_id = {a.assignment_id: a for a in assignments}

    # Để tránh tạo trùng (assignment_id, student_id)
    submitted_pairs: set[tuple[int, int]] = set()

    # Nếu không có fixed_ids thì dùng logic random cũ
    if fixed_ids is None:
        for assignment_id, course_id in assignment_data:
            if course_id not in course_students:
                continue

            students = course_students[course_id]
            num_submissions = min(len(students), random.randint(2, 4))
            submitting_students = random.sample(students, num_submissions)

            for student_id in submitting_students:
                if submissions_created >= max_submissions:
                    break

                score = (
                    Decimal(str(round(random.uniform(60, 100), 2)))
                    if random.random() > 0.2
                    else None
                )

                base_deadline = assignment_by_id.get(assignment_id).deadline if assignment_id in assignment_by_id else datetime.now()
                submitted_at = base_deadline - timedelta(days=random.randint(1, 20))
                graded_at = (
                    submitted_at + timedelta(days=random.randint(0, 5))
                    if score is not None
                    else None
                )
                comments = (
                    "Good work!" if score and score > 80 else "Needs improvement" if score else None
                )

                submission = Submission(
                    submission_id=submission_id,
                    assignment_id=assignment_id,
                    student_id=student_id,
                    score=score,
                    file_path=f"/uploads/submissions/{submission_id}_assignment_{assignment_id}.pdf",
                    submitted_at=submitted_at,
                    graded_at=graded_at,
                    comments=comments,
                )
                session.add(submission)
                submission_id += 1
                submissions_created += 1

            if submissions_created >= max_submissions:
                break

        session.commit()
        print(f"Created {submissions_created} submissions (random-only)")
        return

    # ================== KỊCH BẢN FIXED USERS ==================
    student1_id = fixed_ids["student1"]
    student2_id = fixed_ids["student2"]

    for assignment_id, course_id in assignment_data:
        if submissions_created >= max_submissions:
            break
        if course_id not in course_students:
            continue

        students = course_students[course_id]
        base_deadline = assignment_by_id.get(assignment_id).deadline if assignment_id in assignment_by_id else datetime.now()

        # ---- 1) student1: luôn nộp, điểm cao, đúng/sớm hạn ----
        if student1_id in students and (assignment_id, student1_id) not in submitted_pairs:
            days_before = random.randint(0, 3)  # nộp sớm / đúng hạn
            submitted_at = base_deadline - timedelta(days=days_before)
            score_val = Decimal(str(round(random.uniform(85, 100), 2)))
            graded_at = submitted_at + timedelta(days=random.randint(0, 3))
            comment = "Excellent work!"

            submission = Submission(
                submission_id=submission_id,
                assignment_id=assignment_id,
                student_id=student1_id,
                score=score_val,
                file_path=f"/uploads/submissions/{submission_id}_assignment_{assignment_id}.pdf",
                submitted_at=submitted_at,
                graded_at=graded_at,
                comments=comment,
            )
            session.add(submission)
            submitted_pairs.add((assignment_id, student1_id))
            submission_id += 1
            submissions_created += 1

        if submissions_created >= max_submissions:
            break

        # ---- 2) student2: nộp phần lớn, có thể trễ hoặc bỏ 1 số bài ----
        if student2_id in students and (assignment_id, student2_id) not in submitted_pairs:
            # 20% khả năng không nộp assignment này
            if random.random() > 0.2:
                delta_days = random.randint(-3, 5)  # có thể sớm 3 ngày, trễ 5 ngày
                submitted_at = base_deadline + timedelta(days=delta_days)
                score_val = Decimal(str(round(random.uniform(70, 95), 2)))
                graded_at = submitted_at + timedelta(days=random.randint(0, 5))
                comment = (
                    "Good effort, but can be improved."
                    if score_val < 85
                    else "Good work!"
                )

                submission = Submission(
                    submission_id=submission_id,
                    assignment_id=assignment_id,
                    student_id=student2_id,
                    score=score_val,
                    file_path=f"/uploads/submissions/{submission_id}_assignment_{assignment_id}.pdf",
                    submitted_at=submitted_at,
                    graded_at=graded_at,
                    comments=comment,
                )
                session.add(submission)
                submitted_pairs.add((assignment_id, student2_id))
                submission_id += 1
                submissions_created += 1

        if submissions_created >= max_submissions:
            break

        # ---- 3) Các sinh viên khác: random giống logic cũ ----
        other_students = [sid for sid in students if sid not in (student1_id, student2_id)]
        if not other_students:
            continue

        num_submissions = min(len(other_students), random.randint(1, 3))
        submitting_students = random.sample(other_students, num_submissions)

        for sid in submitting_students:
            if submissions_created >= max_submissions:
                break
            if (assignment_id, sid) in submitted_pairs:
                continue

            if random.random() > 0.2:
                # nộp + có điểm
                delta_days = random.randint(-2, 7)
                submitted_at = base_deadline + timedelta(days=delta_days)
                score_val = Decimal(str(round(random.uniform(60, 100), 2)))
                graded_at = submitted_at + timedelta(days=random.randint(0, 7))
                comment = "Good work!" if score_val > 80 else "Needs improvement"
            else:
                # nộp nhưng chưa chấm
                submitted_at = base_deadline + timedelta(days=random.randint(-1, 3))
                score_val = None
                graded_at = None
                comment = None

            submission = Submission(
                submission_id=submission_id,
                assignment_id=assignment_id,
                student_id=sid,
                score=score_val,
                file_path=f"/uploads/submissions/{submission_id}_assignment_{assignment_id}.pdf",
                submitted_at=submitted_at,
                graded_at=graded_at,
                comments=comment,
            )
            session.add(submission)
            submitted_pairs.add((assignment_id, sid))
            submission_id += 1
            submissions_created += 1

    session.commit()
    print(f"Created {submissions_created} submissions (with fixed-user scenario)")


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


def generate_quiz_attempts(session, quiz_ids, student_user_ids, enrollments, fixed_ids=None, max_attempts=40):
    """Generate quiz attempts.
       - Chỉ sinh attempt cho sinh viên đã enroll course tương ứng.
       - student1: điểm cao, hầu hết quiz completed.
       - student2: điểm khá, đôi khi in_progress hoặc làm sai nhiều hơn.
       - Các sinh viên khác: random như cũ.
    """
    print("Generating quiz attempts...")

    attempt_id = 1
    detail_id = 1
    attempts_created = 0

    # Map course_id -> list student_id đã enroll
    course_students: dict[int, list[int]] = {}
    for student_id, course_id in enrollments:
        course_students.setdefault(course_id, []).append(student_id)

    # Lấy thông tin quiz (để biết course_id, thời gian)
    quizzes = (
        session.query(Quiz)
        .filter(Quiz.quiz_id.in_(quiz_ids))
        .all()
    )
    quiz_by_id = {q.quiz_id: q for q in quizzes}

    # Nếu không có fixed_ids -> dùng logic gần giống cũ, nhưng tôn trọng enrollments
    if fixed_ids is None:
        for quiz_id in quiz_ids:
            if attempts_created >= max_attempts:
                break

            quiz = quiz_by_id.get(quiz_id)
            if quiz is None:
                continue

            students = course_students.get(quiz.course_id, [])
            if not students:
                continue

            questions = session.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
            if not questions:
                continue

            num_attempts = min(len(students), random.randint(2, 3))
            attempting_students = random.sample(students, num_attempts)

            for student_id in attempting_students:
                if attempts_created >= max_attempts:
                    break

                # thời gian làm quiz
                started_at = quiz.start_time + timedelta(
                    minutes=random.randint(0, max(1, quiz.duration_minutes - 5))
                )
                status = random.choice(["completed", "completed", "completed", "in_progress"])
                finished_at = (
                    started_at + timedelta(minutes=random.randint(5, quiz.duration_minutes))
                    if status == "completed"
                    else None
                )

                total_score = Decimal("0.00")
                attempt = QuizAttempt(
                    attempt_id=attempt_id,
                    quiz_id=quiz_id,
                    student_id=student_id,
                    started_at=started_at,
                    finished_at=finished_at,
                    total_score=None,
                    status=status,
                )
                session.add(attempt)
                session.flush()

                for question in questions:
                    # 70% đúng như cũ
                    is_correct = random.random() > 0.3
                    if is_correct:
                        chosen = question.correct_option
                    else:
                        wrong_options = [opt for opt in ["A", "B", "C", "D"] if opt != question.correct_option]
                        chosen = random.choice(wrong_options) if wrong_options else question.correct_option

                    detail = QuizAttemptDetail(
                        detail_id=detail_id,
                        attempt_id=attempt_id,
                        question_id=question.question_id,
                        chosen_option=chosen,
                        is_correct=is_correct,
                    )
                    session.add(detail)
                    detail_id += 1

                    if is_correct:
                        total_score += question.points

                if status == "completed":
                    attempt.total_score = total_score

                attempt_id += 1
                attempts_created += 1

        session.commit()
        print(f"Created {attempts_created} quiz attempts (random-only)")
        return

    # ================== KỊCH BẢN FIXED USERS ==================
    student1_id = fixed_ids["student1"]
    student2_id = fixed_ids["student2"]

    for quiz_id in quiz_ids:
        if attempts_created >= max_attempts:
            break

        quiz = quiz_by_id.get(quiz_id)
        if quiz is None:
            continue

        students = course_students.get(quiz.course_id, [])
        if not students:
            continue

        questions = session.query(QuizQuestion).filter(QuizQuestion.quiz_id == quiz_id).all()
        if not questions:
            continue

        # --- Helper sinh 1 attempt với mức độ chính xác cho trước ---
        def create_attempt_for_student(sid: int, accuracy: float, force_completed: bool = True, allow_in_progress: bool = False):
            nonlocal attempt_id, detail_id, attempts_created

            if attempts_created >= max_attempts:
                return

            started_at = quiz.start_time + timedelta(
                minutes=random.randint(0, max(1, quiz.duration_minutes - 5))
            )

            if force_completed:
                status = "completed"
            elif allow_in_progress and random.random() < 0.2:
                status = "in_progress"
            else:
                status = "completed"

            finished_at = (
                started_at + timedelta(minutes=random.randint(5, quiz.duration_minutes))
                if status == "completed"
                else None
            )

            total_score = Decimal("0.00")
            attempt = QuizAttempt(
                attempt_id=attempt_id,
                quiz_id=quiz_id,
                student_id=sid,
                started_at=started_at,
                finished_at=finished_at,
                total_score=None,
                status=status,
            )
            session.add(attempt)
            session.flush()

            for question in questions:
                # accuracy: xác suất trả lời đúng
                is_correct = random.random() < accuracy
                if is_correct:
                    chosen = question.correct_option
                else:
                    wrong_options = [opt for opt in ["A", "B", "C", "D"] if opt != question.correct_option]
                    chosen = random.choice(wrong_options) if wrong_options else question.correct_option

                detail = QuizAttemptDetail(
                    detail_id=detail_id,
                    attempt_id=attempt_id,
                    question_id=question.question_id,
                    chosen_option=chosen,
                    is_correct=is_correct,
                )
                session.add(detail)
                detail_id += 1

                if is_correct:
                    total_score += question.points

            if status == "completed":
                attempt.total_score = total_score

            attempt_id += 1
            attempts_created += 1

        # --- 1) student1: nếu enroll course này thì hầu như luôn attempt, accuracy cao ---
        if student1_id in students:
            # 90% chính xác
            create_attempt_for_student(student1_id, accuracy=0.9, force_completed=True)

        if attempts_created >= max_attempts:
            break

        # --- 2) student2: nếu enroll course này thì thường attempt, accuracy trung bình-khá ---
        if student2_id in students:
            # 75% chính xác, đôi khi in_progress
            create_attempt_for_student(student2_id, accuracy=0.75, force_completed=False, allow_in_progress=True)

        if attempts_created >= max_attempts:
            break

        # --- 3) Các sinh viên khác: random như cũ ---
        other_students = [sid for sid in students if sid not in (student1_id, student2_id)]
        if not other_students:
            continue

        num_attempts = min(len(other_students), random.randint(1, 3))
        attempting_students = random.sample(other_students, num_attempts)

        for sid in attempting_students:
            if attempts_created >= max_attempts:
                break
            # accuracy 70% như logic cũ
            create_attempt_for_student(sid, accuracy=0.7, force_completed=False, allow_in_progress=True)

    session.commit()
    print(f"Created {attempts_created} quiz attempts (with fixed-user scenario)")


def generate_messages(session, student_user_ids, lecturer_user_ids, manager_user_id):
    """Generate ~100 messages with a storyline for fixed users (in English)."""
    print("Generating messages...")

    all_user_ids = student_user_ids + lecturer_user_ids + [manager_user_id]

    generic_templates = [
        "Hello! I have a question about the recent assignment.",
        "Thank you for your feedback on my submission.",
        "When is the next deadline for the project?",
        "Could you please clarify the grading criteria?",
        "I need some help understanding the course material.",
        "The lecture was very helpful, thank you!",
        "Is there any additional reading material available?",
        "I will be absent for the next class due to a medical appointment.",
        "Can we schedule a meeting to discuss my progress?",
        "Thank you for the extension on the assignment.",
        "I have submitted my work. Please review it when you have time.",
        "The study group session was very productive.",
    ]

    # Fixed users (by order)
    student1_id = student_user_ids[0] if len(student_user_ids) > 0 else None
    student2_id = student_user_ids[1] if len(student_user_ids) > 1 else None
    lecturer1_id = lecturer_user_ids[0] if len(lecturer_user_ids) > 0 else None
    lecturer2_id = lecturer_user_ids[1] if len(lecturer_user_ids) > 1 else None
    manager_id = manager_user_id

    # ============ 1. Scripted conversations (in English) ============
    scripted_messages: list[tuple[int, int, str]] = []

    # student1 <-> lecturer1: assignment questions, rubric, office hours
    if student1_id and lecturer1_id:
        scripted_messages.extend([
            (student1_id, lecturer1_id, "Hi professor, I have a question about Assignment 2."),
            (lecturer1_id, student1_id, "Sure, please check the example in last week's slides."),
            (student1_id, lecturer1_id, "Got it now, thank you so much!"),
            (lecturer1_id, student1_id, "If you need more help, feel free to join my office hours tomorrow."),
            (student1_id, lecturer1_id, "Could you please explain the grading rubric for the final project?"),
            (lecturer1_id, student1_id, "I've just uploaded the rubric to the LMS under the Assignments section."),
        ])

    # student2 <-> lecturer2: absence, extension, submission
    if student2_id and lecturer2_id:
        scripted_messages.extend([
            (student2_id, lecturer2_id, "Hi, I might miss the lab session next week due to a medical appointment."),
            (lecturer2_id, student2_id, "No problem. Please watch the recording and review the slides afterwards."),
            (student2_id, lecturer2_id, "Could I get a one-day extension for the lab report, please?"),
            (lecturer2_id, student2_id, "Yes, that's fine. Just make sure to submit it by tomorrow 11:59 PM."),
            (student2_id, lecturer2_id, "I have submitted the lab report. Could you please take a look when you can?"),
        ])

    # manager <-> lecturers: progress and attendance
    if manager_id and lecturer1_id and lecturer2_id:
        scripted_messages.extend([
            (manager_id, lecturer1_id, "Could you send me the midterm report for CS101, please?"),
            (lecturer1_id, manager_id, "Sure, I will send it to you by the end of this week."),
            (manager_id, lecturer2_id, "How is the attendance in IT201 this semester?"),
            (lecturer2_id, manager_id, "Overall it's quite good. Most students attend regularly."),
        ])

    msg_id = 1
    now = datetime.now()

    # Insert scripted messages first
    for sender_id, receiver_id, content in scripted_messages:
        if sender_id is None or receiver_id is None:
            continue

        created_at = now - timedelta(hours=random.randint(10, 200))
        message = Message(
            message_id=msg_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            is_read=random.choice([True, True, False]),
            created_at=created_at,
        )
        session.add(message)
        msg_id += 1

    # ============ 2. Fill up to 100 messages with semi-random ones ============
    def random_pair_student_lecturer():
        if not student_user_ids or not lecturer_user_ids:
            return None, None
        s = random.choice(student_user_ids)
        l = random.choice(lecturer_user_ids)
        return s, l

    def random_pair_lecturer_manager():
        if not lecturer_user_ids:
            return None, None
        l = random.choice(lecturer_user_ids)
        return l, manager_id

    while msg_id <= 100:
        conv_type = random.choice([
            "student_to_lecturer",
            "lecturer_to_student",
            "lecturer_to_manager",
            "random_any",
        ])

        sender_id = None
        receiver_id = None

        if conv_type == "student_to_lecturer":
            s, l = random_pair_student_lecturer()
            sender_id, receiver_id = s, l
        elif conv_type == "lecturer_to_student":
            s, l = random_pair_student_lecturer()
            sender_id, receiver_id = l, s
        elif conv_type == "lecturer_to_manager":
            l, m = random_pair_lecturer_manager()
            sender_id, receiver_id = l, m
        else:
            # fallback completely random
            sender_id = random.choice(all_user_ids)
            possible_receivers = [uid for uid in all_user_ids if uid != sender_id]
            receiver_id = random.choice(possible_receivers) if possible_receivers else None

        if sender_id is None or receiver_id is None or sender_id == receiver_id:
            continue

        content = random.choice(generic_templates)
        created_at = now - timedelta(hours=random.randint(1, 500))

        message = Message(
            message_id=msg_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content,
            is_read=random.choice([True, True, False]),
            created_at=created_at,
        )
        session.add(message)
        msg_id += 1

    session.commit()
    print(f"Created {msg_id - 1} messages")


def generate_feedback(session, enrollments, fixed_ids=None, max_feedback=50):
    print("Generating feedback...")

    # Generic templates cho sinh viên còn lại
    generic_templates = [
        "Excellent course! The professor explains concepts very clearly.",
        "Good course content but could use more practical examples.",
        "The assignments were challenging but helped me learn a lot.",
        "Would appreciate more interactive sessions.",
        "Great learning experience, highly recommend this course.",
        "The pace was a bit fast, but overall good content.",
        "Very informative lectures with good supporting materials.",
        "Could benefit from more group projects.",
    ]

    # Templates riêng cho student1 (rất tích cực)
    s1_templates = [
        "This course was extremely helpful and well-organized.",
        "The instructor explained every concept clearly and in depth.",
        "Assignments and projects were very meaningful and aligned with the lectures.",
        "I learned a lot from this course. Highly recommended!",
    ]

    # Templates riêng cho student2 (mixed, có khen có góp ý)
    s2_templates = [
        "The content was useful, but some topics felt a bit rushed.",
        "Overall a good course, though a bit heavy near the end.",
        "The instructor was very supportive, but the workload was quite high.",
        "Good course, but I would appreciate clearer instructions for some assignments.",
    ]

    # Unique (student_id, course_id)
    unique_enrollments = list(set(enrollments))
    random.shuffle(unique_enrollments)

    # Map student -> list course
    from collections import defaultdict
    courses_by_student: dict[int, list[int]] = defaultdict(list)
    for s_id, c_id in unique_enrollments:
        courses_by_student[s_id].append(c_id)

    feedback_id = 1
    used_pairs: set[tuple[int, int]] = set()

    # ===== 1) Nếu có fixed_ids -> ưu tiên tạo feedback cho student1 & student2 =====
    if fixed_ids is not None:
        student1_id = fixed_ids.get("student1")
        student2_id = fixed_ids.get("student2")

        # --- Feedback cho student1 ---
        if student1_id in courses_by_student:
            random.shuffle(courses_by_student[student1_id])
            for course_id in courses_by_student[student1_id][:5]:
                if feedback_id > max_feedback:
                    break
                pair = (student1_id, course_id)
                if pair in used_pairs:
                    continue

                feedback = Feedback(
                    feedback_id=feedback_id,
                    content=random.choice(s1_templates),
                    rating=random.randint(4, 5),
                    student_id=student1_id,
                    course_id=course_id,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                )
                session.add(feedback)
                used_pairs.add(pair)
                feedback_id += 1

        # --- Feedback cho student2 ---
        if student2_id in courses_by_student and feedback_id <= max_feedback:
            random.shuffle(courses_by_student[student2_id])
            for course_id in courses_by_student[student2_id][:5]:
                if feedback_id > max_feedback:
                    break
                pair = (student2_id, course_id)
                if pair in used_pairs:
                    continue

                feedback = Feedback(
                    feedback_id=feedback_id,
                    content=random.choice(s2_templates),
                    rating=random.randint(3, 5),
                    student_id=student2_id,
                    course_id=course_id,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                )
                session.add(feedback)
                used_pairs.add(pair)
                feedback_id += 1

    # ===== 2) Phần còn lại: random cho các enrollment khác =====
    for (student_id, course_id) in unique_enrollments:
        if feedback_id > max_feedback:
            break
        pair = (student_id, course_id)
        if pair in used_pairs:
            continue

        feedback = Feedback(
            feedback_id=feedback_id,
            content=random.choice(generic_templates),
            rating=random.randint(3, 5),
            student_id=student_id,
            course_id=course_id,
            created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
        )
        session.add(feedback)
        used_pairs.add(pair)
        feedback_id += 1

    session.commit()
    print(f"Created {feedback_id - 1} feedback entries")


def generate_course_ratings(session, enrollments, fixed_ids=None, max_ratings=20):
    print("Generating course ratings...")

    generic_comments = [
        "Loved this course!",
        "Very helpful for my career.",
        "Great instructor.",
        "Well-structured curriculum.",
        "Challenging but rewarding.",
    ]

    s1_comments = [
        "One of the best courses I have taken.",
        "Highly relevant and very well organized.",
        "The teaching style and course structure were excellent.",
    ]

    s2_comments = [
        "Good course overall, but a bit intense at times.",
        "Useful content, though some parts were hard to follow.",
        "The course was helpful, but the pace could be improved.",
    ]

    unique_enrollments = list(set(enrollments))
    random.shuffle(unique_enrollments)

    from collections import defaultdict
    courses_by_student: dict[int, list[int]] = defaultdict(list)
    for s_id, c_id in unique_enrollments:
        courses_by_student[s_id].append(c_id)

    rating_id = 1
    used_pairs: set[tuple[int, int]] = set()

    # ===== 1) Ratings cho student1 & student2 nếu có fixed_ids =====
    if fixed_ids is not None:
        student1_id = fixed_ids.get("student1")
        student2_id = fixed_ids.get("student2")

        # student1: rating khá cao
        if student1_id in courses_by_student:
            random.shuffle(courses_by_student[student1_id])
            for course_id in courses_by_student[student1_id][:5]:
                if rating_id > max_ratings:
                    break
                pair = (student1_id, course_id)
                if pair in used_pairs:
                    continue

                rating = CourseRating(
                    rating_id=rating_id,
                    student_id=student1_id,
                    course_id=course_id,
                    rating=random.randint(4, 5),
                    comment=random.choice(s1_comments),
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                )
                session.add(rating)
                used_pairs.add(pair)
                rating_id += 1

        # student2: rating hỗn hợp
        if student2_id in courses_by_student and rating_id <= max_ratings:
            random.shuffle(courses_by_student[student2_id])
            for course_id in courses_by_student[student2_id][:5]:
                if rating_id > max_ratings:
                    break
                pair = (student2_id, course_id)
                if pair in used_pairs:
                    continue

                rating = CourseRating(
                    rating_id=rating_id,
                    student_id=student2_id,
                    course_id=course_id,
                    rating=random.randint(3, 5),
                    comment=random.choice(s2_comments) if random.random() > 0.2 else None,
                    created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
                )
                session.add(rating)
                used_pairs.add(pair)
                rating_id += 1

    # ===== 2) Ratings random cho các enrollment khác =====
    for (student_id, course_id) in unique_enrollments:
        if rating_id > max_ratings:
            break
        pair = (student_id, course_id)
        if pair in used_pairs:
            continue

        rating = CourseRating(
            rating_id=rating_id,
            student_id=student_id,
            course_id=course_id,
            rating=random.randint(3, 5),
            comment=random.choice(generic_comments) if random.random() > 0.3 else None,
            created_at=datetime.now() - timedelta(days=random.randint(1, 60)),
        )
        session.add(rating)
        used_pairs.add(pair)
        rating_id += 1

    session.commit()
    print(f"Created {rating_id - 1} course ratings")


def generate_materials(session, course_ids):
    """Generate course materials, more realistic by type and course."""
    print("Generating course materials...")

    material_types = ["lecture", "document", "video", "quiz"]
    material_id = 1

    # Lấy thông tin course để dùng tên và semester
    courses = (
        session.query(Course)
        .filter(Course.course_id.in_(course_ids))
        .all()
    )
    course_by_id = {c.course_id: c for c in courses}

    for course_id in course_ids:
        course = course_by_id.get(course_id)
        course_name = course.Course_name if hasattr(course, "Course_name") else getattr(course, "course_name", f"Course {course_id}")
        semester_str = course.semester if hasattr(course, "semester") else "2024-1"

        # Số materials cho mỗi course: 3–6 thay vì 2–4
        num_materials = random.randint(3, 6)

        for i in range(num_materials):
            mat_type = random.choice(material_types)

            # Đổi title theo loại tài liệu
            if mat_type == "lecture":
                title = f"{course_name} - Lecture {i+1}"
            elif mat_type == "document":
                title = f"{course_name} - Reference Document {i+1}"
            elif mat_type == "video":
                title = f"{course_name} - Video Lesson {i+1}"
            else:  # quiz
                title = f"{course_name} - Quiz Resources {i+1}"

            description = f"{mat_type.capitalize()} material for the course {course_name}."

            # Chọn đuôi file phù hợp
            if mat_type == "video":
                ext = "mp4"
            else:
                ext = "pdf"

            file_path = f"/uploads/materials/{course_id}_{material_id}.{ext}"

            # Upload date dựa trên semester (nếu bạn đã dùng format YYYY-1/2/3)
            try:
                year_str, term_str = semester_str.split("-")
                academic_year = int(year_str)
                term = int(term_str)
            except Exception:
                academic_year = 2024
                term = 1

            if term == 1:
                year_full = academic_year
                month = 9
            elif term == 2:
                year_full = academic_year + 1
                month = 1
            else:
                year_full = academic_year + 1
                month = 6

            # random trong 0–30 ngày đầu học kỳ
            day = random.randint(1, 28)
            upload_date = datetime(
                year_full,
                month,
                day,
                random.randint(8, 20),
                random.randint(0, 59),
            )

            material = Materials(
                materials_id=material_id,   # hoặc Materials_id nếu model viết hoa
                course_id=course_id,
                type=mat_type,
                title=title,
                description=description,
                file_path=file_path,
                upload_date=upload_date,
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

        generate_student_gpa_history(session, student_user_ids, last_year=2025, last_term=1)
        fixed_ids = {
            "student1": student_user_ids[0],
            "student2": student_user_ids[1],
            "lecturer1": lecturer_user_ids[0],
            "lecturer2": lecturer_user_ids[1],
            "manager": manager_user_id,
        }
        course_ids = generate_courses(session, lecturer_user_ids)
        enrollments = generate_enrollments(session, student_user_ids, course_ids, fixed_ids=fixed_ids)
        assignment_data = generate_assignments(session, course_ids)
        generate_submissions(session, assignment_data, enrollments, fixed_ids=fixed_ids)
        quiz_ids = generate_quizzes_and_questions(session, course_ids)
        generate_quiz_attempts(session, quiz_ids, student_user_ids, enrollments, fixed_ids=fixed_ids)
        generate_messages(session, student_user_ids, lecturer_user_ids, manager_user_id)
        generate_feedback(session, enrollments, fixed_ids=fixed_ids)
        generate_course_ratings(session, enrollments, fixed_ids=fixed_ids)
        generate_materials(session, course_ids)
        
        print("\n" + "=" * 50)
        print("Sample data generation completed successfully!")
        print("=" * 50)
        print("\nLogin credentials:")
        print("  Students: student1 to student1000")
        print("  Lecturers: lecturer1 to lecturer50")
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
