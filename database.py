from __future__ import annotations

import os
import shutil
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from uuid import uuid4


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


def _ensure_user_verification_columns() -> None:
    with get_connection() as conn:
        columns = {row[1] for row in conn.execute("PRAGMA table_info(users)").fetchall()}
        if "email" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN email TEXT")
        if "phone" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
        if "full_name" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN full_name TEXT DEFAULT ''")
        if "village" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN village TEXT DEFAULT ''")
        if "status" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active'")
        if "otp_code" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN otp_code TEXT")
        if "otp_expires_at" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN otp_expires_at TEXT")
        if "failed_login_attempts" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN failed_login_attempts INTEGER NOT NULL DEFAULT 0")
        if "last_login_at" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN last_login_at TEXT")
        if "updated_at" not in columns:
            conn.execute("ALTER TABLE users ADD COLUMN updated_at TEXT")


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
            CREATE TABLE IF NOT EXISTS weather_forecasts (
                id TEXT PRIMARY KEY,
                region TEXT NOT NULL,
                period TEXT NOT NULL,
                forecast_date TEXT NOT NULL,
                temperature_c REAL NOT NULL,
                rainfall_mm REAL NOT NULL,
                humidity_pct REAL NOT NULL,
                wind_kmh REAL NOT NULL,
                summary_ta TEXT NOT NULL,
                advisory_ta TEXT NOT NULL,
                source_name TEXT NOT NULL,
                created_at TEXT NOT NULL
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
                email TEXT,
                phone TEXT,
                full_name TEXT DEFAULT '',
                status TEXT NOT NULL DEFAULT 'active',
                otp_code TEXT,
                otp_expires_at TEXT,
                failed_login_attempts INTEGER NOT NULL DEFAULT 0,
                last_login_at TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS government_scheme_updates (
                id TEXT PRIMARY KEY,
                title_ta TEXT NOT NULL,
                summary_ta TEXT NOT NULL,
                eligibility_ta TEXT NOT NULL,
                benefits_ta TEXT NOT NULL,
                apply_steps_ta TEXT NOT NULL,
                category TEXT NOT NULL,
                scheme_type TEXT NOT NULL,
                source_name TEXT NOT NULL,
                source_url TEXT NOT NULL,
                is_archived INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS migration_status (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS scheme_review_actions (
                id TEXT PRIMARY KEY,
                scheme_id TEXT NOT NULL,
                decision TEXT NOT NULL,
                reviewer TEXT NOT NULL,
                reason TEXT,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS fetch_history (
                id TEXT PRIMARY KEY,
                source_name TEXT NOT NULL,
                status TEXT NOT NULL,
                attempts INTEGER NOT NULL DEFAULT 1,
                retry_count INTEGER NOT NULL DEFAULT 0,
                error_message TEXT,
                created_at TEXT NOT NULL
            )
            """
        )

    _ensure_user_verification_columns()


BACKUP_DIRECTORY = Path(__file__).resolve().parent / "backups"
BACKUP_DIRECTORY.mkdir(parents=True, exist_ok=True)
BACKUP_POLICY = {
    "retention_days": 30,
    "max_backups": 10,
    "auto_prune_enabled": True,
}


def _list_backup_history() -> list[dict]:
    entries: list[dict] = []
    for backup_path in sorted(BACKUP_DIRECTORY.glob("*.db"), key=lambda item: item.stat().st_mtime, reverse=True):
        try:
            created_at = datetime.fromtimestamp(backup_path.stat().st_mtime, tz=timezone.utc)
        except (OSError, ValueError):
            created_at = datetime.now(timezone.utc)
        entries.append(
            {
                "name": backup_path.name,
                "path": str(backup_path),
                "created_at": created_at.isoformat(),
                "size_bytes": backup_path.stat().st_size,
            }
        )
    return entries


def _prune_old_backups() -> None:
    if not BACKUP_POLICY["auto_prune_enabled"]:
        return

    cutoff = datetime.now(timezone.utc) - timedelta(days=BACKUP_POLICY["retention_days"])
    for backup_path in sorted(BACKUP_DIRECTORY.glob("*.db"), key=lambda item: item.stat().st_mtime):
        file_time = datetime.fromtimestamp(backup_path.stat().st_mtime, tz=timezone.utc)
        if file_time < cutoff:
            backup_path.unlink(missing_ok=True)

    remaining = sorted(BACKUP_DIRECTORY.glob("*.db"), key=lambda item: item.stat().st_mtime)
    while len(remaining) > BACKUP_POLICY["max_backups"]:
        oldest = remaining.pop(0)
        oldest.unlink(missing_ok=True)


def create_db_backup(label: str | None = None) -> Path:
    source_path = _resolve_db_path()
    BACKUP_DIRECTORY.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    clean_label = (label or "db-backup").strip().lower().replace(" ", "-")
    backup_path = BACKUP_DIRECTORY / f"{clean_label}-{timestamp}.db"

    if source_path.exists():
        shutil.copy2(source_path, backup_path)
    else:
        source_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.touch()
        shutil.copy2(source_path, backup_path)

    _prune_old_backups()
    return backup_path


def record_migration_status(name: str, status: str, details: str = "") -> dict:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS migration_status (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )

        timestamp = datetime.now(timezone.utc).isoformat()
        existing = conn.execute(
            "SELECT id, created_at FROM migration_status WHERE name = ?",
            (name,),
        ).fetchone()

        if existing:
            record_id = existing["id"]
            created_at = existing["created_at"]
            conn.execute(
                "UPDATE migration_status SET status = ?, details = ?, updated_at = ? WHERE id = ?",
                (status, details, timestamp, record_id),
            )
        else:
            record_id = uuid4().hex
            created_at = timestamp
            conn.execute(
                "INSERT INTO migration_status (id, name, status, details, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (record_id, name, status, details, timestamp, timestamp),
            )

        row = conn.execute(
            "SELECT id, name, status, details, created_at, updated_at FROM migration_status WHERE id = ?",
            (record_id,),
        ).fetchone()
        return dict(row)


def get_migration_status() -> dict:
    backup_dir = BACKUP_DIRECTORY
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_history = _list_backup_history()
    latest_backup = backup_history[0] if backup_history else None

    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS migration_status (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL,
                details TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        rows = conn.execute(
            "SELECT id, name, status, details, created_at, updated_at FROM migration_status ORDER BY created_at DESC"
        ).fetchall()

    return {
        "backup_directory": backup_dir,
        "backup_policy": {
            "retention_days": BACKUP_POLICY["retention_days"],
            "max_backups": BACKUP_POLICY["max_backups"],
            "auto_prune_enabled": BACKUP_POLICY["auto_prune_enabled"],
        },
        "backup_history": backup_history,
        "latest_backup": latest_backup,
        "migrations": [dict(row) for row in rows],
    }
