# Developer Setup Guide

This guide will help you set up your development environment for the Dev-Server-Workflow project.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose
- Git
- Node.js and npm (for n8n)

## Clone the Repository

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

## Set Up Python Environment

It's recommended to use a virtual environment for Python development:

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
# On Linux/macOS
source venv/bin/activate
# On Windows
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Set Up Environment Variables

Create a `.env` file in the root directory of the project:

```bash
# Create .env file
cp .env.example .env

# Edit the .env file
nano .env
```

Fill in the required environment variables:

```
# n8n Configuration
N8N_URL=http://localhost:5678
N8N_API_KEY=your-api-key

# OpenHands Configuration
OPENHANDS_PORT=3000
OPENHANDS_API_KEY=your-api-key

# MCP Server Configuration
MCP_HTTP_PORT=3333
MCP_AUTH_TOKEN=your-auth-token

# LLM Configuration
LLM_API_KEY=your-api-key
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
```

## Start the Services

### Start n8n

```bash
# Start n8n
./scripts/start-n8n.sh
```

### Start MCP Servers

```bash
# Start all MCP servers
./scripts/start-all-mcp-servers.sh --http
```

### Start OpenHands

```bash
# Start OpenHands
./scripts/start-openhands.sh
```

## Development Workflow

### Directory Structure

- `src/`: Source code
  - `mcp/`: MCP server implementations
  - `openhands/`: OpenHands integration
- `scripts/`: Scripts for starting and managing services
  - `common/`: Common libraries for scripts
  - `mcp/`: MCP-specific scripts
- `docs/`: Documentation
  - `docs/dev/`: Developer documentation
  - `docs/user/`: User documentation
- `tests/`: Tests
- `docker-mcp-servers/`: Docker Compose configuration for MCP servers

### Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) for Python code
- Use [Google Style Guide](https://google.github.io/styleguide/shellguide.html) for shell scripts
- Document your code with docstrings and comments
- Write tests for your code

### Git Workflow

1. Create a new branch for your feature or bug fix:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and commit them:

```bash
git add .
git commit -m "Description of your changes"
```

3. Push your changes to the remote repository:

```bash
git push origin feature/your-feature-name
```

4. Create a pull request on GitHub

### Running Tests

```bash
# Run all tests
python -m unittest discover

# Run specific tests
python -m unittest tests.test_module
```

## Debugging

### Logs

Logs are stored in the `logs/` directory:

```bash
# View logs
cat logs/mcp-server.log

# Follow logs
tail -f logs/mcp-server.log
```

### Debugging MCP Servers

You can run MCP servers in debug mode:

```bash
# Run n8n MCP server in debug mode
python src/mcp/n8n_mcp_server_improved.py --log-level debug
```

### Debugging n8n Workflows

You can debug n8n workflows using the n8n web interface:

1. Open http://localhost:5678
2. Go to the workflow you want to debug
3. Click on the "Debug" button

## Building Documentation

The documentation is built using [MkDocs](https://www.mkdocs.org/):

```bash
# Install MkDocs
pip install mkdocs

# Build documentation
mkdocs build

# Serve documentation locally
mkdocs serve
```

## Troubleshooting

### Common Issues

#### Docker Compose Issues

If you encounter issues with Docker Compose, try the following:

```bash
# Stop all containers
docker-compose down

# Remove all containers
docker-compose rm -f

# Start containers again
docker-compose up -d
```

#### n8n Issues

If n8n is not working properly, try the following:

```bash
# Restart n8n
./scripts/stop-n8n.sh
./scripts/start-n8n.sh
```

#### MCP Server Issues

If MCP servers are not working properly, try the following:

```bash
# Restart MCP servers
./scripts/stop-all-mcp-servers.sh
./scripts/start-all-mcp-servers.sh --http
```

### Getting Help

If you need help, you can:

- Open an issue on GitHub
- Contact the project maintainers
- Check the documentation