import json
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

import services
from app import app
from database import get_connection, init_db


OPTIONAL_METRICS = ("rainfall_mm", "humidity_pct", "wind_kmh", "moisture_percent")


@pytest.fixture
def weather_database(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "weather.db"))
    init_db()


def normalize(record, imd):
    if imd:
        return services._normalize_imd_city_forecast([{
            "Station_Name": "Chennai", "Todays_Forecast_Max_Temp": "30", **record,
        }])
    return services._normalize_weather_payload(
        [{"city": "Chennai", "temperature_c": "30", **record}], "TNSDMA",
    )


@pytest.mark.parametrize("imd", [False, True])
def test_missing_metrics_are_null_not_zero(imd):
    record = normalize({}, imd)[0]
    assert record["temperature_c"] == 30
    assert all(record[metric] is None for metric in OPTIONAL_METRICS)


@pytest.mark.parametrize("imd", [False, True])
def test_explicit_zero_metrics_are_preserved(imd):
    record = normalize({metric: 0 for metric in OPTIONAL_METRICS}, imd)[0]
    assert all(record[metric] == 0 for metric in OPTIONAL_METRICS)


@pytest.mark.parametrize("imd", [False, True])
@pytest.mark.parametrize("value", ["NaN", "Infinity", "-Infinity", "bad", True, {}, []])
def test_invalid_numbers_are_rejected_and_logged(imd, value, caplog):
    assert normalize({"rainfall_mm": value}, imd) == []
    assert "Rejected" in caplog.text
    assert "rainfall_mm must be a finite number" in caplog.text


@pytest.mark.parametrize("imd", [False, True])
@pytest.mark.parametrize("metric,value", [
    ("rainfall_mm", -1), ("wind_kmh", -1),
    ("humidity_pct", -1), ("humidity_pct", 101),
    ("moisture_percent", -1), ("moisture_percent", 101),
])
def test_out_of_range_metrics_are_rejected(imd, metric, value, caplog):
    assert normalize({metric: value}, imd) == []
    assert metric in caplog.text


@pytest.mark.parametrize("imd", [False, True])
def test_blank_optional_metrics_remain_missing(imd):
    record = normalize({metric: "  " for metric in OPTIONAL_METRICS}, imd)[0]
    assert all(record[metric] is None for metric in OPTIONAL_METRICS)


def test_temperature_is_required_and_imd_minimum_cannot_exceed_maximum(caplog):
    assert normalize({"Todays_Forecast_Min_temp": "31"}, True) == []
    assert normalize({"temperature_c": "NaN"}, False) == []
    assert services._normalize_weather_payload([{"city": "Chennai"}], "TNSDMA") == []
    assert "Minimum temperature exceeds maximum temperature" in caplog.text
    assert "Temperature is required" in caplog.text


def test_large_finite_temperatures_do_not_overflow_during_averaging():
    record = normalize({
        "Todays_Forecast_Max_Temp": 1e308,
        "Todays_Forecast_Min_temp": 1e308,
    }, True)[0]
    assert record["temperature_c"] == 1e308


def test_numeric_conversion_overflow_is_rejected(caplog):
    assert normalize({"temperature_c": 10 ** 1000}, False) == []
    assert "temperature_c must be a finite number" in caplog.text


def test_valid_records_survive_invalid_records_in_same_batch(caplog):
    records = services._normalize_weather_payload([
        {"city": "Chennai", "temperature_c": 30},
        {"city": "Salem", "temperature_c": 32, "humidity_pct": 200},
    ], "TNSDMA")
    assert [record["region"] for record in records] == ["Chennai"]
    assert "Salem" in caplog.text


def install_feed(monkeypatch, records, imd):
    if imd:
        monkeypatch.setenv("IMD_API_KEY", "test-key")
        monkeypatch.setenv("IMD_API_TOKEN", "test-token")
        monkeypatch.delenv("IMD_WEATHER_FEED_URL", raising=False)
        monkeypatch.delenv("TNSDMA_WEATHER_FEED_URL", raising=False)
    else:
        monkeypatch.setenv("TNSDMA_WEATHER_FEED_URL", "https://tnsdma.tn.gov.in/forecast")
        monkeypatch.delenv("IMD_WEATHER_FEED_URL", raising=False)

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return False

        def read(self):
            return json.dumps(records).encode("utf-8")

    monkeypatch.setattr(services, "urlopen", lambda *args, **kwargs: Response())


@pytest.mark.parametrize("imd", [False, True])
@pytest.mark.parametrize("zero", [False, True])
def test_missing_and_zero_metrics_roundtrip_through_api_and_both_views(
    weather_database, monkeypatch, imd, zero,
):
    record = (
        {"Station_Name": "Chennai", "Todays_Forecast_Max_Temp": "30"}
        if imd else {"city": "Chennai", "temperature_c": "30"}
    )
    if zero:
        record.update({metric: 0 for metric in OPTIONAL_METRICS})
    install_feed(monkeypatch, [record], imd)
    result = services.fetch_authorized_weather_updates()
    assert result["city_coverage"]["received"] == 1
    assert result["status"] == "partial"

    client = TestClient(app)
    stored = client.get("/api/weather/daily?region=Chennai").json()["data"][0]
    assert all(stored[metric] == (0 if zero else None) for metric in OPTIONAL_METRICS)
    catalog = services.list_tamil_nadu_city_weather()
    chennai = next(city for city in catalog if city["city"] == "Chennai")
    assert chennai["forecast_status"] == "current"
    assert chennai["forecast"]["rainfall_mm"] == (0 if zero else None)
    for path in ("/weather?region=Chennai", "/weather-market?region=Chennai"):
        page = client.get(path)
        assert page.status_code == 200
        assert f"{'0' if zero else '—'} mm" in page.text
        assert f"{'0' if zero else '—'} km/h" in page.text
        assert f"{'0' if zero else '—'} %" in page.text

    if imd:
        services.fetch_authorized_weather_updates()
        assert len(services.list_weather_forecast("daily", "Chennai")) == 1


@pytest.mark.parametrize("imd", [False, True])
def test_invalid_feed_is_reported_without_persisting_fake_weather(
    weather_database, monkeypatch, imd,
):
    record = (
        {"Station_Name": "Chennai", "Todays_Forecast_Max_Temp": "NaN"}
        if imd else {"city": "Chennai", "temperature_c": "NaN"}
    )
    install_feed(monkeypatch, [record], imd)
    result = services.fetch_authorized_weather_updates()
    assert result["status"] == "warning"
    assert result["errors"]
    assert result["sources"][0]["status"] == "warning"
    assert services.list_weather_forecast("daily", "Chennai") == []
    assert services.list_weather_fetch_history()[0]["error_count"] == 1


def test_legacy_schema_migration_preserves_rows_indexes_and_triggers(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "legacy.db"))
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE weather_forecasts (
                id TEXT PRIMARY KEY, region TEXT NOT NULL, period TEXT NOT NULL,
                forecast_date TEXT NOT NULL, temperature_c REAL NOT NULL,
                rainfall_mm REAL NOT NULL, humidity_pct REAL NOT NULL,
                wind_kmh REAL NOT NULL, summary_ta TEXT NOT NULL,
                advisory_ta TEXT NOT NULL, source_name TEXT NOT NULL,
                created_at TEXT NOT NULL, city_tier TEXT NOT NULL DEFAULT 'Tier 3',
                moisture_percent REAL NOT NULL DEFAULT 60
            )
        """)
        conn.execute(
            "INSERT INTO weather_forecasts VALUES "
            "('legacy', 'Chennai', 'daily', ?, 30, 0, 50, 0, 'Summary', 'Advisory', 'IMD', ?, 'Tier 1', 60)",
            (now, now),
        )
        conn.execute("CREATE INDEX weather_region_idx ON weather_forecasts(region)")
        conn.execute("CREATE TABLE weather_changes (forecast_id TEXT)")
        conn.execute("""
            CREATE TRIGGER weather_update AFTER UPDATE ON weather_forecasts
            BEGIN INSERT INTO weather_changes VALUES (NEW.id); END
        """)

    init_db()
    init_db()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM weather_forecasts").fetchone()
        assert row["id"] == "legacy"
        assert row["rainfall_mm"] == 0
        assert row["moisture_percent"] == 60
        assert conn.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        schema = {row["name"]: row for row in conn.execute("PRAGMA table_info(weather_forecasts)")}
        assert schema["temperature_c"]["notnull"] == 1
        assert all(schema[metric]["notnull"] == 0 for metric in OPTIONAL_METRICS)
        assert conn.execute(
            "SELECT name FROM sqlite_master WHERE name = 'weather_region_idx'"
        ).fetchone()
        conn.execute("UPDATE weather_forecasts SET rainfall_mm = NULL WHERE id = 'legacy'")
        assert conn.execute("SELECT forecast_id FROM weather_changes").fetchone()[0] == "legacy"
