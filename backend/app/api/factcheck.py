from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.analysis import FactCheckRequest, FactCheckResponse
from app.services.factcheck_service import execute_fact_check
from app.services.auth_service import get_current_user_optional
from app.services.mongo_service import sync_analysis_to_mongo
from app.models.user import User

router = APIRouter(prefix="/factcheck", tags=["Fact Checking Engine"])

@router.post("", response_model=FactCheckResponse)
async def fact_check_endpoint(
    request: FactCheckRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional)
):
    if not request.claim.strip():
        raise HTTPException(status_code=400, detail="Claim cannot be empty.")
        
    user_id = user.id if user else None
    result = execute_fact_check(db=db, request=request, user_id=user_id)

    # Persist to MongoDB
    sources_data = [
        {"title": s.title, "source_name": s.source_name, "url": s.url, "stance": s.stance, "snippet": s.snippet}
        for s in result.sources
    ]
    await sync_analysis_to_mongo(
        user_id=str(user_id or "guest_user"),
        content_type="news",
        prediction_label=result.verdict,
        confidence_score=result.confidence,
        model_name="FactCheck Engine & Global Verifier",
        explanation=result.summary,
        original_text=request.claim,
        fact_check_data={
            "claim": request.claim,
            "verdict": result.verdict,
            "sources": sources_data
        }
    )

    return result
