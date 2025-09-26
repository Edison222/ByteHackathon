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

export default function Courses() {
  const [courseName, setCourseName] = useState("");
  const [description, setDescription] = useState("");
  const [courses, setCourses] = useState([]);

  const user = auth.currentUser; // currently signed-in user

  // Fetch courses for this user
  useEffect(() => {
    const fetchCourses = async () => {
      if (!user) return;
      const q = query(
        collection(db, "courses"),
        where("userId", "==", user.uid)
      );
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
        description,
        userId: user.uid,
        createdAt: serverTimestamp(),
      });
      setCourseName("");
      setDescription("");
      alert("Course added!");
    } catch (error) {
      console.error("Error adding course: ", error);
    }
  };

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-4">My Courses</h2>

      {/* Add Course Form */}
      <form onSubmit={addCourse} className="mb-6 space-y-2">
        <input
          type="text"
          placeholder="Course Name"
          value={courseName}
          onChange={(e) => setCourseName(e.target.value)}
          className="border rounded px-3 py-2 w-full"
          required
        />
        <textarea
          placeholder="Description (optional)"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          className="border rounded px-3 py-2 w-full"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Add Course
        </button>
      </form>

      {/* Course List */}
      <ul className="space-y-3">
        {courses.map((course) => (
          <li
            key={course.id}
            className="border p-4 rounded shadow hover:shadow-md transition"
          >
            <h3 className="font-semibold">{course.name}</h3>
            <p className="text-gray-600">{course.description}</p>
          </li>
        ))}
      </ul>
    </div>
  );
}