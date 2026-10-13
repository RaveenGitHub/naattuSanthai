from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any, Dict
from uuid import uuid4

from database import get_connection


def submit_pilot_feedback(payload: Dict[str, Any], submitted_by: str) -> Dict[str, Any]:
    feedback_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO pilot_feedback (
                id, district, village, farmer_group, scheme_under_test,
                clarity_score, usefulness_score, issues, recommended_change,
                feedback_notes, submitted_by, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                feedback_id,
                payload.get("district", ""),
                payload.get("village", ""),
                payload.get("farmer_group", ""),
                payload.get("scheme_under_test", ""),
                payload.get("clarity_score"),
                payload.get("usefulness_score"),
                json.dumps(payload.get("issues", []), ensure_ascii=False),
                payload.get("recommended_change", ""),
                payload.get("feedback_notes", ""),
                submitted_by,
                created_at,
            ),
        )
    return {"id": feedback_id, "created_at": created_at, "status": "recorded"}


def get_pilot_feedback_summary() -> Dict[str, Any]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS total, MAX(created_at) AS latest_at FROM pilot_feedback"
        ).fetchone()
    return {"total_submissions": row["total"], "latest_submission_at": row["latest_at"]}


def list_pilot_feedback(limit: int = 50) -> list[Dict[str, Any]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, district, village, farmer_group, scheme_under_test,
                   clarity_score, usefulness_score, issues, recommended_change,
                   feedback_notes, submitted_by, created_at
            FROM pilot_feedback
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    results = []
    for row in rows:
        item = dict(row)
        item["issues"] = json.loads(item["issues"])
        results.append(item)
    return results
