import { useAuthState } from "react-firebase-hooks/auth";
import { auth } from "../firebase";
import { signOut } from "firebase/auth";
import Sidebar from "../components/Sidebar";
import "./Dashboard.css";

export default function Dashboard() {
  const [user, loading] = useAuthState(auth);

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner"></div>
        <p>Loading your workspace...</p>
      </div>
    );
  }

  // Landing Page (Not logged in)
  if (!user) {
    return (
      <div className="landing-container">
        <nav className="landing-navbar">
          <h1 className="logo">Tutor<span>Net</span></h1>
          <div>
            <a href="/Auth" className="btn-primary">Sign In/Up</a>
          </div>
        </nav>

        <header className="landing-hero">
          <h2>AI-Powered Learning</h2>
          <p>
            Add your courses. Upload your notes and textbooks. Ask questions. Generate mock tests.  
            Let AI accelerate your learning 🚀
          </p>
          <a href="/Auth" className="btn-cta">Get Started Free</a>
        </header>

        <section className="landing-features">
          <div className="feature">
            <h3>📘 Upload Courses</h3>
            <p>Organize your study material in one place.</p>
          </div>
          <div className="feature">
            <h3>💡 AI Study Sessions</h3>
            <p>Ask questions and get context-aware answers from your own notes.</p>
          </div>
          <div className="feature">
            <h3>📝 Mock Tests</h3>
            <p>Test yourself with quizzes generated from your course content.</p>
          </div>
        </section>
      </div>
    );
  }

  // Dashboard (Logged in)
  const handleLogout = async () => {
    await signOut(auth);
  };

  return (
    <div className="dashboard">
      <Sidebar />
      <main className="dashboard-main">
        <header className="dashboard-hero">
          <div className="user-info">
            <img src={user.photoURL} alt="Profile" className="user-avatar" />
            <div>
              <h2>Welcome back, {user.displayName} 👋</h2>
              <p className="user-email">{user.email}</p>
            </div>
          </div>
          <button onClick={handleLogout} className="btn-logout">
            Logout
          </button>
        </header>

        <section className="quick-actions">
          <div className="action-card" onClick={() => window.location.href="/courses"}>
            <h3>📘 Courses</h3>
            <p>Upload and manage your study material.</p>
          </div>
          <div className="action-card" onClick={() => window.location.href="/study"}>
            <h3>💡 Study Session</h3>
            <p>Ask questions and learn from your notes.</p>
          </div>
          <div className="action-card" onClick={() => window.location.href="/mocktest"}>
            <h3>📝 Mock Test</h3>
            <p>Test yourself with AI-generated quizzes.</p>
          </div>
        </section>
      </main>
    </div>
  );}
