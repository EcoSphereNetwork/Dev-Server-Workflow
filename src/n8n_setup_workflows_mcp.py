#!/usr/bin/env python3
"""
n8n Setup - MCP-Workflow Definition

Dieses Modul enthält die Definition für einen MCP-Server-Trigger-Workflow, 
der als Brücke zwischen MCP und n8n dient.
"""

# MCP-Server Workflow
MCP_SERVER_WORKFLOW = {
    "name": "MCP Server Integration",
    "tags": ["mcp", "integration", "automation"],
    "description": "Workflow zur Integration von n8n mit dem Model Context Protocol (MCP) für KI-Agenten",
    "nodes": [
        {
            "parameters": {
                "path": "/mcp/endpoint",
                "options": {
                    "responseMode": "responseNode"
                }
            },
            "name": "MCP Server Trigger",
            "type": "n8n-nodes-base.mcpTrigger",
            "position": [
                250,
                300
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.tool}}",
                            "operation": "equal",
                            "value2": "create_github_issue"
                        }
                    ]
                }
            },
            "name": "Is Create Issue?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                300
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.tool}}",
                            "operation": "equal",
                            "value2": "update_work_package"
                        }
                    ]
                }
            },
            "name": "Is Update Work Package?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                450
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.tool}}",
                            "operation": "equal",
                            "value2": "sync_documentation"
                        }
                    ]
                }
            },
            "name": "Is Sync Documentation?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                600
            ]
        },
        {
            "parameters": {
                "resource": "issue",
                "operation": "create",
                "owner": "={{$json.arguments.owner}}",
                "repository": "={{$json.arguments.repo}}",
                "title": "={{$json.arguments.title}}",
                "body": "={{$json.arguments.body}}",
                "additionalFields": {}
            },
            "name": "Create GitHub Issue",
            "type": "n8n-nodes-base.github",
            "position": [
                650,
                200
            ]
        },
        {
            "parameters": {
                "url": "={{$json.openProjectUrl}}/api/v3/work_packages/{{$json.arguments.id}}",
                "method": "PATCH",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "options": {
                    "additionalHeaders": {
                        "values": {
                            "Content-Type": "application/json"
                        }
                    }
                },
                "bodyParametersUi": {
                    "parameter": [
                        {
                            "name": "_type",
                            "value": "WorkPackage"
                        },
                        {
                            "name": "description.raw",
                            "value": "={{$json.arguments.description || $json.existingDescription}}"
                        },
                        {
                            "name": "status",
                            "value": "={{'/api/v3/statuses/' + ($json.arguments.status || $json.existingStatus)}}"
                        }
                    ]
                }
            },
            "name": "Update Work Package",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                650,
                450
            ]
        },
        {
            "parameters": {
                "functionCode": "// Implementiert die Synchronisierung von Dokumenten zwischen AFFiNE und GitHub\nconst docId = $json.arguments.doc_id;\nconst githubPath = $json.arguments.github_path;\nconst owner = $json.arguments.owner;\nconst repo = $json.arguments.repo;\n\nconsole.log(`Syncing document ${docId} to GitHub ${owner}/${repo}/${githubPath}`);\n\n// Hier würde die tatsächliche Implementierung der Dokumentensynchronisierung erfolgen\n// In diesem Beispiel simulieren wir eine erfolgreiche Synchronisierung\nreturn {\n  json: {\n    status: \"success\",\n    doc_id: docId,\n    github_path: githubPath,\n    commit_sha: \"abc123\",\n    timestamp: new Date().toISOString()\n  }\n};"
            },
            "name": "Sync Documentation",
            "type": "n8n-nodes-base.function",
            "position": [
                650,
                600
            ]
        },
        {
            "parameters": {
                "content": "={{$json}}",
                "options": {}
            },
            "name": "MCP Response",
            "type": "n8n-nodes-base.respondToWebhook",
            "position": [
                850,
                300
            ]
        },
        {
            "parameters": {
                "functionCode": "// Füge Konfiguration für OpenProject hinzu\nconst openProjectUrl = \"https://your-openproject-instance.com\";\n\nreturn {\n  ...item,\n  openProjectUrl\n};"
            },
            "name": "Add OpenProject Config",
            "type": "n8n-nodes-base.function",
            "position": [
                650,
                350
            ]
        }
    ],
    "connections": {
        "MCP Server Trigger": {
            "main": [
                [
                    {
                        "node": "Is Create Issue?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is Create Issue?": {
            "main": [
                [
                    {
                        "node": "Create GitHub Issue",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Is Update Work Package?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is Update Work Package?": {
            "main": [
                [
                    {
                        "node": "Add OpenProject Config",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Is Sync Documentation?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is Sync Documentation?": {
            "main": [
                [
                    {
                        "node": "Sync Documentation",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Create GitHub Issue": {
            "main": [
                [
                    {
                        "node": "MCP Response",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Add OpenProject Config": {
            "main": [
                [
                    {
                        "node": "Update Work Package",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Update Work Package": {
            "main": [
                [
                    {
                        "node": "MCP Response",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Sync Documentation": {
            "main": [
                [
                    {
                        "node": "MCP Response",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}
