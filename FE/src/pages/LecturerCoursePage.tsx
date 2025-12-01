export default function LecturerCoursePage() {
  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">Introduction to Programming (CO1002)</h1>

        <div className="grid grid-2 mt-24">
          {/* Assignments & Quizzes */}
          <section className="card">
            <div className="card-header">
              <h2>Assignments &amp; Quizzes</h2>
              <a href="#" className="small-caption">
                View all
              </a>
            </div>
            <div className="mt-16">
              <div
                className="card card--flat"
                style={{ background: "#fde68a", marginBottom: "8px" }}
              >
                <strong>Assignment 1: Frontend Frameworks Review</strong>
                <div className="small-caption">Due Sep 06</div>
              </div>
            </div>
            <button className="btn btn-primary mt-16">
              Add New Assignment/Quiz
            </button>
          </section>

          {/* Course Materials */}
          <section className="card">
            <div className="card-header">
              <h2>Course Materials</h2>
              <a href="#" className="small-caption">
                View all
              </a>
            </div>
            <div className="mt-16">
              <div
                className="card card--flat"
                style={{ background: "#fde68a", marginBottom: "8px" }}
              >
                Lecture 1: Introduction to React.pdf
              </div>
            </div>
            <button className="btn btn-primary mt-16">Upload New Material</button>
          </section>
        </div>

        {/* Submissions & grading */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Submissions &amp; Grading</h2>
          </div>
          <table className="table mt-8">
            <thead>
              <tr>
                <th>Student</th>
                <th>Assignment</th>
                <th>Status</th>
                <th>Grading</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td>Alice Johnson</td>
                <td>Assignment 1</td>
                <td>Submitted</td>
                <td>8.0</td>
                <td>
                  <a href="#">View Details</a>
                </td>
              </tr>
            </tbody>
          </table>
          <button className="btn btn-primary mt-16">Give grades</button>
        </section>

        {/* Announcements */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Announcements</h2>
          </div>
          <div className="mt-16">
            <p>
              <strong>Welcome to Advanced Web Development (CS401)!</strong>
            </p>
            <p className="small-caption mb-16">August 28, 2024</p>
            <p className="text-muted mb-16">
              I'm excited to embark on this journey with you...
            </p>
            <hr />
            <div className="mt-16">
              <label className="form-label" htmlFor="new-ann">
                Write a new announcement...
              </label>
              <textarea id="new-ann" className="form-control"></textarea>
            </div>
            <div
              className="mt-16"
              style={{
                display: "flex",
                gap: "12px",
                justifyContent: "flex-end",
              }}
            >
              <button className="btn btn-secondary">Clear</button>
              <button className="btn btn-primary">Post Announcement</button>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
