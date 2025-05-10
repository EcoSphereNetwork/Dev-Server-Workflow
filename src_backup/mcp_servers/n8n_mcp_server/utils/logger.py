"""
Logging-Modul für den n8n MCP Server.

Dieses Modul bietet eine einheitliche Logging-Funktionalität für den n8n MCP Server.
"""

import logging
import sys
from pathlib import Path

from ..core.config import settings

# Erstelle Logger
logger = logging.getLogger("n8n_mcp")


def setup_logging():
    """Konfiguriere das Logging."""
    # Setze Log-Level
    log_level = getattr(logging, settings.LOG_LEVEL.upper())
    logger.setLevel(log_level)
    
    # Entferne alle vorhandenen Handler
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Erstelle Konsolen-Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # Erstelle Datei-Handler
    file_handler = logging.FileHandler(settings.LOG_FILE)
    file_handler.setLevel(log_level)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    return logger