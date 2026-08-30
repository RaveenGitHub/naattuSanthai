from __future__ import annotations

from typing import Dict


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

    return {
        "crop_type": crop_type,
        "image_url": image_url,
        "diagnosis": diagnosis,
        "recommendation": recommendation,
        "notes": notes,
        "confidence": "High",
    }
