from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.analysis import FactCheckRequest, FactCheckResponse
from app.services.factcheck_service import execute_fact_check
from app.services.auth_service import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/factcheck", tags=["Fact Checking Engine"])

@router.post("", response_model=FactCheckResponse)
def fact_check_endpoint(
    request: FactCheckRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(get_current_user_optional)
):
    if not request.claim.strip():
        raise HTTPException(status_code=400, detail="Claim cannot be empty.")
        
    user_id = user.id if user else None
    return execute_fact_check(db=db, request=request, user_id=user_id)
