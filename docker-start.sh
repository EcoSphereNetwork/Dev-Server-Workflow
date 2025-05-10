#!/bin/bash

# Docker Start Script for Dev-Server-Workflow
# This script manages Docker containers for the Dev-Server-Workflow project

set -e

# Default values
ENV_FILE=".env"
COMPOSE_FILE="docker-compose.yml"
COMPOSE_FILE_PRODUCTION="docker-compose.production.yml"
COMPOSE_FILE_WEB_UI="docker-compose.web-ui.yml"

# Function to display help
function show_help {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  start           Start all containers"
    echo "  stop            Stop all containers"
    echo "  restart         Restart all containers"
    echo "  status          Show status of containers"
    echo "  logs [service]  Show logs for all or specific service"
    echo "  setup           Run setup for n8n workflows"
    echo "  build           Build containers"
    echo "  help            Show this help message"
    echo ""
    echo "Environment:"
    echo "  --env-file      Specify custom .env file (default: .env)"
    echo "  --production    Use production configuration"
    echo "  --web-ui        Start only the web UI"
    echo ""
}

# Function to check if .env file exists, create if not
function check_env_file {
    if [ ! -f "$ENV_FILE" ]; then
        echo "No $ENV_FILE file found. Creating from template..."
        if [ -f "src/env-template" ]; then
            cp src/env-template "$ENV_FILE"
            echo "Created $ENV_FILE from template. Please edit it with your configuration."
            exit 1
        else
            echo "Error: Could not find env-template. Please create $ENV_FILE manually."
            exit 1
        fi
    fi
}

# Function to start containers
function start_containers {
    echo "Starting containers..."
    if [ "$USE_PRODUCTION" = true ]; then
        docker-compose -f "$COMPOSE_FILE_PRODUCTION" --env-file "$ENV_FILE" up -d
    elif [ "$USE_WEB_UI" = true ]; then
        docker-compose -f "$COMPOSE_FILE_WEB_UI" --env-file "$ENV_FILE" up -d
    else
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" up -d
    fi
    echo "Containers started successfully."
}

# Function to stop containers
function stop_containers {
    echo "Stopping containers..."
    if [ "$USE_PRODUCTION" = true ]; then
        docker-compose -f "$COMPOSE_FILE_PRODUCTION" --env-file "$ENV_FILE" down
    elif [ "$USE_WEB_UI" = true ]; then
        docker-compose -f "$COMPOSE_FILE_WEB_UI" --env-file "$ENV_FILE" down
    else
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" down
    fi
    echo "Containers stopped successfully."
}

# Function to show container status
function show_status {
    echo "Container status:"
    if [ "$USE_PRODUCTION" = true ]; then
        docker-compose -f "$COMPOSE_FILE_PRODUCTION" --env-file "$ENV_FILE" ps
    elif [ "$USE_WEB_UI" = true ]; then
        docker-compose -f "$COMPOSE_FILE_WEB_UI" --env-file "$ENV_FILE" ps
    else
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" ps
    fi
}

# Function to show logs
function show_logs {
    if [ -z "$1" ]; then
        # Show logs for all services
        if [ "$USE_PRODUCTION" = true ]; then
            docker-compose -f "$COMPOSE_FILE_PRODUCTION" --env-file "$ENV_FILE" logs --tail=100 -f
        elif [ "$USE_WEB_UI" = true ]; then
            docker-compose -f "$COMPOSE_FILE_WEB_UI" --env-file "$ENV_FILE" logs --tail=100 -f
        else
            docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs --tail=100 -f
        fi
    else
        # Show logs for specific service
        if [ "$USE_PRODUCTION" = true ]; then
            docker-compose -f "$COMPOSE_FILE_PRODUCTION" --env-file "$ENV_FILE" logs --tail=100 -f "$1"
        elif [ "$USE_WEB_UI" = true ]; then
            docker-compose -f "$COMPOSE_FILE_WEB_UI" --env-file "$ENV_FILE" logs --tail=100 -f "$1"
        else
            docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" logs --tail=100 -f "$1"
        fi
    fi
}

# Function to run setup
function run_setup {
    echo "Running setup..."
    docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" exec n8n python /app/src/n8n_setup_main.py --install --env-file /app/.env
    echo "Setup completed."
}

# Function to build containers
function build_containers {
    echo "Building containers..."
    if [ "$USE_PRODUCTION" = true ]; then
        docker-compose -f "$COMPOSE_FILE_PRODUCTION" --env-file "$ENV_FILE" build
    elif [ "$USE_WEB_UI" = true ]; then
        docker-compose -f "$COMPOSE_FILE_WEB_UI" --env-file "$ENV_FILE" build
    else
        docker-compose -f "$COMPOSE_FILE" --env-file "$ENV_FILE" build
    fi
    echo "Build completed."
}

# Parse command line arguments
USE_PRODUCTION=false
USE_WEB_UI=false
COMMAND=""
SERVICE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --env-file)
            ENV_FILE="$2"
            shift 2
            ;;
        --production)
            USE_PRODUCTION=true
            shift
            ;;
        --web-ui)
            USE_WEB_UI=true
            shift
            ;;
        start|stop|restart|status|logs|setup|build|help)
            COMMAND="$1"
            shift
            ;;
        *)
            # Assume this is a service name for logs
            if [ "$COMMAND" = "logs" ]; then
                SERVICE="$1"
            else
                echo "Unknown option: $1"
                show_help
                exit 1
            fi
            shift
            ;;
    esac
done

# Check if command is provided
if [ -z "$COMMAND" ]; then
    show_help
    exit 1
fi

# Execute command
case "$COMMAND" in
    help)
        show_help
        ;;
    start)
        check_env_file
        start_containers
        ;;
    stop)
        check_env_file
        stop_containers
        ;;
    restart)
        check_env_file
        stop_containers
        start_containers
        ;;
    status)
        check_env_file
        show_status
        ;;
    logs)
        check_env_file
        show_logs "$SERVICE"
        ;;
    setup)
        check_env_file
        run_setup
        ;;
    build)
        check_env_file
        build_containers
        ;;
    *)
        echo "Unknown command: $COMMAND"
        show_help
        exit 1
        ;;
esac

exit 0