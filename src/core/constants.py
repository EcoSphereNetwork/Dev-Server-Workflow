"""
Constants for the Dev-Server-Workflow project.

This module contains constants used throughout the Dev-Server-Workflow project.
"""

import os
from pathlib import Path

# Base directories
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
SCRIPTS_DIR = BASE_DIR / "scripts"
COMMON_DIR = SCRIPTS_DIR / "common"
SRC_DIR = BASE_DIR / "src"
LOGS_DIR = BASE_DIR / "logs"
CONFIG_DIR = BASE_DIR / "config"
DATA_DIR = BASE_DIR / "data"
DOCKER_DIR = BASE_DIR / "docker-mcp-servers"

# Create directories if they don't exist
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Default configuration values
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_LOG_FILE = LOGS_DIR / "app.log"

# MCP Server defaults
DEFAULT_MCP_HTTP_PORT = 3333
DEFAULT_N8N_URL = "http://localhost:5678"
DEFAULT_OPENHANDS_PORT = 3000
DEFAULT_OLLAMA_PORT = 8000
DEFAULT_OLLAMA_MODEL = "qwen2.5-coder:7b-instruct"
DEFAULT_OLLAMA_BASE_URL = "http://localhost:11434"

# Error codes
ERROR_CODES = {
    "SUCCESS": 0,
    "GENERAL_ERROR": 1,
    "INVALID_ARGUMENT": 2,
    "FILE_NOT_FOUND": 3,
    "PERMISSION_DENIED": 4,
    "COMMAND_NOT_FOUND": 5,
    "NETWORK_ERROR": 6,
    "TIMEOUT": 7,
    "CONTAINER_ERROR": 10,
    "DOCKER_ERROR": 11,
    "CONFIG_ERROR": 20,
    "DEPENDENCY_ERROR": 30,
    "VALIDATION_ERROR": 40,
    "UNKNOWN_ERROR": 99,
}