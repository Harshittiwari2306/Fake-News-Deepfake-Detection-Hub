import pytest
from fastapi.testclient import TestClient

def test_health_endpoint(test_client: TestClient):
    """Test health check returns clean status without exposing secrets"""
    response = test_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database" in data
    # Ensure no credentials or passwords leaked
    assert "password" not in str(data).lower()
    assert "@" not in str(data)

def test_submission_lifecycle_endpoints(test_client: TestClient):
    """Test creating, fetching, listing, and deleting submissions via REST API"""
    # 1. Create submission
    payload = {
        "content_type": "news",
        "original_text": "Breaking news test text for API validation.",
        "source_url": "https://example.com/test-news"
    }
    create_res = test_client.post("/api/submissions", json=payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert "_id" in created_data
    sub_id = created_data["_id"]
    assert created_data["content_type"] == "news"

    # 2. Get submission by ID
    get_res = test_client.get(f"/api/submissions/{sub_id}")
    assert get_res.status_code == 200
    assert get_res.json()["_id"] == sub_id

    # 3. List submissions
    list_res = test_client.get("/api/submissions?skip=0&limit=10")
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert len(list_data["items"]) >= 1

    # 4. Save prediction via POST /api/predictions
    pred_payload = {
        "submission_id": sub_id,
        "detection_type": "news",
        "predicted_label": "Likely Authentic",
        "confidence_score": 0.94,
        "model_name": "Groq LLaMA-3.3 70B",
        "model_version": "1.0.0",
        "explanation": "Verified against known factual sources."
    }
    pred_res = test_client.post("/api/predictions", json=pred_payload)
    assert pred_res.status_code == 201
    assert pred_res.json()["confidence_score"] == 0.94

    # 5. Get predictions for submission
    preds_res = test_client.get(f"/api/submissions/{sub_id}/predictions")
    assert preds_res.status_code == 200
    assert len(preds_res.json()) >= 1

    # 6. Delete submission
    del_res = test_client.delete(f"/api/submissions/{sub_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 7. Verify 404 after deletion
    get_after_del = test_client.get(f"/api/submissions/{sub_id}")
    assert get_after_del.status_code == 404

def test_dashboard_analytics_endpoint(test_client: TestClient):
    """Test dashboard analytics aggregation"""
    res = test_client.get("/api/dashboard/analytics")
    assert res.status_code == 200
    data = res.json()
    assert "total_submissions" in data
    assert "by_content_type" in data
    assert "by_status" in data
    assert "flagged_misleading" in data
    assert "likely_authentic" in data

def test_invalid_submission_input(test_client: TestClient):
    """Test validation errors for invalid submission requests"""
    # Invalid content_type
    bad_payload = {
        "content_type": "hologram", # Not in allowed literal enum
        "original_text": "Invalid type payload"
    }
    res = test_client.post("/api/submissions", json=bad_payload)
    assert res.status_code == 422 # Pydantic validation error

def test_prediction_confidence_validation(test_client: TestClient):
    """Test confidence_score must be between 0.0 and 1.0"""
    bad_pred = {
        "submission_id": "507f1f77bcf86cd799439011",
        "detection_type": "news",
        "predicted_label": "False",
        "confidence_score": 95.0, # Must be <= 1.0
        "model_name": "TestModel",
        "explanation": "Out of range confidence test"
    }
    res = test_client.post("/api/predictions", json=bad_pred)
    assert res.status_code == 422

