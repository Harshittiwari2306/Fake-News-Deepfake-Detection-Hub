from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.analysis import AnalysisResult
from app.services.video_service import analyze_video_deepfake
from app.services.auth_service import get_current_user_optional
from app.services.mongo_service import sync_analysis_to_mongo
from app.models.user import User

router = APIRouter(prefix="/analyze", tags=["Video Deepfake Analysis"])

ALLOWED_VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".webm", ".mkv"}

@router.post("/video", response_model=AnalysisResult)
async def analyze_video_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional)
):
    filename = file.filename or "uploaded_video.mp4"
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext not in ALLOWED_VIDEO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video format '{ext}'. Allowed: {', '.join(ALLOWED_VIDEO_EXTENSIONS)}"
        )
        
    contents = await file.read()
    file_size_mb = len(contents) / (1024 * 1024)
    if file_size_mb > 100:
        raise HTTPException(status_code=400, detail="Video exceeds 100MB limit.")
        
    user_id = user.id if user else None
    result = analyze_video_deepfake(db=db, filename=filename, file_size_mb=file_size_mb, duration_seconds=30.0, user_id=user_id)

    # Persist to MongoDB
    await sync_analysis_to_mongo(
        user_id=str(user_id or "guest_user"),
        content_type="video",
        prediction_label=result.prediction,
        confidence_score=result.confidence,
        model_name=result.model_name,
        explanation=result.explanation,
        file_reference=filename
    )

    return result
