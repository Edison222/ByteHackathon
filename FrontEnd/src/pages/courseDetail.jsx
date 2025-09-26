import { useParams } from "react-router-dom";
import Sidebar from "../components/Sidebar";

export default function CourseDetail() {
  const { id } = useParams();

  return (
    <div className="course-detail-page">
      <Sidebar />
      <main className="course-detail-main">
        <h2>Course Details for ID: {id}</h2>
        <p>Here you will upload notes, files, and textbooks.</p>
        {/* TODO: Add upload form + file list */}
      </main>
    </div>
  );
}
