#!/bin/bash
# Verbesserte Konfiguration für die Dev-Server CLI

# Basisverzeichnisse
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CLI_DIR="${BASE_DIR}/cli"
SRC_DIR="${BASE_DIR}/src"
LOGS_DIR="${BASE_DIR}/logs"
BACKUP_DIR="${BASE_DIR}/backups"
DATA_DIR="${BASE_DIR}/data"
CONFIG_DIR="${CLI_DIR}/config"
MODELS_DIR="${CLI_DIR}/models"

# Erstelle Verzeichnisse, falls sie nicht existieren
mkdir -p "${LOGS_DIR}" "${BACKUP_DIR}" "${DATA_DIR}" "${CONFIG_DIR}" "${MODELS_DIR}"

# Konfigurationsdatei
CONFIG_FILE="${CONFIG_DIR}/dev-server.conf"

# Docker-Konfiguration
DOCKER_NETWORK="dev-server-network"

# n8n-Konfiguration
N8N_PORT=5678
N8N_URL="http://localhost:${N8N_PORT}"
N8N_USER="admin"
N8N_PASSWORD="password"
N8N_API_KEY=""
N8N_ENCRYPTION_KEY="your_encryption_key_min_32_chars"
N8N_DATA_DIR="${DATA_DIR}/n8n"

# MCP-Server-Konfiguration
MCP_PORT=3333
DOCKER_MCP_PORT=3334
N8N_MCP_PORT=3335
MCP_AUTH_TOKEN=""

# Ollama-Konfiguration
OLLAMA_PORT=11434
OLLAMA_DEFAULT_MODEL="qwen2.5-coder:7b-instruct"
OLLAMA_DATA_DIR="${DATA_DIR}/ollama"

# OpenHands-Konfiguration
OPENHANDS_PORT=8080
OPENHANDS_API_KEY=""
OPENHANDS_DATA_DIR="${DATA_DIR}/openhands"

# Llamafile-Konfiguration
LLAMAFILE_PORT=8080
LLAMAFILE_PATH="${MODELS_DIR}/Llama-3.2-3B-Instruct.Q6_K.llamafile"
LLAMAFILE_URL="https://huggingface.co/Mozilla/Llama-3.2-3B-Instruct-llamafile/resolve/main/Llama-3.2-3B-Instruct.Q6_K.llamafile?download=true"
LLAMAFILE_CTX_SIZE=4096
LLAMAFILE_GPU_LAYERS=0
LLAMAFILE_THREADS=4

# LLM-Konfiguration
ACTIVE_LLM="llamafile" # Optionen: llamafile, claude
ANTHROPIC_API_KEY=""
CLAUDE_MODEL="claude-3-5-sonnet-20240620" # Standardmodell für Claude

# GitHub-Konfiguration
GITHUB_TOKEN=""

# OpenProject-Konfiguration
OPENPROJECT_URL="https://openproject.example.com"
OPENPROJECT_TOKEN=""

# Web-UI-Konfiguration
WEB_UI_PORT=3000
WEB_UI_DIR="${BASE_DIR}/frontend"

# Logging-Konfiguration
LOG_LEVEL="info"
VERBOSE_MODE=false

# Lade Konfiguration, wenn vorhanden
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
else
    # Erstelle Konfigurationsdatei
    cat > "$CONFIG_FILE" << EOF
# Dev-Server CLI Konfiguration
# Automatisch generiert am $(date)

# Basisverzeichnisse
BASE_DIR="$BASE_DIR"
CLI_DIR="$CLI_DIR"
SRC_DIR="$SRC_DIR"
LOGS_DIR="$LOGS_DIR"
BACKUP_DIR="$BACKUP_DIR"
DATA_DIR="$DATA_DIR"
CONFIG_DIR="$CONFIG_DIR"
MODELS_DIR="$MODELS_DIR"

# Docker-Konfiguration
DOCKER_NETWORK="$DOCKER_NETWORK"

# n8n-Konfiguration
N8N_PORT=$N8N_PORT
N8N_URL="$N8N_URL"
N8N_USER="$N8N_USER"
N8N_PASSWORD="$N8N_PASSWORD"
N8N_API_KEY="$N8N_API_KEY"
N8N_ENCRYPTION_KEY="$N8N_ENCRYPTION_KEY"
N8N_DATA_DIR="$N8N_DATA_DIR"

# MCP-Server-Konfiguration
MCP_PORT=$MCP_PORT
DOCKER_MCP_PORT=$DOCKER_MCP_PORT
N8N_MCP_PORT=$N8N_MCP_PORT
MCP_AUTH_TOKEN="$MCP_AUTH_TOKEN"

# Ollama-Konfiguration
OLLAMA_PORT=$OLLAMA_PORT
OLLAMA_DEFAULT_MODEL="$OLLAMA_DEFAULT_MODEL"
OLLAMA_DATA_DIR="$OLLAMA_DATA_DIR"

# OpenHands-Konfiguration
OPENHANDS_PORT=$OPENHANDS_PORT
OPENHANDS_API_KEY="$OPENHANDS_API_KEY"
OPENHANDS_DATA_DIR="$OPENHANDS_DATA_DIR"

# Llamafile-Konfiguration
LLAMAFILE_PORT=$LLAMAFILE_PORT
LLAMAFILE_PATH="$LLAMAFILE_PATH"
LLAMAFILE_URL="$LLAMAFILE_URL"
LLAMAFILE_CTX_SIZE=$LLAMAFILE_CTX_SIZE
LLAMAFILE_GPU_LAYERS=$LLAMAFILE_GPU_LAYERS
LLAMAFILE_THREADS=$LLAMAFILE_THREADS

# LLM-Konfiguration
ACTIVE_LLM="$ACTIVE_LLM"
ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"
CLAUDE_MODEL="$CLAUDE_MODEL"

# GitHub-Konfiguration
GITHUB_TOKEN="$GITHUB_TOKEN"

# OpenProject-Konfiguration
OPENPROJECT_URL="$OPENPROJECT_URL"
OPENPROJECT_TOKEN="$OPENPROJECT_TOKEN"

# Web-UI-Konfiguration
WEB_UI_PORT=$WEB_UI_PORT
WEB_UI_DIR="$WEB_UI_DIR"

# Logging-Konfiguration
LOG_LEVEL="$LOG_LEVEL"
VERBOSE_MODE=$VERBOSE_MODE
EOF
fi

# Lade Umgebungsvariablen aus .env-Datei, falls vorhanden
if [ -f "${BASE_DIR}/.env" ]; then
    while IFS='=' read -r key value; do
        # Überspringe Kommentare und leere Zeilen
        [[ "${key}" =~ ^#.*$ || -z "${key}" ]] && continue
        
        # Entferne Anführungszeichen aus dem Wert
        value="${value%\"}"
        value="${value#\"}"
        value="${value%\'}"
        value="${value#\'}"
        
        # Exportiere die Variable
        export "${key}=${value}"
        
        # Aktualisiere die entsprechende Variable in diesem Skript
        case "${key}" in
            N8N_PORT) N8N_PORT="${value}" ;;
            N8N_URL) N8N_URL="${value}" ;;
            N8N_USER) N8N_USER="${value}" ;;
            N8N_PASSWORD) N8N_PASSWORD="${value}" ;;
            N8N_API_KEY) N8N_API_KEY="${value}" ;;
            N8N_ENCRYPTION_KEY) N8N_ENCRYPTION_KEY="${value}" ;;
            MCP_PORT) MCP_PORT="${value}" ;;
            DOCKER_MCP_PORT) DOCKER_MCP_PORT="${value}" ;;
            N8N_MCP_PORT) N8N_MCP_PORT="${value}" ;;
            MCP_AUTH_TOKEN) MCP_AUTH_TOKEN="${value}" ;;
            OLLAMA_PORT) OLLAMA_PORT="${value}" ;;
            OLLAMA_DEFAULT_MODEL) OLLAMA_DEFAULT_MODEL="${value}" ;;
            OPENHANDS_PORT) OPENHANDS_PORT="${value}" ;;
            OPENHANDS_API_KEY) OPENHANDS_API_KEY="${value}" ;;
            LLAMAFILE_PORT) LLAMAFILE_PORT="${value}" ;;
            LLAMAFILE_PATH) LLAMAFILE_PATH="${value}" ;;
            ACTIVE_LLM) ACTIVE_LLM="${value}" ;;
            ANTHROPIC_API_KEY) ANTHROPIC_API_KEY="${value}" ;;
            CLAUDE_MODEL) CLAUDE_MODEL="${value}" ;;
            GITHUB_TOKEN) GITHUB_TOKEN="${value}" ;;
            OPENPROJECT_URL) OPENPROJECT_URL="${value}" ;;
            OPENPROJECT_TOKEN) OPENPROJECT_TOKEN="${value}" ;;
            WEB_UI_PORT) WEB_UI_PORT="${value}" ;;
            LOG_LEVEL) LOG_LEVEL="${value}" ;;
            VERBOSE_MODE) VERBOSE_MODE="${value}" ;;
        esac
    done < "${BASE_DIR}/.env"
fi

# Aktualisiere N8N_URL basierend auf N8N_PORT
N8N_URL="http://localhost:${N8N_PORT}"

# Exportiere Variablen
export BASE_DIR CLI_DIR SRC_DIR LOGS_DIR BACKUP_DIR DATA_DIR CONFIG_DIR MODELS_DIR
export DOCKER_NETWORK
export N8N_PORT N8N_URL N8N_USER N8N_PASSWORD N8N_API_KEY N8N_ENCRYPTION_KEY N8N_DATA_DIR
export MCP_PORT DOCKER_MCP_PORT N8N_MCP_PORT MCP_AUTH_TOKEN
export OLLAMA_PORT OLLAMA_DEFAULT_MODEL OLLAMA_DATA_DIR
export OPENHANDS_PORT OPENHANDS_API_KEY OPENHANDS_DATA_DIR
export LLAMAFILE_PORT LLAMAFILE_PATH LLAMAFILE_URL LLAMAFILE_CTX_SIZE LLAMAFILE_GPU_LAYERS LLAMAFILE_THREADS
export ACTIVE_LLM ANTHROPIC_API_KEY CLAUDE_MODEL
export GITHUB_TOKEN
export OPENPROJECT_URL OPENPROJECT_TOKEN
export WEB_UI_PORT WEB_UI_DIR
export LOG_LEVEL VERBOSE_MODE