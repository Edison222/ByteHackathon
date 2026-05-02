import { useState } from "react";
import { useParams } from "react-router-dom";
import { uploadPDF, askQuestion } from "../services/api";

export default function CourseDetails() {
  const { courseId } = useParams();

  const [file, setFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState("");
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([]);
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);

  const handleUpload = async (e) => {
    e.preventDefault();

    if (!file) {
      alert("Choose a PDF first.");
      return;
    }

    setIsUploading(true);
    setUploadStatus("Uploading and indexing PDF...");

    try {
      const data = await uploadPDF(courseId, file);

      if (!data.success) {
        setUploadStatus(data.message || "Upload failed.");
        return;
      }

      setUploadStatus(
        `Uploaded ${data.file?.filename || "PDF"} — ${data.chunks_added} chunks added.`
      );
      setFile(null);
    } catch (error) {
      console.error(error);
      setUploadStatus("Upload failed. Check backend.");
    } finally {
      setIsUploading(false);
    }
  };

  const handleAsk = async (e) => {
    e.preventDefault();

    if (!question.trim()) return;

    const userQuestion = question;
    setQuestion("");

    setMessages((prev) => [
      ...prev,
      { role: "user", content: userQuestion },
    ]);

    setIsAsking(true);

    try {
      const data = await askQuestion(courseId, userQuestion);

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: data.answer || data.message || "No answer returned.",
        },
      ]);
    } catch (error) {
      console.error(error);
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content: "Something went wrong. Check your backend.",
        },
      ]);
    } finally {
      setIsAsking(false);
    }
  };

  return (
    <main className="page">
      <div className="container">
        <div className="section-header">
          <div>
            <h1>Course Workspace</h1>
            <p className="muted">Course ID: {courseId}</p>
          </div>
        </div>

        <section className="two-column">
          <div className="panel">
            <h2>Upload PDF</h2>
            <p className="muted">
              Upload course notes, slides, or textbooks. TutorNet will index it
              for AI search.
            </p>

            <form onSubmit={handleUpload} className="form">
              <input
                type="file"
                accept="application/pdf"
                onChange={(e) => setFile(e.target.files[0])}
              />

              <button className="primary-btn" disabled={isUploading}>
                {isUploading ? "Processing..." : "Upload PDF"}
              </button>
            </form>

            {uploadStatus && <p className="status">{uploadStatus}</p>}
          </div>

          <div className="panel chat-panel">
            <h2>Ask TutorNet AI</h2>

            <div className="chat-box">
              {messages.length === 0 ? (
                <p className="muted">
                  Ask something based on the PDFs you uploaded.
                </p>
              ) : (
                messages.map((message, index) => (
                  <div
                    key={index}
                    className={
                      message.role === "user"
                        ? "message user-message"
                        : "message ai-message"
                    }
                  >
                    {message.content}
                  </div>
                ))
              )}

              {isAsking && <p className="muted">Thinking...</p>}
            </div>

            <form onSubmit={handleAsk} className="chat-form">
              <input
                placeholder="Ask a question..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
              />

              <button className="primary-btn" disabled={isAsking}>
                Ask
              </button>
            </form>
          </div>
        </section>
      </div>
    </main>
  );
}