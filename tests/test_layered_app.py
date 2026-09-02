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


def test_irrigation_plan_route_generates_crop_and_water_schedule():
    response = client.get(
        "/api/v1/operations/irrigation-plan?crop=rice&soil_moisture_percent=42&rainfall_forecast_mm=6&field_area_ha=2.5"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["crop"] == "rice"
    assert payload["recommended_start"]
    assert payload["water_liters_per_ha"] > 0
    assert isinstance(payload["recommendations"], list)
    assert payload["recommendations"]


def test_soil_health_route_returns_nutrient_plan():
    response = client.get(
        "/api/v1/soil/health?crop=groundnut&ph=5.6&nitrogen=24&phosphorus=18&potassium=152"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["crop"] == "groundnut"
    assert payload["soil_status"]
    assert isinstance(payload["nutrient_actions"], list)
    assert payload["nutrient_actions"]
    assert payload["recommendation_summary"]
    assert isinstance(payload["fertilizer_plan"], list)
    assert payload["fertilizer_plan"]


def test_pest_monitoring_route_returns_risk_and_actions():
    response = client.get(
        "/api/v1/field/pest-monitor?crop=rice&field_condition=high_humidity&severity=moderate"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["crop"] == "rice"
    assert "risk_score" in payload
    assert payload["risk_score"] >= 0
    assert isinstance(payload["action_plan"], list)
    assert payload["action_plan"]


def test_crop_calendar_route_returns_seasonal_plan():
    response = client.get("/api/v1/season/crop-calendar?crop=rice&season=Kharif")
    assert response.status_code == 200
    payload = response.json()
    assert payload["crop"] == "rice"
    assert payload["season"] == "Kharif"
    assert isinstance(payload["activities"], list)
    assert payload["activities"]


def test_market_intelligence_route_returns_price_and_procurement_guidance():
    response = client.get("/api/v1/market/intelligence?crop=rice&market=Kallakurichi")
    assert response.status_code == 200
    payload = response.json()
    assert payload["crop"] == "rice"
    assert payload["market"] == "Kallakurichi"
    assert payload["recommended_action"]
    assert isinstance(payload["buyer_insights"], list)
    assert payload["buyer_insights"]


def test_sustainability_report_route_returns_carbon_and_regeneration_summary():
    response = client.get(
        "/api/v1/sustainability/carbon?farm_size_ha=5&soil_carbon_tons=2.4&water_use_liters=4200&energy_use_kwh=320"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["farm_size_ha"] == 5.0
    assert "carbon_status" in payload
    assert payload["carbon_status"]
    assert isinstance(payload["recommendations"], list)
    assert payload["recommendations"]


def test_procurement_traceability_route_returns_lot_status_and_verification():
    response = client.get(
        "/api/v1/procurement/traceability?crop=rice&lot_id=RICE-2041&batch_quality=good"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["crop"] == "rice"
    assert payload["lot_id"] == "RICE-2041"
    assert payload["batch_status"]
    assert isinstance(payload["verification_steps"], list)
    assert payload["verification_steps"]


def test_traceability_route_returns_origin_and_procurement_summary():
    response = client.get(
        "/api/v1/procurement/traceability?farmer=Kumaran&batch=RICE-24A&location=Kallakurichi&quality_grade=A"
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["farmer"] == "Kumaran"
    assert payload["batch"] == "RICE-24A"
    assert payload["quality_grade"] == "A"
    assert payload["traceability_status"]
    assert isinstance(payload["procurement_steps"], list)
    assert payload["procurement_steps"]
