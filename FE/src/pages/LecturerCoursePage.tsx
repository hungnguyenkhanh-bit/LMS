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
    // Implementation would go here
    alert("Announcement posted!");
    setAnnouncement("");
  };
  
  const handleAddAssignmentQuiz = async () => {
    if (!addTitle.trim() || !courseId) return;
    
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
        await quizAPI.create({
          course_id: parseInt(courseId),
          title: addTitle,
          description: addDescription || undefined,
          duration_minutes: parseInt(addDuration) || 30,
          max_attempts: parseInt(addMaxAttempts) || 1,
          end_time: addDeadline || undefined,
        });
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
      
      alert(`${addType === "assignment" ? "Assignment" : "Quiz"} created successfully!`);
    } catch (err) {
      console.error("Failed to create", err);
      alert("Failed to create. Please try again.");
    } finally {
      setAddSubmitting(false);
    }
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
          <button className="btn btn-secondary" onClick={() => navigate("/lecturer-dashboard")}>
            ← Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h1 className="section-title">{course.name} ({course.code})</h1>
          <button className="btn btn-secondary" onClick={() => navigate("/lecturer-dashboard")}>
            ← Back to Dashboard
          </button>
        </div>

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

      </div>
    </div>
  );
}
