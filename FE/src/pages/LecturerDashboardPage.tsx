export default function LecturerDashboardPage() {
  const attendanceBars = [
    { label: "Jan", value: 88 },
    { label: "Feb", value: 92 },
    { label: "Mar", value: 86 },
    { label: "Apr", value: 90 },
    { label: "May", value: 94 },
    { label: "Jun", value: 89 },
  ];
  const attendanceTicks = [0, 25, 50, 75, 100];

  const scoreLabels = ["Jan", "Feb", "Mar", "Apr", "May", "Jun"];
  const averageScore = [74, 78, 81, 83, 85, 83];
  const classAverage = [70, 72, 75, 78, 79, 78];
  const scoreTicks = [70, 74, 78, 82, 86];

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">Dashboard</h1>

        {/* top summary cards */}
        <div className="grid grid-4 mt-16">
          <div className="card">
            <div className="small-caption">Total Active Classes</div>
            <h2 style={{ fontSize: "28px" }}>8</h2>
            <div className="small-caption">Across all subjects</div>
          </div>
          <div className="card">
            <div className="small-caption">Total Students</div>
            <h2 style={{ fontSize: "28px" }}>210</h2>
            <div className="small-caption">Currently enrolled</div>
          </div>
          <div className="card">
            <div className="small-caption">Average Class Grade</div>
            <h2 style={{ fontSize: "28px" }}>84.2%</h2>
            <div className="small-caption">Compared to last semester</div>
          </div>
          <div className="card">
            <div className="small-caption">At-Risk Students</div>
            <h2 style={{ fontSize: "28px" }}>7</h2>
            <div className="small-caption">Needs attention</div>
          </div>
        </div>

        {/* middle row: at-risk students + charts */}
        <div className="grid grid-3 mt-24">
          {/* at-risk students list */}
          <section className="card">
            <div className="card-header">
              <h2>At-Risk Students</h2>
            </div>
            <div className="mt-8">
              {/* mỗi student 1 block */}
              <div
                className="card card--flat"
                style={{ backgroundColor: "#fee2e2", marginBottom: "8px" }}
              >
                <strong>Sophia Chen</strong>
                <div className="small-caption">Low scores in Calculus II</div>
              </div>
              {/* ... */}
            </div>
          </section>

          {/* attendance bar chart container */}
          <section className="card">
            <div className="card-header">
              <h2>Student Attendance Rate</h2>
            </div>
            <p className="small-caption mt-4">Monthly attendance percentages</p>
            <div className="mt-8">
              <svg
                viewBox="0 0 380 230"
                role="img"
                aria-label="Attendance bar chart"
                style={{ width: "100%" }}
              >
                {attendanceTicks.map((tick) => {
                  const yBase = 190;
                  const chartHeight = 140;
                  const y = yBase - (tick / 100) * chartHeight;
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
                {attendanceBars.map((item, index) => {
                  const barWidth = 28;
                  const gap = 20;
                  const x = 70 + index * (barWidth + gap);
                  const yBase = 190;
                  const chartHeight = 140;
                  const barHeight = (item.value / 100) * chartHeight;
                  const y = yBase - barHeight;
                  return (
                    <g key={item.label}>
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
                        {item.label}
                      </text>
                      <text
                        x={x + barWidth / 2}
                        y={y - 6}
                        textAnchor="middle"
                        className="small-caption"
                        fill="#111827"
                      >
                        {item.value}%
                      </text>
                    </g>
                  );
                })}
              </svg>
            </div>
          </section>

          {/* avg course score line chart container */}
          <section className="card">
            <div className="card-header">
              <h2>Average Course Score Trend</h2>
            </div>
            <p className="small-caption mt-4">Semester performance comparison</p>
            <div className="mt-8">
              <svg
                viewBox="0 0 380 230"
                role="img"
                aria-label="Average course score line chart"
                style={{ width: "100%" }}
              >
                {scoreTicks.map((tick) => {
                  const yBase = 190;
                  const chartHeight = 140;
                  const y =
                    yBase - ((tick - scoreTicks[0]) / (scoreTicks[scoreTicks.length - 1] - scoreTicks[0])) * chartHeight;
                  return (
                    <g key={tick}>
                      <line
                        x1="60"
                        y1={y}
                        x2="340"
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
                <line x1="60" y1="50" x2="60" y2="190" stroke="#000" strokeWidth="1" />
                <line x1="60" y1="190" x2="340" y2="190" stroke="#000" strokeWidth="1" />
                <polyline
                  fill="none"
                  stroke="#2563eb"
                  strokeWidth="3"
                  points={averageScore
                    .map((value, index) => {
                      const xStep = 280 / (scoreLabels.length - 1);
                      const x = 60 + index * xStep;
                      const yBase = 190;
                      const chartHeight = 140;
                      const y =
                        yBase - ((value - scoreTicks[0]) / (scoreTicks[scoreTicks.length - 1] - scoreTicks[0])) * chartHeight;
                      return `${x},${y}`;
                    })
                    .join(" ")}
                />
                <polyline
                  fill="none"
                  stroke="#ef4444"
                  strokeWidth="3"
                  points={classAverage
                    .map((value, index) => {
                      const xStep = 280 / (scoreLabels.length - 1);
                      const x = 60 + index * xStep;
                      const yBase = 190;
                      const chartHeight = 140;
                      const y =
                        yBase - ((value - scoreTicks[0]) / (scoreTicks[scoreTicks.length - 1] - scoreTicks[0])) * chartHeight;
                      return `${x},${y}`;
                    })
                    .join(" ")}
                />
                {scoreLabels.map((label, index) => {
                  const xStep = 280 / (scoreLabels.length - 1);
                  const x = 60 + index * xStep;
                  return (
                    <text
                      key={label}
                      x={x}
                      y={210}
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
                <span className="small-caption">Average Score</span>
              </div>
              <div style={{ display: "flex", alignItems: "center", gap: "6px" }}>
                <span
                  style={{
                    display: "inline-block",
                    width: "10px",
                    height: "10px",
                    borderRadius: "999px",
                    background: "#ef4444",
                  }}
                ></span>
                <span className="small-caption">Class Average</span>
              </div>
            </div>
          </section>
        </div>

        {/* bottom: My classes table */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>My Classes</h2>
          </div>
          <table className="table mt-8">
            <thead>
              <tr>
                <th>ID</th>
                <th>Class Name</th>
                <th>Enrolled</th>
                <th>Avg. Grade</th>
                <th>Avg. Attendance</th>
                <th>Tag</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>CO1002</td>
                <td>Introduction to Programming</td>
                <td>35</td>
                <td>88%</td>
                <td>88%</td>
                <td>
                  <span className="badge badge-success">Active</span>
                </td>
                <td>
                  <a href="#">View Details</a>
                </td>
              </tr>
              {/* thêm dòng khác */}
            </tbody>
          </table>
        </section>
      </div>
    </div>
  );
}
