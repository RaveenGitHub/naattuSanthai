from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

import services
from app import app
from database import get_connection, init_db


NOW = datetime(2026, 10, 3, 20, tzinfo=timezone.utc)


def forecast(source_date, period="daily", received=NOW):
    return {
        "id": "sample", "period": period, "forecast_date": source_date,
        "created_at": received.isoformat(),
    }


@pytest.mark.parametrize("period,days", [("daily", 0), ("weekly", 7), ("monthly", 31)])
def test_source_date_bounds_use_india_calendar(period, days):
    today = "2026-10-04"
    assert services.weather_forecast_status(forecast(today, period), NOW) == "current"
    boundary = datetime(2026, 10, 4) + timedelta(days=days)
    assert services.weather_forecast_status(forecast(boundary.date().isoformat(), period), NOW) == "current"
    assert services.weather_forecast_status(
        forecast((boundary + timedelta(days=1)).date().isoformat(), period), NOW,
    ) == "stale"
    assert services.weather_forecast_status(forecast("2026-09-27", period), NOW) == "current"
    assert services.weather_forecast_status(forecast("2026-09-26", period), NOW) == "stale"


def test_receipt_age_bounds_and_offsets():
    assert services.weather_forecast_status(forecast("2026-10-04", received=NOW - timedelta(days=7)), NOW) == "current"
    assert services.weather_forecast_status(forecast("2026-10-04", received=NOW - timedelta(days=7, seconds=1)), NOW) == "stale"
    assert services.weather_forecast_status(forecast("2026-10-04", received=NOW + timedelta(seconds=1)), NOW) == "stale"
    record = forecast("2026-10-03T20:00:00Z")
    record["created_at"] = "2026-10-04T01:30:00+05:30"
    assert services.weather_forecast_status(record, NOW) == "current"
    record["created_at"] = "2026-10-03T20:00:00"
    assert services.weather_forecast_status(record, NOW) == "current"


@pytest.mark.parametrize("field,value", [
    ("forecast_date", "bad"), ("forecast_date", None),
    ("created_at", ""), ("created_at", []), ("period", "yearly"),
])
def test_invalid_dates_are_unavailable_and_logged(field, value, caplog):
    record = forecast("2026-10-04")
    record[field] = value
    assert services.weather_forecast_status(record, NOW) == "unavailable"
    assert "invalid dates or period" in caplog.text


def test_recently_received_old_forecast_is_not_current_anywhere(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "weather.db"))
    init_db()
    now = datetime.now(timezone.utc)
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO weather_forecasts "
            "(id,region,period,forecast_date,temperature_c,summary_ta,advisory_ta,source_name,created_at) "
            "VALUES ('old','Chennai','daily',?,30,'Old source outlook','Old advisory','IMD',?)",
            ((now - timedelta(days=30)).date().isoformat(), now.isoformat()),
        )
    assert services.list_latest_weather("Chennai") == []
    assert services.list_archived_weather("Chennai")[0]["id"] == "old"
    city = next(item for item in services.list_tamil_nadu_city_weather() if item["city"] == "Chennai")
    assert city["forecast_status"] == "stale"
    assert city["forecast"] is None
    status = services.get_weather_fetch_status()
    assert status["latest_window_records"] == 0
    assert status["archived_records"] == 1
    assert status["city_coverage"]["current"] == 0
    assert status["archive_policy"]["source_date_future_horizon_days"] == {
        "daily": 0, "weekly": 7, "monthly": 31,
    }
    client = TestClient(app)
    for path in ("/weather?region=Chennai", "/weather-market?region=Chennai"):
        assert "Old source outlook" not in client.get(path).text
    assert client.get("/api/weather/latest?region=Chennai").json()["data"] == []


def test_bad_new_record_does_not_hide_existing_current_city_forecast(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "weather.db"))
    init_db()
    now = datetime.now(timezone.utc)
    with get_connection() as conn:
        for key, date, received in (
            ("good", now.date().isoformat(), now - timedelta(seconds=1)),
            ("bad", "invalid", now),
        ):
            conn.execute(
                "INSERT INTO weather_forecasts "
                "(id,region,period,forecast_date,temperature_c,summary_ta,advisory_ta,source_name,created_at) "
                "VALUES (?,'Chennai','daily',?,30,'Summary','Advisory','IMD',?)",
                (key, date, received.isoformat()),
            )
    city = next(item for item in services.list_tamil_nadu_city_weather() if item["city"] == "Chennai")
    assert city["forecast_status"] == "current"
    assert city["forecast"]["id"] == "good"
