from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.analysis import TextAnalysisRequest, AnalysisResult
from app.services.text_service import process_text_analysis
from app.services.auth_service import get_current_user_optional
from app.services.mongo_service import sync_analysis_to_mongo
from app.models.user import User

router = APIRouter(prefix="/analyze", tags=["Text & Fake News Analysis"])

@router.post("/text", response_model=AnalysisResult)
async def analyze_text_endpoint(
    request: TextAnalysisRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional)
):
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    
    user_id = user.id if user else None
    result = process_text_analysis(db=db, request=request, user_id=user_id)

    # Persist to MongoDB (Task Rule 5)
    await sync_analysis_to_mongo(
        user_id=str(user_id or "guest_user"),
        content_type="news",
        prediction_label=result.prediction,
        confidence_score=result.confidence,
        model_name=result.model_name,
        explanation=result.explanation,
        original_text=request.text,
        source_url=request.source_url
    )

    return result
