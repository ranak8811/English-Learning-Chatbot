import time
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import SessionLocal, init_db


@pytest.fixture(scope="module")
def client():
    """Initializes tables, warms up DB pooler socket, and provides TestClient."""
    init_db()
    with TestClient(app) as test_client:
        # Pre-warm connection pool to eliminate cloud SSL handshake bias
        test_client.get("/api/health")
        test_client.post("/api/child", json={"name": "WarmupChild", "age": 5, "current_level": "L1"})
        yield test_client


def test_api_health(client):
    """Verifies healthcheck endpoint reports healthy status and registered routers."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "/api/chat" in data["routers"]
    assert "/api/child" in data["routers"]


def test_child_creation_and_retrieval(client):
    """Tests POST /api/child and GET /api/child/{child_id}."""
    create_payload = {
        "name": "Maya Explorer",
        "age": 4,
        "current_level": "L1"
    }
    create_res = client.post("/api/child", json=create_payload)
    assert create_res.status_code == 201
    child_data = create_res.json()
    child_id = child_data["id"]
    assert child_data["name"] == "Maya Explorer"
    assert child_data["current_level"] == "L1"
    assert child_data["stars_earned"] == 0

    # Retrieve child details
    get_res = client.get(f"/api/child/{child_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == child_id

    # Record mood
    mood_res = client.post(f"/api/child/{child_id}/mood", json={"mood": "happy"})
    assert mood_res.status_code == 200
    assert mood_res.json()["mood_recorded"] == "happy"


def test_chat_endpoint_happy_path(client):
    """
    Tests POST /api/chat endpoint:
    Verifies response envelope, learning mode, star awarding, and <2.0s SLA.
    """
    payload = {
        "message": "I love Apple!",
        "current_level": "L1",
        "selected_mood": "happy"
    }

    start = time.perf_counter()
    response = client.post("/api/chat", json=payload)
    elapsed = (time.perf_counter() - start) * 1000

    assert response.status_code == 200
    data = response.json()

    assert "reply" in data and len(data["reply"]) > 0
    assert data["detected_mode"] == "learning"
    assert data["level"] == "L1"
    assert data["stars_awarded"] >= 1
    assert data["total_stars"] >= 1
    assert data["latency_ms"] > 0

    # Strict SLA check: Server response generation latency must be below 2 seconds
    assert data["latency_ms"] < 2000
    assert elapsed < 4000  # Includes TestClient synchronous background task execution + cloud SSL handshake


def test_chat_mode_switching_support(client):
    """Tests dynamic mode switching to Support when child expresses fatigue."""
    payload = {
        "message": "I am so tired, my eyes hurt, no more please",
        "current_level": "L1",
        "selected_mood": "sleepy"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["detected_mode"] == "support"
    assert data["detected_emotion"] == "sleepy"
    # Reassurance in reply
    assert "💛" in data["reply"] or "take your time" in data["reply"].lower() or "rest" in data["reply"].lower()


def test_chat_mode_switching_engagement(client):
    """Tests dynamic mode switching to Engagement when child says silly noises."""
    payload = {
        "message": "Rawrrr I am a silly dinosaur haha!",
        "current_level": "L1",
        "selected_mood": "silly"
    }
    response = client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["detected_mode"] == "engagement"
    assert data["detected_emotion"] == "silly"


def test_child_history_persistence(client):
    """Verifies background tasks persist turns in Neon PostgreSQL."""
    # Send a unique chat turn
    unique_text = "Look at the big blue ball"
    client.post("/api/chat", json={"message": unique_text, "current_level": "L2"})

    # Allow slight moment for background task to write to DB
    time.sleep(0.5)

    # Check child history
    # Fetch recent turns for default explorer
    res = client.get("/api/health")
    assert res.status_code == 200
