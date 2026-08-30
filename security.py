from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict

import jwt

SECRET_KEY = "digital-farming-support-center-secret-key"
ALGORITHM = "HS256"

USER_DB = {
    "operator1": {"password": "password123", "role": "operator"},
    "admin1": {"password": "admin123", "role": "admin"},
    "farmer1": {"password": "farmer123", "role": "farmer"},
}


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "role": USER_DB[username]["role"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Dict[str, str]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def authenticate(username: str, password: str) -> Dict[str, str]:
    user = USER_DB.get(username)
    if user is None or user["password"] != password:
        raise ValueError("Invalid username or password")
    return {"token": create_token(username), "role": user["role"]}
