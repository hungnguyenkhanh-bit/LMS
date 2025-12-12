import { useNavigate, useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { lecturerAPI, courseAPI, quizAPI } from "../services/api";

interface Assignment {
  id: number;
  title: string;
  deadline: string;
  description?: string;
  max_score?: number;
}

interface Quiz {
  id: number;
  title: string;
  description?: string;
  duration_minutes: number;
  question_count: number;
}

interface Material {
  id: number;
  title: string;
  type: string;
  file_path: string;
  description?: string;
}

interface Submission {
  id: number;
  assignment_id: number;
  student_id: number;
  student_name: string;
  score: number | null;
  file_path: string | null;
  submitted_at: string;
  graded_at: string | null;
  comments: string | null;
  assignment_title: string;
  assignment_deadline: string;
  max_score: number;
  is_late: boolean;
}

interface CourseDetail {
  id: number;
  code: string;
  name: string;
  description: string;
  assignments: Assignment[];
  quizzes: Quiz[];
  materials: Material[];
}

export default function LecturerCoursePage() {
  const navigate = useNavigate();
  const { courseId } = useParams<{ courseId: string }>();
  const [course, setCourse] = useState<CourseDetail | null>(null);
  const [submissions, setSubmissions] = useState<Submission[]>([]);
  const [loading, setLoading] = useState(true);
  const [announcement, setAnnouncement] = useState("");
  
  // Add Assignment/Quiz Modal State
  const [showAddModal, setShowAddModal] = useState(false);
  const [addType, setAddType] = useState<"assignment" | "quiz">("assignment");
  const [addTitle, setAddTitle] = useState("");
  const [addDescription, setAddDescription] = useState("");
  const [addDeadline, setAddDeadline] = useState("");
  const [addMaxScore, setAddMaxScore] = useState("100");
  const [addDuration, setAddDuration] = useState("30");
  const [addMaxAttempts, setAddMaxAttempts] = useState("1");
  const [addFile, setAddFile] = useState<File | null>(null);
  const [addSubmitting, setAddSubmitting] = useState(false);
  
  // Quiz questions state
  const [quizQuestions, setQuizQuestions] = useState<Array<{
    question_text: string;
    option_a: string;
    option_b: string;
    option_c: string;
    option_d: string;
    correct_option: string;
    points: number;
  }>>([]);
  const [currentQuestion, setCurrentQuestion] = useState({
    question_text: "",
    option_a: "",
    option_b: "",
    option_c: "",
    option_d: "",
    correct_option: "A",
    points: 10,
  });
  
  // Upload Material Modal State
  const [showMaterialModal, setShowMaterialModal] = useState(false);
  const [materialTitle, setMaterialTitle] = useState("");
  const [materialType, setMaterialType] = useState("pdf");
  const [materialDescription, setMaterialDescription] = useState("");
  const [materialFile, setMaterialFile] = useState<File | null>(null);
  const [materialSubmitting, setMaterialSubmitting] = useState(false);
  
  // Grading Modal State
  const [showGradeModal, setShowGradeModal] = useState(false);
  const [selectedSubmission, setSelectedSubmission] = useState<Submission | null>(null);
  const [gradeScore, setGradeScore] = useState("");
  const [gradeComments, setGradeComments] = useState("");
  const [grading, setGrading] = useState(false);
  
  // View Submission Modal State
  const [showViewModal, setShowViewModal] = useState(false);
  const [viewSubmission, setViewSubmission] = useState<Submission | null>(null);
  
  // Quiz Attempts Viewer State
  const [showQuizAttemptsModal, setShowQuizAttemptsModal] = useState(false);
  const [selectedQuizForAttempts, setSelectedQuizForAttempts] = useState<Quiz | null>(null);
  const [quizAttempts, setQuizAttempts] = useState<Array<{
    attempt_id: number;
    student_id: number;
    student_name: string;
    started_at: string;
    finished_at: string | null;
    total_score: number;
    max_score: number;
    percentage: number;
    duration_seconds: number;
  }>>([]);
  
  // Quiz Attempt Detail Modal State
  const [showAttemptDetailModal, setShowAttemptDetailModal] = useState(false);
  const [attemptDetail, setAttemptDetail] = useState<any>(null);

  useEffect(() => {
    const fetchCourseData = async () => {
      if (!courseId) return;
      try {
        setLoading(true);
        const [courseRes, submissionsRes] = await Promise.all([
          courseAPI.getCourseDetail(parseInt(courseId)),
          lecturerAPI.getCourseSubmissions(parseInt(courseId)),
        ]);
        setCourse(courseRes.data);
        setSubmissions(submissionsRes.data || []);
      } catch (err) {
        console.error("Failed to load course data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchCourseData();
  }, [courseId]);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleDateString("en-US", {
      month: "short",
      day: "2-digit",
      year: "numeric",
    });
  };
  
  const formatDateTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString("en-US", {
      month: "short",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  const handlePostAnnouncement = async () => {
    if (!announcement.trim() || !courseId) return;
    try {
      await courseAPI.postAnnouncement(parseInt(courseId), announcement);
      alert("Announcement posted successfully!");
      setAnnouncement("");
      // Refresh course data to get updated announcements
      const courseRes = await courseAPI.getCourseDetail(parseInt(courseId));
      setCourse(courseRes.data);
    } catch (error) {
      console.error("Failed to post announcement", error);
      alert("Failed to post announcement. Please try again.");
    }
  };
  
  const handleAddAssignmentQuiz = async () => {
    if (!addTitle.trim() || !courseId) return;
    
    // For quizzes, require at least one question
    if (addType === "quiz" && quizQuestions.length === 0) {
      alert("Please add at least one question to the quiz.");
      return;
    }
    
    setAddSubmitting(true);
    try {
      if (addType === "assignment") {
        await courseAPI.createAssignment(parseInt(courseId), {
          title: addTitle,
          description: addDescription || undefined,
          deadline: addDeadline || new Date().toISOString(),
          max_score: parseFloat(addMaxScore) || 100,
        });
      } else {
        // Create quiz
        const quizRes = await quizAPI.create({
          course_id: parseInt(courseId),
          title: addTitle,
          description: addDescription || undefined,
          duration_minutes: parseInt(addDuration) || 30,
          max_attempts: parseInt(addMaxAttempts) || 1,
          start_time: new Date().toISOString(), // Make quiz available immediately
          end_time: addDeadline || undefined,
        });
        
        // Add questions to the quiz
        const quizId = quizRes.data.id;
        for (const question of quizQuestions) {
          await quizAPI.addQuestion(quizId, question);
        }
      }
      
      // Refresh course data
      const courseRes = await courseAPI.getCourseDetail(parseInt(courseId));
      setCourse(courseRes.data);
      
      // Reset form
      setShowAddModal(false);
      setAddTitle("");
      setAddDescription("");
      setAddDeadline("");
      setAddMaxScore("100");
      setAddDuration("30");
      setAddMaxAttempts("1");
      setAddFile(null);
      setQuizQuestions([]);
      setCurrentQuestion({
        question_text: "",
        option_a: "",
        option_b: "",
        option_c: "",
        option_d: "",
        correct_option: "A",
        points: 10,
      });
      
      alert(`${addType === "assignment" ? "Assignment" : "Quiz"} created successfully!`);
    } catch (err: any) {
      console.error("Failed to create", err);
      const errorMsg = err.response?.data?.detail || err.message || "Failed to create. Please try again.";
      alert(`Failed to create: ${errorMsg}`);
    } finally {
      setAddSubmitting(false);
    }
  };
  
  const handleAddQuestionToList = () => {
    if (!currentQuestion.question_text.trim() || !currentQuestion.option_a.trim() || !currentQuestion.option_b.trim()) {
      alert("Please fill in at least the question text and options A and B.");
      return;
    }
    
    setQuizQuestions([...quizQuestions, currentQuestion]);
    setCurrentQuestion({
      question_text: "",
      option_a: "",
      option_b: "",
      option_c: "",
      option_d: "",
      correct_option: "A",
      points: 10,
    });
  };
  
  const handleRemoveQuestion = (index: number) => {
    setQuizQuestions(quizQuestions.filter((_, i) => i !== index));
  };
  
  const handleUploadMaterial = async () => {
    if (!materialTitle.trim() || !courseId) return;
    
    setMaterialSubmitting(true);
    try {
      // In a real app, you would upload the file first and get a URL
      const filePath = materialFile ? `/uploads/${materialFile.name}` : undefined;
      
      await courseAPI.addMaterial(parseInt(courseId), {
        title: materialTitle,
        type: materialType,
        description: materialDescription || undefined,
        file_path: filePath,
      });
      
      // Refresh course data
      const courseRes = await courseAPI.getCourseDetail(parseInt(courseId));
      setCourse(courseRes.data);
      
      // Reset form
      setShowMaterialModal(false);
      setMaterialTitle("");
      setMaterialType("pdf");
      setMaterialDescription("");
      setMaterialFile(null);
      
      alert("Material uploaded successfully!");
    } catch (err) {
      console.error("Failed to upload material", err);
      alert("Failed to upload material. Please try again.");
    } finally {
      setMaterialSubmitting(false);
    }
  };
  
  const handleGradeSubmission = async () => {
    if (!selectedSubmission || !gradeScore) return;
    
    setGrading(true);
    try {
      await lecturerAPI.gradeSubmission(selectedSubmission.id, {
        score: parseFloat(gradeScore),
        comments: gradeComments || undefined,
      });
      
      // Refresh submissions
      const submissionsRes = await lecturerAPI.getCourseSubmissions(parseInt(courseId!));
      setSubmissions(submissionsRes.data || []);
      
      // Reset form
      setShowGradeModal(false);
      setSelectedSubmission(null);
      setGradeScore("");
      setGradeComments("");
      
      alert("Submission graded successfully!");
    } catch (err) {
      console.error("Failed to grade submission", err);
      alert("Failed to grade submission. Please try again.");
    } finally {
      setGrading(false);
    }
  };
  
  const openGradeModal = (submission: Submission) => {
    setSelectedSubmission(submission);
    setGradeScore(submission.score?.toString() || "");
    setGradeComments(submission.comments || "");
    setShowGradeModal(true);
  };
  
  const openViewModal = (submission: Submission) => {
    setViewSubmission(submission);
    setShowViewModal(true);
  };
  
  const handleViewQuizAttempts = async (quiz: Quiz) => {
    setSelectedQuizForAttempts(quiz);
    try {
      console.log('Fetching attempts for quiz ID:', quiz.id);
      const res = await quizAPI.getQuizAttempts(quiz.id);
      console.log('Quiz attempts response:', res);
      console.log('Quiz attempts data:', res.data);
      setQuizAttempts(res.data || []);
      setShowQuizAttemptsModal(true);
    } catch (err: any) {
      console.error("Failed to load quiz attempts", err);
      console.error("Error response:", err.response);
      alert(`Failed to load quiz attempts: ${err.response?.data?.detail || err.message}`);
    }
  };
  
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };
  
  const handleViewAttemptDetail = async (attemptId: number) => {
    try {
      const res = await quizAPI.getAttemptDetail(attemptId);
      setAttemptDetail(res.data);
      setShowAttemptDetailModal(true);
    } catch (err: any) {
      console.error("Failed to load attempt details", err);
      alert("Failed to load attempt details");
    }
  };

  if (loading) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <p>Loading course details...</p>
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <p>Course not found.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <h1 className="section-title">{course.name} ({course.code})</h1>

        <div className="grid grid-2 mt-24">
          {/* Assignments & Quizzes */}
          <section className="card">
            <div className="card-header">
              <h2>Assignments &amp; Quizzes</h2>
            </div>
            <div className="mt-16">
              {course.assignments.length === 0 && (!course.quizzes || course.quizzes.length === 0) ? (
                <p className="small-caption">No assignments or quizzes yet.</p>
              ) : (
                <>
                  {course.assignments.map((assignment) => (
                    <div
                      key={`a-${assignment.id}`}
                      className="card card--flat"
                      style={{ background: "#fde68a", marginBottom: "8px" }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <strong>📝 {assignment.title}</strong>
                          <div className="small-caption">Due {formatDate(assignment.deadline)}</div>
                        </div>
                        <span className="small-caption" style={{ background: "#f59e0b", color: "white", padding: "2px 8px", borderRadius: "4px" }}>
                          Assignment
                        </span>
                      </div>
                    </div>
                  ))}
                  {course.quizzes && course.quizzes.map((quiz) => (
                    <div
                      key={`q-${quiz.id}`}
                      className="card card--flat"
                      style={{ background: "#dbeafe", marginBottom: "8px" }}
                    >
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                        <div>
                          <strong>📋 {quiz.title}</strong>
                          <div className="small-caption">{quiz.duration_minutes} mins • {quiz.question_count || 0} questions</div>
                        </div>
                        <span className="small-caption" style={{ background: "#3b82f6", color: "white", padding: "2px 8px", borderRadius: "4px" }}>
                          Quiz
                        </span>
                      </div>
                    </div>
                  ))}
                </>
              )}
            </div>
            <button className="btn btn-primary mt-16" onClick={() => setShowAddModal(true)}>
              + Add Assignment/Quiz
            </button>
          </section>

          {/* Course Materials */}
          <section className="card">
            <div className="card-header">
              <h2>Course Materials</h2>
            </div>
            <div className="mt-16">
              {course.materials.length === 0 ? (
                <p className="small-caption">No materials uploaded yet.</p>
              ) : (
                course.materials.map((material) => (
                  <div
                    key={material.id}
                    className="card card--flat"
                    style={{ background: "#f3f4f6", marginBottom: "8px" }}
                  >
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                      <div>
                        <strong>
                          {material.type === "pdf" && "📄 "}
                          {material.type === "book" && "📚 "}
                          {material.type === "doc" && "📃 "}
                          {material.type === "video" && "🎬 "}
                          {material.title}
                        </strong>
                        {material.description && (
                          <div className="small-caption">{material.description}</div>
                        )}
                      </div>
                      {material.file_path && (
                        <a href={material.file_path} target="_blank" rel="noopener noreferrer" className="btn btn-secondary" style={{ padding: "4px 12px", fontSize: "12px" }}>
                          View
                        </a>
                      )}
                    </div>
                  </div>
                ))
              )}
            </div>
            <button className="btn btn-primary mt-16" onClick={() => setShowMaterialModal(true)}>
              + Upload Material
            </button>
          </section>
        </div>

        {/* Submissions & grading */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Submissions &amp; Grading</h2>
            <span className="small-caption">{submissions.length} submission(s)</span>
          </div>
          <table className="table mt-8">
            <thead>
              <tr>
                <th>Student</th>
                <th>Assignment</th>
                <th>Submitted</th>
                <th>Status</th>
                <th>Score</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {submissions.length === 0 ? (
                <tr>
                  <td colSpan={6}>No submissions yet.</td>
                </tr>
              ) : (
                submissions.map((sub) => (
                  <tr key={sub.id}>
                    <td>{sub.student_name}</td>
                    <td>{sub.assignment_title}</td>
                    <td>{formatDateTime(sub.submitted_at)}</td>
                    <td>
                      {sub.is_late ? (
                        <span style={{ color: "#dc2626", fontWeight: 500 }}>⚠️ Late</span>
                      ) : (
                        <span style={{ color: "#16a34a", fontWeight: 500 }}>✓ On-time</span>
                      )}
                    </td>
                    <td>
                      {sub.score !== null ? (
                        <span style={{ fontWeight: 500 }}>{sub.score.toFixed(1)} / {sub.max_score}</span>
                      ) : (
                        <span style={{ color: "#f59e0b" }}>Pending</span>
                      )}
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: "8px" }}>
                        <button 
                          className="btn btn-secondary" 
                          style={{ padding: "4px 8px", fontSize: "12px" }}
                          onClick={() => openViewModal(sub)}
                        >
                          View
                        </button>
                        <button 
                          className="btn btn-primary" 
                          style={{ padding: "4px 8px", fontSize: "12px" }}
                          onClick={() => openGradeModal(sub)}
                        >
                          {sub.score !== null ? "Regrade" : "Grade"}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </section>

        {/* Quiz Grades & Attempts Viewer */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Quiz Grades &amp; Attempts</h2>
          </div>
          <div className="mt-16">
            {(!course.quizzes || course.quizzes.length === 0) ? (
              <p className="small-caption">No quizzes available.</p>
            ) : (
              <div>
                <div className="form-group">
                  <label className="form-label">Select Quiz</label>
                  <select 
                    className="form-control"
                    onChange={(e) => {
                      const quizId = parseInt(e.target.value);
                      const quiz = course.quizzes?.find(q => q.id === quizId);
                      if (quiz) handleViewQuizAttempts(quiz);
                    }}
                    defaultValue=""
                  >
                    <option value="">-- Select a quiz --</option>
                    {course.quizzes.map((quiz) => (
                      <option key={quiz.id} value={quiz.id}>
                        {quiz.title}
                      </option>
                    ))}
                  </select>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Announcements */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Announcements</h2>
          </div>
          <div className="mt-16">
            <p>
              <strong>Welcome to {course.name}!</strong>
            </p>
            <p className="small-caption mb-16">Course is now active</p>
            <p className="text-muted mb-16">
              {course.description || "No description available."}
            </p>
            <hr />
            <div className="mt-16">
              <label className="form-label" htmlFor="new-ann">
                Write a new announcement...
              </label>
              <textarea 
                id="new-ann" 
                className="form-control"
                value={announcement}
                onChange={(e) => setAnnouncement(e.target.value)}
              ></textarea>
            </div>
            <div
              className="mt-16"
              style={{
                display: "flex",
                gap: "12px",
                justifyContent: "flex-end",
              }}
            >
              <button className="btn btn-secondary" onClick={() => setAnnouncement("")}>
                Clear
              </button>
              <button className="btn btn-primary" onClick={handlePostAnnouncement}>
                Post Announcement
              </button>
            </div>
          </div>
        </section>

        {/* Add Assignment/Quiz Modal */}
        {showAddModal && (
          <div className="modal-overlay" style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }}>
            <div className="modal-content card" style={{ width: "500px", maxHeight: "90vh", overflow: "auto" }}>
              <div className="card-header">
                <h2>Add New Assignment/Quiz</h2>
                <button onClick={() => setShowAddModal(false)} style={{ background: "none", border: "none", fontSize: "20px", cursor: "pointer" }}>×</button>
              </div>
              <div className="mt-16">
                <div className="mb-16">
                  <label className="form-label">Type</label>
                  <div style={{ display: "flex", gap: "16px" }}>
                    <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                      <input 
                        type="radio" 
                        name="addType" 
                        checked={addType === "assignment"} 
                        onChange={() => setAddType("assignment")}
                      />
                      Assignment
                    </label>
                    <label style={{ display: "flex", alignItems: "center", gap: "8px", cursor: "pointer" }}>
                      <input 
                        type="radio" 
                        name="addType" 
                        checked={addType === "quiz"} 
                        onChange={() => setAddType("quiz")}
                      />
                      Quiz
                    </label>
                  </div>
                </div>
                
                <div className="mb-16">
                  <label className="form-label" htmlFor="add-title">Title *</label>
                  <input 
                    id="add-title"
                    type="text" 
                    className="form-control" 
                    value={addTitle}
                    onChange={(e) => setAddTitle(e.target.value)}
                    placeholder={`Enter ${addType} title`}
                  />
                </div>
                
                <div className="mb-16">
                  <label className="form-label" htmlFor="add-desc">Description</label>
                  <textarea 
                    id="add-desc"
                    className="form-control" 
                    value={addDescription}
                    onChange={(e) => setAddDescription(e.target.value)}
                    placeholder="Enter description..."
                    rows={3}
                  />
                </div>
                
                {addType === "assignment" ? (
                  <>
                    <div className="mb-16">
                      <label className="form-label" htmlFor="add-deadline">Deadline</label>
                      <input 
                        id="add-deadline"
                        type="datetime-local" 
                        className="form-control" 
                        value={addDeadline}
                        onChange={(e) => setAddDeadline(e.target.value)}
                      />
                    </div>
                    <div className="mb-16">
                      <label className="form-label" htmlFor="add-max-score">Max Score</label>
                      <input 
                        id="add-max-score"
                        type="number" 
                        className="form-control" 
                        value={addMaxScore}
                        onChange={(e) => setAddMaxScore(e.target.value)}
                        min="1"
                      />
                    </div>
                    <div className="mb-16">
                      <label className="form-label" htmlFor="add-file">Attachment (PDF/Document)</label>
                      <input 
                        id="add-file"
                        type="file" 
                        className="form-control" 
                        accept=".pdf,.doc,.docx"
                        onChange={(e) => setAddFile(e.target.files?.[0] || null)}
                      />
                    </div>
                  </>
                ) : (
                  <>
                    <div className="mb-16">
                      <label className="form-label" htmlFor="add-duration">Duration (minutes)</label>
                      <input 
                        id="add-duration"
                        type="number" 
                        className="form-control" 
                        value={addDuration}
                        onChange={(e) => setAddDuration(e.target.value)}
                        min="1"
                      />
                    </div>
                    <div className="mb-16">
                      <label className="form-label" htmlFor="add-attempts">Max Attempts</label>
                      <input 
                        id="add-attempts"
                        type="number" 
                        className="form-control" 
                        value={addMaxAttempts}
                        onChange={(e) => setAddMaxAttempts(e.target.value)}
                        min="1"
                      />
                    </div>
                    <div className="mb-16">
                      <label className="form-label" htmlFor="add-endtime">End Time (optional)</label>
                      <input 
                        id="add-endtime"
                        type="datetime-local" 
                        className="form-control" 
                        value={addDeadline}
                        onChange={(e) => setAddDeadline(e.target.value)}
                      />
                    </div>
                    
                    {/* Questions Section */}
                    <div className="mb-16" style={{ borderTop: "2px solid #e5e7eb", paddingTop: "16px" }}>
                      <h3 style={{ marginBottom: "12px", fontSize: "16px" }}>Questions ({quizQuestions.length})</h3>
                      
                      {/* Added Questions List */}
                      {quizQuestions.length > 0 && (
                        <div style={{ marginBottom: "16px", maxHeight: "200px", overflowY: "auto" }}>
                          {quizQuestions.map((q, index) => (
                            <div key={index} className="card card--flat" style={{ background: "#f0f9ff", marginBottom: "8px", padding: "8px" }}>
                              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                                <div style={{ flex: 1 }}>
                                  <strong style={{ fontSize: "13px" }}>Q{index + 1}: {q.question_text}</strong>
                                  <div className="small-caption" style={{ marginTop: "4px" }}>
                                    Correct: {q.correct_option} | Points: {q.points}
                                  </div>
                                </div>
                                <button 
                                  className="btn btn-secondary" 
                                  style={{ padding: "2px 8px", fontSize: "11px" }}
                                  onClick={() => handleRemoveQuestion(index)}
                                >
                                  Remove
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
                      
                      {/* Add New Question Form */}
                      <div className="card card--flat" style={{ background: "#fef3c7", padding: "12px" }}>
                        <label className="form-label" style={{ fontSize: "13px", fontWeight: 600 }}>Add Question</label>
                        
                        <input 
                          type="text" 
                          className="form-control" 
                          placeholder="Question text"
                          value={currentQuestion.question_text}
                          onChange={(e) => setCurrentQuestion({...currentQuestion, question_text: e.target.value})}
                          style={{ marginBottom: "8px" }}
                        />
                        
                        <input 
                          type="text" 
                          className="form-control" 
                          placeholder="Option A"
                          value={currentQuestion.option_a}
                          onChange={(e) => setCurrentQuestion({...currentQuestion, option_a: e.target.value})}
                          style={{ marginBottom: "8px" }}
                        />
                        
                        <input 
                          type="text" 
                          className="form-control" 
                          placeholder="Option B"
                          value={currentQuestion.option_b}
                          onChange={(e) => setCurrentQuestion({...currentQuestion, option_b: e.target.value})}
                          style={{ marginBottom: "8px" }}
                        />
                        
                        <input 
                          type="text" 
                          className="form-control" 
                          placeholder="Option C (optional)"
                          value={currentQuestion.option_c}
                          onChange={(e) => setCurrentQuestion({...currentQuestion, option_c: e.target.value})}
                          style={{ marginBottom: "8px" }}
                        />
                        
                        <input 
                          type="text" 
                          className="form-control" 
                          placeholder="Option D (optional)"
                          value={currentQuestion.option_d}
                          onChange={(e) => setCurrentQuestion({...currentQuestion, option_d: e.target.value})}
                          style={{ marginBottom: "8px" }}
                        />
                        
                        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px", marginBottom: "8px" }}>
                          <div>
                            <label className="form-label" style={{ fontSize: "11px" }}>Correct Answer</label>
                            <select 
                              className="form-control"
                              value={currentQuestion.correct_option}
                              onChange={(e) => setCurrentQuestion({...currentQuestion, correct_option: e.target.value})}
                            >
                              <option value="A">A</option>
                              <option value="B">B</option>
                              <option value="C">C</option>
                              <option value="D">D</option>
                            </select>
                          </div>
                          <div>
                            <label className="form-label" style={{ fontSize: "11px" }}>Points</label>
                            <input 
                              type="number" 
                              className="form-control"
                              value={currentQuestion.points}
                              onChange={(e) => setCurrentQuestion({...currentQuestion, points: parseInt(e.target.value) || 10})}
                              min="1"
                            />
                          </div>
                        </div>
                        
                        <button 
                          className="btn btn-secondary" 
                          style={{ width: "100%", padding: "6px" }}
                          onClick={handleAddQuestionToList}
                        >
                          + Add Question to List
                        </button>
                      </div>
                    </div>
                  </>
                )}
                
                <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "24px" }}>
                  <button className="btn btn-secondary" onClick={() => setShowAddModal(false)}>
                    Cancel
                  </button>
                  <button 
                    className="btn btn-primary" 
                    onClick={handleAddAssignmentQuiz}
                    disabled={addSubmitting || !addTitle.trim()}
                  >
                    {addSubmitting ? "Creating..." : `Create ${addType === "assignment" ? "Assignment" : "Quiz"}`}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upload Material Modal */}
        {showMaterialModal && (
          <div className="modal-overlay" style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }}>
            <div className="modal-content card" style={{ width: "500px", maxHeight: "90vh", overflow: "auto" }}>
              <div className="card-header">
                <h2>Upload Course Material</h2>
                <button onClick={() => setShowMaterialModal(false)} style={{ background: "none", border: "none", fontSize: "20px", cursor: "pointer" }}>×</button>
              </div>
              <div className="mt-16">
                <div className="mb-16">
                  <label className="form-label" htmlFor="mat-title">Title *</label>
                  <input 
                    id="mat-title"
                    type="text" 
                    className="form-control" 
                    value={materialTitle}
                    onChange={(e) => setMaterialTitle(e.target.value)}
                    placeholder="Enter material title"
                  />
                </div>
                
                <div className="mb-16">
                  <label className="form-label" htmlFor="mat-type">Type</label>
                  <select 
                    id="mat-type"
                    className="form-control"
                    value={materialType}
                    onChange={(e) => setMaterialType(e.target.value)}
                  >
                    <option value="pdf">📄 PDF Document</option>
                    <option value="book">📚 Book Reference</option>
                    <option value="doc">📃 Word Document</option>
                    <option value="video">🎬 Video</option>
                    <option value="link">🔗 External Link</option>
                  </select>
                </div>
                
                <div className="mb-16">
                  <label className="form-label" htmlFor="mat-desc">Description</label>
                  <textarea 
                    id="mat-desc"
                    className="form-control" 
                    value={materialDescription}
                    onChange={(e) => setMaterialDescription(e.target.value)}
                    placeholder="Enter description..."
                    rows={3}
                  />
                </div>
                
                <div className="mb-16">
                  <label className="form-label" htmlFor="mat-file">File Upload</label>
                  <input 
                    id="mat-file"
                    type="file" 
                    className="form-control" 
                    accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.mp4,.avi"
                    onChange={(e) => setMaterialFile(e.target.files?.[0] || null)}
                  />
                  <p className="small-caption mt-8">Supported: PDF, Word, PowerPoint, Excel, Video files</p>
                </div>
                
                <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "24px" }}>
                  <button className="btn btn-secondary" onClick={() => setShowMaterialModal(false)}>
                    Cancel
                  </button>
                  <button 
                    className="btn btn-primary" 
                    onClick={handleUploadMaterial}
                    disabled={materialSubmitting || !materialTitle.trim()}
                  >
                    {materialSubmitting ? "Uploading..." : "Upload Material"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Grade Submission Modal */}
        {showGradeModal && selectedSubmission && (
          <div className="modal-overlay" style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }}>
            <div className="modal-content card" style={{ width: "500px" }}>
              <div className="card-header">
                <h2>{selectedSubmission.score !== null ? "Regrade" : "Grade"} Submission</h2>
                <button onClick={() => setShowGradeModal(false)} style={{ background: "none", border: "none", fontSize: "20px", cursor: "pointer" }}>×</button>
              </div>
              <div className="mt-16">
                <div className="mb-16">
                  <p><strong>Student:</strong> {selectedSubmission.student_name}</p>
                  <p><strong>Assignment:</strong> {selectedSubmission.assignment_title}</p>
                  <p><strong>Submitted:</strong> {formatDateTime(selectedSubmission.submitted_at)}</p>
                  {selectedSubmission.is_late && (
                    <p style={{ color: "#dc2626" }}><strong>⚠️ Late submission</strong></p>
                  )}
                </div>
                
                <div className="mb-16">
                  <label className="form-label" htmlFor="grade-score">Score (out of {selectedSubmission.max_score})</label>
                  <input 
                    id="grade-score"
                    type="number" 
                    className="form-control" 
                    value={gradeScore}
                    onChange={(e) => setGradeScore(e.target.value)}
                    min="0"
                    max={selectedSubmission.max_score}
                    step="0.5"
                  />
                </div>
                
                <div className="mb-16">
                  <label className="form-label" htmlFor="grade-comments">Comments (optional)</label>
                  <textarea 
                    id="grade-comments"
                    className="form-control" 
                    value={gradeComments}
                    onChange={(e) => setGradeComments(e.target.value)}
                    placeholder="Enter feedback for the student..."
                    rows={3}
                  />
                </div>
                
                <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end" }}>
                  <button className="btn btn-secondary" onClick={() => setShowGradeModal(false)}>
                    Cancel
                  </button>
                  <button 
                    className="btn btn-primary" 
                    onClick={handleGradeSubmission}
                    disabled={grading || !gradeScore}
                  >
                    {grading ? "Saving..." : "Save Grade"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* View Submission Modal */}
        {showViewModal && viewSubmission && (
          <div className="modal-overlay" style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }}>
            <div className="modal-content card" style={{ width: "600px" }}>
              <div className="card-header">
                <h2>Submission Details</h2>
                <button onClick={() => setShowViewModal(false)} style={{ background: "none", border: "none", fontSize: "20px", cursor: "pointer" }}>×</button>
              </div>
              <div className="mt-16">
                <div className="grid grid-2" style={{ gap: "16px" }}>
                  <div>
                    <p className="small-caption">Student</p>
                    <p><strong>{viewSubmission.student_name}</strong></p>
                  </div>
                  <div>
                    <p className="small-caption">Assignment</p>
                    <p><strong>{viewSubmission.assignment_title}</strong></p>
                  </div>
                  <div>
                    <p className="small-caption">Submitted At</p>
                    <p><strong>{formatDateTime(viewSubmission.submitted_at)}</strong></p>
                  </div>
                  <div>
                    <p className="small-caption">Deadline</p>
                    <p><strong>{formatDateTime(viewSubmission.assignment_deadline)}</strong></p>
                  </div>
                  <div>
                    <p className="small-caption">Status</p>
                    <p>
                      {viewSubmission.is_late ? (
                        <span style={{ color: "#dc2626", fontWeight: 600 }}>⚠️ Late</span>
                      ) : (
                        <span style={{ color: "#16a34a", fontWeight: 600 }}>✓ On-time</span>
                      )}
                    </p>
                  </div>
                  <div>
                    <p className="small-caption">Score</p>
                    <p>
                      {viewSubmission.score !== null ? (
                        <strong>{viewSubmission.score.toFixed(1)} / {viewSubmission.max_score}</strong>
                      ) : (
                        <span style={{ color: "#f59e0b", fontWeight: 600 }}>Not graded</span>
                      )}
                    </p>
                  </div>
                </div>
                
                {viewSubmission.file_path && (
                  <div className="mt-16">
                    <p className="small-caption">Submitted File</p>
                    <a href={viewSubmission.file_path} target="_blank" rel="noopener noreferrer" className="btn btn-secondary">
                      📎 Download Submission
                    </a>
                  </div>
                )}
                
                {viewSubmission.comments && (
                  <div className="mt-16">
                    <p className="small-caption">Grading Comments</p>
                    <p style={{ background: "#f3f4f6", padding: "12px", borderRadius: "8px" }}>{viewSubmission.comments}</p>
                  </div>
                )}
                
                <div style={{ display: "flex", gap: "12px", justifyContent: "flex-end", marginTop: "24px" }}>
                  <button className="btn btn-secondary" onClick={() => setShowViewModal(false)}>
                    Close
                  </button>
                  <button 
                    className="btn btn-primary" 
                    onClick={() => {
                      setShowViewModal(false);
                      openGradeModal(viewSubmission);
                    }}
                  >
                    {viewSubmission.score !== null ? "Regrade" : "Grade"}
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Quiz Attempts Modal */}
        {showQuizAttemptsModal && selectedQuizForAttempts && (
          <div className="modal-overlay" style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1000
          }}>
            <div className="modal-content card" style={{ width: "900px", maxHeight: "90vh", overflow: "auto" }}>
              <div className="card-header">
                <h2>Quiz Attempts: {selectedQuizForAttempts.title}</h2>
                <button onClick={() => setShowQuizAttemptsModal(false)} style={{ background: "none", border: "none", fontSize: "20px", cursor: "pointer" }}>×</button>
              </div>
              <div className="mt-16">
                {quizAttempts.length === 0 ? (
                  <p className="small-caption">No attempts yet.</p>
                ) : (
                  <table className="table">
                    <thead>
                      <tr>
                        <th>Student Name</th>
                        <th>Student ID</th>
                        <th>Submitted At</th>
                        <th>Duration</th>
                        <th>Score</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {quizAttempts.map((attempt) => (
                        <tr key={attempt.attempt_id}>
                          <td>{attempt.student_name}</td>
                          <td>{attempt.student_id || "N/A"}</td>
                          <td>{attempt.started_at ? new Date(attempt.started_at).toLocaleString() : "N/A"}</td>
                          <td>{formatDuration(attempt.duration_seconds)}</td>
                          <td>
                            <strong>{attempt.total_score.toFixed(1)} / {attempt.max_score.toFixed(1)}</strong>
                            <div className="small-caption">({attempt.percentage.toFixed(1)}%)</div>
                          </td>
                          <td>
                            <button 
                              className="btn btn-secondary" 
                              style={{ padding: "4px 12px", fontSize: "12px" }}
                              onClick={() => handleViewAttemptDetail(attempt.attempt_id)}
                            >
                              View Details
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                )}
                <button className="btn btn-secondary mt-16" onClick={() => setShowQuizAttemptsModal(false)}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Quiz Attempt Detail Modal */}
        {showAttemptDetailModal && attemptDetail && (
          <div className="modal-overlay" style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: "rgba(0,0,0,0.5)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 1001
          }}>
            <div className="modal-content card" style={{ width: "800px", maxHeight: "90vh", overflow: "auto" }}>
              <div className="card-header">
                <h2>Quiz Attempt Details</h2>
                <button onClick={() => setShowAttemptDetailModal(false)} style={{ background: "none", border: "none", fontSize: "20px", cursor: "pointer" }}>×</button>
              </div>
              <div className="mt-16">
                {/* Summary */}
                <div style={{ background: "#f9fafb", padding: "16px", borderRadius: "8px", marginBottom: "24px" }}>
                  <div className="grid grid-2" style={{ gap: "16px" }}>
                    <div>
                      <p className="small-caption">Quiz</p>
                      <p><strong>{attemptDetail.quiz_title}</strong></p>
                    </div>
                    <div>
                      <p className="small-caption">Score</p>
                      <p><strong>{attemptDetail.total_score.toFixed(1)} / {attemptDetail.max_score.toFixed(1)} ({attemptDetail.percentage.toFixed(1)}%)</strong></p>
                    </div>
                    <div>
                      <p className="small-caption">Correct Answers</p>
                      <p><strong>{attemptDetail.correct_answers} / {attemptDetail.total_questions}</strong></p>
                    </div>
                    <div>
                      <p className="small-caption">Status</p>
                      <p><strong>{attemptDetail.status}</strong></p>
                    </div>
                  </div>
                </div>

                {/* Questions and Answers */}
                <h3 style={{ marginBottom: "16px" }}>Questions & Answers</h3>
                {attemptDetail.answers && attemptDetail.answers.map((answer: any, index: number) => (
                  <div 
                    key={answer.question_id} 
                    style={{ 
                      padding: "16px", 
                      marginBottom: "16px", 
                      borderRadius: "8px",
                      border: answer.is_correct ? "2px solid #16a34a" : "2px solid #dc2626",
                      background: answer.is_correct ? "#f0fdf4" : "#fef2f2"
                    }}
                  >
                    <div style={{ display: "flex", alignItems: "flex-start", gap: "12px", marginBottom: "12px" }}>
                      <span style={{ 
                        fontSize: "18px", 
                        fontWeight: "bold",
                        color: answer.is_correct ? "#16a34a" : "#dc2626"
                      }}>
                        {answer.is_correct ? "✓" : "✗"}
                      </span>
                      <div style={{ flex: 1 }}>
                        <p style={{ fontWeight: 600, marginBottom: "8px" }}>
                          Question {index + 1}: {answer.question_text}
                        </p>
                        <div style={{ marginLeft: "8px" }}>
                          <p style={{ marginBottom: "4px" }}>
                            <span className={answer.chosen_option === 'A' ? (answer.is_correct ? 'text-success' : 'text-danger') : ''}>
                              A. {answer.option_a} {answer.chosen_option === 'A' && '← Your answer'}
                            </span>
                          </p>
                          <p style={{ marginBottom: "4px" }}>
                            <span className={answer.chosen_option === 'B' ? (answer.is_correct ? 'text-success' : 'text-danger') : ''}>
                              B. {answer.option_b} {answer.chosen_option === 'B' && '← Your answer'}
                            </span>
                          </p>
                          {answer.option_c && (
                            <p style={{ marginBottom: "4px" }}>
                              <span className={answer.chosen_option === 'C' ? (answer.is_correct ? 'text-success' : 'text-danger') : ''}>
                                C. {answer.option_c} {answer.chosen_option === 'C' && '← Your answer'}
                              </span>
                            </p>
                          )}
                          {answer.option_d && (
                            <p style={{ marginBottom: "4px" }}>
                              <span className={answer.chosen_option === 'D' ? (answer.is_correct ? 'text-success' : 'text-danger') : ''}>
                                D. {answer.option_d} {answer.chosen_option === 'D' && '← Your answer'}
                              </span>
                            </p>
                          )}
                          {!answer.is_correct && (
                            <p style={{ marginTop: "8px", color: "#16a34a", fontWeight: 500 }}>
                              ✓ Correct answer: {answer.correct_option}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
                
                <button className="btn btn-secondary mt-16" onClick={() => setShowAttemptDetailModal(false)}>
                  Close
                </button>
              </div>
            </div>
          </div>
        )}

      </div>
    </div>
  );
}
