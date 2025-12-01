export default function StudentFeedbackPage() {
  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">Feedback</h1>

        {/* Course Feedback */}
        <section className="card mt-16">
          <div className="card-header">
            <h2>Student's Course Feedback</h2>
          </div>
          <p className="card-subtitle mb-16">Provide your feedback for a course.</p>
          <div className="card card--flat" style={{ background: "#fde68a" }}>
            <div className="form-group">
              <label className="form-label">Select Course</label>
              <select className="form-control">
                <option>CO106 - Data Structures and Algorithms (CO1032)</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Session Rating</label>
              <div>⭐ ⭐ ⭐ ⭐ ☆</div>
            </div>
            <div className="form-group">
              <label className="form-label">Comments</label>
              <textarea className="form-control"></textarea>
            </div>
            <button className="btn btn-primary">Submit Feedback</button>
          </div>
        </section>

        {/* Feedback history */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Feedback History</h2>
          </div>
          <div className="mt-16">
            <div
              className="card card--flat"
              style={{ background: "#fde68a", marginBottom: "8px" }}
            >
              <div className="small-caption">
                CO1002 · Submitted on 2024-05-16 ·{" "}
                <span className="badge badge-success">Good</span>
              </div>
              <p className="mt-8 text-muted">
                The session was very insightful and promoted active learning...
              </p>
              <div className="mt-8">
                <span className="badge badge-warning">Engaging Content</span>
                <span className="badge badge-warning">Clear Explanations</span>
              </div>
              <div className="text-right mt-8">
                <button className="btn btn-danger">Edit feedback</button>
              </div>
            </div>
          </div>
        </section>

        {/* Direct messaging with professors */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Direct Messaging with Professors</h2>
          </div>
          <div className="mt-16">
            <div className="form-group">
              <label className="form-label">Select Professor</label>
              <select className="form-control">
                <option>Dr. Jane Doe - Computer Science</option>
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Your Feedback</label>
              <textarea className="form-control"></textarea>
            </div>
            <button className="btn btn-primary">Send Message</button>

            <div className="mt-24">
              <h3 style={{ fontSize: "18px" }}>Professor Messages</h3>
              <div className="mt-12">
                <div className="card card--flat mb-8">
                  <strong>Dr. Jane Doe</strong>
                  <div className="small-caption">2024-06-01, 10:30 AM</div>
                  <p className="mt-8 text-muted">
                    Thank you for your valuable feedback! I appreciate your
                    honesty.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  );
}
