import os
import json
import urllib.request
import urllib.error

# Retrieve API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY", "")

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are an advanced AI Misinformation & Fake News Detection Engine.
Analyze the provided text/claim thoroughly.
Evaluate:
1. Factual plausibility and known verified facts.
2. Presence of sensationalist, emotionally manipulative, or clickbait language.
3. Logical inconsistencies or lack of credible sources.

IMPORTANT GUIDELINES:
- Use scientifically nuanced classifications: "Likely Authentic", "Potentially Misleading", or "High Risk of Fabrication".
- Confidence should be a float between 50.0 and 99.0 reflecting uncertainty realistically.
- Provide explainable AI reasoning highlighting key flags or tokens.

You MUST respond strictly with valid JSON conforming to this exact schema:
{
  "prediction": "Potentially Misleading" | "Likely Authentic" | "High Risk of Fabrication",
  "confidence": 85.5,
  "risk_level": "Low" | "Medium" | "High",
  "explanation": "Detailed professional reasoning...",
  "key_factors": [
    "Identified unverified statistical claims",
    "Emotionally charged framing detected",
    "Missing primary source citation"
  ],
  "sentiment": "Neutral" | "Sensationalist" | "Alarmist" | "Informative"
}
"""

def analyze_claim_with_llm(text: str) -> dict:
    if not GROQ_API_KEY:
        return {
            "prediction": "Potentially Misleading (Demo Mode)",
            "confidence": 75.0,
            "risk_level": "Medium",
            "explanation": "No GROQ_API_KEY detected in environment. Operating in mock fallback mode.",
            "key_factors": ["Demo fallback active"],
            "sentiment": "Neutral"
        }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY.strip()}",
        "Content-Type": "application/json",
        "User-Agent": "TruthGuard-Detector/1.0"
    }

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Please analyze this news article / claim:\n\n\"\"\"\n{text}\n\"\"\""}
        ],
        "temperature": 0.2,
        "response_format": {"type": "json_object"}
    }

    req = urllib.request.Request(
        GROQ_ENDPOINT,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            content = data["choices"][0]["message"]["content"]
            result = json.loads(content)
            result["model_used"] = "Groq LLaMA-3.3 70B"
            return result
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8")
        # Try fallback model if 70b has rate limit or deprecation
        try:
            payload["model"] = "llama-3.1-8b-instant"
            req2 = urllib.request.Request(
                GROQ_ENDPOINT,
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req2, timeout=20) as resp2:
                data2 = json.loads(resp2.read().decode("utf-8"))
                result2 = json.loads(data2["choices"][0]["message"]["content"])
                result2["model_used"] = "Groq LLaMA-3.1 8B (Fallback)"
                return result2
        except Exception as fallback_err:
            return {
                "prediction": "Analysis Error",
                "confidence": 0.0,
                "risk_level": "Unknown",
                "explanation": f"API request failed: {e.code} {e.reason} - {error_body}",
                "key_factors": [str(fallback_err)],
                "sentiment": "Unknown"
            }
    except Exception as e:
        return {
            "prediction": "Analysis Error",
            "confidence": 0.0,
            "risk_level": "Unknown",
            "explanation": f"Failed to connect to AI engine: {str(e)}",
            "key_factors": ["Connection failure"],
            "sentiment": "Unknown"
        }
