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
n8n Setup - Installation

Dieses Modul enthält Funktionen für die Installation und initiale Einrichtung von n8n.
"""

import os
import time
import base64
import subprocess
import requests
from typing import Dict, List, Any, Optional, Tuple, Union, Callable

from common.docker_utils import (
    check_docker_installed,
    check_docker_compose_installed,
    start_docker_compose,
    stop_docker_compose,
    restart_docker_compose
)

# Docker Compose file für n8n
DOCKER_COMPOSE_YML = """version: '3'

services:
  n8n:
    image: docker.n8n.io/n8nio/n8n
    ports:
      - "5678:5678"
    environment:
      - N8N_HOST=${N8N_HOST:-localhost}
      - N8N_PORT=5678
      - N8N_PROTOCOL=${N8N_PROTOCOL:-http}
      - N8N_USER_MANAGEMENT_DISABLED=false
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=${N8N_USER:-admin}
      - N8N_BASIC_AUTH_PASSWORD=${N8N_PASSWORD:-password}
      - N8N_ENCRYPTION_KEY=${N8N_ENCRYPTION_KEY:-your_encryption_key_min_32_chars}
      # Uncomment to enable webhook tunneling for local development
      # - N8N_TUNNEL_ENABLED=true
    volumes:
      - ${N8N_DATA_FOLDER:-./n8n_data}:/home/node/.n8n
    restart: unless-stopped
"""

def install_n8n_docker() -> bool:
    """
    Install n8n using Docker Compose.
    
    Returns:
        bool: True if installation was successful, False otherwise.
    """
    # Create directory for n8n data
    os.makedirs('n8n_data', exist_ok=True)
    
    # Create docker-compose.yml file
    with open('docker-compose.yml', 'w') as f:
        f.write(DOCKER_COMPOSE_YML)
    
    # Create .env file if it doesn't exist
    env_file = '.env'
    if not os.path.isfile(env_file):
        with open(env_file, 'w') as f:
            f.write('N8N_USER=admin\n')
            f.write('N8N_PASSWORD=password\n')
            f.write(f'N8N_ENCRYPTION_KEY={base64.b64encode(os.urandom(24)).decode()}\n')
    
    # Start n8n using Docker Compose
    result = start_docker_compose('docker-compose.yml')
    if not result:
        logger.info("Failed to start n8n Docker container.")
        return False
    
    logger.info("n8n is starting up. It should be available at http://localhost:5678 in a few moments.")
    logger.info("Default credentials: admin / password")
    
    # Wait for n8n to start
    for _ in range(10):
        try:
            response = requests.get('http://localhost:5678/healthz')
            if response.status_code == 200:
                logger.info("n8n is up and running!")
                return True
        except:
            pass
        time.sleep(2)
    
    logger.info("n8n may still be starting up. Please check http://localhost:5678 in a few moments.")
    return True


def get_n8n_api_key(n8n_url: str, username: str, password: str) -> str:
    """
    Get n8n API key for the given user.
    
    Args:
        n8n_url: URL of the n8n instance
        username: n8n username
        password: n8n password
        
    Returns:
        str: API key for the user
        
    Raises:
        Exception: If login fails
    """
    login_data = {
        'email': username,
        'password': password
    }
    
    response = requests.post(f"{n8n_url}/rest/login", json=login_data)
    if response.status_code != 200:
        raise Exception(f"Failed to login to n8n: {response.text}")
    
    token = response.json().get('token')
    if not token:
        raise Exception("Failed to get token from login response")
    
    return token


def check_n8n_status(n8n_url: str) -> bool:
    """
    Check if n8n is running.
    
    Args:
        n8n_url: URL of the n8n instance
        
    Returns:
        bool: True if n8n is running, False otherwise
    """
    try:
        response = requests.get(f"{n8n_url}/healthz")
        return response.status_code == 200
    except:
        return False


def stop_n8n_docker() -> None:
    """
    Stop n8n Docker container.
    
    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    stop_docker_compose('docker-compose.yml')
    logger.info("n8n Docker container stopped.")


def restart_n8n_docker() -> None:
    """
    Restart n8n Docker container.
    
    Raises:
        subprocess.CalledProcessError: If the command fails
    """
    restart_docker_compose('docker-compose.yml')
    logger.info("n8n Docker container restarted.")


def setup_n8n_prerequisites() -> bool:
    """
    Check and setup prerequisites for n8n installation.
    
    Returns:
        bool: True if all prerequisites are met, False otherwise
    """
    if not check_docker_installed():
        logger.info("Docker is not installed. Please install Docker first.")
        logger.info("Visit https://docs.docker.com/get-docker/ for installation instructions.")
        return False
    
    if not check_docker_compose_installed():
        logger.info("Docker Compose is not installed. Please install Docker Compose first.")
        logger.info("Visit https://docs.docker.com/compose/install/ for installation instructions.")
        return False
    
    return True


def main() -> None:
    """
    Main function for testing.
    """
    if setup_n8n_prerequisites():
        install_n8n_docker()
        
        # Wait for n8n to start
        time.sleep(10)
        
        if check_n8n_status('http://localhost:5678'):
            logger.info("n8n is running!")
            
            # Get API key
            try:
                api_key = get_n8n_api_key('http://localhost:5678', 'admin', 'password')
                print(f"API key: {api_key}")
            except Exception as e:
                print(f"Failed to get API key: {str(e)}")
                
        else:
            logger.info("n8n is not running.")
    else:
        logger.info("Prerequisites not met. Please install Docker and Docker Compose first.")


if __name__ == "__main__":
    main()