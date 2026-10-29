from datetime import datetime
from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field, EmailStr, ConfigDict

# -------------------------------------------------------------
# 1. USER SCHEMAS
# -------------------------------------------------------------
class UserMongoBase(BaseModel):
    name: str
    email: EmailStr
    role: str = "USER"

class UserCreateMongo(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: str = "USER"

class UserResponseMongo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    name: str
    email: EmailStr
    role: str
    created_at: datetime

# -------------------------------------------------------------
# 2. SUBMISSION SCHEMAS
# -------------------------------------------------------------
ContentTypeEnum = Literal["news", "image", "video", "audio"]
ProcessingStatusEnum = Literal["pending", "processing", "completed", "failed"]

class SubmissionCreate(BaseModel):
    content_type: ContentTypeEnum
    original_text: Optional[str] = None
    file_reference: Optional[str] = None
    source_url: Optional[str] = None

class SubmissionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    user_id: str
    content_type: ContentTypeEnum
    original_text: Optional[str] = None
    file_reference: Optional[str] = None
    source_url: Optional[str] = None
    submitted_at: datetime
    processing_status: ProcessingStatusEnum
    predictions: Optional[List[Dict[str, Any]]] = None
    fact_checks: Optional[List[Dict[str, Any]]] = None

class SubmissionListResponse(BaseModel):
    total: int
    skip: int
    limit: int
    items: List[SubmissionResponse]

# -------------------------------------------------------------
# 3. PREDICTION SCHEMAS
# -------------------------------------------------------------
class PredictionCreate(BaseModel):
    submission_id: str
    detection_type: str
    predicted_label: str
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence score between 0.0 and 1.0")
    model_name: str
    model_version: str = "1.0.0"
    explanation: str

class PredictionResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    submission_id: str
    user_id: str
    detection_type: str
    predicted_label: str
    confidence_score: float
    model_name: str
    model_version: str
    explanation: str
    created_at: datetime

# -------------------------------------------------------------
# 4. FACT CHECK SCHEMAS
# -------------------------------------------------------------
class FactCheckCreate(BaseModel):
    submission_id: str
    claim: str
    verdict: str
    supporting_sources: List[Dict[str, Any]] = []
    contradictory_sources: List[Dict[str, Any]] = []

class FactCheckResponseMongo(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    submission_id: str
    claim: str
    verdict: str
    supporting_sources: List[Dict[str, Any]]
    contradictory_sources: List[Dict[str, Any]]
    checked_at: datetime

# -------------------------------------------------------------
# 5. AUDIT LOG SCHEMAS
# -------------------------------------------------------------
class AuditLogCreate(BaseModel):
    user_id: str
    action: str
    resource_type: str
    resource_id: str

class AuditLogResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")
    user_id: str
    action: str
    resource_type: str
    resource_id: str
    created_at: datetime

# -------------------------------------------------------------
# 6. DASHBOARD ANALYTICS SCHEMAS
# -------------------------------------------------------------
class DashboardAnalyticsResponse(BaseModel):
    total_submissions: int
    by_content_type: Dict[str, int]
    by_status: Dict[str, int]
    flagged_misleading: int
    likely_authentic: int
    average_confidence: float
    recent_submissions: List[SubmissionResponse]
