#!/bin/bash
# Interactive UI for Dev-Server-Workflow
# This script provides an interactive menu-based interface for managing the Dev-Server-Workflow

# Set strict error handling
set -euo pipefail

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Source error handler
source "${BASE_DIR}/cli/error_handler.sh"

# Source config manager
source "${BASE_DIR}/cli/config_manager.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Set up error trap
trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR

# Check if dialog is installed
check_dialog() {
    if ! command -v dialog &> /dev/null; then
        echo -e "${YELLOW}[WARN] Dialog is not installed. Installing...${NC}"
        apt-get update && apt-get install -y dialog
        
        if ! command -v dialog &> /dev/null; then
            echo -e "${RED}[ERROR] Failed to install dialog. Using fallback text-based menu.${NC}"
            return 1
        fi
    fi
    
    return 0
}

# Show main menu using dialog
show_main_menu_dialog() {
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Hauptmenü" \
        --menu "Wählen Sie eine Option:" 20 78 12 \
        "1" "Status anzeigen" \
        "2" "MCP-Server verwalten" \
        "3" "n8n verwalten" \
        "4" "Logs anzeigen" \
        "5" "Konfiguration" \
        "6" "Monitoring" \
        "7" "Backup und Wiederherstellung" \
        "8" "Installation" \
        "9" "Dokumentation" \
        "10" "Über" \
        "11" "Beenden" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        1) show_status_dialog ;;
        2) show_mcp_servers_dialog ;;
        3) show_n8n_dialog ;;
        4) show_logs_dialog ;;
        5) show_config_dialog ;;
        6) show_monitoring_dialog ;;
        7) show_backup_dialog ;;
        8) show_installation_dialog ;;
        9) show_documentation_dialog ;;
        10) show_about_dialog ;;
        11) clear; echo -e "${GREEN}Auf Wiedersehen!${NC}"; exit 0 ;;
        *) show_main_menu_dialog ;;
    esac
}

# Show status dialog
show_status_dialog() {
    # Collect status information
    local status_output=$(
        echo "=== System Status ==="
        echo "Datum: $(date)"
        echo "Hostname: $(hostname)"
        echo "Kernel: $(uname -r)"
        echo "CPU: $(grep "model name" /proc/cpuinfo | head -1 | cut -d: -f2 | sed 's/^[ \t]*//')"
        echo "RAM: $(free -h | grep Mem | awk '{print $2}')"
        echo "Disk: $(df -h / | grep / | awk '{print $2}')"
        echo ""
        echo "=== Docker Status ==="
        echo "Docker Version: $(docker --version)"
        echo "Laufende Container: $(docker ps -q | wc -l)"
        echo "Alle Container: $(docker ps -a -q | wc -l)"
        echo "Images: $(docker images -q | wc -l)"
        echo "Volumes: $(docker volume ls -q | wc -l)"
        echo "Networks: $(docker network ls -q | wc -l)"
        echo ""
        echo "=== MCP-Server Status ==="
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E 'mcp$|mcp-bridge$' || echo "Keine MCP-Server gefunden"
        echo ""
        echo "=== n8n Status ==="
        docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "n8n" || echo "n8n nicht gefunden"
    )
    
    # Show status in dialog
    dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Systemstatus" \
        --msgbox "$status_output" 30 100
    
    # Return to main menu
    show_main_menu_dialog
}

# Show MCP servers dialog
show_mcp_servers_dialog() {
    # Get list of MCP servers
    local mcp_servers=$(docker ps --format "{{.Names}}" | grep -E 'mcp$|mcp-bridge$' | sort)
    
    if [[ -z "$mcp_servers" ]]; then
        dialog --clear --backtitle "Dev-Server-Workflow" \
            --title "MCP-Server verwalten" \
            --msgbox "Keine MCP-Server gefunden. Starten Sie zuerst die MCP-Server." 10 60
        show_main_menu_dialog
        return
    fi
    
    # Create menu items
    local menu_items=()
    local i=1
    
    menu_items+=("0" "Alle MCP-Server starten")
    menu_items+=("00" "Alle MCP-Server stoppen")
    
    for server in $mcp_servers; do
        menu_items+=("$i" "$server")
        i=$((i + 1))
    done
    
    menu_items+=("b" "Zurück zum Hauptmenü")
    
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "MCP-Server verwalten" \
        --menu "Wählen Sie einen MCP-Server:" 20 78 15 \
        "${menu_items[@]}" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        0) 
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "MCP-Server starten" \
                --infobox "Starte alle MCP-Server..." 5 40
            
            # Start all MCP servers
            cd "${BASE_DIR}"
            ./start-mcp-servers.sh
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "MCP-Server starten" \
                --msgbox "Alle MCP-Server wurden gestartet." 6 40
            
            show_mcp_servers_dialog
            ;;
        00)
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "MCP-Server stoppen" \
                --infobox "Stoppe alle MCP-Server..." 5 40
            
            # Stop all MCP servers
            cd "${BASE_DIR}"
            ./stop-mcp-servers.sh
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "MCP-Server stoppen" \
                --msgbox "Alle MCP-Server wurden gestoppt." 6 40
            
            show_mcp_servers_dialog
            ;;
        b) show_main_menu_dialog ;;
        *)
            if [[ -n "$choice" ]]; then
                # Get selected server
                local selected_server=$(echo "$mcp_servers" | sed -n "${choice}p")
                
                show_mcp_server_actions_dialog "$selected_server"
            else
                show_mcp_servers_dialog
            fi
            ;;
    esac
}

# Show MCP server actions dialog
show_mcp_server_actions_dialog() {
    local server_name="$1"
    
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "MCP-Server: $server_name" \
        --menu "Wählen Sie eine Aktion:" 20 78 10 \
        "1" "Status anzeigen" \
        "2" "Logs anzeigen" \
        "3" "Tools auflisten" \
        "4" "Tool aufrufen" \
        "5" "Ressourcen auflisten" \
        "6" "Ressource abrufen" \
        "7" "Prompts auflisten" \
        "8" "Prompt aufrufen" \
        "9" "Server neustarten" \
        "10" "Server stoppen" \
        "b" "Zurück zur MCP-Server-Liste" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        1)
            # Show server status
            local status_output=$(
                echo "=== MCP-Server: $server_name ==="
                echo ""
                docker inspect "$server_name" | jq -r '.[0] | "Status: " + .State.Status + "\nStartzeit: " + .State.StartedAt + "\nImage: " + .Config.Image + "\nPorts: " + (.NetworkSettings.Ports | tostring) + "\nVolumes: " + (.Mounts | map(.Source + " -> " + .Destination) | join("\n"))'
            )
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Status: $server_name" \
                --msgbox "$status_output" 20 78
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        2)
            # Show server logs
            local logs=$(docker logs "$server_name" 2>&1 | tail -n 100)
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Logs: $server_name" \
                --msgbox "$logs" 30 100
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        3)
            # List tools
            local tools_output=$(
                echo "=== Tools für MCP-Server: $server_name ==="
                echo ""
                cd "${BASE_DIR}/docker-mcp-ecosystem"
                ./scripts/mcp-server-manager.sh list-tools --server "$server_name" 2>&1
            )
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Tools: $server_name" \
                --msgbox "$tools_output" 30 100
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        4)
            # Call tool
            local tool_name=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Tool aufrufen: $server_name" \
                --inputbox "Geben Sie den Namen des Tools ein:" 8 60 \
                3>&1 1>&2 2>&3)
            
            if [[ -n "$tool_name" ]]; then
                local args=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Tool aufrufen: $server_name" \
                    --inputbox "Geben Sie die Argumente im JSON-Format ein (oder leer lassen):" 8 60 "{}" \
                    3>&1 1>&2 2>&3)
                
                local tool_output=$(
                    echo "=== Tool aufrufen: $tool_name für MCP-Server: $server_name ==="
                    echo ""
                    cd "${BASE_DIR}/docker-mcp-ecosystem"
                    ./scripts/mcp-server-manager.sh call-tool --server "$server_name" --tool "$tool_name" --args "$args" 2>&1
                )
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Tool-Ergebnis: $tool_name" \
                    --msgbox "$tool_output" 30 100
            fi
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        5)
            # List resources
            local resources_output=$(
                echo "=== Ressourcen für MCP-Server: $server_name ==="
                echo ""
                cd "${BASE_DIR}/docker-mcp-ecosystem"
                ./scripts/mcp-server-manager.sh list-resources --server "$server_name" 2>&1
            )
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Ressourcen: $server_name" \
                --msgbox "$resources_output" 30 100
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        6)
            # Get resource
            local resource_id=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Ressource abrufen: $server_name" \
                --inputbox "Geben Sie die Ressourcen-ID ein:" 8 60 \
                3>&1 1>&2 2>&3)
            
            if [[ -n "$resource_id" ]]; then
                local resource_output=$(
                    echo "=== Ressource abrufen: $resource_id für MCP-Server: $server_name ==="
                    echo ""
                    cd "${BASE_DIR}/docker-mcp-ecosystem"
                    ./scripts/mcp-server-manager.sh get-resource --server "$server_name" --resource "$resource_id" 2>&1
                )
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Ressource: $resource_id" \
                    --msgbox "$resource_output" 30 100
            fi
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        7)
            # List prompts
            local prompts_output=$(
                echo "=== Prompts für MCP-Server: $server_name ==="
                echo ""
                cd "${BASE_DIR}/docker-mcp-ecosystem"
                ./scripts/mcp-server-manager.sh list-prompts --server "$server_name" 2>&1
            )
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Prompts: $server_name" \
                --msgbox "$prompts_output" 30 100
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        8)
            # Call prompt
            local prompt_id=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Prompt aufrufen: $server_name" \
                --inputbox "Geben Sie die Prompt-ID ein:" 8 60 \
                3>&1 1>&2 2>&3)
            
            if [[ -n "$prompt_id" ]]; then
                local args=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Prompt aufrufen: $server_name" \
                    --inputbox "Geben Sie die Argumente im JSON-Format ein (oder leer lassen):" 8 60 "{}" \
                    3>&1 1>&2 2>&3)
                
                local prompt_output=$(
                    echo "=== Prompt aufrufen: $prompt_id für MCP-Server: $server_name ==="
                    echo ""
                    cd "${BASE_DIR}/docker-mcp-ecosystem"
                    ./scripts/mcp-server-manager.sh call-prompt --server "$server_name" --prompt "$prompt_id" --prompt-args "$args" 2>&1
                )
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Prompt-Ergebnis: $prompt_id" \
                    --msgbox "$prompt_output" 30 100
            fi
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        9)
            # Restart server
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Server neustarten: $server_name" \
                --yesno "Möchten Sie den Server $server_name wirklich neustarten?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Server neustarten: $server_name" \
                    --infobox "Starte Server $server_name neu..." 5 40
                
                docker restart "$server_name"
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Server neustarten: $server_name" \
                    --msgbox "Server $server_name wurde neugestartet." 6 40
            fi
            
            show_mcp_server_actions_dialog "$server_name"
            ;;
        10)
            # Stop server
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Server stoppen: $server_name" \
                --yesno "Möchten Sie den Server $server_name wirklich stoppen?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Server stoppen: $server_name" \
                    --infobox "Stoppe Server $server_name..." 5 40
                
                docker stop "$server_name"
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Server stoppen: $server_name" \
                    --msgbox "Server $server_name wurde gestoppt." 6 40
            fi
            
            show_mcp_servers_dialog
            ;;
        b) show_mcp_servers_dialog ;;
        *) show_mcp_server_actions_dialog "$server_name" ;;
    esac
}

# Show n8n dialog
show_n8n_dialog() {
    # Check if n8n is running
    if ! docker ps --format "{{.Names}}" | grep -q "^n8n$"; then
        dialog --clear --backtitle "Dev-Server-Workflow" \
            --title "n8n verwalten" \
            --yesno "n8n ist nicht gestartet. Möchten Sie n8n starten?" 7 60
        
        local result=$?
        
        if [[ $result -eq 0 ]]; then
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n starten" \
                --infobox "Starte n8n..." 5 40
            
            cd "${BASE_DIR}"
            docker compose -f docker compose.yml up -d n8n
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n starten" \
                --msgbox "n8n wurde gestartet." 6 40
        else
            show_main_menu_dialog
            return
        fi
    fi
    
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "n8n verwalten" \
        --menu "Wählen Sie eine Aktion:" 15 60 8 \
        "1" "Status anzeigen" \
        "2" "Logs anzeigen" \
        "3" "Workflows auflisten" \
        "4" "Workflow importieren" \
        "5" "n8n Web-UI öffnen" \
        "6" "n8n neustarten" \
        "7" "n8n stoppen" \
        "b" "Zurück zum Hauptmenü" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        1)
            # Show n8n status
            local status_output=$(
                echo "=== n8n Status ==="
                echo ""
                docker inspect n8n | jq -r '.[0] | "Status: " + .State.Status + "\nStartzeit: " + .State.StartedAt + "\nImage: " + .Config.Image + "\nPorts: " + (.NetworkSettings.Ports | tostring) + "\nVolumes: " + (.Mounts | map(.Source + " -> " + .Destination) | join("\n"))'
            )
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n Status" \
                --msgbox "$status_output" 20 78
            
            show_n8n_dialog
            ;;
        2)
            # Show n8n logs
            local logs=$(docker logs n8n 2>&1 | tail -n 100)
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n Logs" \
                --msgbox "$logs" 30 100
            
            show_n8n_dialog
            ;;
        3)
            # List workflows
            local workflows_output=$(
                echo "=== n8n Workflows ==="
                echo ""
                docker exec n8n n8n list workflows
            )
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n Workflows" \
                --msgbox "$workflows_output" 30 100
            
            show_n8n_dialog
            ;;
        4)
            # Import workflow
            local workflow_file=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Workflow importieren" \
                --inputbox "Geben Sie den Pfad zur Workflow-Datei ein:" 8 60 \
                3>&1 1>&2 2>&3)
            
            if [[ -n "$workflow_file" && -f "$workflow_file" ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Workflow importieren" \
                    --infobox "Importiere Workflow..." 5 40
                
                docker cp "$workflow_file" n8n:/tmp/workflow.json
                docker exec n8n n8n import:workflow --input=/tmp/workflow.json
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Workflow importieren" \
                    --msgbox "Workflow wurde importiert." 6 40
            else
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Workflow importieren" \
                    --msgbox "Datei nicht gefunden: $workflow_file" 6 60
            fi
            
            show_n8n_dialog
            ;;
        5)
            # Open n8n Web-UI
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n Web-UI öffnen" \
                --msgbox "Die n8n Web-UI wird im Browser geöffnet.\n\nURL: http://localhost:5678" 8 60
            
            # Try to open browser (this might not work in all environments)
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:5678" &
            elif command -v open &> /dev/null; then
                open "http://localhost:5678" &
            fi
            
            show_n8n_dialog
            ;;
        6)
            # Restart n8n
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n neustarten" \
                --yesno "Möchten Sie n8n wirklich neustarten?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "n8n neustarten" \
                    --infobox "Starte n8n neu..." 5 40
                
                docker restart n8n
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "n8n neustarten" \
                    --msgbox "n8n wurde neugestartet." 6 40
            fi
            
            show_n8n_dialog
            ;;
        7)
            # Stop n8n
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n stoppen" \
                --yesno "Möchten Sie n8n wirklich stoppen?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "n8n stoppen" \
                    --infobox "Stoppe n8n..." 5 40
                
                docker stop n8n
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "n8n stoppen" \
                    --msgbox "n8n wurde gestoppt." 6 40
            fi
            
            show_main_menu_dialog
            ;;
        b) show_main_menu_dialog ;;
        *) show_n8n_dialog ;;
    esac
}

# Show logs dialog
show_logs_dialog() {
    # Get list of containers
    local containers=$(docker ps --format "{{.Names}}" | sort)
    
    if [[ -z "$containers" ]]; then
        dialog --clear --backtitle "Dev-Server-Workflow" \
            --title "Logs anzeigen" \
            --msgbox "Keine Container gefunden." 6 40
        show_main_menu_dialog
        return
    fi
    
    # Create menu items
    local menu_items=()
    local i=1
    
    for container in $containers; do
        menu_items+=("$i" "$container")
        i=$((i + 1))
    done
    
    menu_items+=("b" "Zurück zum Hauptmenü")
    
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Logs anzeigen" \
        --menu "Wählen Sie einen Container:" 20 78 15 \
        "${menu_items[@]}" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        b) show_main_menu_dialog ;;
        *)
            if [[ -n "$choice" ]]; then
                # Get selected container
                local selected_container=$(echo "$containers" | sed -n "${choice}p")
                
                # Show logs
                local logs=$(docker logs "$selected_container" 2>&1 | tail -n 500)
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Logs: $selected_container" \
                    --msgbox "$logs" 30 100
                
                show_logs_dialog
            else
                show_logs_dialog
            fi
            ;;
    esac
}

# Show configuration dialog
show_config_dialog() {
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Konfiguration" \
        --menu "Wählen Sie eine Option:" 15 60 8 \
        "1" "Konfiguration anzeigen" \
        "2" "Konfiguration bearbeiten" \
        "3" "Umgebungsvariablen anzeigen" \
        "4" "Umgebungsvariable setzen" \
        "5" "Docker-Compose-Konfiguration anzeigen" \
        "b" "Zurück zum Hauptmenü" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        1)
            # Show configuration
            local config_output=""
            
            if [[ -f "${BASE_DIR}/.env" ]]; then
                config_output+="=== .env Konfiguration ===\n\n"
                config_output+=$(grep -v "^#" "${BASE_DIR}/.env" | grep "=" || echo "Keine Konfiguration gefunden")
                config_output+="\n\n"
            fi
            
            if [[ -f "${BASE_DIR}/cli/config.sh" ]]; then
                config_output+="=== config.sh Konfiguration ===\n\n"
                config_output+=$(grep -E "^[A-Z_]+=.*" "${BASE_DIR}/cli/config.sh" || echo "Keine Konfiguration gefunden")
            fi
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Konfiguration anzeigen" \
                --msgbox "$config_output" 30 100
            
            show_config_dialog
            ;;
        2)
            # Edit configuration
            local config_file=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Konfiguration bearbeiten" \
                --menu "Wählen Sie eine Konfigurationsdatei:" 15 60 4 \
                "1" ".env" \
                "2" "cli/config.sh" \
                "3" "docker compose.yml" \
                "b" "Zurück" \
                3>&1 1>&2 2>&3)
            
            case "$config_file" in
                1)
                    # Check if .env exists, if not, copy from .env.example
                    if [[ ! -f "${BASE_DIR}/.env" && -f "${BASE_DIR}/.env.example" ]]; then
                        cp "${BASE_DIR}/.env.example" "${BASE_DIR}/.env"
                    fi
                    
                    # Edit .env
                    ${EDITOR:-nano} "${BASE_DIR}/.env"
                    ;;
                2)
                    # Edit config.sh
                    ${EDITOR:-nano} "${BASE_DIR}/cli/config.sh"
                    ;;
                3)
                    # Edit docker compose.yml
                    ${EDITOR:-nano} "${BASE_DIR}/docker-compose.yml"
                    ;;
                b|*) ;;
            esac
            
            show_config_dialog
            ;;
        3)
            # Show environment variables
            local env_output=$(env | sort)
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Umgebungsvariablen anzeigen" \
                --msgbox "$env_output" 30 100
            
            show_config_dialog
            ;;
        4)
            # Set environment variable
            local var_name=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Umgebungsvariable setzen" \
                --inputbox "Geben Sie den Namen der Umgebungsvariable ein:" 8 60 \
                3>&1 1>&2 2>&3)
            
            if [[ -n "$var_name" ]]; then
                local var_value=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Umgebungsvariable setzen" \
                    --inputbox "Geben Sie den Wert für $var_name ein:" 8 60 \
                    3>&1 1>&2 2>&3)
                
                # Set environment variable
                export "$var_name=$var_value"
                
                # Update .env file
                if [[ -f "${BASE_DIR}/.env" ]]; then
                    if grep -q "^$var_name=" "${BASE_DIR}/.env"; then
                        sed -i "s|^$var_name=.*|$var_name=$var_value|" "${BASE_DIR}/.env"
                    else
                        echo "$var_name=$var_value" >> "${BASE_DIR}/.env"
                    fi
                else
                    echo "$var_name=$var_value" > "${BASE_DIR}/.env"
                fi
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Umgebungsvariable setzen" \
                    --msgbox "Umgebungsvariable $var_name wurde gesetzt und in .env gespeichert." 6 60
            fi
            
            show_config_dialog
            ;;
        5)
            # Show Docker Compose configuration
            local compose_output=$(docker compose -f "${BASE_DIR}/docker-compose.yml" config)
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Docker-Compose-Konfiguration anzeigen" \
                --msgbox "$compose_output" 30 100
            
            show_config_dialog
            ;;
        b) show_main_menu_dialog ;;
        *) show_config_dialog ;;
    esac
}

# Show monitoring dialog
show_monitoring_dialog() {
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Monitoring" \
        --menu "Wählen Sie eine Option:" 15 60 8 \
        "1" "System-Ressourcen anzeigen" \
        "2" "Docker-Container-Statistiken anzeigen" \
        "3" "MCP-Server-Gesundheit prüfen" \
        "4" "Prometheus-Exporter starten" \
        "5" "Grafana öffnen" \
        "b" "Zurück zum Hauptmenü" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        1)
            # Show system resources
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "System-Ressourcen" \
                --infobox "Sammle System-Ressourcen..." 5 40
            
            local resources_output=$(
                echo "=== CPU-Auslastung ==="
                top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print "CPU-Auslastung: " 100 - $1 "%"}'
                echo ""
                echo "=== Speicherauslastung ==="
                free -h
                echo ""
                echo "=== Festplattennutzung ==="
                df -h
                echo ""
                echo "=== Top-Prozesse nach CPU-Auslastung ==="
                ps aux --sort=-%cpu | head -11
                echo ""
                echo "=== Top-Prozesse nach Speicherauslastung ==="
                ps aux --sort=-%mem | head -11
            )
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "System-Ressourcen" \
                --msgbox "$resources_output" 30 100
            
            show_monitoring_dialog
            ;;
        2)
            # Show Docker container statistics
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Docker-Container-Statistiken" \
                --infobox "Sammle Docker-Container-Statistiken..." 5 40
            
            local stats_output=$(docker stats --no-stream)
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Docker-Container-Statistiken" \
                --msgbox "$stats_output" 30 100
            
            show_monitoring_dialog
            ;;
        3)
            # Check MCP server health
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "MCP-Server-Gesundheit" \
                --infobox "Prüfe MCP-Server-Gesundheit..." 5 40
            
            local health_output="=== MCP-Server-Gesundheit ===\n\n"
            local mcp_servers=$(docker ps --format "{{.Names}}" | grep -E 'mcp$|mcp-bridge$' | sort)
            
            if [[ -z "$mcp_servers" ]]; then
                health_output+="Keine MCP-Server gefunden."
            else
                for server in $mcp_servers; do
                    health_output+="$server: "
                    
                    # Get container IP
                    local container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$server")
                    
                    # Check health endpoint
                    if docker exec "$server" curl -s "http://localhost:3333/health" | grep -q "ok"; then
                        health_output+="Gesund\n"
                    else
                        health_output+="Nicht gesund\n"
                    fi
                done
            fi
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "MCP-Server-Gesundheit" \
                --msgbox "$health_output" 20 60
            
            show_monitoring_dialog
            ;;
        4)
            # Start Prometheus exporter
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Prometheus-Exporter starten" \
                --yesno "Möchten Sie den Prometheus-Exporter starten?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Prometheus-Exporter starten" \
                    --infobox "Starte Prometheus-Exporter..." 5 40
                
                # Check if Python is installed
                if ! command -v python3 &> /dev/null; then
                    dialog --clear --backtitle "Dev-Server-Workflow" \
                        --title "Prometheus-Exporter starten" \
                        --msgbox "Python 3 ist nicht installiert. Bitte installieren Sie Python 3." 6 60
                    show_monitoring_dialog
                    return
                fi
                
                # Check if required packages are installed
                if ! python3 -c "import psutil, docker, prometheus_client" &> /dev/null; then
                    dialog --clear --backtitle "Dev-Server-Workflow" \
                        --title "Prometheus-Exporter starten" \
                        --infobox "Installiere erforderliche Python-Pakete..." 5 40
                    
                    pip3 install psutil docker prometheus_client
                fi
                
                # Start Prometheus exporter in background
                nohup python3 "${BASE_DIR}/src/monitoring/prometheus_exporter.py" > "${BASE_DIR}/logs/prometheus_exporter.log" 2>&1 &
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Prometheus-Exporter starten" \
                    --msgbox "Prometheus-Exporter wurde gestartet.\n\nMetriken sind verfügbar unter: http://localhost:9090" 8 60
            fi
            
            show_monitoring_dialog
            ;;
        5)
            # Open Grafana
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Grafana öffnen" \
                --msgbox "Grafana wird im Browser geöffnet.\n\nURL: http://localhost:3000\n\nStandardanmeldedaten:\nBenutzer: admin\nPasswort: admin" 10 60
            
            # Try to open browser (this might not work in all environments)
            if command -v xdg-open &> /dev/null; then
                xdg-open "http://localhost:3000" &
            elif command -v open &> /dev/null; then
                open "http://localhost:3000" &
            fi
            
            show_monitoring_dialog
            ;;
        b) show_main_menu_dialog ;;
        *) show_monitoring_dialog ;;
    esac
}

# Show backup dialog
show_backup_dialog() {
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Backup und Wiederherstellung" \
        --menu "Wählen Sie eine Option:" 15 60 8 \
        "1" "Backup erstellen" \
        "2" "Backup wiederherstellen" \
        "3" "Backups auflisten" \
        "4" "Backup löschen" \
        "b" "Zurück zum Hauptmenü" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        1)
            # Create backup
            local backup_name=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Backup erstellen" \
                --inputbox "Geben Sie einen Namen für das Backup ein:" 8 60 "backup_$(date +%Y%m%d_%H%M%S)" \
                3>&1 1>&2 2>&3)
            
            if [[ -n "$backup_name" ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Backup erstellen" \
                    --infobox "Erstelle Backup $backup_name..." 5 40
                
                # Create backup directory if it doesn't exist
                mkdir -p "${BASE_DIR}/backups"
                
                # Create backup
                local backup_dir="${BASE_DIR}/backups/$backup_name"
                mkdir -p "$backup_dir"
                
                # Backup configuration
                cp -r "${BASE_DIR}/.env" "$backup_dir/" 2>/dev/null || true
                cp -r "${BASE_DIR}/cli/config.sh" "$backup_dir/" 2>/dev/null || true
                cp -r "${BASE_DIR}/docker-compose.yml" "$backup_dir/" 2>/dev/null || true
                
                # Backup data
                if [[ -d "${BASE_DIR}/data" ]]; then
                    cp -r "${BASE_DIR}/data" "$backup_dir/" 2>/dev/null || true
                fi
                
                # Create backup info file
                echo "Backup erstellt am: $(date)" > "$backup_dir/backup_info.txt"
                echo "Hostname: $(hostname)" >> "$backup_dir/backup_info.txt"
                echo "Benutzer: $(whoami)" >> "$backup_dir/backup_info.txt"
                echo "Docker-Version: $(docker --version)" >> "$backup_dir/backup_info.txt"
                echo "Laufende Container:" >> "$backup_dir/backup_info.txt"
                docker ps --format "{{.Names}}" >> "$backup_dir/backup_info.txt"
                
                # Create archive
                tar -czf "${BASE_DIR}/backups/${backup_name}.tar.gz" -C "${BASE_DIR}/backups" "$backup_name"
                
                # Remove temporary directory
                rm -rf "$backup_dir"
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Backup erstellen" \
                    --msgbox "Backup wurde erstellt: ${BASE_DIR}/backups/${backup_name}.tar.gz" 6 60
            fi
            
            show_backup_dialog
            ;;
        2)
            # Restore backup
            local backups=$(find "${BASE_DIR}/backups" -name "*.tar.gz" -type f | sort -r)
            
            if [[ -z "$backups" ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Backup wiederherstellen" \
                    --msgbox "Keine Backups gefunden." 6 40
                show_backup_dialog
                return
            fi
            
            # Create menu items
            local menu_items=()
            local i=1
            
            for backup in $backups; do
                local backup_name=$(basename "$backup")
                local backup_date=$(date -r "$backup" "+%Y-%m-%d %H:%M:%S")
                menu_items+=("$i" "$backup_name ($backup_date)")
                i=$((i + 1))
            done
            
            menu_items+=("b" "Zurück")
            
            # Show menu
            local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Backup wiederherstellen" \
                --menu "Wählen Sie ein Backup:" 20 78 15 \
                "${menu_items[@]}" \
                3>&1 1>&2 2>&3)
            
            # Handle menu choice
            case "$choice" in
                b) show_backup_dialog ;;
                *)
                    if [[ -n "$choice" ]]; then
                        # Get selected backup
                        local selected_backup=$(echo "$backups" | sed -n "${choice}p")
                        local backup_name=$(basename "$selected_backup")
                        
                        dialog --clear --backtitle "Dev-Server-Workflow" \
                            --title "Backup wiederherstellen" \
                            --yesno "Möchten Sie das Backup $backup_name wirklich wiederherstellen?\n\nAchtung: Alle aktuellen Daten werden überschrieben!" 10 60
                        
                        local result=$?
                        
                        if [[ $result -eq 0 ]]; then
                            dialog --clear --backtitle "Dev-Server-Workflow" \
                                --title "Backup wiederherstellen" \
                                --infobox "Stelle Backup $backup_name wieder her..." 5 40
                            
                            # Create temporary directory
                            local temp_dir="${BASE_DIR}/backups/temp"
                            mkdir -p "$temp_dir"
                            
                            # Extract backup
                            tar -xzf "$selected_backup" -C "$temp_dir"
                            
                            # Stop all containers
                            docker compose -f "${BASE_DIR}/docker-compose.yml" down
                            
                            # Restore configuration
                            cp -r "$temp_dir"/*/.env "${BASE_DIR}/" 2>/dev/null || true
                            cp -r "$temp_dir"/*/config.sh "${BASE_DIR}/cli/" 2>/dev/null || true
                            cp -r "$temp_dir"/*/docker-compose.yml "${BASE_DIR}/" 2>/dev/null || true
                            
                            # Restore data
                            if [[ -d "$temp_dir"/*/data ]]; then
                                cp -r "$temp_dir"/*/data "${BASE_DIR}/" 2>/dev/null || true
                            fi
                            
                            # Remove temporary directory
                            rm -rf "$temp_dir"
                            
                            dialog --clear --backtitle "Dev-Server-Workflow" \
                                --title "Backup wiederherstellen" \
                                --msgbox "Backup wurde wiederhergestellt. Starten Sie die Container neu, um die Änderungen zu übernehmen." 6 60
                        fi
                    fi
                    
                    show_backup_dialog
                    ;;
            esac
            ;;
        3)
            # List backups
            local backups=$(find "${BASE_DIR}/backups" -name "*.tar.gz" -type f | sort -r)
            
            if [[ -z "$backups" ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Backups auflisten" \
                    --msgbox "Keine Backups gefunden." 6 40
                show_backup_dialog
                return
            fi
            
            local backup_list="=== Verfügbare Backups ===\n\n"
            
            for backup in $backups; do
                local backup_name=$(basename "$backup")
                local backup_date=$(date -r "$backup" "+%Y-%m-%d %H:%M:%S")
                local backup_size=$(du -h "$backup" | cut -f1)
                
                backup_list+="$backup_name\n"
                backup_list+="  Datum: $backup_date\n"
                backup_list+="  Größe: $backup_size\n\n"
            done
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Backups auflisten" \
                --msgbox "$backup_list" 30 100
            
            show_backup_dialog
            ;;
        4)
            # Delete backup
            local backups=$(find "${BASE_DIR}/backups" -name "*.tar.gz" -type f | sort -r)
            
            if [[ -z "$backups" ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Backup löschen" \
                    --msgbox "Keine Backups gefunden." 6 40
                show_backup_dialog
                return
            fi
            
            # Create menu items
            local menu_items=()
            local i=1
            
            for backup in $backups; do
                local backup_name=$(basename "$backup")
                local backup_date=$(date -r "$backup" "+%Y-%m-%d %H:%M:%S")
                menu_items+=("$i" "$backup_name ($backup_date)")
                i=$((i + 1))
            done
            
            menu_items+=("b" "Zurück")
            
            # Show menu
            local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Backup löschen" \
                --menu "Wählen Sie ein Backup:" 20 78 15 \
                "${menu_items[@]}" \
                3>&1 1>&2 2>&3)
            
            # Handle menu choice
            case "$choice" in
                b) show_backup_dialog ;;
                *)
                    if [[ -n "$choice" ]]; then
                        # Get selected backup
                        local selected_backup=$(echo "$backups" | sed -n "${choice}p")
                        local backup_name=$(basename "$selected_backup")
                        
                        dialog --clear --backtitle "Dev-Server-Workflow" \
                            --title "Backup löschen" \
                            --yesno "Möchten Sie das Backup $backup_name wirklich löschen?" 7 60
                        
                        local result=$?
                        
                        if [[ $result -eq 0 ]]; then
                            dialog --clear --backtitle "Dev-Server-Workflow" \
                                --title "Backup löschen" \
                                --infobox "Lösche Backup $backup_name..." 5 40
                            
                            rm -f "$selected_backup"
                            
                            dialog --clear --backtitle "Dev-Server-Workflow" \
                                --title "Backup löschen" \
                                --msgbox "Backup wurde gelöscht." 6 40
                        fi
                    fi
                    
                    show_backup_dialog
                    ;;
            esac
            ;;
        b) show_main_menu_dialog ;;
        *) show_backup_dialog ;;
    esac
}

# Show installation dialog
show_installation_dialog() {
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Installation" \
        --menu "Wählen Sie eine Option:" 15 60 8 \
        "1" "Abhängigkeiten installieren" \
        "2" "MCP-Server installieren" \
        "3" "n8n installieren" \
        "4" "Monitoring installieren" \
        "5" "Alles installieren" \
        "b" "Zurück zum Hauptmenü" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        1)
            # Install dependencies
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Abhängigkeiten installieren" \
                --yesno "Möchten Sie die Abhängigkeiten installieren?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Abhängigkeiten installieren" \
                    --infobox "Installiere Abhängigkeiten..." 5 40
                
                # Install dependencies
                apt-get update
                apt-get install -y curl jq docker.io docker compose python3 python3-pip
                pip3 install psutil docker prometheus_client
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Abhängigkeiten installieren" \
                    --msgbox "Abhängigkeiten wurden installiert." 6 40
            fi
            
            show_installation_dialog
            ;;
        2)
            # Install MCP servers
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "MCP-Server installieren" \
                --yesno "Möchten Sie die MCP-Server installieren?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "MCP-Server installieren" \
                    --infobox "Installiere MCP-Server..." 5 40
                
                # Install MCP servers
                cd "${BASE_DIR}"
                ./start-mcp-servers.sh
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "MCP-Server installieren" \
                    --msgbox "MCP-Server wurden installiert und gestartet." 6 40
            fi
            
            show_installation_dialog
            ;;
        3)
            # Install n8n
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "n8n installieren" \
                --yesno "Möchten Sie n8n installieren?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "n8n installieren" \
                    --infobox "Installiere n8n..." 5 40
                
                # Install n8n
                cd "${BASE_DIR}"
                docker compose -f docker compose.yml up -d n8n
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "n8n installieren" \
                    --msgbox "n8n wurde installiert und gestartet." 6 40
            fi
            
            show_installation_dialog
            ;;
        4)
            # Install monitoring
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Monitoring installieren" \
                --yesno "Möchten Sie das Monitoring installieren?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Monitoring installieren" \
                    --infobox "Installiere Monitoring..." 5 40
                
                # Install monitoring
                cd "${BASE_DIR}"
                docker compose -f docker compose.yml up -d prometheus grafana
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Monitoring installieren" \
                    --msgbox "Monitoring wurde installiert und gestartet." 6 40
            fi
            
            show_installation_dialog
            ;;
        5)
            # Install everything
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Alles installieren" \
                --yesno "Möchten Sie alle Komponenten installieren?" 7 60
            
            local result=$?
            
            if [[ $result -eq 0 ]]; then
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Alles installieren" \
                    --infobox "Installiere alle Komponenten..." 5 40
                
                # Install dependencies
                apt-get update
                apt-get install -y curl jq docker.io docker compose python3 python3-pip
                pip3 install psutil docker prometheus_client
                
                # Install all components
                cd "${BASE_DIR}"
                ./start-mcp-servers.sh
                docker compose -f docker compose.yml up -d
                
                dialog --clear --backtitle "Dev-Server-Workflow" \
                    --title "Alles installieren" \
                    --msgbox "Alle Komponenten wurden installiert und gestartet." 6 40
            fi
            
            show_installation_dialog
            ;;
        b) show_main_menu_dialog ;;
        *) show_installation_dialog ;;
    esac
}

# Show documentation dialog
show_documentation_dialog() {
    # Show menu
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Dokumentation" \
        --menu "Wählen Sie eine Option:" 15 60 8 \
        "1" "Architektur anzeigen" \
        "2" "Installationsanleitung anzeigen" \
        "3" "Benutzerhandbuch anzeigen" \
        "4" "Entwicklerhandbuch anzeigen" \
        "5" "FAQ anzeigen" \
        "b" "Zurück zum Hauptmenü" \
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        1)
            # Show architecture
            local architecture=""
            
            if [[ -f "${BASE_DIR}/ARCHITECTURE.md" ]]; then
                architecture=$(cat "${BASE_DIR}/ARCHITECTURE.md")
            else
                architecture="Keine Architekturdokumentation gefunden."
            fi
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Architektur" \
                --msgbox "$architecture" 30 100
            
            show_documentation_dialog
            ;;
        2)
            # Show installation guide
            local installation_guide=""
            
            if [[ -f "${BASE_DIR}/docs/installation.md" ]]; then
                installation_guide=$(cat "${BASE_DIR}/docs/installation.md")
            else
                installation_guide="Keine Installationsanleitung gefunden."
            fi
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Installationsanleitung" \
                --msgbox "$installation_guide" 30 100
            
            show_documentation_dialog
            ;;
        3)
            # Show user manual
            local user_manual=""
            
            if [[ -f "${BASE_DIR}/docs/user-manual.md" ]]; then
                user_manual=$(cat "${BASE_DIR}/docs/user-manual.md")
            else
                user_manual="Kein Benutzerhandbuch gefunden."
            fi
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Benutzerhandbuch" \
                --msgbox "$user_manual" 30 100
            
            show_documentation_dialog
            ;;
        4)
            # Show developer manual
            local developer_manual=""
            
            if [[ -f "${BASE_DIR}/docs/developer-manual.md" ]]; then
                developer_manual=$(cat "${BASE_DIR}/docs/developer-manual.md")
            else
                developer_manual="Kein Entwicklerhandbuch gefunden."
            fi
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "Entwicklerhandbuch" \
                --msgbox "$developer_manual" 30 100
            
            show_documentation_dialog
            ;;
        5)
            # Show FAQ
            local faq=""
            
            if [[ -f "${BASE_DIR}/docs/faq.md" ]]; then
                faq=$(cat "${BASE_DIR}/docs/faq.md")
            else
                faq="Keine FAQ gefunden."
            fi
            
            dialog --clear --backtitle "Dev-Server-Workflow" \
                --title "FAQ" \
                --msgbox "$faq" 30 100
            
            show_documentation_dialog
            ;;
        b) show_main_menu_dialog ;;
        *) show_documentation_dialog ;;
    esac
}

# Show about dialog
show_about_dialog() {
    local about=$(
        echo "=== Dev-Server-Workflow ==="
        echo ""
        echo "Version: 1.0.0"
        echo "Autor: EcoSphereNetwork"
        echo ""
        echo "Eine umfassende Lösung für die Verwaltung von MCP-Servern und Workflows."
        echo ""
        echo "GitHub: https://github.com/EcoSphereNetwork/Dev-Server-Workflow"
        echo ""
        echo "Lizenz: MIT"
    )
    
    dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Über" \
        --msgbox "$about" 15 60
    
    show_main_menu_dialog
}

# Show main menu using text-based interface
show_main_menu_text() {
    clear
    echo -e "${BLUE}=== Dev-Server-Workflow ===${NC}"
    echo ""
    echo "1. Status anzeigen"
    echo "2. MCP-Server verwalten"
    echo "3. n8n verwalten"
    echo "4. Logs anzeigen"
    echo "5. Konfiguration"
    echo "6. Monitoring"
    echo "7. Backup und Wiederherstellung"
    echo "8. Installation"
    echo "9. Dokumentation"
    echo "10. Über"
    echo "11. Beenden"
    echo ""
    echo -e "${YELLOW}Wählen Sie eine Option (1-11):${NC} "
    read -r choice
    
    case "$choice" in
        1) show_status_text ;;
        2) show_mcp_servers_text ;;
        3) show_n8n_text ;;
        4) show_logs_text ;;
        5) show_config_text ;;
        6) show_monitoring_text ;;
        7) show_backup_text ;;
        8) show_installation_text ;;
        9) show_documentation_text ;;
        10) show_about_text ;;
        11) clear; echo -e "${GREEN}Auf Wiedersehen!${NC}"; exit 0 ;;
        *) show_main_menu_text ;;
    esac
}

# Text-based menu functions (simplified versions of the dialog-based functions)
show_status_text() {
    clear
    echo -e "${BLUE}=== Systemstatus ===${NC}"
    echo ""
    echo "Datum: $(date)"
    echo "Hostname: $(hostname)"
    echo "Kernel: $(uname -r)"
    echo ""
    echo -e "${BLUE}=== Docker Status ===${NC}"
    echo ""
    echo "Docker Version: $(docker --version)"
    echo "Laufende Container: $(docker ps -q | wc -l)"
    echo ""
    echo -e "${BLUE}=== MCP-Server Status ===${NC}"
    echo ""
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E 'mcp$|mcp-bridge$' || echo "Keine MCP-Server gefunden"
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

# Placeholder for other text-based menu functions
show_mcp_servers_text() {
    clear
    echo -e "${BLUE}=== MCP-Server verwalten ===${NC}"
    echo ""
    echo "Diese Funktion ist in der textbasierten Benutzeroberfläche noch nicht implementiert."
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

show_n8n_text() {
    clear
    echo -e "${BLUE}=== n8n verwalten ===${NC}"
    echo ""
    echo "Diese Funktion ist in der textbasierten Benutzeroberfläche noch nicht implementiert."
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

show_logs_text() {
    clear
    echo -e "${BLUE}=== Logs anzeigen ===${NC}"
    echo ""
    echo "Diese Funktion ist in der textbasierten Benutzeroberfläche noch nicht implementiert."
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

show_config_text() {
    clear
    echo -e "${BLUE}=== Konfiguration ===${NC}"
    echo ""
    echo "Diese Funktion ist in der textbasierten Benutzeroberfläche noch nicht implementiert."
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

show_monitoring_text() {
    clear
    echo -e "${BLUE}=== Monitoring ===${NC}"
    echo ""
    echo "Diese Funktion ist in der textbasierten Benutzeroberfläche noch nicht implementiert."
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

show_backup_text() {
    clear
    echo -e "${BLUE}=== Backup und Wiederherstellung ===${NC}"
    echo ""
    echo "Diese Funktion ist in der textbasierten Benutzeroberfläche noch nicht implementiert."
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

show_installation_text() {
    clear
    echo -e "${BLUE}=== Installation ===${NC}"
    echo ""
    echo "Diese Funktion ist in der textbasierten Benutzeroberfläche noch nicht implementiert."
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

show_documentation_text() {
    clear
    echo -e "${BLUE}=== Dokumentation ===${NC}"
    echo ""
    echo "Diese Funktion ist in der textbasierten Benutzeroberfläche noch nicht implementiert."
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

show_about_text() {
    clear
    echo -e "${BLUE}=== Über ===${NC}"
    echo ""
    echo "Dev-Server-Workflow"
    echo "Version: 1.0.0"
    echo "Autor: EcoSphereNetwork"
    echo ""
    echo "Eine umfassende Lösung für die Verwaltung von MCP-Servern und Workflows."
    echo ""
    echo "GitHub: https://github.com/EcoSphereNetwork/Dev-Server-Workflow"
    echo ""
    echo "Lizenz: MIT"
    echo ""
    echo -e "${YELLOW}Drücken Sie Enter, um fortzufahren...${NC}"
    read -r
    show_main_menu_text
}

# Main function
main() {
    # Check if dialog is installed
    if check_dialog; then
        # Use dialog-based UI
        show_main_menu_dialog
    else
        # Use text-based UI
        show_main_menu_text
    fi
}

# Run main function
main