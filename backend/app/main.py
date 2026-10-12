import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import engine, Base
import app.models.user
import app.models.analysis

# Automatically initialize tables in DB
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Unified Misinformation, Fake News, and Deepfake Detection Hub API",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Middleware - Support all origins safely (Render, Vercel, localhost)
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https?://.*",
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API Routers
from app.api.auth import router as auth_router
from app.api.news import router as news_router
from app.api.images import router as images_router
from app.api.videos import router as videos_router
from app.api.audio import router as audio_router
from app.api.factcheck import router as factcheck_router
from app.api.dashboard import router as dashboard_router

app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(news_router, prefix=settings.API_V1_STR)
app.include_router(images_router, prefix=settings.API_V1_STR)
app.include_router(videos_router, prefix=settings.API_V1_STR)
app.include_router(audio_router, prefix=settings.API_V1_STR)
app.include_router(factcheck_router, prefix=settings.API_V1_STR)
app.include_router(dashboard_router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": "1.0.0",
        "docs": "/docs",
        "health": f"{settings.API_V1_STR}/health"
    }

@app.get(f"{settings.API_V1_STR}/health")
def health_check():
    has_api_key = bool(os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY"))
    return {
        "status": "healthy",
        "service": "Fake News & Deepfake Detection Hub",
        "version": "1.0.0",
        "ai_engine": "Groq Cloud (LLaMA-3.3 70B)",
        "api_key_configured": has_api_key
    }
