from __future__ import annotations

import base64
import hashlib
import hmac
import os
import smtplib
from email.message import EmailMessage
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
    region: str = "",
    area: str = "",
    primary_crop: str = "",
    land_size: str = "",
    water_source: str = "",
    farming_method: str = "",
    secondary_crops: str = "",
    tools: str = "",
    irrigation_type: str = "",
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
            INSERT INTO users (id, username, password, role, email, phone, full_name, village, region, area, primary_crop,
            land_size, water_source, farming_method, secondary_crops, tools, irrigation_type, status, otp_code, otp_expires_at,
            failed_login_attempts, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0, ?, ?)
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
                region,
                area,
                primary_crop,
                land_size,
                water_source,
                farming_method,
                secondary_crops,
                tools,
                irrigation_type,
                status,
                otp_code,
                otp_expires_at,
                datetime.now(timezone.utc).isoformat(),
                datetime.now(timezone.utc).isoformat(),
            ),
        )

    record_audit_log(username, "user_created", "users", "success", f"Created user with role {role} and status {status}")
    return {"username": username, "role": role, "status": status, "otp_code": otp_code}


def send_activation_email(email: str, username: str, otp_code: Optional[str]) -> bool:
    if not email or not otp_code or not settings.smtp_host or not settings.smtp_from_email:
        return False

    message = EmailMessage()
    message["Subject"] = "Digital Farming account activation"
    message["From"] = settings.smtp_from_email
    message["To"] = email
    message.set_content(
        f"Hello {username},\n\n"
        f"Your Digital Farming activation code is {otp_code}.\n"
        "This code expires in 10 minutes.\n\n"
        "If you did not create this account, ignore this email."
    )

    try:
        with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=15) as smtp:
            if settings.smtp_use_tls:
                smtp.starttls()
            if settings.smtp_username:
                smtp.login(settings.smtp_username, settings.smtp_password)
            smtp.send_message(message)
        record_audit_log(username, "activation_email_sent", "auth", "success", email)
        return True
    except (OSError, smtplib.SMTPException) as exc:
        record_audit_log(username, "activation_email_sent", "auth", "failure", str(exc)[:240])
        return False


def list_users(
    *,
    search: str = "",
    role: str = "",
    status: str = "",
    page: int = 1,
    page_size: int = 1000,
) -> Dict[str, object]:
    seed_default_users()
    page = max(1, page)
    page_size = min(1000, max(1, page_size))
    clauses = []
    params: List[object] = []
    if search.strip():
        term = f"%{search.strip().lower()}%"
        clauses.append("(LOWER(username) LIKE ? OR LOWER(full_name) LIKE ? OR LOWER(email) LIKE ? OR phone LIKE ?)")
        params.extend([term, term, term, term])
    if role.strip():
        clauses.append("role = ?")
        params.append(role.strip())
    if status.strip():
        clauses.append("status = ?")
        params.append(status.strip())
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    with get_connection() as conn:
        total = conn.execute(f"SELECT COUNT(*) FROM users{where}", params).fetchone()[0]
        rows = conn.execute(
            f"SELECT id, username, full_name, email, phone, role, status, created_at, last_login_at FROM users{where} ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (*params, page_size, (page - 1) * page_size),
        ).fetchall()
    return {
        "items": [dict(row) for row in rows],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": max(1, (total + page_size - 1) // page_size),
    }


def get_admin_user_detail(username: str) -> Dict[str, object]:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, username, full_name, email, phone, village, region, area, primary_crop, land_size, water_source, farming_method, secondary_crops, tools, irrigation_type, role, status, failed_login_attempts, created_at, updated_at, last_login_at FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    if row is None:
        raise ValueError("User not found")
    return dict(row)


def set_user_status(admin_username: str, username: str, action: str, reason: str = "") -> Dict[str, str]:
    allowed_actions = {"activate": "active", "reactivate": "active", "deactivate": "inactive"}
    if action not in allowed_actions:
        raise ValueError("Unsupported account action")
    if admin_username == username and action == "deactivate":
        raise ValueError("An admin cannot deactivate their own account")
    user = _get_user(username)
    if user is None:
        raise ValueError("User not found")
    new_status = allowed_actions[action]
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            "UPDATE users SET status = ?, failed_login_attempts = 0, otp_code = NULL, otp_expires_at = NULL, updated_at = ? WHERE username = ?",
            (new_status, now, username),
        )
    record_audit_log(admin_username, f"user_{action}", f"users/{username}", "success", reason or f"Account status set to {new_status}")
    return {"username": username, "status": new_status, "action": action}


def get_profile(username: str) -> Dict[str, str]:
    user = _get_user(username)
    if user is None:
        raise ValueError("User not found")
    return {
        "username": user["username"],
        "role": user["role"],
        "status": user.get("status", "active"),
        "full_name": user.get("full_name", ""),
        "village": user.get("village", ""),
        "region": user.get("region", ""),
        "area": user.get("area", ""),
        "primary_crop": user.get("primary_crop", ""),
        "land_size": user.get("land_size", ""),
        "water_source": user.get("water_source", ""),
        "farming_method": user.get("farming_method", ""),
        "secondary_crops": user.get("secondary_crops", ""),
        "tools": user.get("tools", ""),
        "irrigation_type": user.get("irrigation_type", ""),
    }


def update_profile(username: str, updates: Dict[str, Optional[str]]) -> Dict[str, str]:
    allowed_fields = {
        "full_name", "village", "region", "area", "primary_crop", "land_size",
        "water_source", "farming_method", "secondary_crops", "tools", "irrigation_type",
    }
    changes = {field: value for field, value in updates.items() if field in allowed_fields and value is not None}
    if not changes:
        raise ValueError("At least one profile field is required")
    if any(not isinstance(value, str) for value in changes.values()):
        raise ValueError("Profile fields must be strings")
    if _get_user(username) is None:
        raise ValueError("User not found")

    assignments = ", ".join(f"{field} = ?" for field in changes)
    values = [value.strip() for value in changes.values()]
    now = datetime.now(timezone.utc).isoformat()
    with get_connection() as conn:
        conn.execute(
            f"UPDATE users SET {assignments}, updated_at = ? WHERE username = ?",
            (*values, now, username),
        )

    record_audit_log(username, "profile_updated", "users", "success", f"Updated fields: {', '.join(changes)}")
    return get_profile(username)


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
                 SELECT id, username, password, role, status, otp_code, otp_expires_at, failed_login_attempts,
                   email, phone, full_name, village, region, area, primary_crop, land_size,
                     water_source, farming_method, secondary_crops, tools, irrigation_type,
                     created_at, updated_at, last_login_at
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
        "id": row["id"],
        "username": row["username"],
        "password": stored_password,
        "role": row["role"],
        "status": row["status"] or "active",
        "otp_code": row["otp_code"],
        "otp_expires_at": row["otp_expires_at"],
        "failed_login_attempts": row["failed_login_attempts"] or 0,
        "email": row["email"],
        "phone": row["phone"],
        "full_name": row["full_name"],
        "village": row["village"],
        "region": row["region"],
        "area": row["area"],
        "primary_crop": row["primary_crop"],
        "land_size": row["land_size"],
        "water_source": row["water_source"],
        "farming_method": row["farming_method"],
        "secondary_crops": row["secondary_crops"],
        "tools": row["tools"],
        "irrigation_type": row["irrigation_type"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "last_login_at": row["last_login_at"],
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
                "SELECT password, role, status FROM users WHERE username = ?",
                (username,),
            ).fetchone()
        if row is None:
            create_user(username, details["password"], details["role"])
            continue

        current_password = row["password"] or ""
        legacy_plaintext = not current_password.startswith(HASH_PREFIX)
        password_matches_default = current_password == details["password"]
        password_matches_hashed_default = bool(current_password) and verify_password(details["password"], current_password)

        if password_matches_default or password_matches_hashed_default:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE users SET password = ?, role = ?, status = CASE WHEN status = 'locked' THEN 'active' ELSE status END, failed_login_attempts = 0, updated_at = ? WHERE username = ?",
                    (hash_password(details["password"]), details["role"], datetime.now(timezone.utc).isoformat(), username),
                )
            continue

        if legacy_plaintext and password_matches_default:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE users SET password = ? WHERE username = ?",
                    (hash_password(details["password"]), username),
                )

        if row["role"] is None or row["role"] != details["role"]:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE users SET role = ? WHERE username = ?",
                    (details["role"], username),
                )

        if (row["status"] or "active") == "locked":
            with get_connection() as conn:
                conn.execute(
                    "UPDATE users SET status = ?, failed_login_attempts = 0 WHERE username = ?",
                    ("active", username),
                )

        if (row["status"] or "active") not in {"active", "locked", "inactive", "pending_verification"}:
            with get_connection() as conn:
                conn.execute(
                    "UPDATE users SET status = ? WHERE username = ?",
                    ("active", username),
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
    seed_default_users()
    user = _get_user(username)
    if user is None:
        record_audit_log(username or "unknown", "login", "auth", "failure", "Invalid username or password")
        raise ValueError("Invalid username or password")

    if user.get("status") == "pending_verification":
        record_audit_log(username, "login", "auth", "failure", "Account pending verification")
        raise ValueError("Account is pending verification")
    if user.get("status") == "inactive":
        record_audit_log(username, "login", "auth", "failure", "Account inactive")
        raise ValueError("Account is inactive")
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
