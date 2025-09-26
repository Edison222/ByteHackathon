import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

const firebaseConfig = {
  apiKey: "AIzaSyBgiAhlWZJjoCEWRU98V4C4TbMxjSVlnx4",
  authDomain: "tutornet-c6265.firebaseapp.com",
  projectId: "tutornet-c6265",
  storageBucket: "tutornet-c6265.appspot.com",  // ✅ fixed
  messagingSenderId: "920582927745",
  appId: "1:920582927745:web:28b86c591a84ad0ae5a480",
  measurementId: "G-5QLVM36Z9D"
};

const app = initializeApp(firebaseConfig);

export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);
