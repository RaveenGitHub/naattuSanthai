from __future__ import annotations

from functools import wraps

from fastapi import HTTPException, Request

from security import verify_token

ROLE_PERMISSIONS = {
    "farmer": ["read:farmer", "read:weather", "read:market", "read:schemes"],
    "operator": ["read:farmer", "write:farmer", "write:soil_test", "read:market", "read:weather", "write:notifications"],
    "admin": ["read:farmer", "write:farmer", "write:soil_test", "write:weather", "read:market", "write:schemes"],
}

ROLE_HIERARCHY = {
    "farmer": {"farmer", "operator", "admin"},
    "operator": {"operator", "admin"},
    "admin": {"admin"},
}


def get_user_role(request: Request) -> str:
    authorization = request.headers.get("Authorization") or request.headers.get("authorization")
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization.split(" ", 1)[1].strip()
        try:
            payload = verify_token(token)
            role = str(payload.get("role", "")).lower()
            if role in ROLE_PERMISSIONS:
                return role
        except Exception:
            pass

    role = request.headers.get("X-User-Role") or request.headers.get("x-user-role") or "farmer"
    return str(role).lower()


def require_role(required_role: str):
    normalized_role = required_role.lower()

    def decorator(function):
        @wraps(function)
        async def wrapper(*args, **kwargs):
            request = args[0] if args and hasattr(args[0], "headers") else None
            if request is None:
                raise HTTPException(status_code=401, detail="Missing request context")

            role = get_user_role(request)
            allowed_roles = ROLE_HIERARCHY.get(normalized_role, {normalized_role})
            if normalized_role not in ROLE_PERMISSIONS or role not in ROLE_PERMISSIONS:
                raise HTTPException(status_code=403, detail="Role not allowed")
            if role not in allowed_roles:
                raise HTTPException(status_code=403, detail=f"{normalized_role.capitalize()} access required")
            return await function(*args, **kwargs)

        return wrapper

    return decorator
