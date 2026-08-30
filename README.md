# Digital Farming Support Center

A mature agriculture and sustainability platform prototype for farmer support, agronomy advisory, weather intelligence, market data, and scheme guidance.

This repository has been reviewed and reorganized toward a more production-ready Python project structure while retaining compatibility with the earlier prototype modules.

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

```bash
python -m pip install -r requirements.txt
python -m uvicorn app:app --host 0.0.0.0 --port 8000
```

## Run with Docker

```bash
docker build -t digital-farming-support-center .
docker run -p 8000:8000 digital-farming-support-center
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
