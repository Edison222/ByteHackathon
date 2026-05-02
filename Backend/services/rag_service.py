from utils.chunker import chunk_text
from rag.rag_pipeline import add_course_content, search_course_content, build_context
from services.llm_service import generate_rag_answer
from utils.pdf_parser import extract_text_from_pdf
from services.firebase_storage_service import upload_pdf_to_firebase

def ingest_course_text(course_id, raw_text):
    if not raw_text or not raw_text.strip():
        return {
            "success": False,
            "message": "No text provided.",
            "chunks_added": 0
        }

    chunks = chunk_text(raw_text)

    if not chunks:
        return {
            "success": False,
            "message": "No chunks were created from the text.",
            "chunks_added": 0
        }

    add_course_content(course_id, chunks)

    return {
        "success": True,
        "message": "Course content added successfully.",
        "chunks_added": len(chunks)
    }


def ingest_pdf_file(course_id, file_storage):
    if not file_storage:
        return {
            "success": False,
            "message": "No file uploaded.",
            "chunks_added": 0
        }

    filename = file_storage.filename or ""

    if not filename.lower().endswith(".pdf"):
        return {
            "success": False,
            "message": "Only PDF files are supported.",
            "chunks_added": 0
        }

    try:
        firebase_file = upload_pdf_to_firebase(file_storage, course_id)
    except Exception as e:
        return {
            "success": False,
            "message": f"Failed to upload PDF to Firebase: {str(e)}",
            "chunks_added": 0
        }

    try:
        raw_text = extract_text_from_pdf(file_storage)
    except ValueError as e:
        return {
            "success": False,
            "message": str(e),
            "chunks_added": 0,
            "file": firebase_file
        }

    if not raw_text.strip():
        return {
            "success": False,
            "message": "No readable text was found in the PDF.",
            "chunks_added": 0,
            "file": firebase_file
        }

    chunks = chunk_text(raw_text)

    if not chunks:
        return {
            "success": False,
            "message": "No chunks were created from the PDF text.",
            "chunks_added": 0,
            "file": firebase_file
        }

    add_course_content(course_id, chunks)

    return {
        "success": True,
        "message": "PDF uploaded to Firebase and indexed successfully.",
        "chunks_added": len(chunks),
        "file": firebase_file
    }

def retrieve_course_context(course_id, question, k=3):
    if not question or not question.strip():
        return {
            "success": False,
            "message": "Question is required.",
            "results": [],
            "context": ""
        }

    results = search_course_content(course_id, question, k)
    context = build_context(results)

    return {
        "success": True,
        "message": "Relevant chunks retrieved successfully.",
        "results": results,
        "context": context
    }

def answer_course_question(course_id, question, k=3):
    if not question or not question.strip():
        return {
            "success": False,
            "message": "Question is required.",
            "results": [],
            "context": "",
            "answer": ""
        }

    results = search_course_content(course_id, question, k)

    if not results:
        return {
            "success": True,
            "message": "No relevant material found.",
            "results": [],
            "context": "",
            "answer": "I could not find relevant course material to answer that question."
        }

    context = build_context(results)
    answer = generate_rag_answer(question, context)

    return {
        "success": True,
        "message": "Answer generated successfully.",
        "results": results,
        "context": context,
        "answer": answer
    }