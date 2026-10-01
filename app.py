# 🏥 Triage Buddy - a tiny AI symptom checker (EDUCATIONAL ONLY, not real medical advice)
import os, json, requests
from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv

load_dotenv()
KEY = os.getenv("GROQ_API_KEY")
app = Flask(__name__)

# ---- The instructions we give the AI (this is called a "prompt") ----
PROMPT = """You are a school-project triage helper. This is a SIMULATION for learning.
Given a patient's details, reply with ONLY JSON in this exact shape:
{"level":"emergency|urgent|less_urgent|low",
 "possible_conditions":["3 to 4 possible conditions, never a final diagnosis"],
 "reason":"1-2 simple sentences explaining the level",
 "what_to_do":["2 to 3 simple next steps"]}
Levels: emergency = chest pain, trouble breathing, stroke signs, heavy bleeding;
urgent = high fever, severe pain, broken bone; less_urgent = mild but needs a doctor;
low = no warning signs. When unsure, choose the MORE urgent level.
Patient: """

# ---- Backup brain: simple IF rules, used when there is no key or the AI fails ----
def backup_rules(d):
    text = (d["symptoms"] + " " + " ".join(d["extras"])).lower()
    red = ["chest", "breath", "faint", "unconscious", "bleeding", "stroke", "seizure", "face drooping"]
    orange = ["fever", "vomit", "broken", "severe", "dizz", "confus"]
    if any(w in text for w in red) or (d["severity"] >= 9):
        lvl, conds = "emergency", ["Heart or lung problem", "Serious infection", "Allergic reaction"]
    elif any(w in text for w in orange) or d["severity"] >= 7:
        lvl, conds = "urgent", ["Infection", "Injury", "Dehydration"]
    elif d["severity"] >= 4:
        lvl, conds = "less_urgent", ["Common cold or flu", "Muscle strain", "Stomach upset"]
    else:
        lvl, conds = "low", ["Mild cold", "Tiredness", "Minor ache"]
    return {"level": lvl, "possible_conditions": conds,
            "reason": "Simple rule-based check (AI key not used).",
            "what_to_do": ["Tell a trusted adult or doctor", "Rest and drink water"], "source": "rules"}

def ask_groq(d):
    url = "https://api.groq.com/openai/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {KEY}"
    }

    patient = json.dumps(d)

    body = {
        "model": "openai/gpt-oss-20b",
        "messages": [
            {
                "role": "system",
                "content": PROMPT
            },
            {
                "role": "user",
                "content": patient
            }
        ],
        "response_format": {
            "type": "json_object"
        }
    }

    r = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=30
    )

    r.raise_for_status()

    text = r.json()["choices"][0]["message"]["content"]

    out = json.loads(text)
    out["source"] = "ai"

    return out
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-3.8-flash:generateContent"
    )

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": KEY
    }

    patient = json.dumps(d)

    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": PROMPT + patient
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    r = requests.post(
        url,
        headers=headers,
        json=body,
        timeout=30
    )

    if not r.ok:
        print("Gemini API Error:")
        print("Status:", r.status_code)
        print("Response:", r.text)

    r.raise_for_status()

    text = r.json()["candidates"][0]["content"]["parts"][0]["text"]

    out = json.loads(text)
    out["source"] = "ai"

    return out

@app.route("/")
def home():
    return send_from_directory(".", "index.html")

@app.route("/api/triage", methods=["POST"])
def triage():
    d = request.get_json()
    d.setdefault("extras", []); d.setdefault("severity", 5); d.setdefault("symptoms", "")
    try:
        result = ask_groq(d) if KEY else backup_rules(d)
    except Exception as e:
        print("AI problem (using backup rules):", repr(e))
        result = backup_rules(d)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False, port=5000)
