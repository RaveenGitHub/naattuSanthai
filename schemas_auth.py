from __future__ import annotations

import math
from typing import Optional

from pydantic import BaseModel, field_validator


class LoginRequest(BaseModel):
    username: str
    password: str


class DiagnoseRequest(BaseModel):
    crop_type: str
    image_url: str
    notes: str = ""


class UserCreateRequest(BaseModel):
    username: str
    password: str
    role: str = "farmer"


class PasswordResetRequest(BaseModel):
    current_password: str
    new_password: str


class ProfileFieldsModel(BaseModel):
    full_name: Optional[str] = None
    village: Optional[str] = None
    region: Optional[str] = None
    area: Optional[str] = None
    primary_crop: Optional[str] = None
    land_size: Optional[str] = None
    water_source: Optional[str] = None
    farming_method: Optional[str] = None
    secondary_crops: Optional[str] = None
    tools: Optional[str] = None
    irrigation_type: Optional[str] = None

    @field_validator(
        "full_name",
        "village",
        "region",
        "primary_crop",
        "water_source",
        "farming_method",
        "secondary_crops",
        "tools",
        "irrigation_type",
        mode="before",
    )
    @classmethod
    def validate_profile_text(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = str(value).strip()
        if not cleaned:
            raise ValueError("Profile text fields cannot be empty")
        if len(cleaned) > 120:
            raise ValueError("Profile text fields must be 120 characters or fewer")
        return cleaned

    @field_validator("area", "land_size", mode="before")
    @classmethod
    def validate_positive_measurement(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        cleaned = str(value).strip()
        try:
            measurement = float(cleaned)
        except (TypeError, ValueError) as exc:
            raise ValueError("Area and land size must be positive numbers") from exc
        if not math.isfinite(measurement) or measurement <= 0:
            raise ValueError("Area and land size must be positive numbers")
        return cleaned


class ProfileUpdateRequest(ProfileFieldsModel):
    pass


class RegisterRequest(ProfileFieldsModel):
    username: str
    password: str
    role: str = "farmer"
    full_name: str = ""
    email: str = None
    phone: str = None
    village: str = ""
    region: str = ""
    area: str = ""
    primary_crop: str = ""
    land_size: str = ""
    water_source: str = ""
    farming_method: str = ""
    secondary_crops: str = ""
    tools: str = ""
    irrigation_type: str = ""


class ForgotPasswordRequest(BaseModel):
    email: str


class AuthResetPasswordRequest(BaseModel):
    username: str
    new_password: str
