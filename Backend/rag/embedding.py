from sentence_transformers import SentenceTransformer #loads the embedding model
import numpy as np # helps work with vectors
 
_model = SentenceTransformer("all-MiniLM-L6-v2") #T his loads your embedding model into memory.

# This makes the vector length equal to 1.
def normalize_vector(vec): # normalize = cleaner comparison between embeddings
    vec = np.array(vec).astype("float32")
    norm = np.linalg.norm(vec)
    if norm == 0:
        return vec
    return vec / norm

# This takes one string and returns one embedding vector.
def embed_text(text: str):
    embedding = _model.encode([text])[0]
    return normalize_vector(embedding)

# This takes a list of chunks (many texts) and returns a list of embeddings.
def embed_texts(texts: list[str]):
    embeddings = _model.encode(texts)
    return [normalize_vector(e) for e in embeddings]

