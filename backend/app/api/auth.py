from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import register_user, authenticate_user, get_current_user_optional
from app.core.security import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, db: Session = Depends(get_db)):
    user = await register_user(db, user_in)
    token = create_access_token(str(user.id))
    return Token(
        access_token=token,
        token_type="bearer",
        user=user
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = await authenticate_user(db, credentials)
    token = create_access_token(str(user.id))
    return Token(
        access_token=token,
        token_type="bearer",
        user=user
    )

@router.get("/me", response_model=UserResponse)
async def get_me(user: Optional[UserResponse] = Depends(get_current_user_optional)):
    if not user:
        return UserResponse(
            id=1,
            email="guest@truthguard.ai",
            full_name="Guest User",
            name="Guest User",
            role="USER",
            is_active=True,
            created_at=datetime.now(timezone.utc)
        )
    return user
