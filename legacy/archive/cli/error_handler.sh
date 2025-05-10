#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

# Error Handler for Dev-Server-Workflow
# This script provides consistent error handling across all scripts

# Set strict error handling
set -euo pipefail

# Colors for output
RED='\033[0;31m'
YELLOW='\033[0;33m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global variables for error handling
CURRENT_OPERATION=""
CURRENT_CONTAINER=""
CURRENT_COMPONENT=""
ERROR_LOG_FILE="/workspace/Dev-Server-Workflow/logs/error.log"

# Create logs directory if it doesn't exist
mkdir -p "$(dirname "$ERROR_LOG_FILE")"

# Error codes
declare -A ERROR_CODES=(
    ["SUCCESS"]=0
    ["GENERAL_ERROR"]=1
    ["INVALID_ARGUMENT"]=2
    ["FILE_NOT_FOUND"]=3
    ["PERMISSION_DENIED"]=4
    ["COMMAND_NOT_FOUND"]=5
    ["NETWORK_ERROR"]=6
    ["TIMEOUT"]=7
    ["CONTAINER_ERROR"]=10
    ["DOCKER_ERROR"]=11
    ["CONFIG_ERROR"]=20
    ["DEPENDENCY_ERROR"]=30
    ["VALIDATION_ERROR"]=40
    ["UNKNOWN_ERROR"]=99
)

# Main error handling function
handle_error() {
    local exit_code=$1
    local line_number=$2
    local command="$3"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")

    # Log the error
    log_info "${RED}[ERROR] Command '$command' in line $line_number failed with code $exit_code${NC}"
    log_info "[$timestamp] ERROR: Command '$command' in line $line_number failed with code $exit_code" >> "$ERROR_LOG_FILE"

    # Perform rollback actions based on the current operation
    case "$CURRENT_OPERATION" in
        "start_container")
            log_info "${YELLOW}[ROLLBACK] Stopping failed container: $CURRENT_CONTAINER${NC}"
            log_info "[$timestamp] ROLLBACK: Stopping failed container: $CURRENT_CONTAINER" >> "$ERROR_LOG_FILE"
            docker stop "$CURRENT_CONTAINER" 2>/dev/null || true
            ;;
        "install_component")
            log_info "${YELLOW}[ROLLBACK] Removing failed installation: $CURRENT_COMPONENT${NC}"
            log_info "[$timestamp] ROLLBACK: Removing failed installation: $CURRENT_COMPONENT" >> "$ERROR_LOG_FILE"
            # Add specific rollback logic here
            ;;
        "update_config")
            log_info "${YELLOW}[ROLLBACK] Restoring previous configuration${NC}"
            log_info "[$timestamp] ROLLBACK: Restoring previous configuration" >> "$ERROR_LOG_FILE"
            # Add specific rollback logic here
            ;;
        "network_operation")
            log_info "${YELLOW}[ROLLBACK] Cleaning up network resources${NC}"
            log_info "[$timestamp] ROLLBACK: Cleaning up network resources" >> "$ERROR_LOG_FILE"
            # Add specific rollback logic here
            ;;
        *)
            log_info "${YELLOW}[INFO] No specific rollback action defined for operation: $CURRENT_OPERATION${NC}"
            log_info "[$timestamp] INFO: No specific rollback action defined for operation: $CURRENT_OPERATION" >> "$ERROR_LOG_FILE"
            ;;
    esac

    return $exit_code
}

# Function to set the current operation
set_operation() {
    CURRENT_OPERATION="$1"
    log_info "${BLUE}[INFO] Starting operation: $CURRENT_OPERATION${NC}"
}

# Function to set the current container
set_container() {
    CURRENT_CONTAINER="$1"
    log_info "${BLUE}[INFO] Working with container: $CURRENT_CONTAINER${NC}"
}

# Function to set the current component
set_component() {
    CURRENT_COMPONENT="$1"
    log_info "${BLUE}[INFO] Working with component: $CURRENT_COMPONENT${NC}"
}

# Function to check command existence
check_command() {
    local cmd="$1"
    local install_hint="${2:-}"
    
    if ! command -v "$cmd" &> /dev/null; then
        log_info "${RED}[ERROR] Required command not found: $cmd${NC}"
        if [[ -n "$install_hint" ]]; then
            log_info "${YELLOW}[HINT] $install_hint${NC}"
        fi
        return ${ERROR_CODES["COMMAND_NOT_FOUND"]}
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to check file existence
check_file() {
    local file="$1"
    local create="${2:-false}"
    
    if [[ ! -f "$file" ]]; then
        if [[ "$create" == "true" ]]; then
            log_info "${YELLOW}[WARN] File not found, creating: $file${NC}"
            touch "$file" || return ${ERROR_CODES["PERMISSION_DENIED"]}
        else
            log_info "${RED}[ERROR] Required file not found: $file${NC}"
            return ${ERROR_CODES["FILE_NOT_FOUND"]}
        fi
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to check directory existence
check_directory() {
    local dir="$1"
    local create="${2:-false}"
    
    if [[ ! -d "$dir" ]]; then
        if [[ "$create" == "true" ]]; then
            log_info "${YELLOW}[WARN] Directory not found, creating: $dir${NC}"
            mkdir -p "$dir" || return ${ERROR_CODES["PERMISSION_DENIED"]}
        else
            log_info "${RED}[ERROR] Required directory not found: $dir${NC}"
            return ${ERROR_CODES["FILE_NOT_FOUND"]}
        fi
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to validate input
validate_input() {
    local input="$1"
    local pattern="$2"
    local error_message="${3:-Invalid input format}"
    
    if [[ ! "$input" =~ $pattern ]]; then
        log_info "${RED}[ERROR] $error_message${NC}"
        return ${ERROR_CODES["VALIDATION_ERROR"]}
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to execute a command with timeout
execute_with_timeout() {
    local timeout="$1"
    local cmd="${@:2}"
    
    # Check if timeout command exists
    if ! command -v timeout &> /dev/null; then
        log_info "${YELLOW}[WARN] 'timeout' command not found, executing without timeout${NC}"
        $cmd
        return $?
    fi
    
    timeout "$timeout" $cmd
    local exit_code=$?
    
    if [[ $exit_code -eq 124 ]]; then
        log_info "${RED}[ERROR] Command timed out after $timeout seconds: $cmd${NC}"
        return ${ERROR_CODES["TIMEOUT"]}
    fi
    
    return $exit_code
}

# Function to check if a container is running
check_container_running() {
    local container="$1"
    
    if ! docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        log_info "${RED}[ERROR] Container not running: $container${NC}"
        return ${ERROR_CODES["CONTAINER_ERROR"]}
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to check network connectivity
check_network() {
    local host="$1"
    local port="${2:-80}"
    local timeout="${3:-5}"
    
    # Check if nc command exists
    if ! command -v nc &> /dev/null; then
        log_info "${YELLOW}[WARN] 'nc' command not found, skipping network check${NC}"
        return ${ERROR_CODES["SUCCESS"]}
    fi
    
    if ! nc -z -w "$timeout" "$host" "$port"; then
        log_info "${RED}[ERROR] Network connection failed: $host:$port${NC}"
        return ${ERROR_CODES["NETWORK_ERROR"]}
    fi
    
    return ${ERROR_CODES["SUCCESS"]}
}

# Function to log a message
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date +"%Y-%m-%d %H:%M:%S")
    
    case "$level" in
        "INFO")
            log_info "${GREEN}[INFO] $message${NC}"
            ;;
        "WARN")
            log_info "${YELLOW}[WARN] $message${NC}"
            ;;
        "ERROR")
            log_info "${RED}[ERROR] $message${NC}"
            ;;
        "DEBUG")
            log_info "${BLUE}[DEBUG] $message${NC}"
            ;;
        *)
            log_info "[${level}] $message"
            ;;
    esac
    
    log_info "[$timestamp] $level: $message" >> "$ERROR_LOG_FILE"
}

# Function to get error code name from code
get_error_name() {
    local code="$1"
    
    for name in "${!ERROR_CODES[@]}"; do
        if [[ "${ERROR_CODES[$name]}" -eq "$code" ]]; then
            log_info "$name"
            return 0
        fi
    done
    
    log_info "UNKNOWN_ERROR"
    return 0
}

# Function to get error code from name
get_error_code() {
    local name="$1"
    
    if [[ -n "${ERROR_CODES[$name]}" ]]; then
        log_info "${ERROR_CODES[$name]}"
        return 0
    fi
    
    log_info "${ERROR_CODES["UNKNOWN_ERROR"]}"
    return 0
}

# Set up error trap if script is not sourced
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR
    
    # Show usage if no arguments provided
    if [[ $# -eq 0 ]]; then
        log_info "Usage: $0 <function> [arguments...]"
        echo ""
        log_info "Available functions:"
        log_info "  set_operation <operation>            Set the current operation"
        log_info "  set_container <container>            Set the current container"
        log_info "  set_component <component>            Set the current component"
        log_info "  check_command <command> [hint]       Check if a command exists"
        log_info "  check_file <file> [create]           Check if a file exists"
        log_info "  check_directory <dir> [create]       Check if a directory exists"
        log_info "  validate_input <input> <pattern> [msg] Validate input against a pattern"
        log_info "  execute_with_timeout <timeout> <cmd> Execute a command with timeout"
        log_info "  check_container_running <container>  Check if a container is running"
        log_info "  check_network <host> [port] [timeout] Check network connectivity"
        log_info "  log_message <level> <message>        Log a message"
        log_info "  get_error_name <code>                Get error name from code"
        log_info "  get_error_code <name>                Get error code from name"
        exit 1
    fi
    
    # Execute the requested function
    "$@"
fi