# Government Schemes Module — Product Roadmap (Tamil Version)

## 1. Module Objective

இந்த Government Schemes module-ன் நோக்கம்:

- இந்தியா மற்றும் தமிழ்நாடு அரசின் வேளாண்மை தொடர்பான புதிய திட்டங்கள், மானியங்கள், பயிர் காப்பீடு, கருவி உதவிகள், பயிற்சி திட்டங்கள், நிதி உதவிகள் போன்ற அனைத்தையும் AI உதவியுடன் தானாகவே பெறுதல்
- சுருக்கமாக தமிழில் காட்டுதல்
- வாராந்திர archive-ல் சேமித்தல்
- விவசாயிகள், புல அலுவலர்கள், நிர்வாகிகள் மற்றும் அரசு ஆதரவு குழுக்களுக்கு நேரடியான மற்றும் நம்பகமான தகவல் சேவை வழங்குதல்

## 2. Product Vision

விவசாயிகள் தங்கள் பயிர், நிலம், வருமானம், மற்றும் அரசின் ஆதரவு தொடர்பான தகவல்களை சரியான நேரத்தில் அறிந்து கொள்ள வேண்டும். இந்த மாட்யூல் என்பது ஒரு “trusted agritech information layer” ஆக செயல்படும். எந்தவொரு திட்டமும் அங்கீகரிக்கப்பட்ட அரசுத் தரவு ஆதாரங்களிலிருந்து பெறப்பட வேண்டும். AI ஆனது அதன் சுருக்கமான விளக்கத்தை தமிழில் வழங்கும், ஆனால் தகவல் நம்பகத்தன்மை மற்றும் காலக்கெடு முதன்மையானது.

## 3. Target Users

- சிறு மற்றும் குறு விவசாயிகள்
- புல அலுவலர்கள்
- வேளாண்மை ஆலோசகர்கள்
- கூட்டுறவு சங்கங்கள்
- அரசு திட்ட செயல்பாட்டு குழுக்கள்
- விவசாயிகளின் குடும்ப உறுப்பினர்கள் மற்றும் ஆதரவாளர்கள்

## 4. User Needs

- மானியம், நிதி, காப்பீடு, உரம், பயிற்சி, தொழில்நுட்ப உதவி ஆகியவற்றை எளிதாக அறிந்து கொள்ள வேண்டும்
- புதிய அறிவிப்புகள் 7 நாட்களுக்குள் தெளிவாகக் காட்டப்பட வேண்டும்
- பழைய செய்திகள் archive-ஆக மாறி, தேடலில் இருப்பதை உறுதி செய்ய வேண்டும்
- தகவல் எளிய தமிழில் இருக்க வேண்டும்
- AI விளக்கம் சுருக்கமாக, நம்பகமாக, மற்றும் செயல்படத்தக்கதாக இருக்க வேண்டும்

## 5. Problem Statement

விவசாயிகள் பெரும்பாலும் அரசுத் திட்ட தகவல்களை:

- அரசின் அதிகாரப்பூர்வ இணையதளங்களில் தேடி கண்டுபிடிக்க வேண்டும்
- PDF மற்றும் விசாரணை ஆவணங்களை படிக்க வேண்டும்
- அங்கீகரிக்கப்படாத அல்லது சிதைந்த தகவல்களை நம்ப வேண்டியிருக்கும்
- திட்ட காலக்கெடு, தகுதி, மற்றும் விண்ணப்ப முறை பற்றி தெளிவாக புரிந்து கொள்ள முடியாது

இதனால் தகவல் கசியும் சிக்கல், தாமதமான உரிமை கோரிக்கை, மற்றும் வாய்ப்புகள் கிடைக்காமல் போகிறது.

## 6. Goals

- அரசுத் திட்டங்களின் அதிகாரப்பூர்வ புதுப்பிப்புகளை தானாக பெறுதல்
- Tamil summary generation மூலம் சுருக்கமான நுண்ணறிவை வழங்குதல்
- 7 நாட்கள் “Latest Updates” panel-ஐ உறுதி செய்தல்
- Archive flow-ஐ தானியங்கி முறையில் செயல்படுத்துதல்
- AI output quality மற்றும் Tamil readability-ஐ தொடர்ந்து மேம்படுத்துதல்

## 7. Success Metrics

- அரசுத் திட்ட புதுப்பிப்புகள் சரியான நேரத்தில் பதிவாகுதல்
- அரைமனித பரிசோதனை / AI validation-இல் 80% மேல் score
- Tamil readability score 85%+ நிலையை அடைதல்
- archive logic 100% சரியாக செயல்படுதல்
- fetch success rate 95%+ அடைதல்

## 8. Functional Requirements

### 8.1 Data Retrieval

- TN Govt Agriculture Portal
- TNAU
- PM-Kisan
- PMFBY
- Agri Infrastructure Fund
- NABARD updates
- Ministry of Agriculture & Farmers Welfare

மூலங்களிலிருந்து data pull செய்ய வேண்டும். raw English content DB-இல் சேமிக்கப்பட வேண்டும்.

### 8.2 AI Summarization and Translation

Each scheme item should be processed to create:

- Title (Tamil)
- Short Summary (Tamil)
- Eligibility (Tamil)
- Benefits (Tamil)
- Application Steps (Tamil)

AI layer must also tag metadata such as:

- scheme type
- central/state scheme
- category: subsidy / loan / insurance / training

### 8.3 Weekly Update Logic

- தினசரி அல்லது 12 மணி நேரம் fetch cycle
- last 7 days content only shows in Latest Updates
- older records move to archive

### 8.4 Tamil UI Requirements

- Farmer-friendly Tamil language
- Big readable fonts
- Minimal clutter
- Simple cards and detail pages
- Tabs:
  - புதிய அறிவிப்புகள் (Last 7 Days)
  - காப்பக அறிவிப்புகள் (Archive)

## 9. Non-Functional Requirements

- Low-bandwidth mobile-first experience
- Validated official source trust model
- Tamil text should not contain excessive English leftovers
- secure and auditable fetch pipeline
- minimal downtime and high reliability
- admin-only manual refresh should be available

## 10. Data Model

### GovSchemeRaw

- id
- title_en
- content_en
- source_url
- fetched_date

### GovSchemeProcessed

- id
- title_ta
- summary_ta
- eligibility_ta
- benefits_ta
- apply_steps_ta
- created_date
- is_archived
- category
- scheme_type
- source_state

## 11. Archive Logic

```python
if created_date < today - timedelta(days=7):
    is_archived = True
```

## 12. API Design

### GET /schemes/latest

Returns last 7 days of Tamil scheme updates.

### GET /schemes/archive

Returns archived schemes with filters and grouping.

### GET /scheme/{id}

Returns full details of one scheme record.

### POST /fetch/update

Triggers admin-only manual fetch.

### GET /schemes?category={category}

Filters by category such as subsidy, loan, insurance, training.

## 13. UI / UX Requirements

### Latest Updates Panel

Shows only the last 7 days:

- Tamil title
- short summary
- “மேலும் படிக்க” button

### Archive Panel

Shows older updates:

- category filter
- search support
- year-wise grouping
- detail view

### Tamil Writing Rules

- Prefer simple Tamil words over complex terms
- Use short, direct sentence structures
- Keep headings in large readable size
- Use icons for types such as loan / subsidy / insurance / training

## 14. Monitoring and Alerts

### Metrics

- fetch success rate
- translation accuracy
- summary quality
- Tamil readability score
- archive success rate

### Alerts

- fetch fails
- translation fails
- summary is empty
- Tamil output still contains too much English

## 15. 6-Month Product Roadmap

### Phase 1 — Data Source Integration (Weeks 1–4)

- Identify official government sources
- Build automated fetch pipelines
- Create unified GovSchemeData API

### Phase 2 — AI Summarization Engine (Weeks 4–8)

- English → Tamil translation pipeline
- Summarize key fields into Tamil
- Apply rule-based validation for quality

### Phase 3 — Weekly Update Logic (Weeks 8–10)

- Store daily updates
- Show only 7-day content
- Move older data to archive

### Phase 4 — Tamil UI/UX (Weeks 10–14)

- Tamil-first UI
- Tab-based layout
- Quick cards + detail page

### Phase 5 — Testing & Validation (Weeks 14–18)

- Readability testing with farmers
- AI summary testing
- API reliability and archive validation

### Phase 6 — Deployment & Monitoring (Weeks 18–20)

- Production deployment
- Monitoring dashboards
- Monthly model updates and support review

## 16. Technical Implementation Plan

### Data Fetch Layer

- Use cron or scheduler to fetch every 12 hours
- Use RSS / official APIs / HTML parsing where available
- Save raw English content and source URL

### AI Processing Layer

1. Content Cleaning
2. AI Summarization
3. English → Tamil Translation
4. Tamil Text Optimization
5. Metadata Tagging

### Tech Stack

- Python + FastAPI
- HuggingFace summarization models
- IndicTrans2 Tamil translation
- Rule-based grammar validation

## 17. Acceptance Criteria

1. Government scheme items are fetched from official sources.
2. Each item is transformed into Tamil summary fields.
3. Latest Updates shows only the last 7 days.
4. Older entries are moved to archive automatically.
5. Tamil text is readable and farmer-friendly.
6. Admin can trigger a manual refresh.
7. Monitoring alerts catch fetch/translation failures.

## 18. Final Recommendation

This module must be designed as a trusted, farmer-first information feed and not as a generic news aggregator. The key success factors are trustworthy data sources, accurate AI summarization, readable Tamil content, and a clean archive workflow. The system should always favor clarity, relevance, and accessibility for low-literacy rural users.

## 19. Final Output Example (Tamil UI)

### புதிய அரசு திட்டம்: PM-Kisan 16வது தவணை

**சுருக்கம்:** சிறு மற்றும் குறைந்த நிலம் கொண்ட விவசாயிகளுக்கு ரூ.2,000 நேரடி நிதி உதவி.

**தகுதி:** 2 ஹெக்டேர் வரை நிலம்.

**விண்ணப்பம்:** e-KYC + Aadhaar இணைப்பு.

(Displayed only for 7 days, then moved to archive.)
