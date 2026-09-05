# Digital Farming Decision Support — Implementation Plan

## 1. Goal

Build and ship a reliable agritech information stack that covers government schemes, soil testing, weather intelligence, and disease support. Each module must fetch trustworthy data, translate and summarize it in Tamil, expose a clear latest/archive experience for farmers, and remain monitorable by admins.

## Status update — 2026-09-05

- Market intelligence trust metadata is now implemented and validated: source name, source_status, and display_price are returned from the versioned API.
- Government schemes and admin monitoring remain in a stable operational state with continued quality checks.
- Current implementation priority: formalize the soil testing recommendation engine and complete the Tamil-first farmer guidance flow before moving deeper into weather or disease modules.

---

## 2. Delivery Approach

This plan is divided into six phases. It balances MVP readiness, quality checks, and operational monitoring.

### Phase 1 — Foundation and Data Model

### Phase 2 — Fetch Pipeline

### Phase 3 — AI Processing and Validation

### Phase 4 — Archive and Search Logic

### Phase 5 — Tamil UI and Detail Experience

### Phase 6 — Monitoring, QA, and Pilot Rollout

---

## 3. Phase-by-Phase Implementation

## Phase 1 — Foundation and Data Model

### Objective

Set up the schema, source registry, and data contracts needed for the module.

### Tasks

- Define raw and processed scheme models
- Add database tables for scheme records and metadata
- Add admin fetch status tracking
- Define validation rules for published content
- Set up environment variables and source config

### Deliverables

- Raw data table schema
- Processed data table schema
- Source registry configuration
- Validation and admin status structure

### Acceptance criteria

- Scheme records can be inserted and read from the database
- Raw and processed records are separated cleanly
- Metadata includes source name, URL, and timestamp

---

## Phase 2 — Fetch Pipeline

### Objective

Pull scheme information from official sources and store the raw content for downstream processing.

### Tasks

- Build connector framework for trusted sources
- Create scheduled fetch runner
- Store English raw data before transformation
- Handle retry, timeout, and failure logging
- Add source availability checks

### Deliverables

- Fetch job service
- Retry logic and fallback
- Source-level logging and error capture

### Acceptance criteria

- Each fetch saves raw content and source metadata
- Failed fetches are logged and visible to admin operations
- Source data is normalized before AI processing

---

## Phase 3 — AI Processing and Validation

### Objective

Convert raw English text into short, readable Tamil scheme content.

### Tasks

- Clean raw documents
- Translate English text into Tamil
- Summarize into farmer-friendly content
- Extract structured fields:
  - title
  - summary
  - eligibility
  - benefits
  - application steps
- Validate grammar, readability, and completeness
- Flag low-quality output for manual review

### Deliverables

- AI processing pipeline
- validation rules
- manual-review queue or admin flagging flow

### Acceptance criteria

- Each scheme has valid title, summary, and application steps in Tamil
- Empty or broken outputs are rejected before publication
- AI confidence is measured and tracked

---

## Phase 4 — Archive and Search Logic

### Objective

Only fresh updates remain in front-of-house and old content is operationally archived.

### Tasks

- Implement “last 7 days” freshness logic
- Auto-set `is_archived` for older entries
- Add filtering by category and keyword
- Support year-wise archive grouping
- Maintain detail-page access for archived records

### Deliverables

- active vs archive logic
- category filter + search endpoint
- archive grouping support

### Acceptance criteria

- Latest panel contains only recent records
- Archive panel contains older records only
- Search and filters work consistently

---

## Phase 5 — Tamil UI and Detail Experience

### Objective

Build the farmer-facing experience in Tamil with a mobile-friendly layout.

### Tasks

- Create latest schemes panel
- Create archive panel
- Create detail page per scheme
- Add search and category filter UI
- Add category tags and icons
- Use simple, readable Tamil copy

### Deliverables

- scheme landing page
- filter/search interface
- detail view page
- Tamil content rendering

### Acceptance criteria

- Farmer can browse schemes within minutes
- Each scheme card includes summary and CTA
- Detail page loads correct content without broken formatting

---

## Phase 6 — Monitoring, QA, and Pilot Rollout

### Objective

Ensure the module remains reliable after release and can be operated by admins.

### Tasks

- Add admin fetch status endpoint
- Track fetch success/failure rate
- Monitor summary quality and validation pass rate
- Test readability on selected farmer sample cases
- Pilot with field staff and selected farmers
- Capture bug fixes and refinement items

### Deliverables

- monitoring dashboard or status API
- release checklist
- pilot feedback loop

### Acceptance criteria

- Admin can see latest fetch health
- Broken or missing content is visible in operational logs
- Pilot feedback is captured before broader release

---

## 4. Workstreams

### Workstream A — Data ingestion

- source connector management
- raw data storage
- retries and logging

### Workstream B — Content transformation

- translation
- summary generation
- field extraction
- validation

### Workstream C — App experience

- latest panel
- archive panel
- detail page
- search/filter logic

### Workstream D — Monitoring and operations

- admin status endpoint
- quality tracking
- alerts and review

---

## 5. Soil Testing Module Extension

### Objective

Add a soil testing capability that converts raw soil readings into Tamil-ready recommendations for crop planning, fertilizer use, irrigation scheduling, and soil improvement.

### Data inputs

- pH
- Nitrogen, phosphorus, potassium
- Organic carbon
- Moisture
- EC
- Micronutrients (Zn, Fe, Mn, Cu)

### AI and rule requirements

- Convert raw measurements into a clear Tamil summary
- Recommend suitable crops for the field condition
- Produce fertilizer and irrigation plans in simple Tamil
- Suggest soil improvement actions based on deficiency patterns
- Validate recommendations for readability and field practicality

### Data model

#### SoilTestResults

- id
- ph
- nitrogen
- phosphorus
- potassium
- moisture
- organic_carbon
- recommended_crops_ta
- fertilizer_plan_ta
- irrigation_plan_ta
- test_date

### UI requirements

- Manual entry screen
- Lab upload or sensor sync option
- Tamil result screen with summary, recommendations, and action blocks
- Optional Tamil voice readout
- Mobile-friendly, simple-language layout

### Acceptance criteria

- Soil input screen supports manual, sensor, and lab-report entry
- Soil results are summarized in simple Tamil
- Crop, fertilizer, and irrigation recommendations are shown clearly
- Users can understand the field condition without technical terminology

---

## 6. Weather Forecast Module Extension

### Objective

Deliver a Tamil-first weather intelligence module that gives farmers daily, weekly, and monthly forecasts with crop-specific advisories and risk alerts in simple local language.

### Operational requirements

- Add admin-triggered weather fetch job and health monitoring
- Enforce authoritative source whitelist with secondary fallback labeling
- Log fetch failures, stale data warnings, and region coverage gaps
- Validate AI-generated Tamil advisories before publication
- Enforce retention rules:
  - last 7 days remain in the latest panel
  - older summaries move to archive
  - monthly weather summaries are retained for 12 months

### Trusted data sources

#### Tamil Nadu and regional sources

- Tamil Nadu State Disaster Management Authority
- Tamil Nadu Agricultural University
- Tamil Nadu IMD Regional Centre

#### National sources

- IMD
- Ministry of Earth Sciences
- Agromet Advisory Services
- Gramin Krishi Mausam Sewa
- ISRO MOSDAC

#### Fallback sources

- NOAA satellite weather data
- OpenWeather or WeatherAPI as fallback only

### AI and advisory requirements

- English to Tamil translation
- Tamil readability optimization
- Convert raw weather data into farmer-friendly summaries
- Generate crop-specific advisories for irrigation, fertilizer timing, and disease risk
- Detect risk alerts for heavy rain, storm, heat wave, and cold wave
- Produce Tamil summary cards for day, week, and month views

### Region model

- State
- District
- Taluk
- Village
- Optional GPS-based detection with manual override

### Data model

#### WeatherRawData

- id
- region_code
- date
- temp_max
- temp_min
- rainfall_mm
- humidity
- wind_speed
- raw_json

#### WeatherProcessedTamil

- id
- region_code
- date
- day_summary_ta
- week_summary_ta
- month_summary_ta
- crop_advisory_ta
- risk_alerts_ta
- created_at

### Archive and retention

- Last 7 days stays in latest panel
- Older records move to archive
- Monthly data retained for 12 months

### UI requirements

- Home weather dashboard with today, week, and month sections
- Region selector for district, taluk, and village
- Tamil alert panel for rainfall, storm, and temperature risk
- Weather cards with icons for rain, wind, and temperature
- Optional Tamil voice readout

### Acceptance criteria

- Users can select their local region and see forecast data relevant to it
- Daily, weekly, and monthly summaries are displayed in Tamil
- Risk alerts are clearly visible and understandable
- Weather archive supports date and region-based search
- Simple Tamil language is used consistently for low-literacy users
- Weather fetch jobs can be triggered and monitored by admins
- Authoritative-source compliance is enforced before public display

---

## 7. Quality gates and KPIs

### Required quality gates

- forecast accuracy checks by region and time window
- Tamil readability review for all AI-generated weather summaries
- source compliance verification against trusted provider list
- fetch success health checks and alert coverage monitoring
- 7-day latest retention and 12-month archive retention validation

### Suggested KPIs

- Forecast accuracy rate
- Tamil readability score
- Farmer adoption rate for weather dashboard use
- Advisory usefulness rating from field users
- Source compliance rate
- Fetch success rate

---

## 8. Technical Architecture

### Layers

1. Source layer
   - official government portals and feeds
2. Ingestion layer
   - fetchers, normalizers, retries
3. Processing layer
   - AI translation and summarization
4. Storage layer
   - raw and processed scheme records
5. API layer
   - latest/archive/detail/status endpoints
6. UI layer
   - Tamil-first page and detail rendering

### Recommended stack for MVP

- Python + FastAPI
- SQLite for MVP, PostgreSQL for production-ready scale
- scheduled jobs via cron or task runner
- AI translation and summarization service
- simple validation rules for readability and content completeness

---

## 9. API Surface

### GET /api/schemes/latest

Returns recent scheme entries

### GET /api/schemes/archive

Returns archived scheme entries

### GET /api/scheme/{id}

Returns a single scheme with full processed details

### GET /api/schemes?category={category}

Returns category-filtered scheme list

### POST /api/fetch/update

Admin-only manual refresh trigger

### GET /api/fetch/status

Returns fetch health summary and content counts

### GET /api/weather/daily?region=xxx

Returns Tamil daily weather summary for a selected region

### GET /api/weather/weekly?region=xxx

Returns Tamil weekly weather summary for a selected region

### GET /api/weather/monthly?region=xxx

Returns Tamil monthly weather summary for a selected region

### GET /api/weather/alerts?region=xxx

Returns Tamil risk alerts for a selected region

### POST /api/weather/fetch

Admin trigger to fetch new weather data

---

## 10. Database Model Summary

### GovSchemeRaw

- id
- title_en
- content_en
- source_name
- source_url
- fetched_at
- source_type
- raw_metadata

### GovSchemeProcessed

- id
- title_ta
- summary_ta
- eligibility_ta
- benefits_ta
- apply_steps_ta
- category
- scheme_type
- source_name
- source_url
- created_at
- is_archived
- ai_confidence_score
- validation_passed
- status

### WeatherRawData

- id
- region_code
- date
- temp_max
- temp_min
- rainfall_mm
- humidity
- wind_speed
- raw_json

### WeatherProcessedTamil

- id
- region_code
- date
- day_summary_ta
- week_summary_ta
- month_summary_ta
- crop_advisory_ta
- risk_alerts_ta
- created_at

---

## 11. Risks and Mitigation

### Risk: unreliable source updates

Mitigation:

- whitelist trusted sources only
- add retry and failure logs

### Risk: poor AI output quality

Mitigation:

- validation passes before publish
- flagged content requires manual review

### Risk: user confusion due to too much detail

Mitigation:

- keep cards concise and summary-first
- use clear detail pages

### Risk: duplicate records

Mitigation:

- dedupe by source + title + date before creation

---

## 12. QA Strategy

### Functional QA

- latest records appear in the right panel
- archive records are properly separated
- detail page is populated for valid ids
- filter/search works correctly

### Content QA

- Tamil summaries are readable and meaningful
- empty or broken fields are blocked
- source names appear correctly

### UX QA

- page renders clearly on mobile
- buttons and filters are usable on small screens
- content is understandable for low-literacy users

---

## 10. Rollout Recommendation

### MVP rollout

- enable official source fetch for a limited set of schemes
- publish only validated Tamil summary records
- keep admin review available before broader public release

### Pilot rollout

- select 1–2 districts or field teams
- validate scheme usefulness with local farmer feedback
- update wording and filters based on field review

### Full rollout

- expand to additional government schemes and categories
- add richer monitoring and operational reporting

---

## 11. Recommended Next Actions

1. finalize and prioritize official source list
2. create data model and schema in the repo
3. implement fetch/update + status endpoint
4. add AI summary pipeline with validation
5. build Tamil UI panels and detail route
6. test with real scheme samples and farmer feedback

---

## 12. Final Recommendation

The most important success factors are trust, Tamil readability, and freshness. The module should be implemented as a verified agri information service with simple UI, strong source governance, and admin monitoring rather than a generic content portal.
