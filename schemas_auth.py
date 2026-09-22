from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


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


class ProfileUpdateRequest(BaseModel):
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


class RegisterRequest(BaseModel):
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
