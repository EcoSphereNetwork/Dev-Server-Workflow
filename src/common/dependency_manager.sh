#!/bin/bash
# Dependency Manager for Dev-Server-Workflow
# This script manages dependencies between components and ensures they are started/stopped in the correct order

# Set strict error handling
set -euo pipefail

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

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

# Dependency graph
# Format: component_name:dependency1,dependency2,...
declare -A DEPENDENCY_GRAPH=(
    ["n8n"]=""
    ["prometheus"]=""
    ["grafana"]="prometheus"
    ["mcp-inspector-ui"]=""
    ["desktop-commander-mcp"]=""
    ["filesystem-mcp"]=""
    ["github-mcp"]=""
    ["memory-mcp"]=""
    ["prompt-mcp"]="n8n"
    ["openhands-mcp"]="n8n"
    ["generator-mcp"]="n8n"
    ["web-ui"]="n8n,mcp-inspector-ui"
)

# Component status
# Format: component_name:status (running, stopped, unknown)
declare -A COMPONENT_STATUS

# Component start commands
# Format: component_name:command
declare -A START_COMMANDS=(
    ["n8n"]="docker-compose -f ${BASE_DIR}/docker-compose.yml up -d n8n"
    ["prometheus"]="docker-compose -f ${BASE_DIR}/docker-compose.yml up -d prometheus"
    ["grafana"]="docker-compose -f ${BASE_DIR}/docker-compose.yml up -d grafana"
    ["mcp-inspector-ui"]="docker-compose -f ${BASE_DIR}/docker-compose.yml up -d mcp-inspector-ui"
    ["desktop-commander-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml up -d desktop-commander-mcp"
    ["filesystem-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml up -d filesystem-mcp"
    ["github-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml up -d github-mcp"
    ["memory-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml up -d memory-mcp"
    ["prompt-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml up -d prompt-mcp"
    ["openhands-mcp"]="${BASE_DIR}/start-mcp-servers.sh --openhands"
    ["generator-mcp"]="${BASE_DIR}/start-mcp-servers.sh --generator"
    ["web-ui"]="${BASE_DIR}/start-web-ui.sh"
)

# Component stop commands
# Format: component_name:command
declare -A STOP_COMMANDS=(
    ["n8n"]="docker-compose -f ${BASE_DIR}/docker-compose.yml stop n8n"
    ["prometheus"]="docker-compose -f ${BASE_DIR}/docker-compose.yml stop prometheus"
    ["grafana"]="docker-compose -f ${BASE_DIR}/docker-compose.yml stop grafana"
    ["mcp-inspector-ui"]="docker-compose -f ${BASE_DIR}/docker-compose.yml stop mcp-inspector-ui"
    ["desktop-commander-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml stop desktop-commander-mcp"
    ["filesystem-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml stop filesystem-mcp"
    ["github-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml stop github-mcp"
    ["memory-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml stop memory-mcp"
    ["prompt-mcp"]="docker-compose -f ${BASE_DIR}/docker-mcp-ecosystem/docker-compose.yml stop prompt-mcp"
    ["openhands-mcp"]="${BASE_DIR}/stop-mcp-servers.sh --openhands"
    ["generator-mcp"]="${BASE_DIR}/stop-mcp-servers.sh --generator"
    ["web-ui"]="${BASE_DIR}/stop-web-ui.sh"
)

# Component health check commands
# Format: component_name:command
declare -A HEALTH_CHECK_COMMANDS=(
    ["n8n"]="curl -s http://localhost:5678/healthz"
    ["prometheus"]="curl -s http://localhost:9090/-/healthy"
    ["grafana"]="curl -s http://localhost:3000/api/health"
    ["mcp-inspector-ui"]="docker ps | grep -q mcp-inspector-ui"
    ["desktop-commander-mcp"]="curl -s http://localhost:3333/health"
    ["filesystem-mcp"]="curl -s http://localhost:3334/health"
    ["github-mcp"]="curl -s http://localhost:3335/health"
    ["memory-mcp"]="curl -s http://localhost:3336/health"
    ["prompt-mcp"]="curl -s http://localhost:3337/health"
    ["openhands-mcp"]="curl -s http://localhost:3006/health"
    ["generator-mcp"]="curl -s http://localhost:3007/health"
    ["web-ui"]="curl -s http://localhost:8080"
)

# Function to get component status
get_component_status() {
    local component="$1"
    
    # Check if component exists
    if [[ -z "${START_COMMANDS[$component]}" ]]; then
        echo "unknown"
        return 1
    fi
    
    # Check if component is running
    if [[ -n "${HEALTH_CHECK_COMMANDS[$component]}" ]]; then
        if eval "${HEALTH_CHECK_COMMANDS[$component]}" &> /dev/null; then
            echo "running"
            return 0
        fi
    fi
    
    # Check if container is running
    if docker ps --format "{{.Names}}" | grep -q "$component"; then
        echo "running"
        return 0
    fi
    
    # Check if container exists but is stopped
    if docker ps -a --format "{{.Names}}" | grep -q "$component"; then
        echo "stopped"
        return 0
    fi
    
    echo "unknown"
    return 0
}

# Function to update all component statuses
update_component_statuses() {
    for component in "${!DEPENDENCY_GRAPH[@]}"; do
        COMPONENT_STATUS[$component]=$(get_component_status "$component")
    done
}

# Function to get dependencies for a component
get_dependencies() {
    local component="$1"
    
    # Check if component exists
    if [[ -z "${DEPENDENCY_GRAPH[$component]}" ]]; then
        echo ""
        return 1
    fi
    
    echo "${DEPENDENCY_GRAPH[$component]}"
    return 0
}

# Function to check if all dependencies are running
check_dependencies_running() {
    local component="$1"
    local dependencies=$(get_dependencies "$component")
    
    # If no dependencies, return success
    if [[ -z "$dependencies" ]]; then
        return 0
    fi
    
    # Check each dependency
    IFS=',' read -ra DEPS <<< "$dependencies"
    for dep in "${DEPS[@]}"; do
        if [[ "${COMPONENT_STATUS[$dep]}" != "running" ]]; then
            return 1
        fi
    done
    
    return 0
}

# Function to get components that depend on a given component
get_dependents() {
    local component="$1"
    local dependents=""
    
    for comp in "${!DEPENDENCY_GRAPH[@]}"; do
        local deps="${DEPENDENCY_GRAPH[$comp]}"
        if [[ "$deps" == *"$component"* ]]; then
            if [[ -z "$dependents" ]]; then
                dependents="$comp"
            else
                dependents="$dependents,$comp"
            fi
        fi
    done
    
    echo "$dependents"
    return 0
}

# Function to check if any dependents are running
check_dependents_running() {
    local component="$1"
    local dependents=$(get_dependents "$component")
    
    # If no dependents, return success
    if [[ -z "$dependents" ]]; then
        return 0
    fi
    
    # Check each dependent
    IFS=',' read -ra DEPS <<< "$dependents"
    for dep in "${DEPS[@]}"; do
        if [[ "${COMPONENT_STATUS[$dep]}" == "running" ]]; then
            return 0
        fi
    done
    
    return 1
}

# Function to start a component and its dependencies
start_component() {
    local component="$1"
    local force="${2:-false}"
    
    # Check if component exists
    if [[ -z "${START_COMMANDS[$component]}" ]]; then
        echo -e "${RED}Component $component does not exist${NC}"
        return 1
    fi
    
    # Check if component is already running
    if [[ "${COMPONENT_STATUS[$component]}" == "running" && "$force" != "true" ]]; then
        echo -e "${GREEN}Component $component is already running${NC}"
        return 0
    fi
    
    # Start dependencies first
    local dependencies=$(get_dependencies "$component")
    if [[ -n "$dependencies" ]]; then
        echo -e "${BLUE}Starting dependencies for $component: $dependencies${NC}"
        
        IFS=',' read -ra DEPS <<< "$dependencies"
        for dep in "${DEPS[@]}"; do
            start_component "$dep" "$force"
        done
    fi
    
    # Start the component
    echo -e "${BLUE}Starting component $component...${NC}"
    eval "${START_COMMANDS[$component]}"
    
    # Update component status
    COMPONENT_STATUS[$component]=$(get_component_status "$component")
    
    # Check if component started successfully
    if [[ "${COMPONENT_STATUS[$component]}" == "running" ]]; then
        echo -e "${GREEN}Component $component started successfully${NC}"
    else
        echo -e "${RED}Failed to start component $component${NC}"
        return 1
    fi
    
    return 0
}

# Function to stop a component and its dependents
stop_component() {
    local component="$1"
    local force="${2:-false}"
    
    # Check if component exists
    if [[ -z "${STOP_COMMANDS[$component]}" ]]; then
        echo -e "${RED}Component $component does not exist${NC}"
        return 1
    fi
    
    # Check if component is already stopped
    if [[ "${COMPONENT_STATUS[$component]}" == "stopped" && "$force" != "true" ]]; then
        echo -e "${GREEN}Component $component is already stopped${NC}"
        return 0
    fi
    
    # Check if any dependents are running
    local dependents=$(get_dependents "$component")
    if [[ -n "$dependents" && "$force" != "true" ]]; then
        echo -e "${YELLOW}Components depend on $component: $dependents${NC}"
        
        # Ask for confirmation
        read -p "Do you want to stop these components as well? (y/n) " -n 1 -r
        echo
        
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo -e "${RED}Aborting${NC}"
            return 1
        fi
        
        # Stop dependents first
        IFS=',' read -ra DEPS <<< "$dependents"
        for dep in "${DEPS[@]}"; do
            stop_component "$dep" "$force"
        done
    fi
    
    # Stop the component
    echo -e "${BLUE}Stopping component $component...${NC}"
    eval "${STOP_COMMANDS[$component]}"
    
    # Update component status
    COMPONENT_STATUS[$component]=$(get_component_status "$component")
    
    # Check if component stopped successfully
    if [[ "${COMPONENT_STATUS[$component]}" != "running" ]]; then
        echo -e "${GREEN}Component $component stopped successfully${NC}"
    else
        echo -e "${RED}Failed to stop component $component${NC}"
        return 1
    fi
    
    return 0
}

# Function to restart a component
restart_component() {
    local component="$1"
    local force="${2:-false}"
    
    # Check if component exists
    if [[ -z "${START_COMMANDS[$component]}" || -z "${STOP_COMMANDS[$component]}" ]]; then
        echo -e "${RED}Component $component does not exist${NC}"
        return 1
    fi
    
    # Stop the component
    stop_component "$component" "$force"
    
    # Start the component
    start_component "$component" "$force"
    
    return 0
}

# Function to list all components and their status
list_components() {
    echo -e "${BLUE}Components and their status:${NC}"
    echo "-----------------------------"
    
    # Update component statuses
    update_component_statuses
    
    # Print component status
    for component in "${!DEPENDENCY_GRAPH[@]}"; do
        local status="${COMPONENT_STATUS[$component]}"
        local dependencies="${DEPENDENCY_GRAPH[$component]}"
        
        case "$status" in
            "running")
                echo -e "${GREEN}$component${NC}: $status"
                ;;
            "stopped")
                echo -e "${YELLOW}$component${NC}: $status"
                ;;
            *)
                echo -e "${RED}$component${NC}: $status"
                ;;
        esac
        
        if [[ -n "$dependencies" ]]; then
            echo "  Dependencies: $dependencies"
        fi
        
        local dependents=$(get_dependents "$component")
        if [[ -n "$dependents" ]]; then
            echo "  Dependents: $dependents"
        fi
        
        echo
    done
}

# Function to start all components
start_all_components() {
    local force="${1:-false}"
    
    echo -e "${BLUE}Starting all components...${NC}"
    
    # Start components without dependencies first
    for component in "${!DEPENDENCY_GRAPH[@]}"; do
        if [[ -z "${DEPENDENCY_GRAPH[$component]}" ]]; then
            start_component "$component" "$force"
        fi
    done
    
    # Start components with dependencies
    for component in "${!DEPENDENCY_GRAPH[@]}"; do
        if [[ -n "${DEPENDENCY_GRAPH[$component]}" ]]; then
            start_component "$component" "$force"
        fi
    done
    
    echo -e "${GREEN}All components started${NC}"
}

# Function to stop all components
stop_all_components() {
    local force="${1:-false}"
    
    echo -e "${BLUE}Stopping all components...${NC}"
    
    # Stop components with dependents first (in reverse order)
    for component in $(echo "${!DEPENDENCY_GRAPH[@]}" | tr ' ' '\n' | sort -r); do
        local dependents=$(get_dependents "$component")
        if [[ -n "$dependents" ]]; then
            stop_component "$component" "$force"
        fi
    done
    
    # Stop components without dependents
    for component in $(echo "${!DEPENDENCY_GRAPH[@]}" | tr ' ' '\n' | sort -r); do
        local dependents=$(get_dependents "$component")
        if [[ -z "$dependents" ]]; then
            stop_component "$component" "$force"
        fi
    done
    
    echo -e "${GREEN}All components stopped${NC}"
}

# Function to show component details
show_component_details() {
    local component="$1"
    
    # Check if component exists
    if [[ -z "${START_COMMANDS[$component]}" ]]; then
        echo -e "${RED}Component $component does not exist${NC}"
        return 1
    fi
    
    # Update component status
    COMPONENT_STATUS[$component]=$(get_component_status "$component")
    
    # Print component details
    echo -e "${BLUE}Component: $component${NC}"
    echo "Status: ${COMPONENT_STATUS[$component]}"
    echo "Dependencies: ${DEPENDENCY_GRAPH[$component]}"
    
    local dependents=$(get_dependents "$component")
    echo "Dependents: $dependents"
    
    echo "Start command: ${START_COMMANDS[$component]}"
    echo "Stop command: ${STOP_COMMANDS[$component]}"
    echo "Health check command: ${HEALTH_CHECK_COMMANDS[$component]}"
    
    return 0
}

# Main function
main() {
    # Update component statuses
    update_component_statuses
    
    # Parse command line arguments
    local command="$1"
    shift
    
    case "$command" in
        "list")
            list_components
            ;;
        "start")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}No component specified${NC}"
                echo "Usage: $0 start <component> [force]"
                return 1
            fi
            
            start_component "$1" "${2:-false}"
            ;;
        "stop")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}No component specified${NC}"
                echo "Usage: $0 stop <component> [force]"
                return 1
            fi
            
            stop_component "$1" "${2:-false}"
            ;;
        "restart")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}No component specified${NC}"
                echo "Usage: $0 restart <component> [force]"
                return 1
            fi
            
            restart_component "$1" "${2:-false}"
            ;;
        "start-all")
            start_all_components "${1:-false}"
            ;;
        "stop-all")
            stop_all_components "${1:-false}"
            ;;
        "status")
            if [[ $# -lt 1 ]]; then
                list_components
            else
                show_component_details "$1"
            fi
            ;;
        "dependencies")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}No component specified${NC}"
                echo "Usage: $0 dependencies <component>"
                return 1
            fi
            
            echo "Dependencies for $1: $(get_dependencies "$1")"
            ;;
        "dependents")
            if [[ $# -lt 1 ]]; then
                echo -e "${RED}No component specified${NC}"
                echo "Usage: $0 dependents <component>"
                return 1
            fi
            
            echo "Dependents for $1: $(get_dependents "$1")"
            ;;
        *)
            echo -e "${RED}Unknown command: $command${NC}"
            echo "Usage: $0 <command> [arguments]"
            echo "Commands:"
            echo "  list                  List all components and their status"
            echo "  start <component>     Start a component and its dependencies"
            echo "  stop <component>      Stop a component and its dependents"
            echo "  restart <component>   Restart a component"
            echo "  start-all             Start all components"
            echo "  stop-all              Stop all components"
            echo "  status [component]    Show status of all components or a specific component"
            echo "  dependencies <comp>   Show dependencies for a component"
            echo "  dependents <comp>     Show dependents for a component"
            return 1
            ;;
    esac
    
    return 0
}

# If script is executed directly (not sourced), run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <command> [arguments]"
        echo "Run '$0 help' for a list of available commands"
        exit 1
    fi
    
    main "$@"
fi