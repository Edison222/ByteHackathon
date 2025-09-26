import Sidebar from "../components/Sidebar";
import "./Dashboard.css";

export default function Dashboard() {
  return (
    <div className="dashboard">
      <Sidebar />
      <main className="dashboard-main">
        <div className="dashboard-header">
          <h2>Welcome to Your Dashboard</h2>
          <p>Choose a section from the sidebar to get started.</p>
        </div>

        <div className="dashboard-cards">
          <div className="card">
            <h3>📘 Courses</h3>
            <p>Upload and manage your study materials.</p>
          </div>
          <div className="card">
            <h3>💡 Study Session</h3>
            <p>Chat with your notes and get personalized answers.</p>
          </div>
          <div className="card">
            <h3>📝 Mock Test</h3>
            <p>Generate quizzes to test your knowledge.</p>
          </div>
        </div>
      </main>
    </div>
  );
}
