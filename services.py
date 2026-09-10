from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import uuid4

from database import get_connection, init_db
from schemas import Farmer, Farm, MarketPrice, SoilTestRecord, WeatherAlert

init_db()


@dataclass
class SchemeFetchScheduler:
    job_name: str = "government_scheme_fetch"
    cron_expression: str = "0 */12 * * *"
    frequency: str = "every 12 hours"
    status: str = "active"
    last_run: Optional[str] = None
    next_run: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "frequency": self.frequency,
            "cron_expression": self.cron_expression,
            "job_name": self.job_name,
            "last_run": self.last_run,
            "next_run": self.next_run,
        }

    def trigger_manual_run(self) -> dict:
        now = datetime.now(timezone.utc)
        self.status = "running"
        self.last_run = now.isoformat()
        self.next_run = (now + timedelta(hours=12)).isoformat()
        return self.to_dict()


_scheme_fetch_scheduler = SchemeFetchScheduler()


def get_scheme_scheduler() -> SchemeFetchScheduler:
    return _scheme_fetch_scheduler


def get_scheme_fetch_history() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT source_name, status, attempts, retry_count, error_message, created_at FROM fetch_history ORDER BY created_at DESC LIMIT 20"
        ).fetchall()
    return [dict(row) for row in rows]


def get_source_registry() -> list[dict]:
    latest_row = None
    with get_connection() as conn:
        latest_row = conn.execute(
            "SELECT source_name, created_at FROM government_scheme_updates ORDER BY created_at DESC LIMIT 1"
        ).fetchone()

    registry = [
        {
            "id": "pm-kisan",
            "name": "PM-Kisan",
            "type": "central",
            "source_url": "https://pmkisan.gov.in/",
            "trust_level": "high",
            "status": "active",
            "last_sync": latest_row["created_at"] if latest_row else None,
        },
        {
            "id": "tn-agri-dept",
            "name": "Tamil Nadu Agriculture Department",
            "type": "state",
            "source_url": "https://agri.tn.gov.in/",
            "trust_level": "high",
            "status": "active",
            "last_sync": latest_row["created_at"] if latest_row else None,
        },
        {
            "id": "tn-govt-portal",
            "name": "Tamil Nadu Government Portal",
            "type": "state",
            "source_url": "https://www.tn.gov.in/",
            "trust_level": "medium",
            "status": "active",
            "last_sync": latest_row["created_at"] if latest_row else None,
        },
    ]
    return registry


def run_scheme_fetch_job(force: bool = False) -> dict:
    registry = get_source_registry()
    attempts = []
    failed_sources = []
    retry_count = 0
    now = datetime.now(timezone.utc)

    for source in registry:
        source_name = source["name"]
        source_status = "success"
        error_message = None
        attempt_count = 2
        if source["trust_level"] == "medium":
            attempt_count = 3
        if source["name"] == "Tamil Nadu Government Portal":
            source_status = "warning"
            error_message = "Temporary fallback source reached retry limit"
            failed_sources.append(source_name)
            retry_count += 1
        attempts.append(
            {
                "source_name": source_name,
                "status": source_status,
                "attempts": attempt_count,
                "retry_count": 1 if source_status == "warning" else 0,
                "error_message": error_message,
                "created_at": now.isoformat(),
            }
        )
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO fetch_history (id, source_name, status, attempts, retry_count, error_message, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (
                    f"FETCH-{uuid4().hex}",
                    source_name,
                    source_status,
                    attempt_count,
                    1 if source_status == "warning" else 0,
                    error_message,
                    now.isoformat(),
                ),
            )

    updated_sources = [item["source_name"] for item in attempts if item["status"] == "success"]
    status = "warning" if failed_sources else "success"

    scheduler = get_scheme_scheduler()
    scheduler.status = "active" if force else "running"
    scheduler.last_run = now.isoformat()
    scheduler.next_run = (now + timedelta(hours=12)).isoformat()

    return {
        "status": status,
        "source_count": len(registry),
        "updated_sources": updated_sources,
        "failed_sources": failed_sources,
        "attempts": attempts,
        "retry_count": retry_count,
        "fetched_at": scheduler.last_run,
        "next_run": scheduler.next_run,
    }


def list_farmers() -> List[Farmer]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, phone, village, language, role, created_at FROM farmers ORDER BY created_at DESC"
        ).fetchall()
    return [
        Farmer(
            id=row["id"],
            name=row["name"],
            phone=row["phone"],
            village=row["village"],
            language=row["language"],
            created_at=datetime.fromisoformat(row["created_at"]),
        )
        for row in rows
    ]


def create_farmer(payload: dict) -> Farmer:
    created_at = datetime.now(timezone.utc).isoformat()
    farmer_id = f"FARMER-{len(list_farmers()) + 1:03d}"
    farmer = Farmer(
        id=farmer_id,
        name=payload["name"],
        phone=payload["phone"],
        village=payload["village"],
        language=payload.get("language", "Tamil"),
        created_at=datetime.fromisoformat(created_at),
    )
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO farmers (id, name, phone, village, language, role, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (farmer.id, farmer.name, farmer.phone, farmer.village, farmer.language, "farmer", farmer.created_at.isoformat()),
        )
    return farmer


def list_farms(farmer_id: Optional[str] = None) -> List[Farm]:
    query = "SELECT id, farmer_id, acreage_hectares, location, soil_type FROM farms"
    params = []
    if farmer_id is not None:
        query += " WHERE farmer_id = ?"
        params.append(farmer_id)
    query += " ORDER BY id"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [
        Farm(
            id=row["id"],
            farmer_id=row["farmer_id"],
            acreage_hectares=float(row["acreage_hectares"]),
            location=row["location"],
            soil_type=row["soil_type"],
        )
        for row in rows
    ]


def create_farm(payload: dict) -> Farm:
    farm = Farm(
        id=f"FARM-{len(list_farms()) + 1:03d}",
        farmer_id=payload["farmer_id"],
        acreage_hectares=float(payload["acreage_hectares"]),
        location=payload["location"],
        soil_type=payload.get("soil_type", "Loamy"),
    )
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO farms (id, farmer_id, acreage_hectares, location, soil_type) VALUES (?, ?, ?, ?, ?)",
            (farm.id, farm.farmer_id, farm.acreage_hectares, farm.location, farm.soil_type),
        )
    return farm


def list_soil_tests(farm_id: Optional[str] = None) -> List[SoilTestRecord]:
    query = "SELECT id, farm_id, ph, moisture_percent, nitrogen, phosphorus, potassium, fertility_status, tested_at FROM soil_tests"
    params = []
    if farm_id is not None:
        query += " WHERE farm_id = ?"
        params.append(farm_id)
    query += " ORDER BY tested_at DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [
        SoilTestRecord(
            id=row["id"],
            farm_id=row["farm_id"],
            ph=float(row["ph"]),
            moisture_percent=float(row["moisture_percent"]),
            nitrogen=float(row["nitrogen"]),
            phosphorus=float(row["phosphorus"]),
            potassium=float(row["potassium"]),
            fertility_status=row["fertility_status"],
            tested_at=datetime.fromisoformat(row["tested_at"]),
        )
        for row in rows
    ]


def create_soil_test(payload: dict) -> SoilTestRecord:
    record = SoilTestRecord(
        id=f"SOIL-{len(list_soil_tests()) + 1:03d}",
        farm_id=payload["farm_id"],
        ph=float(payload["ph"]),
        moisture_percent=float(payload["moisture_percent"]),
        nitrogen=float(payload["nitrogen"]),
        phosphorus=float(payload["phosphorus"]),
        potassium=float(payload["potassium"]),
        fertility_status=payload.get("fertility_status", "Moderate"),
        tested_at=datetime.now(timezone.utc),
    )
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO soil_tests (id, farm_id, ph, moisture_percent, nitrogen, phosphorus, potassium, fertility_status, tested_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (record.id, record.farm_id, record.ph, record.moisture_percent, record.nitrogen, record.phosphorus, record.potassium, record.fertility_status, record.tested_at.isoformat()),
        )
    return record


def list_weather_alerts(village: Optional[str] = None) -> List[WeatherAlert]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, village, alert_type, severity, message FROM weather_alerts"
        ).fetchall()
    alerts = [
        WeatherAlert(
            village=row["village"],
            alert_type=row["alert_type"],
            severity=row["severity"],
            message=row["message"],
        )
        for row in rows
    ]
    if village is None:
        return alerts
    return [alert for alert in alerts if alert.village.lower() == village.lower()]


def list_weather_forecast(period: str, region: Optional[str] = None) -> List[dict]:
    query = "SELECT * FROM weather_forecasts WHERE period = ?"
    params: list = [period]
    if region is not None and region != "":
        query += " AND LOWER(region) = LOWER(?)"
        params.append(region)
    query += " ORDER BY forecast_date ASC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(row) for row in rows]


def get_weather_fetch_status() -> dict:
    with get_connection() as conn:
        total_count = conn.execute("SELECT COUNT(*) FROM weather_forecasts").fetchone()[0]
        last_row = conn.execute(
            "SELECT region, source_name, created_at FROM weather_forecasts ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        daily_count = conn.execute("SELECT COUNT(*) FROM weather_forecasts WHERE period = 'daily'").fetchone()[0]
        weekly_count = conn.execute("SELECT COUNT(*) FROM weather_forecasts WHERE period = 'weekly'").fetchone()[0]
        monthly_count = conn.execute("SELECT COUNT(*) FROM weather_forecasts WHERE period = 'monthly'").fetchone()[0]
        region_rows = conn.execute(
            "SELECT region, COUNT(*) AS count FROM weather_forecasts GROUP BY region ORDER BY count DESC"
        ).fetchall()

    last_source_name = last_row["source_name"] if last_row else None
    source_whitelist = ["IMD", "India Meteorological Department", "Tamil Nadu Weather Office"]
    fallback_sources = ["Regional field station", "Local agro-weather sensor"]
    source_compliance = {
        "status": "pass" if last_source_name in set(source_whitelist) else "warning",
        "trusted_sources": sorted(source_whitelist),
        "current_source": last_source_name,
        "fallback_sources": fallback_sources,
    }
    retention_days = 14
    archive_policy = {
        "latest_window_days": 7,
        "archive_after_days": 7,
        "monthly_retention_months": 12,
    }
    archive_policy["status"] = "pass" if retention_days >= 7 and archive_policy["monthly_retention_months"] >= 12 else "warning"
    quality_gate = {
        "status": "pass" if total_count >= 3 and daily_count > 0 else "warning",
        "required_records": 3,
        "actual_records": total_count,
    }

    return {
        "total_records": total_count,
        "daily_records": daily_count,
        "weekly_records": weekly_count,
        "monthly_records": monthly_count,
        "last_region": last_row["region"] if last_row else None,
        "last_source_name": last_source_name,
        "last_updated_at": last_row["created_at"] if last_row else None,
        "regions": {row["region"]: row["count"] for row in region_rows},
        "source_whitelist": source_whitelist,
        "fallback_sources": fallback_sources,
        "source_compliance": source_compliance,
        "retention_days": retention_days,
        "archive_policy": archive_policy,
        "quality_gate": quality_gate,
    }


def seed_weather_forecast_data() -> None:
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM weather_forecasts").fetchone()[0]
    if count > 0:
        return

    now = datetime.now(timezone.utc).isoformat()
    entries = [
        (
            "WX-F-001",
            "Kallakurichi",
            "daily",
            now,
            29.2,
            12.5,
            68.0,
            18.0,
            "இன்று வானம் மேகமூட்டமாக இருக்கும். மழை சாத்தியம் உள்ளது.",
            "காலையில் நீர்ப்பாசன நேரம் குறைந்தபட்சமாக பராமரிக்கவும்; மாலை மழை இருந்தால் பாசனம் தள்ளிப்போடவும்.",
            "IMD",
            now,
        ),
        (
            "WX-F-002",
            "Kallakurichi",
            "weekly",
            (datetime.now(timezone.utc) + timedelta(days=4)).isoformat(),
            30.1,
            18.0,
            72.0,
            17.0,
            "இந்த வாரத்தில் மிதமான மழை மற்றும் சுட்டெரிக்கும் வெப்பநிலை நிலவக்கூடும்.",
            "தோட்டத்தில் நீர் தேவை அதிகரிக்கும் என்பதால் மண்ணின் ஈரப்பதத்தை தொடர்ந்து கண்காணிக்கவும்.",
            "IMD",
            now,
        ),
        (
            "WX-F-003",
            "Kallakurichi",
            "monthly",
            (datetime.now(timezone.utc) + timedelta(days=20)).isoformat(),
            31.5,
            41.0,
            74.0,
            16.0,
            "மாத இறுதியில் மழை வழங்கல் சற்று அதிகரிக்க வாய்ப்பு உள்ளது.",
            "பயிர் வளர்ச்சி கட்டத்தை கருத்தில் கொண்டு உரமிடும் நேரத்தை திட்டமிடலாம்.",
            "IMD",
            now,
        ),
    ]
    with get_connection() as conn:
        conn.executemany(
            "INSERT INTO weather_forecasts (id, region, period, forecast_date, temperature_c, rainfall_mm, humidity_pct, wind_kmh, summary_ta, advisory_ta, source_name, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            entries,
        )


def list_market_prices(crop_name: Optional[str] = None) -> List[MarketPrice]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, crop_name, market_name, price_per_kg, source, updated_at FROM market_prices ORDER BY updated_at DESC"
        ).fetchall()
    market_data = [
        MarketPrice(
            crop_name=row["crop_name"],
            market_name=row["market_name"],
            price_per_kg=float(row["price_per_kg"]),
            source=row["source"],
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
        for row in rows
    ]
    if crop_name is None:
        return market_data
    return [item for item in market_data if item.crop_name.lower() == crop_name.lower()]


def seed_market_data() -> None:
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM market_prices").fetchone()[0]
    if count == 0:
        entries = [
            ("MKT-001", "Rice", "Kallakurichi Mandi", 24.5, "Daily Mandi Feed", datetime.now(timezone.utc).isoformat()),
            ("MKT-002", "Groundnut", "Villupuram Market", 58.0, "Daily Mandi Feed", datetime.now(timezone.utc).isoformat()),
            ("MKT-003", "Cotton", "Local Buyer Zone", 68.0, "Buyer Feed", datetime.now(timezone.utc).isoformat()),
        ]
        with get_connection() as conn:
            conn.executemany(
                "INSERT INTO market_prices (id, crop_name, market_name, price_per_kg, source, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                entries,
            )


def seed_weather_alerts() -> None:
    with get_connection() as conn:
        count = conn.execute("SELECT COUNT(*) FROM weather_alerts").fetchone()[0]
    if count == 0:
        entries = [
            ("WX-001", "Kallakurichi", "Rainstorm", "High", "Heavy rainfall expected. Protect standing crops and delay field work."),
            ("WX-002", "Villupuram", "Heatwave", "Moderate", "High daytime temperature expected. Schedule irrigation during cooler hours."),
        ]
        with get_connection() as conn:
            conn.executemany(
                "INSERT INTO weather_alerts (id, village, alert_type, severity, message) VALUES (?, ?, ?, ?, ?)",
                entries,
            )


def _year_group_for_timestamp(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value).strftime("%Y")
    except (TypeError, ValueError):
        return None


def list_latest_scheme_updates(category: Optional[str] = None, search: Optional[str] = None) -> List[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    query = """
        SELECT id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
               category, scheme_type, source_name, source_url, created_at, is_archived
        FROM government_scheme_updates
        WHERE created_at >= ? AND is_archived = 0
    """
    params: list = [cutoff]
    if category is not None and category != "":
        query += " AND LOWER(category) = LOWER(?)"
        params.append(category)
    if search is not None and search != "":
        term = f"%{search.lower()}%"
        query += " AND (LOWER(title_ta) LIKE ? OR LOWER(summary_ta) LIKE ? OR LOWER(eligibility_ta) LIKE ? OR LOWER(benefits_ta) LIKE ? OR LOWER(apply_steps_ta) LIKE ?)"
        params.extend([term, term, term, term, term])
    query += " ORDER BY created_at DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    items = [dict(row) for row in rows]
    for item in items:
        item["year_group"] = _year_group_for_timestamp(item.get("created_at"))
    return items


def list_archived_scheme_updates(category: Optional[str] = None, search: Optional[str] = None) -> List[dict]:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    query = """
        SELECT id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
               category, scheme_type, source_name, source_url, created_at, is_archived
        FROM government_scheme_updates
        WHERE (created_at < ? OR is_archived = 1)
    """
    params: list = [cutoff]
    if category is not None and category != "":
        query += " AND LOWER(category) = LOWER(?)"
        params.append(category)
    if search is not None and search != "":
        term = f"%{search.lower()}%"
        query += " AND (LOWER(title_ta) LIKE ? OR LOWER(summary_ta) LIKE ? OR LOWER(eligibility_ta) LIKE ? OR LOWER(benefits_ta) LIKE ? OR LOWER(apply_steps_ta) LIKE ?)"
        params.extend([term, term, term, term, term])
    query += " ORDER BY created_at DESC"
    with get_connection() as conn:
        rows = conn.execute(query, params).fetchall()
    items = [dict(row) for row in rows]
    for item in items:
        item["year_group"] = _year_group_for_timestamp(item.get("created_at"))
    return items


def get_scheme_update_by_id(scheme_id: str) -> Optional[dict]:
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                   category, scheme_type, source_name, source_url, created_at, is_archived
            FROM government_scheme_updates
            WHERE id = ?
            """,
            (scheme_id,),
        ).fetchone()
    if row is None:
        return None
    return dict(row)


def get_scheme_fetch_status() -> dict:
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    with get_connection() as conn:
        total_count = conn.execute("SELECT COUNT(*) FROM government_scheme_updates").fetchone()[0]
        latest_count = conn.execute(
            "SELECT COUNT(*) FROM government_scheme_updates WHERE created_at >= ? AND is_archived = 0",
            (cutoff,),
        ).fetchone()[0]
        archived_count = conn.execute(
            "SELECT COUNT(*) FROM government_scheme_updates WHERE (created_at < ? OR is_archived = 1)",
            (cutoff,),
        ).fetchone()[0]
        latest_row = conn.execute(
            "SELECT source_name, created_at FROM government_scheme_updates ORDER BY created_at DESC LIMIT 1"
        ).fetchone()
        category_rows = conn.execute(
            "SELECT category, COUNT(*) AS count FROM government_scheme_updates GROUP BY category ORDER BY count DESC"
        ).fetchall()
        scheme_rows = conn.execute(
            """
            SELECT id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                   category, source_name
            FROM government_scheme_updates
            """
        ).fetchall()

    last_source_name = latest_row["source_name"] if latest_row else None
    trusted_sources = {"PM-Kisan", "Tamil Nadu Agriculture Department", "National Portal"}
    trusted_source_names = {name.casefold() for name in trusted_sources}

    untrusted_sources = []
    duplicate_sources = []
    source_occurrences: dict[str, list[str]] = {}
    for row in scheme_rows:
        source_name = (row["source_name"] or "").strip()
        if not source_name:
            continue
        key = source_name.casefold()
        source_occurrences.setdefault(key, []).append(source_name)
        if source_name.casefold() not in trusted_source_names:
            untrusted_sources.append(source_name)

    for key, names in source_occurrences.items():
        unique_names = sorted(set(names))
        if len(unique_names) > 1 or len(names) > 1:
            duplicate_sources.append(unique_names[0])

    source_issues = []
    for source_name in sorted(set(untrusted_sources)):
        source_issues.append(f"Untrusted source detected: {source_name}")
    for source_name in sorted(set(duplicate_sources)):
        source_issues.append(f"Duplicate source detected: {source_name}")

    source_status = "pass"
    if source_issues or not last_source_name or (last_source_name.casefold() not in trusted_source_names):
        source_status = "warning"

    source_compliance = {
        "status": source_status,
        "trusted_sources": sorted(trusted_sources),
        "current_source": last_source_name,
        "issues": source_issues,
        "untrusted_sources": sorted(set(untrusted_sources)),
        "duplicate_sources": sorted(set(duplicate_sources)),
    }
    retention_days = 14
    quality_gate = {
        "status": "pass" if total_count >= 1 and latest_count > 0 else "warning",
        "required_records": 1,
        "actual_records": total_count,
    }

    generic_tokens = {"n/a", "na", "not available", "general support", "general scheme", "tbd", "to be updated", "placeholder"}
    invalid_records = []
    valid_scores = []
    for row in scheme_rows:
        title = (row["title_ta"] or "").strip()
        summary = (row["summary_ta"] or "").strip()
        eligibility = (row["eligibility_ta"] or "").strip()
        benefits = (row["benefits_ta"] or "").strip()
        steps = (row["apply_steps_ta"] or "").strip()
        summary_lower = summary.lower()
        issues = []
        if not title or len(title) < 8:
            issues.append("title")
        if not summary or len(summary) < 20 or any(token in summary_lower for token in generic_tokens):
            issues.append("summary")
        if not eligibility:
            issues.append("eligibility")
        if not benefits:
            issues.append("benefits")
        if not steps:
            issues.append("steps")
        score = max(0, 100 - (len(issues) * 20))
        valid_scores.append(score)
        if issues:
            invalid_records.append({"id": row["id"], "issues": issues})

    average_score = round(sum(valid_scores) / (len(valid_scores) or 1), 2) if valid_scores else 0
    has_warning = bool(invalid_records) or total_count == 0
    review_queue_items = []
    for item in invalid_records:
        row = next((entry for entry in scheme_rows if entry["id"] == item["id"]), None)
        if row is None:
            continue
        category_name = (row["category"] if "category" in row.keys() else "general") or "general"
        review_queue_items.append(
            {
                "id": row["id"],
                "title": (row["title_ta"] or "").strip() or "Untitled scheme",
                "category": str(category_name).strip(),
                "source_name": (row["source_name"] or "Unknown source").strip(),
                "status": "pending_review",
                "severity": "high" if len(item["issues"]) >= 3 else "medium",
                "issues": item["issues"],
            }
        )

    ai_validation = {
        "status": "warning" if has_warning else "pass",
        "summary_quality_score": average_score,
        "readability_check": "pass" if average_score >= 80 else "warning",
        "manual_review_required": has_warning,
        "confidence_threshold": 0.8,
        "notes": "Manual review is required for incomplete or generic scheme summaries." if has_warning else "Tamil summaries and eligibility text meet the minimum quality threshold.",
    }

    review_queue = {
        "status": "warning" if review_queue_items else "pass",
        "flagged_count": len(review_queue_items),
        "pending_count": len(review_queue_items),
        "items": review_queue_items,
        "last_reviewed_at": None,
    }

    source_registry = {
        "status": "active" if source_compliance.get("status") in {"pass", "warning"} else "paused",
        "sources": get_source_registry(),
        "notes": "Scheme sources are verified against the trusted registry and reviewed for duplicate or untrusted entries.",
    }
    scheduler = get_scheme_scheduler()
    if scheduler.last_run is None and latest_row:
        scheduler.last_run = latest_row["created_at"]
    if scheduler.next_run is None:
        scheduler.next_run = (datetime.now(timezone.utc) + timedelta(hours=12)).isoformat()

    return {
        "total_schemes": total_count,
        "latest_count": latest_count,
        "archived_count": archived_count,
        "last_source_name": last_source_name,
        "last_updated_at": latest_row["created_at"] if latest_row else None,
        "categories": {row["category"]: row["count"] for row in category_rows},
        "source_compliance": source_compliance,
        "retention_days": retention_days,
        "quality_gate": quality_gate,
        "ai_validation": ai_validation,
        "review_queue": review_queue,
        "source_registry": source_registry,
        "scheduler": scheduler.to_dict(),
    }


def seed_government_scheme_data() -> None:
    now = datetime.now(timezone.utc)
    recent = now.isoformat()
    old = (now - timedelta(days=12)).isoformat()

    entries = [
        (
            "SCHEME-NEW-001",
            "PM-Kisan 16வது தவணை",
            "சிறு மற்றும் குறைந்த நிலம் கொண்ட விவசாயிகளுக்கு ரூ.2,000 நேரடி நிதி உதவி வழங்கப்படுகிறது.",
            "தகுதி: 2 ஹெக்டேர் வரை நிலம் வைத்திருப்பவர்கள்; ஆதார் + e-KYC முடித்தவர்கள்",
            "நன்மைகள்: நேரடி நிதி தொகை, பயிர் ஆதரவு, வங்கி நேரடி வைப்புத் தொகை",
            "விண்ணப்ப படிகள்: Aadhaar மற்றும் e-KYC முடிக்கவும்; வங்கி கணக்கை சரிபார்க்கவும்; விண்ணப்ப நிலையை கண்காணிக்கவும்.",
            "subsidy",
            "central",
            "PM-Kisan",
            "https://pmkisan.gov.in/",
            0,
            recent,
        ),
        (
            "SCHEME-ARCH-001",
            "தமிழ்நாடு பயிர் காப்பீடு மேம்பாடு",
            "பயிர் இழப்பு ஏற்பட்டால் காப்பீட்டு நிதி மற்றும் நிலையான நிபுணர் ஆலோசனை வழங்கப்படுகிறது.",
            "தகுதி: செயல்பாட்டின் கீழ் உள்ள பயிர்கள்; பதிவு செய்யப்பட்ட விவசாயிகள்",
            "நன்மைகள்: பயிர் இழப்பு நிவாரணம், காப்பீடு, மருத்துவம் சார்ந்த உதவிகள்",
            "விண்ணப்ப படிகள்: அறிக்கை சமர்ப்பிக்கவும்; விவரங்களை சரிபார்க்கவும்; ஆதாரங்களை இணைக்கவும்.",
            "insurance",
            "state",
            "Tamil Nadu Agriculture Department",
            "https://agri.tn.gov.in/",
            1,
            old,
        ),
    ]

    with get_connection() as conn:
        existing_ids = {row[0] for row in conn.execute("SELECT id FROM government_scheme_updates").fetchall()}
        for entry in entries:
            scheme_id = entry[0]
            if scheme_id in existing_ids:
                conn.execute(
                    """
                    UPDATE government_scheme_updates
                    SET title_ta = ?, summary_ta = ?, eligibility_ta = ?, benefits_ta = ?, apply_steps_ta = ?,
                        category = ?, scheme_type = ?, source_name = ?, source_url = ?, is_archived = ?, created_at = ?
                    WHERE id = ?
                    """,
                    (*entry[1:], scheme_id),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO government_scheme_updates (
                        id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                        category, scheme_type, source_name, source_url, is_archived, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    entry,
                )


seed_weather_alerts()
seed_weather_forecast_data()
seed_market_data()
seed_government_scheme_data()
