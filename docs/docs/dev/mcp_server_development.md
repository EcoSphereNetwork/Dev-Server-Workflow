# MCP-Server-Entwicklung

Diese Dokumentation bietet einen umfassenden Leitfaden für die Entwicklung von MCP-Servern für das Dev-Server-Workflow-Projekt.

## Übersicht

MCP (Model Context Protocol) Server stellen Tools für Clients über eine standardisierte Schnittstelle bereit. Jeder MCP-Server implementiert die `MCPServerInterface` und erweitert die `BaseMCPServer`-Klasse.

## Voraussetzungen

Bevor Sie mit der Entwicklung eines MCP-Servers beginnen, stellen Sie sicher, dass Sie Folgendes haben:

- Python 3.8 oder höher
- Grundlegende Kenntnisse von asyncio
- Verständnis des Model Context Protocols

## Erstellen eines neuen MCP-Servers

### 1. Erstellen Sie eine neue Python-Datei

Erstellen Sie eine neue Python-Datei in `src/mcp/servers/your_server/your_server.py`.

### 2. Importieren Sie die erforderlichen Module

```python
#!/usr/bin/env python3

import os
import sys
import json
import asyncio
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Importieren Sie die Kernmodule
from src.core.logger import setup_logging, get_logger
from src.core.config_manager import ConfigManager
from src.core.utils.docker_utils import DockerUtils
from src.core.utils.process_utils import ProcessManager
from src.core.utils.network_utils import NetworkUtils
from src.core.utils.system_utils import SystemUtils

# Importieren Sie den Basis-MCP-Server
from src.mcp.base.base_mcp_server import BaseMCPServer
from src.mcp.interfaces.mcp_tool import MCPTool
```

### 3. Definieren Sie Ihre MCP-Server-Klasse

```python
class YourMCPServer(BaseMCPServer):
    """
    MCP-Server für [kurze Beschreibung].
    
    Diese Klasse implementiert einen MCP-Server, der [detaillierte Beschreibung].
    """
    
    def __init__(self, 
                 # Fügen Sie Ihre spezifischen Parameter hier hinzu
                 **kwargs):
        """
        Initialisieren Sie den MCP-Server.
        
        Args:
            # Dokumentieren Sie Ihre spezifischen Parameter hier
            **kwargs: Zusätzliche Argumente für die Basisklasse
        """
        super().__init__(
            name="your-mcp-server",
            description="MCP-Server für [kurze Beschreibung]",
            version="1.0.0",
            **kwargs
        )
        
        # Initialisieren Sie Ihre spezifischen Attribute hier
```

### 4. Implementieren Sie die erforderlichen Methoden

#### 4.1. `_load_tools`

Diese Methode lädt die verfügbaren Tools.

```python
async def _load_tools(self) -> None:
    """
    Laden Sie die verfügbaren Tools.
    """
    self.tools = [
        MCPTool(
            name="your_tool",
            description="Beschreibung Ihres Tools",
            parameter_schema={
                "type": "object",
                "properties": {
                    "param1": {
                        "type": "string",
                        "description": "Beschreibung von param1"
                    },
                    "param2": {
                        "type": "integer",
                        "description": "Beschreibung von param2"
                    }
                },
                "required": ["param1"]
            }
        ),
        # Fügen Sie weitere Tools hier hinzu
    ]
    
    self.logger.info(f"Loaded {len(self.tools)} tools")
```

#### 4.2. `call_tool`

Diese Methode ruft ein Tool auf.

```python
async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Rufen Sie ein Tool auf.
    
    Args:
        tool_name: Name des Tools
        arguments: Argumente für das Tool
        
    Returns:
        Dict[str, Any]: Ergebnis des Tool-Aufrufs
        
    Raises:
        ValueError: Wenn das Tool nicht gefunden wird
        Exception: Wenn ein Fehler während des Tool-Aufrufs auftritt
    """
    self.logger.info(f"Calling tool {tool_name} with arguments: {json.dumps(arguments)}")
    
    # Finden Sie das Tool
    tool = next((t for t in self.tools if t.name == tool_name), None)
    if not tool:
        raise ValueError(f"Tool not found: {tool_name}")
    
    # Implementieren Sie Ihre Tool-Logik hier
    if tool_name == "your_tool":
        return await self._handle_your_tool(arguments)
    
    # Wenn wir hier ankommen, ist das Tool nicht implementiert
    raise NotImplementedError(f"Tool not implemented: {tool_name}")
```

#### 4.3. Tool-Handler-Methoden

Implementieren Sie Methoden zum Behandeln jedes Tools.

```python
async def _handle_your_tool(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Behandeln Sie das 'your_tool'-Tool.
    
    Args:
        arguments: Argumente für das Tool
        
    Returns:
        Dict[str, Any]: Ergebnis des Tool-Aufrufs
    """
    # Validieren Sie Argumente
    param1 = arguments.get("param1")
    if not param1:
        raise ValueError("param1 is required")
    
    param2 = arguments.get("param2", 0)
    
    # Implementieren Sie Ihre Tool-Logik hier
    result = {
        "param1": param1,
        "param2": param2,
        "result": "Ihr Ergebnis hier"
    }
    
    return result
```

### 5. Definieren Sie die Hauptfunktion

```python
async def main():
    """
    Hauptfunktion zum Starten des MCP-Servers.
    """
    parser = argparse.ArgumentParser(description='Ihr MCP-Server')
    parser = BaseMCPServer.add_common_arguments(parser)
    
    # Fügen Sie Ihre spezifischen Befehlszeilenargumente hier hinzu
    parser.add_argument('--your-param', default='default_value',
                        help='Beschreibung Ihres Parameters')
    
    args = parser.parse_args()
    
    # Starten Sie den Server
    await YourMCPServer.run_server(
        args,
        # Übergeben Sie Ihre spezifischen Parameter hier
        your_param=args.your_param
    )


if __name__ == "__main__":
    asyncio.run(main())
```

## Integration mit Docker Compose

Fügen Sie Ihren Server zur Docker Compose-Konfiguration in `docker/compose/mcp-servers/docker-compose.yml` hinzu:

```yaml
services:
  your-mcp-server:
    build:
      context: ../..
      dockerfile: docker/images/mcp-servers/Dockerfile
    command: python3 src/mcp/servers/your_server/your_server.py --mode http --port 3456
    ports:
      - "3456:3456"
    volumes:
      - ../..:/workspace
    environment:
      - YOUR_ENV_VAR=value
    networks:
      - mcp-network
```

## Dokumentation

Aktualisieren Sie die Dokumentation, um Ihren neuen MCP-Server einzuschließen:

1. Fügen Sie einen Abschnitt zu `docs/docs/dev/index.md` hinzu, der Ihren Server beschreibt
2. Fügen Sie API-Dokumentation zu `docs/docs/dev/api-reference.md` hinzu
3. Fügen Sie Benutzerdokumentation zu `docs/docs/user/index.md` hinzu

## Tests

Erstellen Sie Tests für Ihren MCP-Server in `tests/mcp/`:

```python
import unittest
import asyncio
from src.mcp.servers.your_server.your_server import YourMCPServer

class TestYourMCPServer(unittest.TestCase):
    def setUp(self):
        self.server = YourMCPServer()
        asyncio.run(self.server.initialize())
    
    def tearDown(self):
        asyncio.run(self.server.shutdown())
    
    def test_load_tools(self):
        tools = asyncio.run(self.server.list_tools())
        self.assertGreater(len(tools), 0)
    
    def test_call_tool(self):
        result = asyncio.run(self.server.call_tool("your_tool", {"param1": "test"}))
        self.assertEqual(result["param1"], "test")
```

## Best Practices

1. **Fehlerbehandlung**: Verwenden Sie try-except-Blöcke, um Fehler ordnungsgemäß zu erfassen und zu behandeln
2. **Logging**: Verwenden Sie den von der Basisklasse bereitgestellten Logger für konsistentes Logging
3. **Konfiguration**: Verwenden Sie den Konfigurationsmanager zum Laden und Speichern von Konfigurationen
4. **Dokumentation**: Dokumentieren Sie Ihren Code mit Docstrings und Kommentaren
5. **Tests**: Schreiben Sie Tests für Ihren Code, um sicherzustellen, dass er wie erwartet funktioniert
6. **Sicherheit**: Validieren und bereinigen Sie alle Eingaben, um Sicherheitsprobleme zu vermeiden
7. **Leistung**: Verwenden Sie async/await für I/O-gebundene Operationen, um die Leistung zu verbessern