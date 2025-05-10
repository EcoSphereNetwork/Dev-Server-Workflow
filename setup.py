#!/usr/bin/env python3

import os
import sys
import argparse
import logging
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("setup")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Setup script for Dev-Server-Workflow')
    
    # Main commands
    parser.add_argument('command', choices=['install', 'test', 'uninstall'], 
                        help='Command to execute')
    
    # Options
    parser.add_argument('--env-file', type=str, default='.env',
                        help='Path to environment file')
    parser.add_argument('--workflows', nargs='+', 
                        choices=['github', 'document', 'openhands', 'mcp', 'all'],
                        default=['all'],
                        help='Workflows to install')
    parser.add_argument('--mcp', action='store_true',
                        help='Install MCP integration')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Enable verbose output')
    
    return parser.parse_args()

def load_env_file(env_file: str) -> Dict[str, str]:
    """Load environment variables from file."""
    env_vars = {}
    
    if not os.path.exists(env_file):
        logger.warning(f"Environment file {env_file} not found. Using default values.")
        return env_vars
    
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            key, value = line.split('=', 1)
            env_vars[key] = value
    
    return env_vars

def install_dependencies():
    """Install required dependencies."""
    logger.info("Installing dependencies...")
    
    try:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])
        logger.info("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install dependencies: {e}")
        sys.exit(1)

def install_workflows(workflows: List[str], env_vars: Dict[str, str]):
    """Install selected workflows."""
    if 'all' in workflows:
        workflows = ['github', 'document', 'openhands', 'mcp']
    
    logger.info(f"Installing workflows: {', '.join(workflows)}")
    
    # Import the main setup module
    sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
    
    try:
        from n8n_setup_main import setup_workflows
        
        # Convert env_vars to the format expected by setup_workflows
        config = {
            'env_file': env_vars,
            'workflows': workflows
        }
        
        setup_workflows(config)
        logger.info("Workflows installed successfully.")
    except ImportError as e:
        logger.error(f"Failed to import setup module: {e}")
        logger.info("Make sure you're running this script from the repository root.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to install workflows: {e}")
        sys.exit(1)

def install_mcp(env_vars: Dict[str, str]):
    """Install MCP integration."""
    logger.info("Installing MCP integration...")
    
    try:
        # Run the MCP setup script
        subprocess.check_call(['./scripts/mcp/install-mcp.sh'])
        
        # Generate MCP configuration for OpenHands
        from n8n_setup_workflows_mcp import generate_openhands_config
        
        config = generate_openhands_config(env_vars)
        
        with open('openhands-mcp-config.json', 'w') as f:
            import json
            json.dump(config, f, indent=2)
            
        logger.info("MCP integration installed successfully.")
        logger.info("OpenHands MCP configuration generated at openhands-mcp-config.json")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install MCP integration: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to generate OpenHands configuration: {e}")
        sys.exit(1)

def run_tests():
    """Run tests."""
    logger.info("Running tests...")
    
    try:
        subprocess.check_call(['./run_tests.sh'])
        logger.info("Tests completed successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Tests failed: {e}")
        sys.exit(1)

def uninstall():
    """Uninstall the application."""
    logger.info("Uninstalling Dev-Server-Workflow...")
    
    try:
        # Stop any running containers
        subprocess.check_call(['./docker-start.sh', 'stop'])
        
        # Remove Docker volumes
        subprocess.check_call(['docker', 'volume', 'rm', 'dev-server-workflow_n8n_data',
                              'dev-server-workflow_prometheus_data', 'dev-server-workflow_grafana_data'])
        
        logger.info("Dev-Server-Workflow uninstalled successfully.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to uninstall: {e}")
        sys.exit(1)

def main():
    """Main function."""
    args = parse_arguments()
    
    # Set log level
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # Load environment variables
    env_vars = load_env_file(args.env_file)
    
    # Execute command
    if args.command == 'install':
        install_dependencies()
        install_workflows(args.workflows, env_vars)
        if args.mcp:
            install_mcp(env_vars)
    elif args.command == 'test':
        run_tests()
    elif args.command == 'uninstall':
        uninstall()

if __name__ == '__main__':
    main()