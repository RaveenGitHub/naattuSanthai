from pathlib import Path

from fastapi.testclient import TestClient

from app import app
from database import create_db_backup, get_migration_status, record_migration_status
from security import create_user
from services import get_scheme_fetch_status, list_archived_scheme_updates
from services import get_scheme_fetch_status

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["service"] == "digital-farming-support-center"
    assert "database" in body
    assert body["database"]["status"] == "healthy"


def test_farmer_creation_and_listing():
    payload = {"name": "Raja", "phone": "9876543210", "village": "Kallakurichi", "language": "Tamil"}
    create_response = client.post("/api/farmers", json=payload)
    assert create_response.status_code == 200

    list_response = client.get("/api/farmers")
    assert list_response.status_code == 200
    assert isinstance(list_response.json()["data"], list)


def test_weather_alerts_endpoint():
    response = client.get("/api/weather/alerts?village=Kallakurichi")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_weather_forecast_and_fetch_routes():
    daily_response = client.get("/api/weather/daily?region=Kallakurichi")
    assert daily_response.status_code == 200
    assert daily_response.json()["success"] is True
    assert isinstance(daily_response.json()["data"], list)

    weekly_response = client.get("/api/weather/weekly?region=Kallakurichi")
    assert weekly_response.status_code == 200
    assert weekly_response.json()["success"] is True
    assert isinstance(weekly_response.json()["data"], list)

    monthly_response = client.get("/api/weather/monthly?region=Kallakurichi")
    assert monthly_response.status_code == 200
    assert monthly_response.json()["success"] is True
    assert isinstance(monthly_response.json()["data"], list)

    fetch_response = client.post("/api/weather/fetch", headers={"X-User-Role": "admin"})
    assert fetch_response.status_code == 200
    assert fetch_response.json()["success"] is True
    assert isinstance(fetch_response.json()["data"], dict)

    status_response = client.get("/api/weather/fetch/status", headers={"X-User-Role": "admin"})
    assert status_response.status_code == 200
    assert status_response.json()["success"] is True
    assert isinstance(status_response.json()["data"], dict)


def test_weather_fetch_status_contains_source_and_retention_metadata():
    response = client.get("/api/weather/fetch/status", headers={"X-User-Role": "admin"})
    assert response.status_code == 200
    payload = response.json()["data"]
    assert "source_compliance" in payload
    assert "retention_days" in payload
    assert "quality_gate" in payload
    assert "archive_policy" in payload
    assert "source_whitelist" in payload
    assert "fallback_sources" in payload
    assert payload["retention_days"] >= 7
    assert payload["archive_policy"]["latest_window_days"] == 7
    assert payload["archive_policy"]["monthly_retention_months"] >= 12


def test_weather_quality_page_renders_source_whitelist_and_retention_policy():
    response = client.get("/weather-quality")
    assert response.status_code == 200
    assert "Trusted weather sources" in response.text or "நம்பகமான வானிலை மூலங்கள்" in response.text
    assert "Retention" in response.text or "பொறுப்பு" in response.text or "தக்கவைப்பு" in response.text
    assert "IMD" in response.text or "India Meteorological Department" in response.text


def test_market_prices_endpoint():
    response = client.get("/api/market-prices?crop_name=Rice")
    assert response.status_code == 200
    assert response.json()["success"] is True


def test_government_scheme_latest_and_archive_endpoints():
    latest_response = client.get("/api/schemes/latest")
    assert latest_response.status_code == 200
    assert latest_response.json()["success"] is True
    assert isinstance(latest_response.json()["data"], list)

    archive_response = client.get("/api/schemes/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["success"] is True
    assert isinstance(archive_response.json()["data"], list)

    compatibility_response = client.get("/api/schemes?farmer_id=FARMER-001", headers={"X-User-Role": "admin"})
    assert compatibility_response.status_code == 200
    assert compatibility_response.json()["success"] is True

    detail_response = client.get("/api/scheme/SCHEME-NEW-001")
    assert detail_response.status_code == 200
    assert detail_response.json()["success"] is True
    assert detail_response.json()["data"]["title_ta"]
    assert "தகுதி" in detail_response.json()["data"]["eligibility_ta"] or "Eligibility" in detail_response.json()["data"]["eligibility_ta"]
    assert detail_response.json()["data"]["benefits_ta"]
    assert detail_response.json()["data"]["apply_steps_ta"]

    fetch_response = client.post("/api/fetch/update", headers={"X-User-Role": "admin"})
    assert fetch_response.status_code == 200
    assert fetch_response.json()["success"] is True

    monitoring_response = client.get("/api/fetch/status", headers={"X-User-Role": "admin"})
    assert monitoring_response.status_code == 200
    assert monitoring_response.json()["success"] is True
    assert isinstance(monitoring_response.json()["data"], dict)

    scheme_status_payload = monitoring_response.json()["data"]
    assert "source_compliance" in scheme_status_payload
    assert "retention_days" in scheme_status_payload
    assert "quality_gate" in scheme_status_payload
    assert "ai_validation" in scheme_status_payload
    assert scheme_status_payload["retention_days"] >= 7

    filtered_response = client.get("/api/schemes/archive?category=subsidy")
    assert filtered_response.status_code == 200
    assert filtered_response.json()["success"] is True
    assert isinstance(filtered_response.json()["data"], list)

    page_response = client.get("/government-schemes")
    assert page_response.status_code == 200
    assert "புதிய அறிவிப்புகள்" in page_response.text
    assert "காப்பக அறிவிப்புகள்" in page_response.text
    assert "தேடுக" in page_response.text or "வகை" in page_response.text

    filtered_page_response = client.get("/government-schemes?category=subsidy&search=PM-Kisan")
    assert filtered_page_response.status_code == 200
    assert "PM-Kisan" in filtered_page_response.text or "subsidy" in filtered_page_response.text.lower()
    assert 'data-page="/government-schemes"' in filtered_page_response.text
    assert 'class="nav-link active"' in filtered_page_response.text

    detailed_page_response = client.get("/scheme-page/SCHEME-NEW-001")
    assert detailed_page_response.status_code == 200
    assert "தகுதி" in detailed_page_response.text
    assert "நன்மைகள்" in detailed_page_response.text
    assert "விண்ணப்ப படிகள்" in detailed_page_response.text


def test_database_backup_and_migration_tracking_are_available():
    backup_path = create_db_backup("test-backup")
    assert isinstance(backup_path, Path)
    assert backup_path.exists()

    record = record_migration_status("test_migration", "applied", "validation migration")
    assert record["name"] == "test_migration"
    assert record["status"] == "applied"

    status = get_migration_status()
    assert status["backup_directory"].exists()
    assert any(item["name"] == "test_migration" for item in status["migrations"])
    assert "backup_policy" in status
    assert "backup_history" in status
    assert status["backup_policy"]["retention_days"] >= 7
    assert status["backup_policy"]["max_backups"] >= 1


def test_soil_manual_entry_page_renders_farm_input_form():
    response = client.get("/soil-testing")
    assert response.status_code == 200
    assert "மண் சோதனை" in response.text or "Soil Testing" in response.text
    assert "pH" in response.text or "பிஎச்" in response.text
    assert "நைட்ரஜன்" in response.text or "Nitrogen" in response.text
    assert "பாஸ்பரஸ்" in response.text or "Phosphorus" in response.text
    assert "பொட்டாசியம்" in response.text or "Potassium" in response.text
    assert "சேமி" in response.text or "Submit" in response.text


def test_soil_health_page_shows_crop_and_irrigation_guidance():
    response = client.get("/soil-health?crop=groundnut&ph=5.6&nitrogen=24&phosphorus=18&potassium=152")
    assert response.status_code == 200
    assert "பயிர் பரிந்துரை" in response.text or "Recommended crops" in response.text or "Crop recommendations" in response.text
    assert "நீர் மேலாண்மை" in response.text or "Irrigation" in response.text or "irrigation" in response.text.lower()


def test_soil_health_page_renders_farmer_actionable_summary():
    response = client.get("/soil-health?crop=groundnut&ph=5.6&nitrogen=24&phosphorus=18&potassium=152")
    assert response.status_code == 200
    assert "மண் சோதனை" in response.text or "Soil health" in response.text
    assert "groundnut" in response.text.lower() or "நிலக்கடலை" in response.text
    assert "உரம்" in response.text or "Fertilizer" in response.text
    assert "பரிந்துரை" in response.text or "Recommendation" in response.text
    assert "உர திட்டம்" in response.text or "Fertilizer plan" in response.text or "fertilizer" in response.text.lower()


def test_sustainability_and_traceability_pages_render_regeneration_and_lifecycle_details():
    sustainability_response = client.get("/sustainability?farm_size_ha=5&soil_carbon_tons=2.4&water_use_liters=4200&energy_use_kwh=320")
    assert sustainability_response.status_code == 200
    assert "நிலையான" in sustainability_response.text or "Sustainability" in sustainability_response.text
    assert "regenerative" in sustainability_response.text.lower() or "மேம்பாடு" in sustainability_response.text or "புதுப்பித்தல்" in sustainability_response.text
    assert "carbon" in sustainability_response.text.lower() or "கார்பன்" in sustainability_response.text

    traceability_response = client.get("/traceability?farmer=Kumaran&batch=RICE-24A&location=Kallakurichi&quality_grade=A")
    assert traceability_response.status_code == 200
    assert "trace" in traceability_response.text.lower() or "கண்காணிப்பு" in traceability_response.text
    assert "lot" in traceability_response.text.lower() or "லாட்" in traceability_response.text
    assert "custody" in traceability_response.text.lower() or "பாதுகாப்பு" in traceability_response.text or "சங்கிலி" in traceability_response.text


def test_weather_page_renders_region_forecast_and_guidance():
    response = client.get("/weather?region=Kallakurichi&period=daily")
    assert response.status_code == 200
    assert "வானிலை" in response.text
    assert "Kallakurichi" in response.text or "கல்லக்குறிச்சி" in response.text
    assert "பரிந்துரை" in response.text or "Advisory" in response.text
    assert "மழை" in response.text or "Rain" in response.text


def test_weather_page_reports_rainfall_in_mm_not_percent():
    response = client.get("/weather-market?region=Kallakurichi")
    assert response.status_code == 200
    assert "மழை</span><strong>" in response.text
    rainfall_value = response.text.split("மழை</span><strong>", 1)[1].split("</strong>", 1)[0]
    assert "mm" in rainfall_value.lower()
    assert "%" not in rainfall_value


def test_weather_page_supports_region_selector_for_district_taluk_and_village():
    response = client.get("/weather?region=Kallakurichi&district=Villupuram&taluk=Kallakurichi&village=Periyar Nagar&period=daily")
    assert response.status_code == 200
    assert "district" in response.text.lower() or "மாவட்டம்" in response.text
    assert "taluk" in response.text.lower() or "தாலுக்கா" in response.text
    assert "village" in response.text.lower() or "கிராமம்" in response.text
    assert "Kallakurichi" in response.text or "கல்லக்குறிச்சி" in response.text


def test_weather_weekly_page_renders_7_day_trend_and_crop_advisory():
    response = client.get("/weather?region=Kallakurichi&period=weekly")
    assert response.status_code == 200
    assert "7-day" in response.text or "7 நாள்" in response.text or "weekly" in response.text.lower()
    assert "மழை" in response.text or "Rain" in response.text
    assert "பயிர்" in response.text or "Crop" in response.text
    assert "பரிந்துரை" in response.text or "Advisory" in response.text


def test_weather_monthly_page_renders_seasonal_summary_and_crop_plan():
    response = client.get("/weather?region=Kallakurichi&period=monthly")
    assert response.status_code == 200
    assert "monthly" in response.text.lower() or "மாத" in response.text or "பருவ" in response.text
    assert "மழை" in response.text or "Rain" in response.text
    assert "பயிர்" in response.text or "Crop" in response.text
    assert "பரிந்துரை" in response.text or "Advisory" in response.text


def test_weather_page_renders_warning_alert_panel_for_risk_events():
    response = client.get("/weather?region=Kallakurichi&period=daily")
    assert response.status_code == 200
    assert "எச்சரிக்கை" in response.text or "Warning" in response.text or "Alert" in response.text
    assert "Rainstorm" in response.text or "மழை புயல்" in response.text or "மழை" in response.text
    assert "High" in response.text or "அதிகம்" in response.text or "உயர்" in response.text


def test_market_intelligence_page_renders_price_trend_and_action():
    response = client.get("/market-intelligence?crop=rice&market=Kallakurichi")
    assert response.status_code == 200
    assert "சந்தை" in response.text or "Market" in response.text
    assert "rice" in response.text.lower() or "நெல்" in response.text
    assert "விலை" in response.text or "Price" in response.text
    assert "பரிந்துரை" in response.text or "Recommendation" in response.text


def test_scheme_ai_validation_flags_incomplete_or_generic_records():
    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-QUALITY-REVIEW",
                "General Support",
                "N/A",
                "",
                "",
                "",
                "subsidy",
                "central",
                "Manual Review Source",
                "https://example.com/manual-review",
                0,
                __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            ),
        )

    status = get_scheme_fetch_status()
    assert status["ai_validation"]["status"] == "warning"
    assert status["ai_validation"]["manual_review_required"] is True
    assert status["ai_validation"]["summary_quality_score"] < 100


def test_archived_scheme_updates_include_year_grouping_metadata():
    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-ARCHIVE-YEAR-2024",
                "2024 பழைய உதவி",
                "2024 ஆம் ஆண்டுக்கான பழைய அரசு உதவி சுருக்கம்",
                "2024 தகுதி",
                "2024 நன்மை",
                "2024 விண்ணப்ப படிகள்",
                "subsidy",
                "state",
                "Archive Audit Source",
                "https://example.com/archive-year",
                1,
                "2024-03-15T10:00:00+00:00",
            ),
        )

    archived = list_archived_scheme_updates()
    assert any(item.get("year_group") == "2024" for item in archived)
    assert any(item.get("year_group") == "2026" for item in archived)


def test_government_schemes_archive_page_groups_entries_by_year():
    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-ARCHIVE-YEAR-UI",
                "2024 UI archive",
                "2024 archive UI validation",
                "2024 eligibility",
                "2024 benefits",
                "2024 steps",
                "subsidy",
                "state",
                "Archive UI Source",
                "https://example.com/archive-ui",
                1,
                "2024-09-01T09:00:00+00:00",
            ),
        )

    response = client.get("/government-schemes")
    assert response.status_code == 200
    assert "2024" in response.text
    assert "Archive 2024" in response.text or "2024" in response.text


def test_scheme_source_compliance_flags_untrusted_or_duplicate_sources():
    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-SOURCE-QUALITY-001",
                "Untrusted source scheme",
                "This scheme is from an untrusted source and should be flagged.",
                "Eligibility details",
                "Benefits details",
                "Application steps",
                "subsidy",
                "central",
                "Unverified Local Notice Board",
                "https://example.com/local-notice-board",
                0,
                __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            ),
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-SOURCE-QUALITY-002",
                "Duplicate trusted scheme",
                "Duplicate source record should also be flagged for deduplication review.",
                "Eligibility details",
                "Benefits details",
                "Application steps",
                "subsidy",
                "central",
                "PM-Kisan",
                "https://pmkisan.gov.in/",
                0,
                __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            ),
        )

    status = get_scheme_fetch_status()
    compliance = status["source_compliance"]
    assert compliance["status"] == "warning"
    assert compliance["issues"]
    assert compliance["risk_level"] in {"medium", "high"}
    assert status["source_registry"]["risk_level"] == compliance["risk_level"]
    assert any("untrusted" in issue.lower() or "duplicate" in issue.lower() for issue in compliance["issues"])


def test_admin_quality_gate_page_renders_fetch_and_source_health():
    response = client.get("/admin/quality-gate")
    assert response.status_code == 200
    assert "Quality Gate" in response.text or "தரக்" in response.text
    assert "வானிலை" in response.text or "Weather" in response.text
    assert "அரசு திட்டங்கள்" in response.text or "Schemes" in response.text
    assert "மூலம்" in response.text or "Source" in response.text
    assert "AI validation" in response.text or "AI" in response.text or "செயற்கை நுண்ணறிவு" in response.text
    assert "Readability" in response.text or "படித்தல்" in response.text or "readability" in response.text.lower()


def test_admin_quality_gate_page_surfaces_source_risk_and_review_backlog():
    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-QUALITY-GATE-RISK-001",
                "Quality gate risk sample",
                "This scheme is risky and should trigger a quality gate warning.",
                "Eligibility details",
                "Benefits details",
                "Application steps",
                "subsidy",
                "central",
                "Unverified Local Notice Board",
                "https://example.com/quality-gate-risk",
                0,
                __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            ),
        )

    response = client.get("/admin/quality-gate")
    assert response.status_code == 200
    assert "risk" in response.text.lower() or "Risk" in response.text
    assert "warning" in response.text.lower() or "WARNING" in response.text
    assert "Review Queue" in response.text or "மதிப்பாய்வு" in response.text


def test_scheme_review_queue_tracks_flagged_records_and_admin_actions():
    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-REVIEW-QUEUE-001",
                "Review queue sample",
                "N/A",
                "",
                "",
                "",
                "subsidy",
                "central",
                "Manual Review Source",
                "https://example.com/review-queue",
                0,
                __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            ),
        )

    status = get_scheme_fetch_status()
    assert status["review_queue"]["flagged_count"] >= 1
    assert "review_queue" in status

    response = client.get("/admin/review-queue")
    assert response.status_code == 200
    assert "Review Queue" in response.text or "மதிப்பாய்வு வரிசை" in response.text
    assert "Manual Review Source" in response.text or "Manual Review" in response.text


def test_scheme_review_resolution_records_admin_decision_and_audit_entry():
    isolated_client = TestClient(app)
    login = isolated_client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    assert login.status_code == 200
    token = login.json()["token"]

    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-REVIEW-RESOLVE-001",
                "Resolve queue sample",
                "N/A",
                "",
                "",
                "",
                "insurance",
                "state",
                "Manual Resolve Review Source",
                "https://example.com/review-resolve",
                0,
                __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            ),
        )

    response = isolated_client.post(
        "/api/admin/review-queue/SCHEME-REVIEW-RESOLVE-001/resolve",
        headers={"Authorization": f"Bearer {token}"},
        json={"decision": "approved", "reviewer": "admin1", "reason": "Validated against official notice"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["decision"] == "approved"

    with __import__("sqlite3").connect("digital_farming.db") as conn:
        review_row = conn.execute(
            "SELECT decision, reviewer, reason FROM scheme_review_actions WHERE scheme_id = ? ORDER BY created_at DESC LIMIT 1",
            ("SCHEME-REVIEW-RESOLVE-001",),
        ).fetchone()
        audit_row = conn.execute(
            "SELECT action, resource, outcome FROM audit_logs WHERE resource = ? ORDER BY created_at DESC LIMIT 1",
            ("scheme_review_actions",),
        ).fetchone()

    assert review_row is not None
    assert review_row[0] == "approved"
    assert review_row[1] == "admin1"
    assert audit_row is not None
    assert audit_row[0] == "scheme_review_resolved"


def test_admin_release_runbook_page_renders_release_steps_and_rollback_plan():
    response = client.get("/admin/release-runbook")
    assert response.status_code == 200
    assert "Release Runbook" in response.text or "ரிலீஸ்" in response.text or "deployment" in response.text.lower()
    assert "Rollback" in response.text or "மீட்டெடுப்பு" in response.text
    assert "Health check" in response.text or "சுகாதார சரிபார்ப்பு" in response.text or "health" in response.text.lower()


def test_admin_operations_checklist_page_renders_backup_and_migration_readiness():
    response = client.get("/admin/operations-checklist")
    assert response.status_code == 200
    assert "Operations Checklist" in response.text or "இயக்கச்" in response.text or "operational" in response.text.lower()
    assert "Backup" in response.text or "காப்பு" in response.text
    assert "Migration" in response.text or "மாற்றம்" in response.text or "migration" in response.text.lower()


def test_admin_content_configuration_page_renders_special_news_and_ad_controls():
    response = client.get("/admin/content-config")
    assert response.status_code == 200
    assert "Special News" in response.text or "சிறப்பு செய்திகள்" in response.text
    assert "Advertising" in response.text or "விளம்பரம்" in response.text

    api_response = client.get("/api/admin/content-config")
    assert api_response.status_code == 200
    assert api_response.json()["success"] is True
    assert "special_news" in api_response.json()["data"]
    assert "advertising" in api_response.json()["data"]


def test_source_registry_and_scheduler_metadata_are_exposed_to_admins():
    registry_response = client.get("/api/admin/source-registry")
    assert registry_response.status_code == 200
    payload = registry_response.json()
    assert payload["success"] is True
    assert "sources" in payload["data"]
    assert "scheduler" in payload["data"]

    page_response = client.get("/admin/source-registry")
    assert page_response.status_code == 200
    assert "Source Registry" in page_response.text or "மூலப் பதிவு" in page_response.text
    assert "Scheduler" in page_response.text or "திட்டமிடுபவர்" in page_response.text


def test_admin_audit_logs_are_exposed_on_api_and_page():
    admin_login = client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    assert admin_login.status_code == 200
    token = admin_login.json()["token"]

    api_response = client.get("/api/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert api_response.status_code == 200
    payload = api_response.json()
    assert payload["success"] is True
    assert isinstance(payload["data"], list)

    page_response = client.get("/admin/audit-logs", headers={"Authorization": f"Bearer {token}"})
    assert page_response.status_code == 200
    assert "Audit Logs" in page_response.text or "ஆடிட் பதிவு" in page_response.text
    assert "login" in page_response.text.lower()


def test_admin_scheduler_controls_are_exposed_on_api_and_page():
    admin_login = client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    assert admin_login.status_code == 200
    token = admin_login.json()["token"]

    api_response = client.get("/api/admin/scheduler", headers={"Authorization": f"Bearer {token}"})
    assert api_response.status_code == 200
    payload = api_response.json()
    assert payload["success"] is True
    assert "status" in payload["data"]
    assert "cron_expression" in payload["data"]

    trigger_response = client.post("/api/admin/scheduler/run", headers={"Authorization": f"Bearer {token}"})
    assert trigger_response.status_code == 200
    assert trigger_response.json()["success"] is True

    page_response = client.get("/admin/scheduler", headers={"Authorization": f"Bearer {token}"})
    assert page_response.status_code == 200
    assert "Scheduler" in page_response.text or "திட்டமிடுபவர்" in page_response.text


def test_scheme_fetch_scheduler_is_active_service_with_operational_state():
    from services import get_scheme_scheduler

    scheduler = get_scheme_scheduler()
    assert scheduler.job_name == "government_scheme_fetch"
    assert scheduler.cron_expression == "0 */12 * * *"
    assert scheduler.frequency == "every 12 hours"

    scheduler.trigger_manual_run()
    assert scheduler.status in {"running", "active"}
    assert scheduler.last_run is not None
    assert scheduler.next_run is not None


def test_source_registry_and_fetch_job_use_authoritative_sources_and_record_operation():
    from services import get_source_registry, run_scheme_fetch_job

    registry = get_source_registry()
    assert any(source["name"] == "PM-Kisan" for source in registry)
    assert any(source["name"] == "Tamil Nadu Agriculture Department" for source in registry)
    assert all(source["trust_level"] in {"high", "medium"} for source in registry)

    result = run_scheme_fetch_job(force=True)
    assert result["status"] in {"success", "warning"}
    assert result["source_count"] >= 2
    assert result["updated_sources"]


def test_scheme_fetch_job_tracks_retries_and_source_failures():
    from services import get_scheme_fetch_history, run_scheme_fetch_job

    result = run_scheme_fetch_job(force=True)
    assert result["status"] in {"success", "warning"}
    assert "attempts" in result
    assert "failed_sources" in result
    assert "retry_count" in result
    assert "retry_policy" in result
    assert result["retry_policy"]["max_retries"] >= 2
    assert result["retry_policy"]["timeout_seconds"] >= 10
    assert "backoff_seconds" in result["retry_policy"]
    assert len(result["attempts"]) >= 2

    history = get_scheme_fetch_history()
    assert isinstance(history, list)
    assert len(history) >= 1
    assert any(item.get("source_name") for item in history)


def test_admin_fetch_history_is_exposed_on_api_and_page():
    admin_login = client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    assert admin_login.status_code == 200
    token = admin_login.json()["token"]

    api_response = client.get("/api/admin/fetch-history", headers={"Authorization": f"Bearer {token}"})
    assert api_response.status_code == 200
    payload = api_response.json()
    assert payload["success"] is True
    assert isinstance(payload["data"], list)

    page_response = client.get("/admin/fetch-history", headers={"Authorization": f"Bearer {token}"})
    assert page_response.status_code == 200
    assert "Fetch History" in page_response.text or "டேட்டா பரிமாற்ற வரலாறு" in page_response.text


def test_admin_pilot_readiness_and_feedback_loop_are_exposed_on_api_and_page():
    admin_login = client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    assert admin_login.status_code == 200
    token = admin_login.json()["token"]

    api_response = client.get("/api/admin/pilot-readiness", headers={"Authorization": f"Bearer {token}"})
    assert api_response.status_code == 200
    payload = api_response.json()
    assert payload["success"] is True
    assert "checklist" in payload["data"]
    assert "feedback_template" in payload["data"]

    page_response = client.get("/admin/pilot-readiness", headers={"Authorization": f"Bearer {token}"})
    assert page_response.status_code == 200
    assert "Pilot Readiness" in page_response.text or "பைலட் தயார் நிலை" in page_response.text


def test_pilot_readiness_warns_when_source_risk_or_review_queue_is_unhealthy():
    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO government_scheme_updates (
                id, title_ta, summary_ta, eligibility_ta, benefits_ta, apply_steps_ta,
                category, scheme_type, source_name, source_url, is_archived, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "SCHEME-PILOT-READINESS-WARN",
                "Pilot readiness warning sample",
                "This sample should trigger a pilot readiness warning because it comes from an untrusted source.",
                "Eligibility details",
                "Benefits details",
                "Application steps",
                "subsidy",
                "central",
                "Unverified Local Notice Board",
                "https://example.com/pilot-warning",
                0,
                __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat(),
            ),
        )

    admin_login = client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    token = admin_login.json()["token"]
    response = client.get("/api/admin/pilot-readiness", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["data"]["status"] == "warning"
    assert any(item["status"] == "warning" for item in payload["data"]["checklist"])


def test_shell_home_navigation_does_not_reload_the_shell():
    response = TestClient(app).get("/", headers={"accept": "text/html"})
    assert response.status_code == 200
    assert 'data-page="/home"' in response.text
    assert 'data-page="/"' not in response.text
    assert 'src="/dashboard"' in response.text


def test_form_submission_registers_user_and_persists_data():
    username = f"form_user_{__import__('uuid').uuid4().hex[:8]}"
    isolated_client = TestClient(app)

    response = isolated_client.post(
        "/api/v1/auth/register",
        data={
            "username": username,
            "password": "SecurePass123",
            "role": "farmer",
            "full_name": "Form Farmer",
            "email": "formfarmer@example.com",
            "phone": "9876543211",
            "village": "Kallakurichi",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "pending_verification"

    with __import__("sqlite3").connect("digital_farming.db") as conn:
        row = conn.execute(
            "SELECT username, full_name, email, phone, status FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    assert row is not None
    assert row[0] == username
    assert row[1] == "Form Farmer"
    assert row[2] == "formfarmer@example.com"
    assert row[3] == "9876543211"
    assert row[4] == "pending_verification"


def test_registration_creates_pending_user_and_requires_otp_verification_before_login():
    username = f"otp_user_{__import__('uuid').uuid4().hex[:8]}"
    isolated_client = TestClient(app)

    response = isolated_client.post(
        "/api/v1/auth/register",
        json={
            "username": username,
            "password": "SecurePass123",
            "role": "farmer",
            "phone": "9876543210",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "pending_verification"
    assert payload["data"].get("otp_code")

    with __import__("sqlite3").connect("digital_farming.db") as conn:
        row = conn.execute("SELECT status, otp_code FROM users WHERE username = ?", (username,)).fetchone()
    assert row is not None
    assert row[0] == "pending_verification"
    otp = row[1]

    blocked_login = isolated_client.post("/auth/login", json={"username": username, "password": "SecurePass123"})
    assert blocked_login.status_code == 401

    verify_response = isolated_client.post(
        "/api/v1/auth/verify-otp",
        json={"username": username, "otp_code": otp},
    )
    assert verify_response.status_code == 200
    assert verify_response.json()["success"] is True

    final_login = isolated_client.post("/auth/login", json={"username": username, "password": "SecurePass123"})
    assert final_login.status_code == 200
    assert final_login.json()["role"] == "farmer"


def test_refresh_token_returns_new_token_and_logout_clears_session_cookie():
    isolated_client = TestClient(app)
    login = isolated_client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    assert login.status_code == 200
    original_token = login.json()["token"]

    refresh = isolated_client.post(
        "/api/v1/auth/refresh",
        headers={"Authorization": f"Bearer {original_token}"},
    )
    assert refresh.status_code == 200
    refreshed = refresh.json()
    assert refreshed["success"] is True
    assert refreshed["data"]["token"]
    assert refreshed["data"]["token"] != original_token

    admin_check = isolated_client.get(
        "/api/admin/overview",
        headers={"Authorization": f"Bearer {refreshed['data']['token']}"},
    )
    assert admin_check.status_code == 200

    logout = isolated_client.post("/auth/logout")
    assert logout.status_code == 200
    assert logout.cookies.get("digital_farming_session") in {"", None}


def test_failed_login_attempts_lock_account_after_threshold():
    username = f"lockout_{__import__('uuid').uuid4().hex[:8]}"
    isolated_client = TestClient(app)
    create_user(username, "StrongPass123", "farmer")

    for _ in range(5):
        response = isolated_client.post("/auth/login", json={"username": username, "password": "wrongpass"})
        assert response.status_code == 401

    locked = isolated_client.post("/auth/login", json={"username": username, "password": "StrongPass123"})
    assert locked.status_code == 401

    with __import__("sqlite3").connect("digital_farming.db") as conn:
        row = conn.execute("SELECT status, failed_login_attempts FROM users WHERE username = ?", (username,)).fetchone()
    assert row is not None
    assert row[0] == "locked"
    assert row[1] >= 5


def test_admin_can_unlock_a_locked_user():
    username = f"unlock_{__import__('uuid').uuid4().hex[:8]}"
    isolated_client = TestClient(app)
    create_user(username, "StrongPass123", "farmer")

    with __import__("sqlite3").connect("digital_farming.db") as conn:
        conn.execute(
            "UPDATE users SET status = ?, failed_login_attempts = ? WHERE username = ?",
            ("locked", 5, username),
        )

    admin_login = isolated_client.post("/auth/login", json={"username": "admin1", "password": "admin123"})
    assert admin_login.status_code == 200
    token = admin_login.json()["token"]

    response = isolated_client.post(
        f"/api/users/{username}/unlock",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["data"]["status"] == "active"

    with __import__("sqlite3").connect("digital_farming.db") as conn:
        row = conn.execute("SELECT status, failed_login_attempts FROM users WHERE username = ?", (username,)).fetchone()
    assert row is not None
    assert row[0] == "active"
    assert row[1] == 0


def test_repeated_login_failures_are_rate_limited():
    username = f"ratelimit_{__import__('uuid').uuid4().hex[:8]}"
    isolated_client = TestClient(app)
    create_user(username, "StrongPass123", "farmer")

    for _ in range(5):
        response = isolated_client.post("/auth/login", json={"username": username, "password": "wrongpass"})
        assert response.status_code == 401

    throttled = isolated_client.post("/auth/login", json={"username": username, "password": "wrongpass"})
    assert throttled.status_code == 429
    assert "Too many" in throttled.json()["detail"]


def test_login_page_exposes_registration_and_recovery_ctas():
    response = client.get("/login")
    assert response.status_code == 200
    assert "Login" in response.text or "உள்நுழை" in response.text
    assert "Register" in response.text or "பதிவு" in response.text
    assert "Forgot password" in response.text or "கடவுச்சொல்" in response.text


def test_registration_page_renders_farmer_onboarding_steps():
    response = client.get("/register")
    assert response.status_code == 200
    assert "பதிவு" in response.text or "Register" in response.text
    assert "கிராமம்" in response.text or "Village" in response.text
    assert "நிலம்" in response.text or "Farm" in response.text
    assert "படிவம்" in response.text or "Form" in response.text


def test_password_recovery_pages_render_public_auth_flow_paths():
    forgot = client.get("/forgot-password")
    assert forgot.status_code == 200
    assert "Forgot" in forgot.text or "கடவுச்சொல்" in forgot.text

    reset = client.get("/reset-password")
    assert reset.status_code == 200
    assert "Reset" in reset.text or "மீட்டமை" in reset.text


def test_protected_pages_redirect_to_login_without_session_cookie():
    isolated_client = TestClient(app)
    response = isolated_client.get("/dashboard", follow_redirects=False)
    assert response.status_code in {302, 307}
    assert response.headers.get("location", "").startswith("/login")


def test_profile_page_renders_user_and_farm_summary():
    response = client.get("/profile?username=operator1")
    assert response.status_code == 200
    assert "சுயவிபரம்" in response.text or "Profile" in response.text
    assert "operator1" in response.text or "ஆபரேட்டர்" in response.text
    assert "கிராமம்" in response.text or "Village" in response.text
    assert "நிலம்" in response.text or "Farm" in response.text


def test_sustainability_and_traceability_pages_render_farmer_summary():
    sustainability_response = client.get("/sustainability?farm_size_ha=5&soil_carbon_tons=2.4&water_use_liters=4200&energy_use_kwh=320")
    assert sustainability_response.status_code == 200
    assert "நிலையான" in sustainability_response.text or "Sustainability" in sustainability_response.text
    assert "கார்பன்" in sustainability_response.text or "Carbon" in sustainability_response.text
    assert "பரிந்துரை" in sustainability_response.text or "Recommendation" in sustainability_response.text

    traceability_response = client.get("/traceability?farmer=Kumaran&batch=RICE-24A&location=Kallakurichi&quality_grade=A")
    assert traceability_response.status_code == 200
    assert "கயிறு" in traceability_response.text or "Traceability" in traceability_response.text
    assert "Kumaran" in traceability_response.text or "குமரன்" in traceability_response.text
    assert "வகுப்பு" in traceability_response.text or "Grade" in traceability_response.text
