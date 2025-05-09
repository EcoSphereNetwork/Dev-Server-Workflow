# Architecture

This document describes the architecture of the Dev-Server-Workflow project.

## Overview

The Dev-Server-Workflow project is a comprehensive solution for integrating n8n workflows, MCP servers, and OpenHands for AI-assisted automation of development processes.

The architecture is designed to be modular, extensible, and maintainable, with a focus on standardization and reusability.

## Components

### MCP Servers

MCP (Model Context Protocol) servers provide tools to clients via a standardized interface. Each MCP server implements the `MCPServerInterface` and extends the `BaseMCPServer` class.

The following MCP servers are currently implemented:

- **n8n MCP Server**: Provides n8n workflows as MCP tools
- **OpenHands MCP Server**: Enables parallel execution of OpenHands tasks
- **Docker MCP Server**: Manages Docker containers via MCP
- **Generator MCP Server**: Generates dynamic MCP servers

### n8n Integration

n8n is a workflow automation platform that allows you to create and run workflows. The Dev-Server-Workflow project integrates n8n to provide workflow automation capabilities.

The n8n integration includes:

- **Workflow Definitions**: Predefined workflows for common tasks
- **Setup Scripts**: Scripts for installing and configuring n8n
- **MCP Integration**: Integration of n8n with the MCP protocol

### OpenHands Integration

OpenHands is a platform for AI-assisted automation. The Dev-Server-Workflow project integrates OpenHands to provide AI-assisted automation capabilities.

The OpenHands integration includes:

- **MCP Server**: MCP server for OpenHands
- **Configuration**: Configuration files for OpenHands
- **Examples**: Examples of using OpenHands with MCP

### CLI Tools

The CLI tools provide a command-line interface for managing the system:

- **Main Interface**: `dev-server-cli.sh`
- **Interactive UI**: `cli/interactive_ui.sh`
- **AI Assistant**: `cli/ai_assistant_improved.sh`
- **Configuration Management**: `cli/config_manager.sh`
- **Error Handling**: `cli/error_handler.sh`

### Common Libraries

The common libraries provide standardized functions and classes for all components:

- **Shell Library**: `scripts/common/shell/common.sh`
- **Python Library**: `scripts/common/python/common.py`

## Architecture Diagram

```
+----------------------------------+
|           CLI Tools              |
|  +----------------------------+  |
|  |     dev-server-cli.sh      |  |
|  +----------------------------+  |
|  |    interactive_ui.sh       |  |
|  +----------------------------+  |
|  |  ai_assistant_improved.sh  |  |
|  +----------------------------+  |
+----------------------------------+
              |
              v
+----------------------------------+
|        Common Libraries          |
|  +----------------------------+  |
|  |        common.sh           |  |
|  +----------------------------+  |
|  |        common.py           |  |
|  +----------------------------+  |
+----------------------------------+
              |
              v
+----------------------------------+
|          MCP Servers             |
|  +----------------------------+  |
|  |     n8n MCP Server         |  |
|  +----------------------------+  |
|  |   OpenHands MCP Server     |  |
|  +----------------------------+  |
|  |    Docker MCP Server       |  |
|  +----------------------------+  |
|  |   Generator MCP Server     |  |
|  +----------------------------+  |
+----------------------------------+
              |
              v
+----------------------------------+
|        External Services         |
|  +----------------------------+  |
|  |           n8n              |  |
|  +----------------------------+  |
|  |        OpenHands           |  |
|  +----------------------------+  |
|  |          Docker            |  |
|  +----------------------------+  |
+----------------------------------+
```

## Code Organization

### Directory Structure

```
Dev-Server-Workflow/
├── cli/                    # CLI tools
├── config/                 # Configuration files
├── data/                   # Data files
├── docker-mcp-servers/     # Docker Compose configuration
├── docs/                   # Documentation
│   └── docs/
│       ├── dev/            # Developer documentation
│       ├── user/           # User documentation
│       └── api/            # API documentation
├── logs/                   # Log files
├── scripts/                # Scripts
│   ├── common/             # Common libraries
│   │   ├── python/         # Python libraries
│   │   │   ├── core/       # Core modules
│   │   │   └── utils/      # Utility modules
│   │   └── shell/          # Shell libraries
│   └── mcp/                # MCP-specific scripts
├── src/                    # Source code
│   ├── mcp/                # MCP server implementations
│   │   ├── interfaces/     # MCP interfaces
│   │   └── base_mcp_server_improved.py # Base MCP server
│   └── openhands/          # OpenHands integration
└── tests/                  # Tests
    ├── mcp/                # MCP server tests
    └── openhands/          # OpenHands tests
```

### Module Dependencies

```
+------------------+
|    CLI Tools     |
+------------------+
        |
        v
+------------------+
| Common Libraries |
+------------------+
        |
        v
+------------------+
|   MCP Servers    |
+------------------+
        |
        v
+------------------+
|External Services |
+------------------+
```

## Design Principles

### Modularity

The architecture is designed to be modular, with each component having a well-defined interface and responsibility. This allows for easy extension and maintenance.

### Standardization

The architecture uses standardized interfaces and protocols to ensure interoperability between components. This includes the Model Context Protocol (MCP) for communication between MCP servers and clients.

### Reusability

Common functionality is extracted into reusable libraries to avoid duplication and ensure consistency across the codebase.

### Testability

The architecture is designed to be testable, with clear separation of concerns and dependency injection to facilitate unit testing.

### Security

Security is a key consideration in the architecture, with proper authentication and authorization mechanisms in place to protect sensitive data and operations.

## Future Directions

### Additional MCP Servers

The architecture is designed to be extensible, allowing for the addition of new MCP servers to provide additional functionality.

### Enhanced Web UI

A web-based user interface is planned to provide a more user-friendly way to manage the system.

### Deeper OpenHands Integration

Further integration with OpenHands is planned to provide more advanced AI-assisted automation capabilities.

### LLM Cost Estimation

Integration with LLM cost estimation tools is planned to provide insights into the cost of AI-assisted automation.