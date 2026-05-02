import { useEffect, useState } from "react";
import { auth, db } from "../firebase";
import { useAuthState } from "react-firebase-hooks/auth";
import {
  addDoc,
  collection,
  deleteDoc,
  doc,
  getDocs,
  query,
  serverTimestamp,
  where,
} from "firebase/firestore";
import { useNavigate } from "react-router-dom";

export default function Courses() {
  const [user, authLoading] = useAuthState(auth);
  const [courses, setCourses] = useState([]);
  const [name, setName] = useState("");
  const [school, setSchool] = useState("");
  const [description, setDescription] = useState("");
  const [showForm, setShowForm] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    async function fetchCourses() {
      if (!user) return;

      const q = query(
        collection(db, "courses"),
        where("userId", "==", user.uid)
      );

      const snapshot = await getDocs(q);
      setCourses(snapshot.docs.map((d) => ({ id: d.id, ...d.data() })));
    }

    fetchCourses();
  }, [user]);

  const handleAddCourse = async (e) => {
    e.preventDefault();

    if (!user) return;

    const docRef = await addDoc(collection(db, "courses"), {
      name,
      school,
      description,
      userId: user.uid,
      createdAt: serverTimestamp(),
    });

    setCourses((prev) => [
      {
        id: docRef.id,
        name,
        school,
        description,
        userId: user.uid,
      },
      ...prev,
    ]);

    setName("");
    setSchool("");
    setDescription("");
    setShowForm(false);
  };

  const handleDelete = async (courseId) => {
    await deleteDoc(doc(db, "courses", courseId));
    setCourses((prev) => prev.filter((c) => c.id !== courseId));
  };

  if (authLoading) {
    return (
      <main className="page">
        <div className="container">Loading...</div>
      </main>
    );
  }

  if (!user) {
    return (
      <main className="page">
        <div className="container">
          <h1>Please sign in first.</h1>
        </div>
      </main>
    );
  }

  return (
    <main className="page">
      <div className="container">
        <div className="section-header">
          <div>
            <h1>My Courses</h1>
            <p>Create a course, upload PDFs, and ask AI questions.</p>
          </div>

          <button className="primary-btn" onClick={() => setShowForm(true)}>
            Add Course
          </button>
        </div>

        {showForm && (
          <form onSubmit={handleAddCourse} className="form panel">
            <input
              placeholder="Course name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
            />

            <input
              placeholder="School"
              value={school}
              onChange={(e) => setSchool(e.target.value)}
              required
            />

            <textarea
              placeholder="Description optional"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />

            <div className="row">
              <button className="primary-btn" type="submit">
                Save Course
              </button>
              <button
                className="secondary-btn"
                type="button"
                onClick={() => setShowForm(false)}
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        <section className="grid">
          {courses.map((course) => (
            <div key={course.id} className="card">
              <h3>{course.name}</h3>
              <p className="muted">{course.school}</p>
              <p>{course.description || "No description yet."}</p>

              <div className="row">
                <button
                  className="primary-btn"
                  onClick={() => navigate(`/course/${course.id}`)}
                >
                  Open
                </button>

                <button
                  className="delete-btn"
                  onClick={() => handleDelete(course.id)}
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </section>

        {courses.length === 0 && !showForm && (
          <div className="empty-state">
            <h2>No courses yet</h2>
            <p>Create your first course to upload material.</p>
          </div>
        )}
      </div>
    </main>
  );
}