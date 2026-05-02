const BASE_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

export async function uploadPDF(courseId, file) {
  const formData = new FormData();
  formData.append("course_id", courseId);
  formData.append("file", file);

  const res = await fetch(`${BASE_URL}/rag/upload-pdf`, {
    method: "POST",
    body: formData,
  });

  const data = await res.json();

  if (!res.ok) {
    console.error("Upload failed:", data);
    throw new Error(data.message || "Upload failed");
  }

  return data;
}

export async function askQuestion(courseId, question, k = 3) {
  const res = await fetch(`${BASE_URL}/rag/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      course_id: courseId,
      question,
      k,
    }),
  });

  return res.json();
}