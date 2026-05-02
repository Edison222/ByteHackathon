import { useState } from "react";
import { auth } from "../firebase";
import {
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  updateProfile,
} from "firebase/auth";
import { useNavigate } from "react-router-dom";
import { GoogleAuthProvider, signInWithPopup } from "firebase/auth";

export default function Auth() {
  const [isSignup, setIsSignup] = useState(true);
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    try {
      if (isSignup) {
        const userCredential = await createUserWithEmailAndPassword(
          auth,
          email,
          password
        );

        if (name.trim()) {
          await updateProfile(userCredential.user, {
            displayName: name,
          });
        }
      } else {
        await signInWithEmailAndPassword(auth, email, password);
      }

      navigate("/");
    } catch (error) {
      alert(error.message);
    }
  };
 
  const handleGoogleSignIn = async () => {
  try {
    const provider = new GoogleAuthProvider();
    await signInWithPopup(auth, provider);
    navigate("/");
  } catch (err) {
    console.error("Google sign-in error:", err);
    alert(err.message);
  }
};
  return (
    <main className="page">
      <div className="auth-card">
        <h1>{isSignup ? "Create account" : "Welcome back"}</h1>
        <p>
          {isSignup
            ? "Start organizing your courses with TutorNet."
            : "Sign in to continue studying."}
        </p>

        <form onSubmit={handleSubmit} className="form">
          {isSignup && (
            <input
              placeholder="Full name"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
          )}

          <input
            placeholder="Email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />

          <input
            placeholder="Password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />

          <button className="primary-btn" type="submit">
            {isSignup ? "Sign Up" : "Sign In"}
          </button>
        </form>

        <button className="text-btn" onClick={() => setIsSignup(!isSignup)}>
          {isSignup
            ? "Already have an account? Sign in"
            : "Need an account? Sign up"}
        </button>
        <button type="button" className="secondary-btn" onClick={handleGoogleSignIn}>
        Continue with Google
        </button>
      </div>
    </main>
  );
}