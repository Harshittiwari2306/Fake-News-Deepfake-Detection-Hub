import pytest
from httpx import AsyncClient
from app.core.security import verify_password

@pytest.mark.asyncio
async def test_register_user_creates_mongo_document(test_client, setup_test_mongodb):
    mock_db = setup_test_mongodb
    signup_payload = {
        "email": "agent_alice@truthguard.ai",
        "password": "SuperSecretPassword123!",
        "full_name": "Alice Agent"
    }

    response = test_client.post("/api/v1/auth/register", json=signup_payload)
    assert response.status_code == 200, f"Expected 200 OK, got {response.status_code}: {response.text}"
    data = response.json()

    # Check response payload
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == signup_payload["email"]
    assert data["user"]["full_name"] == signup_payload["full_name"]
    assert data["user"]["role"] == "USER"
    assert "id" in data["user"]

    # Verify document exists in MongoDB Atlas mock
    mongo_user = await mock_db.users.find_one({"email": signup_payload["email"]})
    assert mongo_user is not None
    assert mongo_user["name"] == signup_payload["full_name"]
    assert mongo_user["email"] == signup_payload["email"]
    # Password must be securely hashed, never plaintext
    assert mongo_user["password_hash"] != signup_payload["password"]
    assert verify_password(signup_payload["password"], mongo_user["password_hash"]) is True

@pytest.mark.asyncio
async def test_register_duplicate_email_fails(test_client, setup_test_mongodb):
    signup_payload = {
        "email": "duplicate_user@truthguard.ai",
        "password": "Password123!",
        "full_name": "Original User"
    }

    # First registration succeeds
    res1 = test_client.post("/api/v1/auth/register", json=signup_payload)
    assert res1.status_code == 200

    # Second registration with same email must fail with 400
    res2 = test_client.post("/api/v1/auth/register", json=signup_payload)
    assert res2.status_code == 400
    assert "already exists" in res2.json()["detail"].lower()

@pytest.mark.asyncio
async def test_login_flow(test_client, setup_test_mongodb):
    signup_payload = {
        "email": "login_test@truthguard.ai",
        "password": "PasswordTest123!",
        "full_name": "Login Tester"
    }
    # Register first
    reg_res = test_client.post("/api/v1/auth/register", json=signup_payload)
    assert reg_res.status_code == 200

    # Valid login
    login_res = test_client.post("/api/v1/auth/login", json={
        "email": signup_payload["email"],
        "password": signup_payload["password"]
    })
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data
    assert login_data["user"]["email"] == signup_payload["email"]

    # Invalid password login
    bad_login_res = test_client.post("/api/v1/auth/login", json={
        "email": signup_payload["email"],
        "password": "WrongPassword!"
    })
    assert bad_login_res.status_code == 401
    assert "invalid" in bad_login_res.json()["detail"].lower()

    # Nonexistent user login
    unknown_login_res = test_client.post("/api/v1/auth/login", json={
        "email": "nonexistent@truthguard.ai",
        "password": "PasswordTest123!"
    })
    assert unknown_login_res.status_code == 401

@pytest.mark.asyncio
async def test_get_current_user_me(test_client, setup_test_mongodb):
    signup_payload = {
        "email": "me_test@truthguard.ai",
        "password": "PasswordMe123!",
        "full_name": "Me User"
    }
    reg_res = test_client.post("/api/v1/auth/register", json=signup_payload)
    token = reg_res.json()["access_token"]

    # Authenticated /me
    me_res = test_client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_res.status_code == 200
    me_data = me_res.json()
    assert me_data["email"] == signup_payload["email"]
    assert me_data["full_name"] == signup_payload["full_name"]

    # Unauthenticated /me returns guest user
    guest_res = test_client.get("/api/v1/auth/me")
    assert guest_res.status_code == 200
    guest_data = guest_res.json()
    assert guest_data["email"] == "guest@truthguard.ai"

