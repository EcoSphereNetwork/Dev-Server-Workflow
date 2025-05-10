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
Verbesserter n8n MCP Server

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
import argparse
import signal
import uuid
from datetime import datetime

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("n8n-mcp-server.log")
    ]
)
logger = logging.getLogger("n8n-mcp-server")

class N8nMCPServer:
    """MCP-Server, der n8n-Funktionalität als Tools bereitstellt."""

    def __init__(self, n8n_url, api_key, workflows_cache_path=None):
        """Initialisiert den MCP-Server mit n8n-API Zugangsdaten.

        Args:
            n8n_url: URL der n8n-Instanz
            api_key: API-Key für n8n
            workflows_cache_path: Pfad zum Caching von Workflow-Informationen
        """
        self.n8n_url = n8n_url
        self.api_key = api_key
        self.session = None
        self.workflows = {}
        self.tools = []
        self.workflows_cache_path = workflows_cache_path or Path.home() / ".n8n-mcp-cache.json"
        self.running = True
        self.request_counter = 0
        self.last_cache_update = None
        self.cache_ttl_seconds = 300  # 5 Minuten Cache-Gültigkeit

    async def initialize(self):
        """Initialisiert den Server und lädt Workflow-Informationen."""
        self.session = aiohttp.ClientSession(headers={
            "X-N8N-API-KEY": self.api_key,
            "Content-Type": "application/json"
        })
        
        # Versuche, Workflows aus dem Cache zu laden
        if await self._load_workflows_from_cache():
            logger.info(f"Workflows aus Cache geladen: {len(self.workflows)} Workflows gefunden")
        else:
            # Wenn kein Cache verfügbar, lade von n8n
            await self._fetch_workflows()
            logger.info(f"Workflows von n8n geladen: {len(self.workflows)} Workflows gefunden")
            await self._save_workflows_to_cache()
        
        # Generiere Tools basierend auf den Workflows
        await self._generate_tools()
        logger.info(f"MCP-Tools generiert: {len(self.tools)} Tools verfügbar")

    async def _load_workflows_from_cache(self):
        """Lädt Workflow-Informationen aus dem Cache."""
        try:
            if not Path(self.workflows_cache_path).exists():
                return False
                
            with open(self.workflows_cache_path, 'r') as f:
                cache_data = json.load(f)
                
            # Prüfe Cache-Alter
            last_update = datetime.fromisoformat(cache_data.get('last_update', '2000-01-01T00:00:00'))
            now = datetime.now()
            if (now - last_update).total_seconds() > self.cache_ttl_seconds:
                logger.info("Cache ist veraltet, lade Workflows neu")
                return False
                
            self.workflows = cache_data.get('workflows', {})
            self.last_cache_update = last_update
            return len(self.workflows) > 0
        except Exception as e:
            logger.warning(f"Fehler beim Laden des Workflow-Caches: {e}")
            return False

    async def _save_workflows_to_cache(self):
        """Speichert Workflow-Informationen im Cache."""
        try:
            cache_data = {
                'last_update': datetime.now().isoformat(),
                'workflows': self.workflows
            }
            
            with open(self.workflows_cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            logger.info(f"Workflow-Cache aktualisiert: {len(self.workflows)} Workflows gespeichert")
        except Exception as e:
            logger.warning(f"Fehler beim Speichern des Workflow-Caches: {e}")

    async def _fetch_workflows(self):
        """Lädt alle Workflows von n8n."""
        try:
            async with self.session.get(f"{self.n8n_url}/api/v1/workflows") as response:
                if response.status == 200:
                    workflows_data = await response.json()
                    
                    # Verarbeite Workflows und filtere nach MCP-Tags
                    for workflow in workflows_data:
                        if 'tags' in workflow and 'mcp' in workflow.get('tags', []):
                            workflow_id = workflow['id']
                            self.workflows[workflow_id] = {
                                'id': workflow_id,
                                'name': workflow['name'],
                                'description': workflow.get('description', ''),
                                'tags': workflow.get('tags', []),
                                'active': workflow.get('active', False)
                            }
                else:
                    logger.error(f"Fehler beim Abrufen der Workflows: {response.status}")
        except Exception as e:
            logger.error(f"Fehler bei der Verbindung zu n8n: {e}")

    async def _generate_tools(self):
        """Generiert MCP-Tools basierend auf den verfügbaren Workflows."""
        self.tools = []
        
        for workflow_id, workflow in self.workflows.items():
            # Erstelle ein Tool für jeden Workflow mit MCP-Tag
            if 'mcp' in workflow.get('tags', []):
                # Extrahiere Parameter-Schema aus Workflow-Metadaten oder verwende Standard
                parameter_schema = await self._extract_parameter_schema(workflow_id)
                
                tool = {
                    "name": f"workflow_{workflow['name'].lower().replace(' ', '_')}",
                    "description": workflow.get('description', f"Führt den n8n-Workflow '{workflow['name']}' aus"),
                    "parameter_schema": parameter_schema
                }
                
                self.tools.append(tool)

    async def _extract_parameter_schema(self, workflow_id):
        """Extrahiert das Parameter-Schema aus einem Workflow."""
        # Standard-Schema, falls kein spezifisches Schema definiert ist
        default_schema = {
            "type": "object",
            "properties": {
                "input": {
                    "type": "object",
                    "description": "Eingabedaten für den Workflow"
                }
            }
        }
        
        try:
            # Versuche, detaillierte Workflow-Informationen zu laden
            async with self.session.get(f"{self.n8n_url}/api/v1/workflows/{workflow_id}") as response:
                if response.status == 200:
                    workflow_data = await response.json()
                    
                    # Suche nach MCP-Metadaten in den Workflow-Notizen oder Beschreibung
                    notes = workflow_data.get('notes', '')
                    if notes and '```json' in notes:
                        # Extrahiere JSON aus Markdown-Codeblock
                        try:
                            start = notes.find('```json') + 7
                            end = notes.find('```', start)
                            if start > 7 and end > start:
                                json_str = notes[start:end].strip()
                                metadata = json.loads(json_str)
                                if 'parameter_schema' in metadata:
                                    return metadata['parameter_schema']
                        except json.JSONDecodeError:
                            pass
                    
                    # Alternativ: Analysiere Workflow-Knoten nach Eingabeparametern
                    if 'nodes' in workflow_data:
                        for node in workflow_data['nodes']:
                            if node.get('type') == 'n8n-nodes-base.httpRequest' and node.get('position', {}).get('x', 0) < 300:
                                # Wahrscheinlich ein Trigger-Knoten am Anfang
                                params = node.get('parameters', {})
                                if 'options' in params and 'bodyParametersUi' in params['options']:
                                    body_params = params['options']['bodyParametersUi']
                                    if body_params and 'parameter' in body_params:
                                        # Erstelle Schema aus den definierten Parametern
                                        properties = {}
                                        for param in body_params['parameter']:
                                            properties[param['name']] = {
                                                "type": "string",  # Standard-Typ
                                                "description": param.get('description', f"Parameter {param['name']}")
                                            }
                                        
                                        if properties:
                                            return {
                                                "type": "object",
                                                "properties": properties
                                            }
        except Exception as e:
            logger.warning(f"Fehler beim Extrahieren des Parameter-Schemas für Workflow {workflow_id}: {e}")
        
        return default_schema

    async def handle_jsonrpc_request(self, request_data):
        """Verarbeitet eine JSON-RPC-Anfrage.

        Args:
            request_data: Die JSON-RPC-Anfrage als Dictionary

        Returns:
            Die JSON-RPC-Antwort als Dictionary
        """
        self.request_counter += 1
        request_id = request_data.get('id', None)
        method = request_data.get('method', '')
        params = request_data.get('params', {})
        
        logger.info(f"Anfrage #{self.request_counter}: Methode={method}, ID={request_id}")
        
        try:
            if method == 'mcp.listTools':
                result = await self.handle_list_tools()
            elif method == 'mcp.callTool':
                result = await self.handle_call_tool(params)
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
            logger.error(f"Fehler bei der Verarbeitung der Anfrage: {e}", exc_info=True)
            return {
                'jsonrpc': '2.0',
                'id': request_id,
                'error': {
                    'code': -32603,
                    'message': f'Interner Fehler: {str(e)}'
                }
            }

    async def handle_list_tools(self):
        """Behandelt die mcp.listTools-Anfrage.

        Returns:
            Liste der verfügbaren Tools
        """
        # Prüfe, ob ein Refresh der Workflows nötig ist
        if self.last_cache_update:
            now = datetime.now()
            if (now - self.last_cache_update).total_seconds() > self.cache_ttl_seconds:
                logger.info("Cache ist veraltet, aktualisiere Workflows")
                await self._fetch_workflows()
                await self._generate_tools()
                await self._save_workflows_to_cache()
        
        return self.tools

    async def handle_call_tool(self, params):
        """Behandelt die mcp.callTool-Anfrage.

        Args:
            params: Parameter der Anfrage (enthält 'name' und 'arguments')

        Returns:
            Ergebnis des Werkzeugaufrufs
        """
        tool_name = params.get('name', '')
        arguments = params.get('arguments', {})
        
        logger.info(f"Tool-Aufruf: {tool_name} mit Argumenten: {json.dumps(arguments)}")
        
        # Finde das entsprechende Tool
        tool = None
        workflow_id = None
        
        for workflow_id, workflow in self.workflows.items():
            generated_name = f"workflow_{workflow['name'].lower().replace(' ', '_')}"
            if generated_name == tool_name:
                tool = workflow
                break
        
        if not tool:
            raise Exception(f"Tool nicht gefunden: {tool_name}")
        
        # Führe den Workflow aus
        return await self._execute_workflow(workflow_id, arguments)

    async def _execute_workflow(self, workflow_id, data):
        """Führt einen n8n-Workflow aus.

        Args:
            workflow_id: ID des auszuführenden Workflows
            data: Eingabedaten für den Workflow

        Returns:
            Ergebnis der Workflow-Ausführung
        """
        try:
            execution_id = str(uuid.uuid4())
            payload = {
                'workflowData': {
                    'id': workflow_id
                },
                'executionId': execution_id,
                'runData': data
            }
            
            async with self.session.post(
                f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute",
                json=payload
            ) as response:
                if response.status in (200, 201):
                    result = await response.json()
                    logger.info(f"Workflow {workflow_id} erfolgreich ausgeführt")
                    
                    # Extrahiere relevante Daten aus dem Ergebnis
                    if 'data' in result:
                        return {
                            'success': True,
                            'execution_id': execution_id,
                            'data': result['data']
                        }
                    return {
                        'success': True,
                        'execution_id': execution_id,
                        'result': result
                    }
                else:
                    error_text = await response.text()
                    logger.error(f"Fehler bei der Workflow-Ausführung: {response.status} - {error_text}")
                    return {
                        'success': False,
                        'error': f"HTTP {response.status}: {error_text}"
                    }
        except Exception as e:
            logger.error(f"Fehler bei der Workflow-Ausführung: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }

    async def process_stdin(self):
        """Verarbeitet Eingaben von stdin im JSON-RPC-Format."""
        loop = asyncio.get_event_loop()
        
        while self.running:
            try:
                # Lese eine Zeile von stdin (nicht-blockierend)
                line = await loop.run_in_executor(None, sys.stdin.readline)
                
                if not line:
                    logger.info("Keine Eingabe mehr verfügbar, beende Server")
                    self.running = False
                    break
                
                # Verarbeite die JSON-RPC-Anfrage
                try:
                    request = json.loads(line)
                    response = await self.handle_jsonrpc_request(request)
                    
                    # Sende die Antwort an stdout
                    print(json.dumps(response))
                    sys.stdout.flush()
                except json.JSONDecodeError:
                    logger.error(f"Ungültige JSON-Anfrage: {line}")
                    error_response = {
                        'jsonrpc': '2.0',
                        'id': None,
                        'error': {
                            'code': -32700,
                            'message': 'Ungültige JSON-Anfrage'
                        }
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung der Eingabe: {e}", exc_info=True)

    async def start_http_server(self, host='0.0.0.0', port=3456):
        """Startet einen HTTP-Server für MCP-Anfragen.

        Args:
            host: Host-Adresse für den Server
            port: Port für den Server
        """
        from aiohttp import web
        
        app = web.Application()
        
        async def handle_mcp_request(request):
            try:
                request_data = await request.json()
                response = await self.handle_jsonrpc_request(request_data)
                return web.json_response(response)
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung der HTTP-Anfrage: {e}", exc_info=True)
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
            return web.Response(text=f"""
            <html>
                <head><title>n8n MCP Server</title></head>
                <body>
                    <h1>n8n MCP Server</h1>
                    <p>Status: Aktiv</p>
                    <p>Verfügbare Tools: {len(self.tools)}</p>
                    <p>Verarbeitete Anfragen: {self.request_counter}</p>
                    <p>Letztes Cache-Update: {self.last_cache_update}</p>
                </body>
            </html>
            """, content_type='text/html')
        
        app.router.add_get('/', handle_status)
        
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host, port)
        await site.start()
        
        logger.info(f"HTTP-Server gestartet auf http://{host}:{port}")
        
        return runner

    async def shutdown(self):
        """Beendet den Server ordnungsgemäß."""
        logger.info("Beende Server...")
        self.running = False
        
        if self.session:
            await self.session.close()
            logger.info("HTTP-Session geschlossen")

async def main():
    """Hauptfunktion zum Starten des MCP-Servers."""
    parser = argparse.ArgumentParser(description='n8n MCP Server')
    parser.add_argument('--n8n-url', default=os.environ.get('N8N_URL', 'http://localhost:5678'),
                        help='URL der n8n-Instanz (Standard: http://localhost:5678)')
    parser.add_argument('--api-key', default=os.environ.get('N8N_API_KEY', ''),
                        help='API-Key für n8n')
    parser.add_argument('--cache-path', default=os.environ.get('N8N_MCP_CACHE_PATH', ''),
                        help='Pfad zum Caching von Workflow-Informationen')
    parser.add_argument('--mode', choices=['stdio', 'http'], default='stdio',
                        help='Betriebsmodus (stdio oder http)')
    parser.add_argument('--http-host', default='0.0.0.0',
                        help='Host für den HTTP-Server (nur im HTTP-Modus)')
    parser.add_argument('--http-port', type=int, default=3456,
                        help='Port für den HTTP-Server (nur im HTTP-Modus)')
    
    args = parser.parse_args()
    
    if not args.api_key:
        logger.error("Kein API-Key angegeben. Bitte geben Sie einen API-Key mit --api-key oder der Umgebungsvariable N8N_API_KEY an.")
        sys.exit(1)
    
    # Erstelle und initialisiere den Server
    server = N8nMCPServer(args.n8n_url, args.api_key, args.cache_path)
    await server.initialize()
    
    # Registriere Signal-Handler für sauberes Herunterfahren
    loop = asyncio.get_event_loop()
    
    def signal_handler():
        logger.info("Signal empfangen, fahre Server herunter...")
        asyncio.create_task(server.shutdown())
    
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, signal_handler)
    
    try:
        if args.mode == 'stdio':
            logger.info("Starte MCP-Server im STDIO-Modus")
            await server.process_stdin()
        else:
            logger.info(f"Starte MCP-Server im HTTP-Modus auf {args.http_host}:{args.http_port}")
            runner = await server.start_http_server(args.http_host, args.http_port)
            
            # Halte den Server am Laufen
            while server.running:
                await asyncio.sleep(1)
                
            await runner.cleanup()
    finally:
        await server.shutdown()

if __name__ == "__main__":
    asyncio.run(main())