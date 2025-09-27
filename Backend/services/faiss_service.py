import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any


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

def add_embeddings(course_id, embeddings, chunks, meta=None):
    """Add embeddings for a specific course into its FAISS index + save to disk."""
    if not embeddings:
        return

    if meta is None:
        # default meta just names the file 'notes.pdf' and no page info
        meta = [{"page": None, "source": "notes.pdf"} for _ in chunks]

    dim = len(embeddings[0])
    if course_id not in faiss_indexes:
        faiss_indexes[course_id] = {"index": faiss.IndexFlatL2(dim), "chunks": [], "meta": []}

    index_data = faiss_indexes[course_id]
    index_data["index"].add(np.array(embeddings, dtype="float32"))
    index_data["chunks"].extend(chunks)
    index_data["meta"].extend(meta)

    save_faiss(course_id)  # persist

def search_embeddings(course_id, query_embedding, k=3):
    """Return top-k results WITH scores and metadata."""
    if course_id not in faiss_indexes:
        return []
    idx = faiss_indexes[course_id]
    D, I = idx["index"].search(np.array([query_embedding], dtype="float32"), k)
    out = []
    for rank, (d, i) in enumerate(zip(D[0], I[0]), start=1):
        if i < 0:
            continue
        out.append({
            "rank": rank,
            "score": float(d),
            "text": idx["chunks"][i],
            "page": idx["meta"][i].get("page") if idx.get("meta") else None,
            "source": idx["meta"][i].get("source") if idx.get("meta") else "notes.pdf"
        })
    return out

def save_faiss(course_id):
    """Save FAISS index + chunks (+meta) for a course to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    idx = faiss_indexes[course_id]
    faiss.write_index(idx["index"], f"{DATA_DIR}/{course_id}.index")
    with open(f"{DATA_DIR}/{course_id}_chunks.txt", "w", encoding="utf-8") as f:
        for chunk in idx["chunks"]:
            f.write(chunk.replace("\n", " ") + "\n")
    # save meta 1:1
    with open(f"{DATA_DIR}/{course_id}_meta.txt", "w", encoding="utf-8") as mf:
        for m in idx.get("meta", []):
            # simple TSV: page \t source
            page = "" if m.get("page") is None else str(m["page"])
            source = m.get("source", "notes.pdf")
            mf.write(f"{page}\t{source}\n")

def load_faiss(course_id):
    """Load FAISS index + chunks (with meta) for a course from disk."""
    index_path = f"{DATA_DIR}/{course_id}.index"
    chunks_path = f"{DATA_DIR}/{course_id}_chunks.txt"
    meta_path = f"{DATA_DIR}/{course_id}_meta.txt"
    if os.path.exists(index_path) and os.path.exists(chunks_path):
        index = faiss.read_index(index_path)
        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = [line.strip() for line in f.readlines()]

        meta = []
        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as mf:
                for line in mf:
                    page_str, source = (line.rstrip("\n").split("\t", 1) + [""])[:2]
                    page = int(page_str) if page_str.isdigit() else None
                    meta.append({"page": page, "source": source or "notes.pdf"})
        else:
            meta = [{"page": None, "source": "notes.pdf"} for _ in chunks]

        faiss_indexes[course_id] = {"index": index, "chunks": chunks, "meta": meta}
        print(f"✅ Loaded FAISS index for {course_id}, vectors={index.ntotal}")


def test_search(course_id):
    """Quick test search with random vector."""
    if course_id not in faiss_indexes:
        return []
    query = np.random.rand(1, faiss_indexes[course_id]["index"].d).astype("float32")
    D, I = faiss_indexes[course_id]["index"].search(query, 2)
    return [faiss_indexes[course_id]["chunks"][i] for i in I[0]]

def list_saved_indexes():
    """Return all course_ids that have saved FAISS indexes on disk."""
    if not os.path.exists(DATA_DIR):
        return []
    return [
        f.replace(".index", "")
        for f in os.listdir(DATA_DIR)
        if f.endswith(".index")
    ]

def get_all_chunks(course_id: str) -> List[Dict[str, Any]]:
    """
    Return [{'text': str, 'page': int|None, 'source': str}] for all chunks
    currently loaded in memory for this course_id.
    Works even if 'meta' is missing by creating default meta.
    """
    if course_id not in faiss_indexes:
        return []
    idx = faiss_indexes[course_id]
    chunks = idx.get("chunks", [])
    meta = idx.get("meta")
    if not meta or len(meta) != len(chunks):
        # fallback: no meta persisted -> synthesize defaults
        meta = [{"page": None, "source": "notes.pdf"} for _ in chunks]
    return [
        {"text": t, "page": m.get("page"), "source": m.get("source", "notes.pdf")}
        for t, m in zip(chunks, meta)
    ]

def filter_chunks_by_sources(entries: List[Dict[str, Any]], allowed_sources: List[str] | None):
    """Filter list of {'text','page','source'} by filenames (or allow all if None/empty)."""
    if not allowed_sources:
        return entries
    allowed = set(allowed_sources)
    return [e for e in entries if (e.get("source") in allowed)]