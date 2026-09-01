from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

from auth import get_user_role
from schemas import FarmCreate, FarmerCreate, SoilTestCreate
from services import (
    create_farm,
    create_farmer,
    create_soil_test,
    get_scheme_update_by_id,
    list_archived_scheme_updates,
    list_farms,
    list_farmers,
    list_latest_scheme_updates,
    list_market_prices,
    list_soil_tests,
    list_weather_alerts,
    seed_government_scheme_data,
    seed_market_data,
)

router = APIRouter(prefix="/api")

ROLE_HIERARCHY = {
    "farmer": {"farmer", "operator", "admin"},
    "operator": {"operator", "admin"},
    "admin": {"admin"},
}


def require_route_role(request: Request, required_role: str) -> None:
    role = get_user_role(request)
    allowed_roles = ROLE_HIERARCHY.get(required_role, {required_role})
    if role not in allowed_roles:
        raise HTTPException(status_code=403, detail=f"{required_role.capitalize()} access required")


@router.get("/farmers")
def get_farmers():
    return {"success": True, "data": list_farmers(), "error": None}


@router.post("/farmers")
def post_farmer(request: Request, payload: FarmerCreate):
    require_route_role(request, "farmer")
    farmer = create_farmer(payload.model_dump())
    return {"success": True, "data": farmer.model_dump(), "error": None}


@router.get("/farms")
def get_farms(farmer_id: Optional[str] = Query(default=None)):
    return {"success": True, "data": list_farms(farmer_id), "error": None}


@router.post("/farms")
def post_farm(request: Request, payload: FarmCreate):
    require_route_role(request, "operator")
    farm = create_farm(payload.model_dump())
    return {"success": True, "data": farm.model_dump(), "error": None}


@router.get("/soil-tests")
def get_soil_tests(farm_id: Optional[str] = Query(default=None)):
    return {"success": True, "data": list_soil_tests(farm_id), "error": None}


@router.post("/soil-tests")
def post_soil_test(request: Request, payload: SoilTestCreate):
    require_route_role(request, "operator")
    record = create_soil_test(payload.model_dump())
    return {"success": True, "data": record.model_dump(), "error": None}


@router.get("/weather/alerts")
def get_weather_alerts(village: Optional[str] = Query(default=None)):
    return {"success": True, "data": list_weather_alerts(village), "error": None}


@router.get("/market-prices")
def get_market_prices(crop_name: Optional[str] = Query(default=None)):
    seed_market_data()
    return {"success": True, "data": list_market_prices(crop_name), "error": None}


@router.get("/schemes")
def get_schemes(request: Request, farmer_id: Optional[str] = Query(default=None)):
    require_route_role(request, "farmer")
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


@router.get("/schemes/latest")
def get_latest_schemes(category: Optional[str] = Query(default=None), search: Optional[str] = Query(default=None)):
    return {"success": True, "data": list_latest_scheme_updates(category=category, search=search), "error": None}


@router.get("/schemes/archive")
def get_archived_schemes(category: Optional[str] = Query(default=None), search: Optional[str] = Query(default=None)):
    return {"success": True, "data": list_archived_scheme_updates(category=category, search=search), "error": None}


@router.get("/scheme/{scheme_id}")
def get_scheme_detail(scheme_id: str):
    entry = get_scheme_update_by_id(scheme_id)
    if entry is None:
        raise HTTPException(status_code=404, detail="Scheme not found")
    return {"success": True, "data": entry, "error": None}


@router.post("/fetch/update")
def trigger_scheme_fetch(request: Request):
    require_route_role(request, "admin")
    seed_market_data()
    seed_government_scheme_data()
    return {"success": True, "data": {"message": "Government scheme update fetch completed"}, "error": None}
