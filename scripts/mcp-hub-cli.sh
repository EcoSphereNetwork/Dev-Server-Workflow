#!/bin/bash

# Script to run the MCP Hub CLI

set -e

# Get the repository root directory
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Run the MCP Hub CLI
cd "$REPO_ROOT"
python -m src.mcp_hub.cli_new "$@"