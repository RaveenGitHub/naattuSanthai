import uuid

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
    username = f"newoperator_{uuid.uuid4().hex[:8]}"
    result = create_user(username, "secretpass", "operator")

    assert result["username"] == username
    assert result["role"] == "operator"

    login = client.post(
        "/auth/login",
        json={"username": username, "password": "secretpass"},
    )
    assert login.status_code == 200
    assert login.json()["role"] == "operator"


def test_password_is_stored_hashed_in_database():
    username = f"hashuser_{uuid.uuid4().hex[:8]}"
    create_user(username, "verysecret", "operator")

    with __import__("sqlite3").connect("digital_farming.db") as conn:
        row = conn.execute("SELECT password FROM users WHERE username = ?", (username,)).fetchone()

    assert row is not None
    assert row[0] != "verysecret"
    assert row[0].startswith("pbkdf2_sha256$")


def test_admin_can_list_and_create_users():
    admin_login = client.post(
        "/auth/login",
        json={"username": "admin1", "password": "admin123"},
    )
    token = admin_login.json()["token"]

    list_response = client.get(
        "/api/users",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert list_response.status_code == 200
    assert any(item["username"] == "operator1" for item in list_response.json()["data"])

    new_username = f"adminuser_{uuid.uuid4().hex[:8]}"
    create_response = client.post(
        "/api/users",
        json={"username": new_username, "password": "securepass", "role": "farmer"},
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 200
    assert create_response.json()["data"]["username"] == new_username
