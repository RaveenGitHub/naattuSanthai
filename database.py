from __future__ import annotations

import os
import sqlite3
from pathlib import Path


def _resolve_db_path() -> Path:
    configured_path = os.getenv("DATABASE_PATH")
    if configured_path:
        return Path(configured_path).expanduser()
    return Path(__file__).resolve().with_name("digital_farming.db")


DB_PATH = _resolve_db_path()
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection() -> sqlite3.Connection:
    resolved_path = _resolve_db_path()
    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS farmers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                village TEXT NOT NULL,
                language TEXT DEFAULT 'Tamil',
                role TEXT DEFAULT 'farmer',
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS farms (
                id TEXT PRIMARY KEY,
                farmer_id TEXT NOT NULL,
                acreage_hectares REAL NOT NULL,
                location TEXT NOT NULL,
                soil_type TEXT DEFAULT 'Loamy'
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS soil_tests (
                id TEXT PRIMARY KEY,
                farm_id TEXT NOT NULL,
                ph REAL NOT NULL,
                moisture_percent REAL NOT NULL,
                nitrogen REAL NOT NULL,
                phosphorus REAL NOT NULL,
                potassium REAL NOT NULL,
                fertility_status TEXT NOT NULL,
                tested_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS weather_alerts (
                id TEXT PRIMARY KEY,
                village TEXT NOT NULL,
                alert_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                message TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS market_prices (
                id TEXT PRIMARY KEY,
                crop_name TEXT NOT NULL,
                market_name TEXT NOT NULL,
                price_per_kg REAL NOT NULL,
                source TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS diagnosis_records (
                id TEXT PRIMARY KEY,
                crop_type TEXT NOT NULL,
                image_url TEXT NOT NULL,
                diagnosis TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                notes TEXT,
                confidence TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_logs (
                id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                outcome TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
