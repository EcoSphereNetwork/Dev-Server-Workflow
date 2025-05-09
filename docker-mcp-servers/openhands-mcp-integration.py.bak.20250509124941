#!/usr/bin/env python3

import json
import sys
import os
import argparse
import shutil

def integrate_with_openhands(config_path, openhands_config_dir):
    """Integrate the MCP servers with OpenHands."""
    print("Integrating MCP servers with OpenHands...")
    
    # Load the MCP configuration
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return False
    
    # Create the OpenHands configuration directory if it doesn't exist
    os.makedirs(openhands_config_dir, exist_ok=True)
    
    # Copy the configuration file to the OpenHands configuration directory
    try:
        dest_path = os.path.join(openhands_config_dir, "mcp-config.json")
        shutil.copy(config_path, dest_path)
        print(f"✅ MCP configuration copied to {dest_path}")
    except Exception as e:
        print(f"❌ Error copying configuration: {e}")
        return False
    
    # Create a script to start the MCP servers
    start_script_path = os.path.join(openhands_config_dir, "start-mcp-servers.sh")
    try:
        with open(start_script_path, "w") as f:
            f.write("""#!/bin/bash

# Script to start the MCP servers for OpenHands

# Change to the MCP servers directory
cd /workspace/Dev-Server-Workflow/docker-mcp-servers

# Start the MCP servers
./start-mcp-servers.sh

# Wait for the servers to start
sleep 5

# Test the MCP servers
./test-mcp-servers.py

echo "MCP servers are ready for OpenHands!"
""")
        
        # Make the script executable
        os.chmod(start_script_path, 0o755)
        print(f"✅ Start script created at {start_script_path}")
    except Exception as e:
        print(f"❌ Error creating start script: {e}")
        return False
    
    print("MCP servers have been integrated with OpenHands! 🎉")
    print(f"To start the MCP servers, run: {start_script_path}")
    return True

def main():
    parser = argparse.ArgumentParser(description="Integrate MCP servers with OpenHands")
    parser.add_argument("--config", default="openhands-mcp-config.json", help="Path to the MCP configuration file")
    parser.add_argument("--openhands-config-dir", default=os.environ.get("OPENHANDS_CONFIG_DIR", "/workspace/openhands-config"), help="OpenHands configuration directory")
    
    args = parser.parse_args()
    
    if integrate_with_openhands(args.config, args.openhands_config_dir):
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == "__main__":
    main()