import pytest
from unittest.mock import AsyncMock
from fastapi.testclient import TestClient
from main import app

# Initialize TestClient for testing
client = TestClient(app)

@pytest.fixture(scope="function", autouse=True)
async def setup_and_teardown():
    # Setup: Initialize the database before each test
    await app.router.startup()  # Ensure database initialization
    yield
    # Teardown: Reset the database after each test
    async with app.dependency_overrides[get_db]() as db:
        await db.execute("DELETE FROM MessageHistory")
        await db.execute("DELETE FROM SessionLogs")
        await db.execute("DELETE FROM UserInformation")
        await db.commit()

# Test the `/sessions` GET endpoint
def test_get_sessions():
    response = client.get("/sessions")
    assert response.status_code == 200
    assert "sessions" in response.json()
    assert isinstance(response.json()["sessions"], list)

# Test the `/sessions` POST endpoint
def test_create_session():
    payload = {
        "device_type": "mobile",
        "browser_agent": "Mozilla/5.0"
    }
    response = client.post("/sessions", json=payload)
    assert response.status_code == 200
    assert "sessionId" in response.json()
    assert isinstance(response.json()["sessionId"], int)

# Test the `/sessions/{session_id}/messages` GET endpoint
def test_get_session_messages():
    # Create a session first
    session_response = client.post("/sessions", json={"device_type": "desktop"})
    session_id = session_response.json()["sessionId"]

    response = client.get(f"/sessions/{session_id}/messages")
    assert response.status_code == 200
    assert "messages" in response.json()
    assert isinstance(response.json()["messages"], list)

# Test the `/sessions/{session_id}/messages` POST endpoint
def test_save_message():
    # Create a session first
    session_response = client.post("/sessions", json={"device_type": "desktop"})
    session_id = session_response.json()["sessionId"]

    payload = {
        "message": "Hello, Campi!",
        "sender": "User",
        "timestamp": "2024-12-08T10:00:00"
    }
    response = client.post(f"/sessions/{session_id}/messages", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "success"

# Test the `/sessions/{session_id}` DELETE endpoint
def test_delete_session():
    # Create a session first
    session_response = client.post("/sessions", json={"device_type": "desktop"})
    session_id = session_response.json()["sessionId"]

    response = client.delete(f"/sessions/{session_id}")
    assert response.status_code == 200
    assert response.json()["status"] == "success"

# Test the `/generate` POST endpoint
def test_generate_text(mocker):
    # Mock CampusDemoQueryMapper
    mock_query_mapper = mocker.patch("main.CampusDemoQueryMapper")
    mock_query_mapper.return_value.match_and_execute = AsyncMock(return_value="Mock LLM response")

    # Mock subprocess.run for LLM
    mock_subprocess = mocker.patch("subprocess.run")
    mock_subprocess.return_value.stdout = "Mock LLM response"

    payload = {
        "prompt": "What are the library hours?"
    }

    # Use TestClient to make a POST request
    response = client.post("/generate", json=payload)
    assert response.status_code == 200
    assert "response" in response.json()
    assert response.json()["response"] == "Mock LLM response"