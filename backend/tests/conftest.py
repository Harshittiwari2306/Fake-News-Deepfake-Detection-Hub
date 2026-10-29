import sys
import os
from pathlib import Path
import pytest
import pytest_asyncio
from mongomock_motor import AsyncMongoMockClient

# Ensure backend directory is in PYTHONPATH
backend_dir = str(Path(__file__).resolve().parent.parent)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from fastapi.testclient import TestClient
from app.main import app
from app.database.mongodb import mongo_manager, init_mongo_indexes
from app.core.security import create_access_token

@pytest_asyncio.fixture(autouse=True)
async def setup_test_mongodb():
    """
    Creates an isolated in-memory mock MongoDB database for each test,
    ensuring tests never mutate or depend on production databases.
    """
    mock_client = AsyncMongoMockClient()
    mock_db = mock_client["test_fake_news_hub"]

    # Point mongo_manager to mock db
    mongo_manager.client = mock_client
    mongo_manager.db = mock_db
    mongo_manager.is_connected = True

    await init_mongo_indexes(mock_db)

    yield mock_db

    # Teardown
    mock_client.close()
    mongo_manager.is_connected = False

@pytest.fixture
def test_client():
    return TestClient(app)

@pytest.fixture
def auth_headers():
    token = create_access_token("test_user_123")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def other_user_auth_headers():
    token = create_access_token("other_user_456")
    return {"Authorization": f"Bearer {token}"}

