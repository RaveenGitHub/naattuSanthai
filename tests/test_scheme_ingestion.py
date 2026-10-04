import json
import sys
from unittest.mock import Mock

import httpx
import pytest
from fastapi.testclient import TestClient

from app import app
from database import get_connection, init_db
from digital_farming import scheme_ingestion as ingestion
from digital_farming import scheme_refresh


@pytest.fixture
def scheme_database(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "schemes.db"))
    for _, setting, _ in ingestion.SOURCES:
        monkeypatch.delenv(setting, raising=False)
    init_db()
    monkeypatch.setattr(ingestion.time, "sleep", Mock())


def feed_transport(monkeypatch, handler):
    original = httpx.Client
    monkeypatch.setattr(ingestion.httpx, "Client", lambda **kwargs: original(
        **kwargs, transport=httpx.MockTransport(handler),
    ))


def test_unconfigured_run_is_persistent_and_does_not_seed_publication(scheme_database):
    result = ingestion.ingest_scheme_sources()
    assert result["status"] == "not_configured"
    assert all(item["attempts"] == 0 for item in result["sources"])
    status = ingestion.ingestion_status()
    assert status["history"][0]["id"] == result["id"]
    assert status["publication"] == "disabled_pending_validation"
    with get_connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM government_scheme_updates").fetchone()[0] == 0


def test_raw_payload_and_provenance_are_preserved_and_deduplicated(scheme_database, monkeypatch):
    url = "https://pmkisan.gov.in/authorized-json"
    monkeypatch.setenv("PM_KISAN_SCHEME_FEED_URL", url)
    raw = {"id": "notice-1", "title": "English scheme notice", "unknown_field": {"amount": 100}}
    feed_transport(monkeypatch, lambda request: httpx.Response(200, json={"data": [raw]}))
    first = ingestion.ingest_scheme_sources()
    second = ingestion.ingest_scheme_sources()
    assert first["status"] == second["status"] == "success"
    assert first["sources"][0]["inserted"] == 1
    assert second["sources"][0]["inserted"] == 0
    records = ingestion.list_raw_scheme_records("pm-kisan")
    assert len(records) == 1
    assert records[0]["payload"] == raw
    assert records[0]["source_url"] == url
    assert records[0]["first_received_at"] <= records[0]["last_received_at"]
    assert ingestion.list_raw_scheme_records("unknown") == []
    with get_connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM government_scheme_updates").fetchone()[0] == 0


@pytest.mark.parametrize("url", [
    "http://pmkisan.gov.in/feed", "https://example.com/feed",
    "https://user:secret@pmkisan.gov.in/feed", "https://pmkisan.gov.in/feed?token=secret",
    "https://pmkisan.gov.in:444/feed", "https://[broken",
])
def test_invalid_configuration_is_not_fetched_or_disclosed(scheme_database, monkeypatch, url, caplog):
    monkeypatch.setenv("PM_KISAN_SCHEME_FEED_URL", url)
    feed_transport(monkeypatch, lambda request: pytest.fail("Invalid URL must not be requested"))
    result = ingestion.ingest_scheme_sources()
    assert result["status"] == "failed"
    assert result["sources"][0]["error_code"] == "invalid"
    assert url not in json.dumps(result)
    assert url not in caplog.text


def test_retry_recovers_transient_failure(scheme_database, monkeypatch):
    monkeypatch.setenv("PM_KISAN_SCHEME_FEED_URL", "https://pmkisan.gov.in/feed")
    attempts = []

    def handler(request):
        attempts.append(request)
        return httpx.Response(503 if len(attempts) == 1 else 200, json=[{"title": "Notice"}])

    feed_transport(monkeypatch, handler)
    result = ingestion.ingest_scheme_sources()
    assert result["status"] == "success"
    assert result["sources"][0]["attempts"] == 2
    assert result["sources"][0]["error_code"] is None


@pytest.mark.parametrize("status,attempts", [(429, 3), (503, 3), (401, 1), (302, 1)])
def test_http_failures_are_bounded_and_redirects_not_followed(scheme_database, monkeypatch, status, attempts):
    monkeypatch.setenv("PM_KISAN_SCHEME_FEED_URL", "https://pmkisan.gov.in/feed")
    feed_transport(monkeypatch, lambda request: httpx.Response(status, headers={"Location": "https://example.com"}))
    result = ingestion.ingest_scheme_sources()
    assert result["status"] == "failed"
    assert result["sources"][0]["attempts"] == attempts
    assert result["sources"][0]["error_code"] == f"http_{status}"


@pytest.mark.parametrize("body", [
    b"<html>Portal</html>", b"[]", b'{"data":{}}', b"[null]",
    b'[{"value":NaN}]', b'[{}]', b"x" * (ingestion.MAX_RESPONSE_BYTES + 1),
    b'[{"value":1e999}]',
], ids=["html", "empty", "bad-envelope", "null-record", "nan", "empty-record", "oversized", "overflow"])
def test_invalid_payload_is_not_stored_or_retried(scheme_database, monkeypatch, body):
    monkeypatch.setenv("PM_KISAN_SCHEME_FEED_URL", "https://pmkisan.gov.in/feed")
    feed_transport(monkeypatch, lambda request: httpx.Response(200, content=body))
    result = ingestion.ingest_scheme_sources()
    assert result["status"] == "failed"
    assert result["sources"][0]["attempts"] == 1
    assert ingestion.list_raw_scheme_records() == []


def test_partial_sources_do_not_claim_complete_refresh(scheme_database, monkeypatch):
    monkeypatch.setenv("PM_KISAN_SCHEME_FEED_URL", "https://pmkisan.gov.in/feed")
    monkeypatch.setenv("TN_AGRI_SCHEME_FEED_URL", "https://agri.tn.gov.in/feed")
    feed_transport(monkeypatch, lambda request: httpx.Response(
        200 if request.url.host == "pmkisan.gov.in" else 403, json=[{"title": "Notice"}],
    ))
    assert ingestion.ingest_scheme_sources()["status"] == "partial"


def test_admin_api_access_limits_and_raw_records(scheme_database, monkeypatch):
    client = TestClient(app)
    for path in ("/api/schemes/ingestion/status", "/api/schemes/ingestion/raw"):
        assert client.get(path).status_code == 403
        assert client.get(path, headers={"X-User-Role": "operator"}).status_code == 403
        assert client.get(path + "?limit=101", headers={"X-User-Role": "admin"}).status_code == 422
    assert client.post("/api/schemes/ingestion/run").status_code == 403
    headers = {"X-User-Role": "admin"}
    response = client.post("/api/schemes/ingestion/run", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is False
    assert response.json()["error"] == "not_configured"
    assert client.get("/api/schemes/ingestion/status", headers=headers).json()["data"]["status"] == "not_configured"


def test_worker_check_has_no_run_history(scheme_database, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["scheme_refresh", "--check"])
    monkeypatch.setattr(scheme_refresh, "load_dotenv", Mock())
    assert scheme_refresh.main() == 1
    monkeypatch.setenv("PM_KISAN_SCHEME_FEED_URL", "https://pmkisan.gov.in/feed")
    assert scheme_refresh.main() == 0
    assert ingestion.ingestion_status()["history"] == []


@pytest.mark.parametrize("status,exit_code", [
    ("success", 0), ("partial", 1), ("not_configured", 1), ("failed", 1),
])
def test_worker_exit_code(scheme_database, monkeypatch, tmp_path, status, exit_code):
    monkeypatch.setattr(sys, "argv", ["scheme_refresh"])
    monkeypatch.setattr(scheme_refresh, "load_dotenv", Mock())
    monkeypatch.setattr(scheme_refresh, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(scheme_refresh.logging, "basicConfig", Mock())
    monkeypatch.setattr(scheme_refresh, "RotatingFileHandler", Mock())
    monkeypatch.setattr(ingestion, "ingest_scheme_sources", lambda: {"status": status})
    assert scheme_refresh.main() == exit_code
