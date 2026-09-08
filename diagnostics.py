from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List
from uuid import uuid4

from database import get_connection


def _build_treatment_and_prevention(crop_name: str, diagnosis: str) -> Dict[str, List[str]]:
    crop_key = (crop_name or "").lower()
    treatment_steps: List[str] = []
    prevention_steps: List[str] = []

    if "rice" in crop_key or "paddy" in crop_key:
        treatment_steps = [
            "Apply a recommended fungicide spray at the first sign of lesions and rotate the spray schedule as needed.",
            "Reduce waterlogging for 48 hours and drain excess standing water from affected patches.",
            "Remove severely infected leaves to slow the spread to healthy tillers.",
        ]
        prevention_steps = [
            "Maintain field drainage and avoid late-evening water stagnation.",
            "Use balanced nitrogen and avoid excess canopy growth that raises humidity.",
            "Monitor nearby fields for early blast symptoms after high humidity periods.",
        ]
    elif "groundnut" in crop_key:
        treatment_steps = [
            "Apply a balanced fungicidal spray focused on the lower canopy where leaf spots first appear.",
            "Use a nitrogen-phosphorus-potassium plan that supports pod filling without overfeeding the foliage.",
            "Remove the most affected leaves and keep the field free from weeds that trap moisture.",
        ]
        prevention_steps = [
            "Avoid overhead irrigation during leaf wetness periods.",
            "Rotate with non-host crops in the next season to reduce fungal buildup.",
            "Inspect the field weekly for early lesions and patchy yellowing.",
        ]
    elif "tomato" in crop_key:
        treatment_steps = [
            "Apply a crop-safe fungicide or biological treatment on the affected leaves and stems.",
            "Trim and dispose of infected foliage to prevent spread to healthy fruit clusters.",
            "Review irrigation timing and reduce moisture on leaf surfaces.",
        ]
        prevention_steps = [
            "Improve spacing between plants to improve airflow.",
            "Use drip irrigation or controlled watering to keep leaves dry.",
            "Inspect weekly for powdery mildew or leaf curl before the disease spreads.",
        ]
    else:
        treatment_steps = [
            "Inspect the field closely and isolate the most affected plants before treatment.",
            "Follow a crop-safe spray or treatment plan recommended for the observed stress pattern.",
            "Review irrigation, nutrient balance, and canopy moisture before resuming the normal regimen.",
        ]
        prevention_steps = [
            "Keep field monitoring frequent during the next 7-10 days.",
            "Maintain balanced nutrient and irrigation schedules to reduce recurring stress.",
            "Consult an agronomist if symptoms continue or spread to more plants.",
        ]

    if "leaf blast" in (diagnosis or "").lower() or "fungal" in (diagnosis or "").lower():
        treatment_steps.insert(0, "Start field treatment immediately in the affected patches to keep the disease from spreading to neighboring rows.")
    if "general stress" in (diagnosis or "").lower():
        treatment_steps.insert(0, "Run a rapid field inspection and prioritize irrigation and nutrient checks before applying any chemical input.")

    return {"treatment_steps": treatment_steps, "prevention_steps": prevention_steps}


def diagnose_crop_issue(crop_type: str, image_url: str, notes: str) -> Dict[str, str]:
    crop_name = (crop_type or "").lower()
    note_text = (notes or "").lower()
    low_confidence = (
        "unknown" in crop_name
        or "unclear" in note_text
        or "no clear symptoms" in note_text
        or "uncertain" in note_text
        or "not clear" in note_text
        or len(note_text.strip()) < 8
    )

    if "rice" in crop_name:
        diagnosis = "Leaf blast / fungal infection"
        recommendation = "Apply recommended fungicide spray and avoid waterlogging for 48 hours."
        confidence = "Low" if low_confidence else "High"
    elif "groundnut" in crop_name:
        diagnosis = "Leaf spot disease"
        recommendation = "Use balanced nitrogen and inspect for fungal spread around the lower canopy."
        confidence = "Low" if low_confidence else "High"
    else:
        diagnosis = "General stress pattern detected"
        recommendation = (
            "Manual review recommended. Capture a clearer close-up image or consult an agronomist before treatment."
            if low_confidence
            else "Review irrigation and nutrient balance; schedule agronomist review if symptoms persist."
        )
        confidence = "Low" if low_confidence else "Medium"

    guidance = _build_treatment_and_prevention(crop_name, diagnosis)
    result = {
        "crop_type": crop_type,
        "image_url": image_url,
        "diagnosis": diagnosis,
        "recommendation": recommendation,
        "notes": notes,
        "confidence": confidence,
        "treatment_steps": guidance["treatment_steps"],
        "prevention_steps": guidance["prevention_steps"],
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
