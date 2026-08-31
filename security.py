from __future__ import annotations

import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional
from uuid import uuid4

import jwt

from database import get_connection
from digital_farming.config import settings

SECRET_KEY = os.getenv("SECRET_KEY", settings.secret_key)
ALGORITHM = os.getenv("JWT_ALGORITHM", settings.jwt_algorithm)
HASH_PREFIX = "pbkdf2_sha256$"

DEFAULT_USERS = {
    "operator1": {"password": "password123", "role": "operator"},
    "admin1": {"password": "admin123", "role": "admin"},
    "farmer1": {"password": "farmer123", "role": "farmer"},
}


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    iterations = 200000
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
    return (
        f"{HASH_PREFIX}{iterations}$"
        f"{base64.b64encode(salt).decode('ascii')}$"
        f"{base64.b64encode(digest).decode('ascii')}"
    )


def verify_password(plain_password: str, stored_password: str) -> bool:
    if not stored_password or not stored_password.startswith(HASH_PREFIX):
        return hmac.compare_digest(plain_password, stored_password or "")

    try:
        _, iterations_str, salt_b64, digest_b64 = stored_password.split("$", 3)
        salt = base64.b64decode(salt_b64.encode("ascii"))
        expected = base64.b64decode(digest_b64.encode("ascii"))
        actual = hashlib.pbkdf2_hmac(
            "sha256",
            plain_password.encode("utf-8"),
            salt,
            int(iterations_str),
        )
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


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
            (f"USR-{uuid4().hex}", username, hash_password(password), role, datetime.now(timezone.utc).isoformat()),
        )

    return {"username": username, "role": role}


def list_users() -> List[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT username, role, created_at FROM users ORDER BY created_at ASC"
        ).fetchall()
    return [
        {"username": row["username"], "role": row["role"], "created_at": row["created_at"]}
        for row in rows
    ]


def get_profile(username: str) -> Dict[str, str]:
    user = _get_user(username)
    if user is None:
        raise ValueError("User not found")
    return {"username": user["username"], "role": user["role"]}


def reset_password(username: str, current_password: str, new_password: str) -> Dict[str, str]:
    if not new_password:
        raise ValueError("New password is required")

    user = _get_user(username)
    if user is None or not verify_password(current_password, user["password"]):
        raise ValueError("Current password is incorrect")

    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET password = ? WHERE username = ?",
            (hash_password(new_password), username),
        )

    return {"username": username, "status": "updated"}


def _get_user(username: str) -> Optional[Dict[str, str]]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT username, password, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row is None:
        return None

    stored_password = row["password"]
    if not stored_password.startswith(HASH_PREFIX):
        migrated = hash_password(stored_password)
        with get_connection() as conn:
            conn.execute("UPDATE users SET password = ? WHERE username = ?", (migrated, username))
        stored_password = migrated

    return {"username": row["username"], "password": stored_password, "role": row["role"]}


def seed_default_users() -> None:
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]

    if count == 0:
        for username, details in DEFAULT_USERS.items():
            create_user(username, details["password"], details["role"])
        return

    for username, details in DEFAULT_USERS.items():
        with get_connection() as conn:
            row = conn.execute(
                "SELECT password FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None:
            create_user(username, details["password"], details["role"])
            continue
        if not verify_password(details["password"], row["password"]):
            with get_connection() as conn:
                conn.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (hash_password(details["password"]), username),
                )


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
    if user is None or not verify_password(password, user["password"]):
        raise ValueError("Invalid username or password")
    return {"token": create_token(username), "role": user["role"]}
