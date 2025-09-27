import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

# Store indexes per course in memory
faiss_indexes = {}
_local_model = SentenceTransformer("all-MiniLM-L6-v2")

DATA_DIR = "faiss_data"

# ========== Embedding ==========
def embed_text_local(text: str):
    """Generate a vector embedding using local sentence-transformers."""
    return _local_model.encode([text])[0]

# ========== Add & Search ==========
def get_index_size(course_id):
    if course_id in faiss_indexes:
        return faiss_indexes[course_id]["index"].ntotal
    return 0

def add_embeddings(course_id, embeddings, chunks):
    """Add embeddings for a specific course into its FAISS index + save to disk."""
    if not embeddings:
        return
    
    dim = len(embeddings[0])
    if course_id not in faiss_indexes:
        faiss_indexes[course_id] = {"index": faiss.IndexFlatL2(dim), "chunks": []}
    
    index_data = faiss_indexes[course_id]
    index_data["index"].add(np.array(embeddings).astype("float32"))
    index_data["chunks"].extend(chunks)

    save_faiss(course_id)  # ✅ persist after update

def search_embeddings(course_id, query_embedding, k=3):
    """Search top-k embeddings for a specific course."""
    if course_id not in faiss_indexes:
        return []
    index_data = faiss_indexes[course_id]
    D, I = index_data["index"].search(np.array([query_embedding]).astype("float32"), k)
    return [index_data["chunks"][i] for i in I[0]]

def test_search(course_id):
    """Quick test search with random vector."""
    if course_id not in faiss_indexes:
        return []
    query = np.random.rand(1, faiss_indexes[course_id]["index"].d).astype("float32")
    D, I = faiss_indexes[course_id]["index"].search(query, 2)
    return [faiss_indexes[course_id]["chunks"][i] for i in I[0]]

# ========== Save / Load ==========
def save_faiss(course_id):
    """Save FAISS index + chunks for a course to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    index_data = faiss_indexes[course_id]

    # Save FAISS index
    faiss.write_index(index_data["index"], f"{DATA_DIR}/{course_id}.index")

    # Save chunks
    with open(f"{DATA_DIR}/{course_id}_chunks.txt", "w", encoding="utf-8") as f:
        for chunk in index_data["chunks"]:
            f.write(chunk.replace("\n", " ") + "\n")

def load_faiss(course_id):
    """Load FAISS index + chunks for a course from disk."""
    index_path = f"{DATA_DIR}/{course_id}.index"
    chunks_path = f"{DATA_DIR}/{course_id}_chunks.txt"
    if os.path.exists(index_path) and os.path.exists(chunks_path):
        index = faiss.read_index(index_path)
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = [line.strip() for line in f.readlines()]
        faiss_indexes[course_id] = {"index": index, "chunks": chunks}
        print(f"✅ Loaded FAISS index for {course_id}, vectors={index.ntotal}")

def list_saved_indexes():
    """Return all course_ids that have saved FAISS indexes on disk."""
    if not os.path.exists(DATA_DIR):
        return []
    return [
        f.replace(".index", "")
        for f in os.listdir(DATA_DIR)
        if f.endswith(".index")
    ]
