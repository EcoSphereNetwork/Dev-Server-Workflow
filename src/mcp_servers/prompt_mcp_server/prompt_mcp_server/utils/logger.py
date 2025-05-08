"""
Logging utilities for the Prompt MCP Server.
"""

import logging
import sys
from typing import Optional

from ..core.config import settings


def setup_logging(log_level: Optional[str] = None) -> None:
    """
    Set up logging configuration.

    Args:
        log_level: Optional log level to use. If not provided, the log level from settings is used.
    """
    level = log_level or settings.LOG_LEVEL
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f"Invalid log level: {level}")

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=settings.LOG_FORMAT,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.error").setLevel(logging.ERROR)
    logging.getLogger("fastapi").setLevel(logging.WARNING)

    # Log configuration
    logger = logging.getLogger(__name__)
    logger.debug(f"Logging configured with level: {level}")