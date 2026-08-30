from __future__ import annotations

from fastapi import APIRouter, Query

from digital_farming.services.advisory import get_field_advisory
from digital_farming.services.irrigation import build_irrigation_plan
from digital_farming.services.soil_health import assess_soil_health

router = APIRouter(tags=["v1"])


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy", "service": "digital-farming-support-center"}


@router.get("/advisory/field-health")
def field_health_advisory(crop: str = Query(..., description="Crop type to evaluate"), village: str = Query("general", description="Village name or field zone")) -> dict:
    payload = get_field_advisory(crop=crop, village=village)
    return {
        "crop": payload["crop"],
        "village": payload["village"],
        "risk_level": payload["risk_level"],
        "soil_moisture_percent": payload["soil_moisture_percent"],
        "summary": payload["summary"],
        "recommendations": payload["recommendations"],
    }


@router.get("/operations/irrigation-plan")
def irrigation_plan(
    crop: str = Query(..., description="Crop type for irrigation planning"),
    soil_moisture_percent: float = Query(..., description="Current soil moisture as a percentage"),
    rainfall_forecast_mm: float = Query(0.0, description="Expected rainfall in the next cycle"),
    field_area_ha: float = Query(1.0, description="Irrigated field area in hectares"),
) -> dict:
    plan = build_irrigation_plan(
        crop=crop,
        soil_moisture_percent=soil_moisture_percent,
        rainfall_forecast_mm=rainfall_forecast_mm,
        field_area_ha=field_area_ha,
    )
    return {
        "crop": plan["crop"],
        "recommended_start": plan["recommended_start"],
        "water_liters_per_ha": plan["water_liters_per_ha"],
        "total_water_liters": plan["total_water_liters"],
        "recommendations": plan["recommendations"],
    }


@router.get("/soil/health")
def soil_health(
    crop: str = Query(..., description="Crop type under evaluation"),
    ph: float = Query(..., description="Soil pH value"),
    nitrogen: float = Query(..., description="Nitrogen level (ppm or kg/ha equivalent)"),
    phosphorus: float = Query(..., description="Phosphorus level"),
    potassium: float = Query(..., description="Potassium level"),
) -> dict:
    result = assess_soil_health(crop=crop, ph=ph, nitrogen=nitrogen, phosphorus=phosphorus, potassium=potassium)
    return {
        "crop": result["crop"],
        "soil_status": result["soil_status"],
        "ph_status": result["ph_status"],
        "nitrogen_status": result["nitrogen_status"],
        "phosphorus_status": result["phosphorus_status"],
        "potassium_status": result["potassium_status"],
        "nutrient_actions": result["nutrient_actions"],
    }
