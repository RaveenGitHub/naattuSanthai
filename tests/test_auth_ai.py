from fastapi.testclient import TestClient

from app import app
from security import create_user

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


def test_ai_diagnosis_history_is_available_to_authorized_user():
    login = client.post(
        "/auth/login",
        json={"username": "operator1", "password": "password123"},
    )
    token = login.json()["token"]

    client.post(
        "/api/diagnose",
        json={"crop_type": "Groundnut", "image_url": "https://example.com/groundnut.jpg", "notes": "Wilting patch"},
        headers={"Authorization": f"Bearer {token}"},
    )

    response = client.get(
        "/api/diagnose/history",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True
    assert isinstance(body["data"], list)
    assert any(item["crop_type"] == "Groundnut" for item in body["data"])


def test_new_user_can_be_created_and_authenticated_from_database():
    username = "newoperator"
    result = create_user(username, "secretpass", "operator")

    assert result["username"] == username
    assert result["role"] == "operator"

    login = client.post(
        "/auth/login",
        json={"username": username, "password": "secretpass"},
    )
    assert login.status_code == 200
    assert login.json()["role"] == "operator"
