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


import requests
import json
import sys
import os
import argparse

def create_n8n_workflow(n8n_url, n8n_api_key, mcp_servers):
    """Create an n8n workflow that integrates with the MCP servers."""
    logger.info("Creating n8n workflow for MCP integration...")
    
    # Prepare the workflow data
    workflow = {
        "name": "MCP Server Integration",
        "nodes": [
            {
                "parameters": {
                    "httpMethod": "POST",
                    "path": "mcp-endpoint",
                    "options": {
                        "responseMode": "responseNode"
                    }
                },
                "name": "MCP Endpoint",
                "type": "n8n-nodes-base.webhook",
                "typeVersion": 1,
                "position": [240, 300],
                "id": "mcp-endpoint-webhook"
            },
            {
                "parameters": {
                    "functionCode": f"""
// Parse the incoming request
const body = $input.body;
const method = body.method;
const params = body.params || {{}};

// Handle different MCP methods
if (method === 'mcp.listTools') {{
    // Return a list of available tools
    return {{
        jsonrpc: "2.0",
        id: body.id,
        result: [
            {{
                name: "create_github_issue",
                description: "Create an issue in GitHub",
                parameter_schema: {{
                    type: "object",
                    properties: {{
                        title: {{
                            type: "string",
                            description: "Issue title"
                        }},
                        body: {{
                            type: "string",
                            description: "Issue body"
                        }},
                        repository: {{
                            type: "string",
                            description: "Repository name (format: owner/repo)"
                        }}
                    }},
                    required: ["title", "repository"]
                }}
            }},
            {{
                name: "update_work_package",
                description: "Update a work package in OpenProject",
                parameter_schema: {{
                    type: "object",
                    properties: {{
                        id: {{
                            type: "string",
                            description: "Work package ID"
                        }},
                        subject: {{
                            type: "string",
                            description: "Work package subject"
                        }},
                        description: {{
                            type: "string",
                            description: "Work package description"
                        }},
                        status: {{
                            type: "string",
                            description: "Work package status"
                        }}
                    }},
                    required: ["id"]
                }}
            }},
            {{
                name: "sync_documentation",
                description: "Synchronize documentation between AFFiNE and GitHub",
                parameter_schema: {{
                    type: "object",
                    properties: {{
                        source: {{
                            type: "string",
                            description: "Source document ID"
                        }},
                        destination: {{
                            type: "string",
                            description: "Destination path"
                        }},
                        format: {{
                            type: "string",
                            description: "Output format (md, html, pdf)",
                            enum: ["md", "html", "pdf"]
                        }}
                    }},
                    required: ["source", "destination"]
                }}
            }}
        ]
    }};
}} else if (method === 'mcp.callTool') {{
    // Extract tool name and arguments
    const toolName = params.name;
    const args = params.arguments || {{}};
    
    // Route to the appropriate tool handler
    if (toolName === 'create_github_issue') {{
        // Set output to be processed by the GitHub node
        $node['GitHub Issue'].json = {{
            toolName,
            args,
            action: "create_issue"
        }};
        return {{
            jsonrpc: "2.0",
            id: body.id,
            result: {{
                status: "processing",
                message: "Creating GitHub issue..."
            }}
        }};
    }} else if (toolName === 'update_work_package') {{
        // Set output to be processed by the OpenProject node
        $node['OpenProject'].json = {{
            toolName,
            args,
            action: "update_work_package"
        }};
        return {{
            jsonrpc: "2.0",
            id: body.id,
            result: {{
                status: "processing",
                message: "Updating OpenProject work package..."
            }}
        }};
    }} else if (toolName === 'sync_documentation') {{
        // Set output to be processed by the Documentation Sync node
        $node['Documentation Sync'].json = {{
            toolName,
            args,
            action: "sync_documentation"
        }};
        return {{
            jsonrpc: "2.0",
            id: body.id,
            result: {{
                status: "processing",
                message: "Synchronizing documentation..."
            }}
        }};
    }} else {{
        // Unknown tool
        return {{
            jsonrpc: "2.0",
            id: body.id,
            error: {{
                code: -32601,
                message: `Tool not found: ${{toolName}}`
            }}
        }};
    }}
}} else {{
    // Unknown method
    return {{
        jsonrpc: "2.0",
        id: body.id,
        error: {{
            code: -32601,
            message: `Method not found: ${{method}}`
        }}
    }};
}}
"""
                },
                "name": "MCP Request Handler",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [460, 300],
                "id": "mcp-request-handler"
            },
            {
                "parameters": {
                    "authentication": "githubApi",
                    "resource": "issue",
                    "owner": "={{ $json.args.repository.split('/')[0] }}",
                    "repository": "={{ $json.args.repository.split('/')[1] }}",
                    "title": "={{ $json.args.title }}",
                    "body": "={{ $json.args.body }}",
                    "labels": "={{ $json.args.labels || [] }}",
                    "assignees": "={{ $json.args.assignees || [] }}"
                },
                "name": "GitHub Issue",
                "type": "n8n-nodes-base.github",
                "typeVersion": 1,
                "position": [680, 200],
                "id": "github-issue",
                "credentials": {
                    "githubApi": {
                        "id": "1",
                        "name": "GitHub account"
                    }
                }
            },
            {
                "parameters": {
                    "authentication": "openProjectApi",
                    "resource": "workPackage",
                    "operation": "update",
                    "id": "={{ $json.args.id }}",
                    "updateFields": {
                        "subject": "={{ $json.args.subject }}",
                        "description": "={{ $json.args.description }}",
                        "status": "={{ $json.args.status }}"
                    }
                },
                "name": "OpenProject",
                "type": "n8n-nodes-base.openProject",
                "typeVersion": 1,
                "position": [680, 300],
                "id": "openproject",
                "credentials": {
                    "openProjectApi": {
                        "id": "2",
                        "name": "OpenProject account"
                    }
                }
            },
            {
                "parameters": {
                    "functionCode": """
// Handle documentation synchronization
const source = $input.json.args.source;
const destination = $input.json.args.destination;
const format = $input.json.args.format || 'md';

// This is a placeholder for the actual implementation
// In a real scenario, you would fetch the document from AFFiNE and push it to GitHub

return {
    source,
    destination,
    format,
    status: "success",
    message: `Documentation synchronized from ${source} to ${destination} in ${format} format.`
};
"""
                },
                "name": "Documentation Sync",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [680, 400],
                "id": "documentation-sync"
            },
            {
                "parameters": {
                    "functionCode": """
// Process the result from the tool execution
let result;

if ($input.json.status && $input.json.message) {
    // Result from Documentation Sync
    result = {
        status: $input.json.status,
        message: $input.json.message
    };
} else if ($input.json.number) {
    // Result from GitHub Issue
    result = {
        issue_number: $input.json.number,
        issue_url: $input.json.html_url,
        status: "success",
        message: `GitHub issue created: #${$input.json.number}`
    };
} else if ($input.json.id) {
    // Result from OpenProject
    result = {
        work_package_id: $input.json.id,
        status: "success",
        message: `OpenProject work package updated: #${$input.json.id}`
    };
} else {
    // Unknown result
    result = {
        status: "error",
        message: "Unknown result format"
    };
}

return {
    jsonrpc: "2.0",
    id: $input.body.id,
    result
};
"""
                },
                "name": "Format Response",
                "type": "n8n-nodes-base.function",
                "typeVersion": 1,
                "position": [900, 300],
                "id": "format-response"
            },
            {
                "parameters": {
                    "respondWith": "json",
                    "responseBody": "={{ $json }}",
                    "options": {}
                },
                "name": "Respond to Webhook",
                "type": "n8n-nodes-base.respondToWebhook",
                "typeVersion": 1,
                "position": [1120, 300],
                "id": "respond-to-webhook"
            }
        ],
        "connections": {
            "mcp-endpoint-webhook": {
                "main": [
                    [
                        {
                            "node": "mcp-request-handler",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "mcp-request-handler": {
                "main": [
                    [
                        {
                            "node": "GitHub Issue",
                            "type": "main",
                            "index": 0
                        },
                        {
                            "node": "OpenProject",
                            "type": "main",
                            "index": 0
                        },
                        {
                            "node": "Documentation Sync",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "GitHub Issue": {
                "main": [
                    [
                        {
                            "node": "Format Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "OpenProject": {
                "main": [
                    [
                        {
                            "node": "Format Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Documentation Sync": {
                "main": [
                    [
                        {
                            "node": "Format Response",
                            "type": "main",
                            "index": 0
                        }
                    ]
                ]
            },
            "Format Response": {
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
        "settings": {
            "executionOrder": "v1",
            "saveManualExecutions": True,
            "callerPolicy": "workflowsFromSameOwner",
            "errorWorkflow": ""
        },
        "tags": ["mcp"]
    }
    
    # Add MCP server information to the workflow
    mcp_servers_info = "Available MCP Servers:\\n\\n"
    for server_name, server_url in mcp_servers.items():
        mcp_servers_info += f"- {server_name}: {server_url}\\n"
    
    workflow["description"] = f"Integration with MCP servers for AI agent tools.\\n\\n{mcp_servers_info}"
    
    # Create the workflow in n8n
    try:
        headers = {
            "X-N8N-API-KEY": n8n_api_key,
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            f"{n8n_url}/api/v1/workflows",
            headers=headers,
            json=workflow
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ n8n workflow created successfully with ID: {result['id']}")
            return True
        else:
            print(f"❌ Failed to create n8n workflow: {response.status_code} - {response.text}")
            return False
    
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Create an n8n workflow for MCP integration")
    parser.add_argument("--n8n-url", default=os.environ.get("N8N_URL", "http://localhost:5678"), help="n8n URL")
    parser.add_argument("--n8n-api-key", default=os.environ.get("N8N_API_KEY"), help="n8n API key")
    parser.add_argument("--config", default="openhands-mcp-config.json", help="Path to the MCP configuration file")
    
    args = parser.parse_args()
    
    if not args.n8n_api_key:
        logger.info("Error: n8n API key is required. Set it with --n8n-api-key or the N8N_API_KEY environment variable.")
        sys.exit(1)
    
    # Load the MCP configuration
    try:
        with open(args.config, "r") as f:
            config = json.load(f)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Get the MCP servers from the configuration
    servers = config.get("mcp", {}).get("servers", {})
    if not servers:
        logger.info("No MCP servers found in the configuration.")
        sys.exit(1)
    
    # Extract server URLs
    mcp_servers = {name: server.get("url") for name, server in servers.items()}
    
    # Create the n8n workflow
    if create_n8n_workflow(args.n8n_url, args.n8n_api_key, mcp_servers):
        logger.info("n8n workflow created successfully! 🎉")
        sys.exit(0)
    else:
        logger.info("Failed to create n8n workflow.")
        sys.exit(1)

if __name__ == "__main__":
    main()