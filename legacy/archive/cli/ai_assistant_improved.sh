#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

# Verbesserter KI-Assistent für die Dev-Server CLI

# Source common functions
source "$(dirname "$0")/functions.sh"

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Konfiguration
CONFIG_FILE="$(dirname "$0")/config/dev-server.conf"
if [ -f "$CONFIG_FILE" ]; then
    source "$CONFIG_FILE"
fi

# Funktion zum Auswählen des LLM-Providers
get_llm_provider() {
    if [ "$ACTIVE_LLM" == "llamafile" ]; then
        log_info "llamafile"
    elif [ "$ACTIVE_LLM" == "claude" ]; then
        log_info "claude"
    else
        log_info "llamafile" # Fallback
    fi
}

# Funktion zum Überprüfen, ob Llamafile läuft
check_llamafile_running() {
    if pgrep -f "llamafile" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Funktion zum Starten von Llamafile, falls nicht bereits gestartet
ensure_llamafile_running() {
    if ! check_llamafile_running; then
        log_info "Llamafile ist nicht gestartet. Starte Llamafile..."
        if [ -f "$LLAMAFILE_PATH" ]; then
            chmod +x "$LLAMAFILE_PATH"
            nohup "$LLAMAFILE_PATH" --port "$LLAMAFILE_PORT" --host 0.0.0.0 > "$LOGS_DIR/llamafile.log" 2>&1 &
            sleep 5 # Warte, bis Llamafile gestartet ist
            if check_llamafile_running; then
                log_info "Llamafile erfolgreich gestartet auf Port $LLAMAFILE_PORT"
                return 0
            else
                log_error "Fehler beim Starten von Llamafile"
                return 1
            fi
        else
            log_error "Llamafile nicht gefunden unter $LLAMAFILE_PATH"
            return 1
        fi
    fi
    return 0
}

# Funktion zum Überprüfen der API-Schlüssel
check_api_keys() {
    local provider="$1"
    
    if [ "$provider" == "claude" ]; then
        if [ -z "$ANTHROPIC_API_KEY" ]; then
            log_error "Anthropic API-Schlüssel ist nicht gesetzt. Bitte setzen Sie ihn in der Konfiguration."
            return 1
        fi
    fi
    
    return 0
}

# Funktion zum Verarbeiten einer Anfrage mit Llamafile
process_with_llamafile() {
    local prompt="$1"
    local endpoint="http://localhost:$LLAMAFILE_PORT/completion"
    
    # Stelle sicher, dass Llamafile läuft
    if ! ensure_llamafile_running; then
        log_error "Llamafile konnte nicht gestartet werden."
        return 1
    fi
    
    # Sende Anfrage an Llamafile
    local response=$(curl -s -X POST "$endpoint" \
        -H "Content-Type: application/json" \
        -d "{
            \"prompt\": \"$prompt\",
            \"temperature\": 0.2,
            \"max_tokens\": 500,
            \"stop\": [\"<|im_end|>\"]
        }")
    
    if [ $? -ne 0 ] || [ -z "$response" ]; then
        log_error "Fehler bei der Anfrage an Llamafile"
        return 1
    fi
    
    # Extrahiere die Antwort
    local content=$(log_info "$response" | jq -r '.content')
    
    log_info "$content"
    return 0
}

# Funktion zum Verarbeiten einer Anfrage mit Claude
process_with_claude() {
    local prompt="$1"
    local endpoint="https://api.anthropic.com/v1/messages"
    
    # Überprüfe API-Schlüssel
    if ! check_api_keys "claude"; then
        return 1
    fi
    
    # Sende Anfrage an Claude
    local response=$(curl -s -X POST "$endpoint" \
        -H "Content-Type: application/json" \
        -H "x-api-key: $ANTHROPIC_API_KEY" \
        -H "anthropic-version: 2023-06-01" \
        -d "{
            \"model\": \"$CLAUDE_MODEL\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}],
            \"max_tokens\": 500
        }")
    
    if [ $? -ne 0 ] || [ -z "$response" ]; then
        log_error "Fehler bei der Anfrage an Claude"
        return 1
    fi
    
    # Extrahiere die Antwort
    local content=$(log_info "$response" | jq -r '.content[0].text')
    
    log_info "$content"
    return 0
}

# Funktion zum Verarbeiten eines natürlichsprachlichen Befehls
process_nl_command() {
    local command="$1"
    local provider=$(get_llm_provider)
    
    log_info "Verarbeite Befehl mit $provider: $command"
    
    # Bereite den Prompt vor
    local prompt="Du bist ein CLI-Assistent für das Dev-Server-Workflow-Projekt. Deine Aufgabe ist es, den folgenden natürlichsprachlichen Befehl in einen spezifischen CLI-Befehl mit dem dev-server.sh-Skript zu übersetzen.

Verfügbare Befehle:
- status: Zeigt den Status aller Komponenten an
- start [Komponente]: Startet eine Komponente
- stop [Komponente]: Stoppt eine Komponente
- restart [Komponente]: Startet eine Komponente neu
- logs [Komponente]: Zeigt die Logs einer Komponente an
- config [Option] [Wert]: Konfiguriert eine Option
- list [Ressourcentyp]: Listet verfügbare Ressourcen auf
- install [Komponente]: Installiert eine Komponente
- switch-llm [LLM]: Wechselt zwischen LLMs (llamafile, claude)
- update [Komponente]: Aktualisiert eine Komponente
- package [Aktion] [Paket] [Manager] [Optionen]: Paketmanagement
- configure [Aktion] [Datei] [Schlüssel] [Wert] [Extra]: Konfigurationsmanagement
- monitor [Aktion] [Argumente...]: Monitoring-Funktionen
- web-ui [Aktion]: Verwaltet die Web-UI (start, stop, logs, open)

Komponenten: all, mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, llamafile, monitoring

Benutzerbefehl: $command

Antworte NUR mit dem exakten CLI-Befehl, der ausgeführt werden soll, nichts anderes."
    
    # Verarbeite den Prompt mit dem ausgewählten Provider
    local response=""
    if [ "$provider" == "llamafile" ]; then
        response=$(process_with_llamafile "$prompt")
    elif [ "$provider" == "claude" ]; then
        response=$(process_with_claude "$prompt")
    else
        log_error "Unbekannter LLM-Provider: $provider"
        return 1
    fi
    
    if [ $? -ne 0 ] || [ -z "$response" ]; then
        log_error "Fehler bei der Verarbeitung des Befehls"
        return 1
    fi
    
    log_info "Übersetzter Befehl: $response"
    
    # Extrahiere den Befehl
    local cli_command=$(log_info "$response" | tr -d '\r\n')
    
    # Entferne Anführungszeichen, falls vorhanden
    cli_command=$(log_info "$cli_command" | sed 's/^"//;s/"$//')
    
    # Überprüfe, ob der Befehl mit "dev-server" beginnt
    if [[ "$cli_command" == dev-server* ]]; then
        # Entferne "dev-server"-Präfix
        cli_command=${cli_command#dev-server}
        cli_command=${cli_command# }
    fi
    
    # Führe den Befehl aus
    log_info "Führe Befehl aus: ./dev-server.sh $cli_command"
    ./dev-server.sh $cli_command
    
    return $?
}

# Funktion zum Verarbeiten einer natürlichsprachlichen Frage
process_nl_question() {
    local question="$1"
    local provider=$(get_llm_provider)
    
    log_info "Verarbeite Frage mit $provider: $question"
    
    # Bereite den Prompt vor
    local prompt="Du bist ein CLI-Assistent für das Dev-Server-Workflow-Projekt. Deine Aufgabe ist es, die folgende Frage über das Projekt zu beantworten.

Das Dev-Server-Workflow-Projekt umfasst:
- CLI-Framework zur Verwaltung von Komponenten
- MCP-Server (n8n MCP, Docker MCP)
- Monitoring-Stack (Prometheus, Grafana, Alertmanager)
- LLM-Integration (Llamafile, Claude, Ollama)
- Paketmanagement
- Konfigurationsmanagement
- Monitoring-Funktionen
- Web-UI für die Verwaltung aller Komponenten

Benutzerfrage: $question

Gib eine präzise und hilfreiche Antwort."
    
    # Verarbeite den Prompt mit dem ausgewählten Provider
    local response=""
    if [ "$provider" == "llamafile" ]; then
        response=$(process_with_llamafile "$prompt")
    elif [ "$provider" == "claude" ]; then
        response=$(process_with_claude "$prompt")
    else
        log_error "Unbekannter LLM-Provider: $provider"
        return 1
    fi
    
    if [ $? -ne 0 ] || [ -z "$response" ]; then
        log_error "Fehler bei der Verarbeitung der Frage"
        return 1
    fi
    
    # Gib die Antwort aus
    log_info "${GREEN}KI-Assistent:${NC}"
    log_info "$response"
    
    return 0
}

# Hauptfunktion
main() {
    local input="$1"
    
    # Überprüfe, ob es sich um eine Frage oder einen Befehl handelt
    if [[ "$input" == *"?"* ]]; then
        process_nl_question "$input"
    else
        process_nl_command "$input"
    fi
}

# Führe die Hauptfunktion aus, wenn das Skript direkt ausgeführt wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi