export default function MyCoursesPage() {
  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">My Courses</h1>

        <div className="grid grid-3 mt-24">
          <article className="card">
            <h2 style={{ fontSize: "20px" }}>Introduction to Programming</h2>
            <div className="small-caption">Course ID: CO1002</div>
            <div
              className="mt-16"
              style={{
                height: "140px",
                background: "#111827",
                borderRadius: "14px",
              }}
            ></div>
            <button
              className="btn btn-primary mt-16"
              style={{ width: "100%" }}
            >
              Access Course
            </button>
          </article>
          {/* thêm các card course khác */}
        </div>
      </div>
    </div>
  );
}
