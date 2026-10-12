import time
from sqlalchemy.orm import Session
from app.models.analysis import Analysis
from app.schemas.analysis import TextAnalysisRequest, AnalysisResult
from app.services.llm_service import analyze_claim_with_llm

def process_text_analysis(db: Session, request: TextAnalysisRequest, user_id: int | None = None) -> AnalysisResult:
    start_time = time.time()
    
    # 1. Run LLM Misinformation / Fake News Pipeline via Groq Cloud
    ai_output = analyze_claim_with_llm(request.text)
    
    elapsed_ms = int((time.time() - start_time) * 1000)
    
    prediction = ai_output.get("prediction", "Potentially Misleading")
    confidence = float(ai_output.get("confidence", 85.0))
    risk_level = ai_output.get("risk_level", "Medium")
    explanation = ai_output.get("explanation", "The article displays sensationalist indicators and unverified claims.")
    key_factors = ai_output.get("key_factors", [])
    model_name = ai_output.get("model_used", "Groq LLaMA-3.3 70B")
    
    # Content summary (first 100 characters)
    summary = (request.text[:97] + "...") if len(request.text) > 100 else request.text
    
    # 2. Persist in database
    db_record = Analysis(
        user_id=user_id,
        analysis_type="TEXT",
        status="COMPLETED",
        prediction=prediction,
        confidence=confidence,
        risk_level=risk_level,
        model_name=model_name,
        explanation=explanation,
        content_summary=summary,
        metadata_json={
            "key_factors": key_factors,
            "sentiment": ai_output.get("sentiment", "Neutral"),
            "headline": request.headline,
            "source_url": request.source_url
        },
        processing_time_ms=elapsed_ms
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    
    return AnalysisResult(
        id=db_record.id,
        analysis_type="TEXT",
        prediction=prediction,
        confidence=confidence,
        risk_level=risk_level,
        model_name=model_name,
        explanation=explanation,
        key_factors=key_factors,
        metadata=db_record.metadata_json or {},
        created_at=db_record.created_at
    )
