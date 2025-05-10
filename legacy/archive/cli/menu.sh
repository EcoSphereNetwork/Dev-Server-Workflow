#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

# Interactive menu for the Dev-Server CLI

# Load configuration and functions
source "$(dirname "$0")/config.sh"
source "$(dirname "$0")/functions.sh"

# Function to display the main menu
show_main_menu() {
    clear
    log_info "${BLUE}=== Dev-Server CLI - Interaktives Menü ===${NC}"
    echo ""
    log_info "${CYAN}1)${NC} Status anzeigen"
    log_info "${CYAN}2)${NC} Komponenten starten"
    log_info "${CYAN}3)${NC} Komponenten stoppen"
    log_info "${CYAN}4)${NC} Logs anzeigen"
    log_info "${CYAN}5)${NC} Konfiguration"
    log_info "${CYAN}6)${NC} Ressourcen auflisten"
    log_info "${CYAN}7)${NC} Backup & Wiederherstellung"
    log_info "${CYAN}8)${NC} KI-Befehle"
    log_info "${CYAN}9)${NC} Hilfe"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) show_status_menu ;;
        2) show_start_menu ;;
        3) show_stop_menu ;;
        4) show_logs_menu ;;
        5) show_config_menu ;;
        6) show_list_menu ;;
        7) show_backup_menu ;;
        8) show_ai_menu ;;
        9) show_help_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_main_menu
            ;;
    esac
}

# Function to display the status menu
show_status_menu() {
    clear
    log_info "${BLUE}=== Status anzeigen ===${NC}"
    echo ""
    check_status
    echo ""
    log_info "${CYAN}1)${NC} Zurück zum Hauptmenü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) show_main_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_status_menu
            ;;
    esac
}

# Function to display the start menu
show_start_menu() {
    clear
    log_info "${BLUE}=== Komponenten starten ===${NC}"
    echo ""
    log_info "${CYAN}1)${NC} Alle Komponenten starten"
    log_info "${CYAN}2)${NC} n8n starten"
    log_info "${CYAN}3)${NC} MCP-Server starten"
    log_info "${CYAN}4)${NC} Ollama starten"
    log_info "${CYAN}5)${NC} OpenHands starten"
    log_info "${CYAN}6)${NC} Llamafile starten"
    log_info "${CYAN}7)${NC} Zurück zum Hauptmenü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            start_all
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_start_menu
            ;;
        2) 
            start_n8n
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_start_menu
            ;;
        3) 
            start_mcp
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_start_menu
            ;;
        4) 
            start_ollama
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_start_menu
            ;;
        5) 
            start_openhands
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_start_menu
            ;;
        6) 
            start_llamafile
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_start_menu
            ;;
        7) show_main_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_start_menu
            ;;
    esac
}

# Function to display the stop menu
show_stop_menu() {
    clear
    log_info "${BLUE}=== Komponenten stoppen ===${NC}"
    echo ""
    log_info "${CYAN}1)${NC} Alle Komponenten stoppen"
    log_info "${CYAN}2)${NC} n8n stoppen"
    log_info "${CYAN}3)${NC} MCP-Server stoppen"
    log_info "${CYAN}4)${NC} Ollama stoppen"
    log_info "${CYAN}5)${NC} OpenHands stoppen"
    log_info "${CYAN}6)${NC} Llamafile stoppen"
    log_info "${CYAN}7)${NC} Zurück zum Hauptmenü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            stop_all
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_stop_menu
            ;;
        2) 
            stop_n8n
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_stop_menu
            ;;
        3) 
            stop_mcp
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_stop_menu
            ;;
        4) 
            stop_ollama
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_stop_menu
            ;;
        5) 
            stop_openhands
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_stop_menu
            ;;
        6) 
            stop_llamafile
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_stop_menu
            ;;
        7) show_main_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_stop_menu
            ;;
    esac
}

# Function to display the logs menu
show_logs_menu() {
    clear
    log_info "${BLUE}=== Logs anzeigen ===${NC}"
    echo ""
    log_info "${CYAN}1)${NC} n8n Logs"
    log_info "${CYAN}2)${NC} MCP-Server Logs"
    log_info "${CYAN}3)${NC} Ollama Logs"
    log_info "${CYAN}4)${NC} OpenHands Logs"
    log_info "${CYAN}5)${NC} Llamafile Logs"
    log_info "${CYAN}6)${NC} Alle Logs"
    log_info "${CYAN}7)${NC} Zurück zum Hauptmenü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            clear
            log_info "${BLUE}=== n8n Logs ===${NC}"
            echo ""
            show_logs "n8n" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        2) 
            clear
            log_info "${BLUE}=== MCP-Server Logs ===${NC}"
            echo ""
            show_logs "mcp" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        3) 
            clear
            log_info "${BLUE}=== Ollama Logs ===${NC}"
            echo ""
            show_logs "ollama" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        4) 
            clear
            log_info "${BLUE}=== OpenHands Logs ===${NC}"
            echo ""
            show_logs "openhands" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        5) 
            clear
            log_info "${BLUE}=== Llamafile Logs ===${NC}"
            echo ""
            show_logs "llamafile" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        6) 
            clear
            log_info "${BLUE}=== Alle Logs ===${NC}"
            echo ""
            show_logs "all" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        7) show_main_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_logs_menu
            ;;
    esac
}

# Function to display the configuration menu
show_config_menu() {
    clear
    log_info "${BLUE}=== Konfiguration ===${NC}"
    echo ""
    log_info "${CYAN}1)${NC} LLM API-Key konfigurieren"
    log_info "${CYAN}2)${NC} GitHub Token konfigurieren"
    log_info "${CYAN}3)${NC} OpenProject Token konfigurieren"
    log_info "${CYAN}4)${NC} n8n API-Key konfigurieren"
    log_info "${CYAN}5)${NC} Workspace-Pfad konfigurieren"
    log_info "${CYAN}6)${NC} LLM wechseln"
    log_info "${CYAN}7)${NC} Zurück zum Hauptmenü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            echo -n "Bitte geben Sie den LLM API-Key ein: "
            read -r value
            configure_component "llm-api-key" "${value}"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_config_menu
            ;;
        2) 
            echo -n "Bitte geben Sie das GitHub Token ein: "
            read -r value
            configure_component "github-token" "${value}"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_config_menu
            ;;
        3) 
            echo -n "Bitte geben Sie das OpenProject Token ein: "
            read -r value
            configure_component "openproject-token" "${value}"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_config_menu
            ;;
        4) 
            echo -n "Bitte geben Sie den n8n API-Key ein: "
            read -r value
            configure_component "n8n-api-key" "${value}"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_config_menu
            ;;
        5) 
            echo -n "Bitte geben Sie den Workspace-Pfad ein: "
            read -r value
            configure_component "workspace-path" "${value}"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_config_menu
            ;;
        6) show_switch_llm_menu ;;
        7) show_main_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_config_menu
            ;;
    esac
}

# Function to display the switch LLM menu
show_switch_llm_menu() {
    clear
    log_info "${BLUE}=== LLM wechseln ===${NC}"
    echo ""
    log_info "${CYAN}1)${NC} Llamafile (lokal)"
    log_info "${CYAN}2)${NC} Claude (Anthropic)"
    log_info "${CYAN}3)${NC} GPT-4o (OpenAI)"
    log_info "${CYAN}4)${NC} Zurück zum Konfigurationsmenü"
    log_info "${CYAN}5)${NC} Zurück zum Hauptmenü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            switch_llm "llamafile"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_switch_llm_menu
            ;;
        2) 
            switch_llm "claude"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_switch_llm_menu
            ;;
        3) 
            switch_llm "openai"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_switch_llm_menu
            ;;
        4) show_config_menu ;;
        5) show_main_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_switch_llm_menu
            ;;
    esac
}

# Function to display the list menu
show_list_menu() {
    clear
    log_info "${BLUE}=== Ressourcen auflisten ===${NC}"
    echo ""
    log_info "${CYAN}1)${NC} Workflows auflisten"
    log_info "${CYAN}2)${NC} Modelle auflisten"
    log_info "${CYAN}3)${NC} Container auflisten"
    log_info "${CYAN}4)${NC} Zurück zum Hauptmenü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            clear
            log_info "${BLUE}=== Workflows ===${NC}"
            echo ""
            list_resources "workflows"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_list_menu
            ;;
        2) 
            clear
            log_info "${BLUE}=== Modelle ===${NC}"
            echo ""
            list_resources "models"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_list_menu
            ;;
        3) 
            clear
            log_info "${BLUE}=== Container ===${NC}"
            echo ""
            list_resources "containers"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_list_menu
            ;;
        4) show_main_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_list_menu
            ;;
    esac
}

# Function to display the backup menu
show_backup_menu() {
    clear
    log_info "${BLUE}=== Backup & Wiederherstellung ===${NC}"
    echo ""
    log_info "${CYAN}1)${NC} n8n Backup erstellen"
    log_info "${CYAN}2)${NC} OpenHands Backup erstellen"
    log_info "${CYAN}3)${NC} Alle Komponenten sichern"
    log_info "${CYAN}4)${NC} Backup wiederherstellen"
    log_info "${CYAN}5)${NC} Zurück zum Hauptmenü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            create_backup "n8n"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_backup_menu
            ;;
        2) 
            create_backup "openhands"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_backup_menu
            ;;
        3) 
            create_backup "all"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_backup_menu
            ;;
        4) show_restore_menu ;;
        5) show_main_menu ;;
        0) exit 0 ;;
        *) 
            log_info "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_backup_menu
            ;;
    esac
}

# Function to display the restore menu
show_restore_menu() {
    clear
    log_info "${BLUE}=== Backup wiederherstellen ===${NC}"
    echo ""
    
    # List available backups
    log_info "${CYAN}Verfügbare Backups:${NC}"
    echo ""
    
    # Check if backup directory exists
    if [[ ! -d "${BACKUP_DIR}" ]]; then
        log_info "Keine Backups gefunden."
        echo ""
        echo -n "Drücken Sie eine Taste, um fortzufahren..."
        read -r
        show_backup_menu
        return
    fi
    
    # Find all backup files
    backup_files=()
    while IFS= read -r -d '' file; do
        backup_files+=("${file}")
    done < <(find "${BACKUP_DIR}" -type f -name "*.tar.gz" -print0)
    
    # Check if any backup files were found
    if [[ ${#backup_files[@]} -eq 0 ]]; then
        log_info "Keine Backups gefunden."
        echo ""
        echo -n "Drücken Sie eine Taste, um fortzufahren..."
        read -r
        show_backup_menu
        return
    fi
    
    # Display backup files
    for i in "${!backup_files[@]}"; do
        log_info "${CYAN}$((i+1)))${NC} ${backup_files[i]}"
    done
    
    echo ""
    log_info "${CYAN}$((${#backup_files[@]}+1)))${NC} Zurück zum Backup-Menü"
    log_info "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    if [[ "${option}" -eq 0 ]]; then
        exit 0
    elif [[ "${option}" -eq $((${#backup_files[@]}+1)) ]]; then
        show_backup_menu
    elif [[ "${option}" -ge 1 && "${option}" -le ${#backup_files[@]} ]]; then
        restore_backup "${backup_files[$((option-1))]}"
        echo ""
        echo -n "Drücken Sie eine Taste, um fortzufahren..."
        read -r
        show_backup_menu
    else
        log_info "Ungültige Option. Bitte erneut versuchen."
        sleep 2
        show_restore_menu
    fi
}

# Function to display the AI menu
show_ai_menu() {
    clear
    log_info "${BLUE}=== KI-Befehle ===${NC}"
    echo ""
    log_info "${CYAN}Bitte geben Sie einen Prompt ein (oder 'q' zum Zurückkehren):${NC}"
    echo ""
    read -r prompt
    
    if [[ "${prompt}" == "q" ]]; then
        show_main_menu
    else
        clear
        log_info "${BLUE}=== KI-Antwort ===${NC}"
        echo ""
        execute_ai_command "${prompt}"
        echo ""
        echo -n "Drücken Sie eine Taste, um fortzufahren..."
        read -r
        show_ai_menu
    fi
}

# Function to display the help menu
show_help_menu() {
    clear
    log_info "${BLUE}=== Hilfe ===${NC}"
    echo ""
    log_info "${CYAN}Dev-Server CLI - Eine umfassende CLI zur Verwaltung des Dev-Server-Workflows${NC}"
    echo ""
    log_info "Verwendung: dev-server [Befehl] [Optionen]"
    echo ""
    log_info "${CYAN}Verfügbare Befehle:${NC}"
    log_info "  help                     Zeigt diese Hilfe an"
    log_info "  status                   Zeigt den Status aller Komponenten an"
    log_info "  start [Komponente]        Startet eine Komponente"
    log_info "  stop [Komponente]         Stoppt eine Komponente"
    log_info "  restart [Komponente]      Startet eine Komponente neu"
    log_info "  logs [Komponente]         Zeigt die Logs einer Komponente an"
    log_info "  config [Option] [Wert]    Konfiguriert eine Option"
    log_info "  list [Ressourcentyp]      Listet verfügbare Ressourcen auf"
    log_info "  install [Komponente]      Installiert eine Komponente"
    log_info "  switch-llm [LLM]          Wechselt zwischen LLMs (llamafile, claude)"
    log_info "  update [Komponente]       Aktualisiert eine Komponente"
    log_info "  backup [Komponente]       Erstellt ein Backup einer Komponente"
    log_info "  restore [Backup]          Stellt ein Backup wieder her"
    log_info "  ai [Prompt]               Führt einen KI-Befehl aus"
    log_info "  menu                     Öffnet das interaktive Menü"
    echo ""
    log_info "${CYAN}Komponenten:${NC}"
    log_info "  all                        Alle Komponenten"
    log_info "  mcp                        MCP-Server"
    log_info "  n8n                        n8n-Workflow-Engine"
    log_info "  ollama                     Ollama LLM-Server"
    log_info "  openhands                  OpenHands KI-Agent"
    log_info "  llamafile                  Llamafile LLM"
    log_info "  shellgpt                   ShellGPT CLI"
    echo ""
    log_info "${CYAN}Beispiele:${NC}"
    log_info "  dev-server status"
    log_info "  dev-server start mcp"
    log_info "  dev-server logs n8n"
    log_info "  dev-server ai \"Wie starte ich den MCP-Server?\""
    log_info "  dev-server menu"
    echo ""
    echo -n "Drücken Sie eine Taste, um fortzufahren..."
    read -r
    show_main_menu
}

# Start the menu
show_main_menu