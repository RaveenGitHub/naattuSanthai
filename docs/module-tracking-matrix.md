# Module Tracking Matrix

## 1. Execution overview

This matrix tracks the active product modules and keeps them aligned to the repo's current implementation status, dependencies, and next engineering actions.

---

## 2. Per-module execution table

| Module                        | Owner                    | Priority | Risk level | Status                | Dependency                                                        | Verification command                                                                  | Linked files                                                                                                                                                                         | Next action                                                     | Last reviewed |
| ----------------------------- | ------------------------ | -------- | ---------- | --------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- | ------------- |
| Government Schemes            | Backend + Product        | High     | Medium     | Partially implemented | Source governance, AI validation, admin monitoring                | `.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py tests/test_layered_app.py` | [app.py](../app.py), [routes.py](../routes.py), [services.py](../services.py), [tests/test_api.py](../tests/test_api.py)                                                             | Close AI quality gate and source trust validation               | 2026-09-01    |
| Soil Testing                  | Backend + Agronomy       | High     | Medium     | Partially implemented | Soil metric schema, recommendation rules, Tamil output rules      | `.\.venv\Scripts\python.exe -m pytest -q tests/test_layered_app.py`                   | [digital_farming/services/soil_health.py](../digital_farming/services/soil_health.py), [digital_farming/api/v1/routes.py](../digital_farming/api/v1/routes.py)                       | Formalize crop/fertilizer/irrigation recommendation engine      | 2026-09-01    |
| Weather Intelligence          | Backend + Product + Data | High     | High       | Planned               | Authoritative weather sources, region model, AI summary rules     | `.\.venv\Scripts\python.exe -m pytest -q`                                             | [docs/master-product-backlog.md](master-product-backlog.md), [docs/government-schemes-implementation-plan.md](government-schemes-implementation-plan.md)                             | Define source whitelist, fetch job, retention, and quality KPIs | 2026-09-01    |
| Disease Detection             | Backend + AI + UX        | High     | High       | Planned               | Image model integration, scan flow, diagnosis confidence rules    | `.\.venv\Scripts\python.exe -m pytest -q`                                             | [docs/disease-detection-prd.md](disease-detection-prd.md), [docs/disease-detection-backlog.md](disease-detection-backlog.md)                                                         | Build scan page and diagnosis service contract                  | 2026-09-01    |
| Market Intelligence           | Backend + Product        | Medium   | Medium     | Planned               | Data source contracts, price normalization, farmer-facing display | `.\.venv\Scripts\python.exe -m pytest -q`                                             | [digital_farming/services/market_intelligence.py](../digital_farming/services/market_intelligence.py)                                                                                | Add source validation and display model                         | 2026-09-01    |
| Sustainability & Traceability | Backend + Analytics      | Medium   | Medium     | Planned               | Data model depth, traceability workflows, reporting contracts     | `.\.venv\Scripts\python.exe -m pytest -q`                                             | [digital_farming/services/sustainability.py](../digital_farming/services/sustainability.py), [digital_farming/services/traceability.py](../digital_farming/services/traceability.py) | Add traceability events and reporting data model                | 2026-09-01    |

---

## 3. Module-specific execution notes

### Government Schemes

- Current strength: fetch trigger, status endpoint, latest/archive logic, Tamil-first page
- Main risk: content quality, trust filtering, and AI validation
- Target next milestone: pilot-safe source governance and rejected-low-quality output pipeline

### Soil Testing

- Current strength: base soil health logic exists in service layer and API surface
- Main risk: incomplete recommendation engine and lack of formal data model around recommendations
- Target next milestone: crop, fertilizer, and irrigation recommendation outputs in Tamil

### Weather Intelligence

- Current strength: requirements and backlog coverage are complete
- Main risk: source trust, fetch reliability, retention rules, and AI readability validation
- Target next milestone: implement source whitelist, fetch job, and dashboard data contract

### Disease Detection

- Current strength: product and sprint backlog documentation is ready
- Main risk: image workflow, model integration, and confidence fallbacks
- Target next milestone: create an MVP scan and diagnosis page with confidence-safe handling

### Market Intelligence

- Current strength: service scaffold exists
- Main risk: source quality and completeness of historical pricing data
- Target next milestone: normalize price feed and decide farmer-facing display rules

### Sustainability & Traceability

- Current strength: domain services exist as a foundation
- Main risk: productization and integration across field records and reporting
- Target next milestone: formal event model and operational dashboard patterns

---

## 4. Execution priorities for the next sprint

1. Government Schemes quality gate
2. Soil Testing recommendation engine
3. Weather source + fetch + retention foundation
4. Disease Detection MVP scan flow
5. Shared UX consistency across all farmer-facing modules

---

## 5. Release readiness checklist

- All module stories have owner + status
- Dependencies are listed and tracked
- Verification commands are attached to each module
- AI-generated content has quality gates
- Admin / ops monitoring exists for fetch-related flows
- Tamil-first UX is validated for field readability
- Data retention and archive rules are explicit

This matrix should be used as the repo’s working execution backbone for the next implementation milestone.
