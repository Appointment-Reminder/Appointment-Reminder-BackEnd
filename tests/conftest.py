import os
import pytest
import asyncio
from httpx import AsyncClient
from app.main import app
from app.Database.client import client
from fastapi.testclient import TestClient
from MockTestData import  MockPhotographersCollection, MockAppointmentsCollection
from unittest.mock import AsyncMock, patch


# Use a test DB
os.environ["MONGO_DB"] = "PhotoReminder_Test"

@pytest.fixture(scope="module", autouse=True)
async def seed_test_db():
    db = client[os.environ["MONGO_DB"]]

    # Clear old data
    await db["photographers"].delete_many({})

    # Seed dummy data
    await db["photographers"].insert_many([
        {"_id": "1", "name": "Alice", "email": "alice@example.com"},
        {"_id": "2", "name": "Bob", "email": "bob@example.com"}
    ])

    await db["appointments"].delete_many({})
    await db["appointments"].insert_many([
        {"_id": "1", "client": "Charlie", "time": "2025-09-11 10:00", "location": "Studio A"},
        {"_id": "2", "client": "Dana", "time": "2025-09-12 14:00", "location": "Studio B"},
    ])

    yield  # test runs here

@pytest.fixture
def event_loop():
    yield asyncio.get_event_loop()

def pytest_sessionfinish(session, exitstatus):
    asyncio.get_event_loop().close()

@pytest.fixture
def appointment_client():
    with patch("app.routes.appointments.appointments_col", new=MockAppointmentsCollection()):
        yield TestClient(app)

@pytest.fixture
def reminders_client():
    with patch("app.routes.reminders.appointments_col", new=MockAppointmentsCollection()):
        yield TestClient(app)

@pytest.fixture
def photographers_client():
    with patch("app.routes.photographers.photographers_col", new=MockPhotographersCollection()):
        yield TestClient(app)
@pytest.fixture
async def async_client():
    """Async test client for FastAPI"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


