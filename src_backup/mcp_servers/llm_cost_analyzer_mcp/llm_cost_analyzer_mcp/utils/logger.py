"""
Logging-Utilities für den LLM Cost Analyzer.
"""

import logging
import sys
from typing import Optional

from ..core.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Konfiguriere das Logging.

    Args:
        log_level: Optionales Log-Level. Wenn nicht angegeben, wird das Log-Level aus den Einstellungen verwendet.
    """
    level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Ungültiges Log-Level: {level}")

    # Konfiguriere Root-Logger
    logging.basicConfig(
        level=numeric_level,
        format=settings.LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Setze Log-Level für Drittanbieter-Bibliotheken
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Logge Konfiguration
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging konfiguriert mit Level: {level}")