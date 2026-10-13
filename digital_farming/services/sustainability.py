from __future__ import annotations

import math
from typing import Any, Dict


def assess_carbon_and_sustainability(farm_size_ha: float, soil_carbon_tons: float, water_use_liters: float, energy_use_kwh: float) -> Dict[str, Any]:
    measurements = (farm_size_ha, soil_carbon_tons, water_use_liters, energy_use_kwh)
    if not all(math.isfinite(value) for value in measurements):
        raise ValueError("Sustainability measurements must be finite numbers")
    if farm_size_ha <= 0:
        raise ValueError("Farm size must be greater than zero")
    if any(value < 0 for value in measurements[1:]):
        raise ValueError("Carbon, water, and energy measurements cannot be negative")

    carbon_score = (soil_carbon_tons / farm_size_ha) * 10.0
    water_efficiency = (water_use_liters / farm_size_ha) / 1000.0
    energy_efficiency = energy_use_kwh / farm_size_ha

    if carbon_score >= 6.0:
        carbon_status = "Strong soil carbon performance"
        regeneration_status = "Regenerative practices are performing strongly and soil carbon is stabilizing."
    elif carbon_score >= 3.0:
        carbon_status = "Moderate carbon improvement potential"
        regeneration_status = "Regeneration is progressing, but cover-crop and residue retention should be strengthened."
    else:
        carbon_status = "Carbon build-up needs attention"
        regeneration_status = "Regenerative performance needs attention to restore soil health and water efficiency."

    regenerative_actions = [
        "Maintain residue retention and minimal soil disturbance across active plots.",
        "Add cover crops between seasons to improve root biomass and soil structure.",
        "Validate nutrient cycling and microbial activity with the next soil test cycle.",
    ]
    recommendations = []
    if carbon_score < 5.0:
        recommendations.append("Increase residue retention and cover-crop cycles to improve soil carbon storage.")
    if water_efficiency > 1.0:
        recommendations.append("Improve irrigation precision and mulching to reduce water intensity per hectare.")
    if energy_efficiency > 70:
        recommendations.append("Shift to efficient pumps, solar support, and better scheduling to cut energy use.")
    if not recommendations:
        recommendations.append("Continue current regenerative practices and validate performance through the next seasonal review.")

    return {
        "farm_size_ha": float(farm_size_ha),
        "soil_carbon_tons": float(soil_carbon_tons),
        "water_use_liters": float(water_use_liters),
        "energy_use_kwh": float(energy_use_kwh),
        "carbon_score": round(carbon_score, 2),
        "carbon_status": carbon_status,
        "regeneration_status": regeneration_status,
        "regenerative_actions": regenerative_actions,
        "water_efficiency_m3_per_ha": round(water_efficiency, 2),
        "energy_use_kwh_per_ha": round(energy_efficiency, 2),
        "assessment_basis": "Indicative estimates from user-supplied values; not independently measured or carbon-accounting verified.",
        "recommendations": recommendations,
    }
