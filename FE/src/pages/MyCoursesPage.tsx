import { useNavigate } from "react-router-dom";
import { useEffect, useState } from "react";
import { useAuth } from "../contexts/AuthContext";
import { studentAPI, lecturerAPI, courseAPI } from "../services/api";

interface Course {
  id: number;
  code: string;
  name: string;
  credits: number;
  semester: string;
  capacity: number;
  lecturer_name: string | null;
  enrolled_count: number;
  description: string | null;
  image_url?: string; // Optional course cover image
}

const courseColors = [
  "#111827",
  "#1e3a5f",
  "#374151",
  "#064e3b",
  "#7c2d12",
  "#4c1d95",
];

export default function MyCoursesPage() {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [courses, setCourses] = useState<Course[]>([]);
  const [allCourses, setAllCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [showEnrollModal, setShowEnrollModal] = useState(false);
  const fallbackImages = [
    "https://images.unsplash.com/photo-1523580846011-d3a5bc25702b?auto=format&fit=crop&w=1200&q=60",
    "https://images.unsplash.com/photo-1521737604893-d14cc237f11d?auto=format&fit=crop&w=1200&q=60",
    "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?auto=format&fit=crop&w=1200&q=60",
    "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?auto=format&fit=crop&w=1200&q=60",
    "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?auto=format&fit=crop&w=1200&q=60",
    "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?auto=format&fit=crop&w=1200&q=60",
  ];

  useEffect(() => {
    const fetchCourses = async () => {
      if (!user?.user_id) return;
      
      try {
        setLoading(true);
        if (user.role === "student") {
          const response = await studentAPI.getCourses(user.user_id);
          setCourses(response.data || []);
        } else if (user.role === "lecturer") {
          const response = await lecturerAPI.getCourses(user.user_id);
          setCourses(response.data || []);
        }
      } catch (error) {
        console.error("Error fetching courses:", error);
      } finally {
        setLoading(false);
      }
    };

    fetchCourses();
  }, [user?.user_id, user?.role]);

  const fetchAllCourses = async () => {
    try {
      const response = await courseAPI.getAll();
      const data = response.data || [];
      // Filter out courses already enrolled
      const enrolledIds = courses.map(c => c.id);
      const available = data.filter((c: Course) => !enrolledIds.includes(c.id));
      setAllCourses(available);
    } catch (error) {
      console.error("Error fetching all courses:", error);
    }
  };

  const handleAccessCourse = (courseId: number) => {
    if (user?.role === "student") {
      navigate(`/student-course/${courseId}`);
    } else if (user?.role === "lecturer") {
      navigate(`/lecturer-course/${courseId}`);
    }
  };

  const handleEnroll = async (courseId: number) => {
    if (!user?.user_id) return;
    
    try {
      await studentAPI.enrollCourse(user.user_id, courseId);
      // Refresh courses list
      const response = await studentAPI.getCourses(user.user_id);
      setCourses(response.data || []);
      setShowEnrollModal(false);
    } catch (error) {
      console.error("Error enrolling in course:", error);
      alert("Failed to enroll in course");
    }
  };

  const openEnrollModal = () => {
    fetchAllCourses();
    setShowEnrollModal(true);
  };

  return (
    <div className="app-main">
      <div className="app-main-inner">
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <h1 className="section-title">My Courses</h1>
          {user?.role === "student" && (
            <button className="btn btn-primary" onClick={openEnrollModal}>
              + Enroll in Course
            </button>
          )}
        </div>

        {loading ? (
          <p className="text-muted mt-24">Loading courses...</p>
        ) : courses.length === 0 ? (
          <div className="card mt-24">
            <p className="text-muted">No courses found. {user?.role === "student" && "Click 'Enroll in Course' to get started."}</p>
          </div>
        ) : (
          <div className="grid grid-3 mt-24">
            {courses.map((course, index) => (
              <article key={course.id} className="card">
                <h2 style={{ fontSize: "20px" }}>{course.name}</h2>
                <div className="small-caption">Course ID: {course.code}</div>
                <div className="small-caption">Credits: {course.credits} | Semester: {course.semester}</div>
                {course.lecturer_name && (
                  <div className="small-caption">Lecturer: {course.lecturer_name}</div>
                )}
                <div
                  className="mt-16"
                  style={{
                    position: "relative",
                    height: "160px",
                    borderRadius: "14px",
                    overflow: "hidden",
                    background: courseColors[index % courseColors.length],
                  }}
                >
                  <img
                    src={course.image_url || fallbackImages[index % fallbackImages.length]}
                    alt={`${course.name} cover`}
                    style={{ width: "100%", height: "100%", objectFit: "cover" }}
                    onError={(e) => {
                      // Gracefully fall back to a solid background if image fails
                      e.currentTarget.style.display = "none";
                    }}
                  />
                  <div
                    style={{
                      position: "absolute",
                      inset: 0,
                      background: "linear-gradient(180deg, rgba(0,0,0,0.05) 0%, rgba(0,0,0,0.55) 100%)",
                      display: "flex",
                      alignItems: "flex-end",
                      padding: "12px 14px",
                      color: "#f9fafb",
                      fontWeight: 700,
                      letterSpacing: "0.3px",
                    }}
                  >
                    <div>
                      <div style={{ fontSize: "14px", opacity: 0.8 }}>Code</div>
                      <div style={{ fontSize: "18px" }}>{course.code}</div>
                    </div>
                  </div>
                </div>
                <p className="small-caption mt-8" style={{ 
                  overflow: "hidden", 
                  textOverflow: "ellipsis", 
                  display: "-webkit-box", 
                  WebkitLineClamp: 2, 
                  WebkitBoxOrient: "vertical" 
                }}>
                  {course.description || "No description available"}
                </p>
                <button
                  className="btn btn-primary mt-16"
                  style={{ width: "100%" }}
                  onClick={() => handleAccessCourse(course.id)}
                >
                  Access Course
                </button>
              </article>
            ))}
          </div>
        )}

        {/* Enroll Modal */}
        {showEnrollModal && (
          <div 
            style={{
              position: "fixed",
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              background: "rgba(0,0,0,0.5)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              zIndex: 1000,
            }}
            onClick={() => setShowEnrollModal(false)}
          >
            <div 
              className="card"
              style={{ 
                width: "600px", 
                maxHeight: "80vh", 
                overflow: "auto",
                background: "#fff",
              }}
              onClick={e => e.stopPropagation()}
            >
              <h2>Available Courses</h2>
              <div className="mt-16">
                {allCourses.length === 0 ? (
                  <p className="text-muted">No available courses to enroll</p>
                ) : (
                  allCourses.map(course => (
                    <div 
                      key={course.id} 
                      className="card card--flat mb-8"
                      style={{ padding: "12px", display: "flex", justifyContent: "space-between", alignItems: "center" }}
                    >
                      <div>
                        <strong>{course.name}</strong>
                        <div className="small-caption">{course.code} | {course.credits} credits</div>
                        <div className="small-caption">{course.lecturer_name || "TBA"}</div>
                      </div>
                      <button 
                        className="btn btn-secondary"
                        onClick={() => handleEnroll(course.id)}
                      >
                        Enroll
                      </button>
                    </div>
                  ))
                )}
              </div>
              <button 
                className="btn btn-secondary mt-16"
                onClick={() => setShowEnrollModal(false)}
              >
                Close
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
