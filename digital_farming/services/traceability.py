from __future__ import annotations

from typing import Any, Dict


def build_traceability_summary(farmer: str, batch: str, location: str, quality_grade: str) -> Dict[str, Any]:
    grade = (quality_grade or "B").upper()
    status = "Traceability verified" if grade in {"A", "B"} else "Grade requires review"

    procurement_steps = [
        "Farm registration and farmer identity verification completed.",
        "Field lot and harvest details recorded for the selected batch.",
        "Quality inspection and grading confirmed for procurement readiness.",
        "Local collection and buyer acceptance tracked for traceable transfer.",
    ]

    if grade == "A":
        status = "Traceability verified and premium procurement eligible"
        procurement_steps.insert(0, "Premium lot classification approved for competitive buyer negotiation.")
    elif grade == "B":
        status = "Traceability verified and standard procurement eligible"
        procurement_steps.insert(0, "Lot passed baseline quality standards for regular buyer channels.")
    else:
        procurement_steps.insert(0, "Grade review triggered to improve sorting and reinspection before release.")

    return {
        "farmer": farmer,
        "batch": batch,
        "location": location,
        "quality_grade": grade,
        "traceability_status": status,
        "procurement_steps": procurement_steps,
    }
