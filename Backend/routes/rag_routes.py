from flask import Blueprint, request, jsonify
from services.rag_service import ingest_course_text, ingest_pdf_file, answer_course_question

rag_routes = Blueprint("rag_routes", __name__)


@rag_routes.route("/rag/upload", methods=["POST"])
def upload_course_material():
    data = request.get_json() or {}

    course_id = data.get("course_id")
    raw_text = data.get("text")

    if not course_id:
        return jsonify({
            "success": False,
            "message": "course_id is required."
        }), 400

    result = ingest_course_text(course_id, raw_text)
    status_code = 200 if result["success"] else 400

    return jsonify(result), status_code


@rag_routes.route("/rag/upload-pdf", methods=["POST"])
def upload_pdf_file():
    course_id = request.form.get("course_id")
    file = request.files.get("file")

    if not course_id:
        return jsonify({
            "success": False,
            "message": "course_id is required."
        }), 400

    result = ingest_pdf_file(course_id, file)
    status_code = 200 if result["success"] else 400

    return jsonify(result), status_code


@rag_routes.route("/rag/ask", methods=["POST"])
def ask_course_question():
    data = request.get_json() or {}

    course_id = data.get("course_id")
    question = data.get("question")
    k = data.get("k", 3)

    if not course_id:
        return jsonify({
            "success": False,
            "message": "course_id is required."
        }), 400

    result = answer_course_question(course_id, question, k)
    status_code = 200 if result["success"] else 400

    return jsonify(result), status_code