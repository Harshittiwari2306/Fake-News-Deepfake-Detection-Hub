from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from app.database.session import Base
import app.models.user  # Ensures 'users' table is registered for ForeignKey

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    analysis_type = Column(String(50), nullable=False) # TEXT, IMAGE, VIDEO, AUDIO, FACTCHECK
    status = Column(String(50), default="COMPLETED") # PENDING, COMPLETED, FAILED
    
    # Probabilistic prediction results
    prediction = Column(String(100), nullable=False) # e.g. "Likely Authentic", "Potentially Misleading"
    confidence = Column(Float, nullable=False) # 0.0 - 100.0
    risk_level = Column(String(50), default="Medium") # Low, Medium, High
    
    model_name = Column(String(100), nullable=True)
    explanation = Column(Text, nullable=True)
    content_summary = Column(String(255), nullable=True)
    
    # Detailed metadata, tokens, heatmaps or suspicious frames
    metadata_json = Column(JSON, nullable=True)
    
    processing_time_ms = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
