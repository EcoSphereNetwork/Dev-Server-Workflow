#!/usr/bin/env python3
"""
MCP Client

Ein Client für das Model Context Protocol (MCP), der mit MCP-Servern kommunizieren kann.
"""

import os
import json
import asyncio
import sys
import logging
import aiohttp
import argparse
import subprocess
from pathlib import Path

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("mcp-client.log")
    ]
)
logger = logging.getLogger("mcp-client")

class MCPClient:
    """Ein Client für das Model Context Protocol (MCP)."""

    def __init__(self, transport_type='stdio', **kwargs):
        """Initialisiert den MCP-Client.

        Args:
            transport_type: Art des Transports ('stdio', 'http', 'sse')
            **kwargs: Weitere Parameter je nach Transport-Typ
        """
        self.transport_type = transport_type
        self.kwargs = kwargs
        self.request_id = 0
        self.process = None
        self.session = None
        self.tools = []

    async def connect(self):
        """Stellt eine Verbindung zum MCP-Server her."""
        if self.transport_type == 'stdio':
            await self._connect_stdio()
        elif self.transport_type == 'http':
            await self._connect_http()
        elif self.transport_type == 'sse':
            await self._connect_sse()
        else:
            raise ValueError(f"Unbekannter Transport-Typ: {self.transport_type}")

    async def _connect_stdio(self):
        """Stellt eine Verbindung über stdio her."""
        command = self.kwargs.get('command')
        args = self.kwargs.get('args', [])
        env = self.kwargs.get('env', {})
        
        if not command:
            raise ValueError("Kein Befehl für stdio-Transport angegeben")
        
        # Umgebungsvariablen vorbereiten
        full_env = os.environ.copy()
        full_env.update(env)
        
        logger.info(f"Starte Prozess: {command} {' '.join(args)}")
        
        self.process = await asyncio.create_subprocess_exec(
            command, *args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env=full_env
        )
        
        # Starte einen Task zum Lesen von stderr
        asyncio.create_task(self._read_stderr())

    async def _read_stderr(self):
        """Liest Fehlerausgaben des Prozesses."""
        while True:
            line = await self.process.stderr.readline()
            if not line:
                break
            logger.warning(f"Server stderr: {line.decode().strip()}")

    async def _connect_http(self):
        """Stellt eine Verbindung über HTTP her."""
        url = self.kwargs.get('url')
        headers = self.kwargs.get('headers', {})
        
        if not url:
            raise ValueError("Keine URL für HTTP-Transport angegeben")
        
        # Authentifizierung hinzufügen, falls vorhanden
        auth = self.kwargs.get('auth', {})
        if auth:
            auth_type = auth.get('type')
            if auth_type == 'bearer':
                headers['Authorization'] = f"Bearer {auth.get('token', '')}"
            elif auth_type == 'basic':
                # Basic Auth wird von aiohttp automatisch behandelt
                pass
        
        self.session = aiohttp.ClientSession(headers=headers)
        self.url = url

    async def _connect_sse(self):
        """Stellt eine Verbindung über Server-Sent Events (SSE) her."""
        # SSE ist für Anfragen nicht geeignet, nur für Ereignisse
        # Wir verwenden HTTP für Anfragen
        await self._connect_http()

    async def disconnect(self):
        """Trennt die Verbindung zum MCP-Server."""
        if self.transport_type == 'stdio' and self.process:
            self.process.terminate()
            await self.process.wait()
            self.process = None
        elif (self.transport_type == 'http' or self.transport_type == 'sse') and self.session:
            await self.session.close()
            self.session = None

    async def list_tools(self):
        """Listet alle verfügbaren Tools auf.

        Returns:
            Liste der verfügbaren Tools
        """
        result = await self.send_request('mcp.listTools')
        self.tools = result
        return result

    async def call_tool(self, tool_name, arguments=None):
        """Ruft ein Tool auf.

        Args:
            tool_name: Name des aufzurufenden Tools
            arguments: Argumente für das Tool

        Returns:
            Ergebnis des Werkzeugaufrufs
        """
        return await self.send_request('mcp.callTool', {
            'name': tool_name,
            'arguments': arguments or {}
        })

    async def send_request(self, method, params=None):
        """Sendet eine Anfrage an den MCP-Server.

        Args:
            method: Name der aufzurufenden Methode
            params: Parameter für die Methode

        Returns:
            Ergebnis der Anfrage
        """
        self.request_id += 1
        request = {
            'jsonrpc': '2.0',
            'id': self.request_id,
            'method': method,
            'params': params or {}
        }
        
        if self.transport_type == 'stdio':
            return await self._send_stdio_request(request)
        elif self.transport_type == 'http' or self.transport_type == 'sse':
            return await self._send_http_request(request)

    async def _send_stdio_request(self, request):
        """Sendet eine Anfrage über stdio.

        Args:
            request: Die zu sendende Anfrage

        Returns:
            Ergebnis der Anfrage
        """
        if not self.process:
            raise RuntimeError("Keine Verbindung zum Server")
        
        request_str = json.dumps(request) + "\n"
        self.process.stdin.write(request_str.encode())
        await self.process.stdin.drain()
        
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise RuntimeError("Keine Antwort vom Server erhalten")
        
        response = json.loads(response_line.decode())
        
        if 'error' in response:
            error = response['error']
            raise Exception(f"MCP-Fehler: {error.get('message', 'Unbekannter Fehler')}")
        
        return response.get('result')

    async def _send_http_request(self, request):
        """Sendet eine Anfrage über HTTP.

        Args:
            request: Die zu sendende Anfrage

        Returns:
            Ergebnis der Anfrage
        """
        if not self.session:
            raise RuntimeError("Keine Verbindung zum Server")
        
        async with self.session.post(self.url, json=request) as response:
            if response.status != 200:
                raise RuntimeError(f"HTTP-Fehler: {response.status}")
            
            response_data = await response.json()
            
            if 'error' in response_data:
                error = response_data['error']
                raise Exception(f"MCP-Fehler: {error.get('message', 'Unbekannter Fehler')}")
            
            return response_data.get('result')

    def get_tool_info(self, tool_name):
        """Gibt Informationen zu einem Tool zurück.

        Args:
            tool_name: Name des Tools

        Returns:
            Informationen zum Tool oder None, wenn das Tool nicht gefunden wurde
        """
        for tool in self.tools:
            if tool['name'] == tool_name:
                return tool
        return None

async def main():
    """Hauptfunktion zum Testen des MCP-Clients."""
    parser = argparse.ArgumentParser(description='MCP Client')
    parser.add_argument('--transport', choices=['stdio', 'http', 'sse'], default='stdio',
                        help='Transport-Typ (stdio, http, sse)')
    parser.add_argument('--command', help='Befehl für stdio-Transport')
    parser.add_argument('--args', nargs='*', default=[],
                        help='Argumente für stdio-Transport')
    parser.add_argument('--url', help='URL für HTTP/SSE-Transport')
    parser.add_argument('--token', help='Bearer-Token für HTTP/SSE-Transport')
    parser.add_argument('--list-tools', action='store_true',
                        help='Listet alle verfügbaren Tools auf')
    parser.add_argument('--call-tool', help='Ruft ein Tool auf')
    parser.add_argument('--arguments', help='JSON-Argumente für den Tool-Aufruf')
    
    args = parser.parse_args()
    
    # Konfiguriere den Client basierend auf den Argumenten
    client_kwargs = {}
    
    if args.transport == 'stdio':
        if not args.command:
            parser.error("--command ist für stdio-Transport erforderlich")
        
        client_kwargs = {
            'command': args.command,
            'args': args.args
        }
    elif args.transport in ('http', 'sse'):
        if not args.url:
            parser.error("--url ist für HTTP/SSE-Transport erforderlich")
        
        client_kwargs = {
            'url': args.url
        }
        
        if args.token:
            client_kwargs['auth'] = {
                'type': 'bearer',
                'token': args.token
            }
    
    # Erstelle und verbinde den Client
    client = MCPClient(args.transport, **client_kwargs)
    
    try:
        await client.connect()
        
        if args.list_tools:
            tools = await client.list_tools()
            print(json.dumps(tools, indent=2))
        
        if args.call_tool:
            arguments = {}
            if args.arguments:
                try:
                    arguments = json.loads(args.arguments)
                except json.JSONDecodeError:
                    parser.error("--arguments muss gültiges JSON sein")
            
            result = await client.call_tool(args.call_tool, arguments)
            print(json.dumps(result, indent=2))
    finally:
        await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
