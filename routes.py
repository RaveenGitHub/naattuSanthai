from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query, Request

from auth import require_role
from schemas import FarmCreate, FarmerCreate, SoilTestCreate
from services import (
    create_farm,
    create_farmer,
    create_soil_test,
    list_farms,
    list_farmers,
    list_market_prices,
    list_soil_tests,
    list_weather_alerts,
    seed_market_data,
)

router = APIRouter(prefix="/api")


@router.get("/farmers")
def get_farmers():
    return {"success": True, "data": list_farmers(), "error": None}


@router.post("/farmers")
def post_farmer(request: Request, payload: FarmerCreate):
    role = request.headers.get("X-User-Role", "farmer")
    if role not in {"farmer", "operator", "admin"}:
        raise HTTPException(status_code=403, detail="Role not allowed")
    farmer = create_farmer(payload.model_dump())
    return {"success": True, "data": farmer.model_dump(), "error": None}


@router.get("/farms")
def get_farms(farmer_id: str | None = Query(default=None)):
    return {"success": True, "data": list_farms(farmer_id), "error": None}


@router.post("/farms")
def post_farm(request: Request, payload: FarmCreate):
    role = request.headers.get("X-User-Role", "farmer")
    if role not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator/Admin access required")
    farm = create_farm(payload.model_dump())
    return {"success": True, "data": farm.model_dump(), "error": None}


@router.get("/soil-tests")
def get_soil_tests(farm_id: str | None = Query(default=None)):
    return {"success": True, "data": list_soil_tests(farm_id), "error": None}


@router.post("/soil-tests")
def post_soil_test(request: Request, payload: SoilTestCreate):
    role = request.headers.get("X-User-Role", "farmer")
    if role not in {"operator", "admin"}:
        raise HTTPException(status_code=403, detail="Operator/Admin access required")
    record = create_soil_test(payload.model_dump())
    return {"success": True, "data": record.model_dump(), "error": None}


@router.get("/weather/alerts")
def get_weather_alerts(village: str | None = Query(default=None)):
    return {"success": True, "data": list_weather_alerts(village), "error": None}


@router.get("/market-prices")
def get_market_prices(crop_name: str | None = Query(default=None)):
    seed_market_data()
    return {"success": True, "data": list_market_prices(crop_name), "error": None}


@router.get("/schemes")
def get_schemes(request: Request, farmer_id: str | None = Query(default=None)):
    role = request.headers.get("X-User-Role", "farmer")
    if role not in {"farmer", "operator", "admin"}:
        raise HTTPException(status_code=403, detail="Role not allowed")
    if farmer_id is None:
        raise HTTPException(status_code=400, detail="farmer_id is required")
    return {
        "success": True,
        "data": [
            {"id": "SCHEME-001", "scheme_name": "Crop Insurance Support", "status": "Eligible"},
            {"id": "SCHEME-002", "scheme_name": "Irrigation Grant", "status": "Under review"},
        ],
        "error": None,
    }
