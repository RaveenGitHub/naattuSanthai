import json

import pytest
from fastapi.testclient import TestClient

import services
from app import app
from database import init_db


def long_range_record(period):
    return {
        "city": "Chennai", "period": period,
        "forecast_date": "2026-10-03", "temperature_c": 30,
        "summary_ta": f"Published {period} outlook",
        "advisory_ta": f"Published {period} advisory",
    }


@pytest.mark.parametrize("period", ["weekly", "monthly"])
def test_long_range_feed_roundtrip_preserves_period(monkeypatch, tmp_path, period):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "weather.db"))
    init_db()
    monkeypatch.setenv("TNSDMA_WEATHER_FEED_URL", "https://tnsdma.tn.gov.in/forecast")
    monkeypatch.delenv("IMD_WEATHER_FEED_URL", raising=False)

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps([long_range_record(period)]).encode("utf-8")

    monkeypatch.setattr(services, "urlopen", lambda *args, **kwargs: Response())
    result = services.fetch_authorized_weather_updates()
    assert result["status"] == "partial"
    assert result["city_coverage"]["received"] == 0
    assert services.list_latest_weather("Chennai") == []
    assert services.list_weather_forecast("daily", "Chennai") == []
    client = TestClient(app)
    stored = client.get(f"/api/weather/{period}?region=Chennai").json()["data"]
    assert len(stored) == 1
    assert stored[0]["period"] == period
    assert stored[0]["rainfall_mm"] is None
    page = client.get(f"/weather?region=Chennai&period={period}")
    assert page.status_code == 200
    assert f"Published {period} outlook" in page.text
    assert f"Published {period} advisory" in page.text
    assert f"Published {period} outlook" not in client.get("/weather?region=Chennai").text


@pytest.mark.parametrize("period", ["weekly", "monthly"])
@pytest.mark.parametrize("field,value", [
    ("forecast_date", None), ("forecast_date", "not-a-date"),
    ("summary_ta", ""), ("advisory_ta", None),
    ("period", "yearly"), ("period", []),
])
def test_invalid_long_range_contract_is_logged_and_rejected(period, field, value, caplog):
    record = long_range_record(period)
    record[field] = value
    assert services._normalize_weather_payload([record], "TNSDMA") == []
    assert "Rejected weather record for Chennai" in caplog.text


def test_daily_payload_without_period_keeps_existing_contract():
    records = services._normalize_weather_payload(
        [{"city": "Chennai", "temperature_c": 30}], "TNSDMA",
    )
    assert records[0]["period"] == "daily"


def test_imd_today_forecast_does_not_become_long_range_forecast():
    records = services._normalize_imd_city_forecast([{
        "Station_Name": "Chennai", "Todays_Forecast_Max_Temp": 30,
        "period": "monthly",
    }])
    assert records
    assert all(record.get("period", "daily") == "daily" for record in records)


def test_weather_page_rejects_unknown_period():
    response = TestClient(app).get("/weather?period=yearly")
    assert response.status_code == 422
    assert response.json()["detail"] == "period must be daily, weekly, or monthly"
