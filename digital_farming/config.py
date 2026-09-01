from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _get_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@dataclass(frozen=True)
class Settings:
    app_name: str = os.getenv("APP_NAME", "Digital Farming Support Center")
    app_version: str = os.getenv("APP_VERSION", "0.2.0")
    app_env: str = os.getenv("APP_ENV", "development")
    debug: bool = _get_bool("APP_DEBUG", False)
    port: int = _get_int("PORT", 8000)
    database_path: str = os.getenv("DATABASE_PATH", str(Path(__file__).resolve().parent.parent / "digital_farming.db"))
    secret_key: str = os.getenv("SECRET_KEY", "digital-farming-support-center-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiry_hours: int = _get_int("JWT_EXPIRY_HOURS", 12)


settings = Settings()

__all__ = ["settings", "Settings"]
