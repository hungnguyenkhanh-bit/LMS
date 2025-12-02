import { useNavigate, useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { courseAPI, quizAPI } from "../services/api";
import { useAuth } from "../contexts/AuthContext";

interface Assignment {
  id: number;
  title: string;
  description: string;
  deadline: string;
  max_score: number;
}

interface Material {
  id: number;
  title: string;
  material_type: string;
  file_path: string;
  uploaded_at: string;
}

interface Quiz {
  id: number;
  title: string;
  description: string;
  start_time: string;
  end_time: string;
  duration_minutes: number;
  max_attempts: number;
}

interface QuizAttempt {
  attempt_id: number;
  quiz_id: number;
  status: string;
}

interface CourseDetail {
  id: number;
  code: string;
  name: string;
  description: string;
  credits: number;
  semester: string;
  lecturer_name: string;
  materials: Material[];
  assignments: Assignment[];
  quizzes: Quiz[];
}

export default function StudentCoursePage() {
  const navigate = useNavigate();
  const { courseId } = useParams<{ courseId: string }>();
  const { user } = useAuth();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [quizAttempts, setQuizAttempts] = useState<QuizAttempt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchCourseDetail = async () => {
      if (!courseId || !user?.user_id) return;
      try {
        setLoading(true);
        const [courseRes, attemptsRes] = await Promise.all([
          courseAPI.getCourseDetail(parseInt(courseId)),
          quizAPI.getStudentAttempts(user.user_id)
        ]);
        setCourse(courseRes.data);
        setQuizAttempts(attemptsRes.data || []);
      } catch (err: any) {
        setError(err.response?.data?.detail || "Failed to load course details");
      } finally {
        setLoading(false);
      }
    };
    fetchCourseDetail();
  }, [courseId, user?.user_id]);

  // Calculate remaining attempts for a quiz
  const getRemainingAttempts = (quiz: Quiz) => {
    const completedAttempts = quizAttempts.filter(
      a => a.quiz_id === quiz.id && a.status === "completed"
    ).length;
    const maxAttempts = quiz.max_attempts || 1;
    return Math.max(0, maxAttempts - completedAttempts);
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  };

  const formatTimeRange = (start: string, end: string) => {
    const startDate = new Date(start);
    const endDate = new Date(end);
    const dateStr = startDate.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
    const startTime = startDate.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
    const endTime = endDate.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
    return `${dateStr} · ${startTime} – ${endTime}`;
  };

  if (loading) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <p>Loading course details...</p>
        </div>
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <p style={{ color: "red" }}>{error || "Course not found"}</p>
          <button className="btn btn-secondary" onClick={() => navigate("/my-courses")}>
            ← Back to My Courses
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">
          {course.name} ({course.code})
        </h1>

        {/* Assignments */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Assignments</h2>
          </div>
          <div className="mt-16">
            {course.assignments.length === 0 ? (
              <p>No assignments yet.</p>
            ) : (
              course.assignments.map((assignment) => (
                <div
                  key={assignment.id}
                  className="card card--flat"
                  style={{
                    marginBottom: "12px",
                    background: "#fde68a",
                  }}
                >
                  <strong>{assignment.title}</strong>
                  <div className="small-caption">
                    Deadline: {formatDate(assignment.deadline)}
                  </div>
                  <div
                    className="mt-8"
                    style={{
                      display: "flex",
                      justifyContent: "flex-end",
                      gap: "8px",
                    }}
                  >
                    <a href="#" style={{ cursor: "pointer" }}>Submit work</a>
                  </div>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Course material */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Course material</h2>
          </div>
          <div className="mt-16">
            {course.materials.length === 0 ? (
              <p>No materials uploaded yet.</p>
            ) : (
              course.materials.map((material) => (
                <div
                  key={material.id}
                  className="card card--flat"
                  style={{ background: "#fde68a", marginBottom: "8px" }}
                >
                  <a href={material.file_path || "#"} target="_blank" rel="noopener noreferrer">
                    {material.title}
                  </a>
                  <span className="small-caption" style={{ marginLeft: "8px" }}>
                    ({material.material_type})
                  </span>
                </div>
              ))
            )}
          </div>
        </section>

        {/* Upcoming quizzes */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Upcoming Quizzes</h2>
          </div>
          <div className="mt-16">
            {course.quizzes.length === 0 ? (
              <p>No quizzes scheduled.</p>
            ) : (
              course.quizzes.map((quiz) => {
                const remainingAttempts = getRemainingAttempts(quiz);
                const hasAttempts = remainingAttempts > 0;
                
                return (
                  <div
                    key={quiz.id}
                    className="card card--flat"
                    style={{ background: "#fde68a", marginBottom: "8px" }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                      <div>
                        <strong>{quiz.title}</strong>
                        <div className="small-caption">
                          {formatTimeRange(quiz.start_time, quiz.end_time)}
                        </div>
                        <div className="small-caption" style={{ 
                          marginTop: "4px",
                          color: hasAttempts ? "#059669" : "#dc2626",
                          fontWeight: 600
                        }}>
                          Attempts remaining: {remainingAttempts} / {quiz.max_attempts || 1}
                        </div>
                      </div>
                      <button 
                        className="btn btn-primary"
                        onClick={() => navigate(`/quiz-taking/${quiz.id}`)}
                        disabled={!hasAttempts}
                        style={{ opacity: hasAttempts ? 1 : 0.5 }}
                      >
                        {hasAttempts ? "Attempt quiz" : "No attempts left"}
                      </button>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>

      </div>
    </div>
  );
}
