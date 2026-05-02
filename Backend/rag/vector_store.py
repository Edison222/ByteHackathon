import faiss
import numpy as np
import os
import json
from rag.embedding import embed_texts

faiss_indexes = {}
DATA_DIR = "faiss_data"


def create_index(dim):
    return faiss.IndexFlatIP(dim)  #This creates: a container that stores vectors and lets you search them fast


# Function to get current index size
def get_index_size(course_id):
    if course_id in faiss_indexes:
        return faiss_indexes[course_id]["index"].ntotal
    return 0

# Function to create course storage if missing
def ensure_course_index(course_id, dim):
    if course_id not in faiss_indexes:
        faiss_indexes[course_id] = {
            "index": create_index(dim),
            "chunks": []
        }


def add_embeddings(course_id, embeddings, chunks):
    if not embeddings or not chunks:
        return

    if len(embeddings) != len(chunks):
        raise ValueError("Number of embeddings must match number of chunks.")

    dim = len(embeddings[0])
    ensure_course_index(course_id, dim)

    index_data = faiss_indexes[course_id]
    index_data["index"].add(np.array(embeddings).astype("float32"))
    index_data["chunks"].extend(chunks)


def get_index(course_id):
    return faiss_indexes.get(course_id)


def save_index(course_id):
    if course_id not in faiss_indexes:
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    index_data = faiss_indexes[course_id]

    faiss.write_index(index_data["index"], f"{DATA_DIR}/{course_id}.index")

    with open(f"{DATA_DIR}/{course_id}_chunks.json", "w", encoding="utf-8") as f:
        json.dump(index_data["chunks"], f, ensure_ascii=False, indent=2)


def load_index(course_id):
    index_path = f"{DATA_DIR}/{course_id}.index"
    chunks_path = f"{DATA_DIR}/{course_id}_chunks.json"

    if os.path.exists(index_path) and os.path.exists(chunks_path):
        index = faiss.read_index(index_path)

        with open(chunks_path, "r", encoding="utf-8") as f:
            chunks = json.load(f)

        faiss_indexes[course_id] = {
            "index": index,
            "chunks": chunks
        }

        print(f"✅ Loaded index for {course_id}, vectors={index.ntotal}")

def list_saved_indexes():
    if not os.path.exists(DATA_DIR):
        return []

    return [
        f.replace(".index", "")
        for f in os.listdir(DATA_DIR)
        if f.endswith(".index")
    ]

def load_all_indexes():
    for course_id in list_saved_indexes():
        load_index(course_id)

