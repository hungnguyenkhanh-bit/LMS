export default function QuizTakingPage() {
  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">Quiz: Comparison Based Algorithms</h1>

        <div className="quiz-layout mt-16">
          {/* left: question area */}
          <section className="card">
            <div
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                gap: "12px",
              }}
            >
              <div className="small-caption">Time Left</div>
              <div style={{ fontSize: "32px", fontWeight: 700 }}>05:00</div>
            </div>

            <div className="mt-24">
              <h2 style={{ fontSize: "20px" }}>Question 40:</h2>
              <p className="mt-8">1 + 1 = ?</p>
            </div>

            <div className="quiz-question-options mt-16">
              <div className="quiz-option quiz-option--selected">
                <strong>A</strong>
                <span>1</span>
              </div>
              <div className="quiz-option">
                <strong>B</strong>
                <span>2</span>
              </div>
              <div className="quiz-option">
                <strong>C</strong>
                <span>3</span>
              </div>
              <div className="quiz-option">
                <strong>D</strong>
                <span>4</span>
              </div>
            </div>

            <div
              className="mt-24"
              style={{ display: "flex", justifyContent: "space-between", gap: "12px" }}
            >
              <button className="btn btn-secondary">Previous Question</button>
              <button className="btn btn-primary">Next Question</button>
            </div>
          </section>

          {/* right: questions list */}
          <aside className="card">
            <div className="card-header">
              <h2>Questions</h2>
            </div>
            <div className="quiz-question-grid mt-16">
              <button className="quiz-question-number quiz-question-number--answered">
                1
              </button>
              <button className="quiz-question-number">2</button>
              {/* ... */}
            </div>
            <button className="btn btn-primary mt-24" style={{ width: "100%" }}>
              Submit
            </button>
          </aside>
        </div>
      </div>
    </div>
  );
}
