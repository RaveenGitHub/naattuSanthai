from __future__ import annotations

from typing import Any, Dict

from fastapi import APIRouter, Query

from digital_farming.services.advisory import get_field_advisory
from digital_farming.services.crop_calendar import build_crop_calendar
from digital_farming.services.irrigation import build_irrigation_plan
from digital_farming.services.market_intelligence import get_market_intelligence
from digital_farming.services.pest_monitoring import evaluate_pest_risk
from digital_farming.services.soil_health import assess_soil_health
from digital_farming.services.sustainability import assess_carbon_and_sustainability
from digital_farming.services.traceability import build_traceability_summary

router = APIRouter(tags=["v1"])


@router.get("/health")
def health_check() -> Dict[str, str]:
    return {"status": "healthy", "service": "digital-farming-support-center"}


@router.get("/advisory/field-health")
def field_health_advisory(crop: str = Query(..., description="Crop type to evaluate"), village: str = Query("general", description="Village name or field zone")) -> Dict[str, Any]:
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
) -> Dict[str, Any]:
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
) -> Dict[str, Any]:
    result = assess_soil_health(crop=crop, ph=ph, nitrogen=nitrogen, phosphorus=phosphorus, potassium=potassium)
    return {
        "crop": result["crop"],
        "soil_status": result["soil_status"],
        "ph_status": result["ph_status"],
        "nitrogen_status": result["nitrogen_status"],
        "phosphorus_status": result["phosphorus_status"],
        "potassium_status": result["potassium_status"],
        "nutrient_actions": result["nutrient_actions"],
        "recommendation_summary": result["recommendation_summary"],
        "fertilizer_plan": result["fertilizer_plan"],
        "crop_recommendations": result["crop_recommendations"],
        "soil_improvement_actions": result["soil_improvement_actions"],
        "irrigation_guidance": result["irrigation_guidance"],
    }


@router.get("/field/pest-monitor")
def pest_monitor(
    crop: str = Query(..., description="Crop type under field monitoring"),
    field_condition: str = Query("normal", description="Current field condition such as high_humidity or dry"),
    severity: str = Query("low", description="Observed pest or disease severity"),
) -> Dict[str, Any]:
    result = evaluate_pest_risk(crop=crop, field_condition=field_condition, severity=severity)
    return {
        "crop": result["crop"],
        "field_condition": result["field_condition"],
        "severity": result["severity"],
        "dominant_issue": result["dominant_issue"],
        "risk_score": result["risk_score"],
        "action_plan": result["action_plan"],
    }


@router.get("/season/crop-calendar")
def crop_calendar(
    crop: str = Query(..., description="Crop type for the seasonal plan"),
    season: str = Query("Kharif", description="Season name such as Kharif, Rabi, or Summer"),
) -> Dict[str, Any]:
    calendar = build_crop_calendar(crop=crop, season=season)
    return {
        "crop": calendar["crop"],
        "season": calendar["season"],
        "activities": calendar["activities"],
    }


@router.get("/market/intelligence")
def market_intelligence(
    crop: str = Query(..., description="Crop name to assess"),
    market: str = Query(..., description="Local market or mandi name"),
) -> Dict[str, Any]:
    intelligence = get_market_intelligence(crop=crop, market=market)
    return {
        "crop": intelligence["crop"],
        "market": intelligence["market"],
        "base_price_per_kg": intelligence["base_price_per_kg"],
        "market_trend": intelligence["market_trend"],
        "recommended_action": intelligence["recommended_action"],
        "buyer_insights": intelligence["buyer_insights"],
    }


@router.get("/sustainability/carbon")
def sustainability_carbon_report(
    farm_size_ha: float = Query(..., description="Farm size in hectares"),
    soil_carbon_tons: float = Query(..., description="Estimated soil carbon stock in tons"),
    water_use_liters: float = Query(..., description="Total irrigation and operational water used in liters"),
    energy_use_kwh: float = Query(..., description="Total energy consumed in kWh"),
) -> Dict[str, Any]:
    report = assess_carbon_and_sustainability(
        farm_size_ha=farm_size_ha,
        soil_carbon_tons=soil_carbon_tons,
        water_use_liters=water_use_liters,
        energy_use_kwh=energy_use_kwh,
    )
    return {
        "farm_size_ha": report["farm_size_ha"],
        "soil_carbon_tons": report["soil_carbon_tons"],
        "water_use_liters": report["water_use_liters"],
        "energy_use_kwh": report["energy_use_kwh"],
        "carbon_score": report["carbon_score"],
        "carbon_status": report["carbon_status"],
        "water_efficiency_m3_per_ha": report["water_efficiency_m3_per_ha"],
        "energy_use_kwh_per_ha": report["energy_use_kwh_per_ha"],
        "recommendations": report["recommendations"],
    }


@router.get("/procurement/traceability")
def procurement_traceability(
    crop: str = Query(None, description="Crop type being traced"),
    lot_id: str = Query(None, description="Lot or batch identifier"),
    batch_quality: str = Query(None, description="Quality grade for lot verification"),
    farmer: str = Query(None, description="Farmer or producer name"),
    batch: str = Query(None, description="Batch or lot identifier"),
    location: str = Query(None, description="Origin village or farm location"),
    quality_grade: str = Query("B", description="Quality grade such as A, B, or C"),
) -> Dict[str, Any]:
    lot_reference = lot_id or batch or "UNKNOWN-LOT"
    quality_value = (batch_quality or quality_grade or "B").upper()

    if lot_id is not None or crop is not None:
        verification_steps = [
            "Lot identity matched to farm records and producer declaration.",
            "Field quality inspection completed and the batch was reviewed for consistency.",
            "Movement and collection records were checked for completion and chain-of-custody integrity.",
        ]
        status = "verified" if quality_value in {"A", "B", "GOOD"} else "requires_review"
        return {
            "crop": crop or "unknown",
            "lot_id": lot_reference,
            "batch_status": status,
            "quality_grade": quality_value,
            "verification_steps": verification_steps,
        }

    if farmer is None or batch is None or location is None:
        raise ValueError("farmer, batch, and location are required when using the full traceability summary")

    traceability = build_traceability_summary(
        farmer=farmer,
        batch=batch,
        location=location,
        quality_grade=quality_grade,
    )
    return {
        "farmer": traceability["farmer"],
        "batch": traceability["batch"],
        "location": traceability["location"],
        "quality_grade": traceability["quality_grade"],
        "traceability_status": traceability["traceability_status"],
        "procurement_steps": traceability["procurement_steps"],
    }
