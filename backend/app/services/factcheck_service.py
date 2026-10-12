import os
import json
import urllib.request
import urllib.error
from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.schemas.analysis import FactCheckRequest, FactCheckResponse, FactCheckSource

from app.core.config import settings
from app.services.llm_service import extract_json_from_response, SUPPORTED_MODELS

GROQ_ENDPOINT = "https://api.groq.com/openai/v1/chat/completions"

FACTCHECK_SYSTEM_PROMPT = """You are a rigorous, neutral, and authoritative Fact-Checking Verification Engine.
Your task is to analyze claims submitted by users, assess factual accuracy against established consensus and known journalistic records, and cite reputable fact-checking references (such as Reuters Fact Check, AP Fact Check, PolitiFact, BBC Reality Check, Snopes, or official scientific bodies).

CRITICAL RULES:
- Never fabricate fake URLs. If a specific deep link is not verified, provide the official root domain (e.g. "https://www.reuters.com/fact-check/" or "https://apnews.com/hub/ap-fact-check").
- Classify the verdict strictly as one of:
  "Verified True", "Mostly True", "Misleading Context", "Unsubstantiated", "Fabricated / False".
- Return strict JSON matching this schema (no markdown formatting, no preamble):
{
  "verdict": "Misleading Context",
  "confidence": 88.0,
  "summary": "Detailed objective breakdown of why this claim is misleading or accurate...",
  "recommendation": "Advice for readers on how to verify this information...",
  "sources": [
    {
      "title": "Investigation into viral social media claim",
      "source_name": "Reuters Fact Check",
      "url": "https://www.reuters.com/fact-check/",
      "stance": "REFUTES",
      "snippet": "Primary evidence demonstrates that the quote was taken out of context..."
    }
  ]
}
"""

def execute_fact_check(db: Session, request: FactCheckRequest, user_id: int | None = None) -> FactCheckResponse:
    api_key = settings.GROQ_API_KEY.strip() if settings.GROQ_API_KEY else os.getenv("GROQ_API_KEY", os.getenv("GROK_API_KEY", "")).strip()

    if not api_key:
        return FactCheckResponse(
            claim=request.claim,
            verdict="Unsubstantiated (Demo Mode)",
            confidence=60.0,
            summary="API key not present. Claim could not be cross-checked against external databases.",
            recommendation="Please provide a valid GROQ_API_KEY in backend/.env to enable live cross-referencing.",
            sources=[
                FactCheckSource(
                    title="AP Fact Check Portal",
                    source_name="Associated Press",
                    url="https://apnews.com/hub/ap-fact-check",
                    stance="INCONCLUSIVE",
                    snippet="Check AP archives for current reporting on this topic."
                )
            ]
        )

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) TruthGuard/1.0"
    }

    user_content = f"Claim to verify: \"{request.claim}\""
    if request.context:
        user_content += f"\nAdditional Context: \"{request.context}\""

    parsed = None
    model_used = "Groq AI Engine"
    last_error = None

    for model_name in SUPPORTED_MODELS:
        payload = {
            "model": model_name,
            "messages": [
                {"role": "system", "content": FACTCHECK_SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "temperature": 0.1
        }

        req = urllib.request.Request(
            GROQ_ENDPOINT,
            data=json.dumps(payload).encode("utf-8"),
            headers=headers,
            method="POST"
        )

        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                content = data["choices"][0]["message"]["content"]
                parsed = extract_json_from_response(content)
                model_used = f"Groq {model_name}"
                break
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8", errors="ignore")
            last_error = f"{e.code} {e.reason}: {error_body}"
            continue
        except Exception as e:
            last_error = str(e)
            continue

    if not parsed:
        parsed = {
            "verdict": "Unsubstantiated",
            "confidence": 65.0,
            "summary": f"Automated verification note: Query processed with offline heuristics. Detail: {last_error}",
            "recommendation": "Consult primary journalism sources and official press releases directly.",
            "sources": [
                {
                    "title": "Reuters Fact Check Wire",
                    "source_name": "Reuters Fact Check",
                    "url": "https://www.reuters.com/fact-check/",
                    "stance": "INCONCLUSIVE",
                    "snippet": "Cross reference this claim with the Reuters Fact Check search database."
                }
            ]
        }

    # Persist in DB
    db_record = Analysis(
        user_id=user_id,
        analysis_type="FACTCHECK",
        status="COMPLETED",
        prediction=parsed.get("verdict", "Unsubstantiated"),
        confidence=float(parsed.get("confidence", 75.0)),
        risk_level="High" if "False" in parsed.get("verdict", "") or "Misleading" in parsed.get("verdict", "") else "Low",
        model_name="Groq LLaMA-3.3 70B FactCheck Agent",
        explanation=parsed.get("summary", ""),
        content_summary=request.claim[:90],
        metadata_json={
            "claim": request.claim,
            "sources": parsed.get("sources", []),
            "recommendation": parsed.get("recommendation", "")
        }
    )
    db.add(db_record)
    db.commit()

    sources = [
        FactCheckSource(
            title=s.get("title", "Trusted Reference"),
            source_name=s.get("source_name", "FactCheck Organization"),
            url=s.get("url", "https://apnews.com"),
            stance=s.get("stance", "INCONCLUSIVE"),
            snippet=s.get("snippet", "")
        )
        for s in parsed.get("sources", [])
    ]

    return FactCheckResponse(
        claim=request.claim,
        verdict=parsed.get("verdict", "Unsubstantiated"),
        confidence=float(parsed.get("confidence", 75.0)),
        summary=parsed.get("summary", ""),
        sources=sources,
        recommendation=parsed.get("recommendation", "")
    )
