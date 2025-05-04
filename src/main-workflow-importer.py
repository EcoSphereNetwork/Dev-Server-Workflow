#!/usr/bin/env python3
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

# Exportiere alle Workflows
__all__ = [
    'GITHUB_OPENPROJECT_WORKFLOW',
    'DOCUMENT_SYNC_WORKFLOW',
    'DOCUMENT_SYNC_ENHANCED_WORKFLOW',
    'OPENHANDS_WORKFLOW',
    'DISCORD_NOTIFICATION_WORKFLOW',
    'TIME_TRACKING_WORKFLOW',
    'AI_SUMMARY_WORKFLOW'
]
