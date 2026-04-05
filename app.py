from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

# ✅ NEW IMPORTS FOR RAG
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

load_dotenv()
app = Flask(__name__)
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ✅ ---------------- RAG SETUP ----------------

# Sample knowledge base (you can expand this later)
documents = [
    "Good communication skills are important in interviews.",
    "Candidates should explain projects clearly with examples.",
    "Problem-solving and coding skills are essential for software roles.",
    "Confidence and clarity are key during interviews.",
    "Candidates should align their answers with job requirements."
]

# Load embedding model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# Convert documents to embeddings
doc_embeddings = embed_model.encode(documents)

# Create FAISS index
dimension = len(doc_embeddings[0])
index = faiss.IndexFlatL2(dimension)
index.add(np.array(doc_embeddings))

# Retrieval function
def retrieve_context(query):
    query_embedding = embed_model.encode([query])
    D, I = index.search(np.array(query_embedding), k=2)
    return [documents[i] for i in I[0]]

# ✅ ------------------------------------------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()

        jd = data.get("jd")
        transcript = data.get("transcript")

        # ✅ RAG: Retrieve relevant context
        query = jd + " " + transcript
        retrieved_docs = retrieve_context(query)
        context = "\n".join(retrieved_docs)

        # ✅ UPDATED PROMPT WITH CONTEXT
        prompt = f"""
Use the following context to evaluate the candidate:

Context:
{context}

JD:
{jd}

Transcript:
{transcript}

Give score, strengths, weaknesses, suggestions.
"""

        url = "https://api.groq.com/openai/v1/chat/completions"

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama-3.1-8b-instant",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }

        response = requests.post(url, json=payload, headers=headers)
        result = response.json()

        print("GROQ RESPONSE:", result)

        if "choices" in result:
            content = result["choices"][0]["message"]["content"]
        else:
            content = result.get("error", {}).get("message", "Unknown error")

        return jsonify({"result": content})

    except Exception as e:
        return jsonify({"result": f"Error: {str(e)}"})

if __name__ == "__main__":
    app.run(debug=True)