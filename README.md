# Digital Farming Support Center

This repository contains a product-to-engineering package for the Digital Farming Support Center, including:

- PM/TPO personas and planning prompts
- Product strategy and architecture generation
- MVP backend blueprint for a rural agriculture support platform
- FastAPI application scaffold with farming APIs
- SQLite-backed service layer and role-based access handling
- Docker and Docker Compose deployment setup

## Included modules

- `tech_pm_agent.py` — PM/TPO agent prompt registry and document generation helpers
- `digital_farming_mvp.py` — MVP backend blueprint and service definitions
- `app.py` — FastAPI application entry point
- `routes.py` — API routes for farmers, soil tests, weather, and market data
- `services.py` — business logic and persistence support
- `database.py` — SQLite initialization and storage layer
- `auth.py` — role-based access control helpers

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

## Usage example

```python
from tech_pm_agent import generate_prd, generate_backlog, generate_roadmap

print(generate_prd("Digital Farming Support Center"))
print(generate_backlog("Digital Farming Support Center"))
print(generate_roadmap("Digital Farming Support Center"))
```

## Running tests

```bash
pytest -q
```
