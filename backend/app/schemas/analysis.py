from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

# Text Analysis
class TextAnalysisRequest(BaseModel):
    text: str
    headline: Optional[str] = None
    source_url: Optional[str] = None

class AnalysisResult(BaseModel):
    id: Optional[int] = None
    analysis_type: str
    prediction: str
    confidence: float
    risk_level: str
    model_name: str
    explanation: str
    key_factors: Optional[List[str]] = []
    metadata: Optional[Dict[str, Any]] = {}
    created_at: Optional[datetime] = None

# Fact Check
class FactCheckRequest(BaseModel):
    claim: str
    context: Optional[str] = None

class FactCheckSource(BaseModel):
    title: str
    source_name: str
    url: Optional[str] = None
    stance: str # SUPPORTS, REFUTES, INCONCLUSIVE
    snippet: str

class FactCheckResponse(BaseModel):
    claim: str
    verdict: str # "Verified False", "Mostly True", "Unsubstantiated", "Misleading Context"
    confidence: float
    summary: str
    sources: List[FactCheckSource]
    recommendation: str

# Dashboard Statistics
class DashboardStats(BaseModel):
    total_analyses: int
    text_count: int
    media_count: int
    flagged_misleading: int
    authentic_rate: float
    recent_analyses: List[AnalysisResult]
