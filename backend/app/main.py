import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.database.session import engine, Base
from app.database.mongodb import connect_to_mongo, close_mongo_connection, is_mongo_online
import app.models.user
import app.models.analysis

# Automatically initialize SQL tables in DB if relational backend is configured
try:
    Base.metadata.create_all(bind=engine)
except Exception as e:
    print(f"Warning initializing SQL schema: {e}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to MongoDB & configure collections/indexes
    await connect_to_mongo()
    yield
    # Shutdown: Cleanly close MongoDB client
    await close_mongo_connection()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Unified Misinformation, Fake News, and Deepfake Detection Hub API with MongoDB & PyTorch/Transformers AI",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
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
from app.api.submissions import router as submissions_router

# Mount routes under /api (Task specification)
app.include_router(submissions_router, prefix="/api")

# Mount routes under /api/v1 (Existing frontend client compatibility)
app.include_router(submissions_router, prefix=settings.API_V1_STR)
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
        "health": "/api/health"
    }

@app.get(f"{settings.API_V1_STR}/health")
@app.get("/health")
def health_check():
    has_api_key = bool(os.getenv("GROQ_API_KEY") or os.getenv("GROK_API_KEY"))
    sql_status = "Connected"
    try:
        with engine.connect() as conn:
            pass
    except Exception:
        sql_status = "Unavailable"

    mongo_status = "Connected" if is_mongo_online() else "Disconnected (Fallback Mode)"

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": "1.0.0",
        "databases": {
            "mongodb": mongo_status,
            "sql_engine": f"{engine.url.drivername} ({sql_status})"
        },
        "ai_engine": "Groq Cloud (LLaMA-3.3 70B & Vision Forensics)",
        "api_key_configured": has_api_key
    }
