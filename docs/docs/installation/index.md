# Installation Guide

This guide provides detailed instructions for installing and configuring the Dev-Server-Workflow components.

## Prerequisites

Before you begin, ensure you have the following prerequisites installed:

- **Docker**: Version 20.10.0 or higher
- **Docker Compose**: Version 1.29.0 or higher
- **Python**: Version 3.9 or higher
- **Git**: Version 2.25.0 or higher

## Quick Start

For a quick start with default settings, run:

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
cp src/env-template .env
# Edit .env file with your configuration
./docker-start.sh start
```

## Detailed Installation

For a more detailed installation, follow the guides for each component:

- [MCP Ecosystem Installation](./mcp-ecosystem.md)
- [MCP Servers Installation](./mcp-servers.md)
- [n8n Workflow Installation](./n8n-workflow.md)
- [OpenHands Integration](./openhands-integration.md)
- [CLI Installation](./cli-installation.md)

## Verifying Installation

To verify your installation:

```bash
# Test the setup
python setup.py test

# Check the status of all components
./cli/dev-server.sh status
```

## Troubleshooting

If you encounter issues during installation, see the [Troubleshooting Guide](../troubleshooting/index.md).