import { useState, useEffect } from "react";
import { useAuth } from "../contexts/AuthContext";
import { lecturerAPI, messageAPI } from "../services/api";

interface UserListItem {
  user_id: number;
  username: string;
  email: string;
  role: string;
  full_name: string;
}

interface Message {
  id: number;
  sender_id: number;
  sender_name: string;
  receiver_id: number;
  receiver_name: string;
  content: string;
  created_at: string;
  is_read: boolean;
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

interface RatingSummary {
  average_rating: number;
  total_reviews: number;
}

export default function LecturerFeedbackPage() {
  const { user } = useAuth();
  const [students, setStudents] = useState<UserListItem[]>([]);
  const [selectedStudent, setSelectedStudent] = useState<UserListItem | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [ratingSummary, setRatingSummary] = useState<RatingSummary>({ average_rating: 0, total_reviews: 0 });
  const [messageText, setMessageText] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      if (!user?.user_id) return;
      try {
        setLoading(true);
        const [usersRes, feedbacksRes] = await Promise.all([
          messageAPI.getAvailableUsers(),
          lecturerAPI.getFeedback(user.user_id),
        ]);
        // Filter to only students
        const studentUsers = (usersRes.data || []).filter((u: UserListItem) => u.role === "student");
        setStudents(studentUsers);
        setFeedbacks(feedbacksRes.data || []);
        
        // Calculate average rating from feedbacks
        const feedbackData = feedbacksRes.data || [];
        if (feedbackData.length > 0) {
          const total = feedbackData.reduce((sum: number, fb: Feedback) => sum + fb.rating, 0);
          setRatingSummary({
            average_rating: total / feedbackData.length,
            total_reviews: feedbackData.length,
          });
        }
      } catch (err) {
        console.error("Failed to load feedback data", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [user?.user_id]);

  const handleSelectStudent = async (student: UserListItem) => {
    setSelectedStudent(student);
    try {
      const res = await messageAPI.getMessages(student.user_id);
      // Sort messages by created_at in ascending order (oldest first, newest at bottom)
      const sortedMessages = (res.data || []).sort((a: Message, b: Message) => 
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setMessages(sortedMessages);
    } catch (err) {
      console.error("Failed to load conversation", err);
      setMessages([]);
    }
  };

  const handleSendMessage = async () => {
    if (!selectedStudent || !messageText.trim()) return;
    try {
      await messageAPI.sendMessage({
        receiver_id: selectedStudent.user_id,
        content: messageText,
      });
      setMessageText("");
      // Refresh conversation - sort oldest to newest (bottom)
      const res = await messageAPI.getMessages(selectedStudent.user_id);
      const sortedMessages = (res.data || []).sort((a: Message, b: Message) => 
        new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
      );
      setMessages(sortedMessages);
    } catch (err) {
      console.error("Failed to send message", err);
      alert("Failed to send message.");
    }
  };

  const formatTime = (dateStr: string) => {
    const date = new Date(dateStr);
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  };

  const filteredStudents = students.filter((s) =>
    s.full_name.toLowerCase().includes(searchQuery.toLowerCase())
  );

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

        <div className="layout-chat mt-16">
          {/* left: Conversations list */}
          <aside className="chat-sidebar">
            <div className="chat-sidebar-header">
              <input
                className="form-control"
                type="text"
                placeholder="Search students..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            <ul className="chat-list">
              {filteredStudents.length === 0 ? (
                <li className="chat-list-item">
                  <span className="small-caption">No students found.</span>
                </li>
              ) : (
                filteredStudents.map((student) => (
                  <li
                    key={student.user_id}
                    className={`chat-list-item ${
                      selectedStudent?.user_id === student.user_id
                        ? "chat-list-item--active"
                        : ""
                    }`}
                    onClick={() => handleSelectStudent(student)}
                    style={{ cursor: "pointer" }}
                  >
                    <span>{student.full_name}</span>
                  </li>
                ))
              )}
            </ul>
          </aside>

          {/* right: conversation + avg ratings */}
          <section style={{ display: "flex", flexDirection: "column", gap: "16px" }}>
            <div className="chat-main">
              <div className="card-header" style={{ marginBottom: "12px" }}>
                <h2>
                  {selectedStudent
                    ? `Conversation with ${selectedStudent.full_name}`
                    : "Select a student to start conversation"}
                </h2>
              </div>
              <div className="chat-messages">
                {!selectedStudent ? (
                  <p className="small-caption">Select a student from the list.</p>
                ) : messages.length === 0 ? (
                  <p className="small-caption">No messages yet. Start the conversation!</p>
                ) : (
                  messages.map((msg) => (
                    <div
                      key={msg.id}
                      className={`chat-bubble ${
                        msg.sender_id === selectedStudent.user_id
                          ? "chat-bubble--other"
                          : "chat-bubble--me"
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
                  disabled={!selectedStudent}
                />
                <button
                  className="btn btn-primary"
                  onClick={handleSendMessage}
                  disabled={!selectedStudent}
                >
                  Send
                </button>
              </div>
            </div>

            {/* average ratings panel */}
            <section className="card">
              <div className="card-header">
                <h2>Average Ratings</h2>
                <span style={{ fontSize: "24px", color: "#f59e0b" }}>
                  ★ {ratingSummary.average_rating.toFixed(1)}
                </span>
              </div>
              <div className="mt-12">
                {feedbacks.length === 0 ? (
                  <p className="small-caption">No feedback received yet.</p>
                ) : (
                  feedbacks.slice(0, 5).map((fb) => (
                    <div
                      key={fb.id}
                      className="card card--flat"
                      style={{ background: "#fde68a", marginBottom: "8px" }}
                    >
                      <strong>
                        {fb.student_name} - From {fb.course_name}
                      </strong>
                      <div className="small-caption">
                        Rating: {"★".repeat(fb.rating)}{"☆".repeat(5 - fb.rating)}
                      </div>
                      <p className="mt-8 text-muted">{fb.content}</p>
                    </div>
                  ))
                )}
              </div>
            </section>
          </section>
        </div>

      </div>
    </div>
  );
}
