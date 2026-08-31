from __future__ import annotations

from typing import Any, Dict


def build_crop_calendar(crop: str, season: str) -> Dict[str, Any]:
    crop_name = (crop or "crop").strip().lower()
    season_name = (season or "Kharif").strip().title()

    if "rice" in crop_name:
        activities = [
            {"stage": "Land preparation", "window": "1-2 weeks before sowing", "focus": "Field leveling and puddling to improve water control."},
            {"stage": "Nursery cultivation", "window": "Seedling stage", "focus": "Prepare healthy seedlings and monitor early vigor."},
            {"stage": "Transplanting", "window": "20-25 days after nursery", "focus": "Maintain uniform spacing and correct water depth."},
            {"stage": "Vegetative growth", "window": "30-60 days after transplanting", "focus": "Nitrogen split application and weed management."},
            {"stage": "Reproductive stage", "window": "60-90 days after transplanting", "focus": "Irrigation scheduling and pest surveillance."},
            {"stage": "Harvest readiness", "window": "Late season", "focus": "Drain fields and schedule harvest before heavy rainfall risk."},
        ]
    elif "groundnut" in crop_name:
        activities = [
            {"stage": "Seedbed preparation", "window": "Before sowing", "focus": "Loosen the soil and ensure proper drainage for root development."},
            {"stage": "Sowing", "window": "Early season", "focus": "Use treated seed and maintain recommended spacing."},
            {"stage": "Flowering", "window": "Mid season", "focus": "Monitor soil moisture and support pod filling."},
            {"stage": "Pegging", "window": "Critical growth stage", "focus": "Protect from water stress and maintain nutrient balance."},
            {"stage": "Pod development", "window": "Late season", "focus": "Avoid excess moisture to prevent fungal issues."},
            {"stage": "Harvest", "window": "At maturity", "focus": "Plan harvest before prolonged rain or pod rotting."},
        ]
    else:
        activities = [
            {"stage": "Field preparation", "window": "Before planting", "focus": "Prepare the seedbed and validate soil health."},
            {"stage": "Planting", "window": "Early season", "focus": "Ensure uniform seed placement and moisture support."},
            {"stage": "Growth monitoring", "window": "Mid season", "focus": "Follow nutrient, irrigation, and pest checks closely."},
            {"stage": "Harvest planning", "window": "Late season", "focus": "Prepare labor, storage, and market coordination."},
        ]

    return {
        "crop": crop_name,
        "season": season_name,
        "activities": activities,
    }
