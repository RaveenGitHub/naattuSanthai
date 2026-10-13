from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, constr


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


class TraceabilityLotCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    lot_id: str = Field(min_length=1, max_length=80)
    crop: str = Field(min_length=1, max_length=100)
    farmer: str = Field(min_length=1, max_length=120)
    origin: str = Field(min_length=1, max_length=200)
    quality_grade: Literal["A", "B", "C"] = "B"


class TraceabilityEventCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    event_type: Literal[
        "harvested", "graded", "collected", "transported", "buyer_handoff",
    ]
    location: str = Field(min_length=1, max_length=200)
    notes: str = Field(default="", max_length=2000)


class PilotFeedbackCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    district: str = Field(default="", max_length=120)
    village: str = Field(default="", max_length=120)
    farmer_group: str = Field(default="", max_length=160)
    scheme_under_test: str = Field(default="", max_length=200)
    clarity_score: Optional[int] = Field(default=None, ge=1, le=5)
    usefulness_score: Optional[int] = Field(default=None, ge=1, le=5)
    issues: List[constr(min_length=1, max_length=500, strip_whitespace=True)] = Field(default_factory=list, max_length=10)
    recommended_change: str = Field(default="", max_length=2000)
    feedback_notes: str = Field(default="", max_length=4000)


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
