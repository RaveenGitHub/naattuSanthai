# Tech PM / TPO Agent Package

This repository contains a minimal Python implementation of the requested technical product manager / technical product owner agent personas.

## Included agents

- Strategic Tech PM Architect
- Execution-Driven TPO Commander
- Tech PM/TPO Hybrid Product Intelligence Engine

## Usage

```python
from tech_pm_agent import generate_agent_response

response = generate_agent_response(
    "Strategic Tech PM Architect",
    "Launch a customer onboarding product for enterprise clients",
)

print(response)
```

## Running tests

```bash
pytest -q
```
