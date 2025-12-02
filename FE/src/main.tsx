import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import "./styles/styles.css";
import { AuthProvider } from "./contexts/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./components/AppLayout";
import LoginPage from "./pages/LoginPage";
import StudentDashboardPage from "./pages/StudentDashboardPage";
import LecturerDashboardPage from "./pages/LecturerDashboardPage";
import ManagerDashboardPage from "./pages/ManagerDashboardPage";
import MyCoursesPage from "./pages/MyCoursesPage";
import StudentCoursePage from "./pages/StudentCoursePage";
import LecturerCoursePage from "./pages/LecturerCoursePage";
import StudentFeedbackPage from "./pages/StudentFeedbackPage";
import LecturerFeedbackPage from "./pages/LecturerFeedbackPage";
import QuizTakingPage from "./pages/QuizTakingPage";
import QuizFinishedPage from "./pages/QuizFinishedPage";
import QuizReviewPage from "./pages/QuizReviewPage";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public route - Login */}
          <Route path="/login" element={<LoginPage />} />
          
          {/* Default redirect to login */}
          <Route path="/" element={<Navigate to="/login" replace />} />

          {/* Protected routes with AppLayout */}
          <Route element={<AppLayout />}>
            {/* Student routes */}
            <Route
              path="/student-dashboard"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <StudentDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student-course/:courseId"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <StudentCoursePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/student-feedback"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <StudentFeedbackPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/quiz-taking/:quizId"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <QuizTakingPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/quiz-finished"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <QuizFinishedPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/quiz-review/:attemptId"
              element={
                <ProtectedRoute allowedRoles={["student"]}>
                  <QuizReviewPage />
                </ProtectedRoute>
              }
            />

            {/* Lecturer routes */}
            <Route
              path="/lecturer-dashboard"
              element={
                <ProtectedRoute allowedRoles={["lecturer"]}>
                  <LecturerDashboardPage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/lecturer-course/:courseId"
              element={
                <ProtectedRoute allowedRoles={["lecturer"]}>
                  <LecturerCoursePage />
                </ProtectedRoute>
              }
            />
            <Route
              path="/lecturer-feedback"
              element={
                <ProtectedRoute allowedRoles={["lecturer"]}>
                  <LecturerFeedbackPage />
                </ProtectedRoute>
              }
            />

            {/* Manager routes */}
            <Route
              path="/manager-dashboard"
              element={
                <ProtectedRoute allowedRoles={["manager"]}>
                  <ManagerDashboardPage />
                </ProtectedRoute>
              }
            />

            {/* Shared routes - accessible by students and lecturers */}
            <Route
              path="/my-courses"
              element={
                <ProtectedRoute allowedRoles={["student", "lecturer"]}>
                  <MyCoursesPage />
                </ProtectedRoute>
              }
            />
          </Route>
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
