#!/bin/bash

# Source common functions
source "$(dirname "$0")/functions.sh"

# Start monitoring stack
start_monitoring_stack() {
    log_info "Starting monitoring stack..."
    start_monitoring
}

# Stop monitoring stack
stop_monitoring_stack() {
    log_info "Stopping monitoring stack..."
    stop_monitoring
}

# Main function
main() {
    local command="$1"
    
    case "$command" in
        "start")
            start_monitoring_stack
            ;;
        "stop")
            stop_monitoring_stack
            ;;
        "restart")
            stop_monitoring_stack
            start_monitoring_stack
            ;;
        *)
            echo "Usage: $0 [start|stop|restart]"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"