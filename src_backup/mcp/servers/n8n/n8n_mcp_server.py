#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import logging
import argparse
import uuid
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union, Tuple

# Import from core modules
from src.core.logger import setup_logging, get_logger
from src.core.config_manager import ConfigManager
from src.core.utils.docker_utils import DockerUtils
from src.core.utils.process_utils import ProcessManager
from src.core.utils.network_utils import NetworkUtils
from src.core.utils.system_utils import SystemUtils

# Import the base MCP server
from src.mcp_servers.base.base_mcp_server import BaseMCPServer

class N8nMCPServer(BaseMCPServer):
    """
    MCP-Server, der n8n-Funktionalität als Tools bereitstellt.
    
    Diese Klasse implementiert einen MCP-Server, der n8n-Workflows als Tools
    für KI-Agenten bereitstellt.
    """
    
    def __init__(self, 
                 n8n_url: str = None,
                 api_key: str = None,
                 workflows_cache_path: str = None,
                 cache_ttl_seconds: int = 300,
                 **kwargs):
        """
        Initialisiert den n8n MCP-Server.
        
        Args:
            n8n_url: URL der n8n-Instanz
            api_key: API-Key für n8n
            workflows_cache_path: Pfad zum Caching von Workflow-Informationen
            cache_ttl_seconds: Cache-Gültigkeitsdauer in Sekunden
            **kwargs: Weitere Argumente für die Basisklasse
        """
        super().__init__(
            name="n8n-mcp-server",
            description="MCP-Server, der n8n-Workflows als Tools bereitstellt",
            version="1.1.0",
            **kwargs
        )
        
        # n8n-spezifische Konfiguration
        self.n8n_url = n8n_url or os.environ.get('N8N_URL', 'http://localhost:5678')
        self.api_key = api_key or os.environ.get('N8N_API_KEY', '')
        
        # Cache-Konfiguration
        self.workflows_cache_path = workflows_cache_path or Path.home() / ".n8n-mcp-cache.json"
        self.cache_ttl_seconds = cache_ttl_seconds
        self.last_cache_update = None
        
        # Workflow-Daten
        self.workflows = {}
        self.tools = []
    
    async def initialize(self):
        """
        Initialisiert den Server und lädt Workflow-Informationen.
        """
        await super().initialize()
        
        # Setze HTTP-Header für n8n-API
        if self.session:
            self.session._default_headers.update({
                "X-N8N-API-KEY": self.api_key,
                "Content-Type": "application/json"
            })
        
        # Versuche, Workflows aus dem Cache zu laden
        if await self._load_workflows_from_cache():
            self.logger.info(f"Workflows aus Cache geladen: {len(self.workflows)} Workflows gefunden")
        else:
            # Wenn kein Cache verfügbar, lade von n8n
            await self._fetch_workflows()
            self.logger.info(f"Workflows von n8n geladen: {len(self.workflows)} Workflows gefunden")
            await self._save_workflows_to_cache()
    
    async def _load_tools(self):
        """
        Generiert MCP-Tools basierend auf den verfügbaren Workflows.
        """
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
        
        self.logger.info(f"MCP-Tools generiert: {len(self.tools)} Tools verfügbar")
    
    async def _load_workflows_from_cache(self) -> bool:
        """
        Lädt Workflow-Informationen aus dem Cache.
        
        Returns:
            bool: True, wenn Workflows erfolgreich geladen wurden, sonst False
        """
        try:
            if not Path(self.workflows_cache_path).exists():
                return False
                
            with open(self.workflows_cache_path, 'r') as f:
                cache_data = json.load(f)
                
            # Prüfe Cache-Alter
            last_update = datetime.fromisoformat(cache_data.get('last_update', '2000-01-01T00:00:00'))
            now = datetime.now()
            if (now - last_update).total_seconds() > self.cache_ttl_seconds:
                self.logger.info("Cache ist veraltet, lade Workflows neu")
                return False
                
            self.workflows = cache_data.get('workflows', {})
            self.last_cache_update = last_update
            return len(self.workflows) > 0
        except Exception as e:
            self.logger.warning(f"Fehler beim Laden des Workflow-Caches: {e}")
            return False
    
    async def _save_workflows_to_cache(self):
        """
        Speichert Workflow-Informationen im Cache.
        """
        try:
            cache_data = {
                'last_update': datetime.now().isoformat(),
                'workflows': self.workflows
            }
            
            # Stelle sicher, dass das Verzeichnis existiert
            os.makedirs(os.path.dirname(self.workflows_cache_path), exist_ok=True)
            
            with open(self.workflows_cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
            self.logger.info(f"Workflow-Cache aktualisiert: {len(self.workflows)} Workflows gespeichert")
        except Exception as e:
            self.logger.warning(f"Fehler beim Speichern des Workflow-Caches: {e}")
    
    async def _fetch_workflows(self):
        """
        Lädt alle Workflows von n8n.
        """
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
                    self.logger.error(f"Fehler beim Abrufen der Workflows: {response.status}")
                    self.logger.error(await response.text())
        except Exception as e:
            self.logger.error(f"Fehler bei der Verbindung zu n8n: {e}")
            raise
    
    async def _extract_parameter_schema(self, workflow_id: str) -> Dict[str, Any]:
        """
        Extrahiert das Parameter-Schema aus einem Workflow.
        
        Args:
            workflow_id: ID des Workflows
            
        Returns:
            Dict mit dem Parameter-Schema
        """
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
            self.logger.warning(f"Fehler beim Extrahieren des Parameter-Schemas für Workflow {workflow_id}: {e}")
        
        return default_schema
    
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
        self.logger.info(f"Tool-Aufruf: {tool_name} mit Argumenten: {json.dumps(arguments)}")
        
        # Prüfe, ob ein Refresh der Workflows nötig ist
        if self.last_cache_update:
            now = datetime.now()
            if (now - self.last_cache_update).total_seconds() > self.cache_ttl_seconds:
                self.logger.info("Cache ist veraltet, aktualisiere Workflows")
                await self._fetch_workflows()
                await self._load_tools()
                await self._save_workflows_to_cache()
        
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
    
    async def _execute_workflow(self, workflow_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Führt einen n8n-Workflow aus.
        
        Args:
            workflow_id: ID des auszuführenden Workflows
            data: Eingabedaten für den Workflow
            
        Returns:
            Dict mit dem Ergebnis der Workflow-Ausführung
            
        Raises:
            Exception: Wenn ein Fehler bei der Ausführung auftrat
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
            
            max_retries = 3
            retry_delay = 1.0
            
            for attempt in range(max_retries):
                try:
                    async with self.session.post(
                        f"{self.n8n_url}/api/v1/workflows/{workflow_id}/execute",
                        json=payload
                    ) as response:
                        if response.status in (200, 201):
                            result = await response.json()
                            self.logger.info(f"Workflow {workflow_id} erfolgreich ausgeführt")
                            
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
                            self.logger.error(f"Fehler bei der Workflow-Ausführung: {response.status} - {error_text}")
                            
                            # Bei bestimmten Fehlern einen Retry versuchen
                            if response.status in (429, 500, 502, 503, 504) and attempt < max_retries - 1:
                                self.logger.info(f"Versuche erneut in {retry_delay} Sekunden...")
                                await asyncio.sleep(retry_delay)
                                retry_delay *= 2  # Exponentielles Backoff
                                continue
                            
                            return {
                                'success': False,
                                'error': f"HTTP {response.status}: {error_text}"
                            }
                except aiohttp.ClientError as e:
                    self.logger.error(f"Netzwerkfehler bei der Workflow-Ausführung: {e}")
                    
                    if attempt < max_retries - 1:
                        self.logger.info(f"Versuche erneut in {retry_delay} Sekunden...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponentielles Backoff
                        continue
                    
                    raise
        except Exception as e:
            self.logger.error(f"Fehler bei der Workflow-Ausführung: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }


async def main():
    """
    Hauptfunktion zum Starten des n8n MCP-Servers.
    """
    parser = argparse.ArgumentParser(description='n8n MCP Server')
    parser = BaseMCPServer.add_common_arguments(parser)
    
    parser.add_argument('--n8n-url', default=os.environ.get('N8N_URL', 'http://localhost:5678'),
                        help='URL der n8n-Instanz (Standard: http://localhost:5678)')
    parser.add_argument('--api-key', default=os.environ.get('N8N_API_KEY', ''),
                        help='API-Key für n8n')
    parser.add_argument('--cache-path', default=os.environ.get('N8N_MCP_CACHE_PATH', ''),
                        help='Pfad zum Caching von Workflow-Informationen')
    parser.add_argument('--cache-ttl', type=int, default=300,
                        help='Cache-Gültigkeitsdauer in Sekunden (Standard: 300)')
    
    args = parser.parse_args()
    
    if not args.api_key:
        print("Kein API-Key angegeben. Bitte geben Sie einen API-Key mit --api-key oder der Umgebungsvariable N8N_API_KEY an.")
        sys.exit(1)
    
    await N8nMCPServer.run_server(
        args,
        n8n_url=args.n8n_url,
        api_key=args.api_key,
        workflows_cache_path=args.cache_path,
        cache_ttl_seconds=args.cache_ttl
    )


if __name__ == "__main__":
    asyncio.run(main())