from __future__ import annotations

import math
from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator


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


class AdminUserStatusRequest(BaseModel):
    action: Literal["activate", "deactivate", "reactivate"]
    reason: str = Field(default="", max_length=1000)


class AdminUserSummary(BaseModel):
    id: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    role: str
    status: str
    created_at: str
    last_login_at: Optional[str] = None


class AdminUserListResult(BaseModel):
    items: List[AdminUserSummary]
    page: int
    page_size: int
    total: int
    total_pages: int


class AdminUserListResponse(BaseModel):
    success: bool
    data: AdminUserListResult
    error: Optional[str] = None


class AdminUserDetail(BaseModel):
    id: str
    username: str
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
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
    role: str
    status: str
    failed_login_attempts: int
    created_at: str
    updated_at: Optional[str] = None
    last_login_at: Optional[str] = None


class AdminUserDetailResponse(BaseModel):
    success: bool
    data: AdminUserDetail
    error: Optional[str] = None


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
    username: str = Field(min_length=1, max_length=80)
    password: str = Field(min_length=8, max_length=128)
    role: Literal["farmer"] = "farmer"
    full_name: str = ""
    email: Optional[str] = None
    phone: Optional[str] = None
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
    email: str = Field(min_length=3, max_length=254)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        cleaned = value.strip()
        local, separator, domain = cleaned.partition("@")
        if not separator or not local or "." not in domain or domain.startswith(".") or domain.endswith("."):
            raise ValueError("A valid email address is required")
        return cleaned


class AuthResetPasswordRequest(BaseModel):
    reset_token: str = Field(min_length=32, max_length=256)
    new_password: str = Field(min_length=8, max_length=128)
