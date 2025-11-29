import LoginPage from "./pages/LoginPage";
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import "./styles/styles.css";
import AppLayout from "./components/AppLayout";
import StudentDashboardPage from "./pages/StudentDashboardPage";

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <BrowserRouter>
  <Routes>
    {/* Route login – KHÔNG dùng AppLayout */}
    <Route path="/login" element={<LoginPage />} />

    {/* Các route sau khi đã đăng nhập – dùng AppLayout */}
    <Route element={<AppLayout />}>
      <Route path="/student-dashboard" element={<StudentDashboardPage />} />

      {/* sau này em add thêm các page khác ở đây */}
    </Route>
  </Routes>
</BrowserRouter>

  </React.StrictMode>
);
