# Implementation Guide and Project Metadata

## 1. Project overview

- Name: Digital Farming Support Center
- Type: FastAPI-based agritech MVP and service platform
- Domain focus: farmer operations, advisory workflows, irrigation, soil health, pest monitoring, market intelligence, sustainability reporting, and traceability
- Current maturity: working prototype with tested API/service behavior and compatibility fixes for the current local environment

## 2. Current status

### Status summary

- Runtime baseline: validated in the project venv
- Test status: 23 focused validation checks passing across auth, RBAC, deployment, and env-config regressions
- Main architecture: FastAPI app, modular agriculture services, SQLite-backed data layer, role-based access patterns, admin audit logging
- Active implementation posture: production-hardening pass with verified environment and security controls

### Signal areas

- Stable: API route structure, service modules, auth flows, layered app route compatibility, environment-driven config resolution
- Improved: JWT expiry configuration, RBAC enforcement, deployment config, Docker runtime wiring, admin audit visibility
- Needs attention: deeper operational metric collection, release monitoring, and extended traceability/sustainability workflows

## 3. Repo metadata

| Field                     | Value                                       |
| ------------------------- | ------------------------------------------- |
| Repo name                 | digital-farming-support-center              |
| Primary language          | Python                                      |
| Web framework             | FastAPI                                     |
| Persistence               | SQLite for MVP, extensible to PostgreSQL    |
| Python target             | 3.8-compatible in the current configuration |
| Validation command        | `& .\.venv\Scripts\python.exe -m pytest -q` |
| Current validation result | 45 passed                                   |
| Owner                     | Engineering team / product owner            |
| Status                    | Active development                          |
| Last verified             | 2026-08-31                                  |

## 4. Prerequisites

### Required tools

- Python 3.8+ runtime
- Virtual environment created inside the repo
- pip with internet/intranet package access

### Required dependencies

- fastapi
- uvicorn
- pydantic
- PyJWT
- httpx
- pytest

### Project setup

1. Activate the repo-local environment.
2. Install dependencies from requirements.txt.
3. Verify the app with the test suite before feature work.
4. Keep dependency versions aligned with the validated environment.

## 5. Implementation scope and impacted areas

### Core application entry points

- app.py
- routes.py
- digital_farming/api/v1/routes.py

Impact: application routing, public API contract, auth and authorization flows.

### Domain services

- digital_farming/services/advisory.py
- digital_farming/services/crop_calendar.py
- digital_farming/services/irrigation.py
- digital_farming/services/market_intelligence.py
- digital_farming/services/pest_monitoring.py
- digital_farming/services/soil_health.py
- digital_farming/services/sustainability.py
- digital_farming/services/traceability.py

Impact: field operations, sustainability reporting, seasonal planning, soil and water decisions, market guidance, supply-chain traceability.

### Security and identity

- security.py
- auth.py
- schemas_auth.py
- database.py

Impact: login, token verification, RBAC enforcement, password management, audit and access confidence.

### Data and app configuration

- database.py
- digital_farming/config.py
- pyproject.toml
- requirements.txt

Impact: runtime behavior, environment state, dependency consistency, database readiness.

## 6. Next-step roadmap

### Tamil UI and design backlog status

The UI implementation is now tracked in [tamil-ui-backlog.md](tamil-ui-backlog.md) and organized around the most critical field-use journeys for Tamil Nadu farmers.

Current completed screens:

- home landing page
- farmer dashboard
- services catalog
- crop advisory
- weather and market page

Current in-progress screens:

- soil health screening
- disease detection and image review
- farmer login and profile flow
- government scheme guidance

Planned screens:

- registration and onboarding
- profile and farm record management
- admin control center
- sustainability dashboard
- traceability and procurement analytics

### Phase 1: Stabilize the baseline

- Lock runtime and dependency policy
- Standardize local environment activation and validation steps
- Confirm generated DB artifacts are intentionally managed
- Build a release checklist for production readiness

### Phase 2: Harden production behavior

- Move secrets to environment variables - completed via config-backed runtime settings
- Add audit logs for privileged actions - completed via admin audit log endpoint and DB-backed event tracking
- Standardize error handling and validation contracts - in place for auth and config surfaces
- Define a full role matrix for operators, farmers, admins, agronomists, and procurement staff - in progress with expanded RBAC guardrails

### Phase 3: Expand domain depth

- Add richer field lot and traceability event models
- Strengthen sustainability analytics and carbon reporting workflows
- Integrate live weather, market, and field sensor interfaces behind service boundaries
- Extend crop advisory and irrigation workflows with more realistic agronomy logic

### Phase 4: Operational maturity

- Add metrics, logs, and health checks - in progress with audit log foundations and deployment config review
- Plan DB migrations and backup strategy - pending
- Define deployment, rollback, and monitoring procedures - pending release runbook
- Prepare release review and trial deployment criteria - pending operational checklist

## 7. Tracking metadata

Use the following fields for every implementation task:

- area
- owner
- priority
- risk_level
- status
- dependency
- verification_command
- linked_files
- notes
- next_action
- last_reviewed

Example record:

```yaml
area: traceability
owner: backend
priority: high
risk_level: medium
status: validated
dependency: service contract, route compatibility
verification_command: ".venv\Scripts\python.exe -m pytest -q"
linked_files:
  - digital_farming/api/v1/routes.py
  - digital_farming/services/traceability.py
notes: "Traceability route compatibility fixed for lot-based and farmer-based queries."
next_action: "Add more detailed chain-of-custody and lot lifecycle tracking."
last_reviewed: "2026-08-31"
```

## 8. Exit criteria for the next implementation milestone

The repo is ready for the next milestone when:

- all changes are validated in the repo venv
- dependency versions are recorded and repeatable
- auth and RBAC rules are reviewed
- domain services remain grounded in agriculture workflows
- deployment and secrets strategy are defined
- issue tracking is maintained with explicit owners and statuses

## 9. Recommended next action

Start the next work item by selecting one of these tracks:

1. security hardening and RBAC review
2. production deployment configuration
3. traceability and market workflow expansion
4. sustainability analytics depth
5. stronger database and migration strategy

For the next engineering sprint, prioritize the area with the highest operational risk and the clearest user impact.
