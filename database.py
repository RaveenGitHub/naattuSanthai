from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).with_name("digital_farming.db")


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
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
