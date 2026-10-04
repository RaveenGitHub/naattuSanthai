from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


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


class SchemeDraftUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title_en: Optional[str] = Field(default=None, max_length=10000)
    summary_en: Optional[str] = Field(default=None, max_length=10000)
    title_ta: Optional[str] = Field(default=None, max_length=10000)
    summary_ta: Optional[str] = Field(default=None, max_length=10000)
    eligibility_ta: Optional[str] = Field(default=None, max_length=10000)
    benefits_ta: Optional[str] = Field(default=None, max_length=10000)
    apply_steps_ta: Optional[str] = Field(default=None, max_length=10000)
    category: Optional[str] = Field(default=None, max_length=100)
    scheme_type: Optional[str] = Field(default=None, max_length=100)

class SchemeDraftDecision(BaseModel):
    decision: Literal["approve", "reject"]
    reason: str = Field(min_length=1, max_length=1000)
