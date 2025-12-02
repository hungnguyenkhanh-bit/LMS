import os
from pathlib import Path
from typing import Generator, List

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Load environment variables from .env if present
load_dotenv()



class Settings:
    """Simple settings loader for database connection."""

    def __init__(self) -> None:
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_port = os.getenv("DB_PORT", "5432")
        self.db_name = os.getenv("DB_NAME", "LMS")
        self.db_user = os.getenv("DB_USER", "postgres")
        self.db_password = os.getenv("DB_PASSWORD", "hung")
    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"postgresql+psycopg2://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

settings = Settings()

engine = create_engine(settings.sqlalchemy_database_uri, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db() -> Generator:
    """Provide a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def _prepare_create_statements(raw_sql: str) -> List[str]:
    """Extract CREATE TABLE statements and make them idempotent."""
    statements: List[str] = []
    for chunk in raw_sql.split(";"):
        cleaned = chunk.strip()
        if not cleaned:
            continue
        lowered = cleaned.lower()
        if not lowered.startswith("create table"):
            # Skip SELECT/TRUNCATE/DROP or incomplete lines in the provided SQL file
            continue
        body = cleaned[len("create table") :].strip()
        fixed = f"CREATE TABLE IF NOT EXISTS {body}"
        statements.append(fixed + ";")
    return statements


def sync_sequences() -> None:
    """
    Synchronize all sequences to ensure they are greater than the max ID in each table.
    This prevents duplicate key errors when inserting new records.
    """
    # Mapping of sequence_name -> (table_name, id_column)
    sequence_mappings = [
        ("message_message_id_seq", "message", "message_id"),
        ("feedback_feedback_id_seq", "feedback", "feedback_id"),
        ("quiz_attempt_attempt_id_seq", "quiz_attempt", "attempt_id"),
        ("quiz_attempt_detail_detail_id_seq", "quiz_attempt_detail", "detail_id"),
        ("submission_submission_id_seq", "submission", "submission_id"),
        ("grade_grade_id_seq", "grade", "grade_id"),
        ("course_rating_rating_id_seq", "course_rating", "rating_id"),
        ("enroll_enroll_id_seq", "enroll", "enroll_id"),
        ("user_user_id_seq", "user", "user_id"),
        ("course_course_id_seq", "course", "course_id"),
        ("quiz_quiz_id_seq", "quiz", "quiz_id"),
        ("quiz_question_question_id_seq", "quiz_question", "question_id"),
        ("assignment_assignment_id_seq", "assignment", "assignment_id"),
        ("materials_materials_id_seq", "materials", "materials_id"),
        ("activity_log_log_id_seq", "activity_log", "log_id"),
    ]
    
    with engine.begin() as connection:
        for seq_name, table_name, id_col in sequence_mappings:
            try:
                # Get the max id from the table
                result = connection.execute(
                    text(f"SELECT COALESCE(MAX({id_col}), 0) FROM {table_name}")
                )
                max_id = result.scalar() or 0
                
                # Set the sequence to max_id + 1
                connection.execute(
                    text(f"SELECT setval('{seq_name}', {max_id + 1}, false)")
                )
            except Exception as e:
                # Skip if sequence or table doesn't exist
                pass


def run_schema_sql() -> None:
    """
    Parse and execute CREATE TABLE statements from DB/LMS.sql.

    This function intentionally skips TRUNCATE/DROP/SELECT statements present
    in the SQL file to keep existing data safe.
    """
    # Path: BE/app/database.py -> BE -> DB/LMS.sql
    base_dir = Path(__file__).resolve().parents[1]
    schema_path = base_dir.parent / "DB" / "LMS.sql"
    if not schema_path.exists():
        print(f"[database] Schema file not found at {schema_path}")
        return

    raw_sql = schema_path.read_text(encoding="utf-8")
    statements = _prepare_create_statements(raw_sql)
    if not statements:
        print("[database] No CREATE TABLE statements found in schema.")
        return

    with engine.begin() as connection:
        for stmt in statements:
            connection.execute(text(stmt))
    print(f"[database] Applied schema from {schema_path}")
    
    # Sync sequences to prevent duplicate key errors
    sync_sequences()
