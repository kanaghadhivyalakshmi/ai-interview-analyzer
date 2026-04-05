from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@app.route("/")
def home():
    return render_template("index.html")  # 👈 IMPORTANT

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        data = request.get_json()

        jd = data.get("jd")
        transcript = data.get("transcript")

        # ✅ DEFINE PROMPT HERE
        prompt = f"""
Compare JD and transcript:

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
            "model": "llama-3.1-8b-instant",  # ✅ updated model
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