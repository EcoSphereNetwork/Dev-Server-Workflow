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
n8n Setup - Credentials

Dieses Modul enthält Funktionen für die Einrichtung verschiedener Anmeldedaten in n8n.
"""

import requests
from datetime import datetime

from n8n_setup_utils import create_credential, find_credential_by_name

def setup_github_credential(n8n_url, api_key, github_token):
    """Set up GitHub credential in n8n."""
    # Überprüfen, ob die Anmeldedaten bereits existieren
    existing_credential = find_credential_by_name(n8n_url, api_key, "GitHub")
    if existing_credential:
        logger.info("GitHub credential already exists. Skipping creation.")
        return existing_credential
    
    credential_data = {
        "name": "GitHub",
        "type": "githubApi",
        "data": {
            "accessToken": github_token
        },
        "nodesAccess": [
            {
                "nodeType": "n8n-nodes-base.github",
                "date": datetime.utcnow().isoformat() + "Z"
            },
            {
                "nodeType": "n8n-nodes-base.githubTrigger",
                "date": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }
    
    return create_credential(n8n_url, api_key, credential_data)

def setup_openproject_credential(n8n_url, api_key, openproject_token):
    """Set up OpenProject credential in n8n."""
    # Überprüfen, ob die Anmeldedaten bereits existieren
    existing_credential = find_credential_by_name(n8n_url, api_key, "OpenProject")
    if existing_credential:
        logger.info("OpenProject credential already exists. Skipping creation.")
        return existing_credential
    
    credential_data = {
        "name": "OpenProject",
        "type": "httpHeaderAuth",
        "data": {
            "name": "Authorization",
            "value": f"Bearer {openproject_token}"
        },
        "nodesAccess": [
            {
                "nodeType": "n8n-nodes-base.httpRequest",
                "date": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }
    
    return create_credential(n8n_url, api_key, credential_data)

def setup_discord_credential(n8n_url, api_key, discord_webhook_url):
    """Set up Discord credential in n8n."""
    # Überprüfen, ob die Anmeldedaten bereits existieren
    existing_credential = find_credential_by_name(n8n_url, api_key, "Discord")
    if existing_credential:
        logger.info("Discord credential already exists. Skipping creation.")
        return existing_credential
    
    credential_data = {
        "name": "Discord",
        "type": "discordWebhook",
        "data": {
            "webhookUrl": discord_webhook_url
        },
        "nodesAccess": [
            {
                "nodeType": "n8n-nodes-base.discord",
                "date": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }
    
    return create_credential(n8n_url, api_key, credential_data)

def setup_affine_credential(n8n_url, api_key, affine_api_key):
    """Set up AFFiNE credential in n8n."""
    # Überprüfen, ob die Anmeldedaten bereits existieren
    existing_credential = find_credential_by_name(n8n_url, api_key, "AFFiNE")
    if existing_credential:
        logger.info("AFFiNE credential already exists. Skipping creation.")
        return existing_credential
    
    credential_data = {
        "name": "AFFiNE",
        "type": "httpHeaderAuth",
        "data": {
            "name": "Authorization",
            "value": f"Bearer {affine_api_key}"
        },
        "nodesAccess": [
            {
                "nodeType": "n8n-nodes-base.httpRequest",
                "date": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }
    
    return create_credential(n8n_url, api_key, credential_data)

def setup_appflowy_credential(n8n_url, api_key, appflowy_api_key):
    """Set up AppFlowy credential in n8n."""
    # Überprüfen, ob die Anmeldedaten bereits existieren
    existing_credential = find_credential_by_name(n8n_url, api_key, "AppFlowy")
    if existing_credential:
        logger.info("AppFlowy credential already exists. Skipping creation.")
        return existing_credential
    
    credential_data = {
        "name": "AppFlowy",
        "type": "httpHeaderAuth",
        "data": {
            "name": "Authorization",
            "value": f"Bearer {appflowy_api_key}"
        },
        "nodesAccess": [
            {
                "nodeType": "n8n-nodes-base.httpRequest",
                "date": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }
    
    return create_credential(n8n_url, api_key, credential_data)

def setup_openhands_credential(n8n_url, api_key, llm_api_key):
    """Set up OpenHands credential in n8n."""
    # Überprüfen, ob die Anmeldedaten bereits existieren
    existing_credential = find_credential_by_name(n8n_url, api_key, "OpenHands")
    if existing_credential:
        logger.info("OpenHands credential already exists. Skipping creation.")
        return existing_credential
    
    credential_data = {
        "name": "OpenHands",
        "type": "httpHeaderAuth",
        "data": {
            "name": "Authorization",
            "value": f"Bearer {llm_api_key}"
        },
        "nodesAccess": [
            {
                "nodeType": "n8n-nodes-base.httpRequest",
                "date": datetime.utcnow().isoformat() + "Z"
            }
        ]
    }
    
    return create_credential(n8n_url, api_key, credential_data)
