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
