from fastapi.testclient import TestClient

from digital_farming.app import create_app


app = create_app()
client = TestClient(app)


def test_versioned_health_route_and_docs_are_available():
    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["status"] == "healthy"

    docs = client.get("/docs")
    assert docs.status_code == 200
    assert "Digital Farming Support Center" in docs.text


def test_agriculture_advisory_route_generates_actionable_recommendations():
    response = client.get("/api/v1/advisory/field-health?crop=rice&village=Kallakurichi")
    assert response.status_code == 200
    payload = response.json()
    assert payload["crop"] == "rice"
    assert "recommendations" in payload
    assert isinstance(payload["recommendations"], list)
    assert payload["recommendations"]
