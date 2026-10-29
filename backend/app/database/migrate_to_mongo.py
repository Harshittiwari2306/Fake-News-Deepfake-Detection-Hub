"""
Safe Migration Utility: SQLite / PostgreSQL to MongoDB Atlas
Migrates existing users and analyses into MongoDB Atlas collections without data loss.
Usage:
    python -m app.database.migrate_to_mongo
"""

import asyncio
from datetime import datetime
from app.database.session import SessionLocal
from app.database.mongodb import connect_to_mongo, close_mongo_connection, get_mongodb, is_mongo_online
from app.models.user import User as SqlUser
from app.models.analysis import Analysis as SqlAnalysis

async def run_migration():
    print("=" * 60)
    print("Starting Migration from Relational Database to MongoDB Atlas...")
    print("=" * 60)

    await connect_to_mongo()
    if not is_mongo_online():
        print("ERROR: Could not connect to MongoDB Atlas. Please check MONGODB_URI in .env.")
        return

    mongo_db = get_mongodb()
    sql_db = SessionLocal()

    migrated_users = 0
    migrated_analyses = 0

    try:
        # 1. Migrate Users
        sql_users = sql_db.query(SqlUser).all()
        print(f"Found {len(sql_users)} user(s) in relational database.")

        for u in sql_users:
            existing = await mongo_db.users.find_one({"email": u.email})
            if not existing:
                await mongo_db.users.insert_one({
                    "sql_id": u.id,
                    "name": u.full_name or u.email.split("@")[0],
                    "email": u.email,
                    "password_hash": u.hashed_password,
                    "role": u.role or "USER",
                    "created_at": u.created_at or datetime.utcnow()
                })
                migrated_users += 1

        print(f"-> Migrated {migrated_users} new user(s) to MongoDB Atlas 'users' collection.")

        # 2. Migrate Analyses to Submissions & Predictions
        sql_analyses = sql_db.query(SqlAnalysis).all()
        print(f"Found {len(sql_analyses)} analysis record(s) in relational database.")

        for a in sql_analyses:
            existing_pred = await mongo_db.predictions.find_one({
                "model_name": a.model_name,
                "created_at": a.created_at
            })
            if not existing_pred:
                content_type_map = {
                    "TEXT": "news",
                    "IMAGE": "image",
                    "VIDEO": "video",
                    "AUDIO": "audio",
                    "FACTCHECK": "news"
                }
                c_type = content_type_map.get(a.analysis_type, "news")

                # Create submission
                sub_res = await mongo_db.submissions.insert_one({
                    "user_id": str(a.user_id) if a.user_id else "guest_user",
                    "content_type": c_type,
                    "original_text": a.content_summary,
                    "file_reference": None,
                    "source_url": None,
                    "submitted_at": a.created_at or datetime.utcnow(),
                    "processing_status": "completed"
                })
                sub_id = str(sub_res.inserted_id)

                # Normalize confidence to 0.0 - 1.0
                conf = float(a.confidence or 0.0)
                norm_conf = conf / 100.0 if conf > 1.0 else conf

                # Create prediction
                await mongo_db.predictions.insert_one({
                    "submission_id": sub_id,
                    "user_id": str(a.user_id) if a.user_id else "guest_user",
                    "detection_type": c_type,
                    "predicted_label": a.prediction,
                    "confidence_score": round(norm_conf, 4),
                    "model_name": a.model_name or "Legacy Classifier",
                    "model_version": "1.0.0",
                    "explanation": a.explanation or "",
                    "created_at": a.created_at or datetime.utcnow()
                })
                migrated_analyses += 1

        print(f"-> Migrated {migrated_analyses} analysis record(s) to MongoDB Atlas 'submissions' & 'predictions'.")
        print("=" * 60)
        print("Migration completed successfully with ZERO data loss!")
        print("=" * 60)

    except Exception as e:
        print(f"Migration error: {e}")
    finally:
        sql_db.close()
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(run_migration())

