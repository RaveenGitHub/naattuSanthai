from __future__ import annotations

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


class RegisterRequest(BaseModel):
    username: str
    password: str
    role: str = "farmer"
    full_name: str = ""
    email: str = None
    phone: str = None


class ForgotPasswordRequest(BaseModel):
    email: str


class AuthResetPasswordRequest(BaseModel):
    username: str
    new_password: str
