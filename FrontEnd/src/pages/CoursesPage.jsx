import { useState, useEffect } from "react";
import { db, auth } from "../firebase";
import {
  collection,
  addDoc,
  query,
  where,
  getDocs,
  serverTimestamp,
} from "firebase/firestore";
import { useAuthState } from "react-firebase-hooks/auth";
import Sidebar from "../components/Sidebar";
import "./Courses.css";

export default function Courses() {
  const [courseName, setCourseName] = useState("");
  const [school, setSchool] = useState("");
  const [description, setDescription] = useState("");
  const [courses, setCourses] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [user] = useAuthState(auth);

  // Fetch courses
  useEffect(() => {
    const fetchCourses = async () => {
      if (!user) return;
      const q = query(collection(db, "courses"), where("userId", "==", user.uid));
      const snapshot = await getDocs(q);
      setCourses(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })));
    };

    fetchCourses();
  }, [user]);

  // Add a new course
  const addCourse = async (e) => {
    e.preventDefault();
    if (!user) return alert("Please sign in first.");

    try {
      await addDoc(collection(db, "courses"), {
        name: courseName,
        school,
        description,
        userId: user.uid,
        createdAt: serverTimestamp(),
      });
      setCourseName("");
      setSchool("");
      setDescription("");
      setShowForm(false);
      alert("Course added!");
    } catch (error) {
      console.error("Error adding course: ", error);
    }
  };

  return (
    <div className="courses-page">
      {/* Sidebar */}
      <Sidebar />

      {/* Main content */}
      <div className="courses-main">
        <h2 className="courses-title">My Courses</h2>

        {/* If no courses */}
        {courses.length === 0 && !showForm && (
          <div className="no-courses">
            <p>You don’t have any courses yet.</p>
            <button onClick={() => setShowForm(true)} className="add-btn">
              ➕ Add Course
            </button>
          </div>
        )}

        {/* Show Add Course Form */}
        {showForm && (
          <form onSubmit={addCourse} className="course-form">
            <input
              type="text"
              placeholder="Course Name"
              value={courseName}
              onChange={(e) => setCourseName(e.target.value)}
              required
            />
            <input
              type="text"
              placeholder="School"
              value={school}
              onChange={(e) => setSchool(e.target.value)}
              required
            />
            <textarea
              placeholder="Description (optional)"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
            <div className="form-actions">
              <button type="submit">Save Course</button>
              <button
                type="button"
                onClick={() => setShowForm(false)}
                className="cancel-btn"
              >
                Cancel
              </button>
            </div>
          </form>
        )}

        {/* Show Course List */}
        {courses.length > 0 && (
          <div className="courses-header">
            <button onClick={() => setShowForm(true)} className="add-btn">
              ➕ Add Course
            </button>
          </div>
        )}

        <div className="courses-list">
          {courses.map((course) => (
            <div key={course.id} className="course-card">
              <h3>{course.name}</h3>
              <p className="school">{course.school}</p>
              <p>{course.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
