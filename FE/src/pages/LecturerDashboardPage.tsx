import { useNavigate } from "react-router-dom";
import { useAuth } from "../contexts/AuthContext";
import { useState, useEffect } from "react";
import { lecturerAPI } from "../services/api";

interface DashboardStats {
  courses_teaching: number;
  total_students: number;
  pending_submissions: number;
  average_rating: number | null;
}

interface CourseInfo {
  id: number;
  code: string;
  name: string;
  enrolled_count: number;
  credits: number;
  semester: string;
  lecturer_name: string | null;
  description: string | null;
}

interface AtRiskStudent {
  user_id: number;
  student_id: number;
  full_name: string;
  current_gpa: number;
  risk_factors: string[];
  courses: string[];
  email: string | null;
}

interface AttendanceStat {
  course_id: number;
  course_code: string;
  course_name: string;
  attendance_rate: number;
}

interface ScoreStat {
  course_id: number;
  course_code: string;
  course_name: string;
  avg_quiz_score: number;
  avg_assignment_score: number;
}

export default function LecturerDashboardPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [stats, setStats] = useState<DashboardStats>({
    courses_teaching: 0,
    total_students: 0,
    pending_submissions: 0,
    average_rating: null,
  });
  const [courses, setCourses] = useState<CourseInfo[]>([]);
  const [atRiskStudents, setAtRiskStudents] = useState<AtRiskStudent[]>([]);
  const [attendanceStats, setAttendanceStats] = useState<AttendanceStat[]>([]);
  const [scoreStats, setScoreStats] = useState<ScoreStat[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      if (!user?.user_id) return;
      
      try {
        setLoading(true);
        const [statsRes, coursesRes, atRiskRes, attendanceRes, scoreRes] = await Promise.all([
          lecturerAPI.getDashboard(user.user_id),
          lecturerAPI.getCourses(user.user_id),
          lecturerAPI.getAtRiskStudents(user.user_id),
          lecturerAPI.getAttendanceStats(user.user_id),
          lecturerAPI.getScoreStats(user.user_id),
        ]);
        
        const statsData = statsRes.data || statsRes;
        setStats({
          courses_teaching: statsData.courses_teaching || 0,
          total_students: statsData.total_students || 0,
          pending_submissions: statsData.pending_submissions || 0,
          average_rating: statsData.average_rating || null,
        });
        
        const coursesData = coursesRes.data || coursesRes;
        setCourses(Array.isArray(coursesData) ? coursesData : []);
        
        const atRiskData = atRiskRes.data || atRiskRes;
        setAtRiskStudents(Array.isArray(atRiskData) ? atRiskData : []);
        
        const attendanceData = attendanceRes.data || attendanceRes;
        setAttendanceStats(Array.isArray(attendanceData) ? attendanceData : []);
        
        const scoreData = scoreRes.data || scoreRes;
        setScoreStats(Array.isArray(scoreData) ? scoreData : []);
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboardData();
  }, [user?.user_id]);

  const handleMessageStudent = (studentUserId: number) => {
    navigate("/lecturer-feedback", { state: { selectedStudentId: studentUserId } });
  };

  const maxAttendance = 100;
  const maxScore = 100;

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">Dashboard</h1>

        {/* top summary cards */}
        <div className="grid grid-4 mt-16">
          <div className="card">
            <div className="small-caption">Courses Teaching</div>
            <h2 style={{ fontSize: "28px" }}>{loading ? "..." : stats.courses_teaching}</h2>
            <div className="small-caption">Active courses</div>
          </div>
          <div className="card">
            <div className="small-caption">Total Students</div>
            <h2 style={{ fontSize: "28px" }}>{loading ? "..." : stats.total_students}</h2>
            <div className="small-caption">Currently enrolled</div>
          </div>
          <div className="card">
            <div className="small-caption">Average Rating</div>
            <h2 style={{ fontSize: "28px" }}>{loading ? "..." : stats.average_rating ? `${stats.average_rating.toFixed(1)}/5` : "N/A"}</h2>
            <div className="small-caption">From student feedback</div>
          </div>
          <div className="card">
            <div className="small-caption">At-Risk Students</div>
            <h2 style={{ fontSize: "28px", color: atRiskStudents.length > 0 ? "#dc2626" : "inherit" }}>
              {loading ? "..." : atRiskStudents.length}
            </h2>
            <div className="small-caption">Need attention</div>
          </div>
        </div>

        {/* At-Risk Students Section - PROMINENT */}
        {atRiskStudents.length > 0 && (
          <section className="card mt-24" style={{ borderLeft: "4px solid #dc2626" }}>
            <div className="card-header">
              <h2 style={{ color: "#dc2626" }}>⚠️ At-Risk Students</h2>
              <span className="small-caption">{atRiskStudents.length} student(s) need attention</span>
            </div>
            <div className="mt-16">
              {atRiskStudents.map((student) => (
                <div
                  key={student.user_id}
                  className="card card--flat"
                  style={{ 
                    backgroundColor: "#fef2f2", 
                    marginBottom: "12px",
                    display: "flex",
                    justifyContent: "space-between",
                    alignItems: "center"
                  }}
                >
                  <div style={{ flex: 1 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                      <strong style={{ fontSize: "16px" }}>{student.full_name}</strong>
                      <span className="small-caption" style={{ background: "#fee2e2", padding: "2px 8px", borderRadius: "4px" }}>
                        GPA: {student.current_gpa.toFixed(2)}
                      </span>
                    </div>
                    <div className="small-caption mt-8" style={{ color: "#dc2626" }}>
                      {student.risk_factors.join(" • ")}
                    </div>
                    <div className="small-caption mt-4">
                      Courses: {student.courses.join(", ")}
                    </div>
                  </div>
                  <button
                    className="btn btn-primary"
                    style={{ backgroundColor: "#dc2626", borderColor: "#dc2626" }}
                    onClick={() => handleMessageStudent(student.user_id)}
                  >
                    💬 Message
                  </button>
                </div>
              ))}
            </div>
          </section>
        )}

        {/* Charts Row: Attendance Rate + Score Stats */}
        <div className="grid grid-2 mt-24">
          {/* Attendance Rate Chart */}
          <section className="card">
            <div className="card-header">
              <h2>Student Attendance Rate</h2>
            </div>
            <p className="small-caption mt-4">Attendance percentage per course</p>
            <div className="mt-8">
              {attendanceStats.length === 0 ? (
                <p className="small-caption">No attendance data available.</p>
              ) : (
                <svg viewBox="0 0 380 230" role="img" aria-label="Attendance bar chart" style={{ width: "100%" }}>
                  {[0, 25, 50, 75, 100].map((tick) => {
                    const yBase = 190;
                    const chartHeight = 140;
                    const y = yBase - (tick / maxAttendance) * chartHeight;
                    return (
                      <g key={tick}>
                        <line x1="60" y1={y} x2="340" y2={y} stroke="#e5e7eb" strokeWidth="1" />
                        <text x="50" y={y + 4} textAnchor="end" className="small-caption" fill="#111827">{tick}%</text>
                      </g>
                    );
                  })}
                  <line x1="60" y1="50" x2="60" y2="190" stroke="#000" strokeWidth="1" />
                  <line x1="60" y1="190" x2="340" y2="190" stroke="#000" strokeWidth="1" />
                  {attendanceStats.slice(0, 5).map((stat, index) => {
                    const barWidth = 40;
                    const gap = 16;
                    const x = 70 + index * (barWidth + gap);
                    const yBase = 190;
                    const chartHeight = 140;
                    const barHeight = (stat.attendance_rate / maxAttendance) * chartHeight;
                    const y = yBase - barHeight;
                    const color = stat.attendance_rate >= 80 ? "#22c55e" : stat.attendance_rate >= 60 ? "#eab308" : "#dc2626";
                    return (
                      <g key={stat.course_id}>
                        <rect x={x} y={y} width={barWidth} height={barHeight} rx="6" fill={color} />
                        <text x={x + barWidth / 2} y="210" textAnchor="middle" className="small-caption" fill="#4b5563" style={{ fontSize: "9px" }}>{stat.course_code}</text>
                        <text x={x + barWidth / 2} y={y - 6} textAnchor="middle" className="small-caption" fill="#111827">{stat.attendance_rate}%</text>
                      </g>
                    );
                  })}
                </svg>
              )}
            </div>
          </section>

          {/* Average Scores Chart */}
          <section className="card">
            <div className="card-header">
              <h2>Average Scores by Course</h2>
            </div>
            <p className="small-caption mt-4">Quiz (blue) and Assignment (orange) averages</p>
            <div className="mt-8">
              {scoreStats.length === 0 ? (
                <p className="small-caption">No score data available.</p>
              ) : (
                <svg viewBox="0 0 380 230" role="img" aria-label="Score bar chart" style={{ width: "100%" }}>
                  {[0, 25, 50, 75, 100].map((tick) => {
                    const yBase = 190;
                    const chartHeight = 140;
                    const y = yBase - (tick / maxScore) * chartHeight;
                    return (
                      <g key={tick}>
                        <line x1="60" y1={y} x2="340" y2={y} stroke="#e5e7eb" strokeWidth="1" />
                        <text x="50" y={y + 4} textAnchor="end" className="small-caption" fill="#111827">{tick}%</text>
                      </g>
                    );
                  })}
                  <line x1="60" y1="50" x2="60" y2="190" stroke="#000" strokeWidth="1" />
                  <line x1="60" y1="190" x2="340" y2="190" stroke="#000" strokeWidth="1" />
                  {scoreStats.slice(0, 4).map((stat, index) => {
                    const groupWidth = 60;
                    const barWidth = 24;
                    const gap = 20;
                    const groupX = 70 + index * (groupWidth + gap);
                    const yBase = 190;
                    const chartHeight = 140;
                    const quizHeight = (stat.avg_quiz_score / maxScore) * chartHeight;
                    const quizY = yBase - quizHeight;
                    const assignmentHeight = (stat.avg_assignment_score / maxScore) * chartHeight;
                    const assignmentY = yBase - assignmentHeight;
                    return (
                      <g key={stat.course_id}>
                        <rect x={groupX} y={quizY} width={barWidth} height={quizHeight} rx="4" fill="#3b82f6" />
                        <text x={groupX + barWidth / 2} y={quizY - 4} textAnchor="middle" style={{ fontSize: "9px" }} fill="#111827">{stat.avg_quiz_score.toFixed(0)}</text>
                        <rect x={groupX + barWidth + 4} y={assignmentY} width={barWidth} height={assignmentHeight} rx="4" fill="#f59e0b" />
                        <text x={groupX + barWidth + 4 + barWidth / 2} y={assignmentY - 4} textAnchor="middle" style={{ fontSize: "9px" }} fill="#111827">{stat.avg_assignment_score.toFixed(0)}</text>
                        <text x={groupX + groupWidth / 2} y="210" textAnchor="middle" className="small-caption" fill="#4b5563" style={{ fontSize: "9px" }}>{stat.course_code}</text>
                      </g>
                    );
                  })}
                  <rect x="280" y="30" width="12" height="12" fill="#3b82f6" rx="2" />
                  <text x="296" y="40" style={{ fontSize: "10px" }} fill="#111827">Quiz</text>
                  <rect x="280" y="48" width="12" height="12" fill="#f59e0b" rx="2" />
                  <text x="296" y="58" style={{ fontSize: "10px" }} fill="#111827">Assignment</text>
                </svg>
              )}
            </div>
          </section>
        </div>

        {/* My classes table */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>My Classes</h2>
          </div>
          <table className="table mt-8">
            <thead>
              <tr>
                <th>Code</th>
                <th>Course Name</th>
                <th>Enrolled</th>
                <th>Credits</th>
                <th>Semester</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {loading ? (
                <tr><td colSpan={6}>Loading...</td></tr>
              ) : courses.length === 0 ? (
                <tr><td colSpan={6}>No courses assigned.</td></tr>
              ) : (
                courses.map((course) => (
                  <tr key={course.id}>
                    <td>{course.code}</td>
                    <td>{course.name}</td>
                    <td>{course.enrolled_count || 0}</td>
                    <td>{course.credits}</td>
                    <td>{course.semester}</td>
                    <td>
                      <button 
                        className="btn btn-secondary" 
                        style={{ padding: "4px 12px", fontSize: "12px" }}
                        onClick={() => navigate(`/lecturer-course/${course.id}`)}
                      >
                        View Details
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
}
