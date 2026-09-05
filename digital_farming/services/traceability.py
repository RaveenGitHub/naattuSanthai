from __future__ import annotations

from typing import Any, Dict


def build_traceability_summary(farmer: str, batch: str, location: str, quality_grade: str) -> Dict[str, Any]:
    grade = (quality_grade or "B").upper()
    status = "Traceability verified" if grade in {"A", "B"} else "Grade requires review"

    chain_of_custody = [
        "Farmer identity and farm registration verified against field records.",
        "Harvest lot recorded with timestamp, location, and batch reference.",
        "Storage and transport points documented to maintain chain-of-custody integrity.",
        "Buyer acceptance and procurement transfer logged for downstream review.",
    ]
    lot_lifecycle = [
        "Field production and harvest completed.",
        "Lot graded and quality label assigned.",
        "Collection and transport documentation checked.",
        "Final procurement or buyer handoff verified.",
    ]

    procurement_steps = [
        "Farm registration and farmer identity verification completed.",
        "Field lot and harvest details recorded for the selected batch.",
        "Quality inspection and grading confirmed for procurement readiness.",
        "Local collection and buyer acceptance tracked for traceable transfer.",
    ]

    if grade == "A":
        status = "Traceability verified and premium procurement eligible"
        procurement_steps.insert(0, "Premium lot classification approved for competitive buyer negotiation.")
        chain_of_custody.insert(0, "Premium lot certification approved for premium buyer channels and transparent pricing review.")
        lot_lifecycle.insert(0, "Premium lot flagged for high-value buyer channel and pricing review.")
    elif grade == "B":
        status = "Traceability verified and standard procurement eligible"
        procurement_steps.insert(0, "Lot passed baseline quality standards for regular buyer channels.")
        chain_of_custody.insert(0, "Lot passed standard quality review and entered regular procurement flow.")
        lot_lifecycle.insert(0, "Lot passed baseline grading and moved to routine procurement scheduling.")
    else:
        procurement_steps.insert(0, "Grade review triggered to improve sorting and reinspection before release.")
        chain_of_custody.insert(0, "Grade review triggered; lot requires reinspection and sorting before final release.")
        lot_lifecycle.insert(0, "Lot placed under review for regrading and quality correction before buyer dispatch.")

    return {
        "farmer": farmer,
        "batch": batch,
        "location": location,
        "quality_grade": grade,
        "traceability_status": status,
        "procurement_steps": procurement_steps,
        "chain_of_custody": chain_of_custody,
        "lot_lifecycle": lot_lifecycle,
    }
