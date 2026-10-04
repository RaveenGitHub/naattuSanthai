from __future__ import annotations

import argparse
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from dotenv import load_dotenv

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest official scheme JSON feeds without publication")
    parser.add_argument("--check", action="store_true", help="Check configuration only; no fetch or DB writes")
    args = parser.parse_args()
    load_dotenv(PROJECT_ROOT / ".env", override=False)
    from digital_farming.scheme_ingestion import ingest_scheme_sources, source_configuration

    if args.check:
        checks = source_configuration()
        return 0 if any(item["status"] == "configured" for item in checks) and not any(
            item["status"] == "invalid" for item in checks
        ) else 1
    directory = PROJECT_ROOT / "logs"
    directory.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s",
        handlers=[logging.StreamHandler(), RotatingFileHandler(
            directory / "scheme-refresh.log", maxBytes=1_000_000, backupCount=7, encoding="utf-8",
        )], force=True,
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    result = ingest_scheme_sources()
    return 0 if result["status"] == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
