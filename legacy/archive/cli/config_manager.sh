#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

# Centralized Configuration Management for Dev-Server-Workflow
# This script provides a unified API for managing configuration across different formats

# Set strict error handling
set -euo pipefail

# Base directory
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Current operation for error handling
CURRENT_OPERATION=""

# Error handling function
handle_error() {
    local exit_code=$1
    local line_number=$2
    local command="$3"

    log_info "${RED}[ERROR] Command '$command' in line $line_number failed with code $exit_code${NC}"

    # Perform rollback actions based on the current operation
    case "$CURRENT_OPERATION" in
        "load_config")
            log_info "${YELLOW}[ROLLBACK] Reverting to default configuration...${NC}"
            # No specific rollback needed, just exit
            ;;
        "save_config")
            log_info "${YELLOW}[ROLLBACK] Reverting changes to configuration file...${NC}"
            # Could implement backup/restore here if needed
            ;;
    esac

    exit $exit_code
}

# Set up error trap
trap 'handle_error $? $LINENO "$BASH_COMMAND"' ERR

# Load configuration from different sources
load_config() {
    CURRENT_OPERATION="load_config"
    local config_type="$1"
    local config_path="$2"
    local prefix="${3:-}"  # Optional prefix for variable names

    log_info "${BLUE}[INFO] Loading configuration from $config_path (type: $config_type)${NC}"

    # Check if file exists
    if [[ ! -f "$config_path" ]]; then
        log_info "${YELLOW}[WARN] Configuration file $config_path does not exist${NC}"
        return 1
    fi

    case "$config_type" in
        "env")
            # Load .env file
            while IFS='=' read -r key value || [[ -n "$key" ]]; do
                # Skip comments and empty lines
                [[ "${key}" =~ ^#.*$ || -z "${key}" ]] && continue
                
                # Remove quotes and whitespace from value
                value="${value%\"}"
                value="${value#\"}"
                value="${value%\'}"
                value="${value#\'}"
                value="${value#"${value%%[![:space:]]*}"}"  # Remove leading whitespace
                value="${value%"${value##*[![:space:]]}"}"  # Remove trailing whitespace
                
                # Create variable name with optional prefix
                if [[ -n "$prefix" ]]; then
                    var_name="${prefix}_${key}"
                else
                    var_name="$key"
                fi
                
                # Export the variable
                export "${var_name}=${value}"
                log_info "${GREEN}[DEBUG] Loaded $var_name=${value}${NC}"
            done < "$config_path"
            ;;
        "json")
            # Check if jq is installed
            if ! command -v jq &> /dev/null; then
                log_info "${RED}[ERROR] jq is required for JSON configuration but is not installed${NC}"
                log_info "${YELLOW}[INFO] Install jq with: apt-get install -y jq${NC}"
                return 1
            fi

            # Load JSON file
            local json_config=$(cat "$config_path")
            
            # Extract all keys at the top level
            local keys=$(jq -r 'keys[]' "$config_path")
            
            # Process each key
            for key in $keys; do
                # Get the value
                local value=$(jq -r ".[\"$key\"]" "$config_path")
                
                # Create variable name with optional prefix
                if [[ -n "$prefix" ]]; then
                    var_name="${prefix}_${key}"
                else
                    var_name="$key"
                fi
                
                # Export the variable
                export "${var_name}=${value}"
                log_info "${GREEN}[DEBUG] Loaded $var_name=${value}${NC}"
            done
            ;;
        "yaml")
            # Check if yq is installed
            if ! command -v yq &> /dev/null; then
                log_info "${RED}[ERROR] yq is required for YAML configuration but is not installed${NC}"
                log_info "${YELLOW}[INFO] Install yq with: pip install yq${NC}"
                return 1
            fi

            # Load YAML file and convert to JSON
            local json_config=$(yq -r '.' "$config_path")
            
            # Extract all keys at the top level
            local keys=$(log_info "$json_config" | jq -r 'keys[]')
            
            # Process each key
            for key in $keys; do
                # Get the value
                local value=$(log_info "$json_config" | jq -r ".[\"$key\"]")
                
                # Create variable name with optional prefix
                if [[ -n "$prefix" ]]; then
                    var_name="${prefix}_${key}"
                else
                    var_name="$key"
                fi
                
                # Export the variable
                export "${var_name}=${value}"
                log_info "${GREEN}[DEBUG] Loaded $var_name=${value}${NC}"
            done
            ;;
        *)
            log_info "${RED}[ERROR] Unsupported configuration type: $config_type${NC}"
            return 1
            ;;
    esac

    return 0
}

# Save configuration to different formats
save_config() {
    CURRENT_OPERATION="save_config"
    local config_type="$1"
    local config_path="$2"
    local key="$3"
    local value="$4"
    local create_if_missing="${5:-true}"  # Create file if it doesn't exist

    log_info "${BLUE}[INFO] Saving configuration to $config_path (type: $config_type)${NC}"

    # Check if file exists and create it if needed
    if [[ ! -f "$config_path" && "$create_if_missing" == "true" ]]; then
        log_info "${YELLOW}[WARN] Creating new configuration file: $config_path${NC}"
        touch "$config_path"
    elif [[ ! -f "$config_path" ]]; then
        log_info "${RED}[ERROR] Configuration file $config_path does not exist${NC}"
        return 1
    fi

    case "$config_type" in
        "env")
            # Update or add key-value pair in .env file
            if grep -q "^${key}=" "$config_path"; then
                # Key exists, update it
                sed -i "s|^${key}=.*|${key}=${value}|" "$config_path"
            else
                # Key doesn't exist, add it
                log_info "${key}=${value}" >> "$config_path"
            fi
            ;;
        "json")
            # Check if jq is installed
            if ! command -v jq &> /dev/null; then
                log_info "${RED}[ERROR] jq is required for JSON configuration but is not installed${NC}"
                log_info "${YELLOW}[INFO] Install jq with: apt-get install -y jq${NC}"
                return 1
            fi

            # Create empty JSON object if file is empty
            if [[ ! -s "$config_path" ]]; then
                log_info "{}" > "$config_path"
            fi

            # Update JSON file
            local temp_file=$(mktemp)
            jq ".${key} = \"${value}\"" "$config_path" > "$temp_file"
            mv "$temp_file" "$config_path"
            ;;
        "yaml")
            # Check if yq is installed
            if ! command -v yq &> /dev/null; then
                log_info "${RED}[ERROR] yq is required for YAML configuration but is not installed${NC}"
                log_info "${YELLOW}[INFO] Install yq with: pip install yq${NC}"
                return 1
            fi

            # Create empty YAML file if it's empty
            if [[ ! -s "$config_path" ]]; then
                log_info "{}" > "$config_path"
            fi

            # Update YAML file
            local temp_file=$(mktemp)
            yq -y ".${key} = \"${value}\"" "$config_path" > "$temp_file"
            mv "$temp_file" "$config_path"
            ;;
        *)
            log_info "${RED}[ERROR] Unsupported configuration type: $config_type${NC}"
            return 1
            ;;
    esac

    log_info "${GREEN}[INFO] Successfully updated ${key}=${value} in $config_path${NC}"
    return 0
}

# Get a configuration value
get_config() {
    local config_type="$1"
    local config_path="$2"
    local key="$3"
    local default_value="${4:-}"  # Optional default value

    # Check if file exists
    if [[ ! -f "$config_path" ]]; then
        log_info "${YELLOW}[WARN] Configuration file $config_path does not exist${NC}" >&2
        log_info "$default_value"
        return 0
    fi

    case "$config_type" in
        "env")
            # Get value from .env file
            local value=$(grep "^${key}=" "$config_path" | cut -d= -f2- || log_info "$default_value")
            
            # Remove quotes
            value="${value%\"}"
            value="${value#\"}"
            value="${value%\'}"
            value="${value#\'}"
            
            log_info "$value"
            ;;
        "json")
            # Check if jq is installed
            if ! command -v jq &> /dev/null; then
                log_info "${RED}[ERROR] jq is required for JSON configuration but is not installed${NC}" >&2
                log_info "$default_value"
                return 0
            fi

            # Get value from JSON file
            jq -r ".${key} // \"$default_value\"" "$config_path"
            ;;
        "yaml")
            # Check if yq is installed
            if ! command -v yq &> /dev/null; then
                log_info "${RED}[ERROR] yq is required for YAML configuration but is not installed${NC}" >&2
                log_info "$default_value"
                return 0
            fi

            # Get value from YAML file
            yq -r ".${key} // \"$default_value\"" "$config_path"
            ;;
        *)
            log_info "${RED}[ERROR] Unsupported configuration type: $config_type${NC}" >&2
            log_info "$default_value"
            return 0
            ;;
    esac
}

# List all configuration keys
list_config() {
    local config_type="$1"
    local config_path="$2"

    # Check if file exists
    if [[ ! -f "$config_path" ]]; then
        log_info "${YELLOW}[WARN] Configuration file $config_path does not exist${NC}"
        return 1
    fi

    case "$config_type" in
        "env")
            # List all keys from .env file
            grep -v "^#" "$config_path" | grep "=" | cut -d= -f1
            ;;
        "json")
            # Check if jq is installed
            if ! command -v jq &> /dev/null; then
                log_info "${RED}[ERROR] jq is required for JSON configuration but is not installed${NC}"
                return 1
            fi

            # List all keys from JSON file
            jq -r 'keys[]' "$config_path"
            ;;
        "yaml")
            # Check if yq is installed
            if ! command -v yq &> /dev/null; then
                log_info "${RED}[ERROR] yq is required for YAML configuration but is not installed${NC}"
                return 1
            fi

            # List all keys from YAML file
            yq -r 'keys[]' "$config_path"
            ;;
        *)
            log_info "${RED}[ERROR] Unsupported configuration type: $config_type${NC}"
            return 1
            ;;
    esac

    return 0
}

# Delete a configuration key
delete_config() {
    local config_type="$1"
    local config_path="$2"
    local key="$3"

    # Check if file exists
    if [[ ! -f "$config_path" ]]; then
        log_info "${YELLOW}[WARN] Configuration file $config_path does not exist${NC}"
        return 1
    fi

    case "$config_type" in
        "env")
            # Delete key from .env file
            sed -i "/^${key}=/d" "$config_path"
            ;;
        "json")
            # Check if jq is installed
            if ! command -v jq &> /dev/null; then
                log_info "${RED}[ERROR] jq is required for JSON configuration but is not installed${NC}"
                return 1
            fi

            # Delete key from JSON file
            local temp_file=$(mktemp)
            jq "del(.${key})" "$config_path" > "$temp_file"
            mv "$temp_file" "$config_path"
            ;;
        "yaml")
            # Check if yq is installed
            if ! command -v yq &> /dev/null; then
                log_info "${RED}[ERROR] yq is required for YAML configuration but is not installed${NC}"
                return 1
            fi

            # Delete key from YAML file
            local temp_file=$(mktemp)
            yq -y "del(.${key})" "$config_path" > "$temp_file"
            mv "$temp_file" "$config_path"
            ;;
        *)
            log_info "${RED}[ERROR] Unsupported configuration type: $config_type${NC}"
            return 1
            ;;
    esac

    log_info "${GREEN}[INFO] Successfully deleted ${key} from $config_path${NC}"
    return 0
}

# Load all configuration files
load_all_configs() {
    # Load main .env file
    if [[ -f "${BASE_DIR}/.env" ]]; then
        load_config "env" "${BASE_DIR}/.env"
    fi

    # Load JSON configurations
    for json_file in $(find "${BASE_DIR}" -name "*.json" -not -path "*/node_modules/*" -not -path "*/\.*"); do
        # Extract a prefix from the filename
        local filename=$(basename "$json_file")
        local prefix=$(log_info "$filename" | sed 's/\.json$//' | tr '[:lower:]' '[:upper:]' | tr '-' '_')
        
        load_config "json" "$json_file" "$prefix"
    done

    # Load YAML configurations if yq is available
    if command -v yq &> /dev/null; then
        for yaml_file in $(find "${BASE_DIR}" -name "*.yaml" -o -name "*.yml" -not -path "*/node_modules/*" -not -path "*/\.*"); do
            # Extract a prefix from the filename
            local filename=$(basename "$yaml_file")
            local prefix=$(log_info "$filename" | sed 's/\.ya\?ml$//' | tr '[:lower:]' '[:upper:]' | tr '-' '_')
            
            load_config "yaml" "$yaml_file" "$prefix"
        done
    fi
}

# Main function to handle command-line arguments
main() {
    local command="$1"
    shift

    case "$command" in
        "load")
            if [[ $# -lt 2 ]]; then
                log_info "${RED}[ERROR] Usage: $0 load <config_type> <config_path> [prefix]${NC}"
                return 1
            fi
            
            local config_type="$1"
            local config_path="$2"
            local prefix="${3:-}"
            
            load_config "$config_type" "$config_path" "$prefix"
            ;;
        "save")
            if [[ $# -lt 4 ]]; then
                log_info "${RED}[ERROR] Usage: $0 save <config_type> <config_path> <key> <value> [create_if_missing]${NC}"
                return 1
            fi
            
            local config_type="$1"
            local config_path="$2"
            local key="$3"
            local value="$4"
            local create_if_missing="${5:-true}"
            
            save_config "$config_type" "$config_path" "$key" "$value" "$create_if_missing"
            ;;
        "get")
            if [[ $# -lt 3 ]]; then
                log_info "${RED}[ERROR] Usage: $0 get <config_type> <config_path> <key> [default_value]${NC}"
                return 1
            fi
            
            local config_type="$1"
            local config_path="$2"
            local key="$3"
            local default_value="${4:-}"
            
            get_config "$config_type" "$config_path" "$key" "$default_value"
            ;;
        "list")
            if [[ $# -lt 2 ]]; then
                log_info "${RED}[ERROR] Usage: $0 list <config_type> <config_path>${NC}"
                return 1
            fi
            
            local config_type="$1"
            local config_path="$2"
            
            list_config "$config_type" "$config_path"
            ;;
        "delete")
            if [[ $# -lt 3 ]]; then
                log_info "${RED}[ERROR] Usage: $0 delete <config_type> <config_path> <key>${NC}"
                return 1
            fi
            
            local config_type="$1"
            local config_path="$2"
            local key="$3"
            
            delete_config "$config_type" "$config_path" "$key"
            ;;
        "load-all")
            load_all_configs
            ;;
        *)
            log_info "${RED}[ERROR] Unknown command: $command${NC}"
            log_info "Available commands: load, save, get, list, delete, load-all"
            return 1
            ;;
    esac

    return 0
}

# If script is executed directly (not sourced), run main function
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [[ $# -lt 1 ]]; then
        log_info "${RED}[ERROR] Usage: $0 <command> [args...]${NC}"
        log_info "Available commands: load, save, get, list, delete, load-all"
        exit 1
    fi

    main "$@"
fi