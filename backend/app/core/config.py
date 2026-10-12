import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Search and load .env from backend or root
for p in [Path(".env"), Path("../.env"), Path(__file__).resolve().parent.parent.parent / ".env", Path(__file__).resolve().parent.parent.parent.parent / ".env"]:
    if p.exists():
        load_dotenv(p)
        break

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Fake News & Deepfake Detection Hub"
    API_V1_STR: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "truthguard_super_secret_jwt_key_2026_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440 # 24 hours
    
    # Database - Default to SQLite file if Postgres is not configured locally
    DATABASE_URL: str = "sqlite:///./truthguard.db"
    
    # LLM / Groq API
    GROQ_API_KEY: str = ""
    GROK_API_KEY: str = ""
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "*"
    ]

    class Config:
        env_file = [".env", "../.env"]
        extra = "ignore"

settings = Settings()
# Fallback check directly from os.environ
if not settings.GROQ_API_KEY:
    settings.GROQ_API_KEY = os.getenv("GROQ_API_KEY", os.getenv("GROK_API_KEY", ""))
