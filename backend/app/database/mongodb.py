import os
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.core.config import settings

logger = logging.getLogger("truthguard.mongodb")

def sanitize_mongo_uri(uri: str) -> str:
    """
    Sanitizes MongoDB URI so user credentials/passwords are never logged or exposed.
    """
    if not uri:
        return ""
    try:
        if "@" in uri:
            scheme = uri.split("://")[0] if "://" in uri else "mongodb"
            host_part = uri.split("@", 1)[1]
            host_clean = host_part.split("?")[0]
            return f"{scheme}://***:***@{host_clean}"
        return uri.split("?")[0]
    except Exception:
        return "mongodb://***:***@protected"

class MongoDBManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None
    is_connected: bool = False

mongo_manager = MongoDBManager()

async def connect_to_mongo():
    """
    Initializes the asynchronous MongoDB Atlas/Local connection and configures indexes
    for all required collections: users, submissions, predictions, fact_checks, audit_logs.
    """
    mongo_uri = settings.MONGODB_URI.strip()
    db_name = settings.MONGODB_DATABASE.strip()

    if not mongo_uri:
        logger.warning("MONGODB_URI is empty. Skipping MongoDB connection.")
        mongo_manager.is_connected = False
        return

    # Use certifi CA certificates for MongoDB Atlas SSL/TLS reliability
    client_kwargs = {
        "serverSelectionTimeoutMS": 5000,
        "connectTimeoutMS": 5000
    }

    try:
        import certifi
        client_kwargs["tlsCAFile"] = certifi.where()
    except Exception:
        pass

    try:
        sanitized = sanitize_mongo_uri(mongo_uri)
        logger.info(f"Connecting to MongoDB Atlas / cluster at: {sanitized}")
        
        mongo_manager.client = AsyncIOMotorClient(mongo_uri, **client_kwargs)
        mongo_manager.db = mongo_manager.client[db_name]

        # Verify connectivity via ping command
        await mongo_manager.client.admin.command('ping')
        mongo_manager.is_connected = True
        logger.info(f"Successfully connected to MongoDB Atlas database: '{db_name}'")

        # Initialize collections and indexes
        await init_mongo_indexes(mongo_manager.db)

    except Exception as e:
        mongo_manager.is_connected = False
        logger.warning(
            f"MongoDB connection failed: {e}. "
            "Backend will continue with graceful fallback for offline/unconfigured MongoDB."
        )

async def init_mongo_indexes(db: AsyncIOMotorDatabase):
    """
    Ensures required collections and optimized indexes exist in MongoDB Atlas.
    """
    try:
        # 1. users: unique email
        await db.users.create_index("email", unique=True)

        # 2. submissions: indexed by user_id and submitted_at (descending)
        await db.submissions.create_index([("user_id", 1), ("submitted_at", -1)])
        await db.submissions.create_index("processing_status")
        await db.submissions.create_index("content_type")

        # 3. predictions: indexed by submission_id and user_id
        await db.predictions.create_index("submission_id")
        await db.predictions.create_index("user_id")

        # 4. fact_checks: indexed by submission_id
        await db.fact_checks.create_index("submission_id")

        # 5. audit_logs: indexed by user_id and created_at
        await db.audit_logs.create_index([("user_id", 1), ("created_at", -1)])
        await db.audit_logs.create_index("resource_id")

        logger.info("MongoDB collections and indexes initialized successfully.")
    except Exception as e:
        logger.error(f"Error creating MongoDB indexes: {e}")

async def close_mongo_connection():
    """
    Closes the MongoDB connection on application shutdown.
    """
    if mongo_manager.client:
        mongo_manager.client.close()
        mongo_manager.is_connected = False
        logger.info("MongoDB connection closed.")

def get_mongodb() -> Optional[AsyncIOMotorDatabase]:
    """
    FastAPI dependency yielding the MongoDB database instance.
    """
    return mongo_manager.db

def is_mongo_online() -> bool:
    return mongo_manager.is_connected
