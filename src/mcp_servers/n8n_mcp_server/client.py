"""
MCP-Client-Modul für die Kommunikation mit MCP-Servern.

Dieses Modul bietet Funktionen zur Kommunikation mit MCP-Servern über das JSON-RPC-Protokoll.
"""

import json
import logging
import aiohttp
import asyncio
from typing import Dict, List, Any, Optional, Tuple, Union

from .error_handling import MCPConnectionError, MCPServerError
from .utils.logger import logger

class MCPClient:
    """Client für die Kommunikation mit MCP-Servern."""
    
    def __init__(self, server_url: str, api_key: Optional[str] = None, timeout: int = 30):
        """
        Initialisiere den MCP-Client.
        
        Args:
            server_url: URL des MCP-Servers
            api_key: API-Schlüssel für die Authentifizierung (optional)
            timeout: Timeout für Anfragen in Sekunden
        """
        self.server_url = server_url
        self.api_key = api_key
        self.timeout = timeout
        self.session = None
        self.request_id = 0
    
    async def _ensure_session(self):
        """Stelle sicher, dass eine HTTP-Session existiert."""
        if self.session is None or self.session.closed:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self.session = aiohttp.ClientSession(headers=headers)
    
    async def close(self):
        """Schließe die HTTP-Session."""
        if self.session and not self.session.closed:
            await self.session.close()
            self.session = None
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe ein Tool auf dem MCP-Server auf.
        
        Args:
            tool_name: Name des Tools
            arguments: Argumente für das Tool
            
        Returns:
            Ergebnis des Tool-Aufrufs
            
        Raises:
            MCPConnectionError: Wenn keine Verbindung zum Server hergestellt werden kann
            MCPServerError: Wenn der Server einen Fehler zurückgibt
        """
        await self._ensure_session()
        self.request_id += 1
        
        # Erstelle die JSON-RPC-Anfrage
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "mcp.callTool",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            async with self.session.post(
                self.server_url,
                json=request,
                timeout=self.timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise MCPServerError(f"HTTP error {response.status}: {error_text}")
                
                result = await response.json()
                
                # Überprüfe auf JSON-RPC-Fehler
                if "error" in result:
                    error = result["error"]
                    raise MCPServerError(f"JSON-RPC error {error.get('code')}: {error.get('message')}")
                
                return result.get("result", {})
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Connection error: {str(e)}")
        except asyncio.TimeoutError:
            raise MCPConnectionError(f"Request timed out after {self.timeout} seconds")
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        Liste alle verfügbaren Tools auf dem MCP-Server auf.
        
        Returns:
            Liste der verfügbaren Tools
            
        Raises:
            MCPConnectionError: Wenn keine Verbindung zum Server hergestellt werden kann
            MCPServerError: Wenn der Server einen Fehler zurückgibt
        """
        await self._ensure_session()
        self.request_id += 1
        
        # Erstelle die JSON-RPC-Anfrage
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": "mcp.listTools"
        }
        
        try:
            async with self.session.post(
                self.server_url,
                json=request,
                timeout=self.timeout
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    raise MCPServerError(f"HTTP error {response.status}: {error_text}")
                
                result = await response.json()
                
                # Überprüfe auf JSON-RPC-Fehler
                if "error" in result:
                    error = result["error"]
                    raise MCPServerError(f"JSON-RPC error {error.get('code')}: {error.get('message')}")
                
                return result.get("result", [])
        except aiohttp.ClientError as e:
            raise MCPConnectionError(f"Connection error: {str(e)}")
        except asyncio.TimeoutError:
            raise MCPConnectionError(f"Request timed out after {self.timeout} seconds")
    
    async def test_connection(self) -> Tuple[bool, str]:
        """
        Teste die Verbindung zum MCP-Server.
        
        Returns:
            Tuple mit (Erfolgreich, Nachricht)
        """
        try:
            tools = await self.list_tools()
            return True, f"Verbindung erfolgreich. {len(tools)} Tools verfügbar."
        except Exception as e:
            return False, f"Verbindungsfehler: {str(e)}"
