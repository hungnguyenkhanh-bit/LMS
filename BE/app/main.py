from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models
from app.database import engine, run_schema_sql
from app.routers import auth, courses, quizzes, students, lecturers, managers, messages

app = FastAPI(title="Learning Management System API", version="0.1.0")

# Allow all origins for now; tighten as needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event() -> None:
    # Ensure schema exists based on the provided SQL file.
    run_schema_sql()
    # Sync SQLAlchemy models with the database for convenience
    models.Base.metadata.create_all(bind=engine)


app.include_router(auth.router)
app.include_router(students.router)
app.include_router(courses.router)
app.include_router(quizzes.router)
app.include_router(lecturers.router)
app.include_router(managers.router)
app.include_router(messages.router)


@app.get("/")
def healthcheck() -> dict:
    return {"status": "ok", "service": "lms-api"}