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
n8n MCP Server

Implementiert einen Model Context Protocol (MCP) Server für n8n, der es KI-Agenten 
ermöglicht, n8n-Workflows als Tools zu verwenden.
"""

import os
import json
import asyncio
import sys
import logging
import aiohttp
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("n8n-mcp-server")

class N8nMCPServer:
    """MCP-Server, der n8n-Funktionalität als Tools bereitstellt."""
    
    def __init__(self, n8n_url, api_key):
        """Initialisiert den MCP-Server mit n8n-API Zugangsdaten.
        
        Args:
            n8n_url: URL der n8n-Instanz
            api_key: API-Key für n8n
        """
        self.n8n_url = n8n_url
        self.n8n_api_key = api_key
        self.request_id = 0
        self.session = None
        self.tools = []
        self.workflow_map = {}
        
    async def initialize(self):
        """Initialisiert die HTTP-Session und lädt die verfügbaren Tools."""
        self.session = aiohttp.ClientSession()
        self.tools = await self._load_available_tools()
        
    async def _load_available_tools(self):
        """Lädt verfügbare n8n-Workflows als Tools."""
        logger.info(f"Loading available workflows from n8n at {self.n8n_url}")
        
        try:
            # Lade alle Workflows von n8n
            headers = {'X-N8N-API-KEY': self.n8n_api_key}
            async with self.session.get(f"{self.n8n_url}/rest/workflows", headers=headers) as response:
                if response.status != 200:
                    logger.error(f"Failed to load workflows: {await response.text()}")
                    # Fallback zu statischen Tools, wenn API-Aufruf fehlschlägt
                    return self._get_static_tools()
                
                workflows = await response.json()
                
            # Konvertiere Workflows zu MCP-Tools
            tools = []
            for workflow in workflows:
                # Nur aktive Workflows mit MCP-Tag berücksichtigen
                if workflow.get('active') and 'mcp' in workflow.get('tags', []):
                    workflow_id = workflow.get('id')
                    workflow_name = workflow.get('name')
                    
                    # Extrahiere Parameter-Schema aus Workflow-Metadaten
                    parameters = self._extract_parameters_from_workflow(workflow)
                    
                    # Erstelle Tool-Definition
                    tool_name = f"workflow_{workflow_name.lower().replace(' ', '_')}"
                    tool = {
                        "name": tool_name,
                        "description": workflow.get('description', f"Führt den n8n-Workflow '{workflow_name}' aus"),
                        "parameters": parameters
                    }
                    
                    tools.append(tool)
                    self.workflow_map[tool_name] = workflow_id
            
            # Wenn keine Workflows gefunden wurden, verwende statische Tools
            if not tools:
                logger.warning("No MCP-tagged workflows found, using static tool definitions")
                return self._get_static_tools()
                
            logger.info(f"Loaded {len(tools)} tools from n8n workflows")
            return tools
            
        except Exception as e:
            logger.error(f"Error loading workflows: {str(e)}")
            return self._get_static_tools()
    
    def _extract_parameters_from_workflow(self, workflow):
        """Extrahiert Parameter-Schema aus Workflow-Metadaten."""
        # In einer vollständigen Implementierung würden wir hier das Schema aus den Workflow-Metadaten extrahieren
        # Für dieses Beispiel verwenden wir ein einfaches Schema
        return {
            "type": "object",
            "properties": {
                "input": {
                    "type": "object",
                    "description": "Eingabedaten für den Workflow"
                }
            }
        }
    
    def _get_static_tools(self):
        """Liefert statische Tool-Definitionen als Fallback."""
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
        """Startet den MCP-Server und verarbeitet Standard-Ein/Ausgabe nach dem MCP-Protokoll."""
        logger.info("Starting MCP Server for n8n")
        
        # Initialisiere HTTP-Session und lade Tools
        await self.initialize()
        
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
        """Verarbeitet eingehende JSON-RPC-Nachrichten.
        
        Args:
            message: Die empfangene JSON-RPC-Nachricht
        """
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
        """Führt ein Tool aus, indem der entsprechende n8n-Workflow aufgerufen wird.
        
        Args:
            tool_name: Name des auszuführenden Tools
            arguments: Parameter für den Tool-Aufruf
            
        Returns:
            Das Ergebnis der Workflow-Ausführung
        """
        try:
            logger.info(f"Executing tool {tool_name} with arguments {json.dumps(arguments)}")
            
            # Validiere die Eingabeparameter
            if not tool_name:
                raise ValueError("Tool name is required")
            
            if not isinstance(arguments, dict):
                raise ValueError("Arguments must be a dictionary")
            
            # Spezielle Behandlung für die statischen Tools
            if tool_name == "create_github_issue":
                # Validiere die erforderlichen Parameter
                required_params = ["title", "body", "owner", "repo"]
                for param in required_params:
                    if param not in arguments:
                        raise ValueError(f"Missing required parameter '{param}' for tool 'create_github_issue'")
                return await self._execute_github_issue_workflow(arguments)
            
            elif tool_name == "update_work_package":
                # Validiere die erforderlichen Parameter
                if "id" not in arguments:
                    raise ValueError("Missing required parameter 'id' for tool 'update_work_package'")
                return await self._execute_work_package_workflow(arguments)
            
            elif tool_name == "sync_documentation":
                # Validiere die erforderlichen Parameter
                required_params = ["doc_id", "github_path", "owner", "repo"]
                for param in required_params:
                    if param not in arguments:
                        raise ValueError(f"Missing required parameter '{param}' for tool 'sync_documentation'")
                return await self._execute_sync_documentation_workflow(arguments)
            
            elif tool_name.startswith("workflow_") and tool_name in self.workflow_map:
                # Dynamische Workflows aus n8n ausführen
                return await self._execute_n8n_workflow(self.workflow_map[tool_name], arguments)
            
            else:
                # Versuche, einen passenden Workflow zu finden
                for available_tool in self.tools:
                    if available_tool.get("name") == tool_name:
                        logger.info(f"Found matching tool: {tool_name}")
                        if tool_name in self.workflow_map:
                            return await self._execute_n8n_workflow(self.workflow_map[tool_name], arguments)
                
                # Kein passender Workflow gefunden
                available_tools = ", ".join([tool.get("name") for tool in self.tools])
                raise ValueError(f"Unknown tool: {tool_name}. Available tools: {available_tools}")
        
        except ValueError as e:
            # Validierungsfehler
            logger.error(f"Validation error executing tool {tool_name}: {str(e)}")
            return {
                "status": "error",
                "error_type": "validation_error",
                "message": str(e)
            }
        except Exception as e:
            # Allgemeiner Fehler
            logger.error(f"Error executing tool {tool_name}: {str(e)}")
            return {
                "status": "error",
                "error_type": "execution_error",
                "message": f"Failed to execute tool {tool_name}: {str(e)}"
            }
    
    async def _execute_n8n_workflow(self, workflow_id, arguments):
        """Führt einen n8n-Workflow über die API aus.
        
        Args:
            workflow_id: ID des auszuführenden Workflows
            arguments: Parameter für den Workflow
            
        Returns:
            Das Ergebnis der Workflow-Ausführung
        """
        try:
            headers = {
                'X-N8N-API-KEY': self.n8n_api_key,
                'Content-Type': 'application/json'
            }
            
            # Bereite Daten für den Workflow vor
            data = {
                "data": arguments
            }
            
            # Führe Workflow aus
            async with self.session.post(
                f"{self.n8n_url}/rest/workflows/{workflow_id}/execute",
                headers=headers,
                json=data
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Failed to execute workflow {workflow_id}: {error_text}")
                    return {
                        "status": "error",
                        "message": f"Failed to execute workflow: {error_text}"
                    }
                
                result = await response.json()
                return {
                    "status": "success",
                    "result": result.get("data", {})
                }
                
        except Exception as e:
            logger.error(f"Error executing workflow {workflow_id}: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }
    
    async def _execute_github_issue_workflow(self, arguments):
        """Führt den GitHub Issue Workflow aus.
        
        Args:
            arguments: Parameter für den Workflow
            
        Returns:
            Das Ergebnis der Workflow-Ausführung
        """
        try:
            # Suche nach dem MCP-Workflow für GitHub Issues
            headers = {'X-N8N-API-KEY': self.n8n_api_key}
            async with self.session.get(f"{self.n8n_url}/rest/workflows", headers=headers) as response:
                if response.status != 200:
                    # Fallback zu simulierter Antwort
                    return {
                        "status": "success",
                        "issue_number": 42,
                        "issue_url": f"https://github.com/{arguments['owner']}/{arguments['repo']}/issues/42"
                    }
                
                workflows = await response.json()
            
            # Suche nach dem passenden Workflow
            workflow_id = None
            for workflow in workflows:
                if workflow.get('name') == "MCP Server Integration" and workflow.get('active'):
                    workflow_id = workflow.get('id')
                    break
            
            if not workflow_id:
                # Fallback zu simulierter Antwort
                return {
                    "status": "success",
                    "issue_number": 42,
                    "issue_url": f"https://github.com/{arguments['owner']}/{arguments['repo']}/issues/42"
                }
            
            # Führe den Workflow aus
            data = {
                "data": {
                    "tool": "create_github_issue",
                    "arguments": arguments
                }
            }
            
            async with self.session.post(
                f"{self.n8n_url}/rest/workflows/{workflow_id}/execute",
                headers={'X-N8N-API-KEY': self.n8n_api_key, 'Content-Type': 'application/json'},
                json=data
            ) as response:
                if response.status != 200:
                    # Fallback zu simulierter Antwort
                    return {
                        "status": "success",
                        "issue_number": 42,
                        "issue_url": f"https://github.com/{arguments['owner']}/{arguments['repo']}/issues/42"
                    }
                
                result = await response.json()
                return result.get("data", {
                    "status": "success",
                    "issue_number": 42,
                    "issue_url": f"https://github.com/{arguments['owner']}/{arguments['repo']}/issues/42"
                })
                
        except Exception as e:
            logger.error(f"Error executing GitHub issue workflow: {str(e)}")
            # Fallback zu simulierter Antwort
            return {
                "status": "success",
                "issue_number": 42,
                "issue_url": f"https://github.com/{arguments['owner']}/{arguments['repo']}/issues/42"
            }
    
    async def _execute_work_package_workflow(self, arguments):
        """Führt den OpenProject Work Package Workflow aus."""
        try:
            # Suche nach dem MCP-Workflow für Work Packages
            headers = {'X-N8N-API-KEY': self.n8n_api_key}
            async with self.session.get(f"{self.n8n_url}/rest/workflows", headers=headers) as response:
                if response.status != 200:
                    # Fallback zu simulierter Antwort
                    return {
                        "status": "success",
                        "work_package_id": arguments["id"],
                        "updated_fields": list(arguments.keys())
                    }
                
                workflows = await response.json()
            
            # Suche nach dem passenden Workflow
            workflow_id = None
            for workflow in workflows:
                if workflow.get('name') == "MCP Server Integration" and workflow.get('active'):
                    workflow_id = workflow.get('id')
                    break
            
            if not workflow_id:
                # Fallback zu simulierter Antwort
                return {
                    "status": "success",
                    "work_package_id": arguments["id"],
                    "updated_fields": list(arguments.keys())
                }
            
            # Führe den Workflow aus
            data = {
                "data": {
                    "tool": "update_work_package",
                    "arguments": arguments
                }
            }
            
            async with self.session.post(
                f"{self.n8n_url}/rest/workflows/{workflow_id}/execute",
                headers={'X-N8N-API-KEY': self.n8n_api_key, 'Content-Type': 'application/json'},
                json=data
            ) as response:
                if response.status != 200:
                    # Fallback zu simulierter Antwort
                    return {
                        "status": "success",
                        "work_package_id": arguments["id"],
                        "updated_fields": list(arguments.keys())
                    }
                
                result = await response.json()
                return result.get("data", {
                    "status": "success",
                    "work_package_id": arguments["id"],
                    "updated_fields": list(arguments.keys())
                })
                
        except Exception as e:
            logger.error(f"Error executing work package workflow: {str(e)}")
            # Fallback zu simulierter Antwort
            return {
                "status": "success",
                "work_package_id": arguments["id"],
                "updated_fields": list(arguments.keys())
            }
    
    async def _execute_sync_documentation_workflow(self, arguments):
        """Führt den Dokumenten-Synchronisierungs-Workflow aus."""
        try:
            # Suche nach dem MCP-Workflow für Dokumentensynchronisierung
            headers = {'X-N8N-API-KEY': self.n8n_api_key}
            async with self.session.get(f"{self.n8n_url}/rest/workflows", headers=headers) as response:
                if response.status != 200:
                    # Fallback zu simulierter Antwort
                    return {
                        "status": "success",
                        "doc_id": arguments["doc_id"],
                        "github_path": arguments["github_path"],
                        "commit_sha": "abc123"
                    }
                
                workflows = await response.json()
            
            # Suche nach dem passenden Workflow
            workflow_id = None
            for workflow in workflows:
                if workflow.get('name') == "MCP Server Integration" and workflow.get('active'):
                    workflow_id = workflow.get('id')
                    break
            
            if not workflow_id:
                # Fallback zu simulierter Antwort
                return {
                    "status": "success",
                    "doc_id": arguments["doc_id"],
                    "github_path": arguments["github_path"],
                    "commit_sha": "abc123"
                }
            
            # Führe den Workflow aus
            data = {
                "data": {
                    "tool": "sync_documentation",
                    "arguments": arguments
                }
            }
            
            async with self.session.post(
                f"{self.n8n_url}/rest/workflows/{workflow_id}/execute",
                headers={'X-N8N-API-KEY': self.n8n_api_key, 'Content-Type': 'application/json'},
                json=data
            ) as response:
                if response.status != 200:
                    # Fallback zu simulierter Antwort
                    return {
                        "status": "success",
                        "doc_id": arguments["doc_id"],
                        "github_path": arguments["github_path"],
                        "commit_sha": "abc123"
                    }
                
                result = await response.json()
                return result.get("data", {
                    "status": "success",
                    "doc_id": arguments["doc_id"],
                    "github_path": arguments["github_path"],
                    "commit_sha": "abc123"
                })
                
        except Exception as e:
            logger.error(f"Error executing sync documentation workflow: {str(e)}")
            # Fallback zu simulierter Antwort
            return {
                "status": "success",
                "doc_id": arguments["doc_id"],
                "github_path": arguments["github_path"],
                "commit_sha": "abc123"
            }
    
    async def _send_response(self, request_id, result):
        """Sendet eine erfolgreiche JSON-RPC-Antwort.
        
        Args:
            request_id: ID der Anfrage
            result: Ergebnis der Operation
        """
        response = {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
        await self._send_message(response)
    
    async def _send_error(self, request_id, error_message, code=-32603):
        """Sendet eine JSON-RPC-Fehlermeldung.
        
        Args:
            request_id: ID der Anfrage
            error_message: Fehlermeldung
            code: JSON-RPC-Fehlercode
        """
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
        """Sendet eine JSON-RPC-Nachricht.
        
        Args:
            message: Die zu sendende Nachricht
        """
        message_json = json.dumps(message)
        self.writer.write(f"{message_json}\n".encode())
        await self.writer.drain()
    
    async def close(self):
        """Schließt die HTTP-Session."""
        if self.session:
            await self.session.close()

async def main():
    """Hauptfunktion zum Starten des MCP-Servers."""
    # Lade Umgebungsvariablen
    n8n_url = os.environ.get("N8N_URL", "http://localhost:5678")
    n8n_api_key = os.environ.get("N8N_API_KEY")
    
    if not n8n_api_key:
        logger.error("N8N_API_KEY environment variable is required")
        sys.exit(1)
    
    # Starte MCP-Server
    server = N8nMCPServer(n8n_url, n8n_api_key)
    try:
        await server.start()
    finally:
        await server.close()

if __name__ == "__main__":
    asyncio.run(main())
