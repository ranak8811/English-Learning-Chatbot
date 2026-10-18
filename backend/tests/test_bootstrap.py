import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings


@pytest.fixture
def client():
    """Test client fixture for FastAPI app."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns 200 and welcome information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Welcome" in data["message"]


def test_health_check_endpoint(client):
    """Test /api/health endpoint confirms configuration and healthy status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Neon Cloud PostgreSQL" in data["database"]
    assert data["llm_engine"] == get_settings().OPENROUTER_MODEL
    assert data["latency_budget_ms"] == 2000
