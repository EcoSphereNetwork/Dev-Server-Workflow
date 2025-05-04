#!/usr/bin/env python3
"""
n8n MCP Server

Implementiert einen Model Context Protocol (MCP) Server für n8n, der es KI-Agenten 
ermöglicht, n8n-Workflows als Tools zu verwenden.
"""

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
        self.tools = self._load_available_tools()
        
    def _load_available_tools(self):
        """Lädt verfügbare n8n-Workflows als Tools."""
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
        """Startet den MCP-Server und verarbeitet Standard-Ein/Ausgabe nach dem MCP-Protokoll."""
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
    await server.start()

if __name__ == "__main__":
    asyncio.run(main())
