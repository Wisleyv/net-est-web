"""Testes para endpoints de health check"""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    """Teste básico do health check"""
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()

    assert data["success"] is True
    assert data["status"] == "healthy"
    assert "version" in data
    assert "uptime_seconds" in data
    assert data["uptime_seconds"] >= 0


def test_detailed_status(client: TestClient):
    """Teste do status detalhado"""
    response = client.get("/health")  # Use same endpoint for now

    assert response.status_code == 200
    data = response.json()

    assert "success" in data
    assert "status" in data
    assert data["success"] is True
    assert data["status"] == "healthy"
