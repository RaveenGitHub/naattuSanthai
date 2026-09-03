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


def test_weather_forecast_and_fetch_routes():
    daily_response = client.get("/api/weather/daily?region=Kallakurichi")
    assert daily_response.status_code == 200
    assert daily_response.json()["success"] is True
    assert isinstance(daily_response.json()["data"], list)

    weekly_response = client.get("/api/weather/weekly?region=Kallakurichi")
    assert weekly_response.status_code == 200
    assert weekly_response.json()["success"] is True
    assert isinstance(weekly_response.json()["data"], list)

    monthly_response = client.get("/api/weather/monthly?region=Kallakurichi")
    assert monthly_response.status_code == 200
    assert monthly_response.json()["success"] is True
    assert isinstance(monthly_response.json()["data"], list)

    fetch_response = client.post("/api/weather/fetch", headers={"X-User-Role": "admin"})
    assert fetch_response.status_code == 200
    assert fetch_response.json()["success"] is True
    assert isinstance(fetch_response.json()["data"], dict)

    status_response = client.get("/api/weather/fetch/status", headers={"X-User-Role": "admin"})
    assert status_response.status_code == 200
    assert status_response.json()["success"] is True
    assert isinstance(status_response.json()["data"], dict)


def test_weather_fetch_status_contains_source_and_retention_metadata():
    response = client.get("/api/weather/fetch/status", headers={"X-User-Role": "admin"})
    assert response.status_code == 200
    payload = response.json()["data"]
    assert "source_compliance" in payload
    assert "retention_days" in payload
    assert "quality_gate" in payload
    assert "archive_policy" in payload
    assert payload["retention_days"] >= 7
    assert payload["archive_policy"]["latest_window_days"] == 7
    assert payload["archive_policy"]["monthly_retention_months"] >= 12


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

    scheme_status_payload = monitoring_response.json()["data"]
    assert "source_compliance" in scheme_status_payload
    assert "retention_days" in scheme_status_payload
    assert "quality_gate" in scheme_status_payload
    assert "ai_validation" in scheme_status_payload
    assert scheme_status_payload["retention_days"] >= 7

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
    assert "பரிந்துரை" in response.text or "Recommendation" in response.text
    assert "உர திட்டம்" in response.text or "Fertilizer plan" in response.text or "fertilizer" in response.text.lower()


def test_weather_page_renders_region_forecast_and_guidance():
    response = client.get("/weather?region=Kallakurichi&period=daily")
    assert response.status_code == 200
    assert "வானிலை" in response.text
    assert "Kallakurichi" in response.text or "கல்லக்குறிச்சி" in response.text
    assert "பரிந்துரை" in response.text or "Advisory" in response.text
    assert "மழை" in response.text or "Rain" in response.text


def test_market_intelligence_page_renders_price_trend_and_action():
    response = client.get("/market-intelligence?crop=rice&market=Kallakurichi")
    assert response.status_code == 200
    assert "சந்தை" in response.text or "Market" in response.text
    assert "rice" in response.text.lower() or "நெல்" in response.text
    assert "விலை" in response.text or "Price" in response.text
    assert "பரிந்துரை" in response.text or "Recommendation" in response.text
