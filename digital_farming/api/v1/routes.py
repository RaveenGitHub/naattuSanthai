from __future__ import annotations

from fastapi import APIRouter, Query

from digital_farming.services.advisory import get_field_advisory

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
