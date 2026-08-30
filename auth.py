from __future__ import annotations

from fastapi import HTTPException, Request


ROLE_PERMISSIONS = {
    "farmer": ["read:farmer", "read:weather", "read:market", "read:schemes"],
    "operator": ["read:farmer", "write:farmer", "write:soil_test", "read:market", "read:weather", "write:notifications"],
    "admin": ["read:farmer", "write:farmer", "write:soil_test", "write:weather", "read:market", "write:schemes"],
}


def get_user_role(request: Request) -> str:
    role = request.headers.get("X-User-Role", "farmer")
    return role.lower()


def require_role(required_role: str):
    def decorator(function):
        async def wrapper(*args, **kwargs):
            request = args[0] if args and hasattr(args[0], "headers") else None
            if request is None:
                raise HTTPException(status_code=401, detail="Missing request context")
            role = get_user_role(request)
            if required_role not in ROLE_PERMISSIONS or role not in ROLE_PERMISSIONS:
                raise HTTPException(status_code=403, detail="Role not allowed")
            if required_role == "admin" and role != "admin":
                raise HTTPException(status_code=403, detail="Admin access required")
            return await function(*args, **kwargs)

        return wrapper

    return decorator
