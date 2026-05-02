import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from "./components/Navbar";
import Dashboard from "./pages/Dashboard";
import Auth from "./pages/Auth";
import Courses from "./pages/Courses";
import CourseDetails from "./pages/CourseDetails";
import "./styles/App.css";

export default function App() {
  return (
    <BrowserRouter>
      <Navbar />

      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/auth" element={<Auth />} />
        <Route path="/courses" element={<Courses />} />
        <Route path="/course/:courseId" element={<CourseDetails />} />
      </Routes>
    </BrowserRouter>
  );
}