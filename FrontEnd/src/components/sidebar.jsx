import { Link } from "react-router-dom";

export default function Sidebar() {
  return (
    <div className="w-60 h-screen bg-gray-900 text-white flex flex-col p-4">
      <h1 className="text-2xl font-bold mb-6">Study Assistant</h1>
      <nav className="flex flex-col gap-4">
        <Link to="/courses" className="hover:text-yellow-400">📘 Courses</Link>
        <Link to="/study" className="hover:text-yellow-400">📝 Study Session</Link>
      </nav>
    </div>
  );
}
