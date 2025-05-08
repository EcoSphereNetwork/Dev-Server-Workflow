#!/bin/bash

# Source common functions
source "$(dirname "$0")/functions.sh"

# Monitoring management functions

# Check if a service is running
check_service_status() {
    local service="$1"
    local type="$2"
    
    log_info "Checking status of service $service"
    
    case "$type" in
        "systemd")
            systemctl is-active --quiet "$service"
            ;;
        "docker")
            docker ps --format '{{.Names}}' | grep -q "$service"
            ;;
        "process")
            pgrep -f "$service" > /dev/null
            ;;
        *)
            log_error "Unsupported service type: $type"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        log_info "Service $service is running"
        return 0
    else
        log_info "Service $service is not running"
        return 1
    fi
}

# Get service logs
get_service_logs() {
    local service="$1"
    local type="$2"
    local lines="$3"
    
    # Default to 100 lines
    if [ -z "$lines" ]; then
        lines=100
    fi
    
    log_info "Getting logs for service $service"
    
    case "$type" in
        "systemd")
            journalctl -u "$service" -n "$lines"
            ;;
        "docker")
            docker logs --tail "$lines" "$service"
            ;;
        "file")
            if [ -f "$service" ]; then
                tail -n "$lines" "$service"
            else
                log_error "Log file $service does not exist"
                return 1
            fi
            ;;
        *)
            log_error "Unsupported log type: $type"
            return 1
            ;;
    esac
    
    return $?
}

# Check disk usage
check_disk_usage() {
    local mount_point="$1"
    local threshold="$2"
    
    # Default to 90% threshold
    if [ -z "$threshold" ]; then
        threshold=90
    fi
    
    log_info "Checking disk usage for $mount_point"
    
    # If mount_point is not provided, check all mount points
    if [ -z "$mount_point" ]; then
        df -h
    else
        # Get disk usage percentage
        local usage=$(df -h "$mount_point" | grep -v Filesystem | awk '{print $5}' | sed 's/%//')
        
        if [ $? -ne 0 ]; then
            log_error "Failed to get disk usage for $mount_point"
            return 1
        fi
        
        echo "Disk usage for $mount_point: $usage%"
        
        # Check if usage is above threshold
        if [ "$usage" -gt "$threshold" ]; then
            log_warning "Disk usage for $mount_point is above threshold ($usage% > $threshold%)"
            return 2
        fi
    fi
    
    return 0
}

# Check memory usage
check_memory_usage() {
    local threshold="$1"
    
    # Default to 90% threshold
    if [ -z "$threshold" ]; then
        threshold=90
    fi
    
    log_info "Checking memory usage"
    
    # Get memory usage percentage
    local total=$(free | grep Mem | awk '{print $2}')
    local used=$(free | grep Mem | awk '{print $3}')
    local usage=$(( used * 100 / total ))
    
    if [ $? -ne 0 ]; then
        log_error "Failed to get memory usage"
        return 1
    fi
    
    echo "Memory usage: $usage%"
    
    # Check if usage is above threshold
    if [ "$usage" -gt "$threshold" ]; then
        log_warning "Memory usage is above threshold ($usage% > $threshold%)"
        return 2
    fi
    
    return 0
}

# Check CPU usage
check_cpu_usage() {
    local threshold="$1"
    
    # Default to 90% threshold
    if [ -z "$threshold" ]; then
        threshold=90
    fi
    
    log_info "Checking CPU usage"
    
    # Get CPU usage percentage
    local usage=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')
    
    if [ $? -ne 0 ]; then
        log_error "Failed to get CPU usage"
        return 1
    fi
    
    echo "CPU usage: $usage%"
    
    # Check if usage is above threshold
    if (( $(echo "$usage > $threshold" | bc -l) )); then
        log_warning "CPU usage is above threshold ($usage% > $threshold%)"
        return 2
    fi
    
    return 0
}

# Check port availability
check_port_availability() {
    local port="$1"
    local host="$2"
    
    # Default to localhost
    if [ -z "$host" ]; then
        host="localhost"
    fi
    
    log_info "Checking if port $port is available on $host"
    
    # Check if port is in use
    if nc -z "$host" "$port" 2> /dev/null; then
        log_info "Port $port is in use on $host"
        return 1
    else
        log_info "Port $port is available on $host"
        return 0
    fi
}

# Check URL availability
check_url_availability() {
    local url="$1"
    local timeout="$2"
    
    # Default to 5 seconds timeout
    if [ -z "$timeout" ]; then
        timeout=5
    fi
    
    log_info "Checking if URL $url is available"
    
    # Check if URL is available
    if curl --output /dev/null --silent --head --fail --max-time "$timeout" "$url"; then
        log_info "URL $url is available"
        return 0
    else
        log_info "URL $url is not available"
        return 1
    fi
}

# Check Docker container health
check_docker_container_health() {
    local container="$1"
    
    log_info "Checking health of Docker container $container"
    
    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "$container"; then
        log_error "Docker container $container does not exist"
        return 1
    fi
    
    # Check if container is running
    if ! docker ps --format '{{.Names}}' | grep -q "$container"; then
        log_warning "Docker container $container is not running"
        return 2
    fi
    
    # Check container health status
    local health=$(docker inspect --format='{{.State.Health.Status}}' "$container" 2> /dev/null)
    
    # If container has no health check
    if [ -z "$health" ] || [ "$health" = "<nil>" ]; then
        log_info "Docker container $container has no health check"
        return 0
    fi
    
    echo "Health status of Docker container $container: $health"
    
    # Check health status
    if [ "$health" = "healthy" ]; then
        return 0
    else
        log_warning "Docker container $container is not healthy: $health"
        return 2
    fi
}

# Get Docker container stats
get_docker_container_stats() {
    local container="$1"
    
    log_info "Getting stats for Docker container $container"
    
    # Check if container exists
    if ! docker ps -a --format '{{.Names}}' | grep -q "$container"; then
        log_error "Docker container $container does not exist"
        return 1
    fi
    
    # Get container stats
    docker stats --no-stream "$container"
    
    return $?
}

# Check Prometheus metrics
check_prometheus_metrics() {
    local url="$1"
    local query="$2"
    
    log_info "Checking Prometheus metrics at $url with query $query"
    
    # Check if curl is installed
    if ! command -v curl &> /dev/null; then
        log_error "curl is not installed. Please install it first."
        return 1
    fi
    
    # Check if jq is installed
    if ! command -v jq &> /dev/null; then
        log_error "jq is not installed. Please install it first."
        return 1
    fi
    
    # Query Prometheus
    local result=$(curl -s "$url/api/v1/query?query=$query" | jq -r '.data.result')
    
    if [ $? -ne 0 ]; then
        log_error "Failed to query Prometheus"
        return 1
    fi
    
    echo "Prometheus query result: $result"
    
    return 0
}

# Main function
main() {
    local command="$1"
    local arg1="$2"
    local arg2="$3"
    local arg3="$4"
    
    case "$command" in
        "check-service")
            check_service_status "$arg1" "$arg2"
            ;;
        "get-logs")
            get_service_logs "$arg1" "$arg2" "$arg3"
            ;;
        "check-disk")
            check_disk_usage "$arg1" "$arg2"
            ;;
        "check-memory")
            check_memory_usage "$arg1"
            ;;
        "check-cpu")
            check_cpu_usage "$arg1"
            ;;
        "check-port")
            check_port_availability "$arg1" "$arg2"
            ;;
        "check-url")
            check_url_availability "$arg1" "$arg2"
            ;;
        "check-container")
            check_docker_container_health "$arg1"
            ;;
        "container-stats")
            get_docker_container_stats "$arg1"
            ;;
        "check-prometheus")
            check_prometheus_metrics "$arg1" "$arg2"
            ;;
        *)
            echo "Usage: $0 [check-service|get-logs|check-disk|check-memory|check-cpu|check-port|check-url|check-container|container-stats|check-prometheus] [args...]"
            return 1
            ;;
    esac
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi