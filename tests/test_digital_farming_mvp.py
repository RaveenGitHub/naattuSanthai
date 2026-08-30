from digital_farming_mvp import AdvisoryService, DigitalFarmingMVP, NotificationService, SoilTestRecord, generate_backend_mvp_plan


def test_mvp_blueprint_has_modules_and_endpoints():
    blueprint = DigitalFarmingMVP("Digital Farming Support Center")

    assert "Farmer Service" in blueprint.modules()
    assert "Weather Service" in blueprint.modules()
    assert "GET /api/farmers" in blueprint.endpoints()
    assert "POST /api/notifications" in blueprint.endpoints()


def test_advisory_service_generates_recommendation_for_soil_state():
    soil = SoilTestRecord(
        soil_test_id="ST-001",
        farm_id="F-001",
        ph=5.7,
        moisture_percent=28,
        nitrogen=20,
        phosphorus=14,
        potassium=18,
        fertility_status="Low",
    )

    recommendation = AdvisoryService.create_recommendation(soil, "Rice")

    assert recommendation.crop_name == "Rice"
    assert "Add lime" in recommendation.recommendation_text
    assert recommendation.confidence_score > 0


def test_notification_service_builds_alert_payload():
    payload = NotificationService.build_weather_alert("Kallakurichi", "Rainstorm", "High")

    assert payload["village"] == "Kallakurichi"
    assert payload["severity"] == "High"
    assert "Rainstorm" in payload["message"]


def test_backend_mvp_plan_contains_product_summary():
    plan = generate_backend_mvp_plan("Digital Farming Support Center")

    assert "Digital Farming Support Center MVP Backend Blueprint" in plan
    assert "Technology Stack" in plan
    assert "Implementation Plan" in plan
    assert "offline" in plan.lower()
