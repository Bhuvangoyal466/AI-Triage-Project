# Triage Buddy

Triage Buddy is a small Flask web app that demonstrates an AI-assisted symptom triage flow. Users enter basic patient details, describe symptoms, choose a severity level, and select additional symptoms. The app returns one of four urgency levels with possible conditions, a short explanation, and suggested next steps.

> **Educational project only:** Triage Buddy is not a doctor and does not provide a diagnosis or medical advice. In a real emergency, contact a trusted adult and call the appropriate local emergency number.

## Features

- Quick-start examples for chest pressure, a runny nose, and high fever
- Patient age and symptom duration inputs
- Free-text symptom description
- Severity slider from 1 to 10 with visual feedback
- Optional symptoms including sweating, nausea, shortness of breath, fever, vomiting, dizziness, headache, and cough
- Four triage levels: low, less urgent, urgent, and emergency
- AI responses through the Groq API when a key is configured
- Local rule-based fallback when no API key is available or the AI request fails

## Requirements

- Python 3
- A Groq API key (optional; the fallback rules work without one)

Install the dependencies from the project folder:

```bash
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project folder and add your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key
```

The app sends configured requests to Groq using the `openai/gpt-oss-20b` model. Keep the API key private and do not commit the `.env` file.

## Run

Start the Flask server:

```bash
python app.py
```

Open [http://localhost:5000](http://localhost:5000) in a browser.

## API

The frontend sends a `POST` request to `/api/triage` with JSON in this shape:

```json
{
	"age": 12,
	"symptoms": "runny nose and sneezing",
	"duration": "1-2 days",
	"severity": 2,
	"extras": ["Cough"]
}
```

The endpoint returns JSON containing:

```json
{
	"level": "low",
	"possible_conditions": ["Mild cold", "Tiredness", "Minor ache"],
	"reason": "...",
	"what_to_do": ["Tell a trusted adult or doctor", "Rest and drink water"],
	"source": "rules"
}
```

The `source` value is `ai` for a successful Groq response and `rules` when the local fallback is used.
