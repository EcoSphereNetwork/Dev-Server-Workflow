#!/bin/bash

# AI command function
ai_command() {
    local prompt="$1"

    if [ -z "$prompt" ]; then
        log "ERROR" "Kein Prompt angegeben"
        return 1
    fi
    
    # Prüfe, ob der erweiterte AI-Assistent verfügbar ist
    if [ -f "$SCRIPT_DIR/ai_assistant.sh" ]; then
        # Verwende den erweiterten AI-Assistenten
        source "$SCRIPT_DIR/ai_assistant.sh"
        main "$prompt"
        return $?
    # Fallback auf ShellGPT, wenn verfügbar
    elif [ "$SHELLGPT_INSTALLED" = true ] && command -v sgpt > /dev/null; then
        if [ "$ACTIVE_LLM" = "llamafile" ]; then
            # Prüfe, ob Llamafile läuft
            if ! pgrep -f "llamafile" > /dev/null; then
                log "WARNING" "Llamafile läuft nicht. Starte Llamafile..."
                start_component "llamafile"
                sleep 5
            fi
        elif [ "$ACTIVE_LLM" = "claude" ]; then
            # Prüfe, ob der API-Schlüssel konfiguriert ist
            if [ -z "$ANTHROPIC_API_KEY" ]; then
                log "ERROR" "Anthropic API-Schlüssel ist nicht konfiguriert. Bitte konfigurieren Sie ihn mit 'dev-server config anthropic-key'"
                return 1
            fi
        fi

        # Führe ShellGPT aus
        sgpt "$prompt"
    else
        log "ERROR" "Weder der erweiterte AI-Assistent noch ShellGPT ist verfügbar. Bitte installieren Sie ShellGPT mit 'dev-server install shellgpt'"
        return 1
    fi
}
