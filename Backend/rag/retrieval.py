import numpy as np
from rag.embedding import embed_text
from rag.vector_store import get_index

def search_course(course_id, question, k=3):
    index_data = get_index(course_id)

    if not index_data:
        return []

    index = index_data["index"]
    chunks = index_data["chunks"]

    if index.ntotal == 0:
        return []

    query_embedding = embed_text(question)

    k = min(k, index.ntotal)

    D, I = index.search(
        np.array([query_embedding]).astype("float32"),
        k
    )

    results = []
    for score, i in zip(D[0], I[0]):
        if i != -1 and 0 <= i < len(chunks):
            results.append({
                "chunk": chunks[i],
                "score": float(score)
            })

    return results