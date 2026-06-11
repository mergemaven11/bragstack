from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_root_returns_health_message():
    """Verify the API root route returns the health check message."""
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {"message": "BragStack API is running"}


def test_public_brag_route_returns_public_payload():
    """Verify the public brag route returns a public entries response."""
    response = client.get("/public/brag")

    assert response.status_code == 200

    data = response.json()

    assert "total_entries" in data
    assert "entries" in data
    assert "message" in data
    assert isinstance(data["entries"], list)