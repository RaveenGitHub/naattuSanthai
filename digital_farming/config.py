from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    app_name: str = "Digital Farming Support Center"
    app_version: str = "0.2.0"
    debug: bool = False
    database_path: str = str(Path(__file__).resolve().parent.parent / "digital_farming.db")
    secret_key: str = "digital-farming-support-center-secret-key"
    jwt_algorithm: str = "HS256"
    jwt_expiry_hours: int = 12


settings = Settings()

__all__ = ["settings", "Settings"]
