import { signOut } from "firebase/auth";
import { auth } from "../firebase";
import { useNavigate, useLocation } from "react-router-dom";
import "./Sidebar.css";

export default function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();

  const handleLogout = async () => {
    await signOut(auth);
    navigate("/");
  };

  // helper to highlight active link
  const isActive = (path) => (location.pathname === path ? "active" : "");

  return (
    <div className="sidebar">
      <h1 className="sidebar-logo">
        Tutor<span>Net</span>
      </h1>

      <nav className="sidebar-nav">
        <button onClick={() => navigate("/")} className={isActive("/")}>
          🏠 <span>Home</span>
        </button>
        <button
          onClick={() => navigate("/courses")}
          className={isActive("/courses")}
        >
          📘 <span>Courses</span>
        </button>
      </nav>
    </div>
  );
}
