from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import List, Optional
from urllib.parse import urlparse
from uuid import uuid4

import httpx

from database import get_connection, init_db

SOURCES = (
    ("pm-kisan", "PM_KISAN_SCHEME_FEED_URL", {"pmkisan.gov.in"}),
    ("tn-agri-dept", "TN_AGRI_SCHEME_FEED_URL", {"agri.tn.gov.in"}),
    ("tn-govt-portal", "TN_GOVT_SCHEME_FEED_URL", {"www.tn.gov.in", "tn.gov.in"}),
)
MAX_RESPONSE_BYTES = 2_000_000
MAX_RECORDS = 1000
LOGGER = logging.getLogger(__name__)


class FeedContractError(ValueError):
    pass


def _reject_nonfinite_json(_value: str) -> None:
    raise FeedContractError(f"nonfinite_json:{_value}")


def source_configuration() -> List[dict]:
    checks = []
    for source_id, setting, hosts in SOURCES:
        url = os.getenv(setting, "").strip()
        valid = False
        if url:
            try:
                parsed = urlparse(url)
                valid = (
                    parsed.scheme == "https" and parsed.hostname in hosts
                    and parsed.port in (None, 443)
                    and not parsed.username and not parsed.password
                    and not parsed.query and not parsed.fragment
                )
            except ValueError:
                valid = False
        checks.append({
            "source_id": source_id, "setting": setting,
            "status": "configured" if valid else "invalid" if url else "not_configured",
        })
    return checks


def _read_feed(client: httpx.Client, url: str) -> List[dict]:
    with client.stream("GET", url, headers={"Accept": "application/json"}) as response:
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_bytes():
            content.extend(chunk)
            if len(content) > MAX_RESPONSE_BYTES:
                raise FeedContractError("response_too_large")
    try:
        payload = json.loads(content, parse_constant=_reject_nonfinite_json)
    except FeedContractError:
        raise
    except (ValueError, UnicodeDecodeError) as exc:
        raise FeedContractError("invalid_json") from exc
    records = payload.get("data") if isinstance(payload, dict) else payload
    if not isinstance(records, list) or len(records) > MAX_RECORDS:
        raise FeedContractError("invalid_record_list")
    if not all(isinstance(record, dict) and record for record in records):
        raise FeedContractError("invalid_record")
    if not records:
        raise FeedContractError("empty_feed")
    try:
        json.dumps(records, allow_nan=False)
    except ValueError as exc:
        raise FeedContractError("nonfinite_json") from exc
    return records


def ingest_scheme_sources() -> dict:
    init_db()
    started_at = datetime.now(timezone.utc).isoformat()
    outcomes = []
    with httpx.Client(timeout=15, follow_redirects=False, trust_env=False) as client:
        for check in source_configuration():
            outcome = {**check, "attempts": 0, "received": 0, "inserted": 0, "error_code": None}
            if check["status"] != "configured":
                outcome["error_code"] = check["status"]
                outcomes.append(outcome)
                continue
            url = os.getenv(check["setting"], "").strip()
            records = []
            for attempt in range(1, 4):
                outcome["attempts"] = attempt
                retry = False
                try:
                    records = _read_feed(client, url)
                    break
                except httpx.HTTPStatusError as exc:
                    outcome["error_code"] = f"http_{exc.response.status_code}"
                    retry = exc.response.status_code == 429 or exc.response.status_code >= 500
                except httpx.RequestError:
                    outcome["error_code"] = "network_error"
                    retry = True
                except FeedContractError as exc:
                    outcome["error_code"] = str(exc)
                if not retry or attempt == 3:
                    break
                time.sleep(attempt)
            if records:
                now = datetime.now(timezone.utc).isoformat()
                with get_connection() as conn:
                    for record in records:
                        raw = json.dumps(record, ensure_ascii=False, sort_keys=True, allow_nan=False)
                        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
                        existing = conn.execute(
                            "SELECT id FROM scheme_raw_records WHERE source_id = ? AND content_hash = ?",
                            (check["source_id"], digest),
                        ).fetchone()
                        if existing:
                            conn.execute(
                                "UPDATE scheme_raw_records SET last_received_at = ?, source_url = ? WHERE id = ?",
                                (now, url, existing["id"]),
                            )
                        else:
                            conn.execute(
                                "INSERT INTO scheme_raw_records VALUES (?, ?, ?, ?, ?, ?, ?)",
                                (f"SCHEME-RAW-{uuid4().hex}", check["source_id"], url, digest, raw, now, now),
                            )
                            outcome["inserted"] += 1
                outcome.update(status="success", received=len(records), error_code=None)
            else:
                outcome["status"] = "failed"
            outcomes.append(outcome)
    active = [item for item in outcomes if item["status"] != "not_configured"]
    successful = sum(item["status"] == "success" for item in active)
    status = (
        "not_configured" if not active else
        "success" if successful == len(active) else
        "partial" if successful else "failed"
    )
    result = {
        "id": f"SCHEME-RUN-{uuid4().hex}", "status": status,
        "started_at": started_at, "finished_at": datetime.now(timezone.utc).isoformat(),
        "sources": outcomes,
    }
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO scheme_ingestion_runs VALUES (?, ?, ?, ?, ?)",
            (result["id"], status, started_at, result["finished_at"], json.dumps(outcomes)),
        )
    LOGGER.log(logging.INFO if status == "success" else logging.WARNING,
               "Scheme raw ingestion status=%s sources=%s", status, json.dumps(outcomes))
    return result


def ingestion_status(limit: int = 20) -> dict:
    if not 1 <= limit <= 100:
        raise ValueError("History limit must be between 1 and 100")
    with get_connection() as conn:
        runs = conn.execute(
            "SELECT * FROM scheme_ingestion_runs ORDER BY finished_at DESC, rowid DESC LIMIT ?", (limit,),
        ).fetchall()
        counts = conn.execute(
            "SELECT source_id, COUNT(*) AS count FROM scheme_raw_records GROUP BY source_id",
        ).fetchall()
    history = [{**dict(row), "sources": json.loads(row["sources"])} for row in runs]
    return {
        "configuration": source_configuration(), "history": history,
        "status": history[0]["status"] if history else "never_run",
        "raw_records_by_source": {row["source_id"]: row["count"] for row in counts},
        "publication": "disabled_pending_validation",
        "scheduler_registration": "not_checked",
    }


def list_raw_scheme_records(source_id: Optional[str] = None, limit: int = 20) -> List[dict]:
    if not 1 <= limit <= 100:
        raise ValueError("Raw record limit must be between 1 and 100")
    query = "SELECT * FROM scheme_raw_records"
    params: list = []
    if source_id:
        query += " WHERE source_id = ?"
        params.append(source_id)
    query += " ORDER BY last_received_at DESC, rowid DESC LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [{**dict(row), "payload": json.loads(row["payload"])} for row in rows]


SOURCE_METADATA = {
    "pm-kisan": ("PM-Kisan", "https://pmkisan.gov.in/"),
    "tn-agri-dept": ("Tamil Nadu Agriculture Department", "https://agri.tn.gov.in/"),
    "tn-govt-portal": ("Tamil Nadu Government Portal", "https://www.tn.gov.in/"),
}
NORMALIZED_FIELDS = (
    "title_ta", "summary_ta", "eligibility_ta", "benefits_ta",
    "apply_steps_ta", "category", "scheme_type",
)


def _text_field(payload: dict, *keys: str) -> Optional[str]:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def normalize_raw_scheme_record(raw_record_id: str) -> dict:
    from services import scheme_quality_issues

    with get_connection() as conn:
        raw = conn.execute(
            "SELECT * FROM scheme_raw_records WHERE id = ?", (raw_record_id,),
        ).fetchone()
        if raw is None:
            raise LookupError("Raw scheme record not found")
        existing = conn.execute(
            "SELECT * FROM scheme_normalized_records WHERE raw_record_id = ?",
            (raw_record_id,),
        ).fetchone()
        if existing:
            record = dict(existing)
            record["validation_issues"] = json.loads(record["validation_issues"])
            return record
        if raw["source_id"] not in SOURCE_METADATA:
            raise ValueError("Raw scheme source is not in the trusted source registry")
        source_name, source_url = SOURCE_METADATA[raw["source_id"]]
        payload = json.loads(raw["payload"])
        record = {
            "id": f"SCHEME-DRAFT-{uuid4().hex}",
            "raw_record_id": raw_record_id,
            "source_id": raw["source_id"],
            "source_name": source_name,
            "source_url": source_url,
            "title_en": _text_field(payload, "title_en", "title", "name", "scheme_name"),
            "summary_en": _text_field(payload, "summary_en", "summary", "description"),
            "title_ta": _text_field(payload, "title_ta", "name_ta"),
            "summary_ta": _text_field(payload, "summary_ta", "description_ta"),
            "eligibility_ta": _text_field(payload, "eligibility_ta"),
            "benefits_ta": _text_field(payload, "benefits_ta", "benefits"),
            "apply_steps_ta": _text_field(payload, "apply_steps_ta", "application_steps_ta"),
            "category": _text_field(payload, "category"),
            "scheme_type": _text_field(payload, "scheme_type"),
            "published_scheme_id": None,
        }
        issues = scheme_quality_issues(record)
        if not record["category"]:
            issues.append("category")
        if not record["scheme_type"]:
            issues.append("scheme_type")
        record["validation_issues"] = issues
        record["status"] = "pending_translation" if issues else "pending_review"
        now = datetime.now(timezone.utc).isoformat()
        record["created_at"] = now
        record["updated_at"] = now
        conn.execute(
            """
            INSERT INTO scheme_normalized_records
                (id, raw_record_id, source_id, source_name, source_url, title_en, summary_en,
                 title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta, category,
                 scheme_type, status, validation_issues, created_at, updated_at, published_scheme_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                record["id"], raw_record_id, record["source_id"], source_name, source_url,
                record["title_en"], record["summary_en"], record["title_ta"],
                record["summary_ta"], record["eligibility_ta"], record["benefits_ta"],
                record["apply_steps_ta"], record["category"], record["scheme_type"],
                record["status"], json.dumps(issues, ensure_ascii=False), now, now, None,
            ),
        )
    return record


def _draft_dict(row) -> dict:
    record = dict(row)
    record["validation_issues"] = json.loads(record["validation_issues"])
    if "source_payload" in record:
        record["source_payload"] = json.loads(record["source_payload"])
    return record


def list_scheme_review_drafts(status: Optional[str] = None, limit: int = 50) -> List[dict]:
    if not 1 <= limit <= 100:
        raise ValueError("Review limit must be between 1 and 100")
    query = (
        "SELECT scheme_normalized_records.*, scheme_raw_records.payload AS source_payload "
        "FROM scheme_normalized_records JOIN scheme_raw_records "
        "ON scheme_raw_records.id = scheme_normalized_records.raw_record_id"
    )
    params = []
    if status:
        query += " WHERE scheme_normalized_records.status = ?"
        params.append(status)
    query += " ORDER BY scheme_normalized_records.updated_at DESC, scheme_normalized_records.rowid DESC LIMIT ?"
    params.append(limit)
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_draft_dict(row) for row in rows]


def update_scheme_review_draft(draft_id: str, changes: dict) -> dict:
    from services import scheme_quality_issues

    allowed = set(NORMALIZED_FIELDS) | {"title_en", "summary_en"}
    if not changes or set(changes) - allowed:
        raise ValueError("Provide at least one supported draft field")
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM scheme_normalized_records WHERE id = ?", (draft_id,),
        ).fetchone()
        if row is None:
            raise LookupError("Scheme draft not found")
        if row["status"] in {"published", "rejected"}:
            raise ValueError("Resolved scheme drafts cannot be edited")
        values = _draft_dict(row)
        for field, value in changes.items():
            if value is not None and (not isinstance(value, str) or len(value) > 10000):
                raise ValueError(f"{field} must be text up to 10000 characters")
            values[field] = value.strip() if isinstance(value, str) else value
        issues = scheme_quality_issues(values)
        if not values.get("category"):
            issues.append("category")
        if not values.get("scheme_type"):
            issues.append("scheme_type")
        status = "pending_translation" if issues else "pending_review"
        updated_at = datetime.now(timezone.utc).isoformat()
        conn.execute(
            """
            UPDATE scheme_normalized_records SET title_en=?, summary_en=?, title_ta=?, summary_ta=?,
                eligibility_ta=?, benefits_ta=?, apply_steps_ta=?, category=?, scheme_type=?,
                status=?, validation_issues=?, updated_at=? WHERE id=?
            """,
            (
                values.get("title_en"), values.get("summary_en"), values.get("title_ta"),
                values.get("summary_ta"), values.get("eligibility_ta"), values.get("benefits_ta"),
                values.get("apply_steps_ta"), values.get("category"), values.get("scheme_type"),
                status, json.dumps(issues, ensure_ascii=False), updated_at, draft_id,
            ),
        )
        result = conn.execute(
            "SELECT * FROM scheme_normalized_records WHERE id = ?", (draft_id,),
        ).fetchone()
    return _draft_dict(result)


def resolve_scheme_review_draft(draft_id: str, decision: str, reviewer: str, reason: str) -> dict:
    from services import scheme_quality_issues

    if decision not in {"approve", "reject"}:
        raise ValueError("Decision must be approve or reject")
    if not reviewer.strip() or not reason.strip():
        raise ValueError("Reviewer and reason are required")
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute("BEGIN IMMEDIATE")
        row = conn.execute(
            "SELECT * FROM scheme_normalized_records WHERE id = ?", (draft_id,),
        ).fetchone()
        if row is None:
            raise LookupError("Scheme draft not found")
        if row["status"] not in {"pending_review", "pending_translation"}:
            raise ValueError("Scheme draft has already been resolved")
        draft = _draft_dict(row)
        if decision == "approve":
            issues = scheme_quality_issues(draft)
            if not draft.get("category"):
                issues.append("category")
            if not draft.get("scheme_type"):
                issues.append("scheme_type")
            if issues:
                conn.execute(
                    "UPDATE scheme_normalized_records SET status='pending_translation', validation_issues=?, updated_at=? WHERE id=?",
                    (json.dumps(issues, ensure_ascii=False), now, draft_id),
                )
                raise ValueError("Draft is not publishable: " + ", ".join(issues))
            duplicate = conn.execute(
                "SELECT id FROM government_scheme_updates "
                "WHERE source_record_id = ? OR (source_name = ? AND LOWER(title_ta) = LOWER(?) AND is_archived = 0) "
                "LIMIT 1",
                (draft["raw_record_id"], draft["source_name"], draft["title_ta"]),
            ).fetchone()
            if duplicate:
                raise ValueError("A published scheme already exists for this source record or title")
            raw = conn.execute(
                "SELECT content_hash FROM scheme_raw_records WHERE id = ?",
                (draft["raw_record_id"],),
            ).fetchone()
            if raw is None:
                raise ValueError("Linked raw source record is missing")
            published_id = f"SCHEME-{uuid4().hex}"
            conn.execute(
                """
                INSERT INTO government_scheme_updates
                    (id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                     category, scheme_type, source_name, source_url, is_archived, created_at,
                     source_record_id, source_content_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?)
                """,
                (
                    published_id, draft["title_ta"], draft["summary_ta"], draft["eligibility_ta"],
                    draft["benefits_ta"], draft["apply_steps_ta"], draft["category"],
                    draft["scheme_type"], draft["source_name"], draft["source_url"], now,
                    draft["raw_record_id"], raw["content_hash"],
                ),
            )
            status = "published"
        else:
            published_id = None
            status = "rejected"
        conn.execute(
            "UPDATE scheme_normalized_records SET status=?, published_scheme_id=?, updated_at=? WHERE id=?",
            (status, published_id, now, draft_id),
        )
        conn.execute(
            "INSERT INTO scheme_review_actions (id, scheme_id, decision, reviewer, reason, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (f"REVIEW-{uuid4().hex}", draft_id, decision, reviewer.strip(), reason.strip(), now),
        )
        conn.execute(
            "INSERT INTO audit_logs (id, username, action, resource, outcome, details, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (
                f"AUD-{uuid4().hex}", reviewer.strip(), "scheme_ingestion_review",
                "scheme_normalized_records", "success",
                f"Draft {draft_id} {status}: {reason.strip()}", now,
            ),
        )
        result = conn.execute(
            "SELECT * FROM scheme_normalized_records WHERE id = ?", (draft_id,),
        ).fetchone()
    return _draft_dict(result)
