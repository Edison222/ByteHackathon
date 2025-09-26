import Sidebar from "../components/Sidebar";

export default function Courses() {
  return (
    <div className="flex">
      <Sidebar />
      <div className="flex-1 p-8">
        <h2 className="text-2xl font-bold">Your Courses</h2>
        <p className="mt-4">Upload and manage your course materials here.</p>
      </div>
    </div>
  );
}
