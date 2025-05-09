#!/bin/bash

# Source common functions
source "$(dirname "$0")/functions.sh"

# AI Assistant functions

# Process a natural language command
process_nl_command() {
    local command="$1"
    
    log_info "Processing command: $command"
    
    # Check if OpenAI API key is set
    if [ -z "$OPENAI_API_KEY" ]; then
        log_error "OpenAI API key is not set. Please set it in the configuration."
        return 1
    fi
    
    # Prepare the prompt
    local prompt="You are a CLI assistant for the Dev-Server-Workflow project. Your task is to translate the following natural language command into a specific CLI command using the dev-server.sh script.

Available commands:
- status: Show the status of all components
- start [component]: Start a component
- stop [component]: Stop a component
- restart [component]: Restart a component
- logs [component]: Show logs of a component
- config [option] [value]: Configure an option
- list [resource_type]: List available resources
- install [component]: Install a component
- switch-llm [llm]: Switch between LLMs (llamafile, claude)
- update [component]: Update a component
- package [action] [package] [manager] [options]: Package management
- configure [action] [file] [key] [value] [extra]: Configuration management
- monitor [action] [args...]: Monitoring functions

Components: all, mcp, n8n-mcp, docker-mcp, n8n, ollama, openhands, llamafile, monitoring

User command: $command

Respond with ONLY the exact CLI command to execute, nothing else."
    
    # Call the OpenAI API
    local response=$(curl -s -X POST https://api.openai.com/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -d "{
            \"model\": \"gpt-3.5-turbo\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}],
            \"temperature\": 0.2,
            \"max_tokens\": 100
        }" | jq -r '.choices[0].message.content')
    
    if [ $? -ne 0 ] || [ -z "$response" ]; then
        log_error "Failed to get response from OpenAI API"
        return 1
    fi
    
    log_info "Translated command: $response"
    
    # Extract the command
    local cli_command=$(echo "$response" | tr -d '\r\n')
    
    # Check if the command starts with "dev-server"
    if [[ "$cli_command" == dev-server* ]]; then
        # Remove "dev-server" prefix
        cli_command=${cli_command#dev-server}
        cli_command=${cli_command# }
    fi
    
    # Execute the command
    log_info "Executing command: ./dev-server.sh $cli_command"
    ./dev-server.sh $cli_command
    
    return $?
}

# Process a natural language question
process_nl_question() {
    local question="$1"
    
    log_info "Processing question: $question"
    
    # Check if OpenAI API key is set
    if [ -z "$OPENAI_API_KEY" ]; then
        log_error "OpenAI API key is not set. Please set it in the configuration."
        return 1
    fi
    
    # Prepare the prompt
    local prompt="You are a CLI assistant for the Dev-Server-Workflow project. Your task is to answer the following question about the project.

The Dev-Server-Workflow project includes:
- CLI framework for managing components
- MCP servers (n8n MCP, Docker MCP)
- Monitoring stack (Prometheus, Grafana, Alertmanager)
- LLM integration (Llamafile, Claude, Ollama)
- Package management
- Configuration management
- Monitoring functions

User question: $question

Provide a concise and helpful answer."
    
    # Call the OpenAI API
    local response=$(curl -s -X POST https://api.openai.com/v1/chat/completions \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $OPENAI_API_KEY" \
        -d "{
            \"model\": \"gpt-3.5-turbo\",
            \"messages\": [{\"role\": \"user\", \"content\": \"$prompt\"}],
            \"temperature\": 0.7,
            \"max_tokens\": 500
        }" | jq -r '.choices[0].message.content')
    
    if [ $? -ne 0 ] || [ -z "$response" ]; then
        log_error "Failed to get response from OpenAI API"
        return 1
    fi
    
    # Print the response
    echo -e "${GREEN}AI Assistant:${NC}"
    echo -e "$response"
    
    return 0
}

# Main function
main() {
    local input="$1"
    
    # Check if input is a question or a command
    if [[ "$input" == *"?"* ]]; then
        process_nl_question "$input"
    else
        process_nl_command "$input"
    fi
}

# Run main function if script is executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi