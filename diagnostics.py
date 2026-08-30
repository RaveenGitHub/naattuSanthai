from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from database import get_connection


def diagnose_crop_issue(crop_type: str, image_url: str, notes: str) -> Dict[str, str]:
    crop_name = crop_type.lower()
    if "rice" in crop_name:
        diagnosis = "Leaf blast / fungal infection"
        recommendation = "Apply recommended fungicide spray and avoid waterlogging for 48 hours."
    elif "groundnut" in crop_name:
        diagnosis = "Leaf spot disease"
        recommendation = "Use balanced nitrogen and inspect for fungal spread around the lower canopy."
    else:
        diagnosis = "General stress pattern detected"
        recommendation = "Review irrigation and nutrient balance; schedule agronomist review if symptoms persist."

    result = {
        "crop_type": crop_type,
        "image_url": image_url,
        "diagnosis": diagnosis,
        "recommendation": recommendation,
        "notes": notes,
        "confidence": "High",
    }
    save_diagnosis_record(result)
    return result


def save_diagnosis_record(record: Dict[str, Any]) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO diagnosis_records (
                id, crop_type, image_url, diagnosis, recommendation, notes, confidence, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"DIAG-{uuid4().hex}",
                record["crop_type"],
                record["image_url"],
                record["diagnosis"],
                record["recommendation"],
                record.get("notes", ""),
                record["confidence"],
                created_at,
            ),
        )


def list_diagnosis_history(limit: int = 20) -> List[Dict[str, str]]:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT crop_type, image_url, diagnosis, recommendation, notes, confidence, created_at
            FROM diagnosis_records
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()

    return [
        {
            "crop_type": row["crop_type"],
            "image_url": row["image_url"],
            "diagnosis": row["diagnosis"],
            "recommendation": row["recommendation"],
            "notes": row["notes"],
            "confidence": row["confidence"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]
