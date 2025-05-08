#!/bin/bash
# Configuration for the Dev-Server CLI

# Base directories
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="${BASE_DIR}/src"
LOGS_DIR="${BASE_DIR}/logs"
BACKUP_DIR="${BASE_DIR}/backups"
DATA_DIR="${BASE_DIR}/data"

# Create directories if they don't exist
mkdir -p "${LOGS_DIR}" "${BACKUP_DIR}" "${DATA_DIR}"

# Docker configuration
DOCKER_NETWORK="dev-server-network"

# n8n configuration
N8N_PORT=5678
N8N_URL="http://localhost:${N8N_PORT}"
N8N_USER="admin"
N8N_PASSWORD="password"
N8N_API_KEY=""
N8N_ENCRYPTION_KEY="your_encryption_key_min_32_chars"
N8N_DATA_DIR="${DATA_DIR}/n8n"

# MCP server configuration
MCP_PORT=3333
DOCKER_MCP_PORT=3334
MCP_AUTH_TOKEN=""

# Ollama configuration
OLLAMA_PORT=11434
OLLAMA_DEFAULT_MODEL="qwen2.5-coder:7b-instruct"
OLLAMA_DATA_DIR="${DATA_DIR}/ollama"

# OpenHands configuration
OPENHANDS_PORT=8080
OPENHANDS_API_KEY=""
OPENHANDS_DATA_DIR="${DATA_DIR}/openhands"

# Llamafile configuration
LLAMAFILE_PORT=8080
LLAMAFILE_PATH="${BASE_DIR}/bin/llamafile"
LLAMAFILE_MODEL="${BASE_DIR}/models/llama-3-8b-instruct.Q4_K_M.gguf"
LLAMAFILE_CTX_SIZE=4096
LLAMAFILE_GPU_LAYERS=0
LLAMAFILE_THREADS=4

# LLM configuration
LLM_API_KEY=""
LLM_MODEL="anthropic/claude-3-5-sonnet-20240620"

# GitHub configuration
GITHUB_TOKEN=""

# OpenProject configuration
OPENPROJECT_URL="https://openproject.example.com"
OPENPROJECT_TOKEN=""

# Logging configuration
LOG_LEVEL="info"

# Load environment variables from .env file if it exists
if [[ -f "${BASE_DIR}/.env" ]]; then
    while IFS='=' read -r key value; do
        # Skip comments and empty lines
        [[ "${key}" =~ ^#.*$ || -z "${key}" ]] && continue
        
        # Remove quotes from value
        value="${value%\"}"
        value="${value#\"}"
        value="${value%\'}"
        value="${value#\'}"
        
        # Export the variable
        export "${key}=${value}"
        
        # Update the corresponding variable in this script
        case "${key}" in
            N8N_PORT) N8N_PORT="${value}" ;;
            N8N_URL) N8N_URL="${value}" ;;
            N8N_USER) N8N_USER="${value}" ;;
            N8N_PASSWORD) N8N_PASSWORD="${value}" ;;
            N8N_API_KEY) N8N_API_KEY="${value}" ;;
            N8N_ENCRYPTION_KEY) N8N_ENCRYPTION_KEY="${value}" ;;
            MCP_PORT) MCP_PORT="${value}" ;;
            MCP_AUTH_TOKEN) MCP_AUTH_TOKEN="${value}" ;;
            OLLAMA_PORT) OLLAMA_PORT="${value}" ;;
            OLLAMA_DEFAULT_MODEL) OLLAMA_DEFAULT_MODEL="${value}" ;;
            OPENHANDS_PORT) OPENHANDS_PORT="${value}" ;;
            OPENHANDS_API_KEY) OPENHANDS_API_KEY="${value}" ;;
            LLAMAFILE_PORT) LLAMAFILE_PORT="${value}" ;;
            LLM_API_KEY) LLM_API_KEY="${value}" ;;
            LLM_MODEL) LLM_MODEL="${value}" ;;
            GITHUB_TOKEN) GITHUB_TOKEN="${value}" ;;
            OPENPROJECT_URL) OPENPROJECT_URL="${value}" ;;
            OPENPROJECT_TOKEN) OPENPROJECT_TOKEN="${value}" ;;
            LOG_LEVEL) LOG_LEVEL="${value}" ;;
        esac
    done < "${BASE_DIR}/.env"
fi

# Update N8N_URL based on N8N_PORT
N8N_URL="http://localhost:${N8N_PORT}"

# Export variables
export BASE_DIR SRC_DIR LOGS_DIR BACKUP_DIR DATA_DIR
export DOCKER_NETWORK
export N8N_PORT N8N_URL N8N_USER N8N_PASSWORD N8N_API_KEY N8N_ENCRYPTION_KEY N8N_DATA_DIR
export MCP_PORT MCP_AUTH_TOKEN
export OLLAMA_PORT OLLAMA_DEFAULT_MODEL OLLAMA_DATA_DIR
export OPENHANDS_PORT OPENHANDS_API_KEY OPENHANDS_DATA_DIR
export LLAMAFILE_PORT LLAMAFILE_PATH LLAMAFILE_MODEL LLAMAFILE_CTX_SIZE LLAMAFILE_GPU_LAYERS LLAMAFILE_THREADS
export LLM_API_KEY LLM_MODEL
export GITHUB_TOKEN
export OPENPROJECT_URL OPENPROJECT_TOKEN
export LOG_LEVEL