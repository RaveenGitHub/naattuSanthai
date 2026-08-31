from __future__ import annotations

from typing import Any, Dict


def build_irrigation_plan(
    crop: str,
    soil_moisture_percent: float,
    rainfall_forecast_mm: float = 0.0,
    field_area_ha: float = 1.0,
) -> Dict[str, Any]:
    crop_name = (crop or "crop").strip().lower()

    if "rice" in crop_name:
        target_moisture = 70
        water_need_per_ha = 5500
        recommended_start = "Early morning (05:30 - 07:00)"
        irrigation_window = "2 cycles in the next 36 hours"
        if rainfall_forecast_mm > 10:
            recommended_start = "Delay by 1 day; rainfall expected to cover crop demand"
            irrigation_window = "Natural rainfall likely sufficient for the next cycle"
    elif "groundnut" in crop_name:
        target_moisture = 60
        water_need_per_ha = 4200
        recommended_start = "Late evening (18:30 - 20:00)"
        irrigation_window = "Single light irrigation cycle before the next hot spell"
    else:
        target_moisture = 65
        water_need_per_ha = 4800
        recommended_start = "Morning (06:00 - 08:00)"
        irrigation_window = "Irrigation window remains flexible for the next 24 hours"

    moisture_gap = max(0.0, target_moisture - soil_moisture_percent)
    effective_water = max(0.0, water_need_per_ha * (moisture_gap / 100.0))
    total_liters = effective_water * field_area_ha * 1000

    if rainfall_forecast_mm > 0:
        total_liters = max(0.0, total_liters - (rainfall_forecast_mm * 1000 * field_area_ha * 0.45))

    recommendations = [
        f"Maintain soil moisture near {target_moisture}% to keep the crop in the optimal growth band.",
        f"Start irrigation {recommended_start.lower()} to reduce evaporation and improve root-zone absorption.",
        f"Use a {irrigation_window} and validate field uniformity across all blocks.",
    ]

    return {
        "crop": crop_name,
        "target_moisture_percent": target_moisture,
        "soil_moisture_percent": soil_moisture_percent,
        "rainfall_forecast_mm": rainfall_forecast_mm,
        "field_area_ha": field_area_ha,
        "recommended_start": recommended_start,
        "water_liters_per_ha": round(max(0.0, total_liters / max(field_area_ha, 0.01)), 2),
        "total_water_liters": round(max(0.0, total_liters), 2),
        "recommendations": recommendations,
    }
