from __future__ import annotations

from fastapi import FastAPI

from database import init_db
from digital_farming.api.v1.routes import router as v1_router
from digital_farming.config import settings


def create_app() -> FastAPI:
    init_db()
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    app.include_router(v1_router, prefix="/api/v1")
    return app


app = create_app()
