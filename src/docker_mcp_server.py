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
Docker MCP Server

This script starts the Docker MCP server, which provides a Model Context Protocol (MCP)
interface for Docker operations, enabling AI agents to manage Docker containers and
Docker Compose stacks.
"""

import os
import sys
import argparse
import logging
from mcp_servers.docker_mcp.server import main as run_server

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '../logs/docker_mcp.log'))
    ]
)
logger = logging.getLogger("docker-mcp-server")


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Docker MCP Server')
    parser.add_argument('--log-level', default='INFO',
                        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
                        help='Set the logging level')
    return parser.parse_args()


def main():
    """Main entry point."""
    args = parse_args()
    
    # Set log level
    logging.getLogger().setLevel(getattr(logging, args.log_level))
    
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.join(os.path.dirname(__file__), '../logs'), exist_ok=True)
    
    logger.info("Starting Docker MCP server")
    
    try:
        run_server()
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running server: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())