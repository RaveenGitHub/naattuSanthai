from __future__ import annotations

from typing import Any, Dict


def get_field_advisory(crop: str, village: str = "general", land_size: str = "") -> Dict[str, Any]:
    crop_name = (crop or "crop").strip().lower()
    village_name = village or "general"

    if "rice" in crop_name:
        risk = "Moderate"
        soil_moisture = 68
        summary = "Rice fields are stable, but waterlogging risk remains after afternoon rainfall."
        recommendations = [
            "Monitor drainage channels for 48 hours and prevent ponding around field edges.",
            "Apply nitrogen in split doses to avoid lodging and nutrient stress.",
            "Schedule the next irrigation at early morning when soil moisture drops below 60%.",
        ]
    elif "groundnut" in crop_name:
        risk = "High"
        soil_moisture = 56
        summary = "Groundnut blocks show drying stress and a moderate fungal risk near shaded patches."
        recommendations = [
            "Inspect lower leaves for early fungal spotting and remove infected residues.",
            "Apply a light irrigation cycle before noon to reduce root-zone stress.",
            "Increase potassium support where soil tests show depletion.",
        ]
    else:
        risk = "Low"
        soil_moisture = 64
        summary = "Crop conditions are generally healthy and follow expected seasonal variation."
        recommendations = [
            "Continue routine crop scouting across all active blocks.",
            "Keep nutrient and irrigation records updated for the next advisory cycle.",
            "Review market timing before harvest to improve farm-gate pricing.",
        ]

    try:
        size_value = float((land_size or "").strip())
    except (TypeError, ValueError):
        size_value = None
    if size_value is not None and size_value < 1.0:
        recommendations.append("Focus on intensive practices and high-value crops suitable for small plots.")
    elif size_value is not None and size_value > 5.0:
        recommendations.append("Consider mechanization and crop rotation strategies for larger holdings.")

    return {
        "crop": crop_name,
        "village": village_name,
        "land_size": land_size,
        "soil_moisture_percent": soil_moisture,
        "risk_level": risk,
        "summary": summary,
        "recommendations": recommendations,
    }
