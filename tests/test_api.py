from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "digital-farming-support-center"
    assert "database" in body
    assert body["database"]["status"] == "healthy"


def test_farmer_creation_and_listing():
    payload = {"name": "Raja", "phone": "9876543210", "village": "Kallakurichi", "language": "Tamil"}
    create_response = client.post("/api/farmers", json=payload)
    assert create_response.status_code == 200

    list_response = client.get("/api/farmers")
    assert list_response.status_code == 200
    assert isinstance(list_response.json()["data"], list)


def test_weather_alerts_endpoint():
    response = client.get("/api/weather/alerts?village=Kallakurichi")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_market_prices_endpoint():
    response = client.get("/api/market-prices?crop_name=Rice")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_government_scheme_latest_and_archive_endpoints():
    latest_response = client.get("/api/schemes/latest")
    assert latest_response.status_code == 200
    assert latest_response.json()["success"] is True
    assert isinstance(latest_response.json()["data"], list)

    archive_response = client.get("/api/schemes/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["success"] is True
    assert isinstance(archive_response.json()["data"], list)

    compatibility_response = client.get("/api/schemes?farmer_id=FARMER-001", headers={"X-User-Role": "admin"})
    assert compatibility_response.status_code == 200
    assert compatibility_response.json()["success"] is True

    detail_response = client.get("/api/scheme/SCHEME-NEW-001")
    assert detail_response.status_code == 200
    assert detail_response.json()["success"] is True
    assert detail_response.json()["data"]["title_ta"]

    page_response = client.get("/government-schemes")
    assert page_response.status_code == 200
    assert "புதிய அறிவிப்புகள்" in page_response.text
