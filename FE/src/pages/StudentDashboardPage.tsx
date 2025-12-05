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

const gpaData = [
  { semester: "221", semesterGPA: 2.6, overallGPA: 2.8 },
  { semester: "222", semesterGPA: 3.0, overallGPA: 3.0 },
  { semester: "223", semesterGPA: 3.1, overallGPA: 3.1 },
  { semester: "231", semesterGPA: 3.2, overallGPA: 3.2 },
  { semester: "232", semesterGPA: 3.3, overallGPA: 3.3 },
  { semester: "233", semesterGPA: 3.7, overallGPA: 3.4 },
];

const StudentDashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [showGoalModal, setShowGoalModal] = useState(false);
  const [targetGpa, setTargetGpa] = useState<string>("");
  const [savingGoal, setSavingGoal] = useState(false);

  useEffect(() => {
    const fetchData = async () => {
      if (!user?.user_id) return;
      
      try {
        setLoading(true);
        const [dashboardRes, assignmentsRes, coursesRes] = await Promise.all([
          studentAPI.getDashboard(user.user_id),
          studentAPI.getAssignments(user.user_id),
          studentAPI.getCourses(user.user_id)
        ]);
        setStats(dashboardRes.data);
        setAssignments(assignmentsRes.data || []);
        setCourses(coursesRes.data || []);
        // Set initial target GPA value
        if (dashboardRes.data?.target_gpa) {
          setTargetGpa(dashboardRes.data.target_gpa.toString());
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

  // Get user initials for avatar
  const getInitials = (name: string) => {
    if (!name) return "A";
    const parts = name.split(" ");
    if (parts.length >= 1) {
      return parts[0][0];
    }
    return name[0];
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
    .filter(a => a.submission_status !== "graded")
    .sort((a, b) => new Date(a.deadline).getTime() - new Date(b.deadline).getTime())
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
              <p className="small-caption">Entrance Year: 2022</p>
              <p className="small-caption">Student ID: {user?.student_id || "N/A"}</p>
              <p className="small-caption">Major: {user?.major || "N/A"}</p>
              <p className="small-caption">Current GPA: {stats?.current_gpa?.toFixed(2) || user?.current_gpa?.toFixed(2) || "N/A"}</p>
            </div>
          </div>

          <div className="mt-24">
            <h3 style={{ fontSize: "16px", marginBottom: "4px" }}>
              About Me
            </h3>
            <p className="text-muted">
              Passionate Computer Science student with a keen interest in AI
              and Machine Learning. Actively involved in coding clubs and
              academic research.
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
                const status = getDeadlineStatus(assignment.deadline, assignment.submission_status);
                const course = courses.find(c => c.id === assignment.course_id);
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
                        <div className="small-caption">{course?.code || `Course ${assignment.course_id}`}</div>
                      </div>
                      <div style={{ textAlign: "right" }}>
                        <div className="small-caption">Due {formatDate(assignment.deadline)}</div>
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

        <div
          className="mt-16"
          style={{
            display: "flex",
            justifyContent: "space-between",
            alignItems: "center",
          }}
        >
          <div className="small-caption">
            Current Goal: <strong>{stats?.target_gpa?.toFixed(1) || "Not set"}</strong>
            <button
              className="btn btn-secondary"
              style={{ marginLeft: "8px" }}
              onClick={() => setShowGoalModal(true)}
            >
              Set goal
            </button>
            <button
              className="btn btn-primary"
              style={{ marginLeft: "4px" }}
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
          <div
            className="mt-16"
            style={{ textAlign: "center" }}
          >
            <div style={{ fontSize: "28px", fontWeight: 700 }}>
              {assignments.filter(a => a.submission_status === "graded" || a.submission_status === "submitted").length}
            </div>
            <div className="small-caption">Completed</div>

            <div
              className="mt-16"
              style={{ fontSize: "20px", fontWeight: 700 }}
            >
              {assignments.filter(a => a.submission_status === "pending").length}
            </div>
            <div className="small-caption">Pending</div>

            <div className="mt-16 small-caption">
              Completion Rate: <strong>
                {assignments.length > 0 
                  ? Math.round((assignments.filter(a => a.submission_status !== "pending").length / assignments.length) * 100)
                  : 0}%
              </strong>
            </div>
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <h2>Course Summary</h2>
          </div>
          <div
            className="mt-16"
            style={{ textAlign: "center" }}
          >
            <div style={{ fontSize: "24px", fontWeight: 700 }}>{stats?.courses_enrolled || 0}</div>
            <div className="small-caption">Courses Enrolled</div>

            <div
              className="mt-16"
              style={{ fontSize: "24px", fontWeight: 700 }}
            >
              {stats?.submissions || 0}
            </div>
            <div className="small-caption">Submissions Made</div>

            <div className="mt-16 small-caption">
              Avg Score: <strong>{stats?.average_score?.toFixed(1) || "N/A"}</strong>
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
                <td colSpan={5} className="text-muted">Loading...</td>
              </tr>
            ) : courses.length === 0 ? (
              <tr>
                <td colSpan={5} className="text-muted">No courses enrolled</td>
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
