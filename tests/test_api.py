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
    assert response.json()["status"] == "healthy"


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
