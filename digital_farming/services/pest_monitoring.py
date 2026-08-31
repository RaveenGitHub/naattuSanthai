from __future__ import annotations

from typing import Any, Dict


def evaluate_pest_risk(crop: str, field_condition: str, severity: str = "low") -> Dict[str, Any]:
    crop_name = (crop or "crop").strip().lower()
    condition = (field_condition or "normal").strip().lower()
    severity_value = (severity or "low").strip().lower()

    condition_score = 0
    if "high_humidity" in condition or "humid" in condition:
        condition_score += 25
    if "wet" in condition:
        condition_score += 15
    if "warm" in condition:
        condition_score += 10

    severity_score = {
        "low": 15,
        "moderate": 30,
        "high": 45,
        "critical": 60,
    }.get(severity_value, 15)

    risk_score = min(100, 30 + condition_score + severity_score)

    if "rice" in crop_name:
        dominant_issue = "Blast / sheath blight risk"
        action_plan = [
            "Scout the field at sunrise and inspect flag leaves for lesions and sheath damage.",
            "Improve field drainage and reduce prolonged canopy wetness during the evening.",
            "Apply the recommended fungicidal spray only on hotspots rather than the entire block.",
        ]
    elif "groundnut" in crop_name:
        dominant_issue = "Leaf spot and pod stress"
        action_plan = [
            "Inspect lower leaves for fungal spotting and remove highly infected residue.",
            "Avoid dense canopy coverage by adjusting row spacing and maintaining airflow.",
            "Target spray on affected patches while preserving beneficial insect activity.",
        ]
    else:
        dominant_issue = "General field stress"
        action_plan = [
            "Increase field scouting frequency and document any unusual leaf curling or spotting.",
            "Check for moisture-related stress and schedule a technician review if spread continues.",
            "Use preventive measures on the highest-risk blocks before the next weather shift.",
        ]

    return {
        "crop": crop_name,
        "field_condition": field_condition,
        "severity": severity,
        "dominant_issue": dominant_issue,
        "risk_score": risk_score,
        "action_plan": action_plan,
    }
