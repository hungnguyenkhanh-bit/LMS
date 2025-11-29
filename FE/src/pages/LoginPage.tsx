import React from "react";

const LoginPage: React.FC = () => {
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
              />
            </div>

            <label className="form-checkbox-row">
              <input type="checkbox" />
              <span>Warn me before logging me into other sites.</span>
            </label>

            <button className="btn-login">Login</button>

            <div className="auth-forgot">
              <a href="#">Forgot password?</a>
            </div>
          </div>

          {/* RIGHT: note + support */}
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
              E-learning. This means that you only have to enter your user name
              and password once for websites that subscribe to the Login page.
            </p>
            <p className="auth-right-text">
              You will need to use your E-learning Username and password to log
              in to this site. The &quot;E-learning&quot; account provides
              access to many resources including the E-learning Information
              System, e-mail, ...
            </p>
            <p className="auth-right-text">
              For security reasons, please Exit your web browser when you are
              done accessing services that require authentication!
            </p>

            <div className="auth-right-section-title">Technical support</div>
            <p className="auth-right-text">
              E-mail: <a href="mailto:support@elearning.edu.vn">support@elearning.edu.vn</a>
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
