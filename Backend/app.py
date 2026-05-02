from dotenv import load_dotenv
load_dotenv()

from flask import Flask, jsonify
from flask_cors import CORS
from routes.rag_routes import rag_routes
from rag.vector_store import load_all_indexes

app = Flask(__name__)

CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://127.0.0.1:5173"
        ]
    }
})

load_all_indexes()
app.register_blueprint(rag_routes)

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "message": "TutorNet RAG backend is running."
    })

if __name__ == "__main__":
    app.run(debug=True)