import { Outlet, NavLink, useNavigate } from "react-router-dom";
import { useAuth, getNavLinks } from "../contexts/AuthContext";

export default function AppLayout() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  // Get navigation links based on user role
  const navLinks = user ? getNavLinks(user.role) : [];

  // Get user initials for avatar
  const getInitials = (name: string) => {
    if (!name) return "U";
    const parts = name.split(" ");
    if (parts.length >= 2) {
      return parts[0][0] + parts[parts.length - 1][0];
    }
    return name[0];
  };

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
          {navLinks.map((link) => (
            <NavLink key={link.path} to={link.path}>
              {link.label}
            </NavLink>
          ))}
        </nav>

        {/* User area */}
        <div className="app-user-area">
          <span style={{ marginRight: "12px", fontSize: "14px" }}>
            {user?.full_name}
          </span>
          <button className="btn btn-secondary" onClick={handleLogout}>
            Logout
          </button>
          <div className="avatar-circle" title={user?.full_name || "User"}>
            {getInitials(user?.full_name || "U")}
          </div>
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
