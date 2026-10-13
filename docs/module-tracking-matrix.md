# Module Tracking Matrix

## 1. Execution overview

This matrix tracks the active product modules and keeps them aligned to the repo's current implementation status, dependencies, and next engineering actions.

---

## 2. Per-module execution table

| Module                        | Owner                    | Priority | Risk level | Status                | Dependency                                                        | Verification command                                                                                                                 | Linked files                                                                                                                                                                                                   | Next action                                                                           | Last reviewed |
| ----------------------------- | ------------------------ | -------- | ---------- | --------------------- | ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------- | ------------- |
| Government Schemes            | Backend + Product        | High     | Medium     | Partially implemented | Source governance, AI validation, admin monitoring                | `.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py tests/test_layered_app.py`                                                | [app.py](../app.py), [routes.py](../routes.py), [services.py](../services.py), [tests/test_api.py](../tests/test_api.py)                                                                                       | Close AI quality gate and source trust validation                                     | 2026-09-01    |
| Admin User Management         | Backend + Security + UX  | High     | High       | Implemented; release validation pending | RBAC, user status model, audit logging, paginated queries         | `.\.venv\Scripts\python.exe -m pytest -q tests/test_api.py -k "admin or user"`                                                       | [admin-user-management-prd.md](admin-user-management-prd.md), [admin-user-management-implementation-plan.md](admin-user-management-implementation-plan.md), [app.py](../app.py), [security.py](../security.py) | Complete browser/accessibility and deployment-equivalent release validation | 2026-10-12    |
| Soil Testing                  | Backend + Agronomy       | High     | Medium     | Partially implemented | Soil metric schema, recommendation rules, Tamil output rules      | `D:\Raveendran\naattuSanthai\naattuSanthai\.venv\Scripts\python.exe -m pytest -q tests/test_layered_app.py -k "soil_health"`         | [digital_farming/services/soil_health.py](../digital_farming/services/soil_health.py), [digital_farming/api/v1/routes.py](../digital_farming/api/v1/routes.py)                                                 | Add Tamil-readable labels and farmer validation for crop-specific irrigation guidance | 2026-09-13    |
| Weather Intelligence          | Backend + Product + Data | High     | High       | Planned               | Authoritative weather sources, region model, AI summary rules     | `.\.venv\Scripts\python.exe -m pytest -q`                                                                                            | [docs/master-product-backlog.md](master-product-backlog.md), [docs/government-schemes-implementation-plan.md](government-schemes-implementation-plan.md)                                                       | Define source whitelist, fetch job, retention, and quality KPIs                       | 2026-09-01    |
| Disease Detection             | Backend + AI + UX        | High     | High       | Intake/history and provider contract implemented; model blocked | Authorized model/data, agronomy-reviewed guidance, confidence policy | `.\.venv\Scripts\python.exe -m pytest -q tests/test_auth_ai.py tests/test_pending_backlog_items.py` | [docs/disease-detection-prd.md](disease-detection-prd.md), [docs/disease-detection-backlog.md](disease-detection-backlog.md), [diagnostics.py](../diagnostics.py) | Configure a validated provider and obtain agronomy sign-off | 2026-10-28 |
| Market Intelligence           | Backend + Product        | Medium   | Medium     | Completed / validated | Data source contracts, price normalization, farmer-facing display | `D:\Raveendran\naattuSanthai\naattuSanthai\.venv\Scripts\python.exe -m pytest -q tests/test_layered_app.py -k "market_intelligence"` | [digital_farming/services/market_intelligence.py](../digital_farming/services/market_intelligence.py), [digital_farming/api/v1/routes.py](../digital_farming/api/v1/routes.py)                                 | Keep source compliance checks in the release gate                                     | 2026-09-05    |
| Sustainability & Traceability | Backend + Analytics      | Medium   | Medium     | Indicative calculator and unverified event ledger implemented | Independent evidence verification, approved sustainability methodology | `.\.venv\Scripts\python.exe -m pytest -q tests/test_layered_app.py tests/test_pending_backlog_items.py` | [digital_farming/services/sustainability.py](../digital_farming/services/sustainability.py), [digital_farming/services/traceability.py](../digital_farming/services/traceability.py) | Obtain evidence verification and methodology review before verified claims | 2026-10-28 |

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

- Current strength: image intake, user-scoped history, and a provider-neutral typed inference contract
- Main risk: no validated provider/model or locally representative evaluation set is configured
- Target next milestone: configure an authorized model and secure agronomy review of Tamil recommendations

### Market Intelligence

- Current strength: service scaffold exists
- Main risk: source quality and completeness of historical pricing data
- Target next milestone: normalize price feed and decide farmer-facing display rules

### Sustainability & Traceability

- Current strength: indicative calculation inputs are validated; lot events persist with explicit unverified status
- Main risk: neither operator-entered events nor indicative calculations constitute independent verification
- Target next milestone: approve a measurement methodology and evidence-verification process

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
