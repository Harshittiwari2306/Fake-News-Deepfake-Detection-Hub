import pytest
from datetime import datetime
from app.schemas.mongo_schemas import SubmissionCreate, PredictionCreate, FactCheckCreate
from app.services.mongo_service import (
    create_submission_record,
    get_user_submissions,
    get_single_submission,
    delete_submission_record,
    save_prediction_record,
    get_predictions_for_submission,
    save_fact_check_record,
    compute_dashboard_analytics,
    sync_analysis_to_mongo
)

@pytest.mark.asyncio
async def test_submission_crud(setup_test_mongodb):
    db = setup_test_mongodb
    user_id = "user_abc_1"

    # 1. Create Submission
    sub_data = SubmissionCreate(
        content_type="news",
        original_text="Scientists discovered water on Mars.",
        source_url="https://nasa.gov"
    )
    sub = await create_submission_record(user_id=user_id, submission_data=sub_data, db=db)
    assert "_id" in sub
    assert sub["user_id"] == user_id
    assert sub["content_type"] == "news"
    sub_id = sub["_id"]

    # 2. Get Single Submission
    fetched = await get_single_submission(submission_id=sub_id, user_id=user_id, db=db)
    assert fetched["_id"] == sub_id
    assert fetched["original_text"] == "Scientists discovered water on Mars."

    # 3. List Submissions
    list_res = await get_user_submissions(user_id=user_id, skip=0, limit=10, db=db)
    assert list_res["total"] == 1
    assert len(list_res["items"]) == 1

    # 4. Save Prediction for Submission
    pred_data = PredictionCreate(
        submission_id=sub_id,
        detection_type="news",
        predicted_label="Likely Authentic",
        confidence_score=0.92,
        model_name="Groq LLaMA-3.3 70B",
        explanation="Consistent with NASA findings."
    )
    pred = await save_prediction_record(user_id=user_id, prediction_data=pred_data, db=db)
    assert pred["submission_id"] == sub_id
    assert pred["confidence_score"] == 0.92

    # 5. Fetch Predictions for Submission
    preds = await get_predictions_for_submission(submission_id=sub_id, user_id=user_id, db=db)
    assert len(preds) == 1
    assert preds[0]["predicted_label"] == "Likely Authentic"

    # 6. Delete Submission (Cascade Deletion & Audit Log)
    del_res = await delete_submission_record(submission_id=sub_id, user_id=user_id, db=db)
    assert del_res["success"] is True

    # Verify submission deleted
    assert await db.submissions.find_one({"_id": sub_id}) is None
    # Verify predictions cascade deleted
    assert await db.predictions.count_documents({"submission_id": sub_id}) == 0
    # Verify audit log was recorded
    audit = await db.audit_logs.find_one({"action": "DELETE_SUBMISSION", "resource_id": sub_id})
    assert audit is not None
    assert audit["user_id"] == user_id

@pytest.mark.asyncio
async def test_sync_analysis_and_analytics(setup_test_mongodb):
    db = setup_test_mongodb
    user_id = "user_analytics_test"

    # Sync analysis workflow
    sub_id = await sync_analysis_to_mongo(
        user_id=user_id,
        content_type="news",
        prediction_label="Potentially Misleading",
        confidence_score=85.5, # 0-100 scale should normalize to ~0.855
        model_name="Groq LLaMA-3.3 70B",
        explanation="Sensationalist phrasing detected.",
        original_text="Shocking discovery claims aliens in drinking water.",
        db=db
    )
    assert sub_id is not None

    # Verify prediction normalized
    pred = await db.predictions.find_one({"submission_id": sub_id})
    assert pred is not None
    assert 0.0 <= pred["confidence_score"] <= 1.0
    assert pred["confidence_score"] == 0.855

    # Test Dashboard Analytics
    analytics = await compute_dashboard_analytics(user_id=user_id, db=db)
    assert analytics["total_submissions"] == 1
    assert analytics["flagged_misleading"] == 1
    assert analytics["by_content_type"]["news"] == 1

