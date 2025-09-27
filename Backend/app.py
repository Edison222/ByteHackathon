from dotenv import load_dotenv
from flask import Flask, request, jsonify
from services.gemini_service import generate_response
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.chunker import chunk_text
from services.gemini_service import embed_text
from services.faiss_service import add_embeddings
from services.faiss_service import search_embeddings
from services.gemini_service import embed_text, generate_response
from services.faiss_service import embed_text_local
from services.faiss_service import add_embeddings
from services.faiss_service import get_index_size
from services.faiss_service import list_saved_indexes, get_index_size
from services.faiss_service import load_faiss
import pdfplumber
import os
import requests
from io import BytesIO
import PyPDF2

app = Flask(__name__)
load_dotenv()
CORS(app, resources={r"/*": {"origins": "*"}})


def extract_pdf_text(file_bytes: bytes) -> str:
    text = ""

    # Try PyPDF2
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        if text.strip():
            print("DEBUG: Extracted with PyPDF2, length:", len(text))
            return text
    except Exception as e:
        print("PyPDF2 failed:", e)

    # Try pdfplumber
    try:
        with pdfplumber.open(BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text += page_text + "\n"
        if text.strip():
            print("DEBUG: Extracted with pdfplumber, length:", len(text))
            return text
    except Exception as e:
        print("pdfplumber failed:", e)

    return ""

def preload_indexes():
    os.makedirs("faiss_data", exist_ok=True)
    for filename in os.listdir("faiss_data"):
        if filename.endswith(".index"):
            course_id = filename.replace(".index", "")
            load_faiss(course_id)

@app.get("/api/test")
def test():
    q = request.args.get("q", "Say hi in one short sentence.")
    text = generate_response(q, system_instruction="You are a concise study assistant.")
    return jsonify({"ok": True, "text": text})


@app.route("/upload", methods=["POST"])
def upload():
    data = request.json
    course_id = data["courseId"]
    file_url = data["fileUrl"]

    try:
        # Always download the file
        response = requests.get(file_url)
        file_bytes = response.content

        # Extract text with helper
        text = extract_pdf_text(file_bytes)

        if not text.strip():
            return jsonify({
                "status": "error",
                "message": "No text extracted from PDF. Try a different file or format."
            }), 400

        # Continue: chunk → embed → FAISS
        chunks = chunk_text(text)
        embeddings = [embed_text_local(chunk) for chunk in chunks]
        add_embeddings(course_id, embeddings, chunks)
        
        print("DEBUG chunks:", len(chunks))
        print("DEBUG embedding shape:", len(embeddings), len(embeddings[0]) if embeddings else 0)
        print("DEBUG FAISS total vectors:", get_index_size(course_id))

        return jsonify({"status": "success", "chunks_added": len(chunks)})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500



    
@app.post("/ask")
def ask():
    data = request.json
    course_id = data.get("courseId")
    question = data.get("question")

    try:
        # Step 1: Embed question locally
        q_embedding = embed_text_local(question)

        # Step 2: Search FAISS
        results = search_embeddings(course_id, q_embedding, k=3)
        context = "\n".join(results) if results else "No context found."

        # Step 3: Generate answer with Gemini
        answer = generate_response(
        f"""
        Answer this using only the context below. 
        Always provide a structured, long, and educational explanation:

        Context:
        {context}

        Question: {question}
        """,
            system_instruction=(
                "You are an expert study assistant. "
                "Always provide detailed, professor-level explanations. "
                "Structure answers with sections, examples, and summaries and easy-to-understand. "
                "If context is missing, say so clearly instead of guessing."
            )
        )

        return jsonify({"answer": answer})
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    
@app.get("/faiss-status")
def faiss_status():
    course_id = request.args.get("courseId")
    size = get_index_size(course_id)
    return jsonify({"courseId": course_id, "vectors": size})


@app.route("/faiss-list", methods=["GET"])
def faiss_list():
    try:
        courses = []
        for course_id in list_saved_indexes():
            courses.append({
                "courseId": course_id,
                "vectors": get_index_size(course_id)
            })
        return jsonify({"status": "success", "courses": courses})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    preload_indexes()
    app.run(host="127.0.0.1", port=5001, debug=True)
