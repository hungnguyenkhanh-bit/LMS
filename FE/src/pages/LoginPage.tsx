import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth, getDashboardRoute } from "../contexts/AuthContext";

const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { login, isLoading, error } = useAuth();

  // State điều khiển form
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loginError, setLoginError] = useState<string | null>(null);

  // Real login function connected to backend
  const handleLogin = async () => {
    if (username.trim() === "" || password.trim() === "") {
      setLoginError("Please enter username and password!");
      return;
    }

    setLoginError(null);

    try {
      await login(username, password);
      // Get the user from localStorage after login
      const storedUser = localStorage.getItem("user");
      if (storedUser) {
        const user = JSON.parse(storedUser);
        const dashboardRoute = getDashboardRoute(user.role);
        navigate(dashboardRoute);
      }
    } catch (err) {
      setLoginError(err instanceof Error ? err.message : "Login failed. Please try again.");
    }
  };

  // Handle Enter key press
  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleLogin();
    }
  };

  return (
    <div className="auth-shell">
      {/* Top bar */}
      <header className="auth-header">
        <div className="auth-header-logo">
          <div className="avatar-circle">E</div>
          <span>E-learning</span>
        </div>
      </header>

      {/* Main content */}
      <main className="auth-main">
        <div className="auth-card">
          {/* LEFT: login form */}
          <div>
            <div className="auth-left-title">Login</div>

            <div className="form-field">
              <label className="form-label" htmlFor="username">
                Username
              </label>
              <input
                id="username"
                className="form-control"
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              />
            </div>

            <div className="form-field">
              <label className="form-label" htmlFor="password">
                Password
              </label>
              <input
                id="password"
                className="form-control"
                type="password"
                placeholder="Enter your password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                onKeyDown={handleKeyPress}
              />
            </div>

            <label className="form-checkbox-row">
              <input type="checkbox" />
              <span>Warn me before logging me into other sites.</span>
            </label>

            {/* Error message display */}
            {(loginError || error) && (
              <div style={{ color: "#dc2626", marginBottom: "12px", fontSize: "14px" }}>
                {loginError || error}
              </div>
            )}

            <button 
              className="btn-login" 
              onClick={handleLogin}
              disabled={isLoading}
            >
              {isLoading ? "Logging in..." : "Login"}
            </button>

            <div className="auth-forgot">
              <a href="#">Forgot password?</a>
            </div>
          </div>

          {/* RIGHT note */}
          <div>
            <div style={{ textAlign: "right", fontSize: 12, marginBottom: 16 }}>
              <span style={{ marginRight: 4 }}>Languages:</span>
              <a href="#" style={{ marginRight: 4 }}>
                Vietnamese
              </a>
              <a href="#">English</a>
            </div>

            <div className="auth-right-title">Please note</div>
            <p className="auth-right-text">
              The Login page enables single sign-on to multiple websites at
              E-learning...
            </p>

            <div className="auth-right-section-title">Technical support</div>
            <p className="auth-right-text">
              E-mail:{" "}
              <a href="mailto:support@elearning.edu.vn">
                support@elearning.edu.vn
              </a>
              <br />
              Tel: (84-8) 38647256 - 7204
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="auth-footer">
        © 2025 Ho Chi Minh University of Technology. All rights reserved.
      </footer>
    </div>
  );
};

export default LoginPage;
