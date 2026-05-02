import { Link, useNavigate } from "react-router-dom";
import { useAuthState } from "react-firebase-hooks/auth";
import { signOut } from "firebase/auth";
import { auth } from "../firebase";
import "./Navbar.css";

export default function Navbar() {
  const [user] = useAuthState(auth);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await signOut(auth);
    navigate("/");
  };

  return (
    <nav className="navbar">
      <div className="nav-container">
        <Link to="/" className="nav-logo">
          Tutor<span>Net</span>
        </Link>

        <div className="nav-links">
          {user && <Link to="/courses">Courses</Link>}

          {user ? (
            <button onClick={handleLogout} className="nav-button danger">
              Logout
            </button>
          ) : (
            <Link to="/auth" className="nav-button">
              Sign In
            </Link>
          )}
        </div>
      </div>
    </nav>
  );
}