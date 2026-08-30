from __future__ import annotations

from datetime import datetime, timezone
from typing import List

from database import get_connection, init_db
from schemas import Farmer, Farm, MarketPrice, SoilTestRecord, WeatherAlert

init_db()


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


def list_farms(farmer_id: str | None = None) -> List[Farm]:
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


def list_soil_tests(farm_id: str | None = None) -> List[SoilTestRecord]:
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


def list_weather_alerts(village: str | None = None) -> List[WeatherAlert]:
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


def list_market_prices(crop_name: str | None = None) -> List[MarketPrice]:
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


seed_weather_alerts()
seed_market_data()
