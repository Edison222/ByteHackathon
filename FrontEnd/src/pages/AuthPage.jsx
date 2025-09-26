// src/pages/AuthPage.jsx
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";
import { auth } from "../firebase";
import { useNavigate } from "react-router-dom";
import "./AuthPage.css";

export default function AuthPage() {
  const navigate = useNavigate();

  const signInWithGoogle = async () => {
    const provider = new GoogleAuthProvider();
    try {
      const result = await signInWithPopup(auth, provider);
      console.log("User:", result.user);
      navigate("/dashboard");
    } catch (error) {
      console.error("Auth error:", error);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <h1 className="auth-title">Study Assistant 📚</h1>
        <p className="auth-subtitle">
          Sign in or create an account with your Google account
        </p>
        <button onClick={signInWithGoogle} className="google-btn">
          <img
            src="https://www.svgrepo.com/show/475656/google-color.svg"
            alt="Google"
            className="google-icon"
          />
          Continue with Google
        </button>
      </div>
    </div>
  );
}
