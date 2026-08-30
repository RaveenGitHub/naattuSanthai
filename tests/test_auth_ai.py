from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_login_returns_token_for_valid_user():
    response = client.post(
        "/auth/login",
        json={"username": "operator1", "password": "password123"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "token" in payload
    assert payload["role"] == "operator"


def test_ai_diagnosis_returns_recommendation():
    login = client.post(
        "/auth/login",
        json={"username": "operator1", "password": "password123"},
    )
    token = login.json()["token"]

    response = client.post(
        "/api/diagnose",
        json={"crop_type": "Rice", "image_url": "https://example.com/rice.jpg", "notes": "Yellowing leaves and spots"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert "diagnosis" in body["data"]
    assert "recommendation" in body["data"]
