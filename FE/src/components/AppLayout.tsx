import { Outlet, Link, NavLink } from "react-router-dom";

export default function AppLayout() {
  return (
    <div className="app-shell">
      {/* Header */}
      <header className="app-header">
        {/* Logo */}
        <div className="app-logo">
          {/* sau này thay bằng <img src="/logo.png" /> nếu muốn */}
          <div className="avatar-circle">E</div>
          <span className="app-logo-text">E-learning</span>
        </div>

        {/* Nav */}
        <nav className="app-nav">
          <NavLink to="/" end>
            Dashboard
          </NavLink>
          <NavLink to="/courses">My Courses</NavLink>
          <NavLink to="/feedback">Write Feedback</NavLink>
        </nav>

        {/* User area */}
        <div className="app-user-area">
          <button className="btn btn-secondary">Logout</button>
          <div className="avatar-circle">A</div>
        </div>
      </header>

      {/* Main content */}
      <main className="app-main">
        <div className="app-main-inner">
          {/* Các page con sẽ render ở đây */}
          <Outlet />
        </div>
      </main>

      {/* Footer */}
      <footer className="app-footer">
        <span>Quick Links · Legal</span>
        <span>Settings ⚙️</span>
      </footer>
    </div>
  );
}
