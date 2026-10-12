from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.analysis import AnalysisResult
from app.services.image_service import analyze_image_deepfake
from app.services.auth_service import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/analyze", tags=["Image Deepfake Analysis"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

@router.post("/image", response_model=AnalysisResult)
async def analyze_image_endpoint(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional)
):
    filename = file.filename or "uploaded_image.png"
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )
        
    contents = await file.read()
    if len(contents) > 25 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Image file exceeds maximum 25MB limit.")
        
    user_id = user.id if user else None
    return analyze_image_deepfake(db=db, image_bytes=contents, filename=filename, user_id=user_id)
