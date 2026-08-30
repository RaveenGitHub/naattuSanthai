from fastapi.testclient import TestClient

from app import app

client = TestClient(app)


def test_farmer_role_can_read_weather_and_market():
    response = client.get("/api/weather/alerts", headers={"X-User-Role": "farmer"})
    assert response.status_code == 200

    market = client.get("/api/market-prices?crop_name=Rice", headers={"X-User-Role": "farmer"})
    assert market.status_code == 200


def test_operator_role_can_create_soil_tests():
    payload = {
        "farm_id": "FARM-001",
        "ph": 6.2,
        "moisture_percent": 40,
        "nitrogen": 25,
        "phosphorus": 18,
        "potassium": 22,
        "fertility_status": "Good"
    }
    response = client.post("/api/soil-tests", json=payload, headers={"X-User-Role": "operator"})
    assert response.status_code == 200


def test_admin_role_can_access_schemes():
    response = client.get("/api/schemes?farmer_id=FARMER-001", headers={"X-User-Role": "admin"})
    assert response.status_code == 200


def test_non_admin_cannot_create_farm_without_role():
    payload = {"farmer_id": "FARMER-001", "acreage_hectares": 3.5, "location": "North Field", "soil_type": "Clay"}
    response = client.post("/api/farms", json=payload, headers={"X-User-Role": "farmer"})
    assert response.status_code == 403
