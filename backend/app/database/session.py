import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# Clean up database URL format (Render & Supabase often provide postgres:// which SQLAlchemy 2.0 requires as postgresql://)
db_url = settings.DATABASE_URL.strip() if settings.DATABASE_URL else "sqlite:///./truthguard.db"

if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

connect_args = {}
engine_kwargs = {"pool_pre_ping": True}

if db_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine_kwargs = {}

try:
    engine = create_engine(db_url, connect_args=connect_args, **engine_kwargs)
    with engine.connect() as conn:
        pass
    print(f"INFO: Database connected successfully to: {db_url.split('@')[-1] if '@' in db_url else db_url}")
except Exception as e:
    print(f"WARNING: Could not connect to primary DATABASE_URL ({e}). Falling back to local SQLite.")
    db_url = "sqlite:///./truthguard.db"
    engine = create_engine(db_url, connect_args={"check_same_thread": False})

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
