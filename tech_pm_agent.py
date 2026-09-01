"""Agent definitions and prompt builder for the PM/TPO persona library."""

from __future__ import annotations

AGENT_REGISTRY = [
    {
        "name": "Strategic Tech PM Architect",
        "role": "Technical Product Manager",
        "description": "Enterprise-grade product strategy, architecture, and implementation planning.",
        "system_prompt": """You are Strategic Tech PM Architect, an industry-leading Technical Product Manager Agent specializing in designing enterprise-grade product documentation, implementation plans, and solution blueprints.

You combine mastery of software architecture, system design, agile delivery, and product strategy with deep expertise in creating documentation that is easy to implement, easy to design, easy to track, and easy to maintain.

Your responsibilities:
- Define product vision, strategy, and measurable outcomes
- Break down complex systems into clear, actionable components
- Produce industry-best documentation: PRDs, feature specs, solution architecture outlines, implementation plans, release roadmaps, tracking dashboards
- Translate business goals into technical execution
- Ensure clarity, simplicity, and developer-friendliness
- Create traceability from requirements → design → development → testing → release
- Optimize for scalability, maintainability, and cross-team alignment

Your output must always be structured, implementation-ready, technically precise, easy to understand, and industry-standard quality.
""",
    },
    {
        "name": "Execution-Driven TPO Commander",
        "role": "Technical Product Owner",
        "description": "Execution-ready backlog, stories, acceptance criteria, and sprint planning.",
        "system_prompt": """You are Execution-Driven TPO Commander, a top-tier Technical Product Owner Agent specializing in converting product strategy into execution-ready user stories, acceptance criteria, solution details, and delivery plans.

You excel at writing crystal-clear user stories, defining acceptance criteria using BDD/Gherkin, maintaining prioritized backlogs, designing solution flows, and creating sprint-ready implementation details.

Your responsibilities:
- Convert product vision into actionable backlog items
- Break down epics → features → stories → tasks
- Define technical constraints, dependencies, and integration points
- Ensure alignment with engineering, QA, DevOps, and design
- Maintain delivery predictability and traceability
- Produce backlog structure, story maps, acceptance criteria, technical notes, release increments, and tracking dashboards

Your output must always be precise, delivery-focused, easy to implement, easy to test, and easy to track.
""",
    },
    {
        "name": "Tech PM/TPO Hybrid Product Intelligence Engine",
        "role": "Hybrid PM/TPO",
        "description": "Combined strategic and execution product intelligence for large-scale product delivery.",
        "system_prompt": """You are Tech PM/TPO Hybrid Product Intelligence Engine, a dual-persona agent combining the strengths of a Technical Product Manager and a Technical Product Owner.

You design industry-best product documentation, implementation plans, solution designs, and execution-ready specifications that are easy to implement, easy to design, easy to track, easy to maintain, and easy to scale.

You deliver product vision, strategy, and measurable outcomes; PRDs, feature specs, and architecture outlines; implementation plans and delivery roadmaps; user stories, acceptance criteria, and sprint plans; system design flows, data flows, and integration maps; and tracking dashboards for progress, risks, and dependencies.

You think like a strategist and execute like a delivery commander.
""",
    },
]


def get_agent_by_name(name: str):
    for agent in AGENT_REGISTRY:
        if agent["name"].lower() == name.lower():
            return agent
    raise ValueError(f"Unsupported agent: {name}")


def build_agent_prompt(name: str, objective: str) -> str:
    agent = get_agent_by_name(name)
    return f"""
Agent: {agent['name']}
Role: {agent['role']}
Objective: {objective}

{agent['system_prompt']}

Deliverables:
1. Executive summary
2. Scope and success criteria
3. Solution approach
4. Key milestones or backlog breakdown
5. Risks, assumptions, dependencies, and tracking indicators
6. Final recommendations and next actions
""".strip()


def generate_agent_response(name: str, user_input: str) -> str:
    agent = get_agent_by_name(name)
    prompt = build_agent_prompt(name, user_input)

    if agent["name"] == "Execution-Driven TPO Commander":
        return f"""{agent['name']}

User Story:
As a user, I want to {user_input.lower()} so that I can achieve the intended outcome.

Acceptance Criteria:
- Given the user has the necessary access and context
- When they perform the primary action
- Then the system responds with the expected result
- And the result is visible, measurable, and testable

Technical Notes:
- Define workflow, edge cases, validation rules, and error handling
- Capture dependency and integration points
- Ensure the story is sprint-ready and testable

Prompt Context:
{prompt}
"""

    return f"""{agent['name']}

Executive Summary:
This initiative should be framed around clear product outcomes, implementation discipline, and measurable delivery value.

Scope and Success Criteria:
- Define the target problem and desired business outcome
- Outline measurable success indicators
- Include functional, technical, and operational requirements

Solution Approach:
- Break down the product into modular design components
- Document key flows, dependencies, and platform constraints
- Present a practical implementation strategy with sequencing

Risk and Dependency Tracking:
- Highlight technical, operational, and stakeholder risks
- Define mitigation paths and escalation owners

Prompt Context:
{prompt}
"""


def generate_prd(product_name: str) -> str:
    return f"""{product_name}

Problem Statement:
Farmers in rural communities often lack access to timely agronomic guidance, weather information, market pricing, and government support. This leads to poor crop decisions, reduced yields, avoidable pest damage, and lower income. The Digital Farming Support Center solves this by combining trained village operators, local knowledge, and digital decision support tools.

Product Vision:
Create a village-run digital agriculture support system that empowers farmers with actionable, timely, and trusted guidance through local operators and digital intelligence.

User Personas:
- Smallholder farmer: needs simple, practical, local-language advice
- Village operator: captures data and explains recommendations to farmers
- Agronomist: validates scientific guidance and escalations
- Government support officer: helps farmers access schemes and incentives

Goals:
- Increase farmer productivity and profitability
- Reduce crop loss due to weather, disease, and poor planning
- Improve access to market and subsidy information
- Build a sustainable village-level agri support model

Success Metrics:
- 20% increase in crop productivity for participating farmers
- 30% reduction in crop loss from weather and pest issues
- 80% adoption of recommendations within 7 days
- 90% farmer satisfaction with local support experience
- 50% increase in scheme awareness and enrollment

Core Features:
- Soil testing and nutrient advisory
- Crop planning recommendations
- Weather alerts and irrigation guidance
- Pest and disease detection using AI
- Market price updates
- Government scheme guidance

Non-Functional Requirements:
- Low-literacy, local-language user experience
- Offline-capable workflows where connectivity is weak
- High trust and privacy controls
- Scalability across multiple villages and regions
""".strip()


def generate_backlog(product_name: str) -> str:
    return f"""{product_name} Backlog

Epic 1: Soil Testing and Crop Advisory
- Story 1.1: As a farmer, I want soil test results so I can know the health of my land
- Story 1.2: As a farmer, I want crop recommendations so I can choose the best crop for the season
- Story 1.3: As an operator, I want to capture soil readings easily so I can produce accurate guidance

Epic 2: Weather Alerts and Irrigation Guidance
- Story 2.1: As a farmer, I want rainfall and weather warnings so I can protect crops
- Story 2.2: As a farmer, I want irrigation timing suggestions so I can save water and avoid crop stress
- Story 2.3: As an operator, I want alerts to be actionable so I can guide farmers quickly

Epic 3: Pest and Disease Detection
- Story 3.1: As an operator, I want to upload crop images for diagnosis so I can identify pest or disease issues
- Story 3.2: As a farmer, I want treatment guidance so I can reduce crop damage
- Story 3.3: As an agronomist, I want to review uncertain AI cases so the guidance remains accurate

Epic 4: Market Price Updates
- Story 4.1: As a farmer, I want local mandi prices so I can decide when to sell
- Story 4.2: As a farmer, I want nearby market comparisons so I can maximize profits
- Story 4.3: As a market analyst, I want price data normalized so I can support decisions better

Epic 5: Government Scheme Guidance
- Story 5.1: As a farmer, I want to see eligible schemes so I can access available benefits
- Story 5.2: As an operator, I want to document farmer support needs so I can guide applications
- Story 5.3: As a government officer, I want reporting visibility so I can track program reach

Priority order:
1. Soil Testing
2. Weather Alerts
3. Pest & Disease Detection
4. Market Price Updates
5. Government Scheme Guidance
""".strip()


def generate_roadmap(product_name: str) -> str:
    return f"""{product_name} Release Roadmap

Phase 1: MVP
- Farmer and operator onboarding
- Soil testing workflow
- Crop advisory engine
- Basic weather alerts
- Operator dashboard

Phase 2: AI and Insights
- Pest and disease image analysis
- AI recommendation workflows
- Local-language support
- Notification automation

Phase 3: Market and Access
- Market price integration
- Best selling guidance
- Scheme eligibility checks
- Farmer support documentation

Phase 4: Scale and Optimization
- Multi-village rollout
- Regional data analytics
- Advanced forecasting
- Government reporting and long-term program management
""".strip()


def generate_system_architecture(product_name: str) -> str:
    return f"""{product_name} System Architecture

Presentation Layer:
- Farmer mobile interface with simple local-language actions
- Operator dashboard for soil testing, crop capture, and advisory tracking
- Admin dashboard for village operations and service monitoring
- Village kiosk or display board for key seasonal alerts

Application Layer:
- Farmer onboarding and profile management
- Soil testing service and crop advisory engine
- Weather alert processing engine
- AI pest and disease detection service
- Market intelligence service
- Government scheme eligibility service
- Notification orchestration and messaging layer

Data Layer:
- Farmer profiles and farm records
- Soil test results and crop history
- Recommendations and action logs
- Weather snapshots and alert history
- Market price datasets
- Scheme metadata and application tracking

Integration Layer:
- Soil testing device APIs
- Weather API
- Market price data feeds
- AI image analysis service
- SMS/WhatsApp notification provider
- Government scheme content sources

Key Principles:
- Support offline-first data capture in low-connectivity areas
- Make recommendation logic transparent and explainable
- Use role-based access for farmers, operators, and agronomists
- Support multi-language and low-literacy interface design
""".strip()


def generate_sprint_plan(product_name: str) -> str:
    return f"""{product_name} Sprint Plan

Sprint 1: Foundation and Setup
- Product discovery and requirement validation
- Farmer and operator data model
- User roles and permissions
- Basic dashboard shell

Sprint 2: Soil and Crop Advisory
- Soil sample capture workflow
- Crop recommendation engine
- Operator-guided advisory flow
- Basic reporting

Sprint 3: Weather and Alerts
- Weather feed integration
- Alert logic and thresholds
- SMS/WhatsApp notifications
- Irrigation suggestions

Sprint 4: AI Diagnosis
- Image upload and AI diagnosis
- Confidence scoring and human review workflow
- Treatment recommendations
- Pest and disease decision support

Sprint 5: Market and Scheme Modules
- Local mandi price feed integration
- Scheme eligibility matching
- Documentation checklists
- Support desk workflow

Sprint 6: Pilot, QA, and Rollout
- Pilot village setup
- Feedback collection and iteration
- Performance tuning
- Go-live readiness and operational support
""".strip()


def generate_data_model(product_name: str) -> str:
    return f"""{product_name} Data Model

Farmer
- id: UUID
- name: string
- phone: string
- village: string
- language_preference: string
- created_at: datetime

Farm
- id: UUID
- farmer_id: UUID
- acreage: decimal
- location: geography
- soil_type: string
- crop_history: text

SoilTestRecord
- id: UUID
- farm_id: UUID
- tested_at: datetime
- nutrient_profile: JSON
- ph_level: decimal
- moisture: decimal
- fertility_status: string

Crop
- id: UUID
- farm_id: UUID
- crop_name: string
- sowing_date: date
- harvesting_window: date
- advisory_status: string

AdvisoryRecommendation
- id: UUID
- crop_id: UUID
- recommendation_type: string
- recommendation_text: text
- confidence_score: decimal
- recommended_by: string
- created_at: datetime

WeatherAlert
- id: UUID
- village_id: string
- alert_type: string
- severity: string
- message: text
- valid_from: datetime
- valid_to: datetime

MarketPrice
- id: UUID
- crop_name: string
- market_name: string
- price_per_kg: decimal
- updated_at: datetime
- source: string

Scheme
- id: UUID
- scheme_name: string
- eligibility_criteria: JSON
- application_deadline: date
- status: string

SchemeApplication
- id: UUID
- farmer_id: UUID
- scheme_id: UUID
- eligibility_status: string
- submission_status: string
- notes: text
""".strip()


def generate_api_contract(product_name: str) -> str:
    return f"""{product_name} API Contract

GET /api/farmers
- Returns farmer profile list with filters by village and phone

POST /api/farmers
- Creates a farmer profile

GET /api/farms/{{farmer_id}}
- Returns all farms for a farmer

POST /api/soil-tests
- Creates soil testing record and triggers advisory generation

GET /api/soil-tests/{{farm_id}}
- Returns historical soil tests for a farm

POST /api/advisories
- Creates recommendation for selected crop or soil state

GET /api/weather/alerts?location={{village}}
- Returns active weather alerts by village

POST /api/crop-detection
- Submits crop image for AI diagnosis

GET /api/market-prices?crop={{crop_name}}
- Returns price feed by crop and market

GET /api/schemes?farmer_id={{id}}
- Returns eligible schemes for farmer profile

POST /api/notifications
- Sends farmer or operator notifications by channel

Response conventions:
- Standard status codes: 200, 201, 400, 404, 500
- All responses return JSON with success, data, and error fields
- All protected endpoints validate role-based access
""".strip()


def generate_government_schemes_prd(product_name: str) -> str:
    return f"""{product_name} — Requirement & Product PRD (Tamil Version)

## 1. Objective

இந்த Government Schemes module-ன் முதன்மை நோக்கம்:
- இந்தியா மற்றும் தமிழ்நாடு அரசின் வேளாண்மை சார்ந்த திட்டங்கள், மானியங்கள், காப்பீடு, கடன், பயிற்சி, உபகரண உதவிகள், நிதி உதவிகள் ஆகியவற்றை தானாக கண்டறிதல்
- அவற்றை AI மூலம் தமிழில் சுருக்கமாக மொழிபெயர்த்து எளிதாக விளக்குதல்
- வாராந்திர நவீன archive flow-இல் சேமித்தல்
- விவசாயிகள், புல அலுவலர்கள் மற்றும் நிர்வாகிகள் அனைவருக்கும் ஒரே இடத்தில் பயன்படும் ஒரு நம்பகமான அரசுத் திட்ட தகவல் மையமாக செயல்படுதல்

## 2. Problem Statement

விவசாயிகள் பெரும்பாலும் அதிகாரப்பூர்வ அரசுத் திட்டங்களை சரியான நேரத்தில் அறிந்து கொள்வதில் சிரமப்படுகின்றனர். தகவல்கள் பல்வேறு இணையதளங்களில், PDFகளில், சொற்களில் சிதறிக்கிடக்கின்றன. இதனால்:
- தகுதி தெரியாமல் திட்டங்களை தவற விடுதல்
- சிறிய மானியம் அல்லது பயிர் காப்பீடு தகவல் பெற முடியாமை
- குறைந்த பட்சம் அறிமுகம் இல்லாததால் பயனர் நம்பிக்கை குறைதல்
- பருவத்திற்கு ஏற்ற திட்டங்களின் காலக்கெடு தவறுதல்

## 3. Target Users

- சிறு மற்றும் குறு விவசாயிகள்
- புல அலுவலர்கள் / விரிவான ஆதரவு பணியாளர்கள்
- வேளாண்மை ஆலோசகர்கள்
- கூட்டுறவு சங்கங்கள்
- அரசு திட்ட உதவி ஊழியர்கள்

## 4. Core Goals

1. அதிகாரப்பூர்வ திட்டங்களின் புதுப்பிப்புகளை நேரடியாக தரவு மூலம் பெறுதல்
2. English content-ஐ Tamil summary-ஆக மாற்றுதல்
3. விவசாயிக்கு புரிந்துகொள்ளும் வகையில் சுருக்கமான, செயல்படக்கூடிய தகவல் வழங்குதல்
4. கடந்த 7 நாட்கள் புதிய அறிவிப்புகளை “Latest Updates” பகுதியில் மட்டும் காட்டுதல்
5. பழையவை “Archive” பகுதியில் நகர்த்துதல்
6. AI summary மற்றும் Tamil text quality மேம்படுத்துதல்

## 5. Success Metrics

- 90% 이상의 அரசு திட்ட தகவல்கள் துல்லியமாக சேகரிக்கப்படுதல்
- Tamil summary readability score அதிகமாக இருத்தல்
- AI summary-க்கு 80% மேல் confidence score
- 7 நாள் update panel இயக்கம் சரியாக செயல்படுதல்
- ஆண்டுக்கு 2 முறை model + rule validation review

## 6. Functional Requirements

### 6.1 Data Retrieval
- TN Govt Agriculture Portal, TNAU, PM-Kisan, PMFBY, Agri Infrastructure Fund, NABARD மற்றும் Ministry of Agriculture feeds-ஐ தொடர்ந்து தேடுதல்
- RSS / API / HTML scraping / official portals மூலம் data pull
- Raw English content DB-இல் சேமித்தல்

### 6.2 AI Translation and Summarization
- English document text clean-up
- AI summarization to extract:
  - Tamil title
  - short summary
  - eligibility
  - benefits
  - application steps
- Rule-based validation: no broken Tamil grammar, no empty summary, no unrelated content

### 6.3 Weekly Update Flow
- தினசரி அல்லது 12-மணி fetch cycle
- Fresh records last 7 days are labelled as current
- Older records moved to archive automatically

### 6.4 Tamil Interface Requirements
- Large readable Tamil font
- Easy words and short headings
- Icons for scheme categories
- Two-tab design:
  - புதிய அறிவிப்புகள்
  - காப்பக அறிவிப்புகள்
- “மேலும் படிக்க” action with details page

## 7. Non-Functional Requirements

- Low-bandwidth friendly UI
- Mobile-first experience for farmers
- Support Tamil and English labels where necessary
- Privacy-aware storage of public scheme info
- Strong API fallback and retry logic
- Audit logs for system fetch failures and processed content quality

## 8. Data Model

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

## 9. Archive Logic

```python
if created_date < today - timedelta(days=7):
    is_archived = True
```

## 10. API Endpoints

- GET /schemes/latest
- GET /schemes/archive
- GET /scheme/{id}
- POST /fetch/update
- GET /schemes?category={category}

## 11. Monitoring & Alerts

- fetch success/failure rate
- translation quality metric
- summary quality score
- Tamil readability validation failure
- alert on empty or bad data from official sources

## 12. Acceptance Criteria

1. New scheme items are fetched from verified official sources.
2. Tamil title and summary are generated for each scheme.
3. Latest updates show only the last 7 days.
4. Older items move to archive automatically.
5. AI output quality passes manual review for common farmer schemes.
6. UI remains readable and mobile-friendly in Tamil.
7. Admin can trigger manual refresh and monitor fetch health.

## 13. Scope / Out of Scope

### In scope
- official gov scheme discovery
- AI summarization and translation
- Tamil UI display
- archive process
- monitoring and admin refresh

### Out of scope
- direct application submission to government portals
- full identity verification
- financial disbursement logic
- payment gateway integration

## 14. Recommendation

This module should be treated as a trusted information layer for farmers, not a generic content feed. The critical success factor is accuracy, readable Tamil output, and timely updates from official sources. The module should prioritize clarity over complexity and must remain designed for low-literacy, mobile-first, rural users.
""".strip()


def generate_government_schemes_roadmap(product_name: str) -> str:
    return f"""{product_name} — Product Roadmap (6-Month Rollout)

## Phase 1 — Data Source Integration (Weeks 1–4)
- Identify official data sources: Tamil Nadu Agriculture Department, TNAU, PM-Kisan, PMFBY, Agri Infrastructure Fund, NABARD, MoA&FW
- Build automated fetch pipelines for English content
- Create unified GovSchemeData API
- Store raw government documents in DB

## Phase 2 — AI Summarization Engine (Weeks 4–8)
- Build English-to-Tamil translation pipeline
- Summarize long government docs into:
  - Tamil title
  - short Tamil summary
  - eligibility
  - benefits
  - application steps
- Add rule-based validation for grammar and content completeness

## Phase 3 — Weekly Update Logic (Weeks 8–10)
- Fetch daily or every 12 hours
- Save raw English and processed Tamil records
- Show only last 7 days under Latest Updates
- Auto-archive older items

## Phase 4 — Tamil UI/UX (Weeks 10–14)
- Create Tamil-first interface
- Add tabs: புதிய அறிவிப்புகள் and காப்பக அறிவிப்புகள்
- Use readable bilingual cards and detail page
- Add icons by scheme category

## Phase 5 — Testing and Validation (Weeks 14–18)
- Farmer readability testing
- AI accuracy audits
- API reliability tests
- Archive logic verification
- UI validation for Tamil rendering issues

## Phase 6 — Deployment and Monitoring (Weeks 18–20)
- Deploy to production
- Monitor fetch success rate, translation reliability, summary quality, and Tamil display issues
- Monthly review of model and rules
- Rollout and support checklist for live operations
""".strip()


def generate_government_schemes_requirements(product_name: str) -> str:
    return f"""{product_name} — Implementation Requirements

## 1. Technical Stack
- Python + FastAPI
- Celery or cron-based scheduled jobs
- PostgreSQL / SQLite for MVP
- HuggingFace summarization models
- IndicTrans2 or equivalent Tamil translation models
- Rule-based validation for Tamil quality control

## 2. Components

### Data Fetch Layer
- official data source connectors
- normalized raw content fields
- retry logic and alerting

### AI Processing Layer
- content cleaning
- summarization
- translation
- metadata tagging
- validation gates

### Storage Layer
- GovSchemeRaw table
- GovSchemeProcessed table
- admin tracking and archive status

### Presentation Layer
- Latest Updates panel
- Archive panel
- detail view page
- scheme type filters and search

## 3. Required API Concepts

GET /schemes/latest
Returns only the latest 7-day relevant Tamil entries

GET /schemes/archive
Returns archived entries grouped by year/category

GET /scheme/{{id}}
Returns full Tamil details for a scheme

POST /fetch/update
Might trigger manual ingestion, admin-only

## 4. Business Rules
- Only content from official or authorized sources should be published
- A scheme without a valid Tamil summary is not shown publicly
- Old content moves to archive after 7 days
- Users must see only plain-language, trustworthy details

## 5. Operational Requirements
- job monitoring and health dashboards
- alert on failed fetches
- alert on empty summary or poor Tamil translation
- monthly evaluation of source quality
""".strip()


if __name__ == "__main__":
    print("Available agents:")
    for agent in AGENT_REGISTRY:
        print(f"- {agent['name']}")

    print("\nSample PRD:\n")
    print(generate_prd("Digital Farming Support Center"))
    print("\nSample Architecture:\n")
    print(generate_system_architecture("Digital Farming Support Center"))
    print("\nSample Sprint Plan:\n")
    print(generate_sprint_plan("Digital Farming Support Center"))
    print("\nSample Data Model:\n")
    print(generate_data_model("Digital Farming Support Center"))
    print("\nSample API Contract:\n")
    print(generate_api_contract("Digital Farming Support Center"))
