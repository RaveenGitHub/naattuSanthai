import pytest
from fastapi.testclient import TestClient

import services
from app import app
from database import init_db
from digital_farming import weather_refresh


@pytest.fixture
def weather_database(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "weather.db"))
    init_db()


def weather_result(status, cities):
    return {
        "status": status,
        "records": [{"region": city} for city in cities],
        "sources": [{"name": "India Meteorological Department", "status": status, "records": len(cities)}],
        "errors": [] if cities else ["No source configured."],
    }


def test_weather_refresh_persists_partial_and_unconfigured_runs(weather_database, monkeypatch):
    results = iter([
        weather_result("partial", ["Chennai"]),
        weather_result("not_configured", []),
    ])
    monkeypatch.setattr(services, "_fetch_authorized_weather_updates", lambda timeout_seconds: next(results))

    first = services.fetch_authorized_weather_updates()
    second = services.fetch_authorized_weather_updates()
    history = services.list_weather_fetch_history()

    assert first["city_coverage"]["received"] == 1
    assert second["city_coverage"]["received"] == 0
    assert len(history) == 2
    assert history[0]["status"] == "not_configured"
    assert history[0]["error_count"] == 1
    assert history[1]["status"] == "partial"
    assert history[1]["city_coverage"]["total"] == 35
    assert "Chennai" not in history[1]["city_coverage"]["missing"]
    assert len(history[1]["city_coverage"]["missing"]) == 34
    assert history[0]["finished_at"] >= history[0]["started_at"]


def test_weather_monitoring_reports_recent_full_success_rate(weather_database, monkeypatch):
    cities = [item["city"] for item in services.list_tamil_nadu_weather_cities()]
    results = iter([
        weather_result("success", cities),
        weather_result("partial", ["Chennai"]),
        weather_result("failed", []),
    ])
    monkeypatch.setattr(services, "_fetch_authorized_weather_updates", lambda timeout_seconds: next(results))
    for _ in range(3):
        services.fetch_authorized_weather_updates()

    monitoring = services.get_weather_fetch_status()["fetch_monitoring"]
    assert monitoring["status"] == "failed"
    assert monitoring["runs"] == 3
    assert monitoring["successful_runs"] == 1
    assert monitoring["partial_runs"] == 1
    assert monitoring["failed_runs"] == 1
    assert monitoring["success_rate_pct"] == pytest.approx(100 / 3, abs=0.01)
    assert monitoring["last_run"]["city_coverage"]["received"] == 0


def test_weather_monitoring_never_claims_a_run_before_first_refresh(weather_database):
    monitoring = services.get_weather_fetch_status()["fetch_monitoring"]
    assert monitoring["status"] == "never_run"
    assert monitoring["last_run"] is None
    assert monitoring["success_rate_pct"] is None


def test_weather_fetch_history_is_admin_only_and_bounded(weather_database):
    client = TestClient(app)
    assert client.get("/api/weather/fetch/history").status_code == 403
    headers = {"X-User-Role": "admin"}
    response = client.get("/api/weather/fetch/history?limit=1", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] == []
    assert client.get("/api/weather/fetch/history?limit=0", headers=headers).status_code == 422
    assert client.get("/api/weather/fetch/history?limit=101", headers=headers).status_code == 422


def test_weather_history_does_not_store_credentials_or_raw_errors(weather_database, monkeypatch):
    result = weather_result("failed", [])
    result["sources"][0]["url"] = "https://api.imd.gov.in/?token=private-token"
    result["errors"] = ["private-token"]
    monkeypatch.setattr(services, "_fetch_authorized_weather_updates", lambda timeout_seconds: result)
    services.fetch_authorized_weather_updates()
    history = services.list_weather_fetch_history()
    assert "private-token" not in str(history)
    assert history[0]["error_count"] == 1
    assert history[0]["sources"][0]["status"] == "failed"


def test_weather_monitoring_does_not_confuse_freshness_with_last_run(weather_database, monkeypatch):
    monkeypatch.setattr(
        services, "_fetch_authorized_weather_updates",
        lambda timeout_seconds: weather_result("not_configured", []),
    )
    services.fetch_authorized_weather_updates()
    status = services.get_weather_fetch_status()
    assert status["city_coverage"]["current"] == 0
    assert status["fetch_monitoring"]["last_run"]["city_coverage"]["received"] == 0
    assert status["quality_gate"]["status"] == "warning"


def test_weather_monitoring_window_uses_latest_twenty_runs(weather_database, monkeypatch):
    monkeypatch.setattr(
        services, "_fetch_authorized_weather_updates",
        lambda timeout_seconds: weather_result("failed", []),
    )
    for _ in range(21):
        services.fetch_authorized_weather_updates()
    assert len(services.list_weather_fetch_history()) == 20
    assert len(services.list_weather_fetch_history(100)) == 21
    assert services.get_weather_fetch_status()["fetch_monitoring"]["runs"] == 20


def test_manual_refresh_and_worker_share_persistent_history(weather_database, monkeypatch):
    for name in ("IMD_API_KEY", "IMD_API_TOKEN", "IMD_WEATHER_FEED_URL", "TNSDMA_WEATHER_FEED_URL"):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(weather_refresh, "load_dotenv", lambda *args, **kwargs: False)
    monkeypatch.setattr(weather_refresh, "configure_logging", lambda: services.logging.getLogger("test-weather"))
    client = TestClient(app)
    response = client.post("/api/weather/fetch", headers={"X-User-Role": "admin"})
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["data"]["fetch_status"] == "not_configured"
    assert weather_refresh.main() == 1
    history = client.get("/api/weather/fetch/history", headers={"X-User-Role": "admin"}).json()["data"]
    assert len(history) == 2
    assert all(run["status"] == "not_configured" for run in history)
    page = client.get("/weather-quality")
    assert page.status_code == 200
    assert "Refresh monitoring" in page.text
    assert "not_configured" in page.text
    assert "0.00%" in page.text


def test_full_coverage_with_a_source_error_is_not_complete_success(weather_database, monkeypatch):
    cities = [item["city"] for item in services.list_tamil_nadu_weather_cities()]
    result = weather_result("success", cities)
    result["errors"] = ["Secondary source failed."]
    monkeypatch.setattr(services, "_fetch_authorized_weather_updates", lambda timeout_seconds: result)
    assert services.fetch_authorized_weather_updates()["status"] == "partial"
    monitoring = services.get_weather_fetch_status()["fetch_monitoring"]
    assert monitoring["partial_runs"] == 1
    assert monitoring["success_rate_pct"] == 0
