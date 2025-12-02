import { useState, useEffect, useCallback } from "react";
import { useAuth } from "../contexts/AuthContext";
import { studentAPI, lecturerAPI, messageAPI } from "../services/api";

interface Course {
  id: number;
  code: string;
  name: string;
  lecturer_id?: number;
  lecturer_name?: string;
}

interface Lecturer {
  user_id: number;
  full_name: string;
  department: string;
}

interface Message {
  id: number;
  sender_id: number;
  sender_name: string;
  receiver_id: number;
  receiver_name: string;
  content: string;
  is_read: boolean;
  created_at: string;
}

interface Feedback {
  id: number;
  content: string;
  rating: number;
  student_id: number;
  student_name: string;
  course_id: number;
  course_name: string;
  created_at: string;
}

export default function StudentFeedbackPage() {
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [lecturers, setLecturers] = useState<Lecturer[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [feedbackHistory, setFeedbackHistory] = useState<Feedback[]>([]);
  const [selectedCourse, setSelectedCourse] = useState<number>(0);
  const [rating, setRating] = useState<number>(4);
  const [comment, setComment] = useState("");
  const [selectedLecturer, setSelectedLecturer] = useState<Lecturer | null>(null);
  const [messageText, setMessageText] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);
  const [editingFeedback, setEditingFeedback] = useState<Feedback | null>(null);
  const [editRating, setEditRating] = useState<number>(4);
  const [editComment, setEditComment] = useState("");

  const fetchData = useCallback(async () => {
    if (!user?.user_id) return;
    try {
      const [coursesRes, lecturersRes, messagesRes, feedbackRes] = await Promise.all([
        studentAPI.getCourses(user.user_id),
        lecturerAPI.getAll(),
        studentAPI.getMessages(user.user_id),
        studentAPI.getFeedbackHistory(user.user_id),
      ]);
      setCourses(coursesRes.data || []);
      setLecturers((lecturersRes.data || []).map((l: any) => ({
        user_id: l.user_id,
        full_name: l.full_name,
        department: l.department || "General",
      })));
      setMessages(messagesRes.data || []);
      setFeedbackHistory(feedbackRes.data || []);
    } catch (err) {
      console.error("Failed to load feedback data", err);
    }
  }, [user?.user_id]);

  useEffect(() => {
    const loadData = async () => {
      setLoading(true);
      await fetchData();
      setLoading(false);
    };
    loadData();
  }, [fetchData]);

  const handleSubmitFeedback = async () => {
    if (!user?.user_id || !selectedCourse || !comment.trim()) {
      alert("Please select a course and enter a comment.");
      return;
    }
    try {
      await studentAPI.submitFeedback(user.user_id, { course_id: selectedCourse, rating, content: comment });
      alert("Feedback submitted successfully!");
      setComment("");
      setRating(4);
      setSelectedCourse(0);
      // Refresh feedback history
      const feedbackRes = await studentAPI.getFeedbackHistory(user.user_id);
      setFeedbackHistory(feedbackRes.data || []);
    } catch (err) {
      console.error("Failed to submit feedback", err);
      alert("Failed to submit feedback.");
    }
  };

  const handleEditFeedback = (feedback: Feedback) => {
    setEditingFeedback(feedback);
    setEditRating(feedback.rating);
    setEditComment(feedback.content || "");
  };

  const handleUpdateFeedback = async () => {
    if (!user?.user_id || !editingFeedback) return;
    try {
      await studentAPI.updateFeedback(user.user_id, editingFeedback.id, { 
        rating: editRating, 
        content: editComment 
      });
      alert("Feedback updated successfully!");
      setEditingFeedback(null);
      // Refresh feedback history
      const feedbackRes = await studentAPI.getFeedbackHistory(user.user_id);
      setFeedbackHistory(feedbackRes.data || []);
    } catch (err) {
      console.error("Failed to update feedback", err);
      alert("Failed to update feedback.");
    }
  };

  const handleCancelEdit = () => {
    setEditingFeedback(null);
    setEditRating(4);
    setEditComment("");
  };

  const handleSelectLecturer = async (lecturer: Lecturer) => {
    setSelectedLecturer(lecturer);
    try {
      const res = await messageAPI.getMessages(lecturer.user_id);
      setMessages(res.data || []);
    } catch (err) {
      console.error("Failed to load conversation", err);
      setMessages([]);
    }
  };

  const handleSendMessage = async () => {
    if (!user?.user_id || !selectedLecturer || !messageText.trim()) {
      return;
    }
    try {
      await messageAPI.sendMessage({
        receiver_id: selectedLecturer.user_id,
        content: messageText,
      });
      setMessageText("");
      // Refresh messages
      const res = await messageAPI.getMessages(selectedLecturer.user_id);
      setMessages(res.data || []);
    } catch (err) {
      console.error("Failed to send message", err);
      alert("Failed to send message.");
    }
  };

  const filteredLecturers = lecturers.filter((l) =>
    l.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderStars = (count: number, onClick?: (rating: number) => void) => {
    return Array.from({ length: 5 }, (_, i) => (
      <span
        key={i}
        onClick={() => onClick && onClick(i + 1)}
        style={{ cursor: onClick ? "pointer" : "default", fontSize: "20px" }}
      >
        {i < count ? "⭐" : "☆"}
      </span>
    ));
  };

  const renderEditableStars = (count: number) => renderStars(count, setRating);
  const renderEditStars = (count: number) => renderStars(count, setEditRating);
  const renderStaticStars = (count: number) => renderStars(count);

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleString("en-US", {
      year: "numeric",
      month: "2-digit",
      day: "2-digit",
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  if (loading) {
    return (
      <div className="app-main">
        <div className="app-main-inner">
          <p>Loading feedback page...</p>
        </div>
      </div>
    );
  }

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
              <select
                className="form-control"
                value={selectedCourse}
                onChange={(e) => setSelectedCourse(parseInt(e.target.value))}
              >
                <option value={0}>-- Select a course --</option>
                {courses.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.code} - {c.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-group">
              <label className="form-label">Session Rating</label>
              <div>{renderEditableStars(rating)}</div>
            </div>
            <div className="form-group">
              <label className="form-label">Comments</label>
              <textarea
                className="form-control"
                value={comment}
                onChange={(e) => setComment(e.target.value)}
              ></textarea>
            </div>
            <button className="btn btn-primary" onClick={handleSubmitFeedback}>
              Submit Feedback
            </button>
          </div>
        </section>

        {/* Feedback History */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Your Feedback History</h2>
          </div>
          <div className="mt-16">
            {feedbackHistory.length === 0 ? (
              <p className="small-caption">No feedback submitted yet.</p>
            ) : (
              feedbackHistory.map((fb) => (
                <div key={fb.id} className="card card--flat" style={{ background: "#f0f9ff", marginBottom: "20px" }}>
                  {editingFeedback?.id === fb.id ? (
                    // Edit mode
                    <div>
                      <div className="form-group">
                        <label className="form-label">Course: {fb.course_name}</label>
                      </div>
                      <div className="form-group">
                        <label className="form-label">Rating</label>
                        <div>{renderEditStars(editRating)}</div>
                      </div>
                      <div className="form-group">
                        <label className="form-label">Comments</label>
                        <textarea
                          className="form-control"
                          value={editComment}
                          onChange={(e) => setEditComment(e.target.value)}
                        ></textarea>
                      </div>
                      <div style={{ display: "flex", gap: "8px" }}>
                        <button className="btn btn-primary" onClick={handleUpdateFeedback}>
                          Save Changes
                        </button>
                        <button className="btn btn-secondary" onClick={handleCancelEdit}>
                          Cancel
                        </button>
                      </div>
                    </div>
                  ) : (
                    // View mode
                    <div>
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                        <strong>{fb.course_name}</strong>
                        <button 
                          className="btn btn-secondary" 
                          style={{ padding: "4px 12px", fontSize: "12px" }}
                          onClick={() => handleEditFeedback(fb)}
                        >
                          Edit
                        </button>
                      </div>
                      <div className="mt-8">{renderStaticStars(fb.rating)}</div>
                      <p className="mt-8 text-muted">{fb.content}</p>
                      <div className="small-caption mt-8">{formatDate(fb.created_at)}</div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </section>

        {/* Direct messaging with professors - Chat UI */}
        <section className="card mt-24">
          <div className="card-header">
            <h2>Direct Messaging with Professors</h2>
          </div>
          <div className="layout-chat mt-16">
            {/* left: Professors list */}
            <aside className="chat-sidebar">
              <div className="chat-sidebar-header">
                <input
                  className="form-control"
                  type="text"
                  placeholder="Search professors..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </div>
              <ul className="chat-list">
                {filteredLecturers.length === 0 ? (
                  <li className="chat-list-item">
                    <span className="small-caption">No professors found.</span>
                  </li>
                ) : (
                  filteredLecturers.map((lecturer) => (
                    <li
                      key={lecturer.user_id}
                      className={`chat-list-item ${
                        selectedLecturer?.user_id === lecturer.user_id
                          ? "chat-list-item--active"
                          : ""
                      }`}
                      onClick={() => handleSelectLecturer(lecturer)}
                      style={{ cursor: "pointer" }}
                    >
                      <span>{lecturer.full_name}</span>
                      <span className="small-caption" style={{ display: "block", fontSize: "11px" }}>
                        {lecturer.department}
                      </span>
                    </li>
                  ))
                )}
              </ul>
            </aside>

            {/* right: conversation */}
            <div className="chat-main">
              <div className="card-header" style={{ marginBottom: "12px" }}>
                <h2>
                  {selectedLecturer
                    ? `Conversation with ${selectedLecturer.full_name}`
                    : "Select a professor to start conversation"}
                </h2>
              </div>
              <div className="chat-messages">
                {!selectedLecturer ? (
                  <p className="small-caption">Select a professor from the list.</p>
                ) : messages.length === 0 ? (
                  <p className="small-caption">No messages yet. Start the conversation!</p>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`chat-bubble ${
                        msg.sender_id === user?.user_id
                          ? "chat-bubble--me"
                          : "chat-bubble--other"
                      }`}
                    >
                      {msg.content}
                    </div>
                  ))
                )}
              </div>
              <div className="chat-input-row">
                <input
                  className="form-control"
                  type="text"
                  placeholder="Type your message here..."
                  value={messageText}
                  onChange={(e) => setMessageText(e.target.value)}
                  onKeyPress={(e) => e.key === "Enter" && handleSendMessage()}
                  disabled={!selectedLecturer}
                />
                <button
                  className="btn btn-primary"
                  onClick={handleSendMessage}
                  disabled={!selectedLecturer}
                >
                  Send
                </button>
              </div>
            </div>
          </div>
        </section>

      </div>
    </div>
  );
}
