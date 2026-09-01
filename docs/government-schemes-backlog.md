# Government Schemes Module — Sprint and User Story Backlog

## 1. Product outcome

The Government Schemes module should help farmers discover trusted government support in simple Tamil, with recent updates surfaced first and older information retained in archive for search and review.

---

## 2. Epic structure

### Epic 1 — Trusted source ingestion and fetch pipeline

#### Story GSC-01: As an admin, I want to trigger a scheme refresh so that fresh government updates can be ingested on demand.

- Acceptance criteria:
  - An admin can call the fetch/update endpoint
  - The system records the trigger and attempts raw ingest
  - Failure modes are logged and visible to admin operations
- Repo status: Completed / partially implemented
- Evidence:
  - [routes.py](../routes.py)
  - [services.py](../services.py)
  - [tests/test_api.py](../tests/test_api.py)

#### Story GSC-02: As an operator, I want official scheme sources to be standardized before publication so that only valid data enters the system.

- Acceptance criteria:
  - source name and source URL are stored
  - raw fetch output is kept before processing
  - duplicate or invalid source content can be filtered
- Repo status: Partially implemented
- Evidence:
  - raw scheme data handling exists in the scheme service layer
  - official source integration is not yet fully productionized

### Epic 2 — AI translation, extraction, and validation

#### Story GSC-03: As a farmer, I want a short Tamil summary so that I can understand a scheme without reading long government text.

- Acceptance criteria:
  - each scheme has a Tamil title and summary
  - summary is readable and short enough for mobile use
  - empty or irrelevant summaries are rejected
- Repo status: Partially implemented
- Evidence:
  - scheme data is seeded and shown in Tamil in [app.py](../app.py)
  - AI translation pipeline is still not production-backed by an external processing system

#### Story GSC-04: As a support officer, I want eligibility, benefits, and application steps extracted in a structured way so that I can guide farmers reliably.

- Acceptance criteria:
  - structured fields exist for eligibility, benefits, and application steps
  - fields are readable in Tamil
  - invalid or incomplete fields are flagged
- Repo status: Partially implemented
- Evidence:
  - processed scheme data is returned by the scheme detail logic in [services.py](../services.py) and [app.py](../app.py)

#### Story GSC-05: As an admin, I want low-quality AI output to be rejected so that public-facing scheme content stays trustworthy.

- Acceptance criteria:
  - empty or generic summaries are not published
  - low-confidence output is flagged
  - validation status is tracked
- Repo status: Planned
- Evidence:
  - no explicit AI validation scoring flow is present yet

### Epic 3 — Latest and archive logic

#### Story GSC-06: As a farmer, I want only recent schemes to appear in the main panel so that current opportunities are easy to find.

- Acceptance criteria:
  - only records within the last 7 days are shown as “Latest Updates”
  - older records are hidden from the main panel
  - logic matches the archive rule
- Repo status: Completed / partially implemented
- Evidence:
  - latest and archive endpoints are present in [routes.py](../routes.py)
  - underlying list functions exist in [services.py](../services.py)
  - UI rendering for latest and archive exists in [app.py](../app.py)

#### Story GSC-07: As a farmer, I want older schemes to remain searchable in archive so that historical support information remains useful.

- Acceptance criteria:
  - older records move to archive correctly
  - archive page supports filtering and search
  - archived records remain accessible via detail page
- Repo status: Partially implemented
- Evidence:
  - archive endpoints and filter handling exist in [routes.py](../routes.py) and [services.py](../services.py)
  - deeper archive UX and year grouping still need enhancement

### Epic 4 — Tamil-first farmer UI

#### Story GSC-08: As a farmer, I want a Tamil-first government schemes page so that I can browse schemes without technical friction.

- Acceptance criteria:
  - page is fully readable in Tamil
  - cards include title, summary, and call-to-action
  - page works well on small mobile screens
- Repo status: Completed / validated
- Evidence:
  - government schemes page exists in [app.py](../app.py)
  - tests validate page content in [tests/test_api.py](../tests/test_api.py)

#### Story GSC-09: As a farmer, I want scheme details in a dedicated page so that I can understand eligibility, benefits, and steps in one place.

- Acceptance criteria:
  - detail page loads for each scheme
  - required sections are present
  - content is readable and complete
- Repo status: Completed / validated
- Evidence:
  - `/scheme-page/{scheme_id}` route in [app.py](../app.py)
  - detail assertions exist in [tests/test_api.py](../tests/test_api.py)

### Epic 5 — Admin monitoring and operational visibility

#### Story GSC-10: As an admin, I want fetch health and counts so that scheme ingestion quality can be monitored.

- Acceptance criteria:
  - status endpoint returns a structured summary
  - total, latest, archived, and source-level data are visible
  - admin role is enforced
- Repo status: Completed
- Evidence:
  - `/api/fetch/status` endpoint in [routes.py](../routes.py)
  - `get_scheme_fetch_status` in [services.py](../services.py)
  - test coverage in [tests/test_api.py](../tests/test_api.py)

### Epic 6 — QA, rollout, and polish

#### Story GSC-11: As a product owner, I want a pilot-ready rollout checklist so that the module can be validated before broader release.

- Acceptance criteria:
  - quality review list exists
  - pilot readiness checklist includes content and UX review
  - release blocker conditions are clear
- Repo status: Partially implemented
- Evidence:
  - PRD and implementation docs are present in [docs/government-schemes-prd.md](government-schemes-prd.md) and [docs/government-schemes-implementation-plan.md](government-schemes-implementation-plan.md)

---

## 3. Sprint plan

### Sprint 1 — Foundation and fetch trigger

- GSC-01
- GSC-02
- GSC-10

Status target: Mostly completed in repo

### Sprint 2 — Content quality and latest/archive logic

- GSC-03
- GSC-04
- GSC-06
- GSC-07

Status target: Partially implemented

### Sprint 3 — Farmer UI and detail experience

- GSC-08
- GSC-09

Status target: Completed in repo

### Sprint 4 — Validation, monitoring, and rollout

- GSC-05
- GSC-11

Status target: In progress / planned

---

## 4. Current repo implementation mapping

| Area                                 | Status                | Repo evidence                                               | Notes                                                                |
| ------------------------------------ | --------------------- | ----------------------------------------------------------- | -------------------------------------------------------------------- |
| Admin fetch trigger                  | Completed             | [routes.py](../routes.py), [services.py](../services.py)    | Manual trigger exists                                                |
| Fetch status monitoring              | Completed             | [routes.py](../routes.py), [services.py](../services.py)    | Operational visibility added                                         |
| Latest scheme list                   | Completed             | [routes.py](../routes.py), [app.py](../app.py)              | Recent scheme records available                                      |
| Archive scheme list                  | Completed             | [routes.py](../routes.py), [services.py](../services.py)    | Filtering available                                                  |
| Detail page                          | Completed             | [app.py](../app.py)                                         | Detail view for scheme records                                       |
| Search + category filter             | Completed             | [app.py](../app.py), [services.py](../services.py)          | Main page supports filters                                           |
| AI translation pipeline              | Partially implemented | [services.py](../services.py)                               | Data is processed, but external AI layer is not yet fully formalized |
| Content validation guardrails        | Planned               | None explicit yet                                           | Needs formal validation and QA rules                                 |
| Source quality governance            | Partially implemented | source metadata exists in scheme service model              | Needs stronger source trust framework                                |
| UI polish / Tamil readability tuning | Partially implemented | [app.py](../app.py)                                         | Works, but can be refined for field usability                        |
| Pilot rollout checklist              | Partially implemented | [docs/government-schemes-prd.md](government-schemes-prd.md) | Prd exists, rollout operationalization remains                       |

---

## 5. Recommended next sprint focus

The highest-value work for the next iteration is:

1. strengthen AI validation and content quality gate
2. finalize source governance and deduplication
3. expand archive UX with year-wise grouping and richer search
4. define readiness checklist and pilot feedback loop

This keeps the project aligned with the existing implementation while closing the remaining quality and operational gaps.
