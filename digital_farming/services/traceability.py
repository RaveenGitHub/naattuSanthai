from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from database import get_connection


REQUIRED_LOT_EVENTS = {
    "harvested",
    "graded",
    "collected",
    "transported",
    "buyer_handoff",
}


def register_traceability_lot(
    lot_id: str,
    crop: str,
    farmer: str,
    origin: str,
    quality_grade: str,
    created_by: str,
) -> Dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO traceability_lots
                (lot_id, crop, farmer, origin, quality_grade, created_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (lot_id, crop, farmer, origin, quality_grade, created_by, created_at),
        )
        conn.execute(
            """
            INSERT INTO traceability_events
                (id, lot_id, event_type, location, notes, recorded_by, created_at)
            VALUES (?, ?, 'registered', ?, '', ?, ?)
            """,
            (str(uuid4()), lot_id, origin, created_by, created_at),
        )
    return get_traceability_lot(lot_id)


def record_traceability_event(
    lot_id: str,
    event_type: str,
    location: str,
    notes: str,
    recorded_by: str,
) -> Dict[str, Any]:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        lot = conn.execute(
            "SELECT 1 FROM traceability_lots WHERE lot_id = ?", (lot_id,)
        ).fetchone()
        if lot is None:
            raise LookupError("Traceability lot not found")
        conn.execute(
            """
            INSERT INTO traceability_events
                (id, lot_id, event_type, location, notes, recorded_by, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (str(uuid4()), lot_id, event_type, location, notes, recorded_by, created_at),
        )
    return get_traceability_lot(lot_id)


def get_traceability_lot(lot_id: str) -> Dict[str, Any]:
    with get_connection() as conn:
        lot = conn.execute(
            "SELECT * FROM traceability_lots WHERE lot_id = ?", (lot_id,)
        ).fetchone()
        if lot is None:
            raise LookupError("Traceability lot not found")
        rows = conn.execute(
            """
            SELECT id, event_type, location, notes, recorded_by, created_at
            FROM traceability_events
            WHERE lot_id = ?
            ORDER BY created_at, id
            """,
            (lot_id,),
        ).fetchall()

    events = [dict(row) for row in rows]
    observed = {event["event_type"] for event in events}
    complete = REQUIRED_LOT_EVENTS.issubset(observed)
    return {
        "lot_id": lot["lot_id"],
        "crop": lot["crop"],
        "farmer": lot["farmer"],
        "origin": lot["origin"],
        "quality_grade": lot["quality_grade"],
        "quality_grade_status": "self_reported",
        "created_by": lot["created_by"],
        "created_at": lot["created_at"],
        "events": events,
        "evidence_status": "complete_unverified" if complete else "incomplete",
        "independently_verified": False,
        "missing_event_types": sorted(REQUIRED_LOT_EVENTS - observed),
    }


def build_traceability_summary(
    farmer: str, batch: str, location: str, quality_grade: str,
) -> Dict[str, Any]:
    return {
        "farmer": farmer,
        "batch": batch,
        "location": location,
        "quality_grade": (quality_grade or "B").upper(),
        "traceability_status": "unverified_claim",
        "procurement_steps": [
            "No lot evidence is stored for these submitted details."
        ],
        "chain_of_custody": [
            "Farmer, batch, location, and grade are submitted claims only; no independent verification was performed."
        ],
        "lot_lifecycle": [],
    }
