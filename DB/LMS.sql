CREATE TABLE "User" (
    User_id       SERIAL PRIMARY KEY,
    Username      VARCHAR(20) UNIQUE,
    "Password_Hash" TEXT NOT NULL,
    "Role"        VARCHAR(20) NOT NULL,
    Email         VARCHAR(50) NOT NULL
);

CREATE TABLE "Student" (
    User_id     INT PRIMARY KEY,
    Student_id  INT UNIQUE NOT NULL,
    LName       VARCHAR(20) NOT NULL,
    MName       VARCHAR(20) NOT NULL,
    FName       VARCHAR(20) NOT NULL,
    Major       VARCHAR(50) NOT NULL,
    DOB         DATE,
    Current_GPA DECIMAL(2,1) NOT NULL,
    Target_GPA  DECIMAL(2,1),
    CONSTRAINT fk_student_user
        FOREIGN KEY (User_id)
        REFERENCES "User"(User_id)
        ON DELETE CASCADE
);

CREATE TABLE "Lecturer" (
    User_id    INT PRIMARY KEY,
    Title      VARCHAR(100),
    LName      VARCHAR(20) NOT NULL,
    MName      VARCHAR(20) NOT NULL,
    FName      VARCHAR(20) NOT NULL,
    Department VARCHAR(100) NOT NULL,
    CONSTRAINT fk_lecturer_user
        FOREIGN KEY (User_id)
        REFERENCES "User"(User_id)
        ON DELETE CASCADE
);

CREATE TABLE "Manager" (
    User_id   INT PRIMARY KEY,
    "Name"    VARCHAR(200) NOT NULL,
    Office    VARCHAR(100) NOT NULL,
    "Position" VARCHAR(100),
    CONSTRAINT fk_manager_user
        FOREIGN KEY (User_id)
        REFERENCES "User"(User_id)
        ON DELETE CASCADE
);

CREATE TABLE "Prediction" (
    Prediction_id    SERIAL PRIMARY KEY,
    User_id          INT NOT NULL,
    Predicted_GPA    DECIMAL(2,1) NOT NULL,
    Confidence_level DECIMAL(5,2) NOT NULL,
    Model_version    VARCHAR(20) NOT NULL,
    Recommendations  TEXT,
    Target_GPA       DECIMAL(2,1),
    CONSTRAINT fk_predict_student
        FOREIGN KEY (User_id)
        REFERENCES "Student"(User_id)
        ON DELETE CASCADE
);

CREATE TABLE "Attendance_Record" (
    Record_id SERIAL PRIMARY KEY,
    "Date"    DATE NOT NULL,
    "Status"  VARCHAR(20) NOT NULL
);

CREATE TABLE "Course" (
    Course_id   SERIAL PRIMARY KEY,
    Course_code VARCHAR(100) UNIQUE NOT NULL,
    Course_name VARCHAR(100) NOT NULL,
    Credits     INT NOT NULL,
    Capacity    INT NOT NULL CHECK (Capacity < 100),
    Semester    VARCHAR(20) NOT NULL
);

CREATE TABLE "Feedback" (
    Feedback_id SERIAL PRIMARY KEY,
    "Content"     VARCHAR(500),
    Rating      INT NOT NULL DEFAULT 1 CHECK (Rating >= 1 AND Rating <= 5),
    Student_id  INT NOT NULL,
    Course_id   INT NOT NULL,
    CONSTRAINT fk_feedback_student
        FOREIGN KEY (Student_id)
        REFERENCES "Student"(User_id)
        ON DELETE CASCADE,
    CONSTRAINT fk_feedback_course
        FOREIGN KEY (Course_id)
        REFERENCES "Course"(Course_id)
        ON DELETE CASCADE
);

CREATE TABLE "Attendance_Detail" (
    Course_id            INT,
    Record_id INT,
    Student_id           INT,
    CONSTRAINT fk_check_attendance_record
        FOREIGN KEY (Record_id)
        REFERENCES "Attendance_Record"(Record_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_check_student
        FOREIGN KEY (Student_id)
        REFERENCES "Student"(User_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_check_course
        FOREIGN KEY (Course_id)
        REFERENCES "Course"(Course_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (Course_id, Record_id, Student_id)
);

CREATE TABLE "Materials" (
    Materials_id SERIAL PRIMARY KEY,
    Course_id    INT NOT NULL,
    "Type"       VARCHAR(50) NOT NULL,
    "Description" VARCHAR(200),
    Title        VARCHAR(100) UNIQUE,
    File_path    VARCHAR(200) UNIQUE,
    Upload_date  DATE NOT NULL,
    CONSTRAINT fk_materials_course
        FOREIGN KEY (Course_id)
        REFERENCES "Course"(Course_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);

CREATE TABLE "Enroll" (
    Course_id  INT,
    Student_id INT,
    CONSTRAINT fk_enroll_course
        FOREIGN KEY (Course_id)
        REFERENCES "Course"(Course_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_enroll_student
        FOREIGN KEY (Student_id)
        REFERENCES "Student"(User_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    PRIMARY KEY (Course_id, Student_id)
);

CREATE TABLE "Assignment" (
    Assignment_id SERIAL PRIMARY KEY,
    "Description" VARCHAR(200),
    Deadlines     DATE NOT NULL
);

CREATE TABLE "Submission" (
    Submission_id SERIAL PRIMARY KEY,
    Assignment_id INT NOT NULL,
    Student_id    INT NOT NULL,
    Score         DECIMAL(5,2),
    File_path     VARCHAR(200) UNIQUE,
    CONSTRAINT fk_submission_assignment
        FOREIGN KEY (Assignment_id)
        REFERENCES "Assignment"(Assignment_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT fk_submission_student
        FOREIGN KEY (Student_id)
        REFERENCES "Student"(User_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    CONSTRAINT uq_submission UNIQUE (Assignment_id, Student_id)
);

CREATE TABLE "Activity_Log" (
    Log_id    SERIAL PRIMARY KEY,
    Detail    VARCHAR(100),
    "Action"  VARCHAR(50) NOT NULL,
    "Timestamp" TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    IP_Address VARCHAR(45) NOT NULL,
    User_id    INT NOT NULL,
    CONSTRAINT fk_track_user
        FOREIGN KEY (User_id)
        REFERENCES "User"(User_id)
        ON DELETE CASCADE
);

SELECT * FROM "User";
SELECT * FROM "Student";
SELECT * FROM "Lecturer";
SELECT * FROM "Manager";
SELECT * FROM ;
SELECT * FROM ;
SELECT * FROM ;
SELECT * FROM ;
SELECT * FROM ;
SELECT * FROM ;
SELECT * FROM ;
SELECT * FROM ;
SELECT * FROM ;
SELECT * FROM ;

TRUNCATE TABLE
    "Attendance_Detail",
    "Feedback",
    "Materials",
    "Enroll",
    "Attendance_Record",
    "Prediction",
    "Assignment",
    "Student",
    "Lecturer",
    "Manager",
    "Course",
    "User",
    "Submission",
    "Activity_Log"
RESTART IDENTITY CASCADE;

DROP TABLE IF EXISTS
    "Attendance_Detail",
    "Feedback",
    "Materials",
    "Enroll",
    "Attendance_Record",
    "Prediction",
    "Assignment",
    "Student",
    "Lecturer",
    "Manager",
    "Course",
    "User",
    "Submission",
    "Activity_Log"
CASCADE;
