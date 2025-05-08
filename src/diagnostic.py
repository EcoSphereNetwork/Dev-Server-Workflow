#!/usr/bin/env python3
"""
Diagnostic tool for the Dev-Server-Workflow ecosystem.

This script checks the status of all components and provides troubleshooting information.
"""

import os
import sys
import json
import subprocess
import platform
import socket
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# ANSI colors for terminal output
GREEN = "\033[0;32m"
YELLOW = "\033[1;33m"
RED = "\033[0;31m"
BLUE = "\033[0;34m"
PURPLE = "\033[0;35m"
CYAN = "\033[0;36m"
NC = "\033[0m"  # No Color

def print_header(text: str) -> None:
    """Print a header with formatting."""
    print(f"\n{BLUE}{'=' * 40}{NC}")
    print(f"{BLUE}{text}{NC}")
    print(f"{BLUE}{'=' * 40}{NC}\n")

def print_success(text: str) -> None:
    """Print a success message."""
    print(f"{GREEN}✓ {text}{NC}")

def print_warning(text: str) -> None:
    """Print a warning message."""
    print(f"{YELLOW}⚠ {text}{NC}")

def print_error(text: str) -> None:
    """Print an error message."""
    print(f"{RED}✗ {text}{NC}")

def print_info(text: str) -> None:
    """Print an info message."""
    print(f"{CYAN}ℹ {text}{NC}")

def check_command(command: str) -> bool:
    """Check if a command is available."""
    try:
        subprocess.run(
            ["which", command], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False

def check_port(port: int) -> bool:
    """Check if a port is in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def check_docker() -> Tuple[bool, str]:
    """Check if Docker is installed and running."""
    if not check_command("docker"):
        return False, "Docker is not installed"
    
    try:
        result = subprocess.run(
            ["docker", "info"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        if result.returncode != 0:
            return False, "Docker is installed but not running"
        return True, "Docker is installed and running"
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, "Error checking Docker status"

def check_docker_compose() -> Tuple[bool, str]:
    """Check if Docker Compose is installed."""
    if check_command("docker-compose"):
        try:
            result = subprocess.run(
                ["docker-compose", "--version"], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                check=False
            )
            if result.returncode == 0:
                return True, f"Docker Compose is installed: {result.stdout.decode().strip()}"
        except (subprocess.SubprocessError, FileNotFoundError):
            pass
    
    # Check for docker compose plugin
    try:
        result = subprocess.run(
            ["docker", "compose", "version"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        if result.returncode == 0:
            return True, f"Docker Compose plugin is installed: {result.stdout.decode().strip()}"
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return False, "Docker Compose is not installed"

def check_python() -> Tuple[bool, str]:
    """Check Python version."""
    try:
        version = platform.python_version()
        if version.startswith("3."):
            major, minor, *_ = version.split(".")
            if int(major) >= 3 and int(minor) >= 9:
                return True, f"Python {version} is installed (3.9+ required)"
            else:
                return False, f"Python {version} is installed but 3.9+ is required"
        else:
            return False, f"Python {version} is installed but Python 3 is required"
    except Exception as e:
        return False, f"Error checking Python version: {e}"

def check_env_file() -> Tuple[bool, Dict[str, str]]:
    """Check if .env file exists and load its contents."""
    env_file = Path(".env")
    if not env_file.exists():
        return False, {}
    
    env_vars = {}
    with open(env_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            
            if "=" in line:
                key, value = line.split("=", 1)
                env_vars[key.strip()] = value.strip()
    
    return True, env_vars

def check_n8n(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Check if n8n is running."""
    n8n_url = env_vars.get("N8N_URL", "http://localhost:5678")
    
    try:
        response = requests.get(f"{n8n_url}/healthz", timeout=5)
        if response.status_code == 200:
            return True, f"n8n is running at {n8n_url}"
        else:
            return False, f"n8n returned status code {response.status_code} at {n8n_url}"
    except requests.RequestException as e:
        return False, f"Could not connect to n8n at {n8n_url}: {e}"

def check_mcp_server(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Check if MCP server is running."""
    mcp_port = int(env_vars.get("MCP_PORT", "3333"))
    
    if check_port(mcp_port):
        return True, f"MCP server is running on port {mcp_port}"
    else:
        return False, f"MCP server is not running on port {mcp_port}"

def check_ollama(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Check if Ollama is running."""
    ollama_port = int(env_vars.get("OLLAMA_PORT", "11434"))
    
    if check_port(ollama_port):
        try:
            response = requests.get(f"http://localhost:{ollama_port}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return True, f"Ollama is running with {len(models)} models"
            else:
                return True, f"Ollama is running but returned status code {response.status_code}"
        except requests.RequestException as e:
            return True, f"Ollama is running but API request failed: {e}"
    else:
        return False, f"Ollama is not running on port {ollama_port}"

def check_openhands(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Check if OpenHands is running."""
    openhands_port = int(env_vars.get("OPENHANDS_PORT", "8080"))
    
    if check_port(openhands_port):
        return True, f"OpenHands is running on port {openhands_port}"
    else:
        return False, f"OpenHands is not running on port {openhands_port}"

def check_llamafile(env_vars: Dict[str, str]) -> Tuple[bool, str]:
    """Check if Llamafile is running."""
    llamafile_port = int(env_vars.get("LLAMAFILE_PORT", "8080"))
    
    # Check if the port is in use
    if check_port(llamafile_port):
        try:
            response = requests.get(f"http://localhost:{llamafile_port}/v1/models", timeout=5)
            if response.status_code == 200:
                return True, f"Llamafile is running on port {llamafile_port}"
            else:
                return True, f"Something is running on port {llamafile_port} but it might not be Llamafile"
        except requests.RequestException:
            return True, f"Something is running on port {llamafile_port} but it might not be Llamafile"
    else:
        return False, f"Llamafile is not running on port {llamafile_port}"

def check_cli() -> Tuple[bool, str]:
    """Check if the CLI is properly installed."""
    cli_script = Path("cli/dev-server.sh")
    if not cli_script.exists():
        return False, "CLI script not found"
    
    if not os.access(cli_script, os.X_OK):
        return False, "CLI script is not executable"
    
    return True, "CLI is properly installed"

def check_docker_containers() -> List[Dict[str, str]]:
    """Check running Docker containers."""
    try:
        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}},{{.Status}},{{.Ports}}"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        
        if result.returncode != 0:
            return []
        
        containers = []
        for line in result.stdout.decode().strip().split("\n"):
            if not line:
                continue
            
            parts = line.split(",", 2)
            if len(parts) >= 2:
                name, status = parts[0], parts[1]
                ports = parts[2] if len(parts) > 2 else ""
                containers.append({
                    "name": name,
                    "status": status,
                    "ports": ports
                })
        
        return containers
    except (subprocess.SubprocessError, FileNotFoundError):
        return []

def check_processes() -> List[Dict[str, str]]:
    """Check running processes related to the project."""
    processes = []
    
    # Check for llamafile process
    try:
        result = subprocess.run(
            ["pgrep", "-f", "llamafile"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        
        if result.returncode == 0:
            pid = result.stdout.decode().strip()
            processes.append({
                "name": "llamafile",
                "pid": pid,
                "status": "running"
            })
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    # Check for MCP server process
    try:
        result = subprocess.run(
            ["pgrep", "-f", "n8n_mcp_server.py"], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            check=False
        )
        
        if result.returncode == 0:
            pid = result.stdout.decode().strip()
            processes.append({
                "name": "mcp_server",
                "pid": pid,
                "status": "running"
            })
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    
    return processes

def check_network_ports() -> List[Dict[str, Any]]:
    """Check network ports used by the project."""
    ports = [
        {"port": 5678, "service": "n8n"},
        {"port": 3333, "service": "MCP Server"},
        {"port": 11434, "service": "Ollama"},
        {"port": 8080, "service": "OpenHands/Llamafile"},
        {"port": 8081, "service": "MCP Inspector"},
        {"port": 6379, "service": "Redis"}
    ]
    
    for port_info in ports:
        port_info["in_use"] = check_port(port_info["port"])
    
    return ports

def main() -> int:
    """Main function."""
    print_header("Dev-Server-Workflow Diagnostic Tool")
    
    # Check system requirements
    print_header("System Requirements")
    
    # Check Python
    python_ok, python_msg = check_python()
    if python_ok:
        print_success(python_msg)
    else:
        print_error(python_msg)
    
    # Check Docker
    docker_ok, docker_msg = check_docker()
    if docker_ok:
        print_success(docker_msg)
    else:
        print_error(docker_msg)
    
    # Check Docker Compose
    compose_ok, compose_msg = check_docker_compose()
    if compose_ok:
        print_success(compose_msg)
    else:
        print_error(compose_msg)
    
    # Check CLI
    cli_ok, cli_msg = check_cli()
    if cli_ok:
        print_success(cli_msg)
    else:
        print_error(cli_msg)
    
    # Check environment file
    print_header("Environment Configuration")
    env_ok, env_vars = check_env_file()
    if env_ok:
        print_success(".env file found")
        
        # Check required variables
        required_vars = [
            "N8N_API_KEY",
            "GITHUB_TOKEN",
            "OPENPROJECT_TOKEN",
            "LLM_API_KEY"
        ]
        
        for var in required_vars:
            if var in env_vars and env_vars[var]:
                print_success(f"{var} is set")
            else:
                print_warning(f"{var} is not set")
    else:
        print_error(".env file not found")
    
    # Check component status
    print_header("Component Status")
    
    # Check n8n
    n8n_ok, n8n_msg = check_n8n(env_vars)
    if n8n_ok:
        print_success(n8n_msg)
    else:
        print_error(n8n_msg)
    
    # Check MCP server
    mcp_ok, mcp_msg = check_mcp_server(env_vars)
    if mcp_ok:
        print_success(mcp_msg)
    else:
        print_error(mcp_msg)
    
    # Check Ollama
    ollama_ok, ollama_msg = check_ollama(env_vars)
    if ollama_ok:
        print_success(ollama_msg)
    else:
        print_error(ollama_msg)
    
    # Check OpenHands
    openhands_ok, openhands_msg = check_openhands(env_vars)
    if openhands_ok:
        print_success(openhands_msg)
    else:
        print_error(openhands_msg)
    
    # Check Llamafile
    llamafile_ok, llamafile_msg = check_llamafile(env_vars)
    if llamafile_ok:
        print_success(llamafile_msg)
    else:
        print_error(llamafile_msg)
    
    # Check Docker containers
    print_header("Docker Containers")
    containers = check_docker_containers()
    if containers:
        for container in containers:
            print_info(f"{container['name']}: {container['status']}")
            if container['ports']:
                print_info(f"  Ports: {container['ports']}")
    else:
        print_warning("No Docker containers found")
    
    # Check processes
    print_header("Running Processes")
    processes = check_processes()
    if processes:
        for process in processes:
            print_info(f"{process['name']}: PID {process['pid']} ({process['status']})")
    else:
        print_warning("No relevant processes found")
    
    # Check network ports
    print_header("Network Ports")
    ports = check_network_ports()
    for port_info in ports:
        if port_info["in_use"]:
            print_info(f"Port {port_info['port']} ({port_info['service']}): In use")
        else:
            print_warning(f"Port {port_info['port']} ({port_info['service']}): Not in use")
    
    # Provide troubleshooting advice
    print_header("Troubleshooting Advice")
    
    if not docker_ok:
        print_error("Docker is required for most components. Please install Docker and ensure it's running.")
        print_info("Installation instructions: https://docs.docker.com/get-docker/")
    
    if not n8n_ok:
        print_error("n8n is not running. Try starting it with:")
        print_info("  ./cli/dev-server.sh start n8n")
        print_info("  or check logs with: ./cli/dev-server.sh logs n8n")
    
    if not mcp_ok:
        print_error("MCP server is not running. Try starting it with:")
        print_info("  ./cli/dev-server.sh start mcp")
        print_info("  or check logs with: ./cli/dev-server.sh logs mcp")
    
    if not env_ok:
        print_error("No .env file found. Create one from the template:")
        print_info("  cp src/env-template .env")
        print_info("  Then edit .env to add your configuration")
    
    # Check for port conflicts
    port_conflicts = []
    for i, port1 in enumerate(ports):
        for port2 in ports[i+1:]:
            if port1["port"] == port2["port"] and port1["in_use"] and port2["in_use"]:
                port_conflicts.append((port1, port2))
    
    if port_conflicts:
        print_error("Port conflicts detected:")
        for port1, port2 in port_conflicts:
            print_info(f"  Port {port1['port']} is used by both {port1['service']} and {port2['service']}")
        print_info("Modify the port configuration in .env or docker-compose.yml")
    
    print_header("Next Steps")
    print_info("For detailed documentation, see the docs/ directory")
    print_info("To start all components: ./cli/dev-server.sh start all")
    print_info("To view the interactive menu: ./cli/dev-server.sh menu")
    print_info("For help with specific issues: ./cli/dev-server.sh help")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())