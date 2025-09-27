import { useState, useEffect } from "react";
import { db, storage, auth } from "../firebase";
import {
  collection,
  addDoc,
  query,
  where,
  getDocs,
  serverTimestamp,
  orderBy,
} from "firebase/firestore";
import { ref, uploadBytes, getDownloadURL } from "firebase/storage";
import { useAuthState } from "react-firebase-hooks/auth";
import "./CourseFiles.css";

export default function CourseFiles({ courseId }) {
  const [user] = useAuthState(auth);
  const [file, setFile] = useState(null);
  const [files, setFiles] = useState([]);

  // Fetch uploaded files
  useEffect(() => {
    const fetchFiles = async () => {
      if (!user) return;
      const q = query(
        collection(db, "courseFiles"),
        where("courseId", "==", courseId)
        );
      const snapshot = await getDocs(q);
      setFiles(snapshot.docs.map((doc) => ({ id: doc.id, ...doc.data() })));
    };

    fetchFiles();
  }, [user, courseId]);

  // Handle upload
  const handleUpload = async () => {
  if (!file || !user) return alert("No file selected.");

  try {
    // Upload file to Firebase Storage
    const storageRef = ref(storage, `courses/${courseId}/${file.name}`);
    await uploadBytes(storageRef, file);
    const downloadURL = await getDownloadURL(storageRef);

    // Save metadata in Firestore
    await addDoc(collection(db, "courseFiles"), {
      courseId,
      userId: user.uid,
      filename: file.name,
      url: downloadURL,
      uploadedAt: serverTimestamp(),
    });

    // Call backend to preprocess + embed into FAISS
    await fetch("http://localhost:5001/upload", {
      method: "POST",
      body: JSON.stringify({ courseId, fileUrl: downloadURL }),
      headers: { "Content-Type": "application/json" },
    });

    setFile(null);
    alert("✅ File uploaded and embedded!");
    window.location.reload();
  } catch (error) {
    console.error("Upload failed:", error);
    alert("❌ Upload failed. Check console.");
  }
};

  return (
    <div className="course-files">
      <h3 className="section-title">📂 Course Files</h3>
      <p className="note">
        ⚠️ Please make sure your uploaded files are properly named (e.g., “Chapter1_Notes.pdf”).
      </p>
      {/* Upload Area */}
        <div className="upload-box">
        <input
            type="file"
            onChange={(e) => setFile(e.target.files[0])}
            className="file-input"
        />
        <button
            onClick={handleUpload}
            className="upload-btn"
            disabled={!file} // disable if no file
        >
            Upload
        </button>
        </div>

        {/* Show selected file + clear option */}
        {file && (
        <div className="selected-file">
            <div className="selected-file-info">
            <p>📄 <strong>{file.name}</strong></p>
            <p className="file-meta">
                Size: {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
            </div>
            <button className="clear-btn" onClick={() => setFile(null)}>
            ❌ Clear
            </button>
        </div>
        )}

      {/* File List */}
      <div className="files-list">
        {files.length === 0 ? (
          <p className="empty-msg">No files uploaded yet.</p>
        ) : (
          files.map((f) => (
            <div key={f.id} className="file-card">
              <div className="file-info">
                <h4>{f.filename}</h4>
                <p className="meta">
                  Uploaded:{" "}
                  {f.uploadedAt?.toDate
                    ? f.uploadedAt.toDate().toLocaleString()
                    : "Just now"}
                </p>
              </div>
              <a
                href={f.url}
                target="_blank"
                rel="noreferrer"
                className="download-btn"
              >
                ⬇️ Download
              </a>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
