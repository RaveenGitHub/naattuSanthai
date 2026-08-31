from __future__ import annotations

from typing import Any, Dict, List


def assess_soil_health(crop: str, ph: float, nitrogen: float, phosphorus: float, potassium: float) -> Dict[str, Any]:
    crop_name = (crop or "crop").strip().lower()

    if ph < 5.8:
        ph_status = "Acidic"
        ph_action = "Apply lime in split doses to correct soil acidity before the next nutrient cycle."
    elif ph > 7.2:
        ph_status = "Alkaline"
        ph_action = "Use sulphur or organic matter to bring pH toward the crop-safe range."
    else:
        ph_status = "Balanced"
        ph_action = "Maintain current pH with regular monitoring and residue management."

    if "groundnut" in crop_name:
        nitrogen_status = "Moderate" if nitrogen >= 20 else "Low"
        phosphorus_status = "Low" if phosphorus < 20 else "Adequate"
        potassium_status = "Adequate" if potassium >= 150 else "Low"
        base_status = "Needs nutrient balancing"
    else:
        nitrogen_status = "Adequate" if nitrogen >= 28 else "Moderate"
        phosphorus_status = "Adequate" if phosphorus >= 20 else "Low"
        potassium_status = "Adequate" if potassium >= 180 else "Moderate"
        base_status = "Generally healthy"

    actions: List[str] = [ph_action]
    if nitrogen_status != "Adequate":
        actions.append("Apply a targeted nitrogen application based on the crop stage and soil test trend.")
    if phosphorus_status != "Adequate":
        actions.append("Increase phosphorus availability through rock phosphate or a phosphorus-rich blend.")
    if potassium_status != "Adequate":
        actions.append("Add potassium support to improve water efficiency and fruit or pod development.")
    actions.append("Schedule the next soil test in 2 to 3 weeks to validate nutrient recovery.")

    return {
        "crop": crop_name,
        "ph": ph,
        "nitrogen": nitrogen,
        "phosphorus": phosphorus,
        "potassium": potassium,
        "soil_status": base_status,
        "ph_status": ph_status,
        "nitrogen_status": nitrogen_status,
        "phosphorus_status": phosphorus_status,
        "potassium_status": potassium_status,
        "nutrient_actions": actions,
    }
