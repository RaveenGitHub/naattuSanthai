from tech_pm_agent import (
    AGENT_REGISTRY,
    build_agent_prompt,
    generate_agent_response,
    generate_backlog,
    generate_prd,
    generate_roadmap,
    generate_sprint_plan,
    generate_system_architecture,
)


def test_registry_contains_expected_agents():
    names = sorted(agent["name"] for agent in AGENT_REGISTRY)
    assert names == [
        "Execution-Driven TPO Commander",
        "Strategic Tech PM Architect",
        "Tech PM/TPO Hybrid Product Intelligence Engine",
    ]


def test_build_agent_prompt_includes_role_and_guidance():
    prompt = build_agent_prompt("Strategic Tech PM Architect", "Launch digital marketplace")

    assert "Strategic Tech PM Architect" in prompt
    assert "Launch digital marketplace" in prompt
    assert "PRDs" in prompt
    assert "implementation-ready" in prompt.lower()


def test_generate_agent_response_uses_selected_persona():
    response = generate_agent_response(
        "Execution-Driven TPO Commander",
        "As a buyer, I want to track my cart so I can review my order before checkout.",
    )

    assert "Execution-Driven TPO Commander" in response
    assert "User Story" in response
    assert "Acceptance Criteria" in response


def test_generate_prd_includes_core_product_details():
    prd = generate_prd("Digital Farming Support Center")

    assert "Digital Farming Support Center" in prd
    assert "Problem Statement" in prd
    assert "User Personas" in prd
    assert "Success Metrics" in prd


def test_generate_backlog_includes_prioritized_epics():
    backlog = generate_backlog("Digital Farming Support Center")

    assert "Epic 1" in backlog
    assert "Soil Testing" in backlog
    assert "Weather Alerts" in backlog
    assert "Government Scheme Guidance" in backlog


def test_generate_roadmap_has_phases():
    roadmap = generate_roadmap("Digital Farming Support Center")

    assert "Phase 1" in roadmap
    assert "MVP" in roadmap
    assert "Phase 4" in roadmap
    assert "Scale" in roadmap


def test_generate_system_architecture_includes_layers_and_components():
    architecture = generate_system_architecture("Digital Farming Support Center")

    assert "Presentation Layer" in architecture
    assert "Application Layer" in architecture
    assert "Data Layer" in architecture
    assert "Weather API" in architecture


def test_generate_sprint_plan_has_iterations():
    sprint_plan = generate_sprint_plan("Digital Farming Support Center")

    assert "Sprint 1" in sprint_plan
    assert "Sprint 3" in sprint_plan
    assert "Sprint 6" in sprint_plan
    assert "Pilot" in sprint_plan
