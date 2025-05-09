#!/bin/bash
# Interactive menu for the Dev-Server CLI

# Load configuration and functions
source "$(dirname "$0")/config.sh"
source "$(dirname "$0")/functions.sh"

# Function to display the main menu
show_main_menu() {
    clear
    echo -e "${BLUE}=== Dev-Server CLI - Interaktives Menü ===${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} Status anzeigen"
    echo -e "${CYAN}2)${NC} Komponenten starten"
    echo -e "${CYAN}3)${NC} Komponenten stoppen"
    echo -e "${CYAN}4)${NC} Logs anzeigen"
    echo -e "${CYAN}5)${NC} Konfiguration"
    echo -e "${CYAN}6)${NC} Ressourcen auflisten"
    echo -e "${CYAN}7)${NC} Backup & Wiederherstellung"
    echo -e "${CYAN}8)${NC} KI-Befehle"
    echo -e "${CYAN}9)${NC} Hilfe"
    echo -e "${CYAN}0)${NC} Beenden"
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
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_main_menu
            ;;
    esac
}

# Function to display the status menu
show_status_menu() {
    clear
    echo -e "${BLUE}=== Status anzeigen ===${NC}"
    echo ""
    check_status
    echo ""
    echo -e "${CYAN}1)${NC} Zurück zum Hauptmenü"
    echo -e "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) show_main_menu ;;
        0) exit 0 ;;
        *) 
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_status_menu
            ;;
    esac
}

# Function to display the start menu
show_start_menu() {
    clear
    echo -e "${BLUE}=== Komponenten starten ===${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} Alle Komponenten starten"
    echo -e "${CYAN}2)${NC} n8n starten"
    echo -e "${CYAN}3)${NC} MCP-Server starten"
    echo -e "${CYAN}4)${NC} Ollama starten"
    echo -e "${CYAN}5)${NC} OpenHands starten"
    echo -e "${CYAN}6)${NC} Llamafile starten"
    echo -e "${CYAN}7)${NC} Zurück zum Hauptmenü"
    echo -e "${CYAN}0)${NC} Beenden"
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
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_start_menu
            ;;
    esac
}

# Function to display the stop menu
show_stop_menu() {
    clear
    echo -e "${BLUE}=== Komponenten stoppen ===${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} Alle Komponenten stoppen"
    echo -e "${CYAN}2)${NC} n8n stoppen"
    echo -e "${CYAN}3)${NC} MCP-Server stoppen"
    echo -e "${CYAN}4)${NC} Ollama stoppen"
    echo -e "${CYAN}5)${NC} OpenHands stoppen"
    echo -e "${CYAN}6)${NC} Llamafile stoppen"
    echo -e "${CYAN}7)${NC} Zurück zum Hauptmenü"
    echo -e "${CYAN}0)${NC} Beenden"
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
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_stop_menu
            ;;
    esac
}

# Function to display the logs menu
show_logs_menu() {
    clear
    echo -e "${BLUE}=== Logs anzeigen ===${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} n8n Logs"
    echo -e "${CYAN}2)${NC} MCP-Server Logs"
    echo -e "${CYAN}3)${NC} Ollama Logs"
    echo -e "${CYAN}4)${NC} OpenHands Logs"
    echo -e "${CYAN}5)${NC} Llamafile Logs"
    echo -e "${CYAN}6)${NC} Alle Logs"
    echo -e "${CYAN}7)${NC} Zurück zum Hauptmenü"
    echo -e "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            clear
            echo -e "${BLUE}=== n8n Logs ===${NC}"
            echo ""
            show_logs "n8n" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        2) 
            clear
            echo -e "${BLUE}=== MCP-Server Logs ===${NC}"
            echo ""
            show_logs "mcp" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        3) 
            clear
            echo -e "${BLUE}=== Ollama Logs ===${NC}"
            echo ""
            show_logs "ollama" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        4) 
            clear
            echo -e "${BLUE}=== OpenHands Logs ===${NC}"
            echo ""
            show_logs "openhands" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        5) 
            clear
            echo -e "${BLUE}=== Llamafile Logs ===${NC}"
            echo ""
            show_logs "llamafile" "false"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_logs_menu
            ;;
        6) 
            clear
            echo -e "${BLUE}=== Alle Logs ===${NC}"
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
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_logs_menu
            ;;
    esac
}

# Function to display the configuration menu
show_config_menu() {
    clear
    echo -e "${BLUE}=== Konfiguration ===${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} LLM API-Key konfigurieren"
    echo -e "${CYAN}2)${NC} GitHub Token konfigurieren"
    echo -e "${CYAN}3)${NC} OpenProject Token konfigurieren"
    echo -e "${CYAN}4)${NC} n8n API-Key konfigurieren"
    echo -e "${CYAN}5)${NC} Workspace-Pfad konfigurieren"
    echo -e "${CYAN}6)${NC} LLM wechseln"
    echo -e "${CYAN}7)${NC} Zurück zum Hauptmenü"
    echo -e "${CYAN}0)${NC} Beenden"
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
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_config_menu
            ;;
    esac
}

# Function to display the switch LLM menu
show_switch_llm_menu() {
    clear
    echo -e "${BLUE}=== LLM wechseln ===${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} Llamafile (lokal)"
    echo -e "${CYAN}2)${NC} Claude (Anthropic)"
    echo -e "${CYAN}3)${NC} GPT-4o (OpenAI)"
    echo -e "${CYAN}4)${NC} Zurück zum Konfigurationsmenü"
    echo -e "${CYAN}5)${NC} Zurück zum Hauptmenü"
    echo -e "${CYAN}0)${NC} Beenden"
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
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_switch_llm_menu
            ;;
    esac
}

# Function to display the list menu
show_list_menu() {
    clear
    echo -e "${BLUE}=== Ressourcen auflisten ===${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} Workflows auflisten"
    echo -e "${CYAN}2)${NC} Modelle auflisten"
    echo -e "${CYAN}3)${NC} Container auflisten"
    echo -e "${CYAN}4)${NC} Zurück zum Hauptmenü"
    echo -e "${CYAN}0)${NC} Beenden"
    echo ""
    echo -n "Bitte wählen Sie eine Option: "
    read -r option
    
    case "${option}" in
        1) 
            clear
            echo -e "${BLUE}=== Workflows ===${NC}"
            echo ""
            list_resources "workflows"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_list_menu
            ;;
        2) 
            clear
            echo -e "${BLUE}=== Modelle ===${NC}"
            echo ""
            list_resources "models"
            echo ""
            echo -n "Drücken Sie eine Taste, um fortzufahren..."
            read -r
            show_list_menu
            ;;
        3) 
            clear
            echo -e "${BLUE}=== Container ===${NC}"
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
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_list_menu
            ;;
    esac
}

# Function to display the backup menu
show_backup_menu() {
    clear
    echo -e "${BLUE}=== Backup & Wiederherstellung ===${NC}"
    echo ""
    echo -e "${CYAN}1)${NC} n8n Backup erstellen"
    echo -e "${CYAN}2)${NC} OpenHands Backup erstellen"
    echo -e "${CYAN}3)${NC} Alle Komponenten sichern"
    echo -e "${CYAN}4)${NC} Backup wiederherstellen"
    echo -e "${CYAN}5)${NC} Zurück zum Hauptmenü"
    echo -e "${CYAN}0)${NC} Beenden"
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
            echo "Ungültige Option. Bitte erneut versuchen."
            sleep 2
            show_backup_menu
            ;;
    esac
}

# Function to display the restore menu
show_restore_menu() {
    clear
    echo -e "${BLUE}=== Backup wiederherstellen ===${NC}"
    echo ""
    
    # List available backups
    echo -e "${CYAN}Verfügbare Backups:${NC}"
    echo ""
    
    # Check if backup directory exists
    if [[ ! -d "${BACKUP_DIR}" ]]; then
        echo "Keine Backups gefunden."
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
        echo "Keine Backups gefunden."
        echo ""
        echo -n "Drücken Sie eine Taste, um fortzufahren..."
        read -r
        show_backup_menu
        return
    fi
    
    # Display backup files
    for i in "${!backup_files[@]}"; do
        echo -e "${CYAN}$((i+1)))${NC} ${backup_files[i]}"
    done
    
    echo ""
    echo -e "${CYAN}$((${#backup_files[@]}+1)))${NC} Zurück zum Backup-Menü"
    echo -e "${CYAN}0)${NC} Beenden"
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
        echo "Ungültige Option. Bitte erneut versuchen."
        sleep 2
        show_restore_menu
    fi
}

# Function to display the AI menu
show_ai_menu() {
    clear
    echo -e "${BLUE}=== KI-Befehle ===${NC}"
    echo ""
    echo -e "${CYAN}Bitte geben Sie einen Prompt ein (oder 'q' zum Zurückkehren):${NC}"
    echo ""
    read -r prompt
    
    if [[ "${prompt}" == "q" ]]; then
        show_main_menu
    else
        clear
        echo -e "${BLUE}=== KI-Antwort ===${NC}"
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
    echo -e "${BLUE}=== Hilfe ===${NC}"
    echo ""
    echo -e "${CYAN}Dev-Server CLI - Eine umfassende CLI zur Verwaltung des Dev-Server-Workflows${NC}"
    echo ""
    echo -e "Verwendung: dev-server [Befehl] [Optionen]"
    echo ""
    echo -e "${CYAN}Verfügbare Befehle:${NC}"
    echo -e "  help                     Zeigt diese Hilfe an"
    echo -e "  status                   Zeigt den Status aller Komponenten an"
    echo -e "  start [Komponente]        Startet eine Komponente"
    echo -e "  stop [Komponente]         Stoppt eine Komponente"
    echo -e "  restart [Komponente]      Startet eine Komponente neu"
    echo -e "  logs [Komponente]         Zeigt die Logs einer Komponente an"
    echo -e "  config [Option] [Wert]    Konfiguriert eine Option"
    echo -e "  list [Ressourcentyp]      Listet verfügbare Ressourcen auf"
    echo -e "  install [Komponente]      Installiert eine Komponente"
    echo -e "  switch-llm [LLM]          Wechselt zwischen LLMs (llamafile, claude)"
    echo -e "  update [Komponente]       Aktualisiert eine Komponente"
    echo -e "  backup [Komponente]       Erstellt ein Backup einer Komponente"
    echo -e "  restore [Backup]          Stellt ein Backup wieder her"
    echo -e "  ai [Prompt]               Führt einen KI-Befehl aus"
    echo -e "  menu                     Öffnet das interaktive Menü"
    echo ""
    echo -e "${CYAN}Komponenten:${NC}"
    echo -e "  all                        Alle Komponenten"
    echo -e "  mcp                        MCP-Server"
    echo -e "  n8n                        n8n-Workflow-Engine"
    echo -e "  ollama                     Ollama LLM-Server"
    echo -e "  openhands                  OpenHands KI-Agent"
    echo -e "  llamafile                  Llamafile LLM"
    echo -e "  shellgpt                   ShellGPT CLI"
    echo ""
    echo -e "${CYAN}Beispiele:${NC}"
    echo -e "  dev-server status"
    echo -e "  dev-server start mcp"
    echo -e "  dev-server logs n8n"
    echo -e "  dev-server ai \"Wie starte ich den MCP-Server?\""
    echo -e "  dev-server menu"
    echo ""
    echo -n "Drücken Sie eine Taste, um fortzufahren..."
    read -r
    show_main_menu
}

# Start the menu
show_main_menu