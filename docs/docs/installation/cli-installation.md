# CLI Installation and Usage

This guide provides detailed instructions for installing and using the Dev-Server CLI, which provides a unified interface for managing all components of the Dev-Server-Workflow ecosystem.

## Prerequisites

- Bash shell (Linux, macOS, or Windows with WSL)
- Python 3.9 or higher
- Docker and Docker Compose (for container management)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Add CLI to PATH

#### Linux/macOS

```bash
# Add to current session
export PATH=$PATH:$(pwd)/cli

# Add permanently to .bashrc or .zshrc
echo 'export PATH=$PATH:'$(pwd)'/cli' >> ~/.bashrc
source ~/.bashrc
```

#### Windows (PowerShell)

```powershell
# Add to current session
$env:Path += ";$(Get-Location)\cli"

# Add permanently
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$(Get-Location)\cli", "User")
```

### 3. Make the CLI Executable

```bash
chmod +x cli/dev-server.sh
```

### 4. Verify Installation

```bash
dev-server.sh help
```

## CLI Commands

### Help and Information

```bash
# Show help
dev-server.sh help

# Show status of all components
dev-server.sh status

# Show interactive menu
dev-server.sh menu
```

### Component Management

```bash
# Start a component
dev-server.sh start [component]

# Stop a component
dev-server.sh stop [component]

# Restart a component
dev-server.sh restart [component]

# View logs of a component
dev-server.sh logs [component]
```

Available components:
- `all`: All components
- `mcp`: MCP Server
- `n8n`: n8n Workflow Engine
- `ollama`: Ollama LLM Server
- `openhands`: OpenHands AI Agent
- `llamafile`: Llamafile LLM
- `shellgpt`: ShellGPT CLI

### Configuration

```bash
# Configure a component
dev-server.sh config [option] [value]
```

Configuration options:
- `llm-api-key [key]`: Set the LLM API key
- `github-token [token]`: Set the GitHub token
- `openproject-token [token]`: Set the OpenProject token
- `n8n-api-key [key]`: Set the n8n API key
- `workspace-path [path]`: Set the workspace path

### Installation and Updates

```bash
# Install a component
dev-server.sh install [component]

# Update a component
dev-server.sh update [component]

# Switch between LLMs
dev-server.sh switch-llm [llm]
```

Available LLMs:
- `llamafile`: Local Llamafile LLM
- `claude`: Anthropic Claude API
- `openai`: OpenAI API

### Backup and Restore

```bash
# Create a backup
dev-server.sh backup [component]

# Restore from backup
dev-server.sh restore [backup]
```

### AI Commands

```bash
# Execute an AI command
dev-server.sh ai [prompt]
```

## Examples

### Basic Usage

```bash
# Start all components
dev-server.sh start all

# Check status
dev-server.sh status

# Stop n8n
dev-server.sh stop n8n

# View MCP logs
dev-server.sh logs mcp
```

### Advanced Usage

```bash
# Install OpenHands
dev-server.sh install openhands

# Configure GitHub token
dev-server.sh config github-token ghp_your_token

# Switch to Claude LLM
dev-server.sh switch-llm claude

# Create a backup of n8n
dev-server.sh backup n8n

# Ask AI for help
dev-server.sh ai "How do I create a new n8n workflow?"
```

## Customizing the CLI

You can customize the CLI by editing the following files:

- `cli/dev-server.sh`: Main CLI script
- `cli/config.sh`: Configuration variables
- `cli/functions.sh`: Helper functions
- `cli/menu.sh`: Interactive menu

### Adding a New Command

1. Edit `cli/dev-server.sh`:

```bash
# Add to the case statement
case "$command" in
    # ... existing commands ...
    
    your-command)
        your_command_function "$@"
        ;;
esac
```

2. Add the function to `cli/functions.sh`:

```bash
your_command_function() {
    echo "Executing your command..."
    # Your command implementation
}
```

3. Add help text to the help function in `cli/dev-server.sh`.

## Troubleshooting

### Command Not Found

If you get "command not found" when running `dev-server.sh`:

1. Make sure the script is executable:
   ```bash
   chmod +x cli/dev-server.sh
   ```

2. Make sure the CLI directory is in your PATH:
   ```bash
   echo $PATH | grep cli
   ```

### Permission Denied

If you get "permission denied" when running Docker commands:

1. Add your user to the Docker group:
   ```bash
   sudo usermod -aG docker $USER
   ```

2. Log out and log back in, or run:
   ```bash
   newgrp docker
   ```

### Component Not Starting

If a component doesn't start:

1. Check the logs:
   ```bash
   dev-server.sh logs [component]
   ```

2. Check if the ports are already in use:
   ```bash
   netstat -tuln | grep [port]
   ```

3. Check if Docker is running:
   ```bash
   docker info
   ```