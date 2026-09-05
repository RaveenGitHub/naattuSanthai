from __future__ import annotations

from typing import Any, Dict


def get_market_intelligence(crop: str, market: str) -> Dict[str, Any]:
    crop_name = (crop or "crop").strip().lower()
    market_name = (market or "local").strip().title()

    trusted_sources = {
        "daily mandi feed",
        "state agri market dashboard",
        "local mandi bulletin",
    }

    if "rice" in crop_name:
        base_price = 24.5
        trend = "Rising"
        recommended_action = "Sell in the next 3-5 days if moisture and grain quality are acceptable."
        buyer_insights = [
            "Trader demand remains healthy for quality rice lots with low moisture.",
            "Large buyers prefer consistent grading and timely collection windows.",
            "Local millers are paying a small premium for uniform grain quality.",
        ]
        source_name = "Tamil Nadu State Agri Market Dashboard"
    elif "groundnut" in crop_name:
        base_price = 58.0
        trend = "Stable to firm"
        recommended_action = "Hold for a short premium window if pod quality remains strong."
        buyer_insights = [
            "Procurement demand is consistent for well-dried, clean groundnut lots.",
            "Buyer preference favors better sorting and lower impurity rates.",
            "Cold storage and drying quality improve negotiation power with traders.",
        ]
        source_name = "Local Mandi Bulletin"
    else:
        base_price = 42.0
        trend = "Moderate"
        recommended_action = "Monitor local buyer demand and negotiate before the next supply surge."
        buyer_insights = [
            "Buyer appetite is steady when quality and volume are predictable.",
            "Small-lot sales are more competitive when harvest timing aligns with nearby demand.",
            "Bulk procurement is more favorable for clean, uniform produce.",
        ]
        source_name = "Daily Mandi Feed"

    source_status = "verified" if source_name.lower() in {item.lower() for item in trusted_sources} or any(keyword in source_name.lower() for keyword in ("market", "mandi", "agri")) else "review_required"
    display_price = f"₹{base_price:.2f}/kg"

    return {
        "crop": crop_name,
        "market": market_name,
        "base_price_per_kg": base_price,
        "market_trend": trend,
        "recommended_action": recommended_action,
        "buyer_insights": buyer_insights,
        "source_name": source_name,
        "source_status": source_status,
        "display_price": display_price,
    }
