import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuthState } from "react-firebase-hooks/auth";
import { collection, getDocs, query, where, orderBy, limit } from "firebase/firestore";
import { auth, db } from "../firebase";

export default function Dashboard() {
  const [user, loading] = useAuthState(auth);
  const [courses, setCourses] = useState([]);
  const [coursesLoading, setCoursesLoading] = useState(true);

  useEffect(() => {
    async function fetchCourses() {
      if (!user) {
        setCoursesLoading(false);
        return;
      }

      try {
        const q = query(
          collection(db, "courses"),
          where("userId", "==", user.uid),
          orderBy("createdAt", "desc"),
          limit(5)
        );

        const snapshot = await getDocs(q);
        setCourses(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })));
      } catch (error) {
        console.error("Error fetching dashboard courses:", error);
      } finally {
        setCoursesLoading(false);
      }
    }

    fetchCourses();
  }, [user]);

  if (loading) {
    return (
      <main className="page">
        <div className="container">
          <p>Loading your workspace...</p>
        </div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="page">
        <div className="container">
          <section className="hero dashboard-hero">
            <p className="badge">AI Study Assistant</p>
            <h1>Study from your own notes, PDFs, and course material.</h1>
            <p>
              Upload your class documents, ask questions, and get answers grounded
              in your actual course content.
            </p>

            <div className="hero-actions">
              <Link to="/auth" className="primary-btn">
                Get Started
              </Link>
            </div>
          </section>

          <section className="grid">
            <div className="card">
              <h3>📘 Courses</h3>
              <p>Create separate spaces for each class.</p>
            </div>

            <div className="card">
              <h3>📄 PDF Upload</h3>
              <p>Upload lecture slides, notes, and textbooks.</p>
            </div>

            <div className="card">
              <h3>🤖 Ask AI</h3>
              <p>Ask questions answered using your uploaded files.</p>
            </div>
          </section>
        </div>
      </main>
    );
  }

  return (
    <main className="page">
      <div className="container">
        <section className="hero dashboard-hero">
          <p className="badge">TutorNet Workspace</p>

          <h1>
            Welcome back,{" "}
            <span className="gradient-text">
              {user.displayName || "Student"}
            </span>
          </h1>

          <p>
            Your AI-powered study hub is ready. Create courses, upload PDFs, and
            ask questions grounded in your own class material.
          </p>

          <div className="hero-actions">
            <Link to="/courses" className="primary-btn">
              Open Courses
            </Link>
            <Link to="/courses" className="secondary-btn">
              Add New Course
            </Link>
          </div>
        </section>

        <section className="dashboard-stats">
          <div className="stat-card">
            <span className="stat-icon">📚</span>
            <p>Total Courses</p>
            <h2>{courses.length}</h2>
          </div>

          <div className="stat-card">
            <span className="stat-icon">🧠</span>
            <p>AI Mode</p>
            <h2>Ready</h2>
          </div>

          <div className="stat-card">
            <span className="stat-icon">⚡</span>
            <p>Backend</p>
            <h2>RAG</h2>
          </div>
        </section>

        <section className="dashboard-section">
          <div className="section-header">
            <div>
              <h2>Recent Courses</h2>
              <p className="muted">Continue where you left off.</p>
            </div>

            <Link to="/courses" className="secondary-btn">
              View All
            </Link>
          </div>

          {coursesLoading ? (
            <div className="panel">
              <p className="muted">Loading courses...</p>
            </div>
          ) : courses.length === 0 ? (
            <div className="empty-state">
              <h2>No courses yet</h2>
              <p>Create your first course and start uploading PDFs.</p>
              <Link to="/courses" className="primary-btn">
                Create Course
              </Link>
            </div>
          ) : (
            <div className="grid">
              {courses.map((course) => (
                <Link
                  to={`/course/${course.id}`}
                  className="course-preview-card"
                  key={course.id}
                >
                  <div className="course-orb">✦</div>
                  <h3>{course.name}</h3>
                  <p>{course.school || "No school added"}</p>
                  <span>Open workspace →</span>
                </Link>
              ))}
            </div>
          )}
        </section>

        <section className="grid">
          <div className="card">
            <h3>🚀 Quick Start</h3>
            <p>Create a course, upload a PDF, then ask your first question.</p>
          </div>

          <div className="card">
            <h3>🔎 Source-Grounded</h3>
            <p>Answers are based on your uploaded class files, not random guesses.</p>
          </div>

          <div className="card">
            <h3>🧪 Practice Mode</h3>
            <p>Next upgrade: generate quizzes and mock tests from your notes.</p>
          </div>
        </section>
      </div>
    </main>
  );
}