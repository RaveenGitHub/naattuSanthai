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


def create_user(
    username: str,
    password: str,
    role: str,
    *,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    full_name: str = "",
    village: str = "",
    status: str = "active",
) -> Dict[str, str]:
    if not username or not password:
        raise ValueError("Username and password are required")
    if role not in {"farmer", "operator", "admin"}:
        raise ValueError("Invalid role")

    if status not in {"active", "pending_verification", "locked"}:
        raise ValueError("Invalid status")

    otp_code = None
    otp_expires_at = None
    if status == "pending_verification":
        otp_code = f"{secrets.randbelow(900000) + 100000:06d}"
        otp_expires_at = (datetime.now(timezone.utc) + timedelta(minutes=10)).isoformat()

    with get_connection() as conn:
        existing = conn.execute("SELECT 1 FROM users WHERE username = ?", (username,)).fetchone()
        if existing:
            raise ValueError("User already exists")

        conn.execute(
            """
            INSERT INTO users (id, username, password, role, email, phone, full_name, village, status, otp_code, otp_expires_at,
            failed_login_attempts, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
            """,
            (
                f"USR-{uuid4().hex}",
                username,
                hash_password(password),
                role,
                email,
                phone,
                full_name,
                village,
                status,
                otp_code,
                otp_expires_at,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    record_audit_log(username, "user_created", "users", "success", f"Created user with role {role} and status {status}")
    return {"username": username, "role": role, "status": status, "otp_code": otp_code}


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
    return {"username": user["username"], "role": user["role"], "status": user.get("status", "active")}


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

    record_audit_log(username, "password_reset", "users", "success", "Password reset completed")
    return {"username": username, "status": "updated"}


def unlock_user(username: str) -> Dict[str, str]:
    if not username:
        raise ValueError("Username is required")

    user = _get_user(username)
    if user is None:
        raise ValueError("User not found")

    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET status = ?, failed_login_attempts = 0, otp_code = NULL, otp_expires_at = NULL, updated_at = ? WHERE username = ?",
            ("active", datetime.now(timezone.utc).isoformat(), username),
        )

    record_audit_log(username, "user_unlocked", "users", "success", "Admin reset lockout state")
    return {"username": username, "status": "active"}


def _get_user(username: str) -> Optional[Dict[str, str]]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT username, password, role, status, otp_code, otp_expires_at, failed_login_attempts, email, phone
            FROM users WHERE username = ?
            """,
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

    return {
        "username": row["username"],
        "password": stored_password,
        "role": row["role"],
        "status": row["status"] or "active",
        "otp_code": row["otp_code"],
        "otp_expires_at": row["otp_expires_at"],
        "failed_login_attempts": row["failed_login_attempts"] or 0,
        "email": row["email"],
        "phone": row["phone"],
    }


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


def record_audit_log(username: str, action: str, resource: str, outcome: str, details: Optional[str] = None) -> Dict[str, str]:
    event_id = f"AUD-{uuid4().hex}"
    record = {
        "id": event_id,
        "username": username,
        "action": action,
        "resource": resource,
        "outcome": outcome,
        "details": details,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO audit_logs (id, username, action, resource, outcome, details, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (record["id"], record["username"], record["action"], record["resource"], record["outcome"], record["details"], record["created_at"]),
        )
    return record


def list_audit_logs(limit: int = 100) -> List[Dict[str, str]]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, username, action, resource, outcome, details, created_at FROM audit_logs ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "username": row["username"],
            "action": row["action"],
            "resource": row["resource"],
            "outcome": row["outcome"],
            "details": row["details"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


def create_token(username: str, token_type: str = "access") -> str:
    user = _get_user(username)
    if user is None:
        raise ValueError("User not found")
    expiry_hours = settings.jwt_expiry_hours if token_type == "access" else 168
    now = datetime.now(timezone.utc)
    payload = {
        "sub": username,
        "role": user["role"],
        "type": token_type,
        "jti": uuid4().hex,
        "iat": int(now.timestamp()),
        "exp": now + timedelta(hours=expiry_hours),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str, expected_type: Optional[str] = None) -> Dict[str, str]:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    if expected_type and payload.get("type") not in {None, expected_type}:
        raise ValueError("Unexpected token type")
    return payload


def refresh_access_token(current_token: str) -> Dict[str, str]:
    payload = verify_token(current_token)
    username = payload.get("sub")
    if not username:
        raise ValueError("Invalid token")
    user = _get_user(username)
    if user is None:
        raise ValueError("Invalid token")
    new_token = create_token(username, token_type="access")
    record_audit_log(username, "token_refreshed", "auth", "success", "Access token refreshed")
    return {"token": new_token, "role": user["role"], "type": "access"}


def verify_otp(username: str, otp_code: str) -> Dict[str, str]:
    if not username or not otp_code:
        raise ValueError("Username and OTP are required")

    user = _get_user(username)
    if user is None:
        raise ValueError("Invalid username or OTP")
    if user.get("status") == "active":
        return {"username": username, "status": "active", "verified": True}

    stored_otp = (user.get("otp_code") or "").strip()
    expires_at = user.get("otp_expires_at")
    if not stored_otp or not expires_at:
        raise ValueError("No active OTP found for this user")

    try:
        expires = datetime.fromisoformat(expires_at)
    except (TypeError, ValueError) as exc:
        raise ValueError("OTP has expired") from exc

    if datetime.now(timezone.utc) > expires:
        raise ValueError("OTP has expired")

    if not hmac.compare_digest(stored_otp, str(otp_code).strip()):
        raise ValueError("Invalid username or OTP")

    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET status = ?, otp_code = NULL, otp_expires_at = NULL, updated_at = ? WHERE username = ?",
            ("active", datetime.now(timezone.utc).isoformat(), username),
        )

    record_audit_log(username, "otp_verified", "auth", "success", "OTP verification complete")
    return {"username": username, "status": "active", "verified": True}


def authenticate(username: str, password: str) -> Dict[str, str]:
    user = _get_user(username)
    if user is None:
        record_audit_log(username or "unknown", "login", "auth", "failure", "Invalid username or password")
        raise ValueError("Invalid username or password")

    if user.get("status") == "pending_verification":
        record_audit_log(username, "login", "auth", "failure", "Account pending verification")
        raise ValueError("Account is pending verification")
    if user.get("status") == "locked":
        record_audit_log(username, "login", "auth", "failure", "Account locked")
        raise ValueError("Invalid username or password")

    if not verify_password(password, user["password"]):
        attempts = (user.get("failed_login_attempts") or 0) + 1
        new_status = "locked" if attempts >= 5 else user.get("status", "active")
        with get_connection() as conn:
            conn.execute(
                "UPDATE users SET failed_login_attempts = ?, status = ?, updated_at = ? WHERE username = ?",
                (attempts, new_status, datetime.now(timezone.utc).isoformat(), username),
            )
        record_audit_log(username, "login", "auth", "failure", "Invalid username or password")
        if new_status == "locked":
            record_audit_log(username, "login", "auth", "failure", "Account locked after repeated failed attempts")
        raise ValueError("Invalid username or password")

    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET failed_login_attempts = 0, last_login_at = ?, updated_at = ? WHERE username = ?",
            (datetime.now(timezone.utc).isoformat(), datetime.now(timezone.utc).isoformat(), username),
        )

    token = create_token(username)
    record_audit_log(username, "login", "auth", "success", "JWT token issued")
    return {"token": token, "role": user["role"]}
