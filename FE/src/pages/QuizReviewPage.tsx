import { useNavigate, useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { quizAPI } from "../services/api";

interface QuizAnswer {
  question_id: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string | null;
  option_d: string | null;
  chosen_option: string;
  correct_option: string;
  is_correct: boolean;
  points: number;
}

interface AttemptDetail {
  attempt_id: number;
  quiz_id: number;
  quiz_title: string;
  total_questions: number;
  correct_answers: number;
  total_score: number;
  max_score: number;
  percentage: number;
  status: string;
  started_at: string;
  finished_at: string | null;
  answers: QuizAnswer[];
}

export default function QuizReviewPage() {
  const navigate = useNavigate();
  const { attemptId } = useParams<{ attemptId: string }>();
  const [attempt, setAttempt] = useState<AttemptDetail | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchAttemptDetail = async () => {
      if (!attemptId) return;
      try {
        setLoading(true);
        setError(null);
        const res = await quizAPI.getAttemptDetail(parseInt(attemptId));
        setAttempt(res.data);
      } catch (err: any) {
        console.error("Failed to load attempt details", err);
        setError(err?.response?.data?.detail || "Failed to load attempt details.");
      } finally {
        setLoading(false);
      }
    };
    fetchAttemptDetail();
  }, [attemptId]);

  if (loading) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <p>Loading attempt details...</p>
        </div>
      </div>
    );
  }

  if (error || !attempt) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <div className="card" style={{ padding: "24px", textAlign: "center" }}>
            <h2 style={{ color: "#dc2626" }}>Error</h2>
            <p className="mt-16">{error || "Attempt not found."}</p>
            <button className="btn btn-secondary mt-16" onClick={() => navigate(-1)}>
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  const currentAnswer = attempt.answers[currentIndex];
  const options = [
    { key: "A", value: currentAnswer.option_a },
    { key: "B", value: currentAnswer.option_b },
    { key: "C", value: currentAnswer.option_c },
    { key: "D", value: currentAnswer.option_d },
  ];

  const getOptionClass = (optionKey: string) => {
    const isChosen = currentAnswer.chosen_option === optionKey;
    const isCorrect = currentAnswer.correct_option === optionKey;
    
    if (isCorrect && isChosen) {
      return "quiz-option quiz-option--correct";
    } else if (isCorrect) {
      return "quiz-option quiz-option--correct";
    } else if (isChosen) {
      return "quiz-option quiz-option--incorrect";
    }
    return "quiz-option";
  };

  const getQuestionStatus = (answer: QuizAnswer) => {
    if (!answer.chosen_option) return "unanswered";
    return answer.is_correct ? "correct" : "incorrect";
  };

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">Review: {attempt.quiz_title}</h1>
        
        <div className="card mt-16" style={{ padding: "16px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <span className="small-caption">Your Score</span>
            <p style={{ fontSize: "24px", fontWeight: 700 }}>
              {attempt.total_score.toFixed(1)} / {attempt.max_score.toFixed(1)} ({attempt.percentage.toFixed(1)}%)
            </p>
          </div>
          <button className="btn btn-secondary" onClick={() => navigate(-1)}>
            Back to Results
          </button>
        </div>

        <div className="quiz-layout mt-16">
          {/* left: question area */}
          <section className="card">
            <div className="mt-8">
              <h2 style={{ fontSize: "20px" }}>Question {currentIndex + 1}:</h2>
              <p className="mt-8">{currentAnswer.question_text}</p>
              <p className="mt-8 small-caption">
                Points: {currentAnswer.is_correct ? currentAnswer.points : 0}/{currentAnswer.points}
              </p>
            </div>

            <div className="quiz-question-options mt-16">
              {options.map((opt) => (
                <div
                  key={opt.key}
                  className={getOptionClass(opt.key)}
                  style={{ cursor: "default" }}
                >
                  <strong>{opt.key}</strong>
                  <span>{opt.value}</span>
                  {opt.key === currentAnswer.correct_option && (
                    <span style={{ marginLeft: "auto", color: "#16a34a", fontWeight: 600 }}>✓ Correct</span>
                  )}
                  {opt.key === currentAnswer.chosen_option && opt.key !== currentAnswer.correct_option && (
                    <span style={{ marginLeft: "auto", color: "#dc2626", fontWeight: 600 }}>✗ Your answer</span>
                  )}
                </div>
              ))}
            </div>

            {!currentAnswer.chosen_option && (
              <p className="mt-16" style={{ color: "#f59e0b", fontWeight: 500 }}>
                ⚠ You did not answer this question.
              </p>
            )}

            <div
              className="mt-24"
              style={{ display: "flex", justifyContent: "space-between", gap: "12px" }}
            >
              <button
                className="btn btn-secondary"
                disabled={currentIndex === 0}
                onClick={() => setCurrentIndex((prev) => Math.max(0, prev - 1))}
              >
                Previous Question
              </button>
              <button
                className="btn btn-primary"
                disabled={currentIndex === attempt.answers.length - 1}
                onClick={() => setCurrentIndex((prev) => Math.min(attempt.answers.length - 1, prev + 1))}
              >
                Next Question
              </button>
            </div>
          </section>

          {/* right: questions list */}
          <aside className="card">
            <div className="card-header">
              <h2>Questions</h2>
            </div>
            <div className="quiz-question-grid mt-16">
              {attempt.answers.map((ans, idx) => {
                const status = getQuestionStatus(ans);
                let className = "quiz-question-number";
                if (status === "correct") className += " quiz-question-number--correct";
                else if (status === "incorrect") className += " quiz-question-number--incorrect";
                else className += " quiz-question-number--unanswered";
                if (currentIndex === idx) className += " quiz-question-number--current";
                
                return (
                  <button
                    key={ans.question_id}
                    className={className}
                    onClick={() => setCurrentIndex(idx)}
                  >
                    {idx + 1}
                  </button>
                );
              })}
            </div>
            <div className="mt-16 small-caption">
              Correct: {attempt.answers.filter(a => getQuestionStatus(a) === "correct").length} / {attempt.answers.length}
            </div>
          </aside>
        </div>
      </div>
    </div>
  );
}
