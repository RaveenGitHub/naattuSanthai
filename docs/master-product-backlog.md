# Master Product Backlog — Digital Farming Support Center

## 1. Product vision

Deliver a Tamil-first agriculture support platform that helps farmers access timely government schemes, crop advisories, soil insights, weather intelligence, market information, and disease support through simple digital workflows.

---

## 2. Portfolio priorities

### Priority 1 — Farmer decision support

- Government schemes discovery
- Soil health guidance
- Weather intelligence and regional alerts
- Advisory and field actions
- Disease detection support

### Priority 2 — Trust and operational quality

- Trusted data source governance
- AI validation and quality checks
- Admin monitoring and fetch visibility
- Human review for low-confidence outputs

### Priority 3 — Mobile-first usability

- Tamil-first UI
- Simple action-based cards
- Small-screen readability
- Voice and accessibility enhancements

---

## 3. Master backlog

## Epic A — Government schemes discovery and support

### Story GSC-01

Title: Trigger scheme refresh manually
As an admin, I want to trigger a scheme refresh so that fresh government updates can be ingested on demand.

- Acceptance criteria:
  - admin can call a fetch/update endpoint
  - the system attempts ingestion and logs the result
  - failures are visible to operational users
- Status: Completed
- Evidence: [routes.py](../routes.py), [services.py](../services.py), [tests/test_api.py](../tests/test_api.py)

### Story GSC-02

Title: Standardize source ingestion before publication
As an operator, I want official scheme sources to be standardized before publication so that only valid data enters the system.

- Acceptance criteria:
  - source name and URL are recorded
  - raw records are preserved before processing
  - duplicates and invalid items can be filtered
- Status: Partially implemented
- Evidence: scheme service logic exists in [services.py](../services.py)

### Story GSC-03

Title: Show farmer-friendly Tamil summaries
As a farmer, I want a short Tamil summary so that I can understand a scheme without reading long government text.

- Acceptance criteria:
  - Tamil title and summary are available
  - summary is short and readable
  - empty or bad summaries are rejected
- Status: Partially implemented
- Evidence: [app.py](../app.py), [services.py](../services.py)

### Story GSC-04

Title: Extract structured scheme fields
As a support officer, I want eligibility, benefits, and application steps extracted in a structured way so that I can guide farmers reliably.

- Acceptance criteria:
  - eligibility, benefits, and steps are stored as structured fields
  - content is readable in Tamil
  - incomplete fields are flagged
- Status: Partially implemented
- Evidence: [app.py](../app.py), [services.py](../services.py)

### Story GSC-05

Title: Enforce AI quality validation
As an admin, I want low-quality AI output to be rejected so that public-facing scheme content stays trustworthy.

- Acceptance criteria:
  - empty or generic summaries are blocked
  - low-confidence output is flagged
  - validation state is tracked
- Status: Planned

### Story GSC-06

Title: Keep main panel focused on recent updates
As a farmer, I want only recent schemes to appear in the main panel so that current opportunities are easy to find.

- Acceptance criteria:
  - only last 7 days show in latest panel
  - older records are hidden from latest view
  - archive rule matches the business logic
- Status: Completed / partially implemented
- Evidence: [routes.py](../routes.py), [services.py](../services.py), [app.py](../app.py)

### Story GSC-07

Title: Keep older schemes searchable in archive
As a farmer, I want older schemes to remain searchable in archive so that historical support information remains useful.

- Acceptance criteria:
  - archived records are still accessible
  - search and category filters work
  - detail view remains available
- Status: Partially implemented
- Evidence: [routes.py](../routes.py), [services.py](../services.py), [app.py](../app.py)

### Story GSC-08

Title: Provide Tamil-first scheme page
As a farmer, I want a Tamil-first government schemes page so that I can browse schemes without technical friction.

- Acceptance criteria:
  - page is readable in Tamil
  - cards include summary and call to action
  - page works on mobile screens
- Status: Completed / validated
- Evidence: [app.py](../app.py), [tests/test_api.py](../tests/test_api.py)

### Story GSC-09

Title: Provide detail page for each scheme
As a farmer, I want scheme details in a dedicated page so that I can understand eligibility, benefits, and steps in one place.

- Acceptance criteria:
  - each scheme has a detail page
  - sections show eligibility, benefits, and steps
  - content is readable and structured
- Status: Completed / validated
- Evidence: [app.py](../app.py), [tests/test_api.py](../tests/test_api.py)

### Story GSC-10

Title: Monitor fetch health and content counts
As an admin, I want fetch health and counts so that scheme ingestion quality can be monitored.

- Acceptance criteria:
  - status endpoint returns summary data
  - total, latest, archived counts are visible
  - admin access is enforced
- Status: Completed
- Evidence: [routes.py](../routes.py), [services.py](../services.py), [tests/test_api.py](../tests/test_api.py)

### Story GSC-11

Title: Prepare pilot rollout checklist
As a product owner, I want a pilot-ready rollout checklist so that the module can be validated before broader release.

- Acceptance criteria:
  - quality review list exists
  - pilot readiness includes UX review
  - release blockers are explicit
- Status: Partially implemented
- Evidence: [docs/government-schemes-prd.md](government-schemes-prd.md), [docs/government-schemes-implementation-plan.md](government-schemes-implementation-plan.md)

---

## Epic B — Disease detection and crop issue support

### Story DD-01

Title: Upload crop image for diagnosis
As a farmer, I want to upload a crop image so that I can diagnose crop damage quickly.

- Acceptance criteria:
  - user can choose an image from camera or gallery
  - upload completes successfully
  - loading state is visible during processing
- Status: Planned

### Story DD-02

Title: Provide scan screen for field support
As a field officer, I want a simple scan screen so that I can support multiple farmers without complex steps.

- Acceptance criteria:
  - simple mobile layout
  - upload and camera actions are clear
  - error states are understandable
- Status: Planned

### Story DD-03

Title: Detect likely issue from image
As a farmer, I want the system to detect the likely issue so that I can take action early.

- Acceptance criteria:
  - AI returns likely disease or issue type
  - confidence is displayed
  - result is shown in Tamil
- Status: Planned

### Story DD-04

Title: Handle low-confidence predictions carefully
As an operator, I want low-confidence results to be treated carefully so that uncertain diagnoses do not mislead farmers.

- Acceptance criteria:
  - warning messaging is shown
  - recommend re-upload or human review
  - result is tracked for operational review
- Status: Planned

### Story DD-05

Title: Show Tamil treatment steps
As a farmer, I want treatment steps in Tamil so that I can act without technical language barriers.

- Acceptance criteria:
  - treatment advice is simple and practical
  - steps are clear in field conditions
  - result page includes treatment guidance
- Status: Planned

### Story DD-06

Title: Show prevention tips
As a farmer, I want prevention tips so that I can reduce future risk to the crop.

- Acceptance criteria:
  - prevention steps are displayed after diagnosis
  - actions are crop-relevant and easy to follow
  - content is readable on mobile
- Status: Planned

### Story DD-07

Title: Maintain scan history
As an operator, I want a scan history so that I can review prior diagnoses and treatment actions.

- Acceptance criteria:
  - previous scans are stored with date and diagnosis
  - history list shows disease and time
  - records remain accessible for follow-up
- Status: Planned

### Story DD-08

Title: Provide simple Tamil UX
As a farmer, I want a simple Tamil UI so that I can use the page without reading technical instructions.

- Acceptance criteria:
  - simple Tamil wording and readable layout
  - icons and clear hierarchy are used
  - result page is easy to scan
- Status: Planned

### Story DD-09

Title: Optional voice feedback
As a user, I want optional voice guidance so that I can get instructions in spoken Tamil.

- Acceptance criteria:
  - voice readout can be toggled on
  - main flow remains usable without it
- Status: Planned

---

## Epic C — Soil testing and AI-guided recommendations

### Story ST-01

Title: Enter soil test values manually or via upload
As a farmer or operator, I want to enter soil data manually or upload a lab report so that the system can evaluate field health.

- Acceptance criteria:
  - manual entry is available
  - lab report upload is supported
  - sensor/device sync option is clearly labeled
- Status: Partially implemented
- Evidence: soil health services in [digital_farming/services/soil_health.py](../digital_farming/services/soil_health.py)

### Story ST-02

Title: Capture key soil metrics
As an operator, I want pH, NPK, moisture, organic carbon, and EC data to be stored so that the system can produce a valid recommendation.

- Acceptance criteria:
  - required soil metrics are captured
  - values are stored with a test timestamp
  - incomplete records are flagged for review
- Status: Partially implemented

### Story ST-03

Title: Generate Tamil soil health summary
As a farmer, I want a simple Tamil summary of my soil health so that I can understand my field condition quickly.

- Acceptance criteria:
  - soil status is summarized in Tamil
  - language is simple and farmer-readable
  - summary is shown beside key metrics
- Status: Partially implemented

### Story ST-04

Title: Recommend suitable crops
As a farmer, I want crop recommendations based on my soil analysis so that I can plan the next season better.

- Acceptance criteria:
  - recommended crops are generated from soil metrics
  - output is shown in Tamil
  - advice is easy to understand in field conditions
- Status: Planned

### Story ST-05

Title: Add fertilizer guidance
As a farmer, I want an actionable fertilizer plan so that I can correct nutrient imbalances cost-effectively.

- Acceptance criteria:
  - fertilizer plan is generated from soil output
  - recommendations are written in simple Tamil
  - plan covers major nutrient deficiencies
- Status: Planned

### Story ST-06

Title: Add irrigation plan guidance
As a farmer, I want irrigation advice based on soil moisture and EC so that I can reduce stress and improve water efficiency.

- Acceptance criteria:
  - irrigation guidance is produced for the soil profile
  - recommendations are practical and seasonal
  - actions are easy to execute in the field
- Status: Planned

### Story ST-07

Title: Recommend soil improvement actions
As a farmer, I want soil improvement tips so that I can restore fertility and reduce future decline.

- Acceptance criteria:
  - improvement tips are displayed in Tamil
  - advice prioritizes low-cost, local actions
  - recommendations include organic matter and nutrient correction guidance
- Status: Planned

### Story ST-08

Title: Provide Tamil-first soil results UI
As a farmer, I want a clear Tamil soil health page so that I can read results without technical friction.

- Acceptance criteria:
  - result page is easy to scan on mobile
  - soil parameters use simple Tamil labels
  - icons and optional voice guidance are available
- Status: Partially implemented

---

## Epic D — Weather intelligence and regional advisory

### Story WT-01

Title: Select weather region by district, taluk, and village
As a farmer, I want to select my location so that weather advice is relevant to my field and village.

- Acceptance criteria:
  - region selection supports state, district, taluk, and village
  - user can override auto-detected location
  - selected region is clearly shown in the UI
- Status: Planned

### Story WT-02

Title: View daily weather summary in Tamil
As a farmer, I want daily weather updates so that I can plan irrigation, spraying, and field work.

- Acceptance criteria:
  - daily forecast shows temperature, rainfall, wind, and humidity
  - summary is displayed in simple Tamil
  - practical advisory is shown for the day
- Status: Planned

### Story WT-03

Title: View weekly forecast for crop planning
As a farmer, I want weekly weather trends so that I can plan agronomic work across the coming week.

- Acceptance criteria:
  - 7-day trend is available
  - rainfall and temperature patterns are clear
  - crop-specific advisories are shown in Tamil
- Status: Planned

### Story WT-04

Title: View monthly forecast and seasonal planning
As a farmer, I want a monthly overview so that I can prepare for seasonal weather trends and crop planning.

- Acceptance criteria:
  - monthly forecast includes rainfall and temperature expectations
  - seasonal crop guidance is displayed
  - recommendations are easy to understand on mobile
- Status: Planned

### Story WT-05

Title: Receive warning alerts for risk events
As a farmer, I want alerts for heavy rain, storms, heat waves, and cold spells so that I can act early.

- Acceptance criteria:
  - risk alerts are generated in Tamil
  - severity is clearly labeled
  - weather risk can be seen from the dashboard or alert panel
- Status: Planned

### Story WT-06

Title: Get crop-specific advisories from weather data
As a farmer, I want crop guidance from weather conditions so that I can optimize irrigation and protection actions.

- Acceptance criteria:
  - advisories cover irrigation timing, fertilizer timing, and pest risk
  - recommendations are tailored to crop context
  - output is displayed in simple Tamil
- Status: Planned

### Story WT-07

Title: Access weather archive by date and region
As an operator, I want historical weather summaries so that I can review earlier patterns and compare region conditions.

- Acceptance criteria:
  - older weather summaries remain searchable
  - archive supports date and region filters
  - records are retained according to policy
- Status: Planned

### Story WT-08

Title: Use Tamil-first weather dashboard UX
As a farmer, I want a clear weather dashboard in Tamil so that I can scan essential information quickly.

- Acceptance criteria:
  - dashboard includes today, this week, and this month sections
  - icons and simple labels are used
  - result cards are legible and mobile-friendly
- Status: Planned

### Story WT-09

Title: Optional Tamil voice alerting
As a user, I want optional voice alerts so that I can hear key weather instructions in spoken Tamil.

- Acceptance criteria:
  - voice alert can be toggled on or off
  - it does not block the core weather experience
- Status: Planned

### Story WT-10

Title: Trigger weather fetch and monitor admin status
As an admin, I want to trigger a weather refresh and review fetch health so that the latest forecast data stays current and operationally reliable.

- Acceptance criteria:
  - admin can trigger a fetch job manually
  - fetch success and failure are logged
  - admin can review job health and regional coverage status
- Status: Planned

### Story WT-11

Title: Use authoritative weather sources only
As an operator, I want weather data to come from trusted government and meteorological sources so that farmer advice is evidence-based and safe.

- Acceptance criteria:
  - source list is limited to authoritative sources
  - fallback providers are explicitly marked as secondary
  - invalid or stale source data is flagged before publication
- Status: Planned

### Story WT-12

Title: Validate Tamil readability and forecast usefulness
As a product owner, I want weather recommendations to pass readability and usefulness checks so that farmers can trust the advice in the field.

- Acceptance criteria:
  - Tamil output is reviewed for clarity and simplicity
  - recommendations are linked to actual forecast conditions
  - low-quality AI output is flagged for manual review
- Status: Planned

### Story WT-13

Title: Enforce weather retention and archive policy
As an admin, I want a clear retention policy so that current weather stays current while older summaries remain searchable without cluttering the main dashboard.

- Acceptance criteria:
  - last 7 days remain in the latest panel
  - older summaries move to archive
  - monthly weather data is retained for 12 months
- Status: Planned

### Story WT-14

Title: Track weather quality and adoption KPIs
As a product owner, I want weather KPIs and dashboard metrics so that forecast quality, adoption, and usefulness can be evaluated before scale-up.

- Acceptance criteria:
  - forecast accuracy, Tamil readability, adoption, and usefulness are tracked
  - quality thresholds are defined for release readiness
  - operational dashboards expose the core KPIs
- Status: Planned

---

## 4. Sprint plan

### Sprint 1 — Foundation and fetch flow

- GSC-01
- GSC-02
- GSC-10
- DD-01
- DD-02

Status: Government schemes completed; disease detection not yet started

### Sprint 2 — AI and content quality

- GSC-03
- GSC-04
- GSC-05
- DD-03
- DD-04

Status: Partial for schemes; planned for disease detection

### Sprint 3 — Farmer UI and detail experience

- GSC-06
- GSC-07
- GSC-08
- GSC-09
- DD-05
- DD-06

Status: Government schemes mostly complete; disease detection planned

### Sprint 4 — History, QA, and rollout

- GSC-11
- DD-07
- DD-08
- DD-09

Status: In progress for schemes; planned for disease detection

### Sprint 5 — Soil testing and AI guidance MVP

- ST-01
- ST-02
- ST-03
- ST-04
- ST-05
- ST-06
- ST-07
- ST-08

Status: Soil-health foundation exists; recommendation and output layer still planned

### Sprint 6 — Weather intelligence MVP

- WT-01
- WT-02
- WT-03
- WT-04
- WT-05
- WT-06
- WT-07
- WT-08
- WT-09

Status: Planned

### Sprint 7 — Weather operations, quality, and governance

- WT-10
- WT-11
- WT-12
- WT-13
- WT-14

Status: Planned

---

## 5. Current implementation status summary

| Area                            | Status                | Notes                                                             |
| ------------------------------- | --------------------- | ----------------------------------------------------------------- |
| Government schemes landing page | Completed             | Tamil-first page exists in [app.py](../app.py)                    |
| Government schemes detail page  | Completed             | Detail route and rendering exist                                  |
| Government fetch status         | Completed             | Endpoint and summary logic exist                                  |
| Government source governance    | Partially implemented | Source metadata exists but needs stronger validation              |
| Government AI validation        | Planned               | No formal validation guardrails yet                               |
| Soil health page                | Partially implemented | API and HTML flow exist; recommendations still need formalization |
| Soil testing AI recommendations | Planned               | Requires crop, fertilizer, and irrigation guidance engine         |
| Weather page and forecast flow  | Planned               | No daily, weekly, or monthly weather intelligence yet             |
| Disease detection page          | Planned               | No scan flow or model integration yet                             |
| History model for disease scans | Planned               | DiseaseScanHistory not yet implemented                            |
| Cross-feature UX polish         | Partially implemented | Some screens are present but not fully unified                    |

---

## 6. Weather and AI quality gate

The weather module should not be treated as a simple data feed. It requires the same operational and trust discipline as the other AI-generated farmer services.

### Required KPIs

- forecast accuracy by region and time window
- Tamil readability score for daily, weekly, and monthly summaries
- farmer adoption rate for weather dashboard use
- advisory usefulness rating from field users
- source compliance rate from trusted meteorological feeds
- fetch success rate and operational alert coverage

### Required release checks

- confirm source list is limited to authoritative providers
- confirm fallback providers are clearly labeled as secondary
- confirm daily/weekly/monthly outputs meet readability standards
- confirm 7-day latest view and 12-month archive retention are enforced
- confirm admin monitoring exists for fetch status and regional coverage

---

## 7. Recommended next focus

1. Formalize AI validation and quality gating for scheme content
2. Introduce disease scan page and upload flow
3. Create disease scan history schema and API
4. Build confidence and warning behavior for low-quality disease predictions
5. Add weather admin fetch, data quality, and retention controls
6. Align the remaining user experience across schemes, soil, weather, and disease support flows
