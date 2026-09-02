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
        phosphorus_status = "Adequate" if phosphorus >= 18 else "Low"
        potassium_status = "Adequate" if potassium >= 150 else "Low"
        base_status = "Needs nutrient balancing"
        recommendation_summary = (
            "Groundnut soil needs a corrective nutrient plan with liming support and a split-dose fertilizer strategy for pod filling and root growth."
        )
        fertilizer_plan = [
            {"nutrient": "Nitrogen", "dose": "Apply 20-25 kg N/acre in split doses", "reason": "Supports vegetative growth and pod development."},
            {"nutrient": "Phosphorus", "dose": "Add phosphorus-rich fertilizer if below 18 ppm", "reason": "Improves root formation and pegging."},
            {"nutrient": "Potassium", "dose": "Maintain 150-200 ppm with potash application", "reason": "Improves drought tolerance and pod quality."},
        ]
        crop_recommendations = [
            "Groundnut or sesame are suitable when the soil is moderately balanced and moisture remains stable.",
            "Short-duration pulse crops may perform better while nutrient levels are corrected.",
        ]
    else:
        nitrogen_status = "Adequate" if nitrogen >= 28 else "Moderate"
        phosphorus_status = "Adequate" if phosphorus >= 20 else "Low"
        potassium_status = "Adequate" if potassium >= 180 else "Moderate"
        base_status = "Generally healthy"
        recommendation_summary = (
            f"{crop_name.title()} soil is stable enough for routine management, but the current nutrient profile should be monitored to avoid stress during the next growth phase."
        )
        fertilizer_plan = [
            {"nutrient": "Nitrogen", "dose": "Apply a moderate split nitrogen application", "reason": "Maintains canopy vigor without excess vegetative growth."},
            {"nutrient": "Phosphorus", "dose": "Top up phosphorus where soil value is below crop target", "reason": "Supports root establishment and early growth."},
            {"nutrient": "Potassium", "dose": "Use potash if potassium falls below the crop threshold", "reason": "Improves stress tolerance and grain filling."},
        ]
        crop_recommendations = [
            "This soil profile supports a moderate-yield crop rotation with careful nutrient monitoring.",
            "Consider resilient varieties that fit the local rainfall pattern and season length.",
        ]

    soil_improvement_actions = [
        ph_action,
        "Use compost or farmyard manure to improve soil structure and microbial activity.",
        "Practice crop residue retention and green manure rotation to rebuild organic matter.",
    ]
    if nitrogen_status != "Adequate":
        soil_improvement_actions.append("Apply a targeted nitrogen application based on the crop stage and soil test trend.")
    if phosphorus_status != "Adequate":
        soil_improvement_actions.append("Increase phosphorus availability through rock phosphate or a phosphorus-rich blend.")
    if potassium_status != "Adequate":
        soil_improvement_actions.append("Add potassium support to improve water efficiency and fruit or pod development.")
    soil_improvement_actions.append("Schedule the next soil test in 2 to 3 weeks to validate nutrient recovery.")

    irrigation_guidance = [
        "Irrigate at early morning to reduce evaporation and improve root-zone absorption.",
        "Adjust irrigation frequency based on current moisture and the next rainfall forecast.",
        "Avoid over-irrigation when the soil is near the target moisture range for the crop.",
    ]

    if ph_status != "Balanced":
        irrigation_guidance.append("Correct the pH first, then calibrate irrigation to avoid nutrient locking in the root zone.")

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
        "nutrient_actions": soil_improvement_actions,
        "recommendation_summary": recommendation_summary,
        "fertilizer_plan": fertilizer_plan,
        "crop_recommendations": crop_recommendations,
        "soil_improvement_actions": soil_improvement_actions,
        "irrigation_guidance": irrigation_guidance,
    }
