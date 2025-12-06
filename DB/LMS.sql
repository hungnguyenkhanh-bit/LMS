-- =====================================================
-- LMS Database Schema (lowercase columns for PostgreSQL)
-- =====================================================

-- Drop existing tables if they exist
DROP TABLE IF EXISTS
    activity_log,
    assignment,
    attendance_detail,
    attendance_record,
    course,
    course_rating,
    enroll,
    feedback,
    grade,
    lecturer,
    manager,
    materials,
    message,
    prediction,
    quiz,
    quiz_attempt,
    quiz_attempt_detail,
    quiz_question,
    student,
    submission,
    "user"
CASCADE;

-- =====================================================
-- Core Tables
-- =====================================================

CREATE TABLE "user" (
    user_id       SERIAL PRIMARY KEY,
    username      VARCHAR(100) UNIQUE,
    password_hash TEXT NOT NULL,
    role          VARCHAR(20) NOT NULL,
    email         VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE student (
    user_id     INT PRIMARY KEY REFERENCES "user"(user_id) ON DELETE CASCADE,
    student_id  INT UNIQUE NOT NULL,
    lname       VARCHAR(50) NOT NULL,
    mname       VARCHAR(50),
    fname       VARCHAR(50) NOT NULL,
    major       VARCHAR(100) NOT NULL,
    dob         DATE,
    current_gpa DECIMAL(3,2) NOT NULL DEFAULT 0.00,
    target_gpa  DECIMAL(3,2)
);

CREATE TABLE lecturer (
    user_id    INT PRIMARY KEY REFERENCES "user"(user_id) ON DELETE CASCADE,
    title      VARCHAR(100),
    lname      VARCHAR(50) NOT NULL,
    mname      VARCHAR(50),
    fname      VARCHAR(50) NOT NULL,
    department VARCHAR(100) NOT NULL
);

CREATE TABLE manager (
    user_id   INT PRIMARY KEY REFERENCES "user"(user_id) ON DELETE CASCADE,
    name      VARCHAR(200) NOT NULL,
    office    VARCHAR(100) NOT NULL,
    position  VARCHAR(100)
);

-- =====================================================
-- Course Related Tables
-- =====================================================

CREATE TABLE course (
    course_id    SERIAL PRIMARY KEY,
    course_code  VARCHAR(100) UNIQUE NOT NULL,
    course_name  VARCHAR(200) NOT NULL,
    credits      INT NOT NULL,
    capacity     INT NOT NULL DEFAULT 50,
    semester     VARCHAR(20) NOT NULL,
    lecturer_id  INT REFERENCES lecturer(user_id) ON DELETE SET NULL,
    description  TEXT,
    image_url VARCHAR(500)
);

CREATE TABLE enroll (
    enroll_id   SERIAL PRIMARY KEY,
    course_id   INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    student_id  INT NOT NULL REFERENCES student(user_id) ON DELETE CASCADE,
    semester    VARCHAR(20),
    status      VARCHAR(20) NOT NULL DEFAULT 'active',
    enrolled_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(course_id, student_id)
);

CREATE TABLE materials (
    materials_id SERIAL PRIMARY KEY,
    course_id    INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    type         VARCHAR(50) NOT NULL,
    description  TEXT,
    title        VARCHAR(200) NOT NULL,
    file_path    VARCHAR(500),
    upload_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE assignment (
    assignment_id SERIAL PRIMARY KEY,
    course_id     INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    title         VARCHAR(200) NOT NULL,
    description   TEXT,
    deadline      TIMESTAMP NOT NULL,
    max_score     DECIMAL(5,2) DEFAULT 100.00,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE submission (
    submission_id SERIAL PRIMARY KEY,
    assignment_id INT NOT NULL REFERENCES assignment(assignment_id) ON DELETE CASCADE,
    student_id    INT NOT NULL REFERENCES student(user_id) ON DELETE CASCADE,
    score         DECIMAL(5,2),
    file_path     VARCHAR(500),
    submitted_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    graded_at     TIMESTAMP,
    comments      TEXT,
    UNIQUE(assignment_id, student_id)
);

-- =====================================================
-- Quiz Tables
-- =====================================================

CREATE TABLE quiz (
    quiz_id          SERIAL PRIMARY KEY,
    course_id        INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    title            VARCHAR(200) NOT NULL,
    description      TEXT,
    duration_minutes INT DEFAULT 30,
    max_attempts     INT DEFAULT 1,
    start_time       TIMESTAMP,
    end_time         TIMESTAMP,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE quiz_question (
    question_id    SERIAL PRIMARY KEY,
    quiz_id        INT NOT NULL REFERENCES quiz(quiz_id) ON DELETE CASCADE,
    question_text  TEXT NOT NULL,
    option_a       VARCHAR(500) NOT NULL,
    option_b       VARCHAR(500) NOT NULL,
    option_c       VARCHAR(500),
    option_d       VARCHAR(500),
    correct_option VARCHAR(1) NOT NULL,
    points         DECIMAL(5,2) DEFAULT 1.00
);

CREATE TABLE quiz_attempt (
    attempt_id  SERIAL PRIMARY KEY,
    quiz_id     INT NOT NULL REFERENCES quiz(quiz_id) ON DELETE CASCADE,
    student_id  INT NOT NULL REFERENCES student(user_id) ON DELETE CASCADE,
    started_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    total_score DECIMAL(5,2),
    status      VARCHAR(20) DEFAULT 'in_progress'
);

CREATE TABLE quiz_attempt_detail (
    detail_id     SERIAL PRIMARY KEY,
    attempt_id    INT NOT NULL REFERENCES quiz_attempt(attempt_id) ON DELETE CASCADE,
    question_id   INT NOT NULL REFERENCES quiz_question(question_id) ON DELETE CASCADE,
    chosen_option VARCHAR(1),
    is_correct    BOOLEAN,
    UNIQUE(attempt_id, question_id)
);

-- =====================================================
-- Grade & Feedback Tables
-- =====================================================

CREATE TABLE grade (
    grade_id      SERIAL PRIMARY KEY,
    student_id    INT NOT NULL REFERENCES student(user_id) ON DELETE CASCADE,
    course_id     INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    assignment_id INT REFERENCES assignment(assignment_id) ON DELETE SET NULL,
    quiz_id       INT REFERENCES quiz(quiz_id) ON DELETE SET NULL,
    score         DECIMAL(5,2) NOT NULL,
    max_score     DECIMAL(5,2) DEFAULT 100.00,
    grade_type    VARCHAR(20) NOT NULL,
    graded_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE feedback (
    feedback_id SERIAL PRIMARY KEY,
    content     TEXT,
    rating      INT NOT NULL DEFAULT 3,
    student_id  INT NOT NULL REFERENCES student(user_id) ON DELETE CASCADE,
    course_id   INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE course_rating (
    rating_id  SERIAL PRIMARY KEY,
    course_id  INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES student(user_id) ON DELETE CASCADE,
    rating     INT NOT NULL,
    comment    TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(course_id, student_id)
);

-- =====================================================
-- Communication Tables
-- =====================================================

CREATE TABLE message (
    message_id  SERIAL PRIMARY KEY,
    sender_id   INT NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    receiver_id INT NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    content     TEXT NOT NULL,
    is_read     BOOLEAN DEFAULT FALSE,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Attendance Tables
-- =====================================================

CREATE TABLE attendance_record (
    record_id  SERIAL PRIMARY KEY,
    course_id  INT NOT NULL REFERENCES course(course_id) ON DELETE CASCADE,
    date       DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE attendance_detail (
    detail_id  SERIAL PRIMARY KEY,
    record_id  INT NOT NULL REFERENCES attendance_record(record_id) ON DELETE CASCADE,
    student_id INT NOT NULL REFERENCES student(user_id) ON DELETE CASCADE,
    status     VARCHAR(20) NOT NULL DEFAULT 'present',
    UNIQUE(record_id, student_id)
);

-- =====================================================
-- Analytics Tables
-- =====================================================

CREATE TABLE prediction (
    prediction_id    SERIAL PRIMARY KEY,
    user_id          INT NOT NULL REFERENCES student(user_id) ON DELETE CASCADE,
    predicted_gpa    DECIMAL(3,2) NOT NULL,
    confidence_level DECIMAL(5,2) NOT NULL,
    model_version    VARCHAR(20) NOT NULL,
    recommendations  TEXT,
    target_gpa       DECIMAL(3,2),
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE activity_log (
    log_id     SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES "user"(user_id) ON DELETE CASCADE,
    action     VARCHAR(100) NOT NULL,
    detail     TEXT,
    ip_address VARCHAR(45),
    timestamp  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- =====================================================
-- Indexes
-- =====================================================

CREATE INDEX idx_student_major ON student(major);
CREATE INDEX idx_course_semester ON course(semester);
CREATE INDEX idx_course_lecturer ON course(lecturer_id);
CREATE INDEX idx_enroll_student ON enroll(student_id);
CREATE INDEX idx_enroll_course ON enroll(course_id);
CREATE INDEX idx_assignment_course ON assignment(course_id);
CREATE INDEX idx_submission_student ON submission(student_id);
CREATE INDEX idx_quiz_course ON quiz(course_id);
CREATE INDEX idx_grade_student ON grade(student_id);
CREATE INDEX idx_message_sender ON message(sender_id);
CREATE INDEX idx_message_receiver ON message(receiver_id);

SELECT * FROM "user";