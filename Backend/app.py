from dotenv import load_dotenv
from flask import Flask, request, jsonify
from services.gemini_service import generate_response

app = Flask(__name__)
load_dotenv()

@app.get("/api/test")
def test():
    q = request.args.get("q", "Say hi in one short sentence.")
    text = generate_response(q, system_instruction="You are a concise study assistant.")
    return jsonify({"ok": True, "text": text})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=True)
