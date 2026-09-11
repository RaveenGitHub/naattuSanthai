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
            "சிகிச்சை: பாதிக்கப்பட்ட வரிசைகளில் பூஞ்சைக் கொல்லியை உடனடியாகத் தெளிக்கவும்; உலர்ந்த அல்லது பாதிக்கப்பட்ட இலைகளை அகற்றவும்.",
            "நீர் தேங்குவதை 48 மணி நேரம் குறைக்கவும்; சாகுபடி பகுதிகளில் அதிகப்படியான நீரை வடிகட்டவும்.",
            "நெல் சாகுபடியில் மண் ஈரப்பதம் சீராக இருப்பதை உறுதிசெய்து, நோய் பரவலை குறைக்கவும்.",
        ]
        prevention_steps = [
            "தடுப்பு: வயலில் நீர் வடிகால் சீராக உள்ளதா என்பதை தொடர்ந்து சரிபார்க்கவும்.",
            "அதிக நைட்ரஜன் பயன்பாட்டைத் தவிர்த்து, மழை மற்றும் ஈரப்பதம் காரணமாக உச்சக்கட்ட வளர்ச்சி வராமல் பார்த்துக்கொள்ளவும்.",
            "அருகிலுள்ள வயல்களை வாராந்திரமாக கண்காணித்து, ஆரம்ப அறிகுறிகள் இருந்தால் உடனடியாக செயல்படுங்கள்.",
        ]
    elif "groundnut" in crop_key:
        treatment_steps = [
            "சிகிச்சை: கீழ் இலைகளில் உருவாகும் இலைப் புள்ளிகளை குறிவைத்து, சீரான பூஞ்சைக் கொல்லி தீர்வு பயன்படுத்தவும்.",
            "நைட்ரஜன்-பாஸ்பரஸ்-பொட்டாசியம் சமநிலையை சரிசெய்து, வேர்கள் மற்றும் காய் உருவாக்கத்திற்கு தேவையான உரத்தை வழங்கவும்.",
            "மிகவும் பாதிக்கப்பட்ட இலைகளை அகற்றி, ஈரப்பதத்தை தக்கவைக்கும் களைகளை நீக்கவும்.",
        ]
        prevention_steps = [
            "தடுப்பு: இலைகள் ஈரமாக இருக்கும் நேரங்களில் மேல் பாசனத்தை தவிர்க்கவும்.",
            "அடுத்த பருவத்தில் பூஞ்சை வளர்சிதை மாற்றத்தை குறைக்க, பருவமாற்ற பயிர்களை பயன்படுத்துங்கள்.",
            "வாரந்தோறும் வயலை ஆய்வு செய்து, முந்தைய அறிகுறிகள் மீண்டும் வருவதை எச்சரிக்கையுடன் கண்காணிக்கவும்.",
        ]
    elif "tomato" in crop_key:
        treatment_steps = [
            "சிகிச்சை: பாதிக்கப்பட்ட இலைகள் மற்றும் தண்டுகளில் பாதுகாப்பான பூஞ்சைக் கொல்லி அல்லது உயிரியல் சிகிச்சையை பயன்படுத்தவும்.",
            "மருத்துவமுறைக்கு முன்னர் பாதிக்கப்பட்ட இலைகளை வெட்டி, சுகாதாரமான இடத்தில் அழிக்கவும்.",
            "பாசன நேரத்தை சரிசெய்து, இலைகள் ஈரமாக இருப்பதை குறைக்கவும்.",
        ]
        prevention_steps = [
            "தடுப்பு: தாவரங்களுக்கு இடைவெளி அதிகரித்து, காற்றோட்டத்தை மேம்படுத்தவும்.",
            "மழைநீர் அல்லது மேல் பாசனத்தை குறைத்து, சொட்டுநீர் பாசனத்தை முன்னுரிமை செய்யுங்கள்.",
            "வாரந்தோறும் தக்காளி இலை சுருங்குதல் அல்லது தூள் பாக்டீரியா அறிகுறிகளை நோக்கி கண்காணிக்கவும்.",
        ]
    else:
        treatment_steps = [
            "சிகிச்சை: பாதிக்கப்பட்ட பயிர்களை தனிமைப்படுத்தி, வயலை நெருக்கமாக ஆய்வு செய்து பாசனமும் உரத்தையும் சரிசெய்யவும்.",
            "குறிப்பிட்ட நோய் அல்லது அழுத்தத்தின் அடிப்படையில் பாதுகாப்பான சிகிச்சை திட்டத்தை பின்பற்றுங்கள்.",
            "பாசனம், ஊட்டச்சத்து சமநிலை, மற்றும் இலை ஈரப்பதத்தை மறு ஆய்வு செய்து, வழக்கமான பராமரிப்பை தொடருங்கள்.",
        ]
        prevention_steps = [
            "தடுப்பு: அடுத்த 7-10 நாட்களில் வயலை அடிக்கடி கண்காணிக்கவும்.",
            "சமநிலையான ஊட்டச்சத்து மற்றும் நீர் மேலாண்மையை பராமரித்து, மீண்டும் அழுத்தம் வராமல் பாதுகாக்கவும்.",
            "அறிகுறிகள் தொடர்ந்தால் விவசாய நிபுணரை ஆலோசிக்கவும்.",
        ]

    if "leaf blast" in (diagnosis or "").lower() or "fungal" in (diagnosis or "").lower():
        treatment_steps.insert(0, "சிகிச்சை: பாதிக்கப்பட்ட பகுதிகளில் பூஞ்சை பரவாமல் தடுக்க உடனடியாக வயல் சிகிச்சையை தொடங்குங்கள்.")
    if "general stress" in (diagnosis or "").lower():
        treatment_steps.insert(0, "சிகிச்சை: உயிரியல்/இயற்கை ஆய்வு செய்து, பூச்சிக் கொல்லி பயன்படுத்துவதற்கு முன் நீர் மற்றும் ஊட்டச்சத்து நிலையை முதலில் சரிபார்க்கவும்.")

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
