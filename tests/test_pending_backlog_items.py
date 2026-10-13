from fastapi.testclient import TestClient

from app import app as main_app
from database import init_db
from diagnostics import DiseaseInferenceResult
from digital_farming.app import create_app
from security import create_token, create_user


def _actor(monkeypatch, tmp_path, role="operator"):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "backlog.db"))
    init_db()
    username = f"backlog_{role}"
    create_user(username, "SecurePass123", role)
    return username, create_token(username)


def test_shell_has_voice_controls_and_privacy_safe_offline_support():
    client = TestClient(main_app)
    shell = client.get("/", headers={"accept": "text/html"})
    manifest = client.get("/manifest.webmanifest")
    icon = client.get("/app-icon.svg")
    worker = client.get("/service-worker.js")
    offline = client.get("/offline")

    assert shell.status_code == manifest.status_code == icon.status_code == worker.status_code == offline.status_code == 200
    assert "Read aloud" in shell.text
    assert "speechSynthesis" in shell.text
    assert manifest.json()["start_url"] == "/"
    assert manifest.json()["icons"][0]["src"] == "/app-icon.svg"
    assert "caches.match('/offline')" in worker.text
    assert "digital-farming-shell-" in worker.text
    assert "தனிப்பட்ட அல்லது விவசாயத் தரவை ஆஃப்லைனில் காட்டுவதில்லை" in offline.text
    assert "SAFE_SHELL_PATHS = ['/', '/offline']" in worker.text
    assert "headers: {Accept: 'text/html'}" in worker.text


def test_traceability_lots_are_authenticated_append_only_and_unverified(monkeypatch, tmp_path):
    _, token = _actor(monkeypatch, tmp_path)
    client = TestClient(create_app())
    headers = {"Authorization": f"Bearer {token}"}

    denied = client.post(
        "/api/v1/procurement/lots",
        json={"lot_id": "LOT-1", "crop": "rice", "farmer": "Kannan", "origin": "Village"},
    )
    assert denied.status_code == 401

    created = client.post(
        "/api/v1/procurement/lots",
        headers=headers,
        json={"lot_id": "LOT-1", "crop": "rice", "farmer": "Kannan", "origin": "Village", "quality_grade": "A"},
    )
    assert created.status_code == 201
    assert created.json()["evidence_status"] == "incomplete"
    assert created.json()["quality_grade_status"] == "self_reported"
    assert created.json()["independently_verified"] is False

    duplicate = client.post(
        "/api/v1/procurement/lots",
        headers=headers,
        json={"lot_id": "LOT-1", "crop": "rice", "farmer": "Kannan", "origin": "Village"},
    )
    assert duplicate.status_code == 409

    for event_type in ("harvested", "graded", "collected", "transported", "buyer_handoff"):
        response = client.post(
            "/api/v1/procurement/lots/LOT-1/events",
            headers=headers,
            json={"event_type": event_type, "location": "Kallakurichi", "notes": "Recorded by field operator"},
        )
        assert response.status_code == 201

    lot = client.get("/api/v1/procurement/lots/LOT-1", headers=headers)
    assert lot.status_code == 200
    assert lot.json()["evidence_status"] == "complete_unverified"
    assert lot.json()["independently_verified"] is False
    assert lot.json()["missing_event_types"] == []
    assert len(lot.json()["events"]) == 6

    invalid = client.post(
        "/api/v1/procurement/lots/LOT-1/events",
        headers=headers,
        json={"event_type": "certified", "location": "Kallakurichi"},
    )
    assert invalid.status_code == 422


def test_pilot_feedback_is_validated_persisted_and_not_signoff(monkeypatch, tmp_path):
    username, token = _actor(monkeypatch, tmp_path, role="operator")
    client = TestClient(main_app)
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post(
        "/api/admin/pilot-feedback",
        headers=headers,
        json={
            "district": "Villupuram",
            "village": "Kallakurichi",
            "farmer_group": "Pilot group A",
            "scheme_under_test": "Scheme guidance",
            "clarity_score": 4,
            "usefulness_score": 5,
            "issues": ["Text is small"],
            "recommended_change": "Increase text size",
            "feedback_notes": "Recorded after a field walk-through",
        },
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "recorded"

    admin_name = "backlog_admin"
    create_user(admin_name, "SecurePass123", "admin")
    admin_token = create_token(admin_name)
    feedback = client.get(
        "/api/admin/pilot-feedback",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert feedback.status_code == 200
    assert feedback.json()["data"]["summary"]["total_submissions"] == 1
    assert feedback.json()["data"]["items"][0]["submitted_by"] == username

    readiness = client.get(
        "/api/admin/pilot-readiness",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert readiness.status_code == 200
    data = readiness.json()["data"]
    assert data["feedback_summary"]["total_submissions"] == 1
    feedback_check = next(item for item in data["checklist"] if "feedback logged" in item["item"])
    assert feedback_check["status"] == "recorded"
    assert data["status"] == "warning"

    invalid_score = client.post(
        "/api/admin/pilot-feedback",
        headers=headers,
        json={"clarity_score": 6},
    )
    assert invalid_score.status_code == 422


def test_soil_and_sustainability_reject_invalid_measurements():
    client = TestClient(create_app())
    negative_soil = client.get(
        "/api/v1/soil/health?crop=rice&ph=6&nitrogen=-1&phosphorus=10&potassium=20"
    )
    invalid_farm_size = client.get(
        "/api/v1/sustainability/carbon?farm_size_ha=0&soil_carbon_tons=1&water_use_liters=1&energy_use_kwh=1"
    )
    assert negative_soil.status_code == 422
    assert invalid_farm_size.status_code == 422

    report = client.get(
        "/api/v1/sustainability/carbon?farm_size_ha=0.5&soil_carbon_tons=2&water_use_liters=1000&energy_use_kwh=10"
    )
    assert report.status_code == 200
    assert report.json()["assessment_basis"].startswith("Indicative estimates")


def test_disease_inference_provider_contract_stays_manual_review(monkeypatch, tmp_path):
    username, token = _actor(monkeypatch, tmp_path)

    class Provider:
        def __init__(self):
            self.received = None

        def infer(self, crop_type, image_bytes, media_type):
            self.received = (crop_type, image_bytes, media_type)
            return DiseaseInferenceResult(
                label="Possible leaf blight",
                confidence=0.92,
                provider="test-provider",
                model_version="test-v1",
            )

    provider = Provider()
    monkeypatch.setattr(main_app.state, "disease_inference_provider", provider)
    client = TestClient(main_app)
    response = client.post(
        "/api/diagnose/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"crop_type": "Rice", "notes": "Leaf spots"},
        files={"file": ("rice.jpg", b"\xff\xd8\xfftest-image", "image/jpeg")},
    )

    assert response.status_code == 200, response.text
    result = response.json()["data"]
    assert provider.received == ("Rice", b"\xff\xd8\xfftest-image", "image/jpeg")
    assert result["inference_status"] == "prediction_available_manual_review"
    assert result["provider_prediction"]["label"] == "Possible leaf blight"
    assert result["provider_prediction"]["confidence_score"] == 0.92
    assert result["manual_review_required"] is True
    assert result["diagnosis"] == "Image review required"
