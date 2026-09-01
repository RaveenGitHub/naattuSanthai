# Government Schemes Page — Product Requirements Document (PRD)

## 1. Overview

This module provides a trusted, Tamil-first information layer for farmers to discover active government schemes, subsidies, crop insurance, machinery support, training programs, and financial assistance from central and state government sources.

The feature is built around four critical outcomes:

- fetch official scheme information automatically
- convert long-form English government content into short, farmer-friendly Tamil summaries
- show only recent updates in the main panel
- move older records to archive for historical review

---

## 2. Objective

தமிழ்நாடு மற்றும் இந்திய அரசின் வேளாண்மை திட்டங்கள், மானியங்கள், பயிர் காப்பீடு, கருவி உதவிகள், பயிற்சி திட்டங்கள் போன்ற அனைத்தையும் AI உதவியுடன் தானாகவே பெறுதல், தமிழில் சுருக்கமாக காட்டுதல், மற்றும் வாராந்திர archive-ல் சேமித்தல்.

### Desired outcome

- Farmers can access relevant scheme information without visiting multiple official portals
- Operators and officers can guide farmers toward schemes more quickly
- Scheme updates stay fresh, trustworthy, and readable in Tamil
- Older updates remain searchable in archive without cluttering the main view

---

## 3. Target Users

### Primary users

- Small and marginal farmers
- Women farmers and tenant farmers
- Village-level agricultural officers
- Agronomists and extension workers
- Cooperative and government support staff

### User needs

- Understand eligibility quickly
- See benefits in simple Tamil
- Know how to apply without friction
- Access only relevant schemes for their crop or region

---

## 4. Problem Statement

Farmers often miss timely opportunities because government scheme information is fragmented across multiple sources, often in English, and sometimes buried in long PDF or portal content. This creates a gap between availability of support and actual farmer adoption.

The feature solves this by:

- aggregating trusted public sources
- translating and summarizing the data for farmer use
- ensuring the content remains current and understandable
- using archive rules to keep latest information actionable

---

## 5. Goals and Success Metrics

### Goals

1. Increase scheme awareness among farmers and support staff
2. Make scheme discovery faster and more understandable
3. Reduce information overload by surfacing only recent updates
4. Improve trust through official-source-based data
5. Support bilingual or Tamil-first interpretation for field users

### Success metrics

- 90%+ of scheme items available from verified official data sources
- Tamil summary readability accepted by a field review group
- Fresh scheme panel shows only last 7 days of updates
- Archive logic correctly moves older records out of main view
- Admin can manually trigger fetch and review system status

---

## 6. Functional Requirements

### 6.1 Data retrieval

- Fetch officially published scheme information from trusted public sources
- Store raw source data before processing
- Track the source URL, source name, and fetch time
- Support scheduled or manual refresh

### 6.2 AI processing

- English to Tamil translation
- Short farmer-friendly summary generation
- Automatic field extraction:
  - Title
  - Summary
  - Eligibility
  - Benefits
  - Application steps
- Tamil grammar cleanup and readability optimization
- Duplicate detection and content validation

### 6.3 Latest vs archive flow

- Show records from last 7 days in the main “Latest Updates” panel
- Move older records to archive automatically
- Keep archived records searchable and filterable

### 6.4 Detail view

- Each scheme card opens a dedicated detail page
- Show complete Tamil-ready summary and eligibility details
- Include source attribution

### 6.5 Search and filtering

- Filter by scheme category
- Search by keyword or scheme title
- Support basic year-wise archive grouping

---

## 7. Non-Functional Requirements

- Mobile-first experience for farmer use
- Low-bandwidth friendly UI
- Tamil-first interface with simple, readable language
- Strong role-based access for admin operations
- Audit logs for fetch and validation failures
- Reliability through retries and source fallback logic
- Privacy respecting public information only

---

## 8. Trusted Data Sources

### Government / official sources

- Tamil Nadu Agriculture Department
- TNAU official portal
- Ministry of Agriculture & Farmers Welfare (India)
- PM-Kisan
- PMFBY (Crop Insurance)
- NABARD
- Agri Infrastructure Fund
- TN e-Governance Agriculture Schemes

### Source requirements

- Only official, authorized, and public-sector sources
- Source name and URL should always be stored
- Data should be validated before publishing
- Non-official or low-trust content should not be promoted in public UI

---

## 9. AI Processing Requirements

The AI pipeline must support:

- English → Tamil translation
- Short summary generation for farmers
- Structured extraction of:
  - title
  - summary
  - eligibility
  - benefits
  - application steps
- Tamil grammar correction
- Readability optimization for low-literacy and mobile farmers
- Confidence scoring and validation checks

### AI validation rules

- Do not publish empty summaries
- Do not publish generic or unrelated content
- Flag low-confidence translations for manual review
- Reject low-quality or broken Tamil before public display

---

## 10. Soil Testing Page — Requirements

### 10.1 Objective

மண் பரிசோதனை கருவி / IoT சென்சார் / லேப் ரிப்போர்ட் மூலமாக பெறப்படும் தரவை AI மூலம் தமிழில் சுருக்கமாகக் காட்டுதல்.

The Soil Testing module turns raw soil analytics into farmer-friendly Tamil recommendations for crop choice, fertilizer use, irrigation, and soil improvement.

### 10.2 Trusted data sources

- TNAU Soil Health Card guidelines
- Tamil Nadu Agriculture Department soil manuals
- ICAR Soil Science Division
- Government Soil Health Card Scheme
- Local lab testing standards

### 10.3 Data inputs

- pH value
- NPK levels
- Organic carbon
- Moisture
- EC (Electrical Conductivity)
- Micronutrients (Zn, Fe, Mn, Cu)

### 10.4 AI processing requirements

- Convert raw soil data to Tamil summary
- Recommend:
  - suitable crops
  - fertilizer plan
  - irrigation plan
  - soil improvement tips
- Tamil translation and readability optimization
- Validate output to ensure recommendations are plain-language, relevant, and technically safe

### 10.5 Data storage requirements

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

### 10.6 Tamil UI requirements

#### Input page

- Manual entry
- IoT device sync
- Lab report upload

#### Result page

- Tamil summary
- Crop recommendations
- Fertilizer plan
- Irrigation plan
- Soil improvement tips

#### Tamil display rules

- Use simple Tamil
- Use icons for soil parameters
- Optional Tamil voice reading

### 10.7 Summary table (high-level comparison)

| Module             | Trusted Sources              | AI Tasks                   | Tamil Display    | Archive Logic |
| ------------------ | ---------------------------- | -------------------------- | ---------------- | ------------- |
| Government Schemes | TN Govt, India Govt, NABARD  | Summarize, translate       | Latest + archive | 7-day rule    |
| Disease Detection  | TNAU, ICAR, FAO              | Image inference, translate | Scan + result    | No archive    |
| Soil Testing       | TNAU, ICAR, Soil Health Card | Data → Tamil summary       | Input + result   | No archive    |

---

## 11. Data Storage Requirements

### 11.1 GovSchemeRaw

Purpose: raw English source content

Fields:

- id
- title_en
- content_en
- source_name
- source_url
- fetched_at
- source_type
- raw_metadata

### 11.2 GovSchemeProcessed

Purpose: final Tamil-friendly and structured scheme data

Fields:

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

### Archive logic

```python
if created_at < today - timedelta(days=7):
    is_archived = True
```

---

## 11. UI Requirements

### Latest Panel (புதிய அறிவிப்புகள்)

- Last 7 days only
- Tamil title
- Brief Tamil summary
- “மேலும் படிக்க” action
- Category tag and highlight status

### Archive Panel (காப்பக அறிவிப்புகள்)

- Older items only
- Search + filter support
- Year-wise or period-wise grouping
- Detailed view for older archive records

### Tamil display rules

- Prefer simple Tamil words over complex terminology
- Keep content easy to scan on mobile screens
- Use icons for scheme categories
- Use short titles and direct actions
- Ensure large readability for low-literacy users

---

## 12. API Requirements

### Proposed endpoints

- GET /api/schemes/latest
- GET /api/schemes/archive
- GET /api/scheme/{id}
- GET /api/schemes?category={category}
- POST /api/fetch/update
- GET /api/fetch/status

### Expected behavior

- Latest endpoint returns recent scheme records
- Archive endpoint returns older records
- Detail endpoint returns full processed scheme data
- Fetch/update is admin-only
- Fetch/status returns health and summary detection data

---

## 13. Scope

### In scope

- official scheme discovery
- English raw content acquisition
- Tamil translation and summarization
- latest/archive logic
- search and filter
- farmer-friendly detail page
- admin fetch trigger and monitoring

### Out of scope

- direct online application submission to government portals
- payment settlement or disbursal
- identity verification platform
- full financial processing integration

---

## 15. Acceptance Criteria

1. Official scheme data is fetched from trusted source list
2. English raw content is stored before processing
3. AI transforms content into Tamil summary and structured fields
4. Latest panel shows only items from the last 7 days
5. Older items are archived and hidden from the latest view
6. Archived items remain searchable and filterable
7. Scheme detail view is readable and mobile-friendly
8. Admin can trigger a manual update and monitor fetch health
9. Low-confidence or poor Tamil content is rejected before public display

---

## 15. Risks and Mitigation

### Risk 1: Data inconsistency from source portals

Mitigation:

- official source whitelist
- source metadata tracking
- source quality checks

### Risk 2: Poor Tamil quality

Mitigation:

- rule-based validation
- manual review for flagged records
- readability checks before publish

### Risk 3: Duplicate scheme entries

Mitigation:

- deduplication by title + source + date
- source-aware normalization

### Risk 4: Low usability for farmers

Mitigation:

- simple wording
- short summaries
- mobile-first layout and icons

---

## 17. Recommendation

This module should be treated as a trusted agri-information and support layer, not as a generic content feed. Accuracy, readability, and timeliness are more important than volume. The product should prioritize clarity and trust for farmers over feature complexity.

---

## 17. Final Decision

The Government Schemes module is a high-value feature for farmer enablement and should be implemented with:

- official-source-first ingestion
- AI-assisted Tamil summarization
- archive rules to reduce clutter
- farmer-readable UX
- admin monitoring and verification controls
