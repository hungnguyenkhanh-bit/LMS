import { useNavigate, useLocation } from "react-router-dom";

interface QuizResult {
  score: number;
  max_score: number;
  total_questions: number;
  correct_answers: number;
  answered_questions: number;
  duration_seconds: number;
  quiz_id: number;
  course_id: number;
  percentage: number;
  attempt_id: number;
}

export default function QuizFinishedPage() {
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get result from navigation state (passed from QuizTakingPage)
  const result = location.state as QuizResult | null;

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins} min ${secs} secs`;
  };

  // Default values if no result passed
  const score = result?.score ?? 0;
  const maxScore = result?.max_score ?? 10;
  const totalQuestions = result?.total_questions ?? 0;
  const correctAnswers = result?.correct_answers ?? 0;
  const answeredQuestions = result?.answered_questions ?? 0;
  const durationSeconds = result?.duration_seconds ?? 0;
  const courseId = result?.course_id ?? null;
  const percentage = result?.percentage ?? 0;
  const attemptId = result?.attempt_id ?? null;

  // Calculate percentages
  const answeredPercentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;
  const correctPercentage = totalQuestions > 0 ? Math.round((correctAnswers / totalQuestions) * 100) : 0;

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
            Your Score: {score.toFixed(1)}/{maxScore.toFixed(1)} ({percentage.toFixed(1)}%)
          </p>

          <div className="grid grid-2 mt-24" style={{ gap: "24px" }}>
            <div className="card card--flat" style={{ padding: "16px", textAlign: "center" }}>
              <div className="small-caption">Duration</div>
              <p className="text-muted" style={{ fontSize: "18px", fontWeight: 600 }}>{formatDuration(durationSeconds)}</p>
            </div>
            <div className="card card--flat" style={{ padding: "16px", textAlign: "center" }}>
              <div className="small-caption">Correct Answers</div>
              <p className="text-muted" style={{ fontSize: "18px", fontWeight: 600 }}>{correctAnswers}/{totalQuestions}</p>
            </div>
            <div className="card card--flat" style={{ padding: "16px", textAlign: "center" }}>
              <div className="small-caption">Questions Answered</div>
              <p className="text-muted" style={{ fontSize: "18px", fontWeight: 600 }}>{answeredPercentage}% ({answeredQuestions}/{totalQuestions})</p>
            </div>
            <div className="card card--flat" style={{ padding: "16px", textAlign: "center" }}>
              <div className="small-caption">Accuracy</div>
              <p className="text-muted" style={{ fontSize: "18px", fontWeight: 600 }}>{correctPercentage}%</p>
            </div>
          </div>

          <div
            className="mt-32"
            style={{ display: "flex", justifyContent: "center", gap: "16px" }}
          >
            <button 
              className="btn btn-secondary"
              onClick={() => navigate(courseId ? `/student-course/${courseId}` : "/my-courses")}
            >
              Return to Course
            </button>
            {attemptId && (
              <button 
                className="btn btn-primary"
                onClick={() => navigate(`/quiz-review/${attemptId}`)}
              >
                View Attempt
              </button>
            )}
          </div>
        </section>
      </div>
    </div>
  );
}
