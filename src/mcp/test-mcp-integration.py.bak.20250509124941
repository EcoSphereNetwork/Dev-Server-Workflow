#!/usr/bin/env python3
"""
Test-Skript für die MCP-Integration

Dieses Skript testet die Verbindung zu verschiedenen MCP-Servern und führt Beispiel-Anfragen aus.
"""

import os
import json
import asyncio
import argparse
import logging
from pathlib import Path

# Importiere den MCP-Client
import sys
sys.path.append('/workspace')
from mcp_client import MCPClient

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test-mcp-integration")

async def test_n8n_mcp_server():
    """Testet die Verbindung zum n8n MCP-Server."""
    logger.info("Teste n8n MCP-Server...")
    
    # Konfiguriere den Client für den n8n MCP-Server
    client = MCPClient(
        transport_type='stdio',
        command='python',
        args=['/workspace/improved-n8n-mcp-server.py', '--mode', 'stdio'],
        env={
            'N8N_URL': 'http://localhost:5678',
            'N8N_API_KEY': os.environ.get('N8N_API_KEY', 'test-api-key')
        }
    )
    
    try:
        # Verbinde zum Server
        await client.connect()
        logger.info("Verbindung zum n8n MCP-Server hergestellt")
        
        # Liste verfügbare Tools auf
        tools = await client.list_tools()
        logger.info(f"Verfügbare Tools: {json.dumps(tools, indent=2)}")
        
        # Rufe ein Beispiel-Tool auf
        if tools and len(tools) > 0:
            tool_name = tools[0]['name']
            logger.info(f"Rufe Tool auf: {tool_name}")
            
            # Beispiel-Argumente basierend auf dem Tool-Schema
            tool_info = client.get_tool_info(tool_name)
            if tool_info and 'parameter_schema' in tool_info:
                schema = tool_info['parameter_schema']
                example_args = generate_example_args(schema)
                
                # Rufe das Tool auf
                result = await client.call_tool(tool_name, example_args)
                logger.info(f"Ergebnis: {json.dumps(result, indent=2)}")
            else:
                logger.warning(f"Kein Schema für Tool {tool_name} gefunden")
        else:
            logger.warning("Keine Tools verfügbar")
    finally:
        # Trenne die Verbindung
        await client.disconnect()
        logger.info("Verbindung zum n8n MCP-Server getrennt")

async def test_filesystem_mcp_server():
    """Testet die Verbindung zum Filesystem MCP-Server."""
    logger.info("Teste Filesystem MCP-Server...")
    
    # Konfiguriere den Client für den Filesystem MCP-Server
    client = MCPClient(
        transport_type='stdio',
        command='npx',
        args=['-y', '@modelcontextprotocol/server-filesystem']
    )
    
    try:
        # Verbinde zum Server
        await client.connect()
        logger.info("Verbindung zum Filesystem MCP-Server hergestellt")
        
        # Liste verfügbare Tools auf
        tools = await client.list_tools()
        logger.info(f"Verfügbare Tools: {json.dumps(tools, indent=2)}")
        
        # Rufe das readFile-Tool auf
        try:
            result = await client.call_tool('readFile', {
                'path': '/workspace/test-mcp-integration.py'
            })
            logger.info(f"Dateiinhalt (gekürzt): {result['content'][:100]}...")
        except Exception as e:
            logger.error(f"Fehler beim Aufruf von readFile: {e}")
        
        # Rufe das listFiles-Tool auf
        try:
            result = await client.call_tool('listFiles', {
                'path': '/workspace'
            })
            logger.info(f"Dateien im Verzeichnis: {result['files'][:5]}...")
        except Exception as e:
            logger.error(f"Fehler beim Aufruf von listFiles: {e}")
    finally:
        # Trenne die Verbindung
        await client.disconnect()
        logger.info("Verbindung zum Filesystem MCP-Server getrennt")

def generate_example_args(schema):
    """Generiert Beispiel-Argumente basierend auf einem JSON-Schema.
    
    Args:
        schema: Das JSON-Schema
        
    Returns:
        Ein Dictionary mit Beispiel-Argumenten
    """
    if not schema or not isinstance(schema, dict):
        return {}
    
    result = {}
    properties = schema.get('properties', {})
    
    for prop_name, prop_info in properties.items():
        prop_type = prop_info.get('type')
        
        if prop_type == 'string':
            result[prop_name] = f"Example {prop_name}"
        elif prop_type == 'integer' or prop_type == 'number':
            result[prop_name] = 42
        elif prop_type == 'boolean':
            result[prop_name] = True
        elif prop_type == 'array':
            result[prop_name] = []
        elif prop_type == 'object':
            result[prop_name] = generate_example_args(prop_info)
    
    return result

async def main():
    """Hauptfunktion zum Testen der MCP-Integration."""
    parser = argparse.ArgumentParser(description='Test MCP Integration')
    parser.add_argument('--n8n', action='store_true', help='Teste n8n MCP-Server')
    parser.add_argument('--filesystem', action='store_true', help='Teste Filesystem MCP-Server')
    parser.add_argument('--all', action='store_true', help='Teste alle MCP-Server')
    
    args = parser.parse_args()
    
    # Wenn keine spezifischen Tests angegeben wurden, teste alles
    if not (args.n8n or args.filesystem):
        args.all = True
    
    # Führe die ausgewählten Tests aus
    if args.n8n or args.all:
        await test_n8n_mcp_server()
    
    if args.filesystem or args.all:
        await test_filesystem_mcp_server()

if __name__ == "__main__":
    asyncio.run(main())
