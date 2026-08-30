from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Dict
from uuid import uuid4

import jwt

from database import get_connection

SECRET_KEY = "digital-farming-support-center-secret-key"
ALGORITHM = "HS256"

DEFAULT_USERS = {
    "operator1": {"password": "password123", "role": "operator"},
    "admin1": {"password": "admin123", "role": "admin"},
    "farmer1": {"password": "farmer123", "role": "farmer"},
}


def create_user(username: str, password: str, role: str) -> Dict[str, str]:
    if not username or not password:
        raise ValueError("Username and password are required")
    if role not in {"farmer", "operator", "admin"}:
        raise ValueError("Invalid role")

    with get_connection() as conn:
        existing = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            raise ValueError("User already exists")

        conn.execute(
            "INSERT INTO users (id, username, password, role, created_at) VALUES (?, ?, ?, ?, ?)",
            (f"USR-{uuid4().hex}", username, password, role, datetime.now(timezone.utc).isoformat()),
        )

    return {"username": username, "role": role}


def _get_user(username: str) -> Dict[str, str] | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT username, password, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row is None:
        return None
    return {"username": row["username"], "password": row["password"], "role": row["role"]}


def seed_default_users() -> None:
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count > 0:
        return
    for username, details in DEFAULT_USERS.items():
        create_user(username, details["password"], details["role"])


seed_default_users()


def create_token(username: str) -> str:
    user = _get_user(username)
    if user is None:
        raise ValueError("User not found")
    payload = {
        "sub": username,
        "role": user["role"],
        "exp": datetime.now(timezone.utc) + timedelta(hours=12),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Dict[str, str]:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])


def authenticate(username: str, password: str) -> Dict[str, str]:
    user = _get_user(username)
    if user is None or user["password"] != password:
        raise ValueError("Invalid username or password")
    return {"token": create_token(username), "role": user["role"]}
