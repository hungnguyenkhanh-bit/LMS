import { useNavigate, useParams } from "react-router-dom";
import { useState, useEffect, useCallback } from "react";
import { quizAPI } from "../services/api";

interface QuizQuestion {
  id: number;
  question_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  points: number;
}

interface QuizData {
  id: number;
  title: string;
  course_id: number;
  duration_minutes: number;
  questions: QuizQuestion[];
}

interface AttemptData {
  attempt_id: number;
  quiz_id: number;
}

export default function QuizTakingPage() {
  const navigate = useNavigate();
  const { quizId } = useParams<{ quizId: string }>();
  const [quiz, setQuiz] = useState<QuizData | null>(null);
  const [attempt, setAttempt] = useState<AttemptData | null>(null);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState<{ [key: number]: string }>({});
  const [timeLeft, setTimeLeft] = useState(0);
  const [startTime] = useState<number>(Date.now());
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchQuiz = async () => {
      if (!quizId) return;
      try {
        setLoading(true);
        setError(null);
        // First get quiz details
        const quizRes = await quizAPI.getQuizDetail(parseInt(quizId));
        setQuiz(quizRes.data);
        setTimeLeft(quizRes.data.duration_minutes * 60);
        
        // Start an attempt
        const attemptRes = await quizAPI.startAttempt(parseInt(quizId));
        if (attemptRes.data) {
          setAttempt(attemptRes.data);
        } else {
          setError("Cannot start quiz. You may have reached the maximum number of attempts.");
        }
      } catch (err: any) {
        console.error("Failed to load quiz", err);
        setError(err?.response?.data?.detail || "Failed to load quiz. Please try again.");
      } finally {
        setLoading(false);
      }
    };
    fetchQuiz();
  }, [quizId]);

  // Timer countdown
  useEffect(() => {
    if (timeLeft <= 0 || !quiz || submitting) return;
    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 1) {
          clearInterval(timer);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(timer);
  }, [timeLeft, quiz, submitting]);

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };

  const handleSelectAnswer = (questionId: number, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId]: answer }));
    // Save to localStorage for persistence
    const savedAnswers = { ...answers, [questionId]: answer };
    localStorage.setItem(`quiz_${quizId}_answers`, JSON.stringify(savedAnswers));
  };

  // Load saved answers from localStorage on mount
  useEffect(() => {
    if (quizId) {
      const saved = localStorage.getItem(`quiz_${quizId}_answers`);
      if (saved) {
        try {
          setAnswers(JSON.parse(saved));
        } catch (e) {
          console.error("Failed to load saved answers");
        }
      }
    }
  }, [quizId]);

  // Clear saved answers after successful submission
  const clearSavedAnswers = useCallback(() => {
    if (quizId) {
      localStorage.removeItem(`quiz_${quizId}_answers`);
    }
  }, [quizId]);

  const handleSubmitQuiz = useCallback(async () => {
    if (!attempt || !quiz || submitting) return;
    setSubmitting(true);
    
    const durationSeconds = Math.floor((Date.now() - startTime) / 1000);
    
    try {
      // Submit all answers
      const answersList = Object.entries(answers).map(([questionId, answer]) => ({
        question_id: parseInt(questionId),
        chosen_option: answer,
      }));
      
      const result = await quizAPI.submitAttempt(attempt.attempt_id, { 
        quiz_id: quiz.id,
        answers: answersList 
      });
      
      // Clear saved answers on success
      clearSavedAnswers();
      
      // Navigate to finished page with result data
      navigate("/quiz-finished", { 
        state: {
          score: result.data.total_score,
          max_score: result.data.max_score,
          total_questions: result.data.total_questions,
          correct_answers: result.data.correct_answers,
          answered_questions: Object.keys(answers).length,
          duration_seconds: durationSeconds,
          quiz_id: quiz.id,
          course_id: quiz.course_id,
          percentage: result.data.percentage,
          attempt_id: attempt.attempt_id,
        }
      });
    } catch (err) {
      console.error("Failed to submit quiz", err);
      alert("Failed to submit quiz. Please try again.");
      setSubmitting(false);
    }
  }, [attempt, quiz, answers, submitting, navigate, startTime, clearSavedAnswers]);

  // Auto-submit when time runs out
  useEffect(() => {
    if (timeLeft === 0 && quiz && attempt && !submitting) {
      handleSubmitQuiz();
    }
  }, [timeLeft, quiz, attempt, submitting, handleSubmitQuiz]);

  if (loading) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <p>Loading quiz...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <div className="card" style={{ padding: "24px", textAlign: "center" }}>
            <h2 style={{ color: "#dc2626" }}>Error</h2>
            <p className="mt-16">{error}</p>
            <button className="btn btn-secondary mt-16" onClick={() => navigate(-1)}>
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!quiz || quiz.questions.length === 0) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <p>Quiz not found or has no questions.</p>
          <button className="btn btn-secondary" onClick={() => navigate(-1)}>
            Go Back
          </button>
        </div>
      </div>
    );
  }

  const currentQuestion = quiz.questions[currentIndex];
  const options = [
    { key: "A", value: currentQuestion.option_a },
    { key: "B", value: currentQuestion.option_b },
    { key: "C", value: currentQuestion.option_c },
    { key: "D", value: currentQuestion.option_d },
  ];

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">Quiz: {quiz.title}</h1>

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
              <div style={{ fontSize: "32px", fontWeight: 700, color: timeLeft < 60 ? "red" : "inherit" }}>
                {formatTime(timeLeft)}
              </div>
            </div>

            <div className="mt-24">
              <h2 style={{ fontSize: "20px" }}>Question {currentIndex + 1}:</h2>
              <p className="mt-8">{currentQuestion.question_text}</p>
            </div>

            <div className="quiz-question-options mt-16">
              {options.map((opt) => (
                <div
                  key={opt.key}
                  className={`quiz-option ${
                    answers[currentQuestion.id] === opt.key ? "quiz-option--selected" : ""
                  }`}
                  onClick={() => handleSelectAnswer(currentQuestion.id, opt.key)}
                  style={{ cursor: "pointer" }}
                >
                  <strong>{opt.key}</strong>
                  <span>{opt.value}</span>
                </div>
              ))}
            </div>

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
                disabled={currentIndex === quiz.questions.length - 1}
                onClick={() => setCurrentIndex((prev) => Math.min(quiz.questions.length - 1, prev + 1))}
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
              {quiz.questions.map((q, idx) => (
                <button
                  key={q.id}
                  className={`quiz-question-number ${
                    answers[q.id] ? "quiz-question-number--answered" : ""
                  } ${currentIndex === idx ? "quiz-question-number--current" : ""}`}
                  onClick={() => setCurrentIndex(idx)}
                >
                  {idx + 1}
                </button>
              ))}
            </div>
            <div className="mt-16 small-caption">
              Answered: {Object.keys(answers).length} / {quiz.questions.length}
            </div>
            <button 
              className="btn btn-primary mt-24" 
              style={{ width: "100%" }}
              onClick={handleSubmitQuiz}
              disabled={submitting}
            >
              {submitting ? "Submitting..." : "Submit"}
            </button>
          </aside>
        </div>
      </div>
    </div>
  );
}
