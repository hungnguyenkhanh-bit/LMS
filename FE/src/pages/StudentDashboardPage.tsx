import { useEffect, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { useAuth } from "../contexts/AuthContext";
import { studentAPI } from "../services/api";
import type { PredictionInput, PredictionResult } from "../services/api";

interface DashboardStats {
  courses_enrolled: number;
  submissions: number;
  average_score: number | null;
  current_gpa: number | null;
  predicted_gpa: number | null;
  target_gpa: number | null;
  recommendations: string | null;
}

interface Assignment {
  id: number;
  course_id: number;
  title: string;
  description: string | null;
  deadline: string;
  max_score: number;
  submission_status: string;
  score: number | null;
}

interface Course {
  id: number;
  code: string;
  name: string;
  credits: number;
  semester: string;
  lecturer_name: string | null;
}

interface GPADataPoint {
  semester: string; // label trên trục X, ví dụ "231"
  semesterGPA: number;
  overallGPA: number;
}

// const gpaData = [
//   { semester: "211", semesterGPA: 3.8, overallGPA: 3.6 },
//   { semester: "212", semesterGPA: 3.8, overallGPA: 3.6 },
//   { semester: "213", semesterGPA: 3.8, overallGPA: 3.6 },
//   { semester: "221", semesterGPA: 0.0, overallGPA: 2.8 },
//   { semester: "222", semesterGPA: 3.0, overallGPA: 3.0 },
//   { semester: "223", semesterGPA: 3.1, overallGPA: 3.1 },
//   { semester: "231", semesterGPA: 3.2, overallGPA: 3.2 },
//   { semester: "232", semesterGPA: 3.3, overallGPA: 3.3 },
//   { semester: "233", semesterGPA: 3.7, overallGPA: 3.4 },
//   { semester: "241", semesterGPA: 3.8, overallGPA: 3.6 },
//   { semester: "242", semesterGPA: 3.8, overallGPA: 3.7 },
//   { semester: "243", semesterGPA: 3.8, overallGPA: 3.8 },
//   { semester: "251", semesterGPA: 3.8, overallGPA: 4.0 },
// ];

const StudentDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [gpaData, setGpaData] = useState<GPADataPoint[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [targetGpa, setTargetGpa] = useState<string>("");
  const [savingGoal, setSavingGoal] = useState(false);

  // Prediction feature state
  const [showPredictionModal, setShowPredictionModal] = useState(false);
  const [predictionLoading, setPredictionLoading] = useState(false);
  const [predictionResult, setPredictionResult] =
    useState<PredictionResult | null>(null);
  const [predictionError, setPredictionError] = useState<string | null>(null);

  // Form state for prediction inputs (initialized with default values)
  const [predictionForm, setPredictionForm] = useState({
    attendance_rate: "",
    avg_quiz_score: "",
    assignment_score: "",
    study_hours_per_week: "",
  });

  useEffect(() => {
    const fetchData = async () => {
      if (!user?.user_id) return;

      try {
        setLoading(true);
        const [dashboardRes, assignmentsRes, coursesRes, gpaHistoryRes] =
          await Promise.all([
            studentAPI.getDashboard(user.user_id),
            studentAPI.getAssignments(user.user_id),
            studentAPI.getCourses(user.user_id),
            studentAPI.getGPAHistory(user.user_id),
          ]);

        setStats(dashboardRes.data);
        setAssignments(assignmentsRes.data || []);
        setCourses(coursesRes.data || []);

        if (dashboardRes.data?.target_gpa) {
          setTargetGpa(dashboardRes.data.target_gpa.toString());
        }

        // ---- map GPA history -> data cho chart ----
        const history = gpaHistoryRes.data as {
          entrance_year: number;
          points: {
            semester: string;
            semester_gpa: number;
            overall_gpa: number;
          }[];
        };

        if (history && history.points?.length) {
          const mapped: GPADataPoint[] = history.points.map((p) => {
            // chuyển "2023-1" -> "231" cho đẹp, hoặc thích thì giữ nguyên "2023-1"
            const [yearStr, termStr] = p.semester.split("-");
            const shortLabel =
              yearStr && termStr ? yearStr.slice(-2) + termStr : p.semester;

            return {
              semester: shortLabel,
              semesterGPA: Number(p.semester_gpa.toFixed(2)),
              overallGPA: Number(p.overall_gpa.toFixed(2)),
            };
          });
          setGpaData(mapped);
        } else {
          setGpaData([]);
        }
      } catch (error) {
        console.error("Error fetching dashboard data:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [user?.user_id]);

  const handleSetGoal = async () => {
    if (!user?.user_id) return;

    const gpaValue = parseFloat(targetGpa);
    if (isNaN(gpaValue) || gpaValue < 0 || gpaValue > 4) {
      alert("Please enter a valid GPA between 0.0 and 4.0");
      return;
    }

    try {
      setSavingGoal(true);
      await studentAPI.setTargetGPA(user.user_id, gpaValue);
      // Refresh dashboard stats
      const dashboardRes = await studentAPI.getDashboard(user.user_id);
      setStats(dashboardRes.data);
      setShowGoalModal(false);
      alert("Target GPA saved successfully!");
    } catch (error) {
      console.error("Error setting target GPA:", error);
      alert("Failed to save target GPA. Please try again.");
    } finally {
      setSavingGoal(false);
    }
  };

  const handlePredict = async () => {
    if (!user?.user_id) return;

    // Clear previous errors
    setPredictionError(null);

    // Validate all fields are filled
    if (
      !predictionForm.attendance_rate ||
      !predictionForm.avg_quiz_score ||
      !predictionForm.assignment_score ||
      !predictionForm.study_hours_per_week
    ) {
      setPredictionError("Please fill in all fields");
      return;
    }

    // Convert strings to numbers and validate ranges
    const attendance = parseFloat(predictionForm.attendance_rate);
    const quizScore = parseFloat(predictionForm.avg_quiz_score);
    const assignmentScore = parseFloat(predictionForm.assignment_score);
    const studyHours = parseFloat(predictionForm.study_hours_per_week);

    if (isNaN(attendance) || attendance < 0 || attendance > 100) {
      setPredictionError("Attendance must be between 0 and 100");
      return;
    }

    if (isNaN(quizScore) || quizScore < 0 || quizScore > 100) {
      setPredictionError("Quiz score must be between 0 and 100");
      return;
    }

    if (
      isNaN(assignmentScore) ||
      assignmentScore < 0 ||
      assignmentScore > 100
    ) {
      setPredictionError("Assignment score must be between 0 and 100");
      return;
    }

    if (isNaN(studyHours) || studyHours < 0) {
      setPredictionError("Study hours must be 0 or greater");
      return;
    }

    // Build the API request payload
    const predictionData: PredictionInput = {
      attendance_rate: attendance / 100, // Convert percentage to decimal (85 -> 0.85)
      avg_quiz_score: quizScore,
      assignment_score: assignmentScore,
      study_hours_per_week: studyHours,
    };

    // Call the API
    setPredictionLoading(true);

    try {
      const response = await studentAPI.predictPassFail(
        user.user_id,
        predictionData
      );
      setPredictionResult(response.data);
      setPredictionError(null);
    } catch (error: any) {
      console.error("Prediction error:", error);

      // Handle different error types
      if (error.response) {
        switch (error.response.status) {
          case 401:
            
            setPredictionError("Session expired. Please log in again.");
            break;
          case 403:
            setPredictionError(
              "You don't have permission to make this prediction."
            );
            break;
          case 422:
            return error.response.data.detail;
            setPredictionError("Invalid input data. Please check your values.");
            break;
          case 500:
            setPredictionError(
              "Prediction service is unavailable. Please try again later."
            );
            break;
          default:
            setPredictionError(
              "An unexpected error occurred. Please try again."
            );
        }
      } else {
        setPredictionError("Network error. Please check your connection.");
      }
    } finally {
      setPredictionLoading(false);
    }
  };

  // Get user initials for avatar
  const getInitials = (name: string) => {
    if (!name) return "A";
    const parts = name.split(" ");
    if (parts.length >= 1) {
      return parts[0][0];
    }
    return name[0];
  };

  const getEntranceYear = (studentId?: number | null) => {
    if (!studentId) return null;
    const idStr = studentId.toString();
    if (idStr.length < 2) return null;
    const yearDigits = idStr.slice(0, 2);
    const parsed = parseInt(yearDigits, 10);
    if (Number.isNaN(parsed)) return null;
    return 2000 + parsed;
  };

  // Get status for deadline
  const getDeadlineStatus = (deadline: string, submissionStatus: string) => {
    if (submissionStatus === "graded") return "completed";
    if (submissionStatus === "submitted") return "completed";
    const deadlineDate = new Date(deadline);
    const now = new Date();
    if (deadlineDate < now) return "overdue";
    return "due";
  };

  // Format date
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleDateString();
  };

  // Get upcoming assignments (not completed, sorted by deadline)
  const upcomingAssignments = assignments
    .filter((a) => a.submission_status !== "graded")
    .sort(
      (a, b) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime()
    )
    .slice(0, 5);

  return (
    <>
      {/* TOP ROW: PROFILE + UPCOMING DEADLINES */}
      <div className="grid grid-2">
        {/* LEFT: student profile card */}
        <section className="card card--profile-dark">
          <div
            style={{
              display: "flex",
              gap: "24px",
              alignItems: "center",
            }}
          >
            <div
              style={{
                height: "120px",
                width: "120px",
                borderRadius: "999px",
                background: "#facc6b",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: "56px",
                fontWeight: 700,
              }}
            >
              {getInitials(user?.full_name || "A")}
            </div>
            <div>
              <h2 style={{ fontSize: "24px", marginBottom: "8px" }}>
                {user?.full_name || "Student Name"}
              </h2>
              <p className="small-caption">
                Entrance Year: {getEntranceYear(user?.student_id) || "N/A"}
              </p>
              <p className="small-caption">
                Student ID: {user?.student_id || "N/A"}
              </p>
              <p className="small-caption">Major: {user?.major || "N/A"}</p>
              <p className="small-caption">
                Current GPA:{" "}
                {stats?.current_gpa?.toFixed(2) ||
                  user?.current_gpa?.toFixed(2) ||
                  "N/A"}
              </p>
            </div>
          </div>

          <div className="mt-24">
            <h3 style={{ fontSize: "16px", marginBottom: "4px" }}>About Me</h3>
            <p className="text-muted">
              Passionate Computer Science student with a keen interest in AI and
              Machine Learning. Actively involved in coding clubs and academic
              research.
            </p>
          </div>
        </section>

        {/* RIGHT: upcoming deadlines */}
        <section className="card">
          <div className="card-header">
            <h2>Upcoming Deadlines</h2>
            <a href="#" className="small-caption">
              View All
            </a>
          </div>
          <div className="mt-8">
            {loading ? (
              <p className="text-muted">Loading...</p>
            ) : upcomingAssignments.length === 0 ? (
              <p className="text-muted">No upcoming deadlines</p>
            ) : (
              upcomingAssignments.map((assignment) => {
                const status = getDeadlineStatus(
                  assignment.deadline,
                  assignment.submission_status
                );
                const course = courses.find(
                  (c) => c.id === assignment.course_id
                );
                return (
                  <div
                    key={assignment.id}
                    className="card card--flat"
                    style={{
                      background: "#fff7c9",
                      borderRadius: 0,
                      marginBottom: "4px",
                      padding: "10px 0",
                    }}
                  >
                    <div
                      style={{
                        display: "flex",
                        justifyContent: "space-between",
                        alignItems: "center",
                      }}
                    >
                      <div>
                        <strong>{assignment.title}</strong>
                        <div className="small-caption">
                          {course?.code || `Course ${assignment.course_id}`}
                        </div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div className="small-caption">
                          Due {formatDate(assignment.deadline)}
                        </div>
                        <span className={`status-pill status-pill--${status}`}>
                          {status}
                        </span>
                      </div>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </section>
      </div>

      {/* PERFORMANCE OVERVIEW CHART */}
      <section className="card mt-24">
        <div className="card-header">
          <h2>Performance Overview</h2>
          <a href="#" className="small-caption">
            View Details
          </a>
        </div>

        <div className="mt-16" style={{ height: 260 }}>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart
              data={gpaData}
              margin={{ top: 10, right: 20, left: 0, bottom: 0 }}
            >
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="semester" />
              <YAxis domain={[2.0, 4.0]} />
              <Tooltip />
              <Legend />
              <Line
                type="monotone"
                dataKey="semesterGPA"
                name="Semester GPA"
                stroke="#2563eb"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
              <Line
                type="monotone"
                dataKey="overallGPA"
                name="Overall GPA"
                stroke="#f97316"
                strokeWidth={2}
                dot={{ r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Goal controls below the chart */}
        <div
          className="mt-16"
          style={{
            background: "#f9fafb",
            padding: "12px 16px",
            borderRadius: "8px",
            border: "1px solid #e5e7eb",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div className="small-caption">
            Current Goal:{" "}
            <strong>{stats?.target_gpa?.toFixed(1) || "Not set"}</strong>
          </div>
          <div style={{ display: "flex", gap: "8px" }}>
            <button
              className="btn btn-secondary"
              style={{ padding: "6px 12px", fontSize: "12px" }}
              onClick={() => setShowGoalModal(true)}
            >
              Set goal
            </button>
            <button
              className="btn btn-primary"
              style={{ padding: "6px 12px", fontSize: "12px" }}
              onClick={() => {
                // Pre-fill form with current data if available
                if (stats) {
                  setPredictionForm({
                    attendance_rate: "", // User needs to provide this
                    avg_quiz_score: stats.average_score?.toString() || "",
                    assignment_score: stats.average_score?.toString() || "",
                    study_hours_per_week: "",
                  });
                }
                setShowPredictionModal(true);
                setPredictionResult(null); // Clear previous results
                setPredictionError(null); // Clear previous errors
              }}
            >
              Get prediction
            </button>
          </div>
        </div>
      </section>

      {/* Set Goal Modal */}
      {showGoalModal && (
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
          onClick={() => setShowGoalModal(false)}
        >
          <div
            className="card"
            style={{
              width: "400px",
              background: "#fff",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ marginBottom: "16px" }}>Set Target GPA</h2>
            <div className="form-group">
              <label className="form-label">Target GPA (0.0 - 4.0)</label>
              <input
                type="number"
                className="form-control"
                value={targetGpa}
                onChange={(e) => setTargetGpa(e.target.value)}
                min="0"
                max="4"
                step="0.1"
                placeholder="e.g., 3.5"
              />
            </div>
            <div style={{ display: "flex", gap: "8px", marginTop: "16px" }}>
              <button
                className="btn btn-primary"
                onClick={handleSetGoal}
                disabled={savingGoal}
              >
                {savingGoal ? "Saving..." : "Save Goal"}
              </button>
              <button
                className="btn btn-secondary"
                onClick={() => setShowGoalModal(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Prediction Modal */}
      {showPredictionModal && (
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
            overflow: "auto",
          }}
          onClick={() => setShowPredictionModal(false)}
        >
          <div
            className="card"
            style={{
              width: "600px",
              maxHeight: "90vh",
              overflowY: "auto",
              background: "#fff",
              margin: "20px",
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <h2 style={{ marginBottom: "8px" }}>Pass/Fail Prediction</h2>
            <p className="text-muted" style={{ marginBottom: "24px" }}>
              Enter your performance metrics to get a prediction
            </p>

            {/* Error Display */}
            {predictionError && (
              <div
                style={{
                  background: "#fee",
                  border: "1px solid #fcc",
                  padding: "12px",
                  borderRadius: "4px",
                  marginBottom: "16px",
                  color: "#c33",
                }}
              >
                {predictionError}
              </div>
            )}

            {/* Prediction Form */}
            {!predictionResult && (
              <div>
                <div className="form-group">
                  <label className="form-label">Attendance Rate (%) *</label>
                  <input
                    type="number"
                    className="form-control"
                    value={predictionForm.attendance_rate}
                    onChange={(e) =>
                      setPredictionForm({
                        ...predictionForm,
                        attendance_rate: e.target.value,
                      })
                    }
                    min="0"
                    max="100"
                    step="1"
                    placeholder="e.g., 85"
                  />
                  <small className="text-muted">
                    Enter as percentage (0-100)
                  </small>
                </div>

                <div className="form-group">
                  <label className="form-label">
                    Average Quiz Score (0-100) *
                  </label>
                  <input
                    type="number"
                    className="form-control"
                    value={predictionForm.avg_quiz_score}
                    onChange={(e) =>
                      setPredictionForm({
                        ...predictionForm,
                        avg_quiz_score: e.target.value,
                      })
                    }
                    min="0"
                    max="100"
                    step="0.1"
                    placeholder="e.g., 75"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">
                    Assignment Score (0-100) *
                  </label>
                  <input
                    type="number"
                    className="form-control"
                    value={predictionForm.assignment_score}
                    onChange={(e) =>
                      setPredictionForm({
                        ...predictionForm,
                        assignment_score: e.target.value,
                      })
                    }
                    min="0"
                    max="100"
                    step="0.1"
                    placeholder="e.g., 80"
                  />
                </div>

                <div className="form-group">
                  <label className="form-label">Study Hours per Week *</label>
                  <input
                    type="number"
                    className="form-control"
                    value={predictionForm.study_hours_per_week}
                    onChange={(e) =>
                      setPredictionForm({
                        ...predictionForm,
                        study_hours_per_week: e.target.value,
                      })
                    }
                    min="0"
                    step="0.5"
                    placeholder="e.g., 12"
                  />
                </div>

                <div style={{ display: "flex", gap: "8px", marginTop: "24px" }}>
                  <button
                    className="btn btn-primary"
                    onClick={handlePredict}
                    disabled={predictionLoading}
                  >
                    {predictionLoading ? "Predicting..." : "Get Prediction"}
                  </button>
                  <button
                    className="btn btn-secondary"
                    onClick={() => setShowPredictionModal(false)}
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}

            {/* Prediction Result Display */}
            {predictionResult && (
              <div>
                {/* Pass/Fail Status Banner */}
                <div
                  style={{
                    background:
                      predictionResult.pass_fail === "pass"
                        ? "#d1fae5"
                        : "#fee2e2",
                    border: `2px solid ${
                      predictionResult.pass_fail === "pass"
                        ? "#10b981"
                        : "#ef4444"
                    }`,
                    borderRadius: "8px",
                    padding: "20px",
                    marginBottom: "20px",
                    textAlign: "center",
                  }}
                >
                  <div style={{ fontSize: "48px", marginBottom: "8px" }}>
                    {predictionResult.pass_fail === "pass" ? "✅" : "⚠️"}
                  </div>
                  <h3
                    style={{
                      fontSize: "24px",
                      margin: "0 0 8px 0",
                      color:
                        predictionResult.pass_fail === "pass"
                          ? "#065f46"
                          : "#991b1b",
                    }}
                  >
                    {predictionResult.pass_fail === "pass"
                      ? "Likely to Pass"
                      : "At Risk of Failing"}
                  </h3>
                  <p className="text-muted">
                    Based on your current performance metrics
                  </p>
                </div>

                {/* Prediction Details */}
                <div style={{ marginBottom: "20px" }}>
                  <div
                    style={{
                      display: "grid",
                      gridTemplateColumns: "1fr 1fr",
                      gap: "16px",
                      marginBottom: "16px",
                    }}
                  >
                    {/* Predicted GPA */}
                    <div
                      style={{
                        background: "#f9fafb",
                        padding: "16px",
                        borderRadius: "8px",
                        border: "1px solid #e5e7eb",
                      }}
                    >
                      <div
                        className="small-caption"
                        style={{ marginBottom: "4px" }}
                      >
                        Predicted GPA
                      </div>
                      <div style={{ fontSize: "28px", fontWeight: 700 }}>
                        {predictionResult.predicted_gpa.toFixed(2)}
                      </div>
                      <div className="small-caption">out of 4.0</div>
                    </div>

                    {/* Confidence Score */}
                    <div
                      style={{
                        background: "#f9fafb",
                        padding: "16px",
                        borderRadius: "8px",
                        border: "1px solid #e5e7eb",
                      }}
                    >
                      <div
                        className="small-caption"
                        style={{ marginBottom: "4px" }}
                      >
                        Confidence Level
                      </div>
                      <div style={{ fontSize: "28px", fontWeight: 700 }}>
                        {(predictionResult.confidence * 100).toFixed(0)}%
                      </div>
                      <div className="small-caption">
                        {predictionResult.confidence >= 0.8
                          ? "High confidence"
                          : predictionResult.confidence >= 0.6
                          ? "Moderate confidence"
                          : "Low confidence"}
                      </div>
                    </div>
                  </div>

                  {/* Pass/Fail Threshold Info */}
                  <div
                    style={{
                      background: "#fffbeb",
                      border: "1px solid #fcd34d",
                      padding: "12px",
                      borderRadius: "8px",
                      marginBottom: "16px",
                    }}
                  >
                    <strong>Pass/Fail Threshold:</strong>{" "}
                    {predictionResult.threshold.toFixed(1)} GPA
                    <br />
                    <small className="text-muted">
                      You need a GPA of {predictionResult.threshold.toFixed(1)}{" "}
                      or higher to pass.
                      {predictionResult.pass_fail === "pass" && (
                        <>
                          {" "}
                          You're currently{" "}
                          <strong>
                            {(
                              predictionResult.predicted_gpa -
                              predictionResult.threshold
                            ).toFixed(2)}{" "}
                            points above
                          </strong>{" "}
                          the threshold.
                        </>
                      )}
                      {predictionResult.pass_fail === "fail" && (
                        <>
                          {" "}
                          You're currently{" "}
                          <strong>
                            {(
                              predictionResult.threshold -
                              predictionResult.predicted_gpa
                            ).toFixed(2)}{" "}
                            points below
                          </strong>{" "}
                          the threshold.
                        </>
                      )}
                    </small>
                  </div>

                  {/* Recommendations */}
                  <div
                    style={{
                      background: "#f0f9ff",
                      border: "1px solid #bae6fd",
                      padding: "16px",
                      borderRadius: "8px",
                    }}
                  >
                    <h4 style={{ fontSize: "16px", marginBottom: "12px" }}>
                      📝 Personalized Recommendations
                    </h4>
                    <div style={{ whiteSpace: "pre-wrap", lineHeight: "1.6" }}>
                      {predictionResult.recommendations}
                    </div>
                  </div>

                  {/* Model Version */}
                  <div style={{ marginTop: "16px", textAlign: "center" }}>
                    <small className="text-muted">
                      Model version: {predictionResult.model_version}
                    </small>
                  </div>
                </div>

                {/* Action Buttons */}
                <div style={{ display: "flex", gap: "8px", marginTop: "24px" }}>
                  <button
                    className="btn btn-secondary"
                    onClick={() => {
                      setPredictionResult(null);
                      setPredictionError(null);
                    }}
                  >
                    Try Again
                  </button>
                  <button
                    className="btn btn-primary"
                    onClick={() => {
                      setShowPredictionModal(false);
                      setPredictionResult(null);
                      setPredictionError(null);
                    }}
                  >
                    Close
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* MIDDLE: notifications + attendance + syllabus progress */}
      <div className="grid grid-3 mt-24">
        <section className="card">
          <div className="card-header">
            <h2>Recent Activity</h2>
            <a href="#" className="small-caption">
              View All
            </a>
          </div>
          <div className="mt-12">
            {assignments.slice(0, 3).map((assignment) => (
              <div key={assignment.id} className="mb-8">
                <strong style={{ fontSize: "14px" }}>
                  {assignment.submission_status === "graded"
                    ? `Graded: ${assignment.title}`
                    : assignment.submission_status === "submitted"
                    ? `Submitted: ${assignment.title}`
                    : `Pending: ${assignment.title}`}
                </strong>
                <div className="small-caption">
                  {assignment.submission_status === "graded" && assignment.score
                    ? `Score: ${assignment.score}/${assignment.max_score}`
                    : `Due: ${formatDate(assignment.deadline)}`}
                </div>
              </div>
            ))}
            {assignments.length === 0 && (
              <p className="text-muted">No recent activity</p>
            )}
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <h2>Assignment Progress</h2>
          </div>
          <div className="mt-16" style={{ textAlign: "center" }}>
            <div style={{ fontSize: "28px", fontWeight: 700 }}>
              {
                assignments.filter(
                  (a) =>
                    a.submission_status === "graded" ||
                    a.submission_status === "submitted"
                ).length
              }
            </div>
            <div className="small-caption">Completed</div>

            <div
              className="mt-16"
              style={{ fontSize: "20px", fontWeight: 700 }}
            >
              {
                assignments.filter((a) => a.submission_status === "pending")
                  .length
              }
            </div>
            <div className="small-caption">Pending</div>

            <div className="mt-16 small-caption">
              Completion Rate:{" "}
              <strong>
                {assignments.length > 0
                  ? Math.round(
                      (assignments.filter(
                        (a) => a.submission_status !== "pending"
                      ).length /
                        assignments.length) *
                        100
                    )
                  : 0}
                %
              </strong>
            </div>
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <h2>Course Summary</h2>
          </div>
          <div className="mt-16" style={{ textAlign: "center" }}>
            <div style={{ fontSize: "24px", fontWeight: 700 }}>
              {stats?.courses_enrolled || 0}
            </div>
            <div className="small-caption">Courses Enrolled</div>

            <div
              className="mt-16"
              style={{ fontSize: "24px", fontWeight: 700 }}
            >
              {stats?.submissions || 0}
            </div>
            <div className="small-caption">Submissions Made</div>

            <div className="mt-16 small-caption">
              Avg Score:{" "}
              <strong>{stats?.average_score?.toFixed(1) || "N/A"}</strong>
            </div>
          </div>
        </section>
      </div>

      {/* BOTTOM: academic records table */}
      <section className="card mt-24">
        <div className="card-header">
          <h2>Enrolled Courses</h2>
        </div>
        <table className="table mt-12">
          <thead>
            <tr>
              <th>Course Code</th>
              <th>Course Name</th>
              <th>Lecturer</th>
              <th>Credits</th>
              <th>Semester</th>
            </tr>
          </thead>
          <tbody>
            {loading ? (
              <tr>
                <td colSpan={5} className="text-muted">
                  Loading...
                </td>
              </tr>
            ) : courses.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-muted">
                  No courses enrolled
                </td>
              </tr>
            ) : (
              courses.map((course) => (
                <tr key={course.id}>
                  <td>{course.code}</td>
                  <td>{course.name}</td>
                  <td>{course.lecturer_name || "N/A"}</td>
                  <td>{course.credits}</td>
                  <td>{course.semester}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </section>
    </>
  );
};

export default StudentDashboardPage;
