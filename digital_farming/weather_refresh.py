from __future__ import annotations

import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def configure_logging() -> logging.Logger:
    log_directory = PROJECT_ROOT / "logs"
    log_directory.mkdir(parents=True, exist_ok=True)
    file_handler = RotatingFileHandler(
        log_directory / "weather-refresh.log",
        maxBytes=1_000_000,
        backupCount=7,
        encoding="utf-8",
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(), file_handler],
        force=True,
    )
    return logging.getLogger("weather-refresh")


def main() -> int:
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    from services import fetch_authorized_weather_updates

    logger = configure_logging()
    result = fetch_authorized_weather_updates(timeout_seconds=30)
    coverage = result.get("city_coverage", {})
    summary = {
        "status": result.get("status"),
        "records_received": len(result.get("records", [])),
        "city_coverage": coverage,
        "sources": result.get("sources", []),
        "errors": result.get("errors", []),
    }
    complete = (
        result.get("status") == "success"
        and coverage.get("total", 0) > 0
        and coverage.get("received") == coverage.get("total")
    )
    if complete:
        logger.info("Weather refresh completed: %s", json.dumps(summary, ensure_ascii=False))
        return 0

    logger.error("Weather refresh incomplete: %s", json.dumps(summary, ensure_ascii=False))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
