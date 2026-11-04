"""Tests for health check endpoints."""


def test_liveness(client):
    """Liveness probe must always return 200."""
    res = client.get("/health/live")
    assert res.status_code == 200
    assert res.json()["status"] == "alive"


def test_root(client):
    """Root endpoint returns app metadata."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "app" in data
    assert "docs" in data


def test_health_endpoint_structure(client):
    """/health returns expected keys regardless of DB state."""
    res = client.get("/health")
    data = res.json()
    assert "status" in data
    assert "database" in data
    assert "version" in data
