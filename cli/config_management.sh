#!/bin/bash

# Source common functions
source "$(dirname "$0")/functions.sh"

# Configuration management functions

# Set a configuration value in a file
set_config_value() {
    local file="$1"
    local key="$2"
    local value="$3"
    local delimiter="$4"
    local comment_char="$5"
    
    # Default delimiter is "="
    if [ -z "$delimiter" ]; then
        delimiter="="
    fi
    
    # Default comment character is "#"
    if [ -z "$comment_char" ]; then
        comment_char="#"
    fi
    
    log_info "Setting $key to $value in $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if key exists in file
    if grep -q "^[[:space:]]*$key[[:space:]]*$delimiter" "$file"; then
        # Key exists, update it
        sed -i "s|^[[:space:]]*$key[[:space:]]*$delimiter.*|$key$delimiter$value|" "$file"
    elif grep -q "^[[:space:]]*$comment_char[[:space:]]*$key[[:space:]]*$delimiter" "$file"; then
        # Key exists but is commented out, uncomment and update it
        sed -i "s|^[[:space:]]*$comment_char[[:space:]]*$key[[:space:]]*$delimiter.*|$key$delimiter$value|" "$file"
    else
        # Key does not exist, add it
        echo "$key$delimiter$value" >> "$file"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Successfully set $key to $value in $file"
        return 0
    else
        log_error "Failed to set $key to $value in $file"
        return 1
    fi
}

# Get a configuration value from a file
get_config_value() {
    local file="$1"
    local key="$2"
    local delimiter="$3"
    local comment_char="$4"
    
    # Default delimiter is "="
    if [ -z "$delimiter" ]; then
        delimiter="="
    fi
    
    # Default comment character is "#"
    if [ -z "$comment_char" ]; then
        comment_char="#"
    fi
    
    log_info "Getting value of $key from $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Get value
    local value=$(grep "^[[:space:]]*$key[[:space:]]*$delimiter" "$file" | sed "s|^[[:space:]]*$key[[:space:]]*$delimiter[[:space:]]*||")
    
    if [ -n "$value" ]; then
        echo "$value"
        return 0
    else
        log_error "Key $key not found in $file"
        return 1
    fi
}

# Comment out a configuration value in a file
comment_config_value() {
    local file="$1"
    local key="$2"
    local delimiter="$3"
    local comment_char="$4"
    
    # Default delimiter is "="
    if [ -z "$delimiter" ]; then
        delimiter="="
    fi
    
    # Default comment character is "#"
    if [ -z "$comment_char" ]; then
        comment_char="#"
    fi
    
    log_info "Commenting out $key in $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if key exists in file
    if grep -q "^[[:space:]]*$key[[:space:]]*$delimiter" "$file"; then
        # Key exists, comment it out
        sed -i "s|^[[:space:]]*$key[[:space:]]*$delimiter|$comment_char $key$delimiter|" "$file"
    else
        log_error "Key $key not found in $file"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Successfully commented out $key in $file"
        return 0
    else
        log_error "Failed to comment out $key in $file"
        return 1
    fi
}

# Uncomment a configuration value in a file
uncomment_config_value() {
    local file="$1"
    local key="$2"
    local delimiter="$3"
    local comment_char="$4"
    
    # Default delimiter is "="
    if [ -z "$delimiter" ]; then
        delimiter="="
    fi
    
    # Default comment character is "#"
    if [ -z "$comment_char" ]; then
        comment_char="#"
    fi
    
    log_info "Uncommenting $key in $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if key exists in file
    if grep -q "^[[:space:]]*$comment_char[[:space:]]*$key[[:space:]]*$delimiter" "$file"; then
        # Key exists and is commented out, uncomment it
        sed -i "s|^[[:space:]]*$comment_char[[:space:]]*$key[[:space:]]*$delimiter|$key$delimiter|" "$file"
    else
        log_error "Commented key $key not found in $file"
        return 1
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Successfully uncommented $key in $file"
        return 0
    else
        log_error "Failed to uncomment $key in $file"
        return 1
    fi
}

# Set a JSON configuration value
set_json_config_value() {
    local file="$1"
    local key="$2"
    local value="$3"
    local jq_path="$4"
    
    log_info "Setting JSON value $key to $value in $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_error "jq is not installed. Please install it first."
        return 1
    fi
    
    # If jq_path is not provided, use the key as the path
    if [ -z "$jq_path" ]; then
        jq_path=".$key"
    fi
    
    # Create a temporary file
    local temp_file=$(mktemp)
    
    # Set the value
    jq "$jq_path = $value" "$file" > "$temp_file"
    
    if [ $? -eq 0 ]; then
        # Replace the original file with the temporary file
        mv "$temp_file" "$file"
        log_success "Successfully set JSON value $key to $value in $file"
        return 0
    else
        rm "$temp_file"
        log_error "Failed to set JSON value $key to $value in $file"
        return 1
    fi
}

# Get a JSON configuration value
get_json_config_value() {
    local file="$1"
    local jq_path="$2"
    
    log_info "Getting JSON value at $jq_path from $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_error "jq is not installed. Please install it first."
        return 1
    fi
    
    # Get the value
    local value=$(jq -r "$jq_path" "$file")
    
    if [ $? -eq 0 ] && [ "$value" != "null" ]; then
        echo "$value"
        return 0
    else
        log_error "JSON path $jq_path not found in $file"
        return 1
    fi
}

# Set a YAML configuration value
set_yaml_config_value() {
    local file="$1"
    local key="$2"
    local value="$3"
    local yq_path="$4"
    
    log_info "Setting YAML value $key to $value in $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if yq is installed
    if ! command -v yq &> /dev/null; then
        log_error "yq is not installed. Please install it first."
        return 1
    fi
    
    # If yq_path is not provided, use the key as the path
    if [ -z "$yq_path" ]; then
        yq_path=".$key"
    fi
    
    # Create a temporary file
    local temp_file=$(mktemp)
    
    # Set the value
    yq -y "$yq_path = $value" "$file" > "$temp_file"
    
    if [ $? -eq 0 ]; then
        # Replace the original file with the temporary file
        mv "$temp_file" "$file"
        log_success "Successfully set YAML value $key to $value in $file"
        return 0
    else
        rm "$temp_file"
        log_error "Failed to set YAML value $key to $value in $file"
        return 1
    fi
}

# Get a YAML configuration value
get_yaml_config_value() {
    local file="$1"
    local yq_path="$2"
    
    log_info "Getting YAML value at $yq_path from $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if yq is installed
    if ! command -v yq &> /dev/null; then
        log_error "yq is not installed. Please install it first."
        return 1
    fi
    
    # Get the value
    local value=$(yq -r "$yq_path" "$file")
    
    if [ $? -eq 0 ] && [ "$value" != "null" ]; then
        echo "$value"
        return 0
    else
        log_error "YAML path $yq_path not found in $file"
        return 1
    fi
}

# Set an XML configuration value
set_xml_config_value() {
    local file="$1"
    local xpath="$2"
    local value="$3"
    
    log_info "Setting XML value at $xpath to $value in $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if xmlstarlet is installed
    if ! command -v xmlstarlet &> /dev/null; then
        log_error "xmlstarlet is not installed. Please install it first."
        return 1
    fi
    
    # Create a temporary file
    local temp_file=$(mktemp)
    
    # Set the value
    xmlstarlet ed -L -u "$xpath" -v "$value" "$file" > "$temp_file"
    
    if [ $? -eq 0 ]; then
        # Replace the original file with the temporary file
        mv "$temp_file" "$file"
        log_success "Successfully set XML value at $xpath to $value in $file"
        return 0
    else
        rm "$temp_file"
        log_error "Failed to set XML value at $xpath to $value in $file"
        return 1
    fi
}

# Get an XML configuration value
get_xml_config_value() {
    local file="$1"
    local xpath="$2"
    
    log_info "Getting XML value at $xpath from $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Check if xmlstarlet is installed
    if ! command -v xmlstarlet &> /dev/null; then
        log_error "xmlstarlet is not installed. Please install it first."
        return 1
    fi
    
    # Get the value
    local value=$(xmlstarlet sel -t -v "$xpath" "$file")
    
    if [ $? -eq 0 ] && [ -n "$value" ]; then
        echo "$value"
        return 0
    else
        log_error "XPath $xpath not found in $file"
        return 1
    fi
}

# Set an environment variable in .env file
set_env_var() {
    local file="$1"
    local key="$2"
    local value="$3"
    
    log_info "Setting environment variable $key to $value in $file"
    
    # Check if file exists, create it if it doesn't
    if [ ! -f "$file" ]; then
        touch "$file"
    fi
    
    # Check if key exists in file
    if grep -q "^$key=" "$file"; then
        # Key exists, update it
        sed -i "s|^$key=.*|$key=$value|" "$file"
    else
        # Key does not exist, add it
        echo "$key=$value" >> "$file"
    fi
    
    if [ $? -eq 0 ]; then
        log_success "Successfully set environment variable $key to $value in $file"
        return 0
    else
        log_error "Failed to set environment variable $key to $value in $file"
        return 1
    fi
}

# Get an environment variable from .env file
get_env_var() {
    local file="$1"
    local key="$2"
    
    log_info "Getting environment variable $key from $file"
    
    # Check if file exists
    if [ ! -f "$file" ]; then
        log_error "File $file does not exist"
        return 1
    fi
    
    # Get value
    local value=$(grep "^$key=" "$file" | sed "s|^$key=||")
    
    if [ -n "$value" ]; then
        echo "$value"
        return 0
    else
        log_error "Environment variable $key not found in $file"
        return 1
    fi
}

# Main function
main() {
    local command="$1"
    local file="$2"
    local key="$3"
    local value="$4"
    local extra="$5"
    
    case "$command" in
        "set")
            set_config_value "$file" "$key" "$value" "$extra"
            ;;
        "get")
            get_config_value "$file" "$key" "$extra"
            ;;
        "comment")
            comment_config_value "$file" "$key" "$extra"
            ;;
        "uncomment")
            uncomment_config_value "$file" "$key" "$extra"
            ;;
        "set-json")
            set_json_config_value "$file" "$key" "$value" "$extra"
            ;;
        "get-json")
            get_json_config_value "$file" "$key"
            ;;
        "set-yaml")
            set_yaml_config_value "$file" "$key" "$value" "$extra"
            ;;
        "get-yaml")
            get_yaml_config_value "$file" "$key"
            ;;
        "set-xml")
            set_xml_config_value "$file" "$key" "$value"
            ;;
        "get-xml")
            get_xml_config_value "$file" "$key"
            ;;
        "set-env")
            set_env_var "$file" "$key" "$value"
            ;;
        "get-env")
            get_env_var "$file" "$key"
            ;;
        *)
            echo "Usage: $0 [set|get|comment|uncomment|set-json|get-json|set-yaml|get-yaml|set-xml|get-xml|set-env|get-env] [file] [key] [value] [extra]"
            return 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi