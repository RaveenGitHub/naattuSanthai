"""Digital Farming Support Center application package.

This package provides a cleaner, production-oriented project layout while preserving
backward-compatible imports for the legacy flat-module layout used during the
initial prototype phase.
"""

from __future__ import annotations

__all__ = [
    "app",
    "config",
    "database",
    "diagnostics",
    "routes",
    "schemas",
    "schemas_auth",
    "security",
    "services",
]

__version__ = "0.2.0"
