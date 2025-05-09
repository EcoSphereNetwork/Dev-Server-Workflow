#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import logging
import argparse
import signal
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple
from abc import ABC, abstractmethod
import aiohttp
from aiohttp import web

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

class BaseMCPServer(ABC):
    """
    Basisklasse für MCP-Server-Implementierungen.
    
    Diese Klasse bietet eine gemeinsame Grundlage für alle MCP-Server-Implementierungen
    mit standardisierten Methoden für Logging, Fehlerbehandlung, Konfiguration und
    Kommunikation.
    """
    
    def __init__(self, 
                 name: str, 
                 description: str, 
                 version: str = "1.0.0",
                 host: str = "0.0.0.0", 
                 port: int = 3000,
                 log_level: str = "INFO",
                 log_file: Optional[str] = None,
                 config_file: Optional[str] = None):
        """
        Initialisiert den MCP-Server.
        
        Args:
            name: Name des MCP-Servers
            description: Beschreibung des MCP-Servers
            version: Version des MCP-Servers
            host: Host für den MCP-Server
            port: Port für den MCP-Server
            log_level: Log-Level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            log_file: Pfad zur Log-Datei (optional)
            config_file: Pfad zur Konfigurationsdatei (optional)
        """
        self.name = name
        self.description = description
        self.version = version
        self.host = host
        self.port = port
        
        # Konfiguriere Logging
        self.logger = setup_logging(log_level, log_file)
        
        # Initialisiere Konfigurationsmanager
        self.config_manager = ConfigManager()
        
        # Lade Konfiguration, falls angegeben
        self.config = {}
        if config_file:
            if config_file.endswith('.json'):
                self.config = self.config_manager.load_json_config(config_file, {})
            elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                self.config = self.config_manager.load_yaml_config(config_file, {})
            else:
                self.logger.warning(f"Unbekanntes Konfigurationsformat: {config_file}")
        
        # Lade Umgebungsvariablen
        self.env_config = self.config_manager.load_env_config()
        
        # Initialisiere Zähler und Status
        self.request_counter = 0
        self.running = True
        self.start_time = None
        self.tools = []
        
        # Initialisiere HTTP-Session
        self.session = None
    
    async def initialize(self):
        """
        Initialisiert den MCP-Server.
        
        Diese Methode sollte von abgeleiteten Klassen überschrieben werden,
        um spezifische Initialisierungslogik zu implementieren.
        """
        self.start_time = asyncio.get_event_loop().time()
        self.session = aiohttp.ClientSession()
        self.logger.info(f"MCP-Server {self.name} initialisiert")
        
        # Lade Tools
        await self._load_tools()
    
    @abstractmethod
    async def _load_tools(self):
        """
        Lädt die verfügbaren Tools.
        
        Diese Methode muss von abgeleiteten Klassen implementiert werden.
        """
        pass
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Ruft Informationen über den MCP-Server ab.
        
        Returns:
            Dict mit Serverinformationen
        """
        uptime = 0
        if self.start_time:
            uptime = asyncio.get_event_loop().time() - self.start_time
        
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "status": "online" if self.running else "offline",
            "uptime": uptime,
            "request_count": self.request_counter,
            "tools_count": len(self.tools)
        }
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """
        Ruft die verfügbaren Tools ab.
        
        Returns:
            Liste mit Toolinformationen
        """
        return self.tools
    
    @abstractmethod
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ruft ein Tool auf.
        
        Args:
            tool_name: Name des Tools
            arguments: Argumente für das Tool
            
        Returns:
            Dict mit dem Ergebnis des Toolaufrufs
            
        Raises:
            Exception: Wenn das Tool nicht gefunden wurde oder ein Fehler auftrat
        """
        pass
    
    async def handle_jsonrpc_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeitet eine JSON-RPC-Anfrage.
        
        Args:
            request_data: Die JSON-RPC-Anfrage als Dictionary
            
        Returns:
            Die JSON-RPC-Antwort als Dictionary
        """
        self.request_counter += 1
        request_id = request_data.get('id', None)
        method = request_data.get('method', '')
        params = request_data.get('params', {})
        
        self.logger.info(f"Anfrage #{self.request_counter}: Methode={method}, ID={request_id}")
        
        try:
            if method == 'mcp.listTools':
                result = self.get_tools()
            elif method == 'mcp.callTool':
                tool_name = params.get('name', '')
                arguments = params.get('arguments', {})
                
                if not tool_name:
                    return {
                        'jsonrpc': '2.0',
                        'id': request_id,
                        'error': {
                            'code': -32602,
                            'message': 'Ungültige Parameter: Tool-Name fehlt'
                        }
                    }
                
                result = await self.call_tool(tool_name, arguments)
            elif method == 'mcp.getServerInfo':
                result = self.get_server_info()
            else:
                return {
                    'jsonrpc': '2.0',
                    'id': request_id,
                    'error': {
                        'code': -32601,
                        'message': f'Methode nicht gefunden: {method}'
                    }
                }
            
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'result': result
            }
        except Exception as e:
            self.logger.error(f"Fehler bei der Verarbeitung der Anfrage: {e}", exc_info=True)
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32603,
                    'message': f'Interner Fehler: {str(e)}'
                }
            }
    
    async def process_stdin(self):
        """
        Verarbeitet Eingaben von stdin im JSON-RPC-Format.
        """
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Lese eine Zeile von stdin (nicht-blockierend)
                line = await loop.run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    self.logger.info("Keine Eingabe mehr verfügbar, beende Server")
                    self.running = False
                    break
                
                # Verarbeite die JSON-RPC-Anfrage
                try:
                    request = json.loads(line)
                    response = await self.handle_jsonrpc_request(request)
                    
                    # Sende die Antwort an stdout
                    print(json.dumps(response), flush=True)
                except json.JSONDecodeError:
                    self.logger.error(f"Ungültige JSON-Anfrage: {line}")
                    print(json.dumps({
                        'jsonrpc': '2.0',
                        'id': None,
                        'error': {
                            'code': -32700,
                            'message': 'Parse error'
                        }
                    }), flush=True)
            except Exception as e:
                self.logger.error(f"Fehler bei der Verarbeitung der Eingabe: {e}", exc_info=True)
                print(json.dumps({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32603,
                        'message': f'Interner Fehler: {str(e)}'
                    }
                }), flush=True)
    
    async def start_http_server(self, host: str = None, port: int = None):
        """
        Startet einen HTTP-Server für MCP-Anfragen.
        
        Args:
            host: Host für den HTTP-Server (überschreibt den Konstruktorwert)
            port: Port für den HTTP-Server (überschreibt den Konstruktorwert)
            
        Returns:
            web.AppRunner: Der AppRunner für den HTTP-Server
        """
        if host:
            self.host = host
        if port:
            self.port = port
        
        app = web.Application()
        
        # Füge einen Endpunkt für MCP-Anfragen hinzu
        async def handle_mcp_request(request):
            try:
                # Parse die JSON-RPC-Anfrage
                request_data = await request.json()
                
                # Verarbeite die Anfrage
                response = await self.handle_jsonrpc_request(request_data)
                
                # Sende die Antwort
                return web.json_response(response)
            except json.JSONDecodeError:
                return web.json_response({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32700,
                        'message': 'Parse error'
                    }
                }, status=400)
            except Exception as e:
                self.logger.error(f"Fehler bei der Verarbeitung der HTTP-Anfrage: {e}", exc_info=True)
                return web.json_response({
                    'jsonrpc': '2.0',
                    'id': None,
                    'error': {
                        'code': -32603,
                        'message': f'Interner Fehler: {str(e)}'
                    }
                }, status=500)
        
        app.router.add_post('/mcp', handle_mcp_request)
        
        # Füge eine einfache Statusseite hinzu
        async def handle_status(request):
            server_info = self.get_server_info()
            tools = self.get_tools()
            
            return web.Response(text=f"""
            <html>
                <head>
                    <title>{server_info['name']}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
                        h1 {{ color: #333; }}
                        h2 {{ color: #666; }}
                        .info {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; }}
                        .tools {{ margin-top: 20px; }}
                        .tool {{ background-color: #f9f9f9; padding: 10px; margin-bottom: 10px; border-radius: 5px; }}
                        .tool h3 {{ margin-top: 0; }}
                        pre {{ background-color: #eee; padding: 10px; border-radius: 5px; overflow-x: auto; }}
                    </style>
                </head>
                <body>
                    <h1>{server_info['name']}</h1>
                    <p>{server_info['description']}</p>
                    
                    <h2>Server-Informationen</h2>
                    <div class="info">
                        <p><strong>Version:</strong> {server_info['version']}</p>
                        <p><strong>Status:</strong> {server_info['status']}</p>
                        <p><strong>Uptime:</strong> {server_info['uptime']:.2f} Sekunden</p>
                        <p><strong>Verarbeitete Anfragen:</strong> {server_info['request_count']}</p>
                        <p><strong>Verfügbare Tools:</strong> {server_info['tools_count']}</p>
                    </div>
                    
                    <h2>Verfügbare Tools</h2>
                    <div class="tools">
                        {''.join([f'''
                        <div class="tool">
                            <h3>{tool['name']}</h3>
                            <p>{tool['description']}</p>
                            <h4>Parameter-Schema:</h4>
                            <pre>{json.dumps(tool['parameter_schema'], indent=2)}</pre>
                        </div>
                        ''' for tool in tools])}
                    </div>
                    
                    <h2>API-Endpunkte</h2>
                    <div class="info">
                        <p><strong>MCP-Endpunkt:</strong> <code>POST /mcp</code></p>
                        <p><strong>Statusseite:</strong> <code>GET /</code></p>
                        <p><strong>Gesundheitscheck:</strong> <code>GET /health</code></p>
                    </div>
                </body>
            </html>
            """, content_type='text/html')
        
        app.router.add_get('/', handle_status)
        
        # Füge einen Gesundheitscheck-Endpunkt hinzu
        async def handle_health(request):
            return web.json_response({
                "status": "ok",
                "name": self.name,
                "version": self.version,
                "uptime": asyncio.get_event_loop().time() - self.start_time if self.start_time else 0
            })
        
        app.router.add_get('/health', handle_health)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, self.host, self.port)
        await site.start()
        
        self.logger.info(f"HTTP-Server gestartet auf http://{self.host}:{self.port}")
        
        return runner
    
    async def shutdown(self):
        """
        Beendet den MCP-Server ordnungsgemäß.
        """
        self.logger.info("Beende MCP-Server...")
        self.running = False
        
        if self.session:
            await self.session.close()
            self.logger.info("HTTP-Session geschlossen")
    
    @staticmethod
    def add_common_arguments(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
        """
        Fügt gemeinsame Kommandozeilenargumente zu einem ArgumentParser hinzu.
        
        Args:
            parser: ArgumentParser-Instanz
            
        Returns:
            ArgumentParser mit hinzugefügten Argumenten
        """
        parser.add_argument('--host', default='0.0.0.0',
                            help='Host für den MCP-Server')
        parser.add_argument('--port', type=int, default=3000,
                            help='Port für den MCP-Server')
        parser.add_argument('--log-level', choices=['debug', 'info', 'warning', 'error', 'critical'],
                            default='info', help='Log-Level')
        parser.add_argument('--log-file',
                            help='Pfad zur Log-Datei')
        parser.add_argument('--config-file',
                            help='Pfad zur Konfigurationsdatei')
        parser.add_argument('--mode', choices=['stdio', 'http'], default='stdio',
                            help='Betriebsmodus (stdio oder http)')
        
        return parser
    
    @classmethod
    async def run_server(cls, args: argparse.Namespace, **kwargs):
        """
        Erstellt und startet eine Instanz des MCP-Servers.
        
        Args:
            args: Kommandozeilenargumente
            **kwargs: Weitere Argumente für den Konstruktor
        """
        # Erstelle und initialisiere den Server
        server = cls(
            host=args.host,
            port=args.port,
            log_level=args.log_level.upper(),
            log_file=args.log_file,
            config_file=args.config_file,
            **kwargs
        )
        await server.initialize()
        
        # Registriere Signal-Handler für sauberes Herunterfahren
        loop = asyncio.get_event_loop()
        
        def signal_handler():
            server.logger.info("Signal empfangen, fahre Server herunter...")
            asyncio.create_task(server.shutdown())
        
        for sig in (signal.SIGINT, signal.SIGTERM):
            loop.add_signal_handler(sig, signal_handler)
        
        try:
            if args.mode == 'stdio':
                server.logger.info(f"Starte {server.name} im STDIO-Modus")
                await server.process_stdin()
            else:
                server.logger.info(f"Starte {server.name} im HTTP-Modus auf {args.host}:{args.port}")
                runner = await server.start_http_server()
                
                # Halte den Server am Laufen
                while server.running:
                    await asyncio.sleep(1)
                
                await runner.cleanup()
        finally:
            await server.shutdown()