#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Konfiguriere Logging
logger = setup_logging("INFO")

# Lade Konfiguration
config_manager = ConfigManager()
config = config_manager.load_env_file(".env")

"""
n8n Setup - Haupt-Workflow-Importer

Dieses Modul importiert und kombiniert alle Workflow-Definitionen aus den einzelnen Modulen.
"""

# Imports aus den Workflow-Definitionen
from n8n_setup_workflows_github import GITHUB_OPENPROJECT_WORKFLOW
from n8n_setup_workflows_document import DOCUMENT_SYNC_WORKFLOW, DOCUMENT_SYNC_ENHANCED_WORKFLOW
from n8n_setup_workflows_openhands import OPENHANDS_WORKFLOW
from n8n_setup_workflows_special import (
    DISCORD_NOTIFICATION_WORKFLOW,
    TIME_TRACKING_WORKFLOW,
    AI_SUMMARY_WORKFLOW
)
from n8n_setup_workflows_mcp import MCP_SERVER_WORKFLOW

# Exportiere alle Workflows
__all__ = [
    'GITHUB_OPENPROJECT_WORKFLOW',
    'DOCUMENT_SYNC_WORKFLOW',
    'DOCUMENT_SYNC_ENHANCED_WORKFLOW',
    'OPENHANDS_WORKFLOW',
    'DISCORD_NOTIFICATION_WORKFLOW',
    'TIME_TRACKING_WORKFLOW',
    'AI_SUMMARY_WORKFLOW',
    'MCP_SERVER_WORKFLOW'
]
