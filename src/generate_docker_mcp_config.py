#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Konfiguriere Logging
logger = setup_logging("INFO")

# Lade Konfiguration
config_manager = ConfigManager()
config = config_manager.load_env_file(".env")

"""
Generate OpenHands MCP configuration for Docker MCP server.

This script generates the configuration for the Docker MCP server to be used with OpenHands.
"""

import os
import json
import argparse
import sys


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Generate OpenHands MCP configuration for Docker MCP server')
    parser.add_argument('--output', '-o', default='-',
                        help='Output file (default: stdout)')
    parser.add_argument('--script-path', default=None,
                        help='Path to the Docker MCP server script (default: auto-detect)')
    parser.add_argument('--port', type=int, default=3334,
                        help='Port for the Docker MCP server (default: 3334)')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Determine script path
    if args.script_path:
        script_path = args.script_path
    else:
        # Auto-detect script path
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script_path = os.path.join(script_dir, 'docker_mcp_server.py')
    
    # Create configuration
    config = {
        "mcpServers": {
            "docker-mcp": {
                "command": "python3",
                "args": [script_path],
                "env": {
                    "DOCKER_MCP_PORT": str(args.port),
                    "LOG_LEVEL": "INFO",
                    "MCP_AUTH_SECRET": "your_secret_key_here"
                },
                "autoApprove": [
                    "list-containers",
                    "get-logs",
                    "network-list",
                    "compose-ps",
                    "compose-logs"
                ],
                "metadata": {
                    "authorization": "username:timestamp:signature"
                }
            }
        }
    }
    
    # Add authentication instructions
    print("# Authentication Instructions", file=sys.stderr)
    print("# --------------------------", file=sys.stderr)
    print("# To authenticate with the Docker MCP server, use the authenticate prompt:", file=sys.stderr)
    print("#", file=sys.stderr)
    print("# Default credentials:", file=sys.stderr)
    print("#   Username: admin", file=sys.stderr)
    print("#   API Key: admin_api_key", file=sys.stderr)
    print("#", file=sys.stderr)
    print("# The server will return a token that you can use to authenticate requests.", file=sys.stderr)
    print("# Add the token to the metadata.authorization field in the configuration.", file=sys.stderr)
    print("#", file=sys.stderr)
    
    # Output configuration
    if args.output == '-':
        json.dump(config, sys.stdout, indent=2)
        print()  # Add newline
    else:
        with open(args.output, 'w') as f:
            json.dump(config, f, indent=2)
        print(f"Configuration written to {args.output}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())