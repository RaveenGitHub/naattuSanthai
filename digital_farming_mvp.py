"""Minimal MVP backend blueprint for the Digital Farming Support Center."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class Farmer:
    farmer_id: str
    name: str
    phone: str
    village: str
    language: str = "Tamil"


@dataclass
class Farm:
    farm_id: str
    farmer_id: str
    acreage_hectares: float
    location: str
    soil_type: str = "Loamy"


@dataclass
class SoilTestRecord:
    soil_test_id: str
    farm_id: str
    ph: float
    moisture_percent: float
    nitrogen: float
    phosphorus: float
    potassium: float
    fertility_status: str = "Moderate"


@dataclass
class MarketPrice:
    crop_name: str
    market_name: str
    price_per_kg: float
    source: str = "Mandi Feed"


@dataclass
class AdvisoryRecommendation:
    recommendation_id: str
    crop_name: str
    recommendation_text: str
    confidence_score: float
    created_by: str = "Advisor Engine"


class AdvisoryService:
    @staticmethod
    def create_recommendation(soil: SoilTestRecord, crop_hint: str = "Rice") -> AdvisoryRecommendation:
        if soil.ph < 6.0:
            guidance = "Add lime and prefer pH-balancing amendments before sowing."
        elif soil.moisture_percent < 35:
            guidance = "Irrigation should be scheduled earlier than normal to avoid stress in the active growth stage."
        else:
            guidance = "Soil condition is favorable for the selected crop; follow standard nutrient timing."

        return AdvisoryRecommendation(
            recommendation_id=f"adv-{soil.soil_test_id}",
            crop_name=crop_hint,
            recommendation_text=guidance,
            confidence_score=0.88,
            created_by="Advisory Engine",
        )


class NotificationService:
    @staticmethod
    def build_weather_alert(village: str, weather_type: str, severity: str) -> Dict[str, str]:
        return {
            "village": village,
            "type": weather_type,
            "severity": severity,
            "message": f"{weather_type} alert for {village}. Please take preventive precautions.",
            "channel": "SMS",
        }


class DigitalFarmingMVP:
    def __init__(self, product_name: str):
        self.product_name = product_name

    def backend_stack(self) -> Dict[str, List[str]]:
        return {
            "backend": ["FastAPI", "Python 3.13", "Role-based access control"],
            "database": ["PostgreSQL", "Redis cache", "Object storage for images"],
            "integrations": ["Weather API", "Mandi price feed", "SMS gateway", "AI diagnosis service"],
        }

    def modules(self) -> Dict[str, List[str]]:
        return {
            "Farmer Service": ["Profile management", "Farm onboarding", "Localization and language preferences"],
            "Soil Service": ["Soil testing intake", "Result validation", "Advisory generation"],
            "Weather Service": ["Forecast ingestion", "Village alerting", "Irrigation guidance"],
            "AI Diagnosis Service": ["Image upload", "Disease detection", "Confidence scoring"],
            "Market Service": ["Local mandi feed", "Price comparison", "Best-sale recommendations"],
            "Scheme Service": ["Eligibility checks", "Document checklist", "Application tracking"],
        }

    def endpoints(self) -> List[str]:
        return [
            "GET /api/farmers",
            "POST /api/farmers",
            "GET /api/farms/{farmer_id}",
            "POST /api/soil-tests",
            "GET /api/soil-tests/{farm_id}",
            "POST /api/advisories",
            "GET /api/weather/alerts?location={village}",
            "POST /api/crop-detection",
            "GET /api/market-prices?crop={crop_name}",
            "GET /api/schemes?farmer_id={id}",
            "POST /api/notifications",
        ]

    def implementation_plan(self) -> List[str]:
        return [
            "Set up the monorepo and environment for backend, dashboard, and mobile app workspaces.",
            "Build farmer, farm, and operator identity models with role-based access control.",
            "Implement soil test capture and recommendation workflow for the MVP.",
            "Integrate weather data feed and village-level alert notifications.",
            "Add image-based disease detection and agronomist review workflow.",
            "Integrate mandi price feeds and scheme eligibility service.",
            "Pilot with one or two villages and gather feedback for iteration.",
        ]


def generate_backend_mvp_plan(product_name: str) -> str:
    blueprint = DigitalFarmingMVP(product_name)
    return f"""{product_name} MVP Backend Blueprint

Product Goal:
Build a rural agriculture support system that combines village operators, digital advisories, market insights, and government support workflows in one platform.

Technology Stack:
- Backend: {', '.join(blueprint.backend_stack()['backend'])}
- Database: {', '.join(blueprint.backend_stack()['database'])}
- Integrations: {', '.join(blueprint.backend_stack()['integrations'])}

Core Modules:
{chr(10).join(f'- {name}: {', '.join(features)}' for name, features in blueprint.modules().items())}

Primary API Endpoints:
{chr(10).join(f'- {endpoint}' for endpoint in blueprint.endpoints())}

Implementation Plan:
{chr(10).join(f'{index + 1}. {step}' for index, step in enumerate(blueprint.implementation_plan()))}

Operational Notes:
- Design for low-connectivity environments and offline field capture.
- Keep the user interface simple and narrative-based for low-literacy rural users.
- Include agronomist human review for AI-generated recommendations.
- Use local-language alert templates and voice guidance.
""".strip()


if __name__ == "__main__":
    print(generate_backend_mvp_plan("Digital Farming Support Center"))
