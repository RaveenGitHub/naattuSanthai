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
