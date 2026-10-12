from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.analysis import AnalysisResult
from app.services.audio_service import analyze_audio_voice_clone
from app.services.auth_service import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/analyze", tags=["Voice Clone & Audio Analysis"])

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".flac"}

@router.post("/audio", response_model=AnalysisResult)
async def analyze_audio_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional)
):
    filename = file.filename or "uploaded_audio.mp3"
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported audio format '{ext}'. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )
        
    contents = await file.read()
    file_size_kb = len(contents) / 1024
    if file_size_kb > 50 * 1024:
        raise HTTPException(status_code=400, detail="Audio file exceeds 50MB limit.")
        
    user_id = user.id if user else None
    return analyze_audio_voice_clone(db=db, filename=filename, file_size_kb=file_size_kb, user_id=user_id)
