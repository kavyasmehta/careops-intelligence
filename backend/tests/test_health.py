from fastapi.testclient import TestClient

from app.main import app


def test_root_returns_disclaimer():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
        body = response.json()
        assert "synthetic data" in body["data"]["disclaimer"]


def test_health_endpoint_reports_dependencies():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert "status" in body["data"]
        assert "mongo" in body["data"]["dependencies"]
        assert "neo4j" in body["data"]["dependencies"]
