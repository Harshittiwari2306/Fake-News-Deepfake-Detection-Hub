from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from fastapi import HTTPException, status
from app.database.mongodb import get_mongodb, is_mongo_online
from app.schemas.mongo_schemas import (
    SubmissionCreate,
    SubmissionResponse,
    PredictionCreate,
    PredictionResponse,
    FactCheckCreate,
    FactCheckResponseMongo,
    DashboardAnalyticsResponse
)

def format_mongo_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to convert BSON ObjectId to string"""
    if not doc:
        return {}
    doc["_id"] = str(doc["_id"])
    return doc

# -------------------------------------------------------------
# AUDIT LOG SERVICE
# -------------------------------------------------------------
async def record_audit_log(
    user_id: str,
    action: str,
    resource_type: str,
    resource_id: str,
    db: Optional[AsyncIOMotorDatabase] = None
) -> None:
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        return

    try:
        log_entry = {
            "user_id": str(user_id),
            "action": action,
            "resource_type": resource_type,
            "resource_id": str(resource_id),
            "created_at": datetime.now(timezone.utc)
        }
        await db.audit_logs.insert_one(log_entry)
    except Exception as e:
        print(f"Error recording audit log: {e}")

# -------------------------------------------------------------
# SUBMISSION SERVICE
# -------------------------------------------------------------
async def create_submission_record(
    user_id: str,
    submission_data: SubmissionCreate,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Dict[str, Any]:
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        # Fallback local dict if Mongo is offline
        mock_id = str(ObjectId())
        return {
            "_id": mock_id,
            "user_id": user_id,
            "content_type": submission_data.content_type,
            "original_text": submission_data.original_text,
            "file_reference": submission_data.file_reference,
            "source_url": submission_data.source_url,
            "submitted_at": datetime.now(timezone.utc),
            "processing_status": "pending",
            "predictions": [],
            "fact_checks": []
        }

    submission_dict = {
        "user_id": str(user_id),
        "content_type": submission_data.content_type,
        "original_text": submission_data.original_text,
        "file_reference": submission_data.file_reference,
        "source_url": submission_data.source_url,
        "submitted_at": datetime.now(timezone.utc),
        "processing_status": "pending"
    }

    result = await db.submissions.insert_one(submission_dict)
    submission_dict["_id"] = str(result.inserted_id)

    # Record Audit Log
    await record_audit_log(
        user_id=user_id,
        action="CREATE_SUBMISSION",
        resource_type="submission",
        resource_id=submission_dict["_id"],
        db=db
    )

    return submission_dict

async def get_user_submissions(
    user_id: str,
    skip: int = 0,
    limit: int = 20,
    content_type: Optional[str] = None,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Dict[str, Any]:
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        return {"total": 0, "skip": skip, "limit": limit, "items": []}

    query: Dict[str, Any] = {"user_id": str(user_id)}
    if content_type and content_type.lower() != "all":
        query["content_type"] = content_type.lower()

    total = await db.submissions.count_documents(query)
    cursor = db.submissions.find(query).sort("submitted_at", -1).skip(skip).limit(limit)

    items = []
    async for doc in cursor:
        sub_id = str(doc["_id"])
        formatted = format_mongo_doc(doc)
        
        # Attach predictions for this submission
        preds = []
        async for p in db.predictions.find({"submission_id": sub_id}):
            preds.append(format_mongo_doc(p))
        formatted["predictions"] = preds

        items.append(formatted)

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": items
    }

async def get_single_submission(
    submission_id: str,
    user_id: str,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Dict[str, Any]:
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB service is currently offline."
        )

    try:
        obj_id = ObjectId(submission_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid submission ID format.")

    submission = await db.submissions.find_one({"_id": obj_id})
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    # Ownership check
    if submission.get("user_id") != str(user_id) and str(user_id) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to access this submission.")

    formatted = format_mongo_doc(submission)

    # Attach predictions
    preds = []
    async for p in db.predictions.find({"submission_id": str(obj_id)}):
        preds.append(format_mongo_doc(p))
    formatted["predictions"] = preds

    # Attach fact checks
    fcs = []
    async for f in db.fact_checks.find({"submission_id": str(obj_id)}):
        fcs.append(format_mongo_doc(f))
    formatted["fact_checks"] = fcs

    return formatted

async def delete_submission_record(
    submission_id: str,
    user_id: str,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Dict[str, Any]:
    """
    Deletes an authorized user's submission, along with its associated
    predictions, fact_checks, and writes an audit log.
    """
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="MongoDB service is currently unavailable."
        )

    try:
        obj_id = ObjectId(submission_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid submission ID format.")

    # Check existence and ownership
    submission = await db.submissions.find_one({"_id": obj_id})
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found.")

    if submission.get("user_id") != str(user_id) and str(user_id) != "admin":
        raise HTTPException(status_code=403, detail="Not authorized to delete this submission.")

    # Delete submission
    await db.submissions.delete_one({"_id": obj_id})

    # Delete associated predictions & fact checks
    await db.predictions.delete_many({"submission_id": str(obj_id)})
    await db.fact_checks.delete_many({"submission_id": str(obj_id)})

    # Record Audit Log
    await record_audit_log(
        user_id=user_id,
        action="DELETE_SUBMISSION",
        resource_type="submission",
        resource_id=str(obj_id),
        db=db
    )

    return {
        "success": True,
        "message": f"Submission {submission_id} and all associated predictions were successfully deleted."
    }

# -------------------------------------------------------------
# PREDICTION SERVICE
# -------------------------------------------------------------
async def save_prediction_record(
    user_id: str,
    prediction_data: PredictionCreate,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Dict[str, Any]:
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        mock_id = str(ObjectId())
        return {
            "_id": mock_id,
            "submission_id": prediction_data.submission_id,
            "user_id": user_id,
            "detection_type": prediction_data.detection_type,
            "predicted_label": prediction_data.predicted_label,
            "confidence_score": prediction_data.confidence_score,
            "model_name": prediction_data.model_name,
            "model_version": prediction_data.model_version,
            "explanation": prediction_data.explanation,
            "created_at": datetime.now(timezone.utc)
        }

    # Verify submission exists
    try:
        sub_obj_id = ObjectId(prediction_data.submission_id)
        sub = await db.submissions.find_one({"_id": sub_obj_id})
    except Exception:
        sub = None

    pred_dict = {
        "submission_id": prediction_data.submission_id,
        "user_id": str(user_id),
        "detection_type": prediction_data.detection_type,
        "predicted_label": prediction_data.predicted_label,
        "confidence_score": round(float(prediction_data.confidence_score), 4),
        "model_name": prediction_data.model_name,
        "model_version": prediction_data.model_version,
        "explanation": prediction_data.explanation,
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.predictions.insert_one(pred_dict)
    pred_dict["_id"] = str(result.inserted_id)

    # Update submission status to completed
    if sub:
        await db.submissions.update_one(
            {"_id": sub_obj_id},
            {"$set": {"processing_status": "completed"}}
        )

    # Record Audit Log
    await record_audit_log(
        user_id=user_id,
        action="CREATE_PREDICTION",
        resource_type="prediction",
        resource_id=pred_dict["_id"],
        db=db
    )

    return pred_dict

async def get_predictions_for_submission(
    submission_id: str,
    user_id: str,
    db: Optional[AsyncIOMotorDatabase] = None
) -> List[Dict[str, Any]]:
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        return []

    # Verify submission
    try:
        sub = await db.submissions.find_one({"_id": ObjectId(submission_id)})
        if sub and sub.get("user_id") != str(user_id) and str(user_id) != "admin":
            raise HTTPException(status_code=403, detail="Not authorized to access these predictions.")
    except HTTPException:
        raise
    except Exception:
        pass

    cursor = db.predictions.find({"submission_id": submission_id}).sort("created_at", -1)
    predictions = []
    async for p in cursor:
        predictions.append(format_mongo_doc(p))

    return predictions

# -------------------------------------------------------------
# FACT CHECK SERVICE
# -------------------------------------------------------------
async def save_fact_check_record(
    user_id: str,
    fc_data: FactCheckCreate,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Dict[str, Any]:
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        return {}

    fc_dict = {
        "submission_id": fc_data.submission_id,
        "claim": fc_data.claim,
        "verdict": fc_data.verdict,
        "supporting_sources": fc_data.supporting_sources,
        "contradictory_sources": fc_data.contradictory_sources,
        "checked_at": datetime.now(timezone.utc)
    }

    result = await db.fact_checks.insert_one(fc_dict)
    fc_dict["_id"] = str(result.inserted_id)

    await record_audit_log(
        user_id=user_id,
        action="CREATE_FACT_CHECK",
        resource_type="fact_check",
        resource_id=fc_dict["_id"],
        db=db
    )

    return fc_dict

# -------------------------------------------------------------
# DASHBOARD ANALYTICS SERVICE
# -------------------------------------------------------------
async def compute_dashboard_analytics(
    user_id: Optional[str] = None,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Dict[str, Any]:
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        # Clean default statistics when database has no records yet
        return {
            "total_submissions": 0,
            "by_content_type": {"news": 0, "image": 0, "video": 0, "audio": 0},
            "by_status": {"pending": 0, "processing": 0, "completed": 0, "failed": 0},
            "flagged_misleading": 0,
            "likely_authentic": 0,
            "average_confidence": 0.0,
            "recent_submissions": []
        }

    match_filter: Dict[str, Any] = {}
    if user_id and str(user_id) != "admin":
        match_filter["user_id"] = str(user_id)

    total_subs = await db.submissions.count_documents(match_filter)

    # Content type breakdown
    content_types = ["news", "image", "video", "audio"]
    by_type = {}
    for ct in content_types:
        q = dict(match_filter)
        q["content_type"] = ct
        by_type[ct] = await db.submissions.count_documents(q)

    # Status breakdown
    statuses = ["pending", "processing", "completed", "failed"]
    by_status = {}
    for st in statuses:
        q = dict(match_filter)
        q["processing_status"] = st
        by_status[st] = await db.submissions.count_documents(q)

    # Prediction aggregations (flagged vs authentic, avg confidence)
    pred_filter = {}
    if user_id and str(user_id) != "admin":
        pred_filter["user_id"] = str(user_id)

    preds_cursor = db.predictions.find(pred_filter)
    flagged_count = 0
    authentic_count = 0
    conf_sum = 0.0
    pred_total = 0

    async for p in preds_cursor:
        pred_total += 1
        conf = float(p.get("confidence_score", 0.0))
        conf_sum += conf
        label = str(p.get("predicted_label", "")).lower()
        if "misleading" in label or "manipulated" in label or "fake" in label or "fabricat" in label:
            flagged_count += 1
        elif "authentic" in label or "true" in label or "genuine" in label:
            authentic_count += 1

    avg_conf = round(conf_sum / pred_total, 3) if pred_total > 0 else 0.0

    # Recent submissions
    recent_cursor = db.submissions.find(match_filter).sort("submitted_at", -1).limit(6)
    recent_items = []
    async for s in recent_cursor:
        sub_id = str(s["_id"])
        item = format_mongo_doc(s)
        sub_preds = []
        async for sp in db.predictions.find({"submission_id": sub_id}):
            sub_preds.append(format_mongo_doc(sp))
        item["predictions"] = sub_preds
        recent_items.append(item)

    return {
        "total_submissions": total_subs,
        "by_content_type": by_type,
        "by_status": by_status,
        "flagged_misleading": flagged_count,
        "likely_authentic": authentic_count,
        "average_confidence": avg_conf,
        "recent_submissions": recent_items
    }

# -------------------------------------------------------------
# WORKFLOW SYNC HELPER (Connects existing AI models to MongoDB)
# -------------------------------------------------------------
async def sync_analysis_to_mongo(
    user_id: str,
    content_type: str,
    prediction_label: str,
    confidence_score: float,
    model_name: str,
    explanation: str,
    original_text: Optional[str] = None,
    file_reference: Optional[str] = None,
    source_url: Optional[str] = None,
    fact_check_data: Optional[Dict[str, Any]] = None,
    db: Optional[AsyncIOMotorDatabase] = None
) -> Optional[str]:
    """
    Persists AI prediction workflow outputs into MongoDB:
    1. Saves submission metadata.
    2. Saves prediction with normalized confidence (0.0 to 1.0).
    3. Saves fact-checking sources and logs audit trail.
    """
    db = db or get_mongodb()
    if db is None or not is_mongo_online():
        return None

    try:
        normalized_conf = confidence_score / 100.0 if confidence_score > 1.0 else confidence_score
        normalized_conf = max(0.0, min(1.0, float(normalized_conf)))

        sub_dict = {
            "user_id": str(user_id),
            "content_type": content_type,
            "original_text": original_text,
            "file_reference": file_reference,
            "source_url": source_url,
            "submitted_at": datetime.now(timezone.utc),
            "processing_status": "completed"
        }
        sub_res = await db.submissions.insert_one(sub_dict)
        sub_id = str(sub_res.inserted_id)

        pred_dict = {
            "submission_id": sub_id,
            "user_id": str(user_id),
            "detection_type": content_type,
            "predicted_label": prediction_label,
            "confidence_score": round(normalized_conf, 4),
            "model_name": model_name,
            "model_version": "1.0.0",
            "explanation": explanation,
            "created_at": datetime.now(timezone.utc)
        }
        await db.predictions.insert_one(pred_dict)

        if fact_check_data:
            fc_dict = {
                "submission_id": sub_id,
                "claim": fact_check_data.get("claim", original_text or ""),
                "verdict": fact_check_data.get("verdict", prediction_label),
                "supporting_sources": fact_check_data.get("sources", []),
                "contradictory_sources": fact_check_data.get("contradictory_sources", []),
                "checked_at": datetime.now(timezone.utc)
            }
            await db.fact_checks.insert_one(fc_dict)

        await record_audit_log(
            user_id=str(user_id),
            action=f"ANALYZE_{content_type.upper()}",
            resource_type="submission",
            resource_id=sub_id,
            db=db
        )

        return sub_id
    except Exception as e:
        print(f"Error syncing analysis to MongoDB: {e}")
        return None
