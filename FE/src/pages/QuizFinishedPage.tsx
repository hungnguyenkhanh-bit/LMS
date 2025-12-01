export default function QuizFinishedPage() {
  return (
    <div className="app-main">
      <div className="app-main-inner">
        <section className="card" style={{ padding: "48px" }}>
          <h1
            className="section-title"
            style={{ fontSize: "36px", textAlign: "center" }}
          >
            Quiz Completed
          </h1>
          <p
            style={{
              fontSize: "24px",
              fontWeight: 700,
              textAlign: "center",
              marginTop: "8px",
            }}
          >
            Your Score: 5/10
          </p>

          <div className="grid grid-2 mt-24">
            <div>
              <div className="small-caption">Duration</div>
              <p className="text-muted">39 min 55 secs</p>
            </div>
            <div>
              <div className="small-caption">Correct Answer</div>
              <p className="text-muted">20/40</p>
            </div>
          </div>

          <div
            className="mt-32"
            style={{ display: "flex", justifyContent: "center", gap: "16px" }}
          >
            <button className="btn btn-primary">Review</button>
            <button className="btn btn-secondary">Return</button>
          </div>
        </section>
      </div>
    </div>
  );
}
