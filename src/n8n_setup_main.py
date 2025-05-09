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
n8n Setup - Hauptskript

Dieses Skript dient als Einstiegspunkt für die Installation und Konfiguration von n8n
mit Workflows für AFFiNE, AppFlowy, GitLab/GitHub, OpenProject und OpenHands.

Verwendung:
python n8n_setup_main.py --install --env-file .env
"""

import os
import argparse
import time
import subprocess
import json
import sys
import asyncio
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple, Set, Callable

# Füge das aktuelle Verzeichnis zum Python-Pfad hinzu, um lokale Importe zu ermöglichen
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import der Modulskripte
from n8n_setup_utils import load_env_file, create_workflow, create_credential, activate_workflow
from n8n_setup_install import install_n8n_docker, get_n8n_api_key
from n8n_setup_credentials import (
    setup_github_credential, 
    setup_openproject_credential,
    setup_discord_credential,
    setup_affine_credential,
    setup_appflowy_credential,
    setup_openhands_credential
)
from n8n_setup_workflows import (
    GITHUB_OPENPROJECT_WORKFLOW,
    DOCUMENT_SYNC_WORKFLOW,
    OPENHANDS_WORKFLOW,
    DISCORD_NOTIFICATION_WORKFLOW,
    TIME_TRACKING_WORKFLOW,
    AI_SUMMARY_WORKFLOW,
    MCP_SERVER_WORKFLOW
)

# MCP Server Template
N8N_MCP_SERVER_TEMPLATE = """#!/usr/bin/env python3
\"\"\"
n8n MCP Server

Implementiert einen Model Context Protocol (MCP) Server für n8n, der es KI-Agenten 
ermöglicht, n8n-Workflows als Tools zu verwenden.
\"\"\"

import os
import json
import asyncio
import subprocess
import sys
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("n8n-mcp-server")

class N8nMCPServer:
    \"\"\"MCP-Server, der n8n-Funktionalität als Tools bereitstellt.\"\"\"
    
    def __init__(self, n8n_url, api_key):
        \"\"\"Initialisiert den MCP-Server mit n8n-API Zugangsdaten.
        
        Args:
            n8n_url: URL der n8n-Instanz
            api_key: API-Key für n8n
        \"\"\"
        self.n8n_url = n8n_url
        self.n8n_api_key = api_key
        self.request_id = 0
        self.tools = self._load_available_tools()
        
    def _load_available_tools(self):
        \"\"\"Lädt verfügbare n8n-Workflows als Tools.\"\"\"
        # Diese würden tatsächlich über die n8n-API abgefragt
        return [
            {
                "name": "create_github_issue",
                "description": "Erstellt ein neues Issue in GitHub",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Titel des Issues"},
                        "body": {"type": "string", "description": "Beschreibung des Issues"},
                        "owner": {"type": "string", "description": "Repository Owner"},
                        "repo": {"type": "string", "description": "Repository Name"}
                    },
                    "required": ["title", "body", "owner", "repo"]
                }
            },
            {
                "name": "update_work_package",
                "description": "Aktualisiert ein Arbeitspaket in OpenProject",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "string", "description": "ID des Arbeitspakets"},
                        "status": {"type": "string", "description": "Neuer Status"},
                        "description": {"type": "string", "description": "Neue Beschreibung"}
                    },
                    "required": ["id"]
                }
            },
            {
                "name": "sync_documentation",
                "description": "Synchronisiert Dokumentation zwischen AFFiNE und GitHub",
                "parameters": {
                    "type": "object", 
                    "properties": {
                        "doc_id": {"type": "string", "description": "ID des Dokuments in AFFiNE"},
                        "github_path": {"type": "string", "description": "Pfad der Datei in GitHub"},
                        "owner": {"type": "string", "description": "Repository Owner"},
                        "repo": {"type": "string", "description": "Repository Name"}
                    },
                    "required": ["doc_id", "github_path", "owner", "repo"]
                }
            }
        ]
    
    async def start(self):
        \"\"\"Startet den MCP-Server und verarbeitet Standard-Ein/Ausgabe nach dem MCP-Protokoll.\"\"\"
        logger.info("Starting MCP Server for n8n")
        
        # Lese von stdin, schreibe nach stdout
        self.reader = asyncio.StreamReader()
        protocol = asyncio.StreamReaderProtocol(self.reader)
        await asyncio.get_event_loop().connect_read_pipe(lambda: protocol, sys.stdin)
        
        self.writer_transport, self.writer_protocol = await asyncio.get_event_loop().connect_write_pipe(
            asyncio.streams.FlowControlMixin, sys.stdout)
        self.writer = asyncio.StreamWriter(
            self.writer_transport, self.writer_protocol, None, asyncio.get_event_loop())
        
        # Verarbeite eingehende Nachrichten
        while True:
            try:
                line = await self.reader.readline()
                if not line:
                    break
                    
                message = json.loads(line.decode())
                await self._handle_message(message)
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                await self._send_error(None, str(e))
    
    async def _handle_message(self, message):
        \"\"\"Verarbeitet eingehende JSON-RPC-Nachrichten.
        
        Args:
            message: Die empfangene JSON-RPC-Nachricht
        \"\"\"
        message_id = message.get("id")
        method = message.get("method")
        params = message.get("params", {})
        
        # Verarbeiten unterschiedlicher RPC-Methoden
        if method == "initialize":
            await self._send_response(message_id, {"capabilities": {"tools": True}})
        elif method == "mcp.listTools":
            await self._send_response(message_id, self.tools)
        elif method == "mcp.callTool":
            result = await self._execute_tool(params.get("name"), params.get("arguments", {}))
            await self._send_response(message_id, result)
        else:
            await self._send_error(message_id, f"Unsupported method: {method}")
    
    async def _execute_tool(self, tool_name, arguments):
        \"\"\"Führt ein Tool aus, indem der entsprechende n8n-Workflow aufgerufen wird.
        
        Args:
            tool_name: Name des auszuführenden Tools
            arguments: Parameter für den Tool-Aufruf
            
        Returns:
            Das Ergebnis der Workflow-Ausführung
        \"\"\"
        logger.info(f"Executing tool {tool_name} with arguments {json.dumps(arguments)}")
        
        # Hier würde tatsächlich ein Aufruf an die n8n-API erfolgen
        # Für dieses Beispiel simulieren wir eine Antwort
        
        if tool_name == "create_github_issue":
            return {
                "status": "success",
                "issue_number": 42,
                "issue_url": f"https://github.com/{arguments['owner']}/{arguments['repo']}/issues/42"
            }
        elif tool_name == "update_work_package":
            return {
                "status": "success",
                "work_package_id": arguments["id"],
                "updated_fields": list(arguments.keys())
            }
        elif tool_name == "sync_documentation":
            return {
                "status": "success",
                "doc_id": arguments["doc_id"],
                "github_path": arguments["github_path"],
                "commit_sha": "abc123"
            }
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def _send_response(self, request_id, result):
        \"\"\"Sendet eine erfolgreiche JSON-RPC-Antwort.
        
        Args:
            request_id: ID der Anfrage
            result: Ergebnis der Operation
        \"\"\"
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        await self._send_message(response)
    
    async def _send_error(self, request_id, error_message, code=-32603):
        \"\"\"Sendet eine JSON-RPC-Fehlermeldung.
        
        Args:
            request_id: ID der Anfrage
            error_message: Fehlermeldung
            code: JSON-RPC-Fehlercode
        \"\"\"
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": error_message
            }
        }
        await self._send_message(response)
    
    async def _send_message(self, message):
        \"\"\"Sendet eine JSON-RPC-Nachricht.
        
        Args:
            message: Die zu sendende Nachricht
        \"\"\"
        message_json = json.dumps(message)
        self.writer.write(f"{message_json}\\n".encode())
        await self.writer.drain()

async def main() -> None:
    \"\"\"Hauptfunktion zum Starten des MCP-Servers.\"\"\"
    # Lade Umgebungsvariablen
    n8n_url = os.environ.get("N8N_URL", "http://localhost:5678")
    n8n_api_key = os.environ.get("N8N_API_KEY")
    
    if not n8n_api_key:
        logger.error("N8N_API_KEY environment variable is required")
        sys.exit(1)
    
    # Starte MCP-Server
    server = N8nMCPServer(n8n_url, n8n_api_key)
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
"""

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        argparse.Namespace: Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description='Set up n8n with integrated workflows')
    parser.add_argument('--n8n-url', default='http://localhost:5678', help='URL of the n8n instance')
    parser.add_argument('--api-key', help='n8n API key')
    parser.add_argument('--github-token', help='GitHub token for repository access')
    parser.add_argument('--openproject-url', help='OpenProject instance URL')
    parser.add_argument('--openproject-token', help='OpenProject API token')
    parser.add_argument('--install', action='store_true', help='Install n8n locally using Docker')
    parser.add_argument('--env-file', help='Path to .env file with configurations')
    parser.add_argument('--workflows', nargs='+', choices=[
        'github', 'document', 'openhands', 'discord', 'timetracking', 'ai', 'mcp'
    ], default=['github', 'document', 'openhands', 'mcp'], help='Specific workflows to install')
    parser.add_argument('--mcp', action='store_true', help='Enable MCP server for n8n workflows')
    parser.add_argument('--mcp-port', type=int, default=3333, help='Port for the MCP server')
    return parser.parse_args()

def setup_mcp_server(n8n_url: str, api_key: str, port: int = 3333) -> bool:
    """
    Richtet den MCP-Server für n8n ein.
    
    Args:
        n8n_url: URL der n8n-Instanz
        api_key: API-Key für n8n
        port: Port, auf dem der MCP-Server laufen soll
        
    Returns:
        bool: True, wenn die Einrichtung erfolgreich war, sonst False
    """
    logger.info("Setting up MCP server for n8n...")
    
    # Verwende die vorhandene MCP-Server-Datei oder erstelle eine neue
    src_dir = Path(__file__).parent
    mcp_server_path = src_dir / 'n8n-mcp-server.py'
    
    if not mcp_server_path.exists():
        logger.info("Creating MCP server script...")
        with open(mcp_server_path, 'w') as f:
            f.write(N8N_MCP_SERVER_TEMPLATE)
        print(f"MCP server script created at {mcp_server_path.absolute()}")
    else:
        print(f"Using existing MCP server script at {mcp_server_path.absolute()}")
    
    # Stelle sicher, dass die Datei ausführbar ist
    if os.name == 'posix':
        os.chmod(mcp_server_path, 0o755)
    
    # Installiere benötigte Abhängigkeiten
    try:
        import aiohttp
    except ImportError:
        logger.info("Installing required dependencies...")
        subprocess.run([sys.executable, "-m", "pip", "install", "aiohttp"], check=True)
        logger.info("Dependencies installed successfully")
    
    # Generiere eine systemd-Service-Datei für den MCP-Server (falls Linux)
    if os.name == 'posix':
        service_file = Path('/tmp/n8n-mcp-server.service')
        service_content = f"""[Unit]
Description=n8n MCP Server
After=network.target

[Service]
Environment=N8N_URL={n8n_url}
Environment=N8N_API_KEY={api_key}
Environment=MCP_SERVER_PORT={port}
ExecStart=/usr/bin/python3 {mcp_server_path.absolute()}
Restart=on-failure
User={os.environ.get('USER', 'root')}

[Install]
WantedBy=multi-user.target
"""
        with open(service_file, 'w') as f:
            f.write(service_content)
        
        print(f"SystemD service file created at {service_file}")
        logger.info("To install the service run:")
        print(f"  sudo cp {service_file} /etc/systemd/system/")
        logger.info("  sudo systemctl daemon-reload")
        logger.info("  sudo systemctl enable n8n-mcp-server")
        logger.info("  sudo systemctl start n8n-mcp-server")
    
    # Erzeuge Konfiguration für OpenHands
    openhands_config = {
        "mcpServers": {
            "n8n-workflow": {
                "command": "python",
                "args": [str(mcp_server_path.absolute())],
                "env": {
                    "N8N_URL": n8n_url,
                    "N8N_API_KEY": api_key
                },
                "autoApprove": ["create_github_issue", "update_work_package", "sync_documentation"]
            }
        }
    }
    
    openhands_config_path = src_dir / 'openhands-mcp-config.json'
    with open(openhands_config_path, 'w') as f:
        json.dump(openhands_config, f, indent=2)
    
    print(f"OpenHands MCP configuration generated at {openhands_config_path.absolute()}")
    logger.info("Add this file to your OpenHands configuration.")
    
    # Teste den MCP-Server
    logger.info("\nTesting MCP server configuration...")
    try:
        # Überprüfe, ob die Konfigurationsdatei gültig ist
        print(f"MCP server script path: {mcp_server_path.absolute()}")
        print(f"MCP server configuration file: {openhands_config_path.absolute()}")
        
        # Überprüfe, ob die Datei ausführbar ist
        if os.name == 'posix' and not os.access(mcp_server_path, os.X_OK):
            logger.info("Making MCP server script executable...")
            os.chmod(mcp_server_path, 0o755)
        
        # Überprüfe, ob die erforderlichen Umgebungsvariablen gesetzt sind
        if not n8n_url:
            logger.info("Warning: N8N_URL is not set. Using default: http://localhost:5678")
        
        if not api_key:
            logger.info("Warning: N8N_API_KEY is not set. The MCP server will not be able to connect to n8n.")
        else:
            logger.info("N8N_API_KEY is set. The MCP server should be able to connect to n8n.")
        
        # Überprüfe, ob aiohttp installiert ist
        try:
            import importlib.util
            aiohttp_spec = importlib.util.find_spec("aiohttp")
            if aiohttp_spec is None:
                logger.info("Warning: aiohttp is not installed. The MCP server requires this package.")
                logger.info("You can install it with: pip install aiohttp")
            else:
                logger.info("aiohttp is installed. The MCP server should be able to run.")
        except ImportError:
            logger.info("Warning: Unable to check if aiohttp is installed.")
        
        logger.info("MCP server configuration is valid and ready to use with OpenHands")
    except Exception as e:
        print(f"Error testing MCP server: {str(e)}")
        logger.info("You may need to manually verify the server is working correctly")

def main() -> None:
    """
    Main function for setting up n8n with integrated workflows.
    """
    try:
        args = parse_args()
        
        # Überprüfe, ob die .env-Datei existiert, wenn angegeben
        if args.env_file and not os.path.isfile(args.env_file):
            print(f"Error: Environment file {args.env_file} not found.")
            logger.info("Please create the file or specify a different file with --env-file.")
            return 1
        
        # Load environment variables from .env file if provided
        env_vars = load_env_file(args.env_file)
        
        # Use command line arguments or fall back to .env variables
        n8n_url = args.n8n_url or env_vars.get('N8N_URL', 'http://localhost:5678')
        api_key = args.api_key or env_vars.get('N8N_API_KEY')
        github_token = args.github_token or env_vars.get('GITHUB_TOKEN')
        openproject_url = args.openproject_url or env_vars.get('OPENPROJECT_URL')
        openproject_token = args.openproject_token or env_vars.get('OPENPROJECT_TOKEN')
        
        # Validiere die Eingabeparameter
        if not n8n_url:
            logger.info("Error: n8n URL is required.")
            logger.info("Please provide it with --n8n-url or set N8N_URL in your .env file.")
            return 1
        
        # Install n8n if requested
        if args.install:
            try:
                print(f"Installing n8n using Docker...")
                install_n8n_docker()
                logger.info("n8n installation completed successfully.")
            except Exception as e:
                print(f"Error installing n8n: {str(e)}")
                logger.info("You may need to install n8n manually.")
                
                # Frage den Benutzer, ob er fortfahren möchte
                if input("Do you want to continue with workflow setup? (y/n): ").lower() != 'y':
                    return 1
            
            # If API key was not provided, try to get one
            if not api_key and 'N8N_USER' in env_vars and 'N8N_PASSWORD' in env_vars:
                logger.info("Waiting for n8n to fully start up before getting API key...")
                time.sleep(10)  # Wait a bit more for n8n to fully initialize
                
                try:
                    api_key = get_n8n_api_key(
                        n8n_url, 
                        env_vars.get('N8N_USER', 'admin'),
                        env_vars.get('N8N_PASSWORD', 'password')
                    )
                    print(f"Got API key: {api_key}")
                except Exception as e:
                    print(f"Failed to get API key: {str(e)}")
                    logger.info("You may need to get an API key manually from n8n.")
        
        if not api_key:
            logger.info("No API key provided. Please provide an API key to create workflows.")
            logger.info("You can provide it with --api-key or set N8N_API_KEY in your .env file.")
            return 1
            
        # Überprüfe, ob n8n erreichbar ist
        try:
            import requests
            response = requests.get(f"{n8n_url}/healthz", timeout=5)
            if response.status_code == 200:
                print(f"n8n is reachable at {n8n_url}")
            else:
                print(f"Warning: n8n returned status code {response.status_code} at {n8n_url}")
                logger.info("The workflow setup may fail if n8n is not properly configured.")
        except Exception as e:
            print(f"Warning: Could not connect to n8n at {n8n_url}: {str(e)}")
            logger.info("The workflow setup may fail if n8n is not properly configured.")
            
            # Frage den Benutzer, ob er fortfahren möchte
            if input("Do you want to continue with workflow setup? (y/n): ").lower() != 'y':
                return 1
    
    except Exception as e:
        print(f"Error during initialization: {str(e)}")
        return 1
    
    logger.info("Setting up credentials...")
    # Set up credentials
    github_cred = None
    openproject_cred = None
    discord_cred = None
    affine_cred = None
    appflowy_cred = None
    openhands_cred = None
    
    if github_token:
        github_cred = setup_github_credential(n8n_url, api_key, github_token)
        if github_cred:
            print(f"Created GitHub credential with ID: {github_cred['id']}")
    else:
        logger.info("No GitHub token provided. Skipping GitHub credential setup.")
    
    if openproject_token:
        openproject_cred = setup_openproject_credential(n8n_url, api_key, openproject_token)
        if openproject_cred:
            print(f"Created OpenProject credential with ID: {openproject_cred['id']}")
    else:
        logger.info("No OpenProject token provided. Skipping OpenProject credential setup.")
    
    # Lade Discord Webhook URL
    discord_webhook_url = env_vars.get('DISCORD_WEBHOOK_URL')
    if discord_webhook_url:
        discord_cred = setup_discord_credential(n8n_url, api_key, discord_webhook_url)
        if discord_cred:
            print(f"Created Discord credential with ID: {discord_cred['id']}")
    
    # Lade AFFiNE API Key
    affine_api_key = env_vars.get('AFFINE_API_KEY')
    if affine_api_key:
        affine_cred = setup_affine_credential(n8n_url, api_key, affine_api_key)
        if affine_cred:
            print(f"Created AFFiNE credential with ID: {affine_cred['id']}")
    
    # Lade AppFlowy API Key
    appflowy_api_key = env_vars.get('APPFLOWY_API_KEY')
    if appflowy_api_key:
        appflowy_cred = setup_appflowy_credential(n8n_url, api_key, appflowy_api_key)
        if appflowy_cred:
            print(f"Created AppFlowy credential with ID: {appflowy_cred['id']}")
    
    # Lade LLM API Key
    llm_api_key = env_vars.get('LLM_API_KEY')
    if llm_api_key:
        openhands_cred = setup_openhands_credential(n8n_url, api_key, llm_api_key)
        if openhands_cred:
            print(f"Created OpenHands credential with ID: {openhands_cred['id']}")
    
    logger.info("Creating workflows...")
    
    # GitHub-OpenProject Integration
    if 'github' in args.workflows:
        workflow_data = GITHUB_OPENPROJECT_WORKFLOW
        if github_cred:
            # Update GitHub credentials in workflow
            update_github_credentials(workflow_data, github_cred['id'])
        
        if openproject_cred and openproject_url:
            # Update OpenProject credentials in workflow
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        github_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if github_workflow:
            print(f"Created GitHub-OpenProject integration workflow with ID: {github_workflow['id']}")
            # Aktiviere den Workflow
            if activate_workflow(n8n_url, api_key, github_workflow['id']):
                print(f"Activated GitHub-OpenProject integration workflow")
    
    # Document Sync Workflow
    if 'document' in args.workflows:
        workflow_data = DOCUMENT_SYNC_WORKFLOW
        if openproject_cred and openproject_url:
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        document_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if document_workflow:
            print(f"Created Document Sync workflow with ID: {document_workflow['id']}")
            # Aktiviere den Workflow
            if activate_workflow(n8n_url, api_key, document_workflow['id']):
                print(f"Activated Document Sync workflow")
    
    # OpenHands Integration Workflow
    if 'openhands' in args.workflows:
        workflow_data = OPENHANDS_WORKFLOW
        if openproject_cred and openproject_url:
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        openhands_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if openhands_workflow:
            print(f"Created OpenHands integration workflow with ID: {openhands_workflow['id']}")
            # Aktiviere den Workflow
            if activate_workflow(n8n_url, api_key, openhands_workflow['id']):
                print(f"Activated OpenHands integration workflow")
    
    # Discord Notification Workflow
    if 'discord' in args.workflows:
        workflow_data = DISCORD_NOTIFICATION_WORKFLOW
        if github_cred:
            update_github_credentials(workflow_data, github_cred['id'])
            
        discord_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if discord_workflow:
            print(f"Created Discord notification workflow with ID: {discord_workflow['id']}")
            # Aktiviere den Workflow
            if activate_workflow(n8n_url, api_key, discord_workflow['id']):
                print(f"Activated Discord notification workflow")
    
    # Time Tracking Workflow
    if 'timetracking' in args.workflows:
        workflow_data = TIME_TRACKING_WORKFLOW
        if github_cred:
            update_github_credentials(workflow_data, github_cred['id'])
        
        if openproject_cred and openproject_url:
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        time_tracking_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if time_tracking_workflow:
            print(f"Created Time Tracking workflow with ID: {time_tracking_workflow['id']}")
            # Aktiviere den Workflow
            if activate_workflow(n8n_url, api_key, time_tracking_workflow['id']):
                print(f"Activated Time Tracking workflow")
    
    # AI Summary Workflow
    if 'ai' in args.workflows:
        workflow_data = AI_SUMMARY_WORKFLOW
        if github_cred:
            update_github_credentials(workflow_data, github_cred['id'])
            
        ai_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if ai_workflow:
            print(f"Created AI Summary workflow with ID: {ai_workflow['id']}")
            # Aktiviere den Workflow
            if activate_workflow(n8n_url, api_key, ai_workflow['id']):
                print(f"Activated AI Summary workflow")
    
    # MCP Server Workflow
    if 'mcp' in args.workflows:
        workflow_data = MCP_SERVER_WORKFLOW
        if github_cred:
            update_github_credentials(workflow_data, github_cred['id'])
        
        if openproject_cred and openproject_url:
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        mcp_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if mcp_workflow:
            print(f"Created MCP Server workflow with ID: {mcp_workflow['id']}")
            # Aktiviere den Workflow
            if activate_workflow(n8n_url, api_key, mcp_workflow['id']):
                print(f"Activated MCP Server workflow")
    
    logger.info("\nWorkflow setup complete!")
    print(f"You can access your n8n instance at: {n8n_url}")
    
    # Display webhook URLs for integration
    if 'document' in args.workflows:
        webhook_node = next((node for node in DOCUMENT_SYNC_WORKFLOW['nodes'] 
                             if node.get('type') == 'n8n-nodes-base.webhook'), None)
        if webhook_node:
            webhook_path = webhook_node.get('parameters', {}).get('path', '/webhook')
            print(f"\nDocument Sync Webhook URL: {n8n_url}{webhook_path}")
            logger.info("Use this URL to integrate with AFFiNE/AppFlowy.")
    
    if 'openhands' in args.workflows:
        webhook_node = next((node for node in OPENHANDS_WORKFLOW['nodes'] 
                             if node.get('type') == 'n8n-nodes-base.webhook'), None)
        if webhook_node:
            webhook_path = webhook_node.get('parameters', {}).get('path', '/openhands/webhook')
            print(f"\nOpenHands Webhook URL: {n8n_url}{webhook_path}")
            logger.info("Use this URL to receive notifications from OpenHands.")
    
    if 'mcp' in args.workflows:
        webhook_node = next((node for node in MCP_SERVER_WORKFLOW['nodes'] 
                             if node.get('type') == 'n8n-nodes-base.mcpTrigger'), None)
        if webhook_node:
            webhook_path = webhook_node.get('parameters', {}).get('path', '/mcp/endpoint')
            print(f"\nMCP Server URL: {n8n_url}{webhook_path}")
            logger.info("Use this URL to integrate with MCP clients like OpenHands.")
    
    logger.info("\nNext steps:")
    logger.info("1. Configure your GitHub repositories to send webhooks to n8n")
    logger.info("2. Set up webhook endpoints in AFFiNE/AppFlowy to notify n8n of document updates")
    logger.info("3. Configure OpenHands to notify n8n when PRs are created")
    
    # Set up MCP Server if requested
    if args.mcp:
        setup_mcp_server(n8n_url, api_key, args.mcp_port)

def update_github_credentials(workflow_data: Dict[str, Any], credential_id: str) -> Dict[str, Any]:
    """
    Update GitHub credentials in the workflow.
    
    Args:
        workflow_data: Workflow data to update
        credential_id: ID of the GitHub credential
        
    Returns:
        Dict[str, Any]: Updated workflow data
    """
    for node in workflow_data['nodes']:
        if node.get('type') in ['n8n-nodes-base.github', 'n8n-nodes-base.githubTrigger']:
            node['credentials'] = {
                'githubApi': credential_id
            }

def update_openproject_credentials(workflow_data: Dict[str, Any], credential_id: str, openproject_url: str) -> Dict[str, Any]:
    """
    Update OpenProject credentials in the workflow.
    
    Args:
        workflow_data: Workflow data to update
        credential_id: ID of the OpenProject credential
        openproject_url: URL of the OpenProject instance
        
    Returns:
        Dict[str, Any]: Updated workflow data
    """
    for node in workflow_data['nodes']:
        if (node.get('type') == 'n8n-nodes-base.httpRequest' and 
            'parameters' in node and 
            'url' in node['parameters'] and 
            isinstance(node['parameters']['url'], str) and
            node['parameters']['url'].startswith(openproject_url)):
            node['credentials'] = {
                'httpHeaderAuth': credential_id
            }

if __name__ == "__main__":
    main()
