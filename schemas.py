from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class FarmerCreate(BaseModel):
    name: str
    phone: str
    village: str
    language: str = "Tamil"


class Farmer(BaseModel):
    id: str
    name: str
    phone: str
    village: str
    language: str = "Tamil"
    created_at: datetime = Field(default_factory=datetime.utcnow)


class FarmCreate(BaseModel):
    farmer_id: str
    acreage_hectares: float
    location: str
    soil_type: str = "Loamy"


class Farm(BaseModel):
    id: str
    farmer_id: str
    acreage_hectares: float
    location: str
    soil_type: str = "Loamy"


class SoilTestCreate(BaseModel):
    farm_id: str
    ph: float
    moisture_percent: float
    nitrogen: float
    phosphorus: float
    potassium: float
    fertility_status: Optional[str] = "Moderate"


class SoilTestRecord(BaseModel):
    id: str
    farm_id: str
    ph: float
    moisture_percent: float
    nitrogen: float
    phosphorus: float
    potassium: float
    fertility_status: str
    tested_at: datetime = Field(default_factory=datetime.utcnow)


class WeatherAlert(BaseModel):
    village: str
    alert_type: str
    severity: str
    message: str


class MarketPrice(BaseModel):
    crop_name: str
    market_name: str
    price_per_kg: float
    source: str = "Mandi Feed"
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Scheme(BaseModel):
    id: str
    scheme_name: str
    eligibility_criteria: dict
    application_deadline: Optional[str] = None
    status: str = "Active"
