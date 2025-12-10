import { useState, useEffect } from "react";
import { managerAPI } from "../services/api";

interface DashboardStats {
  total_students: number;
  total_lecturers: number;
  total_courses: number;
  active_enrollments: number;
  average_gpa: number | null;
}

interface LecturerInfo {
  user_id: number;
  title: string;
  full_name: string;
  department: string;
  email: string | null;
  average_rating?: number;
}

interface CourseInfo {
  id: number;
  code: string;
  name: string;
  credits: number;
  semester: string;
  capacity: number;
  lecturer_name: string | null;
  enrolled_count: number;
  average_grade?: number;
}

interface GradeDistribution {
  grade: string;
  value: number;
}

export default function ManagerDashboardPage() {
  const [stats, setStats] = useState<DashboardStats>({
    total_students: 0,
    total_lecturers: 0,
    total_courses: 0,
    active_enrollments: 0,
    average_gpa: null,
  });
  const [lecturers, setLecturers] = useState<LecturerInfo[]>([]);
  const [courses, setCourses] = useState<CourseInfo[]>([]);
  const [gradeDistribution, setGradeDistribution] = useState<GradeDistribution[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const [statsRes, lecturersRes, coursesRes, gpaRes] = await Promise.all([
          managerAPI.getDashboard(),
          managerAPI.getLecturers(),
          managerAPI.getCourses(),
          managerAPI.getGPADistribution(),
        ]);
        
        const statsData = statsRes.data || statsRes;
        setStats({
          total_students: statsData.total_students || 0,
          total_lecturers: statsData.total_lecturers || 0,
          total_courses: statsData.total_courses || 0,
          active_enrollments: statsData.active_enrollments || 0,
          average_gpa: statsData.average_gpa,
        });
        
        const lecturersData = lecturersRes.data || lecturersRes;
        setLecturers(Array.isArray(lecturersData) ? lecturersData : []);
        
        const coursesData = coursesRes.data || coursesRes;
        setCourses(Array.isArray(coursesData) ? coursesData : []);
        
        // Convert GPA distribution to grade distribution for chart
        const gpaData = gpaRes.data || gpaRes;
        if (gpaData && typeof gpaData === 'object') {
          const gradeMap: GradeDistribution[] = [
            { grade: "A", value: (gpaData["3.5-4.0"] || 0) },
            { grade: "B", value: (gpaData["3.0-3.5"] || 0) },
            { grade: "C", value: (gpaData["2.5-3.0"] || 0) },
            { grade: "D", value: (gpaData["2.0-2.5"] || 0) },
            { grade: "F", value: (gpaData["0.0-1.0"] || 0) + (gpaData["1.0-2.0"] || 0) },
          ];
          setGradeDistribution(gradeMap);
        }
      } catch (err) {
        console.error("Failed to load dashboard data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  const enrollmentTicks = [0, 10, 20, 30, 40];
  
  // Calculate max grade value for chart scaling
  const maxGradeValue = Math.max(...gradeDistribution.map(g => g.value), 10);
  const gradeTicks = [0, Math.ceil(maxGradeValue / 4), Math.ceil(maxGradeValue / 2), Math.ceil(maxGradeValue * 3 / 4), maxGradeValue];

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">System Overview</h1>

        {/* top summary row */}
        <div className="grid grid-4 mt-16">
          <div className="card">
            <div className="small-caption">Total Students</div>
            <h2>{loading ? "..." : stats.total_students}</h2>
          </div>
          <div className="card">
            <div className="small-caption">Total Lecturers</div>
            <h2>{loading ? "..." : stats.total_lecturers}</h2>
          </div>
          <div className="card">
            <div className="small-caption">Active Courses</div>
            <h2>{loading ? "..." : stats.total_courses}</h2>
          </div>
          <div className="card">
            <div className="small-caption">Active Enrollments</div>
            <h2>{loading ? "..." : stats.active_enrollments}</h2>
          </div>
        </div>

        {/* middle charts */}
        <div className="grid grid-2 mt-24">
          <section className="card">
            <div className="card-header">
              <h2>Courses by Enrollment</h2>
            </div>
            <p className="small-caption mt-4">
              Number of students enrolled per course.
            </p>
            <div className="mt-8">
              <svg
                viewBox="0 0 420 240"
                role="img"
                aria-label="Enrollment bar chart"
                style={{ width: "100%" }}
              >
                {enrollmentTicks.map((tick) => {
                  const yBase = 200;
                  const chartHeight = 140;
                  const maxTick = enrollmentTicks[enrollmentTicks.length - 1] || 40;
                  const y = yBase - (tick / maxTick) * chartHeight;
                  return (
                    <g key={tick}>
                      <line
                        x1="60"
                        y1={y}
                        x2="380"
                        y2={y}
                        stroke="#e5e7eb"
                        strokeWidth="1"
                        strokeDasharray="4 4"
                      />
                      <text
                        x="50"
                        y={y + 4}
                        textAnchor="end"
                        className="small-caption"
                        fill="#111827"
                      >
                        {tick}
                      </text>
                    </g>
                  );
                })}
                <line x1="60" y1="60" x2="60" y2="200" stroke="#000" strokeWidth="1" />
                <line x1="60" y1="200" x2="380" y2="200" stroke="#000" strokeWidth="1" />
                {courses.slice(0, 6).map((course, index) => {
                  const barWidth = 36;
                  const gap = 16;
                  const x = 70 + index * (barWidth + gap);
                  const yBase = 200;
                  const chartHeight = 140;
                  const maxTick = enrollmentTicks[enrollmentTicks.length - 1] || 40;
                  const barHeight = ((course.enrolled_count || 0) / maxTick) * chartHeight;
                  const y = yBase - barHeight;
                  return (
                    <g key={course.id}>
                      <rect
                        x={x}
                        y={y}
                        width={barWidth}
                        height={barHeight}
                        rx="6"
                        fill="#2563eb"
                      />
                      <text
                        x={x + barWidth / 2}
                        y={220}
                        textAnchor="middle"
                        className="small-caption"
                        fill="#4b5563"
                        style={{ fontSize: "10px" }}
                      >
                        {course.code}
                      </text>
                      <text
                        x={x + barWidth / 2}
                        y={y - 6}
                        textAnchor="middle"
                        className="small-caption"
                        fill="#111827"
                      >
                        {course.enrolled_count || 0}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </section>
          <section className="card">
            <div className="card-header">
              <h2>Overall Course Grade Distribution</h2>
            </div>
            <p className="small-caption mt-4">Student Count</p>
            <div className="mt-8">
              <svg
                viewBox="0 0 380 230"
                role="img"
                aria-label="Grade distribution bar chart"
                style={{ width: "100%" }}
              >
                {gradeTicks.map((tick) => {
                  const yBase = 190;
                  const chartHeight = 140;
                  const y = yBase - (tick / gradeTicks[gradeTicks.length - 1]) * chartHeight;
                  return (
                    <g key={tick}>
                      <line
                        x1="60"
                        y1={y}
                        x2="340"
                        y2={y}
                        stroke="#e5e7eb"
                        strokeWidth="1"
                      />
                      <text
                        x="50"
                        y={y + 4}
                        textAnchor="end"
                        className="small-caption"
                        fill="#111827"
                      >
                        {tick}
                      </text>
                    </g>
                  );
                })}
                <line x1="60" y1="50" x2="60" y2="190" stroke="#000" strokeWidth="1" />
                <line x1="60" y1="190" x2="340" y2="190" stroke="#000" strokeWidth="1" />
                {gradeDistribution.map((item, index) => {
                  const barWidth = 36;
                  const gap = 20;
                  const x = 70 + index * (barWidth + gap);
                  const yBase = 190;
                  const chartHeight = 140;
                  const barHeight = (item.value / gradeTicks[gradeTicks.length - 1]) * chartHeight;
                  const y = yBase - barHeight;
                  return (
                    <g key={item.grade}>
                      <rect
                        x={x}
                        y={y}
                        width={barWidth}
                        height={barHeight}
                        rx="6"
                        fill="#6ab8de"
                      />
                      <text
                        x={x + barWidth / 2}
                        y="210"
                        textAnchor="middle"
                        className="small-caption"
                        fill="#4b5563"
                      >
                        {item.grade}
                      </text>
                      <text
                        x={x + barWidth / 2}
                        y={y - 6}
                        textAnchor="middle"
                        className="small-caption"
                        fill="#111827"
                      >
                        {item.value}
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </section>
        </div>

        {/* bottom row */}
        <div className="grid grid-2 mt-24">
          <section className="card">
            <div className="card-header">
              <h2>Faculty Members</h2>
            </div>
            <table className="table mt-8">
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Department</th>
                  <th>Email</th>
                  <th>Avg Rating</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={4}>Loading...</td>
                  </tr>
                ) : lecturers.length === 0 ? (
                  <tr>
                    <td colSpan={4}>No faculty data available.</td>
                  </tr>
                ) : (
                  lecturers.slice(0, 5).map((lecturer) => (
                    <tr key={lecturer.user_id}>
                      <td>{lecturer.full_name}</td>
                      <td>{lecturer.department}</td>
                      <td>{lecturer.email || "N/A"}</td>
                      <td>
                        {lecturer.average_rating !== undefined && lecturer.average_rating !== null 
                          ? `⭐ ${lecturer.average_rating.toFixed(1)}/5` 
                          : "N/A"}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </section>
          <section className="card">
            <div className="card-header">
              <h2>All Courses</h2>
            </div>
            <table className="table mt-8">
              <thead>
                <tr>
                  <th>Code</th>
                  <th>Name</th>
                  <th>Enrolled</th>
                  <th>Lecturer</th>
                </tr>
              </thead>
              <tbody>
                {loading ? (
                  <tr>
                    <td colSpan={4}>Loading...</td>
                  </tr>
                ) : courses.length === 0 ? (
                  <tr>
                    <td colSpan={4}>No courses available.</td>
                  </tr>
                ) : (
                  courses.slice(0, 5).map((course) => (
                    <tr key={course.id}>
                      <td>{course.code}</td>
                      <td>{course.name}</td>
                      <td>{course.enrolled_count || 0}</td>
                      <td>{course.lecturer_name || "Unassigned"}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </section>
        </div>
      </div>
    </div>
  );
}
