# Combined Roadmap — Government Schemes, Disease Detection, and Soil Testing

## 1. Overview

This combined roadmap tracks both high-priority modules currently mapped to the repo and product backlog.

The three modules are:

- Government Schemes module
- Disease Detection module
- Soil Testing module

Together they form the next layer of farmer support beyond the already-established dashboard, advisory, and soil-health flows.

---

## 2. Current repository status snapshot

### Completed in repo

- Government schemes landing page and detail page in [app.py](../app.py)
- Government schemes API routes in [routes.py](../routes.py)
- Government schemes service and fetch-status logic in [services.py](../services.py)
- Test coverage for schemes and public page behavior in [tests/test_api.py](../tests/test_api.py)
- Soil health page flow and related API route are present

### Partially implemented

- AI validation and trust rules for scheme content
- Archive UX quality improvements
- Source governance and deduplication rules
- Real external source integration beyond seeded content

### Planned

- Disease detection upload and scan flow
- AI model integration with image inference
- Diagnosis result page with Tamil treatment and prevention guidance
- Disease scan history and review model
- Confidence warnings and human review workflow
- Soil testing AI summary and recommendation engine
- Crop, fertilizer, and irrigation guidance from soil data
- Tamil-first soil result page with optional voice guidance

---

## 3. Combined roadmap by phase

## Phase 1 — Stabilize the current product base

Status: In progress / mostly complete

Workstreams:

- final polish on Government Schemes landing and detail experience
- confirm admin fetch health and quality monitoring
- finalize scheme page filters and archive behavior

Repo evidence:

- [app.py](../app.py)
- [routes.py](../routes.py)
- [services.py](../services.py)
- [tests/test_api.py](../tests/test_api.py)

---

## Phase 2 — Strengthen AI quality and trust

Status: Planned

Workstreams:

- AI content validation for scheme summaries
- source trust scoring and deduplication
- content review pipeline before public publishing
- confidence-aware handling for all AI-generated outputs

Goal:

- ensure public-facing scheme guidance remains trustworthy and farmer-safe

---

## Phase 3 — Launch soil testing guidance MVP

Status: Planned

Workstreams:

- manual soil entry, lab upload, and sensor sync flow
- soil data normalization for pH, NPK, moisture, EC, and micronutrients
- Tamil summary generation from soil results
- crop, fertilizer, and irrigation recommendation engine
- mobile-friendly Tamil result page with optional voice output

Goal:

- convert raw soil readings into actionable, low-literacy Tamil guidance for farmers

---

## Phase 4 — Launch disease detection MVP

Status: Planned

Workstreams:

- crop image upload and camera capture flow
- disease detection inference layer
- Tamil diagnosis and guidance output
- low-confidence warnings and fallback review

Goal:

- provide a lightweight but effective diagnostic tool for common field issues

---

## Phase 5 — Build operational history and support flow

Status: Planned

Workstreams:

- DiseaseScanHistory model and endpoint
- follow-up support review for repeated cases
- archive/trend review for common crop issues
- operational dashboards for detection volume and confidence

Goal:

- turn diagnosis into a repeatable support workflow, not a one-off demo

---

## Phase 6 — Final field-readiness and rollout

Status: Planned

Workstreams:

- Tamil UX refinement and accessibility polish
- voice guidance optional mode
- pilot validation with farmers and extension officers
- release checklist and operational review

Goal:

- confirm the modules are field-ready and understandable for real farmer use

---

## 4. Combined priority matrix

| Priority | Module                          | Current status        | Strategic value                                  |
| -------- | ------------------------------- | --------------------- | ------------------------------------------------ |
| High     | Government Schemes              | Mostly implemented    | Trust-building, policy access, farmer enablement |
| High     | Soil Testing                    | Partially implemented | Converts raw field data into actionable guidance |
| High     | Disease Detection               | Planned               | Early crop issue detection and intervention      |
| High     | Admin monitoring and validation | Partial               | Needed for quality and operational safety        |
| Medium   | Archive UX quality              | Partial               | Improves discovery and reduces clutter           |
| Medium   | Source governance               | Partial               | Needed for trust and scale                       |
| Medium   | UX refinement                   | Partial               | Needed for mobile field use                      |

---

## 5. Recommended delivery order

1. Government schemes quality and trust hardening
2. Soil testing AI guidance MVP
3. Disease detection upload and diagnosis MVP
4. Scan history and review flow
5. UX polish and field pilot readiness

This keeps the roadmap grounded in the current codebase while sequencing the next highest-value user-facing work.
