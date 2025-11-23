import psycopg2
from faker import Faker
import csv
import random
from datetime import datetime
import Fake_info  # module của bạn để clean tên cho email

# =========================
# Cấu hình database
# =========================
DB_NAME = "LMS"
DB_USER = "postgres"
DB_PASS = "hung"
DB_HOST = "localhost"
DB_PORT = "5432"

fake = Faker("vi_VN")


# =========================
# Helper: tạo MSSV giả
# =========================
def create_student_id():
    enroll_year = fake.random_element(elements=(2020, 2021, 2022, 2023, 2024, 2025))
    id_prefix = f"{enroll_year % 100}5"  # vd: 205xxx
    id_suffix = fake.numerify(text="####")
    student_id = f"{id_prefix}{id_suffix}"
    return student_id


# =========================
# 1. Seed User + Student/Lecturer/Manager
# =========================
def send_database():
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()

        print("Start inserting User / Student / Lecturer / Manager ...")

        for i in range(50):  # tạo khoảng ~50 user, tỉ lệ student cao hơn
            # Tăng tỉ lệ Student
            role = random.choices(
                ["Student", "Lecturer", "Manager"],
                weights=[0.75, 0.2, 0.05]
            )[0]

            gender = fake.random_element(elements=("male", "female"))
            last_name = fake.last_name()
            middle_name = fake.middle_name()
            if gender == "male":
                first_name = fake.first_name_male()
            else:
                first_name = fake.first_name_female()

            clean_first = Fake_info.clean_name_for_email(first_name)
            clean_last = Fake_info.clean_name_for_email(last_name)
            base_username = f"{clean_first}.{clean_last}"

            if role == "Student":
                mssv_suffix = create_student_id()
                username = f"{base_username}{mssv_suffix}"
            else:
                # dùng i để giảm khả năng trùng
                username = f"{base_username}{i}"

            email = f"{username}@hcmut.edu.vn"
            password_hash = "password123"

            sql_insert_user = """
                INSERT INTO "User" ("Role", Username, Email, "Password_Hash")
                VALUES (%s, %s, %s, %s)
                RETURNING User_id;
            """
            cur.execute(sql_insert_user, (role, username, email, password_hash))
            user_id = cur.fetchone()[0]

            # ---------- Student ----------
            if role == "Student":
                student_id_str = create_student_id()
                student_id_int = int(student_id_str)

                major = fake.random_element(
                    elements=(
                        "Computer Science",
                        "Computer Engineering",
                        "Electrical Engineering",
                        "Industrial Management",
                    )
                )

                enroll_year = int("20" + student_id_str[:2])
                birth_year = enroll_year - 18

                start_of_year = datetime(birth_year, 1, 1)
                end_of_year = datetime(birth_year, 12, 31)
                dob = fake.date_between_dates(
                    date_start=start_of_year, date_end=end_of_year
                )

                current_gpa = round(fake.pyfloat(min_value=0.0, max_value=4.0), 1)
                target_gpa = round(min(current_gpa + 0.5, 4.0), 1)

                sql_insert_student = """
                    INSERT INTO "Student"
                        (User_id, Student_id, LName, MName, FName, Major, DOB, Current_GPA, Target_GPA)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);
                """
                cur.execute(
                    sql_insert_student,
                    (
                        user_id,
                        student_id_int,
                        last_name,
                        middle_name,
                        first_name,
                        major,
                        dob,
                        current_gpa,
                        target_gpa,
                    ),
                )

            # ---------- Lecturer ----------
            elif role == "Lecturer":
                title = fake.random_element(elements=("ThS.", "TS.", "PGS.TS."))
                department = fake.random_element(
                    elements=(
                        "Computer Science and Engineering",
                        "Electrical Engineering",
                        "Industrial Management",
                    )
                )

                sql_insert_lecturer = """
                    INSERT INTO "Lecturer" (User_id, Title, LName, MName, FName, Department)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """
                cur.execute(
                    sql_insert_lecturer,
                    (user_id, title, last_name, middle_name, first_name, department),
                )

            # ---------- Manager ----------
            elif role == "Manager":
                full_name = f"{last_name} {middle_name} {first_name}"
                office = fake.random_element(
                    elements=(
                        "Training Department",
                        "Student Affairs Department",
                        "Faculty Office",
                    )
                )
                position = fake.random_element(elements=("Specialist", "Head of Department"))
                sql_insert_manager = """
                    INSERT INTO "Manager" (User_id, "Name", Office, "Position")
                    VALUES (%s, %s, %s, %s);
                """
                cur.execute(
                    sql_insert_manager, (user_id, full_name, office, position)
                )

        conn.commit()
        print("Done inserting User / Student / Lecturer / Manager")

    except Exception as error:
        print("Error in send_database:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_database)")


# =========================
# 2. Seed Course từ CSV mon_all.csv
# =========================
def send_course_database(csv_path="mon_all.csv"):
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        print("Start inserting courses from CSV into database...")

        with open(csv_path, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)

            sql_insert_course = """
                INSERT INTO "Course" (Course_code, Course_name, Credits, Capacity, Semester)
                VALUES (%s, %s, %s, %s, %s);
            """

            count = 0
            for row in reader:
                course_code = row["Mã MH"].strip()
                course_name = row["Tên MH"].strip()
                credits_str = row["Tín chỉ"].strip().replace(",", ".")
                credits = int(float(credits_str))  # chuyển về int

                capacity = fake.random_element(elements=(50, 60, 70, 80))
                semester = fake.random_element(
                    elements=("HK231", "HK232", "HK241", "HK242", "HK251", "HK252")
                )

                cur.execute(
                    sql_insert_course,
                    (course_code, course_name, credits, capacity, semester),
                )
                count += 1

        conn.commit()
        print(f"Inserted {count} courses from CSV")

    except Exception as error:
        print("Error while inserting courses:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_course_database)")


# =========================
# 3. Seed Enroll (đăng ký môn) có kiểm tra Capacity
# =========================
def send_enroll_data():
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        print("Start inserting enroll data with capacity check...")

        # Lấy students
        cur.execute('SELECT User_id FROM "Student";')
        student_ids = [row[0] for row in cur.fetchall()]
        if not student_ids:
            print("No students found.")
            return

        # Lấy courses + capacity
        cur.execute('SELECT Course_id, Capacity FROM "Course";')
        course_rows = cur.fetchall()
        if not course_rows:
            print("No courses found.")
            return

        course_capacity = {row[0]: row[1] for row in course_rows}

        # Số đã enroll hiện tại
        cur.execute('SELECT Course_id, COUNT(*) FROM "Enroll" GROUP BY Course_id;')
        current_enroll_rows = cur.fetchall()
        current_enroll = {row[0]: row[1] for row in current_enroll_rows}

        # remaining_slots = capacity - current_enrolled
        remaining_slots = {}
        for cid, cap in course_capacity.items():
            used = current_enroll.get(cid, 0)
            remain = max(cap - used, 0)
            if remain > 0:
                remaining_slots[cid] = remain

        if not remaining_slots:
            print("All courses are full. Cannot enroll anyone.")
            return

        sql_insert_enroll = """
            INSERT INTO "Enroll" (Course_id, Student_id)
            VALUES (%s, %s)
            ON CONFLICT DO NOTHING;
        """

        total_inserted = 0

        for student_id in student_ids:
            available_courses = [cid for cid, r in remaining_slots.items() if r > 0]
            if not available_courses:
                print("All courses filled, stop assigning more enrollments.")
                break

            desired_courses = random.randint(3, 7)
            desired_courses = min(desired_courses, len(available_courses))
            if desired_courses <= 0:
                continue

            selected_courses = random.sample(available_courses, k=desired_courses)

            for cid in selected_courses:
                if remaining_slots.get(cid, 0) <= 0:
                    continue

                cur.execute(sql_insert_enroll, (cid, student_id))
                remaining_slots[cid] -= 1
                total_inserted += 1

        conn.commit()
        print(f"Inserted {total_inserted} enrollments (respecting capacity).")

    except Exception as error:
        print("Error inserting enroll data:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection closed (send_enroll_data)")


# =========================
# 4. Seed Attendance_Record (Rec001, Rec002, ...)
# =========================
def send_attendance_data(num_records=50):
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()

        print("Start inserting attendance records...")

        sql_insert_att = """
            INSERT INTO "Attendance_Record" ("Date", "Status")
            VALUES (%s, %s);
        """

        for _ in range(num_records):
            date = fake.date_between(start_date="-90d", end_date="today")
            status = fake.random_element(elements=("Present", "Absent", "Late"))
            cur.execute(sql_insert_att, (date, status))

        conn.commit()
        print(f"Inserted {num_records} attendance records.")

    except Exception as error:
        print("Error in send_attendance_data:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_attendance_data)")


# =========================
# 5. Seed Attendance_Detail
# =========================
def send_attendance_detail_data():
    conn = None
    cur = None
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        print("Start inserting attendance detail...")

        # Record_id (Rec001, Rec002, ...)
        cur.execute('SELECT Record_id FROM "Attendance_Record";')
        record_ids = [row[0] for row in cur.fetchall()]
        if not record_ids:
            print("No attendance records found — cannot insert.")
            return

        # Students
        cur.execute('SELECT User_id FROM "Student";')
        student_ids = [row[0] for row in cur.fetchall()]
        if not student_ids:
            print("No students found — cannot insert.")
            return

        # Courses
        cur.execute('SELECT Course_id FROM "Course";')
        course_ids = [row[0] for row in cur.fetchall()]
        if not course_ids:
            print("No courses found — cannot insert.")
            return

        sql_insert_detail = """
            INSERT INTO "Attendance_Detail" (Course_id, Record_id, Student_id)
            VALUES (%s, %s, %s)
            ON CONFLICT DO NOTHING;
        """

        inserted_count = 0

        for record_id in record_ids:
            course_id = random.choice(course_ids)

            upper_bound = min(40, len(student_ids))
            num_students = random.randint(5, upper_bound)
            sampled_students = random.sample(student_ids, k=num_students)

            for sid in sampled_students:
                cur.execute(sql_insert_detail, (course_id, record_id, sid))
                inserted_count += 1

        conn.commit()
        print(f"Inserted {inserted_count} attendance detail rows.")

    except Exception as error:
        print("Error in send_attendance_detail_data:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_attendance_detail_data)")


# =========================
# 6. Seed Materials
# =========================
def send_materials_data():
    conn = None
    cur = None

    material_types = [
        "Lecture Slides",
        "PDF Notes",
        "Assignment Guide",
        "Reference Document",
        "Tutorial",
        "Exercise Sheet",
    ]

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()

        print("Start inserting materials...")

        cur.execute('SELECT Course_id, Course_code FROM "Course";')
        courses = cur.fetchall()
        if not courses:
            print("No courses found — cannot insert materials.")
            return

        sql_insert_material = """
            INSERT INTO "Materials" (Course_id, "Type", Title, File_path, Upload_date)
            VALUES (%s, %s, %s, %s, %s);
        """

        count = 0

        for course_id, course_code in courses:
            num_materials = random.randint(2, 6)

            for i in range(num_materials):
                mat_type = random.choice(material_types)
                title = f"{course_code} - {mat_type} #{i+1}"
                file_path = f"/materials/{course_code}/{title.replace(' ', '_')}.pdf"
                upload_date = fake.date_between(start_date="-120d", end_date="today")

                cur.execute(
                    sql_insert_material,
                    (course_id, mat_type, title, file_path, upload_date),
                )
                count += 1

        conn.commit()
        print(f"Inserted {count} materials.")

    except Exception as error:
        print("Error in send_materials_data:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_materials_data)")


# =========================
# 7. Seed Feedback
# =========================
def send_feedback_data():
    conn = None
    cur = None

    feedback_templates = [
        "Môn học này rất hữu ích và giúp tôi hiểu rõ hơn về {topic}.",
        "Giảng viên giảng dễ hiểu, nội dung được trình bày logic.",
        "Tài liệu môn học chi tiết và dễ theo dõi.",
        "Bài tập khá thử thách nhưng giúp tôi rèn luyện kỹ năng {skill}.",
        "Tiến độ môn học hợp lý và phù hợp với sinh viên.",
        "Tôi mong muốn có thêm ví dụ thực tế trong bài giảng.",
        "Phần {topic} hơi khó, nhưng giảng viên hỗ trợ rất nhiệt tình.",
        "Hoạt động nhóm giúp tôi học được nhiều điều mới.",
    ]

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()
        print("Start inserting feedback...")

        # students
        cur.execute('SELECT User_id FROM "Student";')
        student_ids = [row[0] for row in cur.fetchall()]
        if not student_ids:
            print("No students found.")
            return

        # courses
        cur.execute('SELECT Course_id FROM "Course";')
        course_ids = [row[0] for row in cur.fetchall()]
        if not course_ids:
            print("No courses found.")
            return

        sql_insert_feedback = """
            INSERT INTO "Feedback" ("Content", Rating, Student_id, Course_id)
            VALUES (%s, %s, %s, %s);
        """

        count = 0

        for _ in range(120):
            sid = random.choice(student_ids)
            cid = random.choice(course_ids)

            content = random.choice(feedback_templates).format(
                topic=fake.word(), skill=fake.word()
            )
            rating = fake.random_int(min=1, max=5)

            cur.execute(sql_insert_feedback, (content, rating, sid, cid))
            count += 1

        conn.commit()
        print(f"Inserted {count} feedback rows.")

    except Exception as error:
        print("Error in send_feedback_data:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_feedback_data)")


# =========================
# 8. Seed Prediction
# =========================
def generate_recommendations(current_gpa, predicted_gpa):
    rec = []

    if predicted_gpa < current_gpa:
        rec.append("Xem lại thời gian học và giảm tải lịch ngoài giờ.")
        rec.append("Tập trung vào các môn nền tảng để cải thiện điểm số.")
    else:
        rec.append("Tiếp tục duy trì tiến độ học hiện tại.")
        rec.append("Nên tham gia study group để tối ưu hiệu quả học.")

    if predicted_gpa < 2.0:
        rec.append("Cần trao đổi với cố vấn học tập để nhận hỗ trợ thêm.")
    elif predicted_gpa < 3.0:
        rec.append("Ưu tiên học đều, hạn chế bỏ tiết, và ôn tập hàng tuần.")
    else:
        rec.append("Khả năng hoàn thành tốt mục tiêu GPA.")

    return " ".join(rec)


def send_prediction_data():
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()

        print("Start inserting prediction data...")

        cur.execute(
            'SELECT User_id, Target_GPA, Current_GPA FROM "Student";'
        )
        students = cur.fetchall()
        if not students:
            print("No students found.")
            return

        sql_insert_prediction = """
            INSERT INTO "Prediction"
            (User_id, Predicted_GPA, Confidence_level, Model_version, Recommendations, Target_GPA)
            VALUES (%s, %s, %s, %s, %s, %s);
        """

        model_versions = ["v1.0", "v1.1", "v2.0", "exp-2025"]

        count = 0

        for user_id, target_gpa, current_gpa in students:
            # Decimal -> float
            current_gpa_f = float(current_gpa)
            target_gpa_f = float(target_gpa) if target_gpa is not None else None

            noise = random.uniform(-0.2, 0.4)
            base = current_gpa_f + noise
            predicted_gpa = round(min(max(base, 0.0), 4.0), 1)

            confidence = round(random.uniform(0.65, 0.98), 2)
            model_version = random.choice(model_versions)
            recommendations = generate_recommendations(current_gpa_f, predicted_gpa)

            cur.execute(
                sql_insert_prediction,
                (
                    user_id,
                    predicted_gpa,
                    confidence,
                    model_version,
                    recommendations,
                    target_gpa_f,
                ),
            )
            count += 1

        conn.commit()
        print(f"Inserted {count} prediction rows.")

    except Exception as error:
        print("Error in send_prediction_data:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_prediction_data)")


# =========================
# 9. Seed Assignment (độc lập, chưa gắn Course)
# =========================
def send_assignment_data():
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME, user=DB_USER,
            password=DB_PASS, host=DB_HOST, port=DB_PORT
        )
        cur = conn.cursor()

        print("Start inserting assignments...")

        sql_insert_assignment = """
            INSERT INTO "Assignment" ("Description", Deadlines)
            VALUES (%s, %s);
        """

        count = 0

        for i in range(50):
            description = f"Bài tập số {i+1} cho các môn trong học kỳ"
            deadline = fake.date_between(start_date="today", end_date="+60d")
            cur.execute(sql_insert_assignment, (description, deadline))
            count += 1

        conn.commit()
        print(f"Inserted {count} assignments.")

    except Exception as error:
        print("Error in send_assignment_data:", error)
        if conn:
            conn.rollback()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_assignment_data)")

def send_submission_data():
    conn = None
    cur = None

    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASS,
            host=DB_HOST,
            port=DB_PORT
        )
        cur = conn.cursor()
        print("Start inserting submission data...")

        # --- Lấy danh sách assignment ---
        cur.execute('SELECT Assignment_id FROM "Assignment";')
        assignment_ids = [row[0] for row in cur.fetchall()]
        if not assignment_ids:
            print("No assignments found — cannot insert submissions.")
            return

        # --- Lấy danh sách student ---
        cur.execute('SELECT User_id FROM "Student";')
        student_ids = [row[0] for row in cur.fetchall()]
        if not student_ids:
            print("No students found — cannot insert submissions.")
            return

        sql_insert_submission = """
            INSERT INTO "Submission" (Assignment_id, Student_id, Score, File_path)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (Assignment_id, Student_id) DO NOTHING;
        """

        total_inserted = 0

        for assignment_id in assignment_ids:
            # Số sinh viên nộp bài cho assignment này
            max_sub = min(30, len(student_ids))
            if max_sub == 0:
                continue

            num_submissions = random.randint(10, max_sub)

            chosen_students = random.sample(student_ids, k=num_submissions)

            for sid in chosen_students:
                # 1 phần nhỏ không có điểm (chưa chấm)
                if random.random() < 0.15:
                    score = None
                else:
                    score = round(random.uniform(4.0, 10.0), 2)

                # File path unique theo assignment + student
                file_path = f"/submissions/assign_{assignment_id}/stud_{sid}.pdf"

                cur.execute(sql_insert_submission, (assignment_id, sid, score, file_path))
                total_inserted += 1

        conn.commit()
        print(f"Inserted {total_inserted} submissions.")

    except Exception as error:
        print("Error in send_submission_data:", error)
        if conn:
            conn.rollback()

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
        print("PostgreSQL connection is closed (send_submission_data)")



# =========================
# Main
# =========================
if __name__ == "__main__":
    # Bạn có thể comment/bỏ comment từng hàm tùy thứ tự muốn chạy
    send_database()
    send_course_database()
    send_enroll_data()
    send_attendance_data()
    send_attendance_detail_data()
    send_materials_data()
    send_feedback_data()
    send_prediction_data()
    send_assignment_data()
    send_submission_data()