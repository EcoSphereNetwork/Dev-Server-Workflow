# Prompt MCP Server

A Model Context Protocol (MCP) server for prompt engineering with templates, memory, and pre-prompts. This server automatically selects the appropriate LLM based on task complexity, using both local and cloud LLMs for optimal cost-efficiency. 

## Features

- **Prompt Templates**: Reusable prompt templates with Jinja2 syntax
- **Memory Management**: Conversation history and context management
- **Pre-Prompts**: System prompts and instructions that can be applied before user input
- **User Input Optimization**: Automatic improvement of user inputs to follow best practices
- **Automatic LLM Selection**: Selects the most appropriate LLM based on task complexity
- **Cost Optimization**: Uses local LLMs for simple tasks and cloud LLMs for complex tasks
- **API Endpoints**: RESTful API for interacting with the server

## Architecture

The Prompt MCP Server consists of the following components:

1. **Template Manager**: Manages prompt templates and their rendering
2. **Memory Manager**: Handles conversation history and context
3. **Pre-Prompt Manager**: Manages system prompts and instructions
4. **Input Optimizer**: Improves user inputs to follow best practices
5. **LLM Selector**: Selects the appropriate LLM based on task complexity
6. **API Server**: Provides RESTful API endpoints for interacting with the server

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/prompt-mcp-server.git
cd prompt-mcp-server

# Install dependencies
poetry install

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys and configuration
```

## Usage

```bash
# Start the server
poetry run python -m prompt_mcp_server

# Or with uvicorn directly
poetry run uvicorn prompt_mcp_server.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

- `POST /api/v1/chat`: Send a message to the chat endpoint
- `GET /api/v1/templates`: List available templates
- `POST /api/v1/templates`: Create a new template
- `GET /api/v1/templates/{template_id}`: Get a specific template
- `PUT /api/v1/templates/{template_id}`: Update a template
- `DELETE /api/v1/templates/{template_id}`: Delete a template
- `GET /api/v1/models`: List available LLM models
- `GET /api/v1/health`: Check server health

## Configuration

The server can be configured using environment variables or a `.env` file:

```
# API Keys
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key

# LLM Configuration
DEFAULT_MODEL=gpt-3.5-turbo
USE_LOCAL_MODELS=true
LOCAL_MODEL_ENDPOINT=http://localhost:8080/v1

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=false

# Memory Configuration
MEMORY_TYPE=redis  # redis, in_memory, chroma
REDIS_URL=redis://localhost:6379/0
```

## License

MIT
