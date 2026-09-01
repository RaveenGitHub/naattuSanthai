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
    assert "தகுதி" in detail_response.json()["data"]["eligibility_ta"] or "Eligibility" in detail_response.json()["data"]["eligibility_ta"]
    assert detail_response.json()["data"]["benefits_ta"]
    assert detail_response.json()["data"]["apply_steps_ta"]

    fetch_response = client.post("/api/fetch/update", headers={"X-User-Role": "admin"})
    assert fetch_response.status_code == 200
    assert fetch_response.json()["success"] is True

    monitoring_response = client.get("/api/fetch/status", headers={"X-User-Role": "admin"})
    assert monitoring_response.status_code == 200
    assert monitoring_response.json()["success"] is True
    assert isinstance(monitoring_response.json()["data"], dict)

    filtered_response = client.get("/api/schemes/archive?category=subsidy")
    assert filtered_response.status_code == 200
    assert filtered_response.json()["success"] is True
    assert isinstance(filtered_response.json()["data"], list)

    page_response = client.get("/government-schemes")
    assert page_response.status_code == 200
    assert "புதிய அறிவிப்புகள்" in page_response.text
    assert "காப்பக அறிவிப்புகள்" in page_response.text
    assert "தேடுக" in page_response.text or "வகை" in page_response.text

    filtered_page_response = client.get("/government-schemes?category=subsidy&search=PM-Kisan")
    assert filtered_page_response.status_code == 200
    assert "PM-Kisan" in filtered_page_response.text or "subsidy" in filtered_page_response.text.lower()

    detailed_page_response = client.get("/scheme-page/SCHEME-NEW-001")
    assert detailed_page_response.status_code == 200
    assert "தகுதி" in detailed_page_response.text
    assert "நன்மைகள்" in detailed_page_response.text
    assert "விண்ணப்ப படிகள்" in detailed_page_response.text


def test_soil_health_page_renders_farmer_actionable_summary():
    response = client.get("/soil-health?crop=groundnut&ph=5.6&nitrogen=24&phosphorus=18&potassium=152")
    assert response.status_code == 200
    assert "மண் சோதனை" in response.text or "Soil health" in response.text
    assert "groundnut" in response.text.lower() or "நிலக்கடலை" in response.text
    assert "உரம்" in response.text or "Fertilizer" in response.text
