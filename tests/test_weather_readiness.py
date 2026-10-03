import json

import pytest
from fastapi.testclient import TestClient

import services
from app import app
from database import init_db


@pytest.fixture
def readiness_environment(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "weather.db"))
    init_db()
    for setting in (
        "IMD_API_KEY", "IMD_API_TOKEN", "IMD_CITY_FORECAST_URL",
        "IMD_WEATHER_FEED_URL", "TNSDMA_WEATHER_FEED_URL",
    ):
        monkeypatch.delenv(setting, raising=False)

    def forbidden_network(*args, **kwargs):
        pytest.fail("Readiness must not fetch weather")

    monkeypatch.setattr(services, "urlopen", forbidden_network)


def test_unconfigured_rollout_has_explicit_blockers(readiness_environment):
    result = services.get_weather_rollout_readiness()
    assert result["status"] == "blocked"
    assert result["configuration"]["status"] == "blocked"
    assert set(result["blockers"]) == {
        "missing_imd_api_key", "missing_imd_api_token",
        "no_completed_refresh", "incomplete_fresh_city_coverage",
    }
    assert result["last_refresh_status"] == "never_run"
    assert result["scheduler_registration"] == "not_checked"
    assert result["long_range_live_verification"] == "not_verified"
    assert services.list_weather_fetch_history() == []


def test_credentials_are_presence_only_not_proof_of_readiness(readiness_environment, monkeypatch):
    monkeypatch.setenv("IMD_API_KEY", "private-key-123")
    monkeypatch.setenv("IMD_API_TOKEN", "private-token-456")
    result = services.get_weather_rollout_readiness()
    assert result["configuration"]["status"] == "configured"
    assert result["configuration"]["network_verified"] is False
    assert result["status"] == "blocked"
    serialized = json.dumps(result)
    assert "private-key-123" not in serialized
    assert "private-token-456" not in serialized


@pytest.mark.parametrize("url", [
    "http://api.imd.gov.in/api/v1/cityforecast",
    "https://example.com/private",
    "https://[broken",
])
def test_invalid_endpoint_is_reported_without_url_leak(readiness_environment, monkeypatch, url):
    monkeypatch.setenv("IMD_CITY_FORECAST_URL", url)
    result = services.get_weather_configuration_readiness()
    assert "invalid_imd_city_endpoint" in result["blockers"]
    assert url not in json.dumps(result)


def test_feed_mode_matches_fetcher_precedence_and_hides_urls(readiness_environment, monkeypatch):
    monkeypatch.setenv("TNSDMA_WEATHER_FEED_URL", "https://tnsdma.tn.gov.in/feed?token=private-feed-token")
    result = services.get_weather_configuration_readiness()
    assert result["mode"] == "authorized_json_feeds"
    assert result["status"] == "configured"
    assert result["credential_presence"] == {"api_key": False, "api_token": False}
    assert "private-feed-token" not in json.dumps(result)


def test_ignored_feed_is_diagnosed_without_exposing_value(readiness_environment, monkeypatch, caplog):
    monkeypatch.setenv("TNSDMA_WEATHER_FEED_URL", "https://[broken")
    result = services.get_weather_configuration_readiness()
    assert result["mode"] == "official_imd_city_api"
    assert result["warnings"] == ["ignored_tnsdma_weather_feed_url"]
    assert result["feed_checks"][1]["configured"] is True
    assert result["feed_checks"][1]["accepted"] is False
    assert "https://[broken" not in caplog.text


def test_malformed_official_endpoint_fails_without_network(readiness_environment, monkeypatch):
    monkeypatch.setenv("IMD_API_KEY", "key")
    monkeypatch.setenv("IMD_API_TOKEN", "token")
    monkeypatch.setenv("IMD_CITY_FORECAST_URL", "https://[broken")
    result = services._fetch_imd_city_forecasts(15)
    assert result["status"] == "failed"
    assert result["records"] == []
    assert "https://[broken" not in json.dumps(result)


@pytest.mark.parametrize("refresh,current,expected", [
    ("success", 35, "ready"), ("partial", 35, "blocked"),
    ("success", 34, "blocked"), ("failed", 0, "blocked"),
])
def test_rollout_requires_complete_refresh_and_current_coverage(
    readiness_environment, monkeypatch, refresh, current, expected,
):
    monkeypatch.setenv("IMD_API_KEY", "key")
    monkeypatch.setenv("IMD_API_TOKEN", "token")
    monkeypatch.setattr(services, "get_weather_fetch_status", lambda: {
        "fetch_monitoring": {"last_run": {"status": refresh}},
        "city_coverage": {"current": current, "total": 35, "missing": []},
    })
    result = services.get_weather_rollout_readiness()
    assert result["status"] == expected
    assert result["long_range_live_verification"] == "not_verified"


def test_readiness_api_is_admin_only_and_does_not_mutate_history(readiness_environment):
    client = TestClient(app)
    assert client.get("/api/weather/rollout/readiness").status_code == 403
    assert client.get("/api/weather/rollout/readiness", headers={"X-User-Role": "operator"}).status_code == 403
    response = client.get("/api/weather/rollout/readiness", headers={"X-User-Role": "admin"})
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["status"] == "blocked"
    assert services.list_weather_fetch_history() == []
