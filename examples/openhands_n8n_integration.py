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
Beispiel für die Integration von OpenHands mit n8n-Workflows.

Dieses Skript demonstriert, wie man OpenHands mit n8n-Workflows integrieren kann,
um komplexe Automatisierungsaufgaben zu lösen.
"""

import os
import sys
import json
import time
import argparse
import logging
from typing import Dict, List, Any, Optional

# Füge das Stammverzeichnis zum Pfad hinzu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.mcp.client import MCPClient
from src.openhands.agent import get_openhands_agent

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('openhands-n8n-integration')


def parse_args():
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(description='OpenHands n8n Integration')
    parser.add_argument('--n8n-url', default='http://localhost:5678', help='URL der n8n-Instanz')
    parser.add_argument('--n8n-api-key', help='API-Schlüssel für n8n')
    parser.add_argument('--n8n-mcp-url', default='http://localhost:3000', help='URL des n8n MCP-Servers')
    parser.add_argument('--openhands-mcp-url', default='http://localhost:3006', help='URL des OpenHands MCP-Servers')
    parser.add_argument('--config-file', help='Pfad zur Konfigurationsdatei')
    parser.add_argument('--workflow-name', default='OpenHands Integration', help='Name des Workflows')
    parser.add_argument('--verbose', '-v', action='store_true', help='Ausführliche Ausgabe')
    return parser.parse_args()


def create_openhands_n8n_workflow(n8n_client: MCPClient, workflow_name: str) -> str:
    """
    Erstelle einen n8n-Workflow für die OpenHands-Integration.
    
    Args:
        n8n_client: MCPClient für den n8n MCP-Server
        workflow_name: Name des Workflows
        
    Returns:
        ID des erstellten Workflows
    """
    # Definiere den Workflow
    workflow = {
        "name": workflow_name,
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "openhands",
                    "options": {}
                },
                "name": "Webhook",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [
                    250,
                    300
                ]
            },
            {
                "parameters": {
                    "functionCode": "// Extract the task from the request\nconst task = $input.item.json.task || 'Keine Aufgabe angegeben';\nconst context = $input.item.json.context || {};\n\n// Return the task and context\nreturn {\n  task,\n  context,\n  timestamp: new Date().toISOString()\n};"
                },
                "name": "Extract Task",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [
                    500,
                    300
                ]
            },
            {
                "parameters": {
                    "url": "http://localhost:3006/mcp",
                    "options": {},
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "method",
                                "value": "mcp.call_function"
                            },
                            {
                                "name": "params",
                                "value": "={{ {\"function_name\": \"create_agent\", \"parameters\": {}} }}"
                            },
                            {
                                "name": "id",
                                "value": "={{ $json.timestamp }}"
                            }
                        ]
                    }
                },
                "name": "Create Agent",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [
                    750,
                    300
                ]
            },
            {
                "parameters": {
                    "functionCode": "// Extract the agent ID from the response\nconst agentId = $input.item.json.result.agent_id;\n\n// Return the agent ID along with the task and context\nreturn {\n  agent_id: agentId,\n  task: $input.item.json.task,\n  context: $input.item.json.context,\n  timestamp: $input.item.json.timestamp\n};"
                },
                "name": "Extract Agent ID",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [
                    1000,
                    300
                ]
            },
            {
                "parameters": {
                    "url": "http://localhost:3006/mcp",
                    "options": {},
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "method",
                                "value": "mcp.call_function"
                            },
                            {
                                "name": "params",
                                "value": "={{ {\"function_name\": \"execute_task\", \"parameters\": {\"agent_id\": $json.agent_id, \"task\": $json.task, \"context\": $json.context}} }}"
                            },
                            {
                                "name": "id",
                                "value": "={{ $json.timestamp }}"
                            }
                        ]
                    }
                },
                "name": "Execute Task",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [
                    1250,
                    300
                ]
            },
            {
                "parameters": {
                    "functionCode": "// Extract the task ID from the response\nconst taskId = $input.item.json.result.task_id;\n\n// Return the task ID along with the agent ID\nreturn {\n  agent_id: $input.item.json.agent_id,\n  task_id: taskId,\n  timestamp: $input.item.json.timestamp\n};"
                },
                "name": "Extract Task ID",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [
                    1500,
                    300
                ]
            },
            {
                "parameters": {
                    "amount": 1,
                    "unit": "seconds"
                },
                "name": "Wait",
                "type": "n8n-nodes-base.wait",
                "typeVersion": 1,
                "position": [
                    1750,
                    300
                ],
                "webhookId": "wait-1"
            },
            {
                "parameters": {
                    "url": "http://localhost:3006/mcp",
                    "options": {},
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "method",
                                "value": "mcp.call_function"
                            },
                            {
                                "name": "params",
                                "value": "={{ {\"function_name\": \"get_task_status\", \"parameters\": {\"task_id\": $json.task_id}} }}"
                            },
                            {
                                "name": "id",
                                "value": "={{ $json.timestamp }}"
                            }
                        ]
                    }
                },
                "name": "Get Task Status",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [
                    2000,
                    300
                ]
            },
            {
                "parameters": {
                    "conditions": {
                        "string": [
                            {
                                "value1": "={{ $json.result.status }}",
                                "operation": "notEqual",
                                "value2": "completed"
                            }
                        ]
                    }
                },
                "name": "Task Completed?",
                "type": "n8n-nodes-base.if",
                "typeVersion": 1,
                "position": [
                    2250,
                    300
                ]
            },
            {
                "parameters": {
                    "url": "http://localhost:3006/mcp",
                    "options": {},
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "method",
                                "value": "mcp.call_function"
                            },
                            {
                                "name": "params",
                                "value": "={{ {\"function_name\": \"get_task_result\", \"parameters\": {\"task_id\": $json.task_id}} }}"
                            },
                            {
                                "name": "id",
                                "value": "={{ $json.timestamp }}"
                            }
                        ]
                    }
                },
                "name": "Get Task Result",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [
                    2500,
                    200
                ]
            },
            {
                "parameters": {
                    "url": "http://localhost:3006/mcp",
                    "options": {},
                    "method": "POST",
                    "sendBody": True,
                    "bodyParameters": {
                        "parameters": [
                            {
                                "name": "method",
                                "value": "mcp.call_function"
                            },
                            {
                                "name": "params",
                                "value": "={{ {\"function_name\": \"delete_agent\", \"parameters\": {\"agent_id\": $json.agent_id}} }}"
                            },
                            {
                                "name": "id",
                                "value": "={{ $json.timestamp }}"
                            }
                        ]
                    }
                },
                "name": "Delete Agent",
                "type": "n8n-nodes-base.httpRequest",
                "typeVersion": 3,
                "position": [
                    2750,
                    200
                ]
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ {\"result\": $json.result.result} }}",
                    "options": {}
                },
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [
                    3000,
                    200
                ]
            }
        ],
        "connections": {
            "Webhook": {
                "main": [
                    [
                        {
                            "node": "Extract Task",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Extract Task": {
                "main": [
                    [
                        {
                            "node": "Create Agent",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Create Agent": {
                "main": [
                    [
                        {
                            "node": "Extract Agent ID",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Extract Agent ID": {
                "main": [
                    [
                        {
                            "node": "Execute Task",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Execute Task": {
                "main": [
                    [
                        {
                            "node": "Extract Task ID",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Extract Task ID": {
                "main": [
                    [
                        {
                            "node": "Wait",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Wait": {
                "main": [
                    [
                        {
                            "node": "Get Task Status",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Task Status": {
                "main": [
                    [
                        {
                            "node": "Task Completed?",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Task Completed?": {
                "main": [
                    [
                        {
                            "node": "Wait",
                            "type": "main",
                            "index": 0
                        }
                    ],
                    [
                        {
                            "node": "Get Task Result",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Get Task Result": {
                "main": [
                    [
                        {
                            "node": "Delete Agent",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Delete Agent": {
                "main": [
                    [
                        {
                            "node": "Respond to Webhook",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            }
        },
        "active": True,
        "settings": {},
        "versionId": "",
        "id": "1",
        "meta": {
            "instanceId": "1234567890"
        },
        "tags": []
    }
    
    # Erstelle den Workflow
    result = n8n_client.call_function("create_workflow", {
        "name": workflow_name,
        "nodes": workflow["nodes"],
        "connections": workflow["connections"],
        "active": True
    })
    
    return result["workflow"]["id"]


def test_openhands_n8n_workflow(n8n_url: str, workflow_name: str) -> Dict[str, Any]:
    """
    Teste den OpenHands n8n-Workflow.
    
    Args:
        n8n_url: URL der n8n-Instanz
        workflow_name: Name des Workflows
        
    Returns:
        Dict mit dem Ergebnis des Tests
    """
    # Hole die Webhook-URL
    webhook_url = f"{n8n_url}/webhook/openhands"
    
    # Definiere die Aufgabe
    task_data = {
        "task": "Erkläre, wie OpenHands mit n8n integriert werden kann und welche Vorteile diese Integration bietet.",
        "context": {
            "source": "openhands_n8n_integration.py",
            "purpose": "Demonstration der Integration"
        }
    }
    
    # Sende die Anfrage an den Webhook
    response = requests.post(webhook_url, json=task_data)
    
    if response.status_code != 200:
        raise Exception(f"Fehler bei der Anfrage an den Webhook: {response.text}")
    
    return response.json()


def main():
    """
    Main function.
    """
    args = parse_args()
    
    # Setze Log-Level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Hole API-Schlüssel aus Umgebungsvariablen, falls nicht angegeben
    n8n_api_key = args.n8n_api_key or os.environ.get('N8N_API_KEY')
    if not n8n_api_key:
        logger.error("API-Schlüssel für n8n nicht angegeben")
        sys.exit(1)
    
    # Verbinde mit dem n8n MCP-Server
    n8n_client = MCPClient(args.n8n_mcp_url)
    
    # Überprüfe die Verbindung
    server_info = n8n_client.get_server_info()
    logger.info(f"Verbunden mit {server_info['name']} v{server_info['version']}")
    logger.info(f"Status: {server_info['status']}")
    
    # Verbinde mit dem OpenHands MCP-Server
    openhands_client = MCPClient(args.openhands_mcp_url)
    
    # Überprüfe die Verbindung
    server_info = openhands_client.get_server_info()
    logger.info(f"Verbunden mit {server_info['name']} v{server_info['version']}")
    logger.info(f"Status: {server_info['status']}")
    logger.info(f"Aktive Agenten: {server_info['active_agents']}")
    logger.info(f"Aktive Aufgaben: {server_info['active_tasks']}")
    
    # Hole alle Workflows
    workflows = n8n_client.call_function("get_workflows", {})
    
    # Suche nach dem OpenHands-Workflow
    workflow_id = None
    for workflow in workflows["workflows"]:
        if workflow["name"] == args.workflow_name:
            workflow_id = workflow["id"]
            logger.info(f"Workflow '{args.workflow_name}' gefunden (ID: {workflow_id})")
            break
    
    # Erstelle den Workflow, falls er nicht existiert
    if not workflow_id:
        logger.info(f"Workflow '{args.workflow_name}' nicht gefunden, erstelle ihn...")
        workflow_id = create_openhands_n8n_workflow(n8n_client, args.workflow_name)
        logger.info(f"Workflow '{args.workflow_name}' erstellt (ID: {workflow_id})")
    
    # Aktiviere den Workflow
    n8n_client.call_function("activate_workflow", {
        "workflow_id": workflow_id
    })
    logger.info(f"Workflow '{args.workflow_name}' aktiviert")
    
    # Teste den Workflow
    logger.info("Teste den Workflow...")
    result = test_openhands_n8n_workflow(args.n8n_url, args.workflow_name)
    
    # Zeige das Ergebnis
    logger.info("Ergebnis des Tests:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()