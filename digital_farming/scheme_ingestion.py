from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from datetime import datetime, timezone
from typing import Optional
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


def _reject_nonfinite_json(value: str) -> None:
    raise FeedContractError("nonfinite_json")


def source_configuration() -> list[dict]:
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


def _read_feed(client: httpx.Client, url: str) -> list[dict]:
    with client.stream("GET", url, headers={"Accept": "application/json"}) as response:
        response.raise_for_status()
        content = bytearray()
        for chunk in response.iter_bytes():
            content.extend(chunk)
            if len(content) > MAX_RESPONSE_BYTES:
                raise FeedContractError("response_too_large")
    try:
        payload = json.loads(content, parse_constant=_reject_nonfinite_json)
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


def list_raw_scheme_records(source_id: Optional[str] = None, limit: int = 20) -> list[dict]:
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
