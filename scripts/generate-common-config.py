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
Gemeinsame Konfigurationsgenerator für MCP-Server-Implementierungen

Dieses Skript generiert gemeinsame Konfigurationsdateien für beide MCP-Server-Implementierungen
(docker-mcp-ecosystem und docker-mcp-servers), um Konsistenz zu gewährleisten.
"""

import argparse
import json
import os
import shutil
import sys
import yaml
from pathlib import Path

# Konfiguration des Loggings
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('generate-common-config')

# Standardwerte
DEFAULT_MCP_SERVERS = [
    {
        "name": "filesystem",
        "image": "mcp/filesystem:latest",
        "port": 3001,
        "description": "File system operations"
    },
    {
        "name": "desktop-commander",
        "image": "mcp/desktop-commander:latest",
        "port": 3002,
        "description": "Terminal command execution"
    },
    {
        "name": "sequential-thinking",
        "image": "mcp/sequentialthinking:latest",
        "port": 3003,
        "description": "Structured problem-solving"
    },
    {
        "name": "github-chat",
        "image": "mcp/github-chat:latest",
        "port": 3004,
        "description": "GitHub discussions interaction"
    },
    {
        "name": "github",
        "image": "mcp/github:latest",
        "port": 3005,
        "description": "GitHub repository management"
    },
    {
        "name": "puppeteer",
        "image": "mcp/puppeteer:latest",
        "port": 3006,
        "description": "Web browsing and interaction"
    },
    {
        "name": "basic-memory",
        "image": "mcp/basic-memory:latest",
        "port": 3007,
        "description": "Simple key-value storage"
    },
    {
        "name": "wikipedia",
        "image": "mcp/wikipedia-mcp:latest",
        "port": 3008,
        "description": "Wikipedia search"
    }
]

def generate_env_file(output_path, github_token=None, redis_password=None):
    """Generiert eine .env-Datei mit gemeinsamen Umgebungsvariablen."""
    try:
        env_content = f"""# Gemeinsame Umgebungsvariablen für MCP-Server-Implementierungen
# Generiert von generate-common-config.py

# GitHub-Konfiguration
GITHUB_TOKEN={github_token or "your-github-token"}

# Redis-Konfiguration
REDIS_PASSWORD={redis_password or "redis_password"}

# Workspace-Pfad
WORKSPACE_PATH=/workspace

# MCP-Server-Konfiguration
MCP_SERVERS_CONFIG={{"servers":[
  {{"name":"filesystem","url":"http://mcp-filesystem:3001","type":"filesystem"}},
  {{"name":"desktop-commander","url":"http://mcp-desktop-commander:3002","type":"desktop"}},
  {{"name":"sequential-thinking","url":"http://mcp-sequential-thinking:3003","type":"thinking"}},
  {{"name":"github-chat","url":"http://mcp-github-chat:3004","type":"github"}},
  {{"name":"github","url":"http://mcp-github:3005","type":"github"}},
  {{"name":"puppeteer","url":"http://mcp-puppeteer:3006","type":"browser"}},
  {{"name":"basic-memory","url":"http://mcp-basic-memory:3007","type":"memory"}},
  {{"name":"wikipedia","url":"http://mcp-wikipedia:3008","type":"knowledge"}}
]}}

# n8n-Konfiguration
N8N_ENCRYPTION_KEY=n8n-encryption-key
POSTGRES_USER=n8n
POSTGRES_PASSWORD=n8n
POSTGRES_DB=n8n

# OpenHands-Konfiguration
OPENHANDS_CONFIG_DIR=$HOME/.config/openhands
OPENHANDS_STATE_DIR=$HOME/.openhands-state
OPENHANDS_WORKSPACE_DIR=$HOME/workspace
OPENHANDS_PORT=3000

# Slack-Konfiguration
SLACK_CHANNEL_ALERTS=mcp-alerts
SLACK_CHANNEL_GITHUB=github-updates

# AppFlowy-Konfiguration
APPFLOWY_DATABASE_ID=your-appflowy-db-id
APPFLOWY_DATABASE_ID_ANALYSIS=your-appflowy-analysis-db-id
"""
        
        with open(output_path, 'w') as f:
            f.write(env_content)
        
        logger.info(f"✅ .env-Datei wurde erfolgreich erstellt: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Erstellen der .env-Datei: {e}")
        return False

def generate_docker_compose_common(output_path, mcp_servers=None):
    """Generiert eine gemeinsame Docker-Compose-Datei für die MCP-Server."""
    try:
        if mcp_servers is None:
            mcp_servers = DEFAULT_MCP_SERVERS
        
        # Erstelle die Docker-Compose-Konfiguration
        compose_config = {
            "version": "3.8",
            "networks": {
                "mcp-network": {
                    "driver": "bridge"
                }
            },
            "volumes": {
                "redis_data": {},
                "filesystem_data": {},
                "basic_memory_data": {},
                "wikipedia_data": {}
            },
            "services": {
                "redis": {
                    "image": "redis:7-alpine",
                    "container_name": "mcp-redis",
                    "restart": "always",
                    "command": "redis-server --requirepass ${REDIS_PASSWORD:-redis_password} --maxmemory 512mb --maxmemory-policy allkeys-lru",
                    "volumes": ["redis_data:/data"],
                    "networks": ["mcp-network"],
                    "deploy": {
                        "resources": {
                            "limits": {
                                "cpus": "0.5",
                                "memory": "768M"
                            },
                            "reservations": {
                                "cpus": "0.2",
                                "memory": "256M"
                            }
                        }
                    },
                    "healthcheck": {
                        "test": ["CMD", "redis-cli", "ping"],
                        "interval": "30s",
                        "timeout": "10s",
                        "retries": 3
                    }
                }
            }
        }
        
        # Füge die MCP-Server hinzu
        for server in mcp_servers:
            server_name = server["name"]
            container_name = f"mcp-{server_name}"
            
            compose_config["services"][f"{server_name}-mcp"] = {
                "image": server["image"],
                "container_name": container_name,
                "restart": "always",
                "environment": [
                    f"MCP_PORT={server['port']}",
                    "REDIS_HOST=redis",
                    "REDIS_PORT=6379",
                    "REDIS_PASSWORD=${REDIS_PASSWORD:-redis_password}",
                    "LOG_LEVEL=info"
                ],
                "ports": [f"{server['port']}:{server['port']}"],
                "networks": ["mcp-network"],
                "depends_on": ["redis"],
                "deploy": {
                    "resources": {
                        "limits": {
                            "cpus": "0.5",
                            "memory": "512M"
                        },
                        "reservations": {
                            "cpus": "0.25",
                            "memory": "256M"
                        }
                    }
                },
                "healthcheck": {
                    "test": ["CMD", "curl", "-f", f"http://localhost:{server['port']}/health"],
                    "interval": "30s",
                    "timeout": "10s",
                    "retries": 3
                }
            }
            
            # Spezifische Konfigurationen für bestimmte Server
            if server_name == "filesystem":
                compose_config["services"][f"{server_name}-mcp"]["volumes"] = [
                    "${WORKSPACE_PATH:-/workspace}:/workspace:rw",
                    "filesystem_data:/data"
                ]
                compose_config["services"][f"{server_name}-mcp"]["environment"].append("ALLOWED_PATHS=/workspace")
            
            elif server_name == "desktop-commander":
                compose_config["services"][f"{server_name}-mcp"]["volumes"] = [
                    "${WORKSPACE_PATH:-/workspace}:/workspace:rw",
                    "/tmp/.X11-unix:/tmp/.X11-unix:ro"
                ]
                compose_config["services"][f"{server_name}-mcp"]["environment"].extend([
                    "DISPLAY=${DISPLAY}",
                    'ALLOWED_DIRECTORIES=["/workspace"]',
                    'BLOCKED_COMMANDS=["rm -rf /", "sudo", "su", "dd", "mkfs", "format", "fdisk", "shutdown", "reboot", "halt", "poweroff"]'
                ])
            
            elif server_name == "github" or server_name == "github-chat":
                compose_config["services"][f"{server_name}-mcp"]["environment"].extend([
                    "GITHUB_TOKEN=${GITHUB_TOKEN}",
                    "CACHE_ENABLED=true",
                    "CACHE_TTL=3600",
                    "RATE_LIMIT_ENABLED=true",
                    "RATE_LIMIT_REQUESTS=60",
                    "RATE_LIMIT_PERIOD=60"
                ])
                
                if server_name == "github":
                    compose_config["services"][f"{server_name}-mcp"]["environment"].append("ALLOWED_REPOS=EcoSphereNetwork/*")
            
            elif server_name == "puppeteer":
                compose_config["services"][f"{server_name}-mcp"]["environment"].extend([
                    "PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser",
                    "PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true",
                    "PUPPETEER_ARGS=--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage,--disable-gpu,--disable-extensions",
                    "MAX_CONCURRENT_BROWSERS=5",
                    "BROWSER_TIMEOUT=60000",
                    "ALLOWED_DOMAINS=github.com,gitlab.com,openproject.org,wikipedia.org"
                ])
                compose_config["services"][f"{server_name}-mcp"]["security_opt"] = ["seccomp=unconfined"]
            
            elif server_name == "basic-memory":
                compose_config["services"][f"{server_name}-mcp"]["volumes"] = ["basic_memory_data:/data"]
                compose_config["services"][f"{server_name}-mcp"]["environment"].extend([
                    "STORAGE_TYPE=redis",
                    "MAX_MEMORY_SIZE=100MB",
                    "MEMORY_EXPIRATION=86400"
                ])
            
            elif server_name == "wikipedia":
                compose_config["services"][f"{server_name}-mcp"]["volumes"] = ["wikipedia_data:/data"]
                compose_config["services"][f"{server_name}-mcp"]["environment"].extend([
                    "CACHE_ENABLED=true",
                    "CACHE_TTL=86400",
                    "DEFAULT_LANGUAGE=en",
                    "RATE_LIMIT_ENABLED=true",
                    "RATE_LIMIT_REQUESTS=30",
                    "RATE_LIMIT_PERIOD=60",
                    "MAX_SEARCH_RESULTS=10"
                ])
        
        # Füge den MCP Inspector hinzu
        compose_config["services"]["mcp-inspector"] = {
            "image": "mcp/inspector:latest",
            "container_name": "mcp-inspector",
            "restart": "always",
            "environment": [
                "PORT=8080",
                "MCP_SERVERS=filesystem-mcp:3001,desktop-commander-mcp:3002,sequential-thinking-mcp:3003,github-chat-mcp:3004,github-mcp:3005,puppeteer-mcp:3006,basic-memory-mcp:3007,wikipedia-mcp:3008",
                "LOG_LEVEL=info",
                "REFRESH_INTERVAL=30"
            ],
            "ports": ["8080:8080"],
            "networks": ["mcp-network"],
            "depends_on": [f"{server['name']}-mcp" for server in mcp_servers],
            "deploy": {
                "resources": {
                    "limits": {
                        "cpus": "0.3",
                        "memory": "256M"
                    },
                    "reservations": {
                        "cpus": "0.1",
                        "memory": "128M"
                    }
                }
            },
            "healthcheck": {
                "test": ["CMD", "curl", "-f", "http://localhost:8080/health"],
                "interval": "30s",
                "timeout": "10s",
                "retries": 3
            }
        }
        
        # Schreibe die Docker-Compose-Datei
        with open(output_path, 'w') as f:
            yaml.dump(compose_config, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"✅ Docker-Compose-Datei wurde erfolgreich erstellt: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Erstellen der Docker-Compose-Datei: {e}")
        return False

def generate_openhands_config(output_path, mcp_servers=None, github_token=None):
    """Generiert eine OpenHands-Konfigurationsdatei für die MCP-Server."""
    try:
        if mcp_servers is None:
            mcp_servers = DEFAULT_MCP_SERVERS
        
        # Erstelle die OpenHands-Konfiguration
        openhands_config = {
            "mcp": {
                "servers": [
                    {
                        "name": f"{server['name']}-mcp",
                        "url": f"http://mcp-{server['name']}:{server['port']}",
                        "description": server["description"]
                    }
                    for server in mcp_servers
                ],
                "autoApproveTools": True,
                "autoApproveToolsList": [
                    "read_file",
                    "write_file",
                    "list_directory",
                    "execute_command",
                    "search_wikipedia",
                    "create_github_issue",
                    "create_github_pr",
                    "update_work_package",
                    "sync_documentation"
                ]
            }
        }
        
        # Füge GitHub-Token hinzu, wenn vorhanden
        if github_token:
            for server in openhands_config["mcp"]["servers"]:
                if "github" in server["name"]:
                    server["auth"] = {
                        "type": "token",
                        "token": github_token
                    }
        
        # Schreibe die OpenHands-Konfigurationsdatei
        with open(output_path, 'w') as f:
            json.dump(openhands_config, f, indent=2)
        
        logger.info(f"✅ OpenHands-Konfigurationsdatei wurde erfolgreich erstellt: {output_path}")
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Erstellen der OpenHands-Konfigurationsdatei: {e}")
        return False

def copy_files_to_implementations(common_dir, ecosystem_dir, servers_dir):
    """Kopiert die gemeinsamen Konfigurationsdateien in die Implementierungsverzeichnisse."""
    try:
        # Erstelle die Verzeichnisse, falls sie nicht existieren
        os.makedirs(common_dir, exist_ok=True)
        
        # Kopiere die .env-Datei
        env_file = os.path.join(common_dir, ".env.example")
        if os.path.exists(env_file):
            shutil.copy2(env_file, os.path.join(ecosystem_dir, ".env.example"))
            shutil.copy2(env_file, os.path.join(servers_dir, ".env.example"))
            logger.info(f"✅ .env.example wurde in beide Implementierungsverzeichnisse kopiert")
        
        # Kopiere die Docker-Compose-Datei
        compose_file = os.path.join(common_dir, "docker-compose-common.yml")
        if os.path.exists(compose_file):
            shutil.copy2(compose_file, os.path.join(ecosystem_dir, "docker-compose-common.yml"))
            shutil.copy2(compose_file, os.path.join(servers_dir, "docker-compose-common.yml"))
            logger.info(f"✅ docker-compose-common.yml wurde in beide Implementierungsverzeichnisse kopiert")
        
        # Kopiere die OpenHands-Konfigurationsdatei
        openhands_config_file = os.path.join(common_dir, "openhands-mcp-config.json")
        if os.path.exists(openhands_config_file):
            shutil.copy2(openhands_config_file, os.path.join(ecosystem_dir, "openhands-mcp-config.json"))
            shutil.copy2(openhands_config_file, os.path.join(servers_dir, "openhands-mcp-config.json"))
            logger.info(f"✅ openhands-mcp-config.json wurde in beide Implementierungsverzeichnisse kopiert")
        
        return True
    
    except Exception as e:
        logger.error(f"❌ Fehler beim Kopieren der Dateien: {e}")
        return False

def main():
    """Hauptfunktion des Skripts."""
    parser = argparse.ArgumentParser(description="Gemeinsame Konfigurationsgenerator für MCP-Server-Implementierungen")
    parser.add_argument("--common-dir", default="config/common", help="Verzeichnis für gemeinsame Konfigurationsdateien")
    parser.add_argument("--ecosystem-dir", default="docker-mcp-ecosystem", help="Verzeichnis für die Ecosystem-Implementierung")
    parser.add_argument("--servers-dir", default="docker-mcp-servers", help="Verzeichnis für die Servers-Implementierung")
    parser.add_argument("--github-token", help="GitHub-Token für die GitHub-MCP-Server")
    parser.add_argument("--redis-password", help="Redis-Passwort")
    parser.add_argument("--copy", action="store_true", help="Kopiere die Dateien in die Implementierungsverzeichnisse")
    
    args = parser.parse_args()
    
    # Erstelle das Verzeichnis für gemeinsame Konfigurationsdateien
    os.makedirs(args.common_dir, exist_ok=True)
    
    # Generiere die .env-Datei
    env_file = os.path.join(args.common_dir, ".env.example")
    if not generate_env_file(env_file, args.github_token, args.redis_password):
        logger.error(".env-Datei konnte nicht erstellt werden.")
        return 1
    
    # Generiere die Docker-Compose-Datei
    compose_file = os.path.join(args.common_dir, "docker-compose-common.yml")
    if not generate_docker_compose_common(compose_file):
        logger.error("Docker-Compose-Datei konnte nicht erstellt werden.")
        return 1
    
    # Generiere die OpenHands-Konfigurationsdatei
    openhands_config_file = os.path.join(args.common_dir, "openhands-mcp-config.json")
    if not generate_openhands_config(openhands_config_file, github_token=args.github_token):
        logger.error("OpenHands-Konfigurationsdatei konnte nicht erstellt werden.")
        return 1
    
    # Kopiere die Dateien in die Implementierungsverzeichnisse, wenn gewünscht
    if args.copy:
        if not copy_files_to_implementations(args.common_dir, args.ecosystem_dir, args.servers_dir):
            logger.error("Dateien konnten nicht kopiert werden.")
            return 1
    
    logger.info(f"✅ Gemeinsame Konfigurationsdateien wurden erfolgreich erstellt in {args.common_dir}")
    logger.info(f"Um die Dateien in die Implementierungsverzeichnisse zu kopieren, verwenden Sie --copy")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())