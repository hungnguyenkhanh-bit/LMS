export default function LecturerFeedbackPage() {
  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">Feedback</h1>

        <div className="layout-chat mt-16">
          {/* left: Conversations list */}
          <aside className="chat-sidebar">
            <div className="chat-sidebar-header">
              <input
                className="form-control"
                type="text"
                placeholder="Search students..."
              />
            </div>
            <ul className="chat-list">
              <li className="chat-list-item chat-list-item--active">
                <span>Alice Johnson</span>
                <span className="small-caption">10:30 AM</span>
              </li>
              {/* thêm item */}
            </ul>
          </aside>

          {/* right: conversation + avg ratings */}
          <section style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div className="chat-main">
              <div className="card-header" style={{ marginBottom: "12px" }}>
                <h2>Conversation with Alice Johnson</h2>
              </div>
              <div className="chat-messages">
                <div className="chat-bubble chat-bubble--other">
                  Hello Dr. Smith, I have a question about Assignment 3.
                </div>
                <div className="chat-bubble chat-bubble--me">
                  Certainly, Alice. What specifically are you having trouble with?
                </div>
                {/* ... */}
              </div>
              <div className="chat-input-row">
                <input
                  className="form-control"
                  type="text"
                  placeholder="Type your message here..."
                />
                <button className="btn btn-primary">Send</button>
              </div>
            </div>

            {/* average ratings panel */}
            <section className="card">
              <div className="card-header">
                <h2>Average Ratings</h2>
                <span style={{ fontSize: "24px", color: "#f59e0b" }}>★ 4.7</span>
              </div>
              <div className="mt-12">
                <div
                  className="card card--flat"
                  style={{ background: "#fde68a", marginBottom: "8px" }}
                >
                  <strong>John Doe - From Introduction to Programming (CO1003)</strong>
                  <p className="mt-8 text-muted">
                    Dr. Smith is an excellent lecturer! Always clear and helpful...
                  </p>
                </div>
              </div>
            </section>
          </section>
        </div>
      </div>
    </div>
  );
}
