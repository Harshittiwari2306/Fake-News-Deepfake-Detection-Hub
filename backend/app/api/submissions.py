from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.database.mongodb import get_mongodb, is_mongo_online
from app.services.auth_service import get_current_user_optional
from app.models.user import User
from app.core.config import settings
from app.schemas.mongo_schemas import (
    SubmissionCreate,
    SubmissionResponse,
    SubmissionListResponse,
    PredictionCreate,
    PredictionResponse,
    DashboardAnalyticsResponse
)
from app.services.mongo_service import (
    create_submission_record,
    get_user_submissions,
    get_single_submission,
    delete_submission_record,
    save_prediction_record,
    get_predictions_for_submission,
    compute_dashboard_analytics
)

router = APIRouter(tags=["Submissions & Predictions"])

def resolve_user_id(user: Optional[User]) -> str:
    """
    Enforces authentication and ownership on the server.
    User ID is extracted from validated server token, never trusted from frontend request body.
    """
    if user:
        return str(user.id)
    # Default to guest user identifier for non-authenticated demo sessions
    return "guest_user"

# -------------------------------------------------------------
# 1. SUBMISSIONS ENDPOINTS
# -------------------------------------------------------------
@router.post("/submissions", response_model=SubmissionResponse, status_code=status.HTTP_201_CREATED)
async def create_submission(
    submission: SubmissionCreate,
    user: Optional[User] = Depends(get_current_user_optional),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_mongodb)
):
    """
    Create a new digital content submission (news, image, video, audio).
    """
    user_id = resolve_user_id(user)
    created = await create_submission_record(user_id=user_id, submission_data=submission, db=db)
    return created

@router.get("/submissions", response_model=SubmissionListResponse)
async def list_submissions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    content_type: Optional[str] = Query(None, description="Filter by: news, image, video, audio"),
    user: Optional[User] = Depends(get_current_user_optional),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_mongodb)
):
    """
    List submissions for the current authenticated user with pagination and optional type filter.
    """
    user_id = resolve_user_id(user)
    result = await get_user_submissions(
        user_id=user_id,
        skip=skip,
        limit=limit,
        content_type=content_type,
        db=db
    )
    return result

@router.get("/submissions/{submission_id}", response_model=SubmissionResponse)
async def get_submission(
    submission_id: str,
    user: Optional[User] = Depends(get_current_user_optional),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_mongodb)
):
    """
    Retrieve details of a single submission along with its predictions and fact-checks.
    """
    user_id = resolve_user_id(user)
    submission = await get_single_submission(submission_id=submission_id, user_id=user_id, db=db)
    return submission

@router.delete("/submissions/{submission_id}", status_code=status.HTTP_200_OK)
async def delete_submission(
    submission_id: str,
    user: Optional[User] = Depends(get_current_user_optional),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_mongodb)
):
    """
    Delete an authorized user's submission and all associated predictions and fact-checks.
    """
    user_id = resolve_user_id(user)
    result = await delete_submission_record(submission_id=submission_id, user_id=user_id, db=db)
    return result

# -------------------------------------------------------------
# 2. PREDICTIONS ENDPOINTS
# -------------------------------------------------------------
@router.post("/predictions", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
async def save_prediction(
    prediction: PredictionCreate,
    user: Optional[User] = Depends(get_current_user_optional),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_mongodb)
):
    """
    Save a completed AI prediction for a submission with normalized confidence score (0.0 to 1.0).
    """
    user_id = resolve_user_id(user)
    saved = await save_prediction_record(user_id=user_id, prediction_data=prediction, db=db)
    return saved

@router.get("/submissions/{submission_id}/predictions", response_model=List[PredictionResponse])
async def get_submission_predictions(
    submission_id: str,
    user: Optional[User] = Depends(get_current_user_optional),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_mongodb)
):
    """
    Retrieve prediction history for a specific submission.
    """
    user_id = resolve_user_id(user)
    predictions = await get_predictions_for_submission(
        submission_id=submission_id,
        user_id=user_id,
        db=db
    )
    return predictions

# -------------------------------------------------------------
# 3. DASHBOARD ANALYTICS ENDPOINT
# -------------------------------------------------------------
@router.get("/dashboard/analytics", response_model=DashboardAnalyticsResponse)
async def get_dashboard_analytics(
    user: Optional[User] = Depends(get_current_user_optional),
    db: Optional[AsyncIOMotorDatabase] = Depends(get_mongodb)
):
    """
    Retrieve unified dashboard analytics and metrics from MongoDB collections.
    """
    user_id = resolve_user_id(user)
    analytics = await compute_dashboard_analytics(user_id=user_id, db=db)
    return analytics

# -------------------------------------------------------------
# 4. HEALTH CHECK ENDPOINT
# -------------------------------------------------------------
@router.get("/health", tags=["Health"])
async def check_system_health():
    """
    Comprehensive health check for backend, MongoDB, and AI inference engine.
    """
    mongo_status = "Connected" if is_mongo_online() else "Disconnected (Fallback Mode)"
    has_api_key = bool(settings.GROQ_API_KEY)

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "database": {
            "mongodb": mongo_status,
            "configured_database": settings.MONGODB_DATABASE
        },
        "ai_engine": {
            "name": "Groq LLaMA-3.3 70B & Vision Forensics",
            "api_key_configured": has_api_key
        }
    }

