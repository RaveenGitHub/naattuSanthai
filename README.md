# Digital Farming Support Center

A mature agriculture and sustainability platform prototype for farmer support, agronomy advisory, weather intelligence, market data, and scheme guidance.

This repository has been reviewed and reorganized toward a more production-ready Python project structure while retaining compatibility with the earlier prototype modules.

## Implementation guide and project metadata

Use the implementation tracking guide in [docs/implementation-guide.md](docs/implementation-guide.md), the Tamil UI and backlog tracker in [docs/tamil-ui-backlog.md](docs/tamil-ui-backlog.md), the Government Schemes product PRD in [docs/government-schemes-module-prd.md](docs/government-schemes-module-prd.md), and the repo metadata file at [project-metadata.yaml](project-metadata.yaml) to track the current status, next steps, prerequisites, and impacted implementation areas.

## Tamil-first product direction

This app is being shaped as a Tamil Nadu farmer-first digital agriculture platform with a mobile-ready design system, practical field workflows, and plain-language guidance. The current UI work prioritizes a Tamil-first landing experience, dashboard, services, crop advisory, and weather-market views that map to the most important farmer decisions.

## Repository structure

```text
.
├── .github/
│   └── agents/
│       ├── ui-ux-designer-agent.agent.md
│       ├── agriculture-farming-sustainability-master-engineer.agent.md
│       ├── agriculture-farming-sustainability-domain-reliability-commander.agent.md
│       ├── agri-data-engineer.agent.md
│       ├── farm-operations-analyst.agent.md
│       └── sustainability-carbon-reporting-specialist.agent.md
├── digital_farming/
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── database.py
│   ├── diagnostics.py
│   ├── routes.py
│   ├── schemas.py
│   ├── schemas_auth.py
│   ├── security.py
│   └── services.py
├── tests/
│   └── test_auth_ai.py
├── app.py
├── auth.py
├── database.py
├── diagnostics.py
├── digital_farming_mvp.py
├── routes.py
├── schemas.py
├── schemas_auth.py
├── security.py
├── services.py
├── tech_pm_agent.py
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── README.md
└── digital_farming.db
```

## Architectural direction

- Domain-oriented service boundaries for agriculture operations, advisory workflows, and auth
- Configuration-driven app settings via a central config module
- FastAPI app entrypoint intentionally kept stable for compatibility with the earlier implementation
- SQLite-backed persistence for MVP validation with future extension paths toward PostgreSQL and service isolation
- Clear separation between app runtime, domain logic, and prototype compatibility shims

## Run locally

1. Copy `.env.example` to `.env` and adjust the values for your local or deployment environment.
2. Install dependencies:

```bash
python -m pip install -r requirements.txt
```

3. Start the app:

```bash
python -m uvicorn app:app --host 0.0.0.0 --port 8000 --env-file .env
```

The app reads configuration values from the environment, including `APP_NAME`, `APP_VERSION`, `APP_ENV`, `APP_DEBUG`, `PORT`, `DATABASE_PATH`, `SECRET_KEY`, `JWT_ALGORITHM`, and `JWT_EXPIRY_HOURS`.

The Docker runtime and Docker Compose configuration both pass these values through so local development and container deployment remain consistent.

### Official city weather data

The weather page lists the configured Tier 1, Tier 2, and Tier 3 Tamil Nadu city catalog and only displays measured forecast values when a matching forecast passes both receipt-age and source-date checks. Missing or stale city data is identified rather than replaced with sample weather.

Current forecasts must have been received within the last seven days, not in the
future. Their source date must be between seven calendar days ago and the period's
future horizon: today for daily forecasts, seven days ahead for weekly, and 31 days
ahead for monthly. Source dates use the India calendar; date-only and timezone-naive
source dates are interpreted in India time, while legacy naive receipt timestamps
are interpreted as UTC. Explicit offsets and `Z` timestamps are supported.
Re-fetching an old source forecast does not make it current. Invalid dates/periods
are logged and marked unavailable, without deleting stored history.

Both weather views, latest/archive endpoints, city coverage, and stored-freshness
counts use these same checks. The period-specific raw forecast endpoints retain
historical rows; use `/api/weather/latest` or city forecast status for current daily
data. A bad newer row does not hide an older row that still passes freshness checks.
Fetch monitoring continues to report received records separately from freshness.

To fetch official IMD city forecasts, request API access and a key/token from the [IMD API portal](https://api.imd.gov.in/public/index.php), then set `IMD_API_KEY` and `IMD_API_TOKEN` in your local `.env`. IMD binds API access to the registering client/IP; follow the portal's current access requirements. The default endpoint is `https://api.imd.gov.in/api/v1/cityforecast`. Restart the app after changing `.env`, sign in as an admin, then trigger a refresh with `POST /api/weather/fetch` (or use the admin UI/API client). The response and `GET /api/weather/fetch/status` report per-city freshness and missing-city coverage.

Without valid IMD credentials, forecast refresh returns an explicit not-configured/failure result and the page shows cities with no current data. Credentials and access tokens must remain in `.env` or a secret store; never commit them.

Weather ingestion requires a finite temperature and rejects records with nonnumeric,
nonfinite, or out-of-range supplied measurements. Rainfall and wind cannot be negative;
humidity and soil moisture must be between 0 and 100 percent. Rejected records are
logged by city and field without logging the raw payload. Valid records in the same
response are still accepted.

Missing rainfall, humidity, wind, and soil moisture are stored as SQL NULL and returned
as JSON `null`, not invented zero readings. Both weather views label these measurements
as unavailable and preserve explicitly reported zero measurements. Existing forecast
rows are preserved during the automatic nullable-column migration; historical numeric
values are not reinterpreted because their original missing-value provenance is unknown.

### Weekly and monthly source contracts

Authorized JSON feeds configured through `IMD_WEATHER_FEED_URL` or
`TNSDMA_WEATHER_FEED_URL` may supply `period` as `daily`, `weekly`, or `monthly`.
Omitting it retains the daily contract. Weekly/monthly records must provide an ISO
`forecast_date`, finite `temperature_c`, and nonempty source-supplied `summary_ta`
and `advisory_ta`. Optional measurements retain the same validation/null rules.
Unknown periods and incomplete long-range records are rejected and logged.
The date identifies the source outlook date; it does not imply seven individual
daily forecasts or a derived monthly total.

Records retain their period in storage and are exposed by the corresponding
`/api/weather/weekly` or `/api/weather/monthly` endpoint and weather page period.
Long-range records never satisfy daily city coverage or populate the daily view.
The official IMD city connector currently consumes today's forecast only; it
does not synthesize weekly/monthly data from that response. Longer-range live
availability still requires an authorized feed with the documented contract.

### Schedule automatic IMD refreshes on Windows

The refresh worker runs outside Uvicorn so app restarts or multiple web workers cannot create duplicate timers. To run it once:

```powershell
.\.venv\Scripts\python.exe -m digital_farming.weather_refresh
```

It reads `.env`, writes rotating output to `logs/weather-refresh.log`, and exits with a failure code unless the entire configured city catalog was refreshed. After creating `.env` with valid IMD credentials and installing dependencies, register a daily 6:00 AM Task Scheduler job:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\Register-WeatherRefreshTask.ps1
```

The task runs as the current Windows user and requires that user to be signed in. Adjust the schedule with `-Hour` and `-Minute`. For unattended deployments, configure an OS scheduler/service with a dedicated account that can read `.env` and access the network; do not put API credentials in task arguments. The app does not install or register a task automatically.

### Monitor weather refresh reliability

Admins can inspect `GET /api/weather/rollout/readiness` before a live rollout.
After signing in as an admin, open `/admin/weather-readiness` (linked from the
admin overview) for the same read-only diagnostics, tier coverage, missing cities,
configuration warnings, and next actions. Reload diagnostics re-renders current
checks without triggering a weather refresh. Guests and non-admins cannot view it.
This read-only diagnostic makes no network requests and does not create refresh
history. It reports configuration presence/acceptance, the selected connector
(configured feeds take precedence over the official city API), static blocker
codes, current daily city coverage, and the last completed refresh result.
Credential values and configured endpoint/feed URLs are never returned.
Ignored feed configuration is reported as a warning rather than silently accepted.

`configured` only means settings pass the connector's local checks; it does not
prove credentials, source access, or payload compatibility. Daily rollout readiness
also requires the last completed refresh to be successful and all 35 configured
cities to have current forecasts. Weekly/monthly live verification and OS scheduler
registration remain explicitly unverified/not checked, even when daily readiness
passes. Do not treat this endpoint as certification of the entire platform.

Manual and scheduled refreshes store completed-run metadata in SQLite. Admins can use
`GET /api/weather/fetch/history?limit=20` (1–100 runs) and the `fetch_monitoring`
section of `GET /api/weather/fetch/status` to inspect timestamps, source outcomes,
received/missing cities, and the complete-refresh success rate over the latest 20 runs.
Partial coverage and unconfigured sources do not count as successful runs.
Before the first refresh, monitoring reports `never_run` and a null success rate.
The weather quality page shows this summary separately from stored forecast freshness.
History stores counts and source outcomes, not API credentials, feed URLs, or raw exception text;
the refresh response and worker logs provide immediate diagnostic details.

## Official scheme raw-ingestion pipeline

The new raw pipeline is separate from legacy seeded scheme content and its
timestamp-only scheduler. It does **not** publish records or translate summaries.
Configure at least one authorized JSON endpoint locally using
`PM_KISAN_SCHEME_FEED_URL`, `TN_AGRI_SCHEME_FEED_URL`, or `TN_GOVT_SCHEME_FEED_URL`.
Only HTTPS on that source's listed official host is accepted (PM-Kisan:
`pmkisan.gov.in`; TN Agriculture: `agri.tn.gov.in`; TN Government:
`tn.gov.in`/`www.tn.gov.in`). Userinfo, query strings, fragments, nonstandard
ports and redirects are rejected. No feed URLs are supplied by default: official
portal homepages are HTML, not verified JSON feed endpoints.

Feeds must return a nonempty array of JSON objects, or `{"data": [...]}`, at most
1,000 records and 2 MB of decoded response data. Nonfinite JSON values and malformed
or empty feeds fail explicitly. Each object is preserved as canonical JSON with
source URL, SHA-256 content hash, and first/last receipt timestamps; repeated content
per source updates receipt metadata rather than creating duplicates. This is raw
provenance, not verification of eligibility, translation quality, or publication.

Admin-only endpoints:
- `POST /api/schemes/ingestion/run`: fetch configured sources.
- `GET /api/schemes/ingestion/status?limit=20`: safe configuration checks and
  persistent completed-run history.
- `GET /api/schemes/ingestion/raw?limit=20&source_id=pm-kisan`: raw records for review.
- `POST /api/schemes/ingestion/raw/{raw_record_id}/normalize`: create an idempotent
  normalized draft linked to one raw source record.
- `GET /api/schemes/ingestion/review?status=pending_translation&limit=50`: review
  drafts and validation issues.
- `PATCH /api/schemes/ingestion/review/{draft_id}`: edit bounded English/Tamil and
  classification fields; validation is recalculated on save.
- `POST /api/schemes/ingestion/review/{draft_id}/resolve`: reject or approve. Approval
  publishes immediately only if required Tamil content, category and scheme type pass
  the existing scheme quality gate. Publication, review action, and audit event share
  one SQLite transaction; duplicate source records/titles and repeat resolutions are
  rejected.

The admin UI is `/admin/scheme-ingestion-review` (also linked from the legacy review
queue). Raw English content is only a reference; there is no automatic translation.
An administrator must write/review all required Tamil fields, save a valid draft,
then explicitly approve and provide a reason. Published records retain the raw record
ID and content hash; source details and editorial decisions are auditable. Existing
legacy seeded schemes are not changed by this workflow.

Limits are 1–100. Ingestion retries network errors, HTTP 429 and 5xx up to three
attempts, with a 15-second HTTP timeout and 1/2-second backoff. Other HTTP errors,
redirects and payload errors are not retried. Partial/failed/unconfigured runs are
not successful; history/logs contain source IDs and error codes, not feed URLs or
raw exceptions. Raw admin records intentionally contain public-source provenance.
No automatic raw-record pruning is enabled in this first increment.

Run from the project root:
```powershell
.\.venv\Scripts\python.exe -m digital_farming.scheme_refresh --check
.\.venv\Scripts\python.exe -m digital_farming.scheme_refresh
powershell -ExecutionPolicy Bypass -File scripts\Register-SchemeRefreshTask.ps1
```

`--check` performs no fetch or database writes. The worker loads `.env`, writes
rotating `logs/scheme-refresh.log`, and exits nonzero unless all configured sources
succeed. Task registration is explicit, checks feed configuration, prevents overlapping
instances, and runs at midnight/noon in Windows local time for the signed-in current
user. Registration is not evidence of successful execution. Use a managed service
account scheduler for unattended deployments. Live source verification is still
required; mocked test responses are not proof of an official feed's availability.

## Run with Docker

```bash
docker build -t digital-farming-support-center .
docker run --env-file .env -p 8000:8000 digital-farming-support-center
```

Or with Docker Compose:

```bash
docker-compose up --build
```

## Quality standards applied

- Secure password hashing using PBKDF2
- Authentication and role checks enforced at API boundaries
- Explicit validation for user creation and password reset flows
- Structured response envelopes for API actions
- Backward compatibility for the existing flat-module app layout during transition

## Usage example

```python
from tech_pm_agent import generate_prd, generate_backlog, generate_roadmap

print(generate_prd("Digital Farming Support Center"))
print(generate_backlog("Digital Farming Support Center"))
print(generate_roadmap("Digital Farming Support Center"))
```

## Running tests

```bash
py -3.13 -m pytest -q
```
