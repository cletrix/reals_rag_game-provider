import pytest
from fastapi.testclient import TestClient


def test_health_check(client):
    """Testa endpoint /health."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
    assert "services" in data


def test_readiness(client):
    """Testa endpoint /readiness."""
    response = client.get("/readiness")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data


def test_liveness(client):
    """Testa endpoint /liveness."""
    response = client.get("/liveness")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "timestamp" in data
