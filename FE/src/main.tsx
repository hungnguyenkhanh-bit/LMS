import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import "./styles/styles.css";
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

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
      <Routes>
        {/* Route login - KHONG dang AppLayout */}
        <Route path="/login" element={<LoginPage />} />

        {/* Cac route sau khi da dang nhap - dang AppLayout */}
        <Route element={<AppLayout />}>
          <Route path="/student-dashboard" element={<StudentDashboardPage />} />
          <Route path="/lecturer-dashboard" element={<LecturerDashboardPage />} />
          <Route path="/manager-dashboard" element={<ManagerDashboardPage />} />
          <Route path="/my-courses" element={<MyCoursesPage />} />
          <Route path="/student-course" element={<StudentCoursePage />} />
          <Route path="/lecturer-course" element={<LecturerCoursePage />} />
          <Route path="/student-feedback" element={<StudentFeedbackPage />} />
          <Route path="/lecturer-feedback" element={<LecturerFeedbackPage />} />
          <Route path="/quiz-taking" element={<QuizTakingPage />} />
          <Route path="/quiz-finished" element={<QuizFinishedPage />} />

          {/* sau nay em add them cac page khac o day */}
        </Route>
      </Routes>
    </BrowserRouter>
  </React.StrictMode>
);
