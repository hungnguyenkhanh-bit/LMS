import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

// ============ Prediction API Types ============

/**
 * Input data for pass/fail prediction
 *
 * This interface defines the 7 required metrics that the ML model
 * needs to make a prediction. All fields are required and must be
 * within specific ranges (also validated by backend).
 *
 * @interface PredictionInput
 * @example
 * ```typescript
 * const input: PredictionInput = {
 *   current_gpa: 3.0,
 *   attendance_rate: 0.85,  // 0.85 = 85%
 *   avg_quiz_score: 75.0,
 *   avg_assignment_score: 80.0,
 *   late_submissions: 2,
 *   courses_enrolled: 5,
 *   study_hours_per_week: 12.0
 * };
 * ```
 */
export interface PredictionInput {
  /** Attendance rate as decimal (0.0 - 1.0, where 0.85 = 85%) */
  attendance_rate: number;

  /** Average quiz score (0 - 100) */
  avg_quiz_score: number;

  /** Average assignment score (0 - 100) */
  assignment_score: number;

  /** Average hours spent studying per week */
  study_hours_per_week: number;
}

/**
 * Result of pass/fail prediction
 *
 * This interface defines what the backend returns after making a
 * prediction. It includes the predicted GPA, confidence score,
 * pass/fail status, and personalized recommendations.
 *
 * @interface PredictionResult
 * @example
 * ```typescript
 * const result: PredictionResult = {
 *   predicted_gpa: 3.25,
 *   confidence: 0.85,
 *   pass_fail: 'pass',
 *   threshold: 2.0,
 *   recommendations: '✅ You are on track to pass...',
 *   model_version: 'v1.0'
 * };
 * ```
 */
export interface PredictionResult {
  /** Predicted GPA (0.0 - 4.0) */
  predicted_gpa: number;

  /** Confidence score (0.0 - 1.0, where 1.0 = 100% confident) */
  confidence: number;

  /** Pass or fail status based on threshold (only 'pass' or 'fail' allowed) */
  pass_fail: "pass" | "fail";

  /** GPA threshold used for pass/fail determination (typically 2.0) */
  threshold: number;

  /** Personalized advice for improvement (formatted with emojis) */
  recommendations: string;

  /** Version of ML model used (e.g., "v1.0") */
  model_version: string;
}

// ============ Auth API ============
export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await api.post("/auth/login", { username, password });
    return response.data;
  },

  getCurrentUser: async () => {
    const response = await api.get("/auth/me");
    return response.data;
  },
};

// ============ Student API ============
export const studentAPI = {
  getProfile: (userId: number) => api.get(`/students/${userId}/profile`),

  getGPAHistory: (studentId: number) =>
    api.get(`/students/${studentId}/gpa-history`),

  getDashboard: (userId: number) => api.get(`/students/${userId}/dashboard`),

  getCourses: (userId: number) => api.get(`/students/${userId}/courses`),

  getAssignments: (userId: number) =>
    api.get(`/students/${userId}/assignments`),

  getGrades: (userId: number) => api.get(`/students/${userId}/grades`),

  getQuizzes: (userId: number) => api.get(`/students/${userId}/quizzes`),

  getQuizAttempts: (userId: number) =>
    api.get(`/students/${userId}/quiz-attempts`),

  setTargetGPA: (userId: number, targetGpa: number) =>
    api.put(`/students/${userId}/target-gpa`, { target_gpa: targetGpa }),

  submitAssignment: (
    userId: number,
    data: { assignment_id: number; file_path?: string }
  ) => api.post(`/students/${userId}/submissions`, data),

  enrollCourse: (userId: number, courseId: number) =>
    api.post(`/students/${userId}/enroll`, { course_id: courseId }),

  getMessages: (userId: number) => api.get(`/students/${userId}/messages`),

  sendMessage: (
    userId: number,
    data: { receiver_id: number; content: string }
  ) => api.post(`/students/${userId}/messages`, data),

  submitFeedback: (
    userId: number,
    data: { course_id: number; content?: string; rating: number }
  ) => api.post(`/students/${userId}/feedback`, data),

  getFeedbackHistory: (userId: number) =>
    api.get(`/students/${userId}/feedback`),

  updateFeedback: (
    userId: number,
    feedbackId: number,
    data: { content?: string; rating?: number }
  ) => api.put(`/students/${userId}/feedback/${feedbackId}`, data),

  /**
   * Generate a pass/fail prediction for a student
   *
   * Makes a POST request to the backend prediction endpoint with
   * performance metrics. The backend uses an ML model to predict
   * the student's GPA and determine if they're likely to pass.
   *
   * @param userId - The student's user ID
   * @param data - Performance metrics (7 required fields)
   * @returns Promise<AxiosResponse<PredictionResult>> - Axios response with prediction result
   *
   * @example
   * ```typescript
   * try {
   *   const response = await studentAPI.predictPassFail(42, {
   *     current_gpa: 3.0,
   *     attendance_rate: 0.85,
   *     avg_quiz_score: 75.0,
   *     avg_assignment_score: 80.0,
   *     late_submissions: 2,
   *     courses_enrolled: 5,
   *     study_hours_per_week: 12.0
   *   });
   *
   *   const result = response.data;
   *   console.log(result.predicted_gpa);  // 3.25
   *   console.log(result.pass_fail);      // "pass"
   *   console.log(result.recommendations); // Personalized advice
   * } catch (error: any) {
   *   if (error.response?.status === 401) {
   *     console.error("Not authenticated");
   *   } else if (error.response?.status === 403) {
   *     console.error("Not authorized (students can only predict for self)");
   *   } else if (error.response?.status === 422) {
   *     console.error("Invalid input data:", error.response.data.detail);
   *   } else if (error.response?.status === 500) {
   *     console.error("Prediction service error");
   *   }
   * }
   * ```
   *
   * @throws {AxiosError} 401 Unauthorized - Missing or invalid JWT token
   * @throws {AxiosError} 403 Forbidden - Not authorized (students can only predict for self)
   * @throws {AxiosError} 404 Not Found - Student not found
   * @throws {AxiosError} 422 Unprocessable Entity - Invalid input data (wrong types or ranges)
   * @throws {AxiosError} 500 Internal Server Error - Prediction service failure (model loading/prediction error)
   *
   * @see {@link PredictionInput} for input data structure
   * @see {@link PredictionResult} for response data structure
   * @see Backend documentation: BE/PREDICTION_API_DESIGN.md
   */
  predictPassFail: (userId: number, data: PredictionInput) =>
    api.post<PredictionResult>(`/students/${userId}/predict`, data),
};

// ============ Lecturer API ============
export const lecturerAPI = {
  getAll: () => api.get("/lecturers"),

  getProfile: (userId: number) => api.get(`/lecturers/${userId}/profile`),

  getDashboard: (userId: number) => api.get(`/lecturers/${userId}/dashboard`),

  getCourses: (userId: number) => api.get(`/lecturers/${userId}/courses`),

  getPendingSubmissions: (userId: number) =>
    api.get(`/lecturers/${userId}/pending-submissions`),

  getFeedback: (userId: number) => api.get(`/lecturers/${userId}/feedback`),

  getAtRiskStudents: (userId: number) =>
    api.get(`/lecturers/${userId}/at-risk-students`),

  getAttendanceStats: (userId: number) =>
    api.get(`/lecturers/${userId}/attendance-stats`),

  getScoreStats: (userId: number) =>
    api.get(`/lecturers/${userId}/score-stats`),

  createAssignment: (
    userId: number,
    data: {
      course_id: number;
      title: string;
      description?: string;
      deadline: string;
      max_score?: number;
    }
  ) => api.post(`/lecturers/${userId}/assignments`, data),

  gradeSubmission: (
    submissionId: number,
    data: { score: number; comments?: string }
  ) => api.put(`/lecturers/submissions/${submissionId}/grade`, data),

  getCourseSubmissions: (courseId: number) =>
    api.get(`/courses/${courseId}/submissions`),

  getMessages: (userId: number) => api.get(`/lecturers/${userId}/messages`),

  sendMessage: (
    userId: number,
    data: { receiver_id: number; content: string }
  ) => api.post(`/lecturers/${userId}/messages`, data),
};

// ============ Manager API ============
export const managerAPI = {
  getProfile: () => api.get("/manager/profile"),

  getDashboard: () => api.get("/manager/dashboard"),

  getStudents: () => api.get("/manager/students"),

  getLecturers: () => api.get("/manager/lecturers"),

  getCourses: () => api.get("/manager/courses"),

  createCourse: (data: {
    code: string;
    name: string;
    credits?: number;
    capacity?: number;
    semester: string;
    lecturer_id?: number;
    description?: string;
  }) => api.post("/manager/courses", data),

  updateCourse: (
    courseId: number,
    data: {
      name?: string;
      credits?: number;
      capacity?: number;
      semester?: string;
      lecturer_id?: number;
      description?: string;
    }
  ) => api.put(`/manager/courses/${courseId}`, data),

  deleteCourse: (courseId: number) =>
    api.delete(`/manager/courses/${courseId}`),

  assignLecturer: (courseId: number, lecturerId: number) =>
    api.put(
      `/manager/courses/${courseId}/assign-lecturer?lecturer_id=${lecturerId}`
    ),

  getFeedback: () => api.get("/manager/feedback"),

  getCourseStatistics: () => api.get("/manager/statistics/courses"),

  getGPADistribution: () => api.get("/manager/statistics/gpa"),

  getMessages: () => api.get("/manager/messages"),

  sendMessage: (data: { receiver_id: number; content: string }) =>
    api.post("/manager/messages", data),
};

// ============ Course API ============
export const courseAPI = {
  getAll: () => api.get("/courses"),

  getCourseDetail: (courseId: number) => api.get(`/courses/${courseId}`),

  getMaterials: (courseId: number) => api.get(`/courses/${courseId}/materials`),

  addMaterial: (
    courseId: number,
    data: {
      title: string;
      type: string;
      description?: string;
      file_path?: string;
    }
  ) =>
    api.post(`/courses/${courseId}/materials`, {
      ...data,
      course_id: courseId,
    }),

  getAssignments: (courseId: number) =>
    api.get(`/courses/${courseId}/assignments`),

  createAssignment: (
    courseId: number,
    data: {
      title: string;
      description?: string;
      deadline: string;
      max_score?: number;
    }
  ) =>
    api.post(`/courses/${courseId}/assignments`, {
      ...data,
      course_id: courseId,
    }),

  getStudents: (courseId: number) => api.get(`/courses/${courseId}/students`),

  getFeedback: (courseId: number) => api.get(`/courses/${courseId}/feedback`),

  submitFeedback: (
    courseId: number,
    data: { comment?: string; rating: number }
  ) =>
    api.post(`/courses/${courseId}/feedback`, { ...data, course_id: courseId }),

  postAnnouncement: (courseId: number, content: string) =>
    api.post(`/courses/${courseId}/announcements`, { content }),
};

// ============ Quiz API ============
export const quizAPI = {
  getAll: (courseId?: number) => {
    const params = courseId ? `?course_id=${courseId}` : "";
    return api.get(`/quizzes${params}`);
  },

  getQuizDetail: (quizId: number) => api.get(`/quizzes/${quizId}`),

  create: (data: {
    course_id: number;
    title: string;
    description?: string;
    duration_minutes?: number;
    max_attempts?: number;
    start_time?: string;
    end_time?: string;
  }) => api.post("/quizzes", data),

  addQuestion: (
    quizId: number,
    data: {
      question_text: string;
      option_a: string;
      option_b: string;
      option_c?: string;
      option_d?: string;
      correct_option: string;
      points?: number;
    }
  ) => api.post(`/quizzes/${quizId}/questions`, data),

  startAttempt: (quizId: number) => api.post(`/quizzes/${quizId}/start`),

  submitAttempt: (
    attemptId: number,
    data: {
      quiz_id?: number;
      answers: Array<{ question_id: number; chosen_option: string }>;
    }
  ) => api.post(`/quizzes/attempts/${attemptId}/submit`, data),

  getAttempt: (attemptId: number) => api.get(`/quizzes/attempts/${attemptId}`),

  getAttemptDetail: (attemptId: number) =>
    api.get(`/quizzes/attempts/${attemptId}/detail`),

  getStudentAttempts: (studentId: number, quizId?: number) => {
    const params = quizId ? `?quiz_id=${quizId}` : "";
    return api.get(`/quizzes/student/${studentId}/attempts${params}`);
  },

  getQuizAttempts: (quizId: number) => api.get(`/quizzes/${quizId}/attempts`),
};

// ============ Message API ============
export const messageAPI = {
  getMessages: (otherUserId?: number) => {
    const params = otherUserId ? `?other_user_id=${otherUserId}` : "";
    return api.get(`/messages${params}`);
  },

  sendMessage: (data: { receiver_id: number; content: string }) =>
    api.post("/messages", data),

  getConversations: () => api.get("/messages/conversations"),

  getConversation: (userId: number) =>
    api.get(`/messages?other_user_id=${userId}`),

  getUnreadCount: () => api.get("/messages/unread-count"),

  markRead: (senderId: number) => api.post(`/messages/mark-read/${senderId}`),

  getAvailableUsers: () => api.get("/messages/users"),
};

export default api;
