from rag.embedding import embed_texts
from rag.vector_store import add_embeddings, save_index
from rag.retrieval import search_course

def add_course_content(course_id, chunks):
    if not chunks:
        return

    embeddings = embed_texts(chunks)
    add_embeddings(course_id, embeddings, chunks)
    save_index(course_id)

def search_course_content(course_id, question, k=3):
    return search_course(course_id, question, k)

def build_context(results):
    return "\n\n".join([result["chunk"] for result in results])