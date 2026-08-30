import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext.jsx";

export default function Navbar() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <nav className="navbar navbar-expand navbar-glass">
      <div className="container">
        <Link className="navbar-brand d-flex align-items-center" to="/">
          <span className="brand-mark">H</span>
          CampusHire
        </Link>
        <div className="d-flex w-100 align-items-center">
          <ul className="navbar-nav me-auto">
            {user && (
              <li className="nav-item">
                <Link
                  className="nav-link"
                  to={
                    user.role === "company"
                      ? "/company"
                      : user.role === "admin"
                        ? "/admin"
                        : "/student"
                  }
                >
                  Dashboard
                </Link>
              </li>
            )}
          </ul>
          <ul className="navbar-nav align-items-center">
            {user ? (
              <>
                <li className="nav-item me-2">
                  <span className="nav-link">
                    {user.full_name} <span className="role-pill">{user.role}</span>
                  </span>
                </li>
                <li className="nav-item">
                  <button className="btn btn-primary btn-sm" onClick={handleLogout}>
                    Logout
                  </button>
                </li>
              </>
            ) : (
              <>
                <li className="nav-item">
                  <Link className="nav-link" to="/login">
                    Login
                  </Link>
                </li>
                <li className="nav-item ms-2">
                  <Link className="btn btn-primary btn-sm" to="/signup">
                    Sign up free
                  </Link>
                </li>
              </>
            )}
          </ul>
        </div>
      </div>
    </nav>
  );
}
