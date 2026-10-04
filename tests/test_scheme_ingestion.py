import json
import sys
from unittest.mock import Mock
from uuid import uuid4

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


def persist_raw_record(payload, source_id="pm-kisan"):
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True)
    digest = ingestion.hashlib.sha256(raw.encode("utf-8")).hexdigest()
    now = "2026-10-04T08:00:00+00:00"
    raw_id = f"SCHEME-RAW-REVIEW-{uuid4().hex}"
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO scheme_raw_records VALUES (?, ?, ?, ?, ?, ?, ?)",
            (raw_id, source_id, "https://pmkisan.gov.in/feed", digest, raw, now, now),
        )
    return raw_id


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


def test_normalize_requires_editorial_tamil_and_is_idempotent(scheme_database):
    raw_id = persist_raw_record({"title": "PM Kisan support", "description": "English description"})
    draft = ingestion.normalize_raw_scheme_record(raw_id)
    assert draft["status"] == "pending_translation"
    assert draft["title_en"] == "PM Kisan support"
    assert draft["title_ta"] is None
    assert {"title", "summary", "eligibility", "benefits", "steps", "category", "scheme_type"} <= set(draft["validation_issues"])
    assert ingestion.normalize_raw_scheme_record(raw_id)["id"] == draft["id"]
    assert ingestion.list_scheme_review_drafts()[0]["raw_record_id"] == raw_id


def complete_draft_fields():
    return {
        "title_ta": "பிரதமர் விவசாயி நிதி உதவி",
        "summary_ta": "தகுதியான விவசாயிகளுக்கு நேரடி நிதி உதவி வழங்கப்படுகிறது.",
        "eligibility_ta": "தகுதியுள்ள விவசாயிகள் பதிவு செய்யலாம்.",
        "benefits_ta": "நேரடி நிதி உதவி கிடைக்கும்.",
        "apply_steps_ta": "அதிகாரப்பூர்வ இணையதளத்தில் பதிவு செய்யவும்.",
        "category": "subsidy",
        "scheme_type": "central",
    }


def test_admin_review_publishes_valid_tamil_with_raw_provenance_atomically(scheme_database):
    raw_id = persist_raw_record({"title": "PM Kisan support"})
    draft = ingestion.normalize_raw_scheme_record(raw_id)
    client = TestClient(app)
    headers = {"X-User-Role": "admin"}
    path = f"/api/schemes/ingestion/review/{draft['id']}"
    updated = client.patch(path, json=complete_draft_fields(), headers=headers)
    assert updated.status_code == 200
    assert updated.json()["data"]["status"] == "pending_review"
    resolved = client.post(path + "/resolve", json={
        "decision": "approve", "reason": "Tamil copy checked against official notice",
    }, headers=headers)
    assert resolved.status_code == 200
    published = resolved.json()["data"]
    assert published["status"] == "published"
    assert published["published_scheme_id"]
    with get_connection() as conn:
        row = conn.execute(
            "SELECT title_ta,source_record_id,source_content_hash FROM government_scheme_updates WHERE id=?",
            (published["published_scheme_id"],),
        ).fetchone()
        action = conn.execute(
            "SELECT decision,reviewer,reason FROM scheme_review_actions WHERE scheme_id=?",
            (draft["id"],),
        ).fetchone()
        audit = conn.execute(
            "SELECT username,action,outcome FROM audit_logs WHERE resource='scheme_normalized_records' ORDER BY created_at DESC LIMIT 1",
        ).fetchone()
    assert row["title_ta"] == complete_draft_fields()["title_ta"]
    assert row["source_record_id"] == raw_id
    assert row["source_content_hash"]
    assert tuple(action) == ("approve", "admin", "Tamil copy checked against official notice")
    assert tuple(audit) == ("admin", "scheme_ingestion_review", "success")
    assert client.post(path + "/resolve", json={
        "decision": "approve", "reason": "second approval",
    }, headers=headers).status_code == 422


def test_invalid_draft_cannot_be_approved_or_published(scheme_database):
    raw_id = persist_raw_record({"title": "English only"})
    draft = ingestion.normalize_raw_scheme_record(raw_id)
    client = TestClient(app)
    response = client.post(
        f"/api/schemes/ingestion/review/{draft['id']}/resolve",
        json={"decision": "approve", "reason": "attempt"},
        headers={"X-User-Role": "admin"},
    )
    assert response.status_code == 422
    with get_connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM government_scheme_updates").fetchone()[0] == 0
        assert conn.execute("SELECT COUNT(*) FROM scheme_review_actions").fetchone()[0] == 0


def test_reject_is_audited_and_never_publishes(scheme_database):
    raw_id = persist_raw_record({"title": "English only"})
    draft = ingestion.normalize_raw_scheme_record(raw_id)
    result = ingestion.resolve_scheme_review_draft(draft["id"], "reject", "reviewer", "Cannot verify source")
    assert result["status"] == "rejected"
    with get_connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM government_scheme_updates").fetchone()[0] == 0
        assert conn.execute(
            "SELECT COUNT(*) FROM audit_logs WHERE resource='scheme_normalized_records'",
        ).fetchone()[0] == 1


def test_review_api_is_admin_only_and_validates_payload(scheme_database):
    raw_id = persist_raw_record({"title": "English only"})
    draft = ingestion.normalize_raw_scheme_record(raw_id)
    client = TestClient(app)
    path = f"/api/schemes/ingestion/review/{draft['id']}"
    assert client.get("/api/schemes/ingestion/review").status_code == 403
    assert client.get("/api/schemes/ingestion/review", headers={"X-User-Role": "operator"}).status_code == 403
    assert client.get("/api/schemes/ingestion/review?status=bad", headers={"X-User-Role": "admin"}).status_code == 422
    assert client.patch(path, json={"unknown": "field"}, headers={"X-User-Role": "admin"}).status_code == 422
    assert client.patch(path, json={}, headers={"X-User-Role": "admin"}).status_code == 422
    assert client.post(path + "/resolve", json={"decision": "approve", "reason": "x" * 1001}, headers={"X-User-Role": "admin"}).status_code == 422


def test_published_source_record_cannot_be_published_twice(scheme_database):
    raw_id = persist_raw_record({"title": "PM Kisan support"})
    draft = ingestion.normalize_raw_scheme_record(raw_id)
    ingestion.update_scheme_review_draft(draft["id"], complete_draft_fields())
    ingestion.resolve_scheme_review_draft(draft["id"], "approve", "admin", "verified")
    duplicate_raw_id = persist_raw_record(
        {"title": "PM Kisan support", "updated_notice": True},
        source_id="pm-kisan",
    )
    duplicate = ingestion.normalize_raw_scheme_record(duplicate_raw_id)
    ingestion.update_scheme_review_draft(duplicate["id"], complete_draft_fields())
    with pytest.raises(ValueError, match="already exists"):
        ingestion.resolve_scheme_review_draft(duplicate["id"], "approve", "admin", "verified")
    with get_connection() as conn:
        assert conn.execute("SELECT COUNT(*) FROM government_scheme_updates").fetchone()[0] == 1


def test_admin_html_review_edits_and_approves_using_session_cookie(scheme_database):
    raw_id = persist_raw_record({
        "title": "PM Kisan support", "description": "Support for registered farmers.",
        "source_markup": "<script>alert(1)</script>",
    })
    draft = ingestion.normalize_raw_scheme_record(raw_id)
    client = TestClient(app)
    login = client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    assert login.status_code == 200
    page = client.get("/admin/scheme-ingestion-review")
    assert page.status_code == 200
    assert "Source text is not automatically translated" in page.text
    assert "pending_translation" in page.text
    assert "raw_record_id" not in page.text
    assert raw_id in page.text
    assert "Raw official feed record" in page.text
    assert "Support for registered farmers." in page.text
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page.text
    assert "<script>alert(1)</script>" not in page.text
    save = client.post(
        f"/admin/scheme-ingestion-review/{draft['id']}/save",
        data=complete_draft_fields(),
        follow_redirects=False,
    )
    assert save.status_code == 303
    assert save.headers["location"].endswith("?notice=saved")
    publish = client.post(
        f"/admin/scheme-ingestion-review/{draft['id']}/resolve",
        data={"decision": "approve", "reason": "Reviewed against source notice"},
        follow_redirects=False,
    )
    assert publish.status_code == 303
    assert publish.headers["location"].endswith("?notice=published")
    assert "title_ta" in client.get("/api/scheme/" + ingestion.list_scheme_review_drafts("published")[0]["published_scheme_id"]).json()["data"]


def test_non_admin_cannot_open_or_post_review_ui(scheme_database):
    client = TestClient(app)
    assert client.get("/admin/scheme-ingestion-review", follow_redirects=False).status_code == 302
    login = client.post("/auth/login", json={"username": "farmer1", "password": "farmer123"})
    assert login.status_code == 200
    page = client.get("/admin/scheme-ingestion-review", follow_redirects=False)
    assert page.status_code == 302
    assert page.headers["location"] == "/dashboard"
    denied = client.post(
        "/admin/scheme-ingestion-review/not-a-draft/save",
        data=complete_draft_fields(),
        follow_redirects=False,
    )
    assert denied.status_code == 302
