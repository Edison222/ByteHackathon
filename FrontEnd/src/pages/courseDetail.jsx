import { useParams } from "react-router-dom";
import { useState, useEffect } from "react";
import { doc, getDoc } from "firebase/firestore";
import { db } from "../firebase";
import Sidebar from "../components/Sidebar";
import StudySession from "./StudySessionPage";
import MockTest from "./MockTestPage";
import CourseFiles from "./CourseFiles"; 
import "./CourseDetail.css";

export default function CourseDetail() {
  const { id } = useParams(); // courseId from URL
  const [activeTab, setActiveTab] = useState("files");
  const [courseName, setCourseName] = useState("");

  useEffect(() => {
    const fetchCourse = async () => {
      try {
        const courseRef = doc(db, "courses", id);
        const courseSnap = await getDoc(courseRef);

        if (courseSnap.exists()) {
          setCourseName(courseSnap.data().name);
        } else {
          setCourseName("Unknown Course");
        }
      } catch (error) {
        console.error("Error fetching course:", error);
      }
    };

    fetchCourse();
  }, [id]);

  return (
    <div className="course-detail-page">
      <Sidebar />
      <main className="course-detail-main">
        <h2 className="course-title">Course: {courseName}</h2>

        {/* Tab Menu */}
        <div className="tabs">
          <button
            onClick={() => setActiveTab("files")}
            className={activeTab === "files" ? "active" : ""}
          >
            📂 Files
          </button>
          <button
            onClick={() => setActiveTab("study")}
            className={activeTab === "study" ? "active" : ""}
          >
            💡 Study Session
          </button>
          <button
            onClick={() => setActiveTab("mocktest")}
            className={activeTab === "mocktest" ? "active" : ""}
          >
            📝 Mock Test
          </button>
        </div>

        {/* Tab Content */}
        <div className="tab-content">
          {activeTab === "files" && <CourseFiles courseId={id} />}
          {activeTab === "study" && <StudySession courseId={id} />}
          {activeTab === "mocktest" && <MockTest courseId={id} />}
        </div>
      </main>
    </div>
  );
}
