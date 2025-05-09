#!/usr/bin/env python3
"""
MCP-Server-Generator für die dynamische Erstellung von MCP-Servern.

Dieser MCP-Server ermöglicht die dynamische Erstellung und Verwaltung von MCP-Servern
basierend auf benutzerdefinierten Konfigurationen.
"""

import os
import sys
import json
import uuid
import shutil
import logging
import asyncio
import argparse
import subprocess
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Tuple

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mcp-generator-server')


class MCPServerGenerator:
    """
    Generator für MCP-Server.
    
    Diese Klasse bietet Methoden zur dynamischen Erstellung und Verwaltung von MCP-Servern
    basierend auf benutzerdefinierten Konfigurationen.
    """
    
    def __init__(self, host: str = "0.0.0.0", port: int = 3007, servers_dir: str = "generated_servers"):
        """
        Initialisiere den MCP-Server-Generator.
        
        Args:
            host: Host für den MCP-Server
            port: Port für den MCP-Server
            servers_dir: Verzeichnis für generierte Server
        """
        self.host = host
        self.port = port
        self.servers_dir = servers_dir
        
        # Erstelle das Verzeichnis für generierte Server, falls es nicht existiert
        os.makedirs(servers_dir, exist_ok=True)
        
        # Initialisiere die Server
        self.servers = {}
        self._load_existing_servers()
        
        # Definiere die verfügbaren Funktionen
        self.functions = [
            {
                "name": "create_server",
                "description": "Erstellt einen neuen MCP-Server",
                "parameters": {
                    "name": {
                        "type": "string",
                        "description": "Name des Servers"
                    },
                    "description": {
                        "type": "string",
                        "description": "Beschreibung des Servers"
                    },
                    "functions": {
                        "type": "array",
                        "description": "Funktionen des Servers"
                    },
                    "port": {
                        "type": "integer",
                        "description": "Port für den Server"
                    },
                    "implementation": {
                        "type": "string",
                        "description": "Python-Code für die Implementierung der Funktionen"
                    }
                }
            },
            {
                "name": "get_server",
                "description": "Ruft Informationen über einen MCP-Server ab",
                "parameters": {
                    "server_id": {
                        "type": "string",
                        "description": "ID des Servers"
                    }
                }
            },
            {
                "name": "list_servers",
                "description": "Listet alle verfügbaren MCP-Server auf",
                "parameters": {}
            },
            {
                "name": "update_server",
                "description": "Aktualisiert einen MCP-Server",
                "parameters": {
                    "server_id": {
                        "type": "string",
                        "description": "ID des Servers"
                    },
                    "name": {
                        "type": "string",
                        "description": "Name des Servers"
                    },
                    "description": {
                        "type": "string",
                        "description": "Beschreibung des Servers"
                    },
                    "functions": {
                        "type": "array",
                        "description": "Funktionen des Servers"
                    },
                    "implementation": {
                        "type": "string",
                        "description": "Python-Code für die Implementierung der Funktionen"
                    }
                }
            },
            {
                "name": "delete_server",
                "description": "Löscht einen MCP-Server",
                "parameters": {
                    "server_id": {
                        "type": "string",
                        "description": "ID des Servers"
                    }
                }
            },
            {
                "name": "start_server",
                "description": "Startet einen MCP-Server",
                "parameters": {
                    "server_id": {
                        "type": "string",
                        "description": "ID des Servers"
                    }
                }
            },
            {
                "name": "stop_server",
                "description": "Stoppt einen MCP-Server",
                "parameters": {
                    "server_id": {
                        "type": "string",
                        "description": "ID des Servers"
                    }
                }
            },
            {
                "name": "restart_server",
                "description": "Startet einen MCP-Server neu",
                "parameters": {
                    "server_id": {
                        "type": "string",
                        "description": "ID des Servers"
                    }
                }
            },
            {
                "name": "get_server_status",
                "description": "Ruft den Status eines MCP-Servers ab",
                "parameters": {
                    "server_id": {
                        "type": "string",
                        "description": "ID des Servers"
                    }
                }
            },
            {
                "name": "get_server_logs",
                "description": "Ruft die Logs eines MCP-Servers ab",
                "parameters": {
                    "server_id": {
                        "type": "string",
                        "description": "ID des Servers"
                    },
                    "lines": {
                        "type": "integer",
                        "description": "Anzahl der Zeilen"
                    }
                }
            },
            {
                "name": "create_server_from_template",
                "description": "Erstellt einen neuen MCP-Server aus einer Vorlage",
                "parameters": {
                    "name": {
                        "type": "string",
                        "description": "Name des Servers"
                    },
                    "template": {
                        "type": "string",
                        "description": "Name der Vorlage"
                    },
                    "parameters": {
                        "type": "object",
                        "description": "Parameter für die Vorlage"
                    }
                }
            }
        ]
        
        # Definiere die verfügbaren Vorlagen
        self.templates = {
            "simple": {
                "description": "Einfacher MCP-Server mit grundlegenden Funktionen",
                "functions": [
                    {
                        "name": "hello_world",
                        "description": "Gibt 'Hello, World!' zurück",
                        "parameters": {}
                    },
                    {
                        "name": "echo",
                        "description": "Gibt den übergebenen Text zurück",
                        "parameters": {
                            "text": {
                                "type": "string",
                                "description": "Text, der zurückgegeben werden soll"
                            }
                        }
                    }
                ],
                "implementation": """
def _hello_world(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Gibt 'Hello, World!' zurück.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    return {
        "message": "Hello, World!"
    }

def _echo(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Gibt den übergebenen Text zurück.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    text = parameters.get("text", "")
    return {
        "text": text
    }
"""
            },
            "calculator": {
                "description": "MCP-Server für mathematische Berechnungen",
                "functions": [
                    {
                        "name": "add",
                        "description": "Addiert zwei Zahlen",
                        "parameters": {
                            "a": {
                                "type": "number",
                                "description": "Erste Zahl"
                            },
                            "b": {
                                "type": "number",
                                "description": "Zweite Zahl"
                            }
                        }
                    },
                    {
                        "name": "subtract",
                        "description": "Subtrahiert zwei Zahlen",
                        "parameters": {
                            "a": {
                                "type": "number",
                                "description": "Erste Zahl"
                            },
                            "b": {
                                "type": "number",
                                "description": "Zweite Zahl"
                            }
                        }
                    },
                    {
                        "name": "multiply",
                        "description": "Multipliziert zwei Zahlen",
                        "parameters": {
                            "a": {
                                "type": "number",
                                "description": "Erste Zahl"
                            },
                            "b": {
                                "type": "number",
                                "description": "Zweite Zahl"
                            }
                        }
                    },
                    {
                        "name": "divide",
                        "description": "Dividiert zwei Zahlen",
                        "parameters": {
                            "a": {
                                "type": "number",
                                "description": "Erste Zahl"
                            },
                            "b": {
                                "type": "number",
                                "description": "Zweite Zahl"
                            }
                        }
                    }
                ],
                "implementation": """
def _add(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Addiert zwei Zahlen.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    a = parameters.get("a", 0)
    b = parameters.get("b", 0)
    return {
        "result": a + b
    }

def _subtract(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Subtrahiert zwei Zahlen.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    a = parameters.get("a", 0)
    b = parameters.get("b", 0)
    return {
        "result": a - b
    }

def _multiply(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Multipliziert zwei Zahlen.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    a = parameters.get("a", 0)
    b = parameters.get("b", 0)
    return {
        "result": a * b
    }

def _divide(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Dividiert zwei Zahlen.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    a = parameters.get("a", 0)
    b = parameters.get("b", 1)
    if b == 0:
        return {
            "error": "Division by zero"
        }
    return {
        "result": a / b
    }
"""
            },
            "file_manager": {
                "description": "MCP-Server für Dateiverwaltung",
                "functions": [
                    {
                        "name": "read_file",
                        "description": "Liest eine Datei",
                        "parameters": {
                            "path": {
                                "type": "string",
                                "description": "Pfad zur Datei"
                            }
                        }
                    },
                    {
                        "name": "write_file",
                        "description": "Schreibt in eine Datei",
                        "parameters": {
                            "path": {
                                "type": "string",
                                "description": "Pfad zur Datei"
                            },
                            "content": {
                                "type": "string",
                                "description": "Inhalt der Datei"
                            }
                        }
                    },
                    {
                        "name": "delete_file",
                        "description": "Löscht eine Datei",
                        "parameters": {
                            "path": {
                                "type": "string",
                                "description": "Pfad zur Datei"
                            }
                        }
                    },
                    {
                        "name": "list_directory",
                        "description": "Listet den Inhalt eines Verzeichnisses auf",
                        "parameters": {
                            "path": {
                                "type": "string",
                                "description": "Pfad zum Verzeichnis"
                            }
                        }
                    }
                ],
                "implementation": """
import os

def _read_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Liest eine Datei.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    path = parameters.get("path", "")
    if not os.path.isfile(path):
        return {
            "error": f"File not found: {path}"
        }
    
    try:
        with open(path, "r") as f:
            content = f.read()
        return {
            "content": content
        }
    except Exception as e:
        return {
            "error": f"Error reading file: {str(e)}"
        }

def _write_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Schreibt in eine Datei.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    path = parameters.get("path", "")
    content = parameters.get("content", "")
    
    try:
        with open(path, "w") as f:
            f.write(content)
        return {
            "success": True,
            "message": f"File written: {path}"
        }
    except Exception as e:
        return {
            "error": f"Error writing file: {str(e)}"
        }

def _delete_file(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Löscht eine Datei.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    path = parameters.get("path", "")
    if not os.path.isfile(path):
        return {
            "error": f"File not found: {path}"
        }
    
    try:
        os.remove(path)
        return {
            "success": True,
            "message": f"File deleted: {path}"
        }
    except Exception as e:
        return {
            "error": f"Error deleting file: {str(e)}"
        }

def _list_directory(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Listet den Inhalt eines Verzeichnisses auf.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    path = parameters.get("path", ".")
    if not os.path.isdir(path):
        return {
            "error": f"Directory not found: {path}"
        }
    
    try:
        files = os.listdir(path)
        return {
            "files": files
        }
    except Exception as e:
        return {
            "error": f"Error listing directory: {str(e)}"
        }
"""
            },
            "database": {
                "description": "MCP-Server für einfache Datenbankverwaltung",
                "functions": [
                    {
                        "name": "create_table",
                        "description": "Erstellt eine Tabelle",
                        "parameters": {
                            "table_name": {
                                "type": "string",
                                "description": "Name der Tabelle"
                            },
                            "columns": {
                                "type": "array",
                                "description": "Spalten der Tabelle"
                            }
                        }
                    },
                    {
                        "name": "insert_data",
                        "description": "Fügt Daten in eine Tabelle ein",
                        "parameters": {
                            "table_name": {
                                "type": "string",
                                "description": "Name der Tabelle"
                            },
                            "data": {
                                "type": "object",
                                "description": "Daten, die eingefügt werden sollen"
                            }
                        }
                    },
                    {
                        "name": "query_data",
                        "description": "Fragt Daten aus einer Tabelle ab",
                        "parameters": {
                            "table_name": {
                                "type": "string",
                                "description": "Name der Tabelle"
                            },
                            "query": {
                                "type": "object",
                                "description": "Abfrage"
                            }
                        }
                    },
                    {
                        "name": "delete_data",
                        "description": "Löscht Daten aus einer Tabelle",
                        "parameters": {
                            "table_name": {
                                "type": "string",
                                "description": "Name der Tabelle"
                            },
                            "query": {
                                "type": "object",
                                "description": "Abfrage"
                            }
                        }
                    }
                ],
                "implementation": """
import os
import json
import sqlite3
from pathlib import Path

def _get_db_path(self) -> str:
    \"\"\"
    Gibt den Pfad zur Datenbank zurück.
    
    Returns:
        Pfad zur Datenbank
    \"\"\"
    db_dir = Path(self.servers_dir) / self.server_id
    os.makedirs(db_dir, exist_ok=True)
    return str(db_dir / "database.db")

def _create_table(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Erstellt eine Tabelle.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    table_name = parameters.get("table_name", "")
    columns = parameters.get("columns", [])
    
    if not table_name:
        return {
            "error": "Table name is required"
        }
    
    if not columns:
        return {
            "error": "Columns are required"
        }
    
    try:
        conn = sqlite3.connect(self._get_db_path())
        cursor = conn.cursor()
        
        # Erstelle die Tabelle
        column_defs = []
        for column in columns:
            name = column.get("name", "")
            type = column.get("type", "TEXT")
            column_defs.append(f"{name} {type}")
        
        sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(column_defs)})"
        cursor.execute(sql)
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Table created: {table_name}"
        }
    except Exception as e:
        return {
            "error": f"Error creating table: {str(e)}"
        }

def _insert_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Fügt Daten in eine Tabelle ein.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    table_name = parameters.get("table_name", "")
    data = parameters.get("data", {})
    
    if not table_name:
        return {
            "error": "Table name is required"
        }
    
    if not data:
        return {
            "error": "Data is required"
        }
    
    try:
        conn = sqlite3.connect(self._get_db_path())
        cursor = conn.cursor()
        
        # Füge die Daten ein
        columns = list(data.keys())
        values = list(data.values())
        placeholders = ", ".join(["?" for _ in values])
        
        sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
        cursor.execute(sql, values)
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Data inserted into {table_name}"
        }
    except Exception as e:
        return {
            "error": f"Error inserting data: {str(e)}"
        }

def _query_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Fragt Daten aus einer Tabelle ab.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    table_name = parameters.get("table_name", "")
    query = parameters.get("query", {})
    
    if not table_name:
        return {
            "error": "Table name is required"
        }
    
    try:
        conn = sqlite3.connect(self._get_db_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Erstelle die WHERE-Klausel
        where_clause = ""
        values = []
        
        if query:
            conditions = []
            for key, value in query.items():
                conditions.append(f"{key} = ?")
                values.append(value)
            
            where_clause = f"WHERE {' AND '.join(conditions)}"
        
        # Führe die Abfrage aus
        sql = f"SELECT * FROM {table_name} {where_clause}"
        cursor.execute(sql, values)
        
        # Hole die Ergebnisse
        rows = cursor.fetchall()
        results = []
        
        for row in rows:
            result = {}
            for key in row.keys():
                result[key] = row[key]
            results.append(result)
        
        conn.close()
        
        return {
            "results": results
        }
    except Exception as e:
        return {
            "error": f"Error querying data: {str(e)}"
        }

def _delete_data(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
    \"\"\"
    Löscht Daten aus einer Tabelle.
    
    Args:
        parameters: Parameter für die Funktion
        
    Returns:
        Dict mit dem Ergebnis
    \"\"\"
    table_name = parameters.get("table_name", "")
    query = parameters.get("query", {})
    
    if not table_name:
        return {
            "error": "Table name is required"
        }
    
    try:
        conn = sqlite3.connect(self._get_db_path())
        cursor = conn.cursor()
        
        # Erstelle die WHERE-Klausel
        where_clause = ""
        values = []
        
        if query:
            conditions = []
            for key, value in query.items():
                conditions.append(f"{key} = ?")
                values.append(value)
            
            where_clause = f"WHERE {' AND '.join(conditions)}"
        
        # Führe die Löschung aus
        sql = f"DELETE FROM {table_name} {where_clause}"
        cursor.execute(sql, values)
        
        conn.commit()
        conn.close()
        
        return {
            "success": True,
            "message": f"Data deleted from {table_name}"
        }
    except Exception as e:
        return {
            "error": f"Error deleting data: {str(e)}"
        }
"""
            }
        }
    
    def _load_existing_servers(self) -> None:
        """
        Lade existierende Server.
        """
        for server_dir in os.listdir(self.servers_dir):
            server_path = os.path.join(self.servers_dir, server_dir)
            if os.path.isdir(server_path):
                config_path = os.path.join(server_path, "config.json")
                if os.path.isfile(config_path):
                    try:
                        with open(config_path, "r") as f:
                            config = json.load(f)
                        
                        self.servers[server_dir] = config
                        logger.info(f"Loaded server {config['name']} (ID: {server_dir})")
                    except Exception as e:
                        logger.error(f"Error loading server {server_dir}: {e}")
    
    def get_server_info(self) -> Dict[str, Any]:
        """
        Rufe Informationen über den MCP-Server-Generator ab.
        
        Returns:
            Dict mit Serverinformationen
        """
        return {
            "name": "mcp-generator-server",
            "version": "1.0.0",
            "description": "MCP-Server-Generator für die dynamische Erstellung von MCP-Servern",
            "status": "online",
            "servers": len(self.servers),
            "templates": list(self.templates.keys())
        }
    
    def get_functions(self) -> List[Dict[str, Any]]:
        """
        Rufe die verfügbaren Funktionen ab.
        
        Returns:
            Liste mit Funktionsinformationen
        """
        return self.functions
    
    def call_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe eine Funktion auf.
        
        Args:
            function_name: Name der Funktion
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Funktion
            
        Raises:
            Exception: Wenn die Funktion nicht gefunden wurde oder ein Fehler auftrat
        """
        # Überprüfe, ob die Funktion existiert
        function = next((f for f in self.functions if f["name"] == function_name), None)
        if not function:
            raise Exception(f"Funktion {function_name} nicht gefunden")
        
        # Rufe die entsprechende Methode auf
        method_name = f"_{function_name}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(parameters)
        else:
            raise Exception(f"Methode {method_name} nicht implementiert")
    
    def _create_server(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstelle einen neuen MCP-Server.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem erstellten Server
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        name = parameters.get("name")
        if not name:
            raise Exception("Parameter name fehlt")
        
        description = parameters.get("description", "")
        functions = parameters.get("functions", [])
        port = parameters.get("port", 3100)
        implementation = parameters.get("implementation", "")
        
        # Generiere eine ID für den Server
        server_id = str(uuid.uuid4())
        
        # Erstelle das Verzeichnis für den Server
        server_dir = os.path.join(self.servers_dir, server_id)
        os.makedirs(server_dir, exist_ok=True)
        
        # Erstelle die Konfigurationsdatei
        config = {
            "name": name,
            "description": description,
            "functions": functions,
            "port": port,
            "status": "stopped"
        }
        
        with open(os.path.join(server_dir, "config.json"), "w") as f:
            json.dump(config, f, indent=2)
        
        # Erstelle die Implementierungsdatei
        server_code = self._generate_server_code(name, description, functions, port, implementation)
        
        with open(os.path.join(server_dir, "server.py"), "w") as f:
            f.write(server_code)
        
        # Mache die Datei ausführbar
        os.chmod(os.path.join(server_dir, "server.py"), 0o755)
        
        # Speichere den Server
        self.servers[server_id] = config
        
        return {
            "server_id": server_id,
            "name": name,
            "description": description,
            "functions": functions,
            "port": port,
            "status": "stopped"
        }
    
    def _get_server(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe Informationen über einen MCP-Server ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Server
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        server_id = parameters.get("server_id")
        if not server_id:
            raise Exception("Parameter server_id fehlt")
        
        if server_id not in self.servers:
            raise Exception(f"Server {server_id} nicht gefunden")
        
        server = self.servers[server_id]
        
        return {
            "server_id": server_id,
            "name": server["name"],
            "description": server["description"],
            "functions": server["functions"],
            "port": server["port"],
            "status": server["status"]
        }
    
    def _list_servers(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Liste alle verfügbaren MCP-Server auf.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit den Servern
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        servers = []
        
        for server_id, server in self.servers.items():
            servers.append({
                "server_id": server_id,
                "name": server["name"],
                "description": server["description"],
                "port": server["port"],
                "status": server["status"]
            })
        
        return {
            "servers": servers
        }
    
    def _update_server(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Aktualisiere einen MCP-Server.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem aktualisierten Server
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        server_id = parameters.get("server_id")
        if not server_id:
            raise Exception("Parameter server_id fehlt")
        
        if server_id not in self.servers:
            raise Exception(f"Server {server_id} nicht gefunden")
        
        server = self.servers[server_id]
        
        # Aktualisiere die Felder
        name = parameters.get("name")
        if name:
            server["name"] = name
        
        description = parameters.get("description")
        if description:
            server["description"] = description
        
        functions = parameters.get("functions")
        if functions:
            server["functions"] = functions
        
        implementation = parameters.get("implementation")
        
        # Speichere die Konfiguration
        with open(os.path.join(self.servers_dir, server_id, "config.json"), "w") as f:
            json.dump(server, f, indent=2)
        
        # Aktualisiere die Implementierung, falls angegeben
        if implementation:
            server_code = self._generate_server_code(
                server["name"],
                server["description"],
                server["functions"],
                server["port"],
                implementation
            )
            
            with open(os.path.join(self.servers_dir, server_id, "server.py"), "w") as f:
                f.write(server_code)
        
        return {
            "server_id": server_id,
            "name": server["name"],
            "description": server["description"],
            "functions": server["functions"],
            "port": server["port"],
            "status": server["status"]
        }
    
    def _delete_server(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Lösche einen MCP-Server.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        server_id = parameters.get("server_id")
        if not server_id:
            raise Exception("Parameter server_id fehlt")
        
        if server_id not in self.servers:
            raise Exception(f"Server {server_id} nicht gefunden")
        
        # Stoppe den Server, falls er läuft
        server = self.servers[server_id]
        if server["status"] == "running":
            self._stop_server({"server_id": server_id})
        
        # Lösche das Verzeichnis
        shutil.rmtree(os.path.join(self.servers_dir, server_id))
        
        # Lösche den Server aus der Liste
        del self.servers[server_id]
        
        return {
            "success": True,
            "message": f"Server {server_id} erfolgreich gelöscht"
        }
    
    def _start_server(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Starte einen MCP-Server.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        server_id = parameters.get("server_id")
        if not server_id:
            raise Exception("Parameter server_id fehlt")
        
        if server_id not in self.servers:
            raise Exception(f"Server {server_id} nicht gefunden")
        
        server = self.servers[server_id]
        
        # Überprüfe, ob der Server bereits läuft
        if server["status"] == "running":
            return {
                "success": True,
                "message": f"Server {server_id} läuft bereits"
            }
        
        # Starte den Server
        server_path = os.path.join(self.servers_dir, server_id, "server.py")
        log_path = os.path.join(self.servers_dir, server_id, "server.log")
        
        try:
            process = subprocess.Popen(
                [sys.executable, server_path],
                stdout=open(log_path, "a"),
                stderr=subprocess.STDOUT,
                cwd=os.path.join(self.servers_dir, server_id)
            )
            
            # Speichere die PID
            with open(os.path.join(self.servers_dir, server_id, "server.pid"), "w") as f:
                f.write(str(process.pid))
            
            # Aktualisiere den Status
            server["status"] = "running"
            
            # Speichere die Konfiguration
            with open(os.path.join(self.servers_dir, server_id, "config.json"), "w") as f:
                json.dump(server, f, indent=2)
            
            return {
                "success": True,
                "message": f"Server {server_id} erfolgreich gestartet",
                "pid": process.pid
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Fehler beim Starten des Servers {server_id}: {e}"
            }
    
    def _stop_server(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Stoppe einen MCP-Server.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        server_id = parameters.get("server_id")
        if not server_id:
            raise Exception("Parameter server_id fehlt")
        
        if server_id not in self.servers:
            raise Exception(f"Server {server_id} nicht gefunden")
        
        server = self.servers[server_id]
        
        # Überprüfe, ob der Server läuft
        if server["status"] != "running":
            return {
                "success": True,
                "message": f"Server {server_id} läuft nicht"
            }
        
        # Hole die PID
        pid_path = os.path.join(self.servers_dir, server_id, "server.pid")
        if not os.path.isfile(pid_path):
            return {
                "success": False,
                "message": f"PID-Datei für Server {server_id} nicht gefunden"
            }
        
        try:
            with open(pid_path, "r") as f:
                pid = int(f.read().strip())
            
            # Töte den Prozess
            os.kill(pid, 9)
            
            # Lösche die PID-Datei
            os.remove(pid_path)
            
            # Aktualisiere den Status
            server["status"] = "stopped"
            
            # Speichere die Konfiguration
            with open(os.path.join(self.servers_dir, server_id, "config.json"), "w") as f:
                json.dump(server, f, indent=2)
            
            return {
                "success": True,
                "message": f"Server {server_id} erfolgreich gestoppt"
            }
        except Exception as e:
            return {
                "success": False,
                "message": f"Fehler beim Stoppen des Servers {server_id}: {e}"
            }
    
    def _restart_server(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Starte einen MCP-Server neu.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        server_id = parameters.get("server_id")
        if not server_id:
            raise Exception("Parameter server_id fehlt")
        
        # Stoppe den Server
        stop_result = self._stop_server({"server_id": server_id})
        if not stop_result["success"]:
            return stop_result
        
        # Starte den Server
        return self._start_server({"server_id": server_id})
    
    def _get_server_status(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe den Status eines MCP-Servers ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Status
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        server_id = parameters.get("server_id")
        if not server_id:
            raise Exception("Parameter server_id fehlt")
        
        if server_id not in self.servers:
            raise Exception(f"Server {server_id} nicht gefunden")
        
        server = self.servers[server_id]
        
        # Überprüfe, ob der Server läuft
        pid_path = os.path.join(self.servers_dir, server_id, "server.pid")
        if os.path.isfile(pid_path):
            try:
                with open(pid_path, "r") as f:
                    pid = int(f.read().strip())
                
                # Überprüfe, ob der Prozess läuft
                try:
                    os.kill(pid, 0)
                    server["status"] = "running"
                except OSError:
                    server["status"] = "stopped"
                    os.remove(pid_path)
            except Exception:
                server["status"] = "stopped"
        else:
            server["status"] = "stopped"
        
        # Speichere die Konfiguration
        with open(os.path.join(self.servers_dir, server_id, "config.json"), "w") as f:
            json.dump(server, f, indent=2)
        
        return {
            "server_id": server_id,
            "status": server["status"]
        }
    
    def _get_server_logs(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Rufe die Logs eines MCP-Servers ab.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit den Logs
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        server_id = parameters.get("server_id")
        if not server_id:
            raise Exception("Parameter server_id fehlt")
        
        if server_id not in self.servers:
            raise Exception(f"Server {server_id} nicht gefunden")
        
        lines = parameters.get("lines", 100)
        
        log_path = os.path.join(self.servers_dir, server_id, "server.log")
        if not os.path.isfile(log_path):
            return {
                "logs": ""
            }
        
        try:
            with open(log_path, "r") as f:
                logs = f.readlines()
            
            # Hole die letzten Zeilen
            logs = logs[-lines:]
            
            return {
                "logs": "".join(logs)
            }
        except Exception as e:
            return {
                "error": f"Fehler beim Abrufen der Logs: {e}"
            }
    
    def _create_server_from_template(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Erstelle einen neuen MCP-Server aus einer Vorlage.
        
        Args:
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem erstellten Server
            
        Raises:
            Exception: Wenn ein Fehler auftrat
        """
        name = parameters.get("name")
        if not name:
            raise Exception("Parameter name fehlt")
        
        template = parameters.get("template")
        if not template:
            raise Exception("Parameter template fehlt")
        
        if template not in self.templates:
            raise Exception(f"Vorlage {template} nicht gefunden")
        
        template_data = self.templates[template]
        
        # Hole die Parameter für die Vorlage
        template_parameters = parameters.get("parameters", {})
        
        # Erstelle den Server
        return self._create_server({
            "name": name,
            "description": template_data["description"],
            "functions": template_data["functions"],
            "port": template_parameters.get("port", 3100),
            "implementation": template_data["implementation"]
        })
    
    def _generate_server_code(self, name: str, description: str, functions: List[Dict[str, Any]], port: int, implementation: str) -> str:
        """
        Generiere den Code für einen MCP-Server.
        
        Args:
            name: Name des Servers
            description: Beschreibung des Servers
            functions: Funktionen des Servers
            port: Port für den Server
            implementation: Python-Code für die Implementierung der Funktionen
            
        Returns:
            Generierter Code
        """
        # Erstelle den Code
        code = f"""#!/usr/bin/env python3
\"\"\"
{name} MCP-Server

{description}
\"\"\"

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Any, Optional, Union, Tuple

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('{name.lower()}-mcp-server')


class {name.replace(' ', '')}MCPServer:
    \"\"\"
    {name} MCP-Server.
    
    {description}
    \"\"\"
    
    def __init__(self, host: str = "0.0.0.0", port: int = {port}, server_id: str = ""):
        \"\"\"
        Initialisiere den {name} MCP-Server.
        
        Args:
            host: Host für den MCP-Server
            port: Port für den MCP-Server
            server_id: ID des Servers
        \"\"\"
        self.host = host
        self.port = port
        self.server_id = server_id
        self.servers_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Definiere die verfügbaren Funktionen
        self.functions = {json.dumps(functions, indent=4)}
    
    def get_server_info(self) -> Dict[str, Any]:
        \"\"\"
        Rufe Informationen über den MCP-Server ab.
        
        Returns:
            Dict mit Serverinformationen
        \"\"\"
        return {{
            "name": "{name}",
            "version": "1.0.0",
            "description": "{description}",
            "status": "online"
        }}
    
    def get_functions(self) -> List[Dict[str, Any]]:
        \"\"\"
        Rufe die verfügbaren Funktionen ab.
        
        Returns:
            Liste mit Funktionsinformationen
        \"\"\"
        return self.functions
    
    def call_function(self, function_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Rufe eine Funktion auf.
        
        Args:
            function_name: Name der Funktion
            parameters: Parameter für die Funktion
            
        Returns:
            Dict mit dem Ergebnis der Funktion
            
        Raises:
            Exception: Wenn die Funktion nicht gefunden wurde oder ein Fehler auftrat
        \"\"\"
        # Überprüfe, ob die Funktion existiert
        function = next((f for f in self.functions if f["name"] == function_name), None)
        if not function:
            raise Exception(f"Funktion {{function_name}} nicht gefunden")
        
        # Rufe die entsprechende Methode auf
        method_name = f"_{{function_name}}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            return method(parameters)
        else:
            raise Exception(f"Methode {{method_name}} nicht implementiert")
    
{implementation}
    
    async def start(self):
        \"\"\"
        Starte den MCP-Server.
        \"\"\"
        server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"MCP-Server gestartet auf {{addr}}")
        
        async with server:
            await server.serve_forever()
    
    async def _handle_client(self, reader, writer):
        \"\"\"
        Behandle eine Client-Verbindung.
        
        Args:
            reader: StreamReader für die Verbindung
            writer: StreamWriter für die Verbindung
        \"\"\"
        addr = writer.get_extra_info('peername')
        logger.info(f"Verbindung von {{addr}}")
        
        while True:
            try:
                # Lese eine Zeile vom Client
                data = await reader.readline()
                if not data:
                    break
                
                # Parse die Anfrage
                try:
                    request = json.loads(data.decode())
                except json.JSONDecodeError:
                    logger.error(f"Ungültige JSON-Anfrage: {{data.decode()}}")
                    response = {{
                        "error": {{
                            "code": -32700,
                            "message": "Parse error"
                        }}
                    }}
                    writer.write(f"{{json.dumps(response)}}\\n".encode())
                    await writer.drain()
                    continue
                
                # Verarbeite die Anfrage
                response = self._process_request(request)
                
                # Sende die Antwort
                writer.write(f"{{json.dumps(response)}}\\n".encode())
                await writer.drain()
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung der Anfrage: {{e}}")
                response = {{
                    "error": {{
                        "code": -32603,
                        "message": f"Internal error: {{str(e)}}"
                    }}
                }}
                writer.write(f"{{json.dumps(response)}}\\n".encode())
                await writer.drain()
                break
        
        # Schließe die Verbindung
        writer.close()
        await writer.wait_closed()
        logger.info(f"Verbindung zu {{addr}} geschlossen")
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        \"\"\"
        Verarbeite eine Anfrage.
        
        Args:
            request: Anfrage
            
        Returns:
            Dict mit der Antwort
        \"\"\"
        # Überprüfe, ob die Anfrage gültig ist
        if "method" not in request:
            return {{
                "error": {{
                    "code": -32600,
                    "message": "Invalid request"
                }}
            }}
        
        method = request["method"]
        params = request.get("params", {{}})
        request_id = request.get("id")
        
        # Verarbeite die Methode
        if method == "mcp.get_server_info":
            result = self.get_server_info()
        elif method == "mcp.get_functions":
            result = self.get_functions()
        elif method == "mcp.call_function":
            function_name = params.get("function_name")
            function_params = params.get("parameters", {{}})
            
            if not function_name:
                return {{
                    "error": {{
                        "code": -32602,
                        "message": "Invalid params: function_name is required"
                    }},
                    "id": request_id
                }}
            
            try:
                result = self.call_function(function_name, function_params)
            except Exception as e:
                return {{
                    "error": {{
                        "code": -32603,
                        "message": f"Internal error: {{str(e)}}"
                    }},
                    "id": request_id
                }}
        else:
            return {{
                "error": {{
                    "code": -32601,
                    "message": f"Method not found: {{method}}"
                }},
                "id": request_id
            }}
        
        # Erstelle die Antwort
        response = {{
            "result": result
        }}
        
        if request_id is not None:
            response["id"] = request_id
        
        return response


def parse_args():
    \"\"\"
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    \"\"\"
    parser = argparse.ArgumentParser(description='{name} MCP-Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host für den MCP-Server')
    parser.add_argument('--port', type=int, default={port}, help='Port für den MCP-Server')
    parser.add_argument('--server-id', help='ID des Servers')
    parser.add_argument('--verbose', '-v', action='store_true', help='Ausführliche Ausgabe')
    return parser.parse_args()


async def main():
    \"\"\"
    Main function.
    \"\"\"
    args = parse_args()
    
    # Setze Log-Level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Starte den MCP-Server
    server = {name.replace(' ', '')}MCPServer(args.host, args.port, args.server_id)
    await server.start()


if __name__ == "__main__":
    asyncio.run(main())
"""
        
        return code
    
    async def start(self):
        """
        Starte den MCP-Server-Generator.
        """
        server = await asyncio.start_server(
            self._handle_client,
            self.host,
            self.port
        )
        
        addr = server.sockets[0].getsockname()
        logger.info(f"MCP-Server-Generator gestartet auf {addr}")
        
        async with server:
            await server.serve_forever()
    
    async def _handle_client(self, reader, writer):
        """
        Behandle eine Client-Verbindung.
        
        Args:
            reader: StreamReader für die Verbindung
            writer: StreamWriter für die Verbindung
        """
        addr = writer.get_extra_info('peername')
        logger.info(f"Verbindung von {addr}")
        
        while True:
            try:
                # Lese eine Zeile vom Client
                data = await reader.readline()
                if not data:
                    break
                
                # Parse die Anfrage
                try:
                    request = json.loads(data.decode())
                except json.JSONDecodeError:
                    logger.error(f"Ungültige JSON-Anfrage: {data.decode()}")
                    response = {
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    writer.write(f"{json.dumps(response)}\n".encode())
                    await writer.drain()
                    continue
                
                # Verarbeite die Anfrage
                response = self._process_request(request)
                
                # Sende die Antwort
                writer.write(f"{json.dumps(response)}\n".encode())
                await writer.drain()
            except Exception as e:
                logger.error(f"Fehler bei der Verarbeitung der Anfrage: {e}")
                response = {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                writer.write(f"{json.dumps(response)}\n".encode())
                await writer.drain()
                break
        
        # Schließe die Verbindung
        writer.close()
        await writer.wait_closed()
        logger.info(f"Verbindung zu {addr} geschlossen")
    
    def _process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verarbeite eine Anfrage.
        
        Args:
            request: Anfrage
            
        Returns:
            Dict mit der Antwort
        """
        # Überprüfe, ob die Anfrage gültig ist
        if "method" not in request:
            return {
                "error": {
                    "code": -32600,
                    "message": "Invalid request"
                }
            }
        
        method = request["method"]
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Verarbeite die Methode
        if method == "mcp.get_server_info":
            result = self.get_server_info()
        elif method == "mcp.get_functions":
            result = self.get_functions()
        elif method == "mcp.call_function":
            function_name = params.get("function_name")
            function_params = params.get("parameters", {})
            
            if not function_name:
                return {
                    "error": {
                        "code": -32602,
                        "message": "Invalid params: function_name is required"
                    },
                    "id": request_id
                }
            
            try:
                result = self.call_function(function_name, function_params)
            except Exception as e:
                return {
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    },
                    "id": request_id
                }
        else:
            return {
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                },
                "id": request_id
            }
        
        # Erstelle die Antwort
        response = {
            "result": result
        }
        
        if request_id is not None:
            response["id"] = request_id
        
        return response


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='MCP-Server-Generator')
    parser.add_argument('--host', default='0.0.0.0', help='Host für den MCP-Server-Generator')
    parser.add_argument('--port', type=int, default=3007, help='Port für den MCP-Server-Generator')
    parser.add_argument('--servers-dir', default='generated_servers', help='Verzeichnis für generierte Server')
    parser.add_argument('--verbose', '-v', action='store_true', help='Ausführliche Ausgabe')
    return parser.parse_args()


async def main():
    """
    Main function.
    """
    args = parse_args()
    
    # Setze Log-Level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Starte den MCP-Server-Generator
    generator = MCPServerGenerator(args.host, args.port, args.servers_dir)
    await generator.start()


if __name__ == "__main__":
    asyncio.run(main())