from dotenv import load_dotenv
from flask import Flask, request, jsonify
from services.gemini_service import generate_response
from flask import Flask, request, jsonify
from flask_cors import CORS
from utils.chunker import chunk_text
from services.faiss_service import add_embeddings
from services.faiss_service import search_embeddings
from services.gemini_service import generate_response
from services.faiss_service import embed_text_local
from services.faiss_service import add_embeddings
from services.faiss_service import get_index_size
from services.faiss_service import list_saved_indexes, get_index_size
from services.faiss_service import load_faiss
from services.quiz_service import generate_mcq_quiz
import pdfplumber
import os, json, time, uuid
import requests
from io import BytesIO
import PyPDF2

app = Flask(__name__)
load_dotenv()
CORS(app, resources={r"/*": {"origins": "*"}})

QUIZ_DIR = "quizzes"
os.makedirs(QUIZ_DIR, exist_ok=True)

@app.post("/quiz/create")
def quiz_create():
    """
    Body:
    {
      "courseId": "cs101",
      "sources": ["Lecture_14.pdf", "Lecture_15.pdf"],  # optional; omit or [] => all
      "numQuestions": 6,
      "seed": 42,
      "persist": true
    }
    """
    data = request.get_json(force=True)
    course_id = data["courseId"]
    sources   = data.get("sources")          # None or list[str]
    num_q     = int(data.get("numQuestions", 6))
    seed      = data.get("seed")
    persist   = bool(data.get("persist", True))

    # make sure the FAISS index is in memory (no-op if already loaded)
    try:
        load_faiss(course_id)
    except Exception:
        pass

    # generate quiz (may raise RuntimeError if no chunks for the chosen sources)
    try:
        quiz = generate_mcq_quiz(course_id, sources, num_questions=num_q, seed=seed)
    except RuntimeError as e:
        # e.g., "No indexed chunks found for the requested sources."
        return jsonify({"ok": False, "error": str(e)}), 400
    except Exception as e:
        # model returned malformed JSON twice, or other unexpected failure
        return jsonify({"ok": False, "error": "quiz generation failed", "detail": str(e)}), 500

    # assign id and optionally persist
    ts = time.strftime("%Y%m%d-%H%M%S")
    quiz_id = f"{course_id}-{ts}-{seed or uuid.uuid4().hex[:6]}"
    quiz["quizId"] = quiz_id

    if persist:
        with open(os.path.join(QUIZ_DIR, f"{quiz_id}.json"), "w", encoding="utf-8") as f:
            json.dump(quiz, f, ensure_ascii=False, indent=2)

    return jsonify({"ok": True, **quiz})


@app.post("/quiz/grade")
def quiz_grade():
    """
    Body:
    {
      "quizId": "cs101-20250927-173000-42",
      "answers": [{"id":"Q1","answer":2}, {"id":"Q2","answer":0}, ...]
    }
    """
    data = request.get_json(force=True)
    quiz_id = data.get("quizId")
    answers = data.get("answers", [])
    if not quiz_id:
        return jsonify({"ok": False, "error": "quizId is required"}), 400

    path = os.path.join(QUIZ_DIR, f"{quiz_id}.json")
    if not os.path.exists(path):
        return jsonify({"ok": False, "error": "quiz not found"}), 404

    with open(path, "r", encoding="utf-8") as f:
        quiz = json.load(f)

    qmap = {q["id"]: q for q in quiz["questions"]}
    results = []
    correct = 0
    total = 0

    for a in answers:
        qid = a["id"]
        q = qmap.get(qid)
        if not q:
            results.append({"id": qid, "status": "unknown"})
            continue
        if q.get("type") != "mcq":
            results.append({"id": qid, "status": "unsupported"})
            continue

        total += 1
        user_idx = int(a.get("answer"))
        is_correct = (user_idx == q.get("correctIndex"))
        if is_correct:
            correct += 1
        results.append({
            "id": qid,
            "correct": is_correct,
            "correctIndex": q.get("correctIndex"),
            "explanation": q.get("explanation"),
            "citation": q.get("citation")
        })

    score = {"correct": correct, "total": total, "percent": round(100*correct/max(1,total), 1)}
    return jsonify({"ok": True, "quizId": quiz_id, "score": score, "results": results})




# replace extract_pdf_text() with page-aware version in app.py
def extract_pdf_pages(file_bytes: bytes):
    pages = []
    try:
        reader = PyPDF2.PdfReader(BytesIO(file_bytes))
        for i, page in enumerate(reader.pages, start=1):
            t = (page.extract_text() or "").strip()
            if t: pages.append({"page": i, "text": t})
    except Exception as e:
        print("PyPDF2 failed:", e)

    if not pages:
        try:
            with pdfplumber.open(BytesIO(file_bytes)) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    t = (page.extract_text() or "").strip()
                    if t: pages.append({"page": i, "text": t})
        except Exception as e:
            print("pdfplumber failed:", e)
    return pages


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
        pages = extract_pdf_pages(file_bytes)
        if not pages:
            return jsonify({"status":"error","message":"No text extracted"}), 400

        chunks, meta = [], []
        for p in pages:
            for c in chunk_text(p["text"]):   # your utils.chunker
                chunks.append(c)
                meta.append({"page": p["page"], "source": os.path.basename(file_url) or "notes.pdf"})
        pages = extract_pdf_pages(file_bytes)
        if not pages:
            return jsonify({"status":"error","message":"No text extracted"}), 400

        chunks, meta = [], []
        for p in pages:
            for c in chunk_text(p["text"]):
                chunks.append(c)
                meta.append({"page": p["page"], "source": os.path.basename(file_url) or "notes.pdf"})

        embeddings = [embed_text_local(c) for c in chunks]
        add_embeddings(course_id, embeddings, chunks, meta)
        
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

        def dedupe_results(results):
            seen = set()
            uniq = []
            for r in results:
                # normalize the text to dedupe
                key = (r["source"], (r.get("page") or -1), (r["text"] or "").strip())
                if key in seen:
                    continue
                seen.add(key)
                uniq.append(r)
            return uniq

        results = dedupe_results(results)
        # Format context
        def format_context(retrieved, max_chars=8000):
            lines, total = [], 0
            for r in retrieved:
                header = f"[S{r['rank']}] (p.{r.get('page','?')} · {r.get('source','?')} · d={r['score']:.3f})"
                body = (r["text"] or "").replace("\n", " ").strip()
                entry = f"{header}\n{body}"
                if total + len(entry) + 2 > max_chars:
                    break
                lines.append(entry)
                total += len(entry) + 2
            return "\n\n".join(lines) if lines else "No context found."

        context = format_context(results)
        # context = "\n".join(results) if results else "No context found."

        # Step 3: Generate answer with Gemini
        prompt = f"""
        ROLE
        You are a precise study assistant. Ground every answer ONLY in the provided course notes.

        CONTEXT
        {context}

        INSTRUCTIONS
        - Use only the CONTEXT to answer.
        - If the answer is not in the context, say: "I don't see this in the uploaded notes."
        - Cite supporting snippets inline using [S#].
        - Prefer higher-ranked snippets; lower distance d means closer match.
        - Be concise; use bullets when useful.
        - End with 2-3 practice questions answerable from this context.

        QUESTION
        {question}

        FINAL FORMAT
        - Direct answer with [S#] citations
        - Brief reasoning tied to [S#]
        - 2-3 practice questions
        """
        answer = generate_response(
            prompt,
            system_instruction="You are a helpful, accurate tutor."
        )

        def build_sources_footer(results):
            # De-dupe by (source, page). If page is None, show only the filename.
            seen = set()
            lines = []
            for r in results:
                key = (r.get("source") or "notes.pdf", r.get("page"))
                if key in seen:
                    continue
                seen.add(key)
                fname = key[0]
                page = key[1]
                if page is None:
                    lines.append(f"- {fname}")
                else:
                    lines.append(f"- {fname}, p. {page}")
            if not lines:
                return ""
            return "\n\nSources:\n" + "\n".join(lines)
        
        footer = build_sources_footer(results)
        if footer:
            # Ensure a blank line between answer and footer
            answer = (answer.rstrip() + "\n\n" + footer).strip()


        # at the end of /ask
        return jsonify({
            "answer": answer,
            "sources": [
                {"s": r["rank"], "source": r.get("source"), "page": r.get("page"),
                "score": r.get("score"), "preview": (r.get("text") or "")[:280]}
                for r in results
            ]
        })


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
