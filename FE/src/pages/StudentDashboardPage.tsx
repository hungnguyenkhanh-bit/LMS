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
const gpaData = [
  { semester: "221", semesterGPA: 2.6, overallGPA: 2.8 },
  { semester: "222", semesterGPA: 3.0, overallGPA: 3.0 },
  { semester: "223", semesterGPA: 3.1, overallGPA: 3.1 },
  { semester: "231", semesterGPA: 3.2, overallGPA: 3.2 },
  { semester: "232", semesterGPA: 3.3, overallGPA: 3.3 },
  { semester: "233", semesterGPA: 3.5, overallGPA: 3.4 },
];
const StudentDashboardPage: React.FC = () => {
  return (
    <>
      {/* TOP ROW: PROFILE + UPCOMING DEADLINES */}
      <div className="grid grid-2">
        {/* LEFT: student profile card */}
        <section
        //   className="card"
        //   style={{ backgroundColor: "#6ab8de" }}
        className="card card--profile-dark"
        >
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
              A
            </div>
            <div>
              <h2 style={{ fontSize: "24px", marginBottom: "8px" }}>
                Nguyen Van A
              </h2>
              <p className="small-caption">Entrance Year: 2022</p>
              <p className="small-caption">Student ID: 2253201</p>
              <p className="small-caption">Class: CC22KHM1</p>
              <p className="small-caption">Current GPA: 3.25</p>
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
            {/* mỗi row là 1 deadline */}
            <div
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
                  <strong>Chemistry Lab Report</strong>
                  <div className="small-caption">CHEM101</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="small-caption">Due 2024-05-20</div>
                  <span className="status-pill status-pill--due">due</span>
                </div>
              </div>
            </div>

            {/* ví dụ overdue */}
            <div
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
                  <strong>Math Homework Chapter 5</strong>
                  <div className="small-caption">MATH105</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="small-caption">Due 2024-05-18</div>
                  <span className="status-pill status-pill--overdue">
                    overdue
                  </span>
                </div>
              </div>
            </div>

            {/* ví dụ completed */}
            <div
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
                  <strong>Computer Science Project</strong>
                  <div className="small-caption">CS301 – Phase 1</div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div className="small-caption">Due 2024-05-15</div>
                  <span className="status-pill status-pill--completed">
                    Completed
                  </span>
                </div>
              </div>
            </div>
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

  {/* CHART THẬT Ở ĐÂY */}
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

  {/* Phần scale + buttons giữ nguyên */}
  <div
    className="mt-16"
    style={{
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
    }}
  >
    <div className="small-caption">
      <span style={{ marginRight: "8px" }}>Scale 4</span>
      <span>Scale 10</span>
    </div>
    <div className="small-caption">
      Current Goal: <strong>3.6</strong>
      <button
        className="btn btn-secondary"
        style={{ marginLeft: "8px" }}
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


      {/* MIDDLE: notifications + attendance + syllabus progress */}
      <div className="grid grid-3 mt-24">
        <section className="card">
          <div className="card-header">
            <h2>Recent Notifications</h2>
            <a href="#" className="small-caption">
              View All
            </a>
          </div>
          <div className="mt-12">
            <div className="mb-8">
              <strong style={{ fontSize: "14px" }}>
                New assignment posted in Calculus I.
              </strong>
              <div className="small-caption">2 hours ago</div>
            </div>
            <div className="mb-8">
              <strong style={{ fontSize: "14px" }}>
                Grade updated for Biology Lab.
              </strong>
              <div className="small-caption">1 day ago</div>
            </div>
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <h2>Attendance Summary</h2>
          </div>
          <div
            className="mt-16"
            style={{ textAlign: "center" }}
          >
            <div style={{ fontSize: "28px", fontWeight: 700 }}>105</div>
            <div className="small-caption">Classes Attended</div>

            <div
              className="mt-16"
              style={{ fontSize: "20px", fontWeight: 700 }}
            >
              15
            </div>
            <div className="small-caption">Classes Missed</div>

            <div className="mt-16 small-caption">
              Overall Attendance: <strong>88%</strong>
            </div>
          </div>
        </section>

        <section className="card">
          <div className="card-header">
            <h2>Syllabus progress</h2>
          </div>
          <div
            className="mt-16"
            style={{ textAlign: "center" }}
          >
            <div style={{ fontSize: "24px", fontWeight: 700 }}>68</div>
            <div className="small-caption">Credits passed</div>

            <div
              className="mt-16"
              style={{ fontSize: "24px", fontWeight: 700 }}
            >
              60
            </div>
            <div className="small-caption">Credits remaining</div>

            <div className="mt-16 small-caption">
              Overall progress: <strong>53%</strong>
            </div>
          </div>
        </section>
      </div>

      {/* BOTTOM: academic records table */}
      <section className="card mt-24">
        <div className="card-header">
          <h2>Academic Records Summary</h2>
        </div>
        <table className="table mt-12">
          <thead>
            <tr>
              <th>Course</th>
              <th>Lecturer</th>
              <th>Grade</th>
              <th>Attendance</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Calculus I</td>
              <td>Dr. Evans</td>
              <td>A-</td>
              <td>95%</td>
              <td>
                <span className="status-pill status-pill--passed">
                  Passed
                </span>
              </td>
            </tr>
            <tr>
              <td>Biology 101</td>
              <td>Prof. Miller</td>
              <td>B+</td>
              <td>90%</td>
              <td>
                <span className="status-pill status-pill--passed">
                  Passed
                </span>
              </td>
            </tr>
            <tr>
              <td>English Literature</td>
              <td>Dr. White</td>
              <td>F</td>
              <td>40%</td>
              <td>
                <span className="status-pill status-pill--failed">
                  Failed
                </span>
              </td>
            </tr>
            <tr>
              <td>Introduction to Programming</td>
              <td>Prof. Green</td>
              <td>N/A</td>
              <td>N/A</td>
              <td>
                <span className="status-pill status-pill--ongoing">
                  Ongoing
                </span>
              </td>
            </tr>
            <tr>
              <td>History of Art</td>
              <td>Ms. Brown</td>
              <td>N/A</td>
              <td>N/A</td>
              <td>
                <span className="status-pill status-pill--pending">
                  Pending
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </section>
    </>
  );
};

export default StudentDashboardPage;
