export default function MockTest({ courseId }) {
  const generateTest = async () => {
    const response = await fetch("http://localhost:5000/mocktest", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId, numQuestions: 5 }),
    });
    const data = await response.json();
    console.log("Mock Test:", data.questions);
  };

  return (
    <div>
      <h3>Mock Test for {courseId}</h3>
      <button onClick={generateTest} className="btn">
        Generate Mock Test
      </button>
    </div>
  );
}
