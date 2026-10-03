from unittest.mock import Mock

import services
from digital_farming import weather_refresh


def test_weather_refresh_exits_successfully_only_with_full_city_coverage(monkeypatch):
    monkeypatch.setattr(weather_refresh, "configure_logging", Mock(return_value=Mock()))
    monkeypatch.setattr(
        services,
        "fetch_authorized_weather_updates",
        lambda timeout_seconds: {
            "status": "success",
            "records": [{} for _ in range(35)],
            "sources": [],
            "errors": [],
            "city_coverage": {"received": 35, "total": 35, "missing": []},
        },
    )

    assert weather_refresh.main() == 0


def test_weather_refresh_reports_partial_or_missing_data_as_failure(monkeypatch):
    monkeypatch.setattr(weather_refresh, "configure_logging", Mock(return_value=Mock()))
    monkeypatch.setattr(
        services,
        "fetch_authorized_weather_updates",
        lambda timeout_seconds: {
            "status": "partial",
            "records": [{}],
            "sources": [],
            "errors": [],
            "city_coverage": {"received": 1, "total": 35, "missing": ["Chennai"]},
        },
    )

    assert weather_refresh.main() == 1


def test_weather_refresh_reports_unconfigured_source_as_failure(monkeypatch):
    monkeypatch.setattr(weather_refresh, "configure_logging", Mock(return_value=Mock()))
    monkeypatch.setattr(
        services,
        "fetch_authorized_weather_updates",
        lambda timeout_seconds: {
            "status": "not_configured",
            "records": [],
            "sources": [],
            "errors": ["Set IMD_API_KEY and IMD_API_TOKEN."],
        },
    )

    assert weather_refresh.main() == 1
