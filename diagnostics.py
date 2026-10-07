from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from database import get_connection


def diagnose_crop_issue(
    crop_type: str,
    image_url: str,
    notes: str,
    *,
    created_by: Optional[str] = None,
    persist: bool = True,
) -> Dict[str, Any]:
    diagnosis = "Image review required"
    recommendation = (
        "This prototype does not analyze image pixels. Do not use this result to identify a disease "
        "or choose a chemical treatment. Share the image and symptoms with a qualified agricultural advisor."
    )
    confidence = "Low"
    guidance = {
        "treatment_steps": [
            "தற்போது நோயறிதல் உறுதி செய்யப்படவில்லை; இந்த முடிவின் அடிப்படையில் பூச்சிக்கொல்லி அல்லது பூஞ்சைக்கொல்லி பயன்படுத்த வேண்டாம்.",
            "பாதிக்கப்பட்ட செடியின் தெளிவான படத்தையும் அறிகுறிகள் தொடங்கிய நேரத்தையும் பதிவு செய்து, அருகிலுள்ள வேளாண்மை அலுவலரிடம் ஆலோசனை பெறுங்கள்.",
        ],
        "prevention_steps": [
            "வயலை தொடர்ந்து கவனித்து, பாதிப்பு பரவும் பகுதிகளை தேதி குறிப்புடன் பதிவு செய்யுங்கள்.",
            "தாவரங்களுக்கு நீர் மற்றும் ஊட்டச்சத்து தேவையை உள்ளூர் வேளாண்மை ஆலோசனையுடன் சரிபார்க்கவும்.",
        ],
    }
    result = {
        "crop_type": crop_type,
        "image_url": image_url,
        "diagnosis": diagnosis,
        "recommendation": recommendation,
        "notes": notes,
        "confidence": confidence,
        "assessment_method": "intake_only_no_image_inference",
        "image_analyzed": False,
        "manual_review_required": True,
        "treatment_steps": guidance["treatment_steps"],
        "prevention_steps": guidance["prevention_steps"],
    }
    if persist:
        save_diagnosis_record(result, created_by=created_by)
    return result


def save_diagnosis_record(record: Dict[str, Any], *, created_by: Optional[str] = None) -> None:
    created_at = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO diagnosis_records (
                id, crop_type, image_url, diagnosis, recommendation, notes, confidence, created_at, created_by
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
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
                created_by,
            ),
        )


def list_diagnosis_history(
    limit: int = 20,
    *,
    username: Optional[str] = None,
    include_all: bool = False,
) -> List[Dict[str, str]]:
    if not username and not include_all:
        return []
    where_clause = "" if include_all else "WHERE created_by = ?"
    params: tuple[Any, ...] = (max(1, min(limit, 100)),) if include_all else (username, max(1, min(limit, 100)))
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT crop_type, image_url, diagnosis, recommendation, notes, confidence, created_at
            FROM diagnosis_records
            {where_clause}
            ORDER BY created_at DESC
            LIMIT ?
            """,
            params,
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
