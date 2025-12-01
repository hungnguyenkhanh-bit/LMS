export default function StudentCoursePage() {
  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">
          Data Structures and Algorithms (CO1032)
        </h1>

        {/* Assignments */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Assignments</h2>
          </div>
          <div className="mt-16">
            <div
              className="card card--flat"
              style={{
                marginBottom: "12px",
                background: "#fde68a",
              }}
            >
              <strong>Assignment 1 - BFS, DFS Path Finding implementation</strong>
              <div className="small-caption">
                Deadline: 11:30 AM, October 26, 2024
              </div>
              <div
                className="mt-8"
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "8px",
                }}
              >
                <a href="#">Submit work</a>
              </div>
            </div>
            {/* thêm assignment */}
          </div>
        </section>

        {/* Course material */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Course material</h2>
          </div>
          <div className="mt-16">
            <div
              className="card card--flat"
              style={{ background: "#fde68a", marginBottom: "8px" }}
            >
              Sorting Algorithms
            </div>
            {/* thêm material */}
          </div>
        </section>

        {/* Upcoming quizzes */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Upcoming Quizzes</h2>
          </div>
          <div className="mt-16">
            <div
              className="card card--flat"
              style={{ background: "#fde68a", marginBottom: "8px" }}
            >
              <strong>Selection sort, Bubble sort...</strong>
              <div className="small-caption">
                October 26, 2024 · 10:00 AM – 11:30 AM
              </div>
              <div
                className="mt-8"
                style={{
                  display: "flex",
                  justifyContent: "flex-end",
                  gap: "8px",
                }}
              >
                <a href="#">Attempt quiz</a>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
