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
  total_score?: number;
  max_score?: number;
  percentage?: number;
  started_at?: string;
  finished_at?: string;
  duration_seconds?: number;
}

interface QuizAttemptHistory {
  quiz_id: number;
  quiz_title: string;
  attempts: QuizAttempt[];
}

interface Announcement {
  announcement_id: number;
  course_id: number;
  content: string;
  created_at: string;
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
  announcements?: Announcement[];
}

export default function StudentCoursePage() {
  const navigate = useNavigate();
  const { courseId } = useParams<{ courseId: string }>();
  const { user } = useAuth();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [quizAttempts, setQuizAttempts] = useState<QuizAttempt[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [showSubmitModal, setShowSubmitModal] = useState(false);
  const [selectedAssignment, setSelectedAssignment] = useState<Assignment | null>(null);
  const [submitFile, setSubmitFile] = useState<File | null>(null);
  const [submitting, setSubmitting] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [selectedQuizForHistory, setSelectedQuizForHistory] = useState<Quiz | null>(null);
  const [quizAttemptHistory, setQuizAttemptHistory] = useState<QuizAttempt[]>([]);

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

  const handleOpenSubmitModal = (assignment: Assignment) => {
    setSelectedAssignment(assignment);
    setShowSubmitModal(true);
  };

  const handleSubmitAssignment = async () => {
    if (!selectedAssignment || !user?.user_id) return;
    
    setSubmitting(true);
    try {
      // In a real app, you would upload the file first and get a URL
      const filePath = submitFile ? `/uploads/${submitFile.name}` : undefined;
      
      await studentAPI.submitAssignment(user.user_id, {
        assignment_id: selectedAssignment.id,
        file_path: filePath,
      });
      
      alert("Assignment submitted successfully!");
      setShowSubmitModal(false);
      setSubmitFile(null);
      setSelectedAssignment(null);
      
      // Refresh course data if needed
    } catch (err) {
      console.error("Failed to submit assignment", err);
      alert("Failed to submit assignment. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleShowQuizHistory = async (quiz: Quiz) => {
    if (!user?.user_id) return;
    
    setSelectedQuizForHistory(quiz);
    try {
      const res = await quizAPI.getStudentAttempts(user.user_id, quiz.id);
      // Filter attempts for this specific quiz and sort by started_at descending (newest first)
      const attempts = (res.data || [])
        .filter((a: QuizAttempt) => a.quiz_id === quiz.id)
        .sort((a: QuizAttempt, b: QuizAttempt) => {
          const aTime = new Date(a.started_at || 0).getTime();
          const bTime = new Date(b.started_at || 0).getTime();
          return bTime - aTime;
        });
      setQuizAttemptHistory(attempts);
      setShowHistoryModal(true);
    } catch (err) {
      console.error("Failed to load attempt history", err);
      alert("Failed to load attempt history.");
    }
  };

  const formatDuration = (seconds?: number) => {
    if (!seconds) return "N/A";
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
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

        {/* Announcements */}
        {course.announcements && course.announcements.length > 0 && (
          <section className="card mt-24" style={{ background: "#dbeafe", borderLeft: "4px solid #3b82f6" }}>
            <div className="card-header">
              <h2>📢 Announcements</h2>
            </div>
            <div className="mt-16">
              {course.announcements.map((announcement) => (
                <div
                  key={announcement.announcement_id}
                  style={{
                    marginBottom: "16px",
                    paddingBottom: "16px",
                    borderBottom: "1px solid #bfdbfe",
                  }}
                >
                  <p style={{ marginBottom: "8px" }}>{announcement.content}</p>
                  <div className="small-caption" style={{ color: "#64748b" }}>
                    Posted on {new Date(announcement.created_at).toLocaleString()}
                  </div>
                </div>
              ))}
            </div>
          </section>
        )}

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
                    <button 
                      className="btn btn-primary"
                      style={{ cursor: "pointer" }}
                      onClick={() => handleOpenSubmitModal(assignment)}
                    >
                      Submit work
                    </button>
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
                      <div style={{ display: "flex", gap: "8px" }}>
                        <button 
                          className="btn btn-secondary"
                          onClick={() => handleShowQuizHistory(quiz)}
                          style={{ padding: "6px 12px", fontSize: "13px" }}
                        >
                          View History
                        </button>
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
                  </div>
                );
              })
            )}
          </div>
        </section>

        {/* Submit Assignment Modal */}
        {showSubmitModal && selectedAssignment && (
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "rgba(0,0,0,0.5)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1000,
            }}
            onClick={() => setShowSubmitModal(false)}
          >
            <div
              className="card"
              style={{
                width: "500px",
                background: "#fff",
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <h2 style={{ marginBottom: "16px" }}>Submit Assignment</h2>
              <p className="small-caption" style={{ marginBottom: "16px" }}>
                <strong>{selectedAssignment.title}</strong>
              </p>
              <div className="form-group">
                <label className="form-label">Upload File</label>
                <input
                  type="file"
                  className="form-control"
                  onChange={(e) => setSubmitFile(e.target.files?.[0] || null)}
                />
                {submitFile && (
                  <p className="small-caption mt-8">
                    Selected: {submitFile.name} ({(submitFile.size / 1024).toFixed(2)} KB)
                  </p>
                )}
              </div>
              <div style={{ display: "flex", gap: "8px", marginTop: "16px" }}>
                <button
                  className="btn btn-primary"
                  onClick={handleSubmitAssignment}
                  disabled={submitting || !submitFile}
                >
                  {submitting ? "Submitting..." : "Submit"}
                </button>
                <button
                  className="btn btn-secondary"
                  onClick={() => {
                    setShowSubmitModal(false);
                    setSubmitFile(null);
                  }}
                >
                  Cancel
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Quiz Attempt History Modal */}
        {showHistoryModal && selectedQuizForHistory && (
          <div
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "rgba(0,0,0,0.5)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1000,
            }}
            onClick={() => setShowHistoryModal(false)}
          >
            <div
              className="card"
              style={{
                width: "700px",
                maxHeight: "80vh",
                overflow: "auto",
                background: "#fff",
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <h2 style={{ marginBottom: "8px" }}>Attempt History</h2>
              <p className="small-caption" style={{ marginBottom: "16px" }}>
                <strong>{selectedQuizForHistory.title}</strong>
              </p>
              {quizAttemptHistory.length === 0 ? (
                <p className="text-muted">No attempts yet.</p>
              ) : (
                <table className="table">
                  <thead>
                    <tr>
                      <th>Attempt</th>
                      <th>Date</th>
                      <th>Duration</th>
                      <th>Score</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {quizAttemptHistory.map((attempt, index) => (
                      <tr key={attempt.attempt_id}>
                        <td>#{quizAttemptHistory.length - index}</td>
                        <td>{attempt.started_at ? new Date(attempt.started_at).toLocaleString() : "N/A"}</td>
                        <td>{formatDuration(attempt.duration_seconds)}</td>
                        <td>
                          {attempt.total_score !== undefined && attempt.max_score !== undefined
                            ? `${attempt.total_score.toFixed(1)}/${attempt.max_score.toFixed(1)} (${attempt.percentage?.toFixed(1)}%)`
                            : "N/A"}
                        </td>
                        <td>
                          <button
                            className="btn btn-secondary"
                            style={{ padding: "4px 12px", fontSize: "12px" }}
                            onClick={() => {
                              setShowHistoryModal(false);
                              navigate(`/quiz-review/${attempt.attempt_id}`);
                            }}
                          >
                            View Details
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              )}
              <button
                className="btn btn-secondary mt-16"
                onClick={() => setShowHistoryModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
