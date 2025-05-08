#!/bin/bash
# Common Library for MCP Server Management
# This script provides shared functionality for docker-mcp-ecosystem and docker-mcp-servers

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

# Function to check Docker installation
check_docker() {
    set_operation "check_docker"
    
    log_message "INFO" "Checking Docker installation..."
    
    # Check if Docker is installed
    if ! command -v docker &> /dev/null; then
        log_message "ERROR" "Docker is not installed"
        return ${ERROR_CODES["DEPENDENCY_ERROR"]}
    fi
    
    # Check if Docker is running
    if ! docker info &> /dev/null; then
        log_message "ERROR" "Docker is not running"
        return ${ERROR_CODES["DEPENDENCY_ERROR"]}
    fi
    
    # Check if Docker Compose is installed
    if ! command -v docker-compose &> /dev/null; then
        log_message "ERROR" "Docker Compose is not installed"
        return ${ERROR_CODES["DEPENDENCY_ERROR"]}
    fi
    
    log_message "INFO" "Docker installation is valid"
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to create Docker network
create_docker_network() {
    local network_name="$1"
    
    set_operation "create_docker_network"
    
    log_message "INFO" "Creating Docker network: $network_name"
    
    # Check if network already exists
    if docker network ls --format '{{.Name}}' | grep -q "^${network_name}$"; then
        log_message "INFO" "Network $network_name already exists"
        return ${ERROR_CODES["SUCCESS"]}
    fi
    
    # Create network
    docker network create "$network_name"
    
    log_message "INFO" "Network $network_name created successfully"
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to start MCP server
start_mcp_server() {
    local server_name="$1"
    local compose_file="$2"
    local env_file="${3:-.env}"
    
    set_operation "start_container"
    set_container "$server_name"
    
    log_message "INFO" "Starting MCP server: $server_name"
    
    # Check if server is already running
    if docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "INFO" "Server $server_name is already running"
        return ${ERROR_CODES["SUCCESS"]}
    fi
    
    # Start server
    docker-compose -f "$compose_file" --env-file "$env_file" up -d "$server_name"
    
    # Wait for server to be ready
    local max_attempts=30
    local attempt=0
    local server_ready=false
    
    log_message "INFO" "Waiting for server $server_name to be ready..."
    
    while [[ $attempt -lt $max_attempts ]]; do
        if docker logs "$server_name" 2>&1 | grep -q "Server started"; then
            server_ready=true
            break
        fi
        
        attempt=$((attempt + 1))
        sleep 1
    done
    
    if [[ "$server_ready" == "true" ]]; then
        log_message "INFO" "Server $server_name started successfully"
        return ${ERROR_CODES["SUCCESS"]}
    else
        log_message "ERROR" "Server $server_name failed to start within timeout"
        return ${ERROR_CODES["TIMEOUT"]}
    fi
}

# Function to stop MCP server
stop_mcp_server() {
    local server_name="$1"
    local compose_file="$2"
    local env_file="${3:-.env}"
    
    set_operation "stop_container"
    set_container "$server_name"
    
    log_message "INFO" "Stopping MCP server: $server_name"
    
    # Check if server is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "INFO" "Server $server_name is not running"
        return ${ERROR_CODES["SUCCESS"]}
    fi
    
    # Stop server
    docker-compose -f "$compose_file" --env-file "$env_file" stop "$server_name"
    
    log_message "INFO" "Server $server_name stopped successfully"
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to get MCP server status
get_mcp_server_status() {
    local server_name="$1"
    
    set_operation "get_server_status"
    set_container "$server_name"
    
    log_message "INFO" "Getting status of MCP server: $server_name"
    
    # Check if server is running
    if docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        echo "running"
    elif docker ps -a --format '{{.Names}}' | grep -q "^${server_name}$"; then
        echo "stopped"
    else
        echo "not_found"
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to get MCP server logs
get_mcp_server_logs() {
    local server_name="$1"
    local lines="${2:-100}"
    
    set_operation "get_server_logs"
    set_container "$server_name"
    
    log_message "INFO" "Getting logs of MCP server: $server_name (last $lines lines)"
    
    # Check if server exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "ERROR" "Server $server_name not found"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    # Get logs
    docker logs --tail "$lines" "$server_name"
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to execute command in MCP server
exec_in_mcp_server() {
    local server_name="$1"
    local command="${@:2}"
    
    set_operation "exec_in_server"
    set_container "$server_name"
    
    log_message "INFO" "Executing command in MCP server: $server_name"
    
    # Check if server is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "ERROR" "Server $server_name is not running"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    # Execute command
    docker exec -it "$server_name" $command
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to check MCP server health
check_mcp_server_health() {
    local server_name="$1"
    local port="${2:-3333}"
    
    set_operation "check_server_health"
    set_container "$server_name"
    
    log_message "INFO" "Checking health of MCP server: $server_name"
    
    # Check if server is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "ERROR" "Server $server_name is not running"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    # Get container IP
    local container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$server_name")
    
    # Check if server is responding
    if ! curl -s "http://${container_ip}:${port}/health" | grep -q "ok"; then
        log_message "ERROR" "Server $server_name is not healthy"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    log_message "INFO" "Server $server_name is healthy"
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to list all MCP servers
list_mcp_servers() {
    local compose_file="$1"
    
    set_operation "list_servers"
    
    log_message "INFO" "Listing all MCP servers"
    
    # List all services in compose file that end with -mcp
    docker-compose -f "$compose_file" config --services | grep -E 'mcp$|mcp-bridge$'
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to list all MCP server tools
list_mcp_server_tools() {
    local server_name="$1"
    local port="${2:-3333}"
    
    set_operation "list_server_tools"
    set_container "$server_name"
    
    log_message "INFO" "Listing tools of MCP server: $server_name"
    
    # Check if server is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "ERROR" "Server $server_name is not running"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    # Get container IP
    local container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$server_name")
    
    # Get tools
    curl -s "http://${container_ip}:${port}/tools/list" | jq .
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to call MCP server tool
call_mcp_server_tool() {
    local server_name="$1"
    local tool_name="$2"
    local args="${3:-{}}"
    local port="${4:-3333}"
    
    set_operation "call_server_tool"
    set_container "$server_name"
    
    log_message "INFO" "Calling tool $tool_name of MCP server: $server_name"
    
    # Check if server is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "ERROR" "Server $server_name is not running"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    # Get container IP
    local container_ip=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' "$server_name")
    
    # Call tool
    curl -s -X POST "http://${container_ip}:${port}/tools/call" \
        -H "Content-Type: application/json" \
        -d "{\"name\":\"${tool_name}\",\"args\":${args}}" | jq .
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to backup MCP server data
backup_mcp_server() {
    local server_name="$1"
    local backup_dir="${2:-${BASE_DIR}/backups}"
    
    set_operation "backup_server"
    set_container "$server_name"
    
    log_message "INFO" "Backing up MCP server: $server_name"
    
    # Create backup directory if it doesn't exist
    mkdir -p "$backup_dir"
    
    # Check if server exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "ERROR" "Server $server_name not found"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    # Create backup filename with timestamp
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local backup_file="${backup_dir}/${server_name}_${timestamp}.tar"
    
    # Export container
    docker export "$server_name" > "$backup_file"
    
    log_message "INFO" "Server $server_name backed up to $backup_file"
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to restore MCP server from backup
restore_mcp_server() {
    local server_name="$1"
    local backup_file="$2"
    
    set_operation "restore_server"
    set_container "$server_name"
    
    log_message "INFO" "Restoring MCP server: $server_name from $backup_file"
    
    # Check if backup file exists
    if [[ ! -f "$backup_file" ]]; then
        log_message "ERROR" "Backup file $backup_file not found"
        return ${ERROR_CODES["FILE_NOT_FOUND"]}
    fi
    
    # Stop server if it's running
    if docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "INFO" "Stopping server $server_name before restore"
        docker stop "$server_name"
    fi
    
    # Remove existing container if it exists
    if docker ps -a --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "INFO" "Removing existing container $server_name"
        docker rm "$server_name"
    fi
    
    # Import backup
    cat "$backup_file" | docker import - "${server_name}:restored"
    
    log_message "INFO" "Server $server_name restored from $backup_file"
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to update MCP server configuration
update_mcp_server_config() {
    local server_name="$1"
    local config_key="$2"
    local config_value="$3"
    local config_file="${4:-/app/config.json}"
    
    set_operation "update_config"
    set_container "$server_name"
    
    log_message "INFO" "Updating configuration of MCP server: $server_name"
    
    # Check if server is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "ERROR" "Server $server_name is not running"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    # Update configuration
    docker exec "$server_name" bash -c "echo \$(jq '.${config_key} = \"${config_value}\"' ${config_file}) > ${config_file}"
    
    log_message "INFO" "Configuration of server $server_name updated successfully"
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to monitor MCP server resources
monitor_mcp_server() {
    local server_name="$1"
    local interval="${2:-5}"
    local count="${3:-10}"
    
    set_operation "monitor_server"
    set_container "$server_name"
    
    log_message "INFO" "Monitoring MCP server: $server_name (interval: ${interval}s, count: $count)"
    
    # Check if server is running
    if ! docker ps --format '{{.Names}}' | grep -q "^${server_name}$"; then
        log_message "ERROR" "Server $server_name is not running"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    # Monitor resources
    for ((i=1; i<=count; i++)); do
        echo "=== Monitoring $server_name (${i}/${count}) ==="
        docker stats --no-stream "$server_name"
        
        if [[ $i -lt $count ]]; then
            sleep "$interval"
        fi
    done
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to check dependencies
check_dependencies() {
    log_message "INFO" "Checking dependencies..."
    
    # Check required commands
    check_command "docker" "Install Docker: https://docs.docker.com/get-docker/"
    check_command "docker-compose" "Install Docker Compose: https://docs.docker.com/compose/install/"
    check_command "curl" "Install curl: apt-get install -y curl"
    check_command "jq" "Install jq: apt-get install -y jq"
    
    log_message "INFO" "All dependencies are installed"
    return ${ERROR_CODES["SUCCESS"]}
}

# Main function to handle command-line arguments
main() {
    local command="$1"
    shift
    
    # Check dependencies
    check_dependencies
    
    case "$command" in
        "check-docker")
            check_docker
            ;;
        "create-network")
            if [[ $# -lt 1 ]]; then
                log_message "ERROR" "Usage: $0 create-network <network_name>"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            create_docker_network "$1"
            ;;
        "start-server")
            if [[ $# -lt 2 ]]; then
                log_message "ERROR" "Usage: $0 start-server <server_name> <compose_file> [env_file]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            start_mcp_server "$1" "$2" "${3:-.env}"
            ;;
        "stop-server")
            if [[ $# -lt 2 ]]; then
                log_message "ERROR" "Usage: $0 stop-server <server_name> <compose_file> [env_file]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            stop_mcp_server "$1" "$2" "${3:-.env}"
            ;;
        "status")
            if [[ $# -lt 1 ]]; then
                log_message "ERROR" "Usage: $0 status <server_name>"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            get_mcp_server_status "$1"
            ;;
        "logs")
            if [[ $# -lt 1 ]]; then
                log_message "ERROR" "Usage: $0 logs <server_name> [lines]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            get_mcp_server_logs "$1" "${2:-100}"
            ;;
        "exec")
            if [[ $# -lt 2 ]]; then
                log_message "ERROR" "Usage: $0 exec <server_name> <command> [args...]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            exec_in_mcp_server "$@"
            ;;
        "health")
            if [[ $# -lt 1 ]]; then
                log_message "ERROR" "Usage: $0 health <server_name> [port]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            check_mcp_server_health "$1" "${2:-3333}"
            ;;
        "list-servers")
            if [[ $# -lt 1 ]]; then
                log_message "ERROR" "Usage: $0 list-servers <compose_file>"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            list_mcp_servers "$1"
            ;;
        "list-tools")
            if [[ $# -lt 1 ]]; then
                log_message "ERROR" "Usage: $0 list-tools <server_name> [port]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            list_mcp_server_tools "$1" "${2:-3333}"
            ;;
        "call-tool")
            if [[ $# -lt 3 ]]; then
                log_message "ERROR" "Usage: $0 call-tool <server_name> <tool_name> <args_json> [port]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            call_mcp_server_tool "$1" "$2" "$3" "${4:-3333}"
            ;;
        "backup")
            if [[ $# -lt 1 ]]; then
                log_message "ERROR" "Usage: $0 backup <server_name> [backup_dir]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            backup_mcp_server "$1" "${2:-${BASE_DIR}/backups}"
            ;;
        "restore")
            if [[ $# -lt 2 ]]; then
                log_message "ERROR" "Usage: $0 restore <server_name> <backup_file>"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            restore_mcp_server "$1" "$2"
            ;;
        "update-config")
            if [[ $# -lt 3 ]]; then
                log_message "ERROR" "Usage: $0 update-config <server_name> <config_key> <config_value> [config_file]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            update_mcp_server_config "$1" "$2" "$3" "${4:-/app/config.json}"
            ;;
        "monitor")
            if [[ $# -lt 1 ]]; then
                log_message "ERROR" "Usage: $0 monitor <server_name> [interval] [count]"
                return ${ERROR_CODES["INVALID_ARGUMENT"]}
            fi
            
            monitor_mcp_server "$1" "${2:-5}" "${3:-10}"
            ;;
        *)
            log_message "ERROR" "Unknown command: $command"
            echo "Available commands:"
            echo "  check-docker                     Check Docker installation"
            echo "  create-network <network>         Create Docker network"
            echo "  start-server <server> <compose>  Start MCP server"
            echo "  stop-server <server> <compose>   Stop MCP server"
            echo "  status <server>                  Get MCP server status"
            echo "  logs <server> [lines]            Get MCP server logs"
            echo "  exec <server> <command>          Execute command in MCP server"
            echo "  health <server> [port]           Check MCP server health"
            echo "  list-servers <compose>           List all MCP servers"
            echo "  list-tools <server> [port]       List MCP server tools"
            echo "  call-tool <server> <tool> <args> Call MCP server tool"
            echo "  backup <server> [dir]            Backup MCP server"
            echo "  restore <server> <file>          Restore MCP server from backup"
            echo "  update-config <server> <key> <val> Update MCP server configuration"
            echo "  monitor <server> [interval] [count] Monitor MCP server resources"
            return ${ERROR_CODES["INVALID_ARGUMENT"]}
            ;;
    esac
    
    return ${ERROR_CODES["SUCCESS"]}
}

# If script is executed directly (not sourced), run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        echo "Usage: $0 <command> [args...]"
        echo "Run '$0 help' for a list of available commands"
        exit 1
    fi
    
    main "$@"
fi