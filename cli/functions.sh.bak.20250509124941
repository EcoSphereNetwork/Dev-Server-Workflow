#!/bin/bash
# Functions for the Dev-Server CLI

# Load configuration
source "$(dirname "$0")/config.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Log levels
LOG_DEBUG=0
LOG_INFO=1
LOG_WARN=2
LOG_ERROR=3

# Current log level (default: INFO)
CURRENT_LOG_LEVEL=${LOG_INFO}

# Set log level from environment variable if available
if [[ -n "${LOG_LEVEL}" ]]; then
    case "${LOG_LEVEL}" in
        debug) CURRENT_LOG_LEVEL=${LOG_DEBUG} ;;
        info) CURRENT_LOG_LEVEL=${LOG_INFO} ;;
        warn) CURRENT_LOG_LEVEL=${LOG_WARN} ;;
        error) CURRENT_LOG_LEVEL=${LOG_ERROR} ;;
    esac
fi

# Logging functions
log_debug() {
    if [[ ${CURRENT_LOG_LEVEL} -le ${LOG_DEBUG} ]]; then
        echo -e "${CYAN}[DEBUG]${NC} $1"
    fi
}

log_info() {
    if [[ ${CURRENT_LOG_LEVEL} -le ${LOG_INFO} ]]; then
        echo -e "${GREEN}[INFO]${NC} $1"
    fi
}

log_warn() {
    if [[ ${CURRENT_LOG_LEVEL} -le ${LOG_WARN} ]]; then
        echo -e "${YELLOW}[WARN]${NC} $1"
    fi
}

log_error() {
    if [[ ${CURRENT_LOG_LEVEL} -le ${LOG_ERROR} ]]; then
        echo -e "${RED}[ERROR]${NC} $1"
    fi
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Cannot connect to the Docker daemon. Is the docker daemon running?"
        return 1
    fi
    return 0
}

# Check if a container is running
check_container_running() {
    local container_name="$1"
    if docker ps --format '{{.Names}}' | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

# Check if a container exists
check_container_exists() {
    local container_name="$1"
    if docker ps -a --format '{{.Names}}' | grep -q "^${container_name}$"; then
        return 0
    else
        return 1
    fi
}

# Check if a port is in use
check_port_in_use() {
    local port="$1"
    if command -v netstat > /dev/null; then
        if netstat -tuln | grep -q ":${port} "; then
            return 0
        fi
    elif command -v ss > /dev/null; then
        if ss -tuln | grep -q ":${port} "; then
            return 0
        fi
    else
        log_warn "Neither netstat nor ss is available. Cannot check if port ${port} is in use."
        return 1
    fi
    return 1
}

# Check if a command is available
check_command() {
    local cmd="$1"
    if command -v "${cmd}" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Check if a Python package is installed
check_python_package() {
    local package="$1"
    if python3 -c "import ${package}" > /dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Check if a file exists
check_file_exists() {
    local file="$1"
    if [[ -f "${file}" ]]; then
        return 0
    else
        return 1
    fi
}

# Check if a directory exists
check_directory_exists() {
    local dir="$1"
    if [[ -d "${dir}" ]]; then
        return 0
    else
        return 1
    fi
}

# Create a directory if it doesn't exist
create_directory() {
    local dir="$1"
    if ! check_directory_exists "${dir}"; then
        log_debug "Creating directory ${dir}"
        mkdir -p "${dir}"
        return $?
    fi
    return 0
}

# Check if a process is running
check_process_running() {
    local process_name="$1"
    if pgrep -f "${process_name}" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Kill a process by name
kill_process() {
    local process_name="$1"
    if check_process_running "${process_name}"; then
        log_debug "Killing process ${process_name}"
        pkill -f "${process_name}"
        return $?
    fi
    return 0
}

# Start a container
start_container() {
    local container_name="$1"
    local image_name="$2"
    local port_mapping="$3"
    local environment="$4"
    local volume_mapping="$5"
    local network="$6"
    
    if check_container_running "${container_name}"; then
        log_info "Container ${container_name} is already running"
        return 0
    fi
    
    if check_container_exists "${container_name}"; then
        log_debug "Starting existing container ${container_name}"
        docker start "${container_name}"
        return $?
    fi
    
    log_debug "Creating and starting container ${container_name}"
    
    local cmd="docker run -d --name ${container_name}"
    
    if [[ -n "${port_mapping}" ]]; then
        cmd="${cmd} ${port_mapping}"
    fi
    
    if [[ -n "${environment}" ]]; then
        cmd="${cmd} ${environment}"
    fi
    
    if [[ -n "${volume_mapping}" ]]; then
        cmd="${cmd} ${volume_mapping}"
    fi
    
    if [[ -n "${network}" ]]; then
        cmd="${cmd} --network ${network}"
    fi
    
    cmd="${cmd} ${image_name}"
    
    log_debug "Running command: ${cmd}"
    eval "${cmd}"
    return $?
}

# Stop a container
stop_container() {
    local container_name="$1"
    
    if ! check_container_running "${container_name}"; then
        log_info "Container ${container_name} is not running"
        return 0
    fi
    
    log_debug "Stopping container ${container_name}"
    docker stop "${container_name}"
    return $?
}

# Restart a container
restart_container() {
    local container_name="$1"
    
    if ! check_container_exists "${container_name}"; then
        log_error "Container ${container_name} does not exist"
        return 1
    fi
    
    log_debug "Restarting container ${container_name}"
    docker restart "${container_name}"
    return $?
}

# Get container logs
get_container_logs() {
    local container_name="$1"
    local tail="${2:-100}"
    
    if ! check_container_exists "${container_name}"; then
        log_error "Container ${container_name} does not exist"
        return 1
    fi
    
    log_debug "Getting logs for container ${container_name}"
    docker logs --tail "${tail}" "${container_name}"
    return $?
}

# Follow container logs
follow_container_logs() {
    local container_name="$1"
    
    if ! check_container_exists "${container_name}"; then
        log_error "Container ${container_name} does not exist"
        return 1
    fi
    
    log_debug "Following logs for container ${container_name}"
    docker logs -f "${container_name}"
    return $?
}

# Check if a Docker network exists
check_network_exists() {
    local network_name="$1"
    if docker network ls --format '{{.Name}}' | grep -q "^${network_name}$"; then
        return 0
    else
        return 1
    fi
}

# Create a Docker network if it doesn't exist
create_network() {
    local network_name="$1"
    if ! check_network_exists "${network_name}"; then
        log_debug "Creating Docker network ${network_name}"
        docker network create "${network_name}"
        return $?
    fi
    return 0
}

# Check if a Docker volume exists
check_volume_exists() {
    local volume_name="$1"
    if docker volume ls --format '{{.Name}}' | grep -q "^${volume_name}$"; then
        return 0
    else
        return 1
    fi
}

# Create a Docker volume if it doesn't exist
create_volume() {
    local volume_name="$1"
    if ! check_volume_exists "${volume_name}"; then
        log_debug "Creating Docker volume ${volume_name}"
        docker volume create "${volume_name}"
        return $?
    fi
    return 0
}

# Start n8n
start_n8n() {
    log_info "Starting n8n..."
    
    # Check if Docker is running
    if ! check_docker; then
        log_error "Docker is not running. Cannot start n8n."
        return 1
    fi
    
    # Create network if it doesn't exist
    create_network "${DOCKER_NETWORK}"
    
    # Create data directory if it doesn't exist
    create_directory "${N8N_DATA_DIR}"
    
    # Check if port is in use
    if check_port_in_use "${N8N_PORT}"; then
        log_warn "Port ${N8N_PORT} is already in use. n8n may not start properly."
    fi
    
    # Start n8n container
    start_container "n8n" \
        "n8nio/n8n:latest" \
        "-p ${N8N_PORT}:5678" \
        "-e N8N_BASIC_AUTH_ACTIVE=true -e N8N_BASIC_AUTH_USER=${N8N_USER} -e N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD} -e N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY}" \
        "-v ${N8N_DATA_DIR}:/home/node/.n8n" \
        "${DOCKER_NETWORK}"
    
    if [[ $? -eq 0 ]]; then
        log_info "n8n started successfully. Web interface available at http://localhost:${N8N_PORT}"
        return 0
    else
        log_error "Failed to start n8n."
        return 1
    fi
}

# Stop n8n
stop_n8n() {
    log_info "Stopping n8n..."
    
    # Check if Docker is running
    if ! check_docker; then
        log_error "Docker is not running. Cannot stop n8n."
        return 1
    fi
    
    # Stop n8n container
    stop_container "n8n"
    
    if [[ $? -eq 0 ]]; then
        log_info "n8n stopped successfully."
        return 0
    else
        log_error "Failed to stop n8n."
        return 1
    fi
}

# Start MCP server
start_mcp() {
    local mcp_type="${1:-n8n}"
    log_info "Starting ${mcp_type} MCP server..."
    
    # Check if Python is available
    if ! check_command "python3"; then
        log_error "Python 3 is not available. Cannot start MCP server."
        return 1
    fi
    
    # Check if required Python packages are installed
    if ! check_python_package "aiohttp"; then
        log_warn "aiohttp package is not installed. Installing..."
        python3 -m pip install aiohttp
    fi
    
    # Create logs directory if it doesn't exist
    create_directory "${LOGS_DIR}"
    
    if [[ "${mcp_type}" == "n8n" ]]; then
        # Check if port is in use
        if check_port_in_use "${MCP_PORT}"; then
            log_warn "Port ${MCP_PORT} is already in use. MCP server may not start properly."
        fi
        
        # Kill any existing MCP server process
        kill_process "n8n_mcp_server.py"
        
        # Start n8n MCP server
        log_debug "Starting n8n MCP server with command: python3 ${SRC_DIR}/n8n_mcp_server.py --n8n-url ${N8N_URL} --api-key ${N8N_API_KEY} --log-level ${LOG_LEVEL}"
        nohup python3 "${SRC_DIR}/n8n_mcp_server.py" --n8n-url "${N8N_URL}" --api-key "${N8N_API_KEY}" --log-level "${LOG_LEVEL}" > "${LOGS_DIR}/mcp_server.log" 2>&1 &
        
        # Check if MCP server started successfully
        sleep 2
        if check_process_running "n8n_mcp_server.py"; then
            log_info "n8n MCP server started successfully. Listening on port ${MCP_PORT}"
            return 0
        else
            log_error "Failed to start n8n MCP server. Check logs at ${LOGS_DIR}/mcp_server.log"
            return 1
        fi
    elif [[ "${mcp_type}" == "docker" ]]; then
        # Check if port is in use
        if check_port_in_use "${DOCKER_MCP_PORT}"; then
            log_warn "Port ${DOCKER_MCP_PORT} is already in use. Docker MCP server may not start properly."
        fi
        
        # Kill any existing Docker MCP server process
        kill_process "docker_mcp_server.py"
        
        # Start Docker MCP server
        log_debug "Starting Docker MCP server with command: python3 ${SRC_DIR}/docker_mcp_server.py --log-level ${LOG_LEVEL}"
        nohup python3 "${SRC_DIR}/docker_mcp_server.py" --log-level "${LOG_LEVEL}" > "${LOGS_DIR}/docker_mcp_server.log" 2>&1 &
        
        # Check if Docker MCP server started successfully
        sleep 2
        if check_process_running "docker_mcp_server.py"; then
            log_info "Docker MCP server started successfully. Listening on port ${DOCKER_MCP_PORT}"
            return 0
        else
            log_error "Failed to start Docker MCP server. Check logs at ${LOGS_DIR}/docker_mcp_server.log"
            return 1
        fi
    else
        log_error "Unknown MCP server type: ${mcp_type}"
        log_info "Available MCP server types: n8n, docker"
        return 1
    fi
}

# Stop MCP server
stop_mcp() {
    local mcp_type="${1:-n8n}"
    log_info "Stopping ${mcp_type} MCP server..."
    
    if [[ "${mcp_type}" == "n8n" ]]; then
        # Kill n8n MCP server process
        kill_process "n8n_mcp_server.py"
        
        if [[ $? -eq 0 ]]; then
            log_info "n8n MCP server stopped successfully."
            return 0
        else
            log_error "Failed to stop n8n MCP server."
            return 1
        fi
    elif [[ "${mcp_type}" == "docker" ]]; then
        # Kill Docker MCP server process
        kill_process "docker_mcp_server.py"
        
        if [[ $? -eq 0 ]]; then
            log_info "Docker MCP server stopped successfully."
            return 0
        else
            log_error "Failed to stop Docker MCP server."
            return 1
        fi
    elif [[ "${mcp_type}" == "all" ]]; then
        # Kill all MCP server processes
        kill_process "n8n_mcp_server.py"
        kill_process "docker_mcp_server.py"
        
        log_info "All MCP servers stopped."
        return 0
    else
        log_error "Unknown MCP server type: ${mcp_type}"
        log_info "Available MCP server types: n8n, docker, all"
        return 1
    fi
}

# Start Ollama
start_ollama() {
    log_info "Starting Ollama..."
    
    # Check if Docker is running
    if ! check_docker; then
        log_error "Docker is not running. Cannot start Ollama."
        return 1
    fi
    
    # Create network if it doesn't exist
    create_network "${DOCKER_NETWORK}"
    
    # Create data directory if it doesn't exist
    create_directory "${OLLAMA_DATA_DIR}"
    
    # Check if port is in use
    if check_port_in_use "${OLLAMA_PORT}"; then
        log_warn "Port ${OLLAMA_PORT} is already in use. Ollama may not start properly."
    fi
    
    # Start Ollama container
    start_container "ollama" \
        "ollama/ollama:latest" \
        "-p ${OLLAMA_PORT}:11434" \
        "" \
        "-v ${OLLAMA_DATA_DIR}:/root/.ollama" \
        "${DOCKER_NETWORK}"
    
    if [[ $? -eq 0 ]]; then
        log_info "Ollama started successfully. API available at http://localhost:${OLLAMA_PORT}"
        
        # Pull the default model if specified
        if [[ -n "${OLLAMA_DEFAULT_MODEL}" ]]; then
            log_info "Pulling default model ${OLLAMA_DEFAULT_MODEL}..."
            sleep 5 # Wait for Ollama to initialize
            docker exec ollama ollama pull "${OLLAMA_DEFAULT_MODEL}"
        fi
        
        return 0
    else
        log_error "Failed to start Ollama."
        return 1
    fi
}

# Stop Ollama
stop_ollama() {
    log_info "Stopping Ollama..."
    
    # Check if Docker is running
    if ! check_docker; then
        log_error "Docker is not running. Cannot stop Ollama."
        return 1
    fi
    
    # Stop Ollama container
    stop_container "ollama"
    
    if [[ $? -eq 0 ]]; then
        log_info "Ollama stopped successfully."
        return 0
    else
        log_error "Failed to stop Ollama."
        return 1
    fi
}

# Start OpenHands
start_openhands() {
    log_info "Starting OpenHands..."
    
    # Check if Docker is running
    if ! check_docker; then
        log_error "Docker is not running. Cannot start OpenHands."
        return 1
    fi
    
    # Create network if it doesn't exist
    create_network "${DOCKER_NETWORK}"
    
    # Create data directory if it doesn't exist
    create_directory "${OPENHANDS_DATA_DIR}"
    
    # Check if port is in use
    if check_port_in_use "${OPENHANDS_PORT}"; then
        log_warn "Port ${OPENHANDS_PORT} is already in use. OpenHands may not start properly."
    fi
    
    # Start OpenHands container
    start_container "openhands" \
        "openhands/openhands:latest" \
        "-p ${OPENHANDS_PORT}:8080" \
        "-e OPENHANDS_API_KEY=${OPENHANDS_API_KEY} -e LLM_API_KEY=${LLM_API_KEY} -e LLM_MODEL=${LLM_MODEL}" \
        "-v ${OPENHANDS_DATA_DIR}:/root/.config/openhands" \
        "${DOCKER_NETWORK}"
    
    if [[ $? -eq 0 ]]; then
        log_info "OpenHands started successfully. API available at http://localhost:${OPENHANDS_PORT}"
        return 0
    else
        log_error "Failed to start OpenHands."
        return 1
    fi
}

# Stop OpenHands
stop_openhands() {
    log_info "Stopping OpenHands..."
    
    # Check if Docker is running
    if ! check_docker; then
        log_error "Docker is not running. Cannot stop OpenHands."
        return 1
    fi
    
    # Stop OpenHands container
    stop_container "openhands"
    
    if [[ $? -eq 0 ]]; then
        log_info "OpenHands stopped successfully."
        return 0
    else
        log_error "Failed to stop OpenHands."
        return 1
    fi
}

# Start Llamafile
start_llamafile() {
    log_info "Starting Llamafile..."
    
    # Check if Llamafile exists
    if ! check_file_exists "${LLAMAFILE_PATH}"; then
        log_error "Llamafile not found at ${LLAMAFILE_PATH}. Cannot start Llamafile."
        return 1
    fi
    
    # Check if Llamafile is executable
    if [[ ! -x "${LLAMAFILE_PATH}" ]]; then
        log_warn "Llamafile is not executable. Making it executable..."
        chmod +x "${LLAMAFILE_PATH}"
    fi
    
    # Check if port is in use
    if check_port_in_use "${LLAMAFILE_PORT}"; then
        log_warn "Port ${LLAMAFILE_PORT} is already in use. Llamafile may not start properly."
    fi
    
    # Create logs directory if it doesn't exist
    create_directory "${LOGS_DIR}"
    
    # Kill any existing Llamafile process
    kill_process "${LLAMAFILE_PATH}"
    
    # Start Llamafile
    log_debug "Starting Llamafile with command: ${LLAMAFILE_PATH} -m ${LLAMAFILE_MODEL} -c ${LLAMAFILE_CTX_SIZE} -ngl ${LLAMAFILE_GPU_LAYERS} -t ${LLAMAFILE_THREADS} --port ${LLAMAFILE_PORT}"
    nohup "${LLAMAFILE_PATH}" -m "${LLAMAFILE_MODEL}" -c "${LLAMAFILE_CTX_SIZE}" -ngl "${LLAMAFILE_GPU_LAYERS}" -t "${LLAMAFILE_THREADS}" --port "${LLAMAFILE_PORT}" > "${LOGS_DIR}/llamafile.log" 2>&1 &
    
    # Check if Llamafile started successfully
    sleep 2
    if check_process_running "${LLAMAFILE_PATH}"; then
        log_info "Llamafile started successfully. API available at http://localhost:${LLAMAFILE_PORT}"
        return 0
    else
        log_error "Failed to start Llamafile. Check logs at ${LOGS_DIR}/llamafile.log"
        return 1
    fi
}

# Stop Llamafile
stop_llamafile() {
    log_info "Stopping Llamafile..."
    
    # Kill Llamafile process
    kill_process "${LLAMAFILE_PATH}"
    
    if [[ $? -eq 0 ]]; then
        log_info "Llamafile stopped successfully."
        return 0
    else
        log_error "Failed to stop Llamafile."
        return 1
    fi
}

# Install ShellGPT
install_shellgpt() {
    log_info "Installing ShellGPT..."
    
    # Check if Python is available
    if ! check_command "python3"; then
        log_error "Python 3 is not available. Cannot install ShellGPT."
        return 1
    fi
    
    # Install ShellGPT
    log_debug "Installing ShellGPT with pip..."
    python3 -m pip install shell-gpt
    
    if [[ $? -eq 0 ]]; then
        log_info "ShellGPT installed successfully."
        
        # Configure ShellGPT if API key is available
        if [[ -n "${LLM_API_KEY}" ]]; then
            log_info "Configuring ShellGPT with API key..."
            sgpt --api-key "${LLM_API_KEY}" config set
        fi
        
        return 0
    else
        log_error "Failed to install ShellGPT."
        return 1
    fi
}

# Check status of all components
check_status() {
    echo -e "${BLUE}=== Dev-Server Status ===${NC}"
    
    # Check if Docker is running
    if ! check_docker; then
        log_warn "Docker is not running. Container status checks will be skipped."
        docker_running=false
    else
        docker_running=true
    fi
    
    # Check MCP server status
    if check_process_running "n8n_mcp_server.py"; then
        echo -e "${GREEN}✅ MCP-Server: Läuft${NC}"
    else
        echo -e "${RED}❌ MCP-Server: Gestoppt${NC}"
    fi
    
    # Check n8n status
    if [[ "${docker_running}" == "true" ]]; then
        if check_container_running "n8n"; then
            echo -e "${GREEN}✅ n8n: Läuft${NC}"
        else
            echo -e "${RED}❌ n8n: Gestoppt${NC}"
        fi
    else
        echo -e "${RED}❌ n8n: Gestoppt${NC}"
    fi
    
    # Check Ollama status
    if [[ "${docker_running}" == "true" ]]; then
        if check_container_running "ollama"; then
            echo -e "${GREEN}✅ Ollama: Läuft${NC}"
        else
            echo -e "${RED}❌ Ollama: Gestoppt${NC}"
        fi
    else
        echo -e "${RED}❌ Ollama: Gestoppt${NC}"
    fi
    
    # Check OpenHands status
    if [[ "${docker_running}" == "true" ]]; then
        if check_container_running "openhands"; then
            echo -e "${GREEN}✅ OpenHands: Läuft${NC}"
        else
            echo -e "${RED}❌ OpenHands: Gestoppt${NC}"
        fi
    else
        echo -e "${RED}❌ OpenHands: Gestoppt${NC}"
    fi
    
    # Check Llamafile status
    if check_process_running "${LLAMAFILE_PATH}"; then
        echo -e "${GREEN}✅ Llamafile: Läuft${NC}"
    else
        echo -e "${RED}❌ Llamafile: Gestoppt${NC}"
    fi
    
    # Check ShellGPT status
    if check_command "sgpt"; then
        echo -e "${GREEN}✅ ShellGPT: Installiert${NC}"
    else
        echo -e "${RED}❌ ShellGPT: Nicht installiert${NC}"
    fi
}

# Start all components
start_all() {
    log_info "Starting all components..."
    
    start_n8n
    start_mcp
    start_ollama
    start_openhands
    start_llamafile
    
    log_info "All components started."
    check_status
}

# Stop all components
stop_all() {
    log_info "Stopping all components..."
    
    stop_n8n
    stop_mcp
    stop_ollama
    stop_openhands
    stop_llamafile
    
    log_info "All components stopped."
    check_status
}

# Restart all components
restart_all() {
    log_info "Restarting all components..."
    
    stop_all
    start_all
    
    log_info "All components restarted."
}

# Show logs for a component
show_logs() {
    local component="$1"
    local follow="${2:-false}"
    
    case "${component}" in
        n8n)
            if check_container_exists "n8n"; then
                if [[ "${follow}" == "true" ]]; then
                    follow_container_logs "n8n"
                else
                    get_container_logs "n8n"
                fi
            else
                log_error "n8n container does not exist."
                return 1
            fi
            ;;
        mcp)
            if check_file_exists "${LOGS_DIR}/mcp_server.log"; then
                if [[ "${follow}" == "true" ]]; then
                    tail -f "${LOGS_DIR}/mcp_server.log"
                else
                    cat "${LOGS_DIR}/mcp_server.log"
                fi
            else
                log_error "MCP server log file does not exist."
                return 1
            fi
            ;;
        ollama)
            if check_container_exists "ollama"; then
                if [[ "${follow}" == "true" ]]; then
                    follow_container_logs "ollama"
                else
                    get_container_logs "ollama"
                fi
            else
                log_error "Ollama container does not exist."
                return 1
            fi
            ;;
        openhands)
            if check_container_exists "openhands"; then
                if [[ "${follow}" == "true" ]]; then
                    follow_container_logs "openhands"
                else
                    get_container_logs "openhands"
                fi
            else
                log_error "OpenHands container does not exist."
                return 1
            fi
            ;;
        llamafile)
            if check_file_exists "${LOGS_DIR}/llamafile.log"; then
                if [[ "${follow}" == "true" ]]; then
                    tail -f "${LOGS_DIR}/llamafile.log"
                else
                    cat "${LOGS_DIR}/llamafile.log"
                fi
            else
                log_error "Llamafile log file does not exist."
                return 1
            fi
            ;;
        all)
            log_info "Showing logs for all components..."
            
            log_info "n8n logs:"
            show_logs "n8n" "false"
            
            log_info "MCP server logs:"
            show_logs "mcp" "false"
            
            log_info "Ollama logs:"
            show_logs "ollama" "false"
            
            log_info "OpenHands logs:"
            show_logs "openhands" "false"
            
            log_info "Llamafile logs:"
            show_logs "llamafile" "false"
            ;;
        *)
            log_error "Unknown component: ${component}"
            return 1
            ;;
    esac
}

# Configure a component
configure_component() {
    local option="$1"
    local value="$2"
    
    case "${option}" in
        llm-api-key)
            log_info "Setting LLM API key..."
            sed -i "s/^LLM_API_KEY=.*/LLM_API_KEY=${value}/" "${CONFIG_FILE}"
            log_info "LLM API key updated."
            ;;
        github-token)
            log_info "Setting GitHub token..."
            sed -i "s/^GITHUB_TOKEN=.*/GITHUB_TOKEN=${value}/" "${CONFIG_FILE}"
            log_info "GitHub token updated."
            ;;
        openproject-token)
            log_info "Setting OpenProject token..."
            sed -i "s/^OPENPROJECT_TOKEN=.*/OPENPROJECT_TOKEN=${value}/" "${CONFIG_FILE}"
            log_info "OpenProject token updated."
            ;;
        n8n-api-key)
            log_info "Setting n8n API key..."
            sed -i "s/^N8N_API_KEY=.*/N8N_API_KEY=${value}/" "${CONFIG_FILE}"
            log_info "n8n API key updated."
            ;;
        workspace-path)
            log_info "Setting workspace path..."
            sed -i "s|^WORKSPACE_PATH=.*|WORKSPACE_PATH=${value}|" "${CONFIG_FILE}"
            log_info "Workspace path updated."
            ;;
        openhands-docker-mcp)
            log_info "Generating OpenHands Docker MCP configuration..."
            python3 "${SRC_DIR}/generate_docker_mcp_config.py" -o "${value}"
            if [[ $? -eq 0 ]]; then
                log_info "OpenHands Docker MCP configuration generated at ${value}"
            else
                log_error "Failed to generate OpenHands Docker MCP configuration"
                return 1
            fi
            ;;
        *)
            log_error "Unknown configuration option: ${option}"
            return 1
            ;;
    esac
    
    # Reload configuration
    source "${CONFIG_FILE}"
}

# List available resources
list_resources() {
    local resource_type="$1"
    
    case "${resource_type}" in
        workflows)
            log_info "Listing available workflows..."
            
            # Check if n8n is running
            if ! check_container_running "n8n"; then
                log_error "n8n is not running. Cannot list workflows."
                return 1
            fi
            
            # Check if API key is available
            if [[ -z "${N8N_API_KEY}" ]]; then
                log_error "n8n API key is not set. Cannot list workflows."
                return 1
            fi
            
            # List workflows
            curl -s -H "X-N8N-API-KEY: ${N8N_API_KEY}" "${N8N_URL}/api/v1/workflows" | jq -r '.data[] | "ID: \(.id) | Name: \(.name) | Active: \(.active)"'
            ;;
        models)
            log_info "Listing available models..."
            
            # Check if Ollama is running
            if ! check_container_running "ollama"; then
                log_error "Ollama is not running. Cannot list models."
                return 1
            fi
            
            # List models
            docker exec ollama ollama list
            ;;
        containers)
            log_info "Listing running containers..."
            
            # Check if Docker is running
            if ! check_docker; then
                log_error "Docker is not running. Cannot list containers."
                return 1
            fi
            
            # List containers
            docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
            ;;
        *)
            log_error "Unknown resource type: ${resource_type}"
            return 1
            ;;
    esac
}

# Switch between LLMs
switch_llm() {
    local llm="$1"
    
    case "${llm}" in
        llamafile)
            log_info "Switching to Llamafile LLM..."
            
            # Stop any running LLM containers
            stop_ollama
            
            # Start Llamafile
            start_llamafile
            
            # Update configuration
            sed -i "s/^LLM_MODEL=.*/LLM_MODEL=llamafile/" "${CONFIG_FILE}"
            log_info "Switched to Llamafile LLM."
            ;;
        claude)
            log_info "Switching to Claude LLM..."
            
            # Check if API key is available
            if [[ -z "${LLM_API_KEY}" ]]; then
                log_error "LLM API key is not set. Cannot switch to Claude."
                return 1
            fi
            
            # Stop any running LLM processes
            stop_llamafile
            
            # Update configuration
            sed -i "s/^LLM_MODEL=.*/LLM_MODEL=anthropic\/claude-3-5-sonnet-20240620/" "${CONFIG_FILE}"
            log_info "Switched to Claude LLM."
            ;;
        openai)
            log_info "Switching to OpenAI LLM..."
            
            # Check if API key is available
            if [[ -z "${LLM_API_KEY}" ]]; then
                log_error "LLM API key is not set. Cannot switch to OpenAI."
                return 1
            fi
            
            # Stop any running LLM processes
            stop_llamafile
            
            # Update configuration
            sed -i "s/^LLM_MODEL=.*/LLM_MODEL=openai\/gpt-4o/" "${CONFIG_FILE}"
            log_info "Switched to OpenAI LLM."
            ;;
        *)
            log_error "Unknown LLM: ${llm}"
            return 1
            ;;
    esac
    
    # Reload configuration
    source "${CONFIG_FILE}"
}

# Create a backup
create_backup() {
    local component="$1"
    local backup_dir="${BACKUP_DIR}/$(date +%Y%m%d_%H%M%S)"
    
    # Create backup directory
    create_directory "${backup_dir}"
    
    case "${component}" in
        n8n)
            log_info "Creating backup of n8n..."
            
            # Check if n8n data directory exists
            if ! check_directory_exists "${N8N_DATA_DIR}"; then
                log_error "n8n data directory does not exist."
                return 1
            fi
            
            # Create backup
            tar -czf "${backup_dir}/n8n_backup.tar.gz" -C "$(dirname "${N8N_DATA_DIR}")" "$(basename "${N8N_DATA_DIR}")"
            
            if [[ $? -eq 0 ]]; then
                log_info "n8n backup created at ${backup_dir}/n8n_backup.tar.gz"
                return 0
            else
                log_error "Failed to create n8n backup."
                return 1
            fi
            ;;
        openhands)
            log_info "Creating backup of OpenHands..."
            
            # Check if OpenHands data directory exists
            if ! check_directory_exists "${OPENHANDS_DATA_DIR}"; then
                log_error "OpenHands data directory does not exist."
                return 1
            fi
            
            # Create backup
            tar -czf "${backup_dir}/openhands_backup.tar.gz" -C "$(dirname "${OPENHANDS_DATA_DIR}")" "$(basename "${OPENHANDS_DATA_DIR}")"
            
            if [[ $? -eq 0 ]]; then
                log_info "OpenHands backup created at ${backup_dir}/openhands_backup.tar.gz"
                return 0
            else
                log_error "Failed to create OpenHands backup."
                return 1
            fi
            ;;
        all)
            log_info "Creating backup of all components..."
            
            create_backup "n8n"
            create_backup "openhands"
            
            log_info "All backups created at ${backup_dir}"
            return 0
            ;;
        *)
            log_error "Unknown component: ${component}"
            return 1
            ;;
    esac
}

# Restore a backup
restore_backup() {
    local backup_file="$1"
    
    # Check if backup file exists
    if ! check_file_exists "${backup_file}"; then
        log_error "Backup file does not exist: ${backup_file}"
        return 1
    fi
    
    # Determine component from backup file name
    if [[ "${backup_file}" == *"n8n"* ]]; then
        log_info "Restoring n8n backup..."
        
        # Stop n8n
        stop_n8n
        
        # Restore backup
        tar -xzf "${backup_file}" -C "$(dirname "${N8N_DATA_DIR}")"
        
        if [[ $? -eq 0 ]]; then
            log_info "n8n backup restored."
            
            # Start n8n
            start_n8n
            
            return 0
        else
            log_error "Failed to restore n8n backup."
            return 1
        fi
    elif [[ "${backup_file}" == *"openhands"* ]]; then
        log_info "Restoring OpenHands backup..."
        
        # Stop OpenHands
        stop_openhands
        
        # Restore backup
        tar -xzf "${backup_file}" -C "$(dirname "${OPENHANDS_DATA_DIR}")"
        
        if [[ $? -eq 0 ]]; then
            log_info "OpenHands backup restored."
            
            # Start OpenHands
            start_openhands
            
            return 0
        else
            log_error "Failed to restore OpenHands backup."
            return 1
        fi
    else
        log_error "Unknown backup type: ${backup_file}"
        return 1
    fi
}

# Execute an AI command
execute_ai_command() {
    local prompt="$1"
    
    # Check if ShellGPT is installed
    if ! check_command "sgpt"; then
        log_warn "ShellGPT is not installed. Installing..."
        install_shellgpt
    fi
    
    # Execute AI command
    sgpt "${prompt}"
}

# Show interactive menu
show_menu() {
    # Source the menu script
    source "$(dirname "$0")/menu.sh"
}
# Start monitoring stack
start_monitoring() {
    log_info "Starting monitoring stack..."
    
    # Check if Docker is available
    if ! check_command "docker"; then
        log_error "Docker is not available. Cannot start monitoring stack."
        return 1
    fi
    
    # Check if Docker Compose is available
    if ! check_command "docker compose"; then
        log_warn "docker compose is not available. Trying docker compose..."
        if ! docker compose version > /dev/null 2>&1; then
            log_error "Docker Compose is not available. Cannot start monitoring stack."
            return 1
        fi
        
        # Use docker compose
        (cd "${WORKSPACE_DIR}/docker" && docker compose -f docker compose.monitoring.yml up -d)
    else
        # Use docker compose
        (cd "${WORKSPACE_DIR}/docker" && docker compose -f docker compose.monitoring.yml up -d)
    fi
    
    if [ $? -eq 0 ]; then
        log_info "Monitoring stack started successfully."
        log_info "Grafana is available at http://localhost:3000 (admin/admin)"
        log_info "Prometheus is available at http://localhost:9090"
        log_info "Alertmanager is available at http://localhost:9093"
        return 0
    else
        log_error "Failed to start monitoring stack."
        return 1
    fi
}

# Stop monitoring stack
stop_monitoring() {
    log_info "Stopping monitoring stack..."
    
    # Check if Docker is available
    if ! check_command "docker"; then
        log_error "Docker is not available. Cannot stop monitoring stack."
        return 1
    fi
    
    # Check if Docker Compose is available
    if ! check_command "docker compose"; then
        log_warn "docker compose is not available. Trying docker compose..."
        if ! docker compose version > /dev/null 2>&1; then
            log_error "Docker Compose is not available. Cannot stop monitoring stack."
            return 1
        fi
        
        # Use docker compose
        (cd "${WORKSPACE_DIR}/docker" && docker compose -f docker compose.monitoring.yml down)
    else
        # Use docker compose
        (cd "${WORKSPACE_DIR}/docker" && docker compose -f docker compose.monitoring.yml down)
    fi
    
    if [ $? -eq 0 ]; then
        log_info "Monitoring stack stopped successfully."
        return 0
    else
        log_error "Failed to stop monitoring stack."
        return 1
    fi
}
