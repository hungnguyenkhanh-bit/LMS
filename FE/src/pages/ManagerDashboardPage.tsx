export default function ManagerDashboardPage() {
  const enrollmentLabels = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
  ];
  const currentYearEnrollments = [110, 130, 155, 140, 180, 175, 200, 220, 215, 235, 230, 260];
  const lastYearEnrollments = [90, 110, 135, 130, 165, 170, 190, 205, 200, 220, 215, 230];
  const enrollmentTicks = [90, 135, 180, 225, 270];

  const gradeDistribution = [
    { grade: "A", value: 190 },
    { grade: "B", value: 240 },
    { grade: "C", value: 130 },
    { grade: "D", value: 55 },
    { grade: "F", value: 25 },
  ];
  const gradeTicks = [0, 65, 130, 195, 260];

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">System Overview</h1>

        {/* top summary row */}
        <div className="grid grid-4 mt-16">
          <div className="card">
            <div className="small-caption">Total Faculty</div>
            <h2>120</h2>
          </div>
          <div className="card">
            <div className="small-caption">Total Enrollments</div>
            <h2>1,850</h2>
          </div>
          <div className="card">
            <div className="small-caption">Active Courses</div>
            <h2>75</h2>
          </div>
          <div className="card">
            <div className="small-caption">Completion Rate</div>
            <h2>88.2%</h2>
          </div>
        </div>

        {/* middle charts */}
        <div className="grid grid-2 mt-24">
          <section className="card">
            <div className="card-header">
              <h2>Enrollment Trends</h2>
            </div>
            <p className="small-caption mt-4">
              Monthly student enrollment figures, indicating growth and seasonal patterns.
            </p>
            <div className="mt-8">
              <svg
                viewBox="0 0 420 240"
                role="img"
                aria-label="Enrollment trend line chart"
                style={{ width: "100%" }}
              >
                {enrollmentTicks.map((tick) => {
                  const yBase = 200;
                  const chartHeight = 140;
                  const y =
                    yBase - ((tick - enrollmentTicks[0]) / (enrollmentTicks[enrollmentTicks.length - 1] - enrollmentTicks[0])) * chartHeight;
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
                <polyline
                  fill="none"
                  stroke="#2563eb"
                  strokeWidth="3"
                  points={currentYearEnrollments
                    .map((value, index) => {
                      const xStep = 320 / (enrollmentLabels.length - 1);
                      const x = 60 + index * xStep;
                      const yBase = 200;
                      const chartHeight = 140;
                      const y =
                        yBase -
                        ((value - enrollmentTicks[0]) /
                          (enrollmentTicks[enrollmentTicks.length - 1] - enrollmentTicks[0])) *
                          chartHeight;
                      return `${x},${y}`;
                    })
                    .join(" ")}
                />
                <polyline
                  fill="none"
                  stroke="#ec4899"
                  strokeWidth="3"
                  points={lastYearEnrollments
                    .map((value, index) => {
                      const xStep = 320 / (enrollmentLabels.length - 1);
                      const x = 60 + index * xStep;
                      const yBase = 200;
                      const chartHeight = 140;
                      const y =
                        yBase -
                        ((value - enrollmentTicks[0]) /
                          (enrollmentTicks[enrollmentTicks.length - 1] - enrollmentTicks[0])) *
                          chartHeight;
                      return `${x},${y}`;
                    })
                    .join(" ")}
                />
                {enrollmentLabels.map((label, index) => {
                  const xStep = 320 / (enrollmentLabels.length - 1);
                  const x = 60 + index * xStep;
                  return (
                    <text
                      key={label}
                      x={x}
                      y={220}
                      textAnchor="middle"
                      className="small-caption"
                      fill="#4b5563"
                    >
                      {label}
                    </text>
                  );
                })}
              </svg>
            </div>
            <div className="mt-12" style={{ display: "flex", gap: "16px", alignItems: "center" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span
                  style={{
                    display: "inline-block",
                    width: "10px",
                    height: "10px",
                    borderRadius: "999px",
                    background: "#2563eb",
                  }}
                ></span>
                <span className="small-caption">Current Year Enrollments</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span
                  style={{
                    display: "inline-block",
                    width: "10px",
                    height: "10px",
                    borderRadius: "999px",
                    background: "#ec4899",
                  }}
                ></span>
                <span className="small-caption">Last Year Enrollments</span>
              </div>
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
              <h2>Faculty Workload Distribution</h2>
            </div>
            <table className="table mt-8">
              <thead>
                <tr>
                  <th>Lecturer</th>
                  <th>Course</th>
                  <th>Active Students</th>
                  <th>Avg. Rating</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>Dr. Jane Doe</td>
                  <td>Advanced Algorithms</td>
                  <td>45</td>
                  <td>4.8</td>
                </tr>
              </tbody>
            </table>
          </section>
          <section className="card">
            <div className="card-header">
              <h2>Recent System Activities</h2>
            </div>
            <div className="mt-8 small-caption">
              {/* list of activities */}
              <p>
                <strong>Dr. Jane Doe</strong> uploaded new assignment for Advanced
                Algorithms · 2 hours ago
              </p>
              <p className="mt-8">
                <strong>Student A. Sharma</strong> submitted “Database Project” · 4
                hours ago
              </p>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
