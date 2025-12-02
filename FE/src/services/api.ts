import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
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
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// ============ Auth API ============
export const authAPI = {
  login: async (username: string, password: string) => {
    const response = await api.post('/auth/login', { username, password });
    return response.data;
  },
  
  getCurrentUser: async () => {
    const response = await api.get('/auth/me');
    return response.data;
  },
};

// ============ Student API ============
export const studentAPI = {
  getProfile: (userId: number) => api.get(`/students/${userId}/profile`),
  
  getDashboard: (userId: number) => api.get(`/students/${userId}/dashboard`),
  
  getCourses: (userId: number) => api.get(`/students/${userId}/courses`),
  
  getAssignments: (userId: number) => api.get(`/students/${userId}/assignments`),
  
  getGrades: (userId: number) => api.get(`/students/${userId}/grades`),
  
  getQuizzes: (userId: number) => api.get(`/students/${userId}/quizzes`),
  
  getQuizAttempts: (userId: number) => api.get(`/students/${userId}/quiz-attempts`),
  
  setTargetGPA: (userId: number, targetGpa: number) =>
    api.put(`/students/${userId}/target-gpa`, { target_gpa: targetGpa }),
  
  submitAssignment: (userId: number, data: { assignment_id: number; file_path?: string }) =>
    api.post(`/students/${userId}/submissions`, data),
  
  enrollCourse: (userId: number, courseId: number) =>
    api.post(`/students/${userId}/enroll`, { course_id: courseId }),
  
  getMessages: (userId: number) => api.get(`/students/${userId}/messages`),
  
  sendMessage: (userId: number, data: { receiver_id: number; content: string }) =>
    api.post(`/students/${userId}/messages`, data),
    
  submitFeedback: (userId: number, data: { course_id: number; content?: string; rating: number }) =>
    api.post(`/students/${userId}/feedback`, data),
    
  getFeedbackHistory: (userId: number) => api.get(`/students/${userId}/feedback`),
  
  updateFeedback: (userId: number, feedbackId: number, data: { content?: string; rating?: number }) =>
    api.put(`/students/${userId}/feedback/${feedbackId}`, data),
};

// ============ Lecturer API ============
export const lecturerAPI = {
  getAll: () => api.get('/lecturers'),
  
  getProfile: (userId: number) => api.get(`/lecturers/${userId}/profile`),
  
  getDashboard: (userId: number) => api.get(`/lecturers/${userId}/dashboard`),
  
  getCourses: (userId: number) => api.get(`/lecturers/${userId}/courses`),
  
  getPendingSubmissions: (userId: number) => api.get(`/lecturers/${userId}/pending-submissions`),
  
  getFeedback: (userId: number) => api.get(`/lecturers/${userId}/feedback`),
  
  getAtRiskStudents: (userId: number) => api.get(`/lecturers/${userId}/at-risk-students`),
  
  getAttendanceStats: (userId: number) => api.get(`/lecturers/${userId}/attendance-stats`),
  
  getScoreStats: (userId: number) => api.get(`/lecturers/${userId}/score-stats`),
  
  createAssignment: (userId: number, data: {
    course_id: number;
    title: string;
    description?: string;
    deadline: string;
    max_score?: number;
  }) => api.post(`/lecturers/${userId}/assignments`, data),
  
  gradeSubmission: (submissionId: number, data: { score: number; comments?: string }) =>
    api.put(`/lecturers/submissions/${submissionId}/grade`, data),
  
  getCourseSubmissions: (courseId: number) => api.get(`/courses/${courseId}/submissions`),
  
  getMessages: (userId: number) => api.get(`/lecturers/${userId}/messages`),
  
  sendMessage: (userId: number, data: { receiver_id: number; content: string }) =>
    api.post(`/lecturers/${userId}/messages`, data),
};

// ============ Manager API ============
export const managerAPI = {
  getProfile: () => api.get('/manager/profile'),
  
  getDashboard: () => api.get('/manager/dashboard'),
  
  getStudents: () => api.get('/manager/students'),
  
  getLecturers: () => api.get('/manager/lecturers'),
  
  getCourses: () => api.get('/manager/courses'),
  
  createCourse: (data: {
    code: string;
    name: string;
    credits?: number;
    capacity?: number;
    semester: string;
    lecturer_id?: number;
    description?: string;
  }) => api.post('/manager/courses', data),
  
  updateCourse: (courseId: number, data: {
    name?: string;
    credits?: number;
    capacity?: number;
    semester?: string;
    lecturer_id?: number;
    description?: string;
  }) => api.put(`/manager/courses/${courseId}`, data),
  
  deleteCourse: (courseId: number) => api.delete(`/manager/courses/${courseId}`),
  
  assignLecturer: (courseId: number, lecturerId: number) =>
    api.put(`/manager/courses/${courseId}/assign-lecturer?lecturer_id=${lecturerId}`),
  
  getFeedback: () => api.get('/manager/feedback'),
  
  getCourseStatistics: () => api.get('/manager/statistics/courses'),
  
  getGPADistribution: () => api.get('/manager/statistics/gpa'),
  
  getMessages: () => api.get('/manager/messages'),
  
  sendMessage: (data: { receiver_id: number; content: string }) =>
    api.post('/manager/messages', data),
};

// ============ Course API ============
export const courseAPI = {
  getAll: () => api.get('/courses'),
  
  getCourseDetail: (courseId: number) => api.get(`/courses/${courseId}`),
  
  getMaterials: (courseId: number) => api.get(`/courses/${courseId}/materials`),
  
  addMaterial: (courseId: number, data: {
    title: string;
    type: string;
    description?: string;
    file_path?: string;
  }) => api.post(`/courses/${courseId}/materials`, { ...data, course_id: courseId }),
  
  getAssignments: (courseId: number) => api.get(`/courses/${courseId}/assignments`),
  
  createAssignment: (courseId: number, data: {
    title: string;
    description?: string;
    deadline: string;
    max_score?: number;
  }) => api.post(`/courses/${courseId}/assignments`, { ...data, course_id: courseId }),
  
  getStudents: (courseId: number) => api.get(`/courses/${courseId}/students`),
  
  getFeedback: (courseId: number) => api.get(`/courses/${courseId}/feedback`),
  
  submitFeedback: (courseId: number, data: { comment?: string; rating: number }) =>
    api.post(`/courses/${courseId}/feedback`, { ...data, course_id: courseId }),
};

// ============ Quiz API ============
export const quizAPI = {
  getAll: (courseId?: number) => {
    const params = courseId ? `?course_id=${courseId}` : '';
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
  }) => api.post('/quizzes', data),
  
  addQuestion: (quizId: number, data: {
    question_text: string;
    option_a: string;
    option_b: string;
    option_c?: string;
    option_d?: string;
    correct_option: string;
    points?: number;
  }) => api.post(`/quizzes/${quizId}/questions`, data),
  
  startAttempt: (quizId: number) => api.post(`/quizzes/${quizId}/start`),
  
  submitAttempt: (attemptId: number, data: {
    quiz_id?: number;
    answers: Array<{ question_id: number; chosen_option: string }>;
  }) => api.post(`/quizzes/attempts/${attemptId}/submit`, data),
  
  getAttempt: (attemptId: number) => api.get(`/quizzes/attempts/${attemptId}`),
  
  getAttemptDetail: (attemptId: number) => api.get(`/quizzes/attempts/${attemptId}/detail`),
  
  getStudentAttempts: (studentId: number, quizId?: number) => {
    const params = quizId ? `?quiz_id=${quizId}` : '';
    return api.get(`/quizzes/student/${studentId}/attempts${params}`);
  },
};

// ============ Message API ============
export const messageAPI = {
  getMessages: (otherUserId?: number) => {
    const params = otherUserId ? `?other_user_id=${otherUserId}` : '';
    return api.get(`/messages${params}`);
  },
  
  sendMessage: (data: { receiver_id: number; content: string }) =>
    api.post('/messages', data),
  
  getConversations: () => api.get('/messages/conversations'),
  
  getConversation: (userId: number) => api.get(`/messages?other_user_id=${userId}`),
  
  getUnreadCount: () => api.get('/messages/unread-count'),
  
  markRead: (senderId: number) => api.post(`/messages/mark-read/${senderId}`),
  
  getAvailableUsers: () => api.get('/messages/users'),
};

export default api;
