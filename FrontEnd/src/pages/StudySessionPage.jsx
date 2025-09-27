import { useState, useRef, useEffect } from "react";
import "./StudySession.css";

export default function StudySession({ courseId }) {
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text:
        "Hi! I’m your study buddy. Ask me anything about this course, or pick a suggestion below. The more specific you are, the better I can help!",
      context: [],
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const chatEndRef = useRef(null);


  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const sendQuestion = async (qText) => {
    if (!qText?.trim() || !courseId) return;
    setErrorMsg("");

    // Add user message immediately
    setMessages((prev) => [...prev, { role: "user", text: qText }]);
    setQuestion("");
    setLoading(true);

    try {
      const res = await fetch("http://localhost:5001/ask", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ courseId, question: qText }),
      });

      if (!res.ok) throw new Error(`Server error: ${res.status}`);
      const data = await res.json();

      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: data.answer || "I couldn’t generate an answer this time.",
          context: data.context || [],
        },
      ]);
    } catch (err) {
      console.error(err);
      setErrorMsg(
        "Couldn’t reach the study engine. Check your backend and try again."
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAsk = (e) => {
    e.preventDefault();
    sendQuestion(question);
  };

  const handleSuggestion = (s) => sendQuestion(s);

  return (
    <div className="study-wrapper">
      <header className="study-header">
        <div>
          <h3>💡 Study Session</h3>
          <p className="subtle">
            Ask questions about your uploaded notes & textbooks for this course.
          </p>
        </div>
      </header>


      {/* Chat area */}
      <div className="chat-area">
        {messages.map((m, i) => (
          <div
            key={i}
            className={`msg ${m.role === "user" ? "msg-user" : "msg-assistant"}`}
          >
            <div className="bubble">
              <p className="bubble-text">{m.text}</p>
              {m.role === "assistant" && m.context && m.context.length > 0 && (
                <div className="context-box">
                  <p className="context-title">Context used:</p>
                  <ul>
                    {m.context.map((c, idx) => (
                      <li key={idx} className="context-line">
                        {c.slice(0, 220)}{c.length > 220 ? "…" : ""}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="msg msg-assistant">
            <div className="bubble">
              <div className="typing">
                <span className="dot" />
                <span className="dot" />
                <span className="dot" />
              </div>
              <p className="subtle">Analyzing your course material…</p>
            </div>
          </div>
        )}

        {!!errorMsg && (
          <div className="error-banner">
            {errorMsg}
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleAsk} className="ask-box">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a question… e.g., “Explain the proof of theorem 2.”"
          className="ask-input"
        />
        <button className="ask-btn" disabled={!question.trim() || loading}>
          {loading ? "Thinking…" : "Ask"}
        </button>
      </form>
    </div>
  );
}
