#!/usr/bin/env python3
"""
n8n Setup - Enhanced MCP-Workflow Definition

Dieses Modul enthält eine verbesserte Definition für einen MCP-Server-Trigger-Workflow,
der als Brücke zwischen MCP und n8n dient. Es unterstützt alle implementierten MCP-Server
und bietet eine verbesserte Fehlerbehandlung und Logging.
"""

# Enhanced MCP-Server Workflow
ENHANCED_MCP_SERVER_WORKFLOW = {
    "name": "Enhanced MCP Server Integration",
    "tags": ["mcp", "integration", "automation", "enhanced"],
    "description": "Verbesserter Workflow zur Integration von n8n mit dem Model Context Protocol (MCP) für KI-Agenten. Unterstützt alle implementierten MCP-Server.",
    "nodes": [
        {
            "parameters": {
                "httpMethod": "POST",
                "path": "mcp/endpoint",
                "options": {
                    "responseMode": "responseNode"
                }
            },
            "name": "MCP Webhook",
            "type": "n8n-nodes-base.webhook",
            "typeVersion": 1,
            "position": [250, 300]
        },
        {
            "parameters": {
                "functionCode": """
// Parse the incoming MCP request
const body = $input.body;
const method = body.method;
const params = body.params || {};
const requestId = body.id;

// Initialize response object
let response = {
    jsonrpc: "2.0",
    id: requestId
};

// Log the incoming request
console.log(`MCP Request: ${method}`, JSON.stringify(params));

// Handle different MCP methods
if (method === 'mcp.listTools') {
    // Return a list of all available tools from all MCP servers
    return {
        method,
        params,
        requestId,
        action: "listTools"
    };
} else if (method === 'mcp.callTool') {
    // Extract tool name and arguments
    const toolName = params.name;
    const args = params.arguments || {};
    
    // Log the tool call
    console.log(`Tool Call: ${toolName}`, JSON.stringify(args));
    
    return {
        method,
        params,
        requestId,
        action: "callTool",
        toolName,
        args
    };
} else {
    // Unknown method
    response.error = {
        code: -32601,
        message: `Method not supported: ${method}`
    };
    return response;
}
"""
            },
            "name": "Parse MCP Request",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [450, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.action}}",
                            "operation": "equal",
                            "value2": "listTools"
                        }
                    ]
                }
            },
            "name": "Is List Tools?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [650, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.action}}",
                            "operation": "equal",
                            "value2": "callTool"
                        }
                    ]
                }
            },
            "name": "Is Call Tool?",
            "type": "n8n-nodes-base.if",
            "typeVersion": 1,
            "position": [650, 500]
        },
        {
            "parameters": {
                "functionCode": """
// Return a list of all available tools
return {
    jsonrpc: "2.0",
    id: $json.requestId,
    result: [
        // Filesystem MCP Server Tools
        {
            name: "read_file",
            description: "Read the content of a file",
            parameter_schema: {
                type: "object",
                properties: {
                    path: {
                        type: "string",
                        description: "Path to the file"
                    }
                },
                required: ["path"]
            }
        },
        {
            name: "write_file",
            description: "Write content to a file",
            parameter_schema: {
                type: "object",
                properties: {
                    path: {
                        type: "string",
                        description: "Path to the file"
                    },
                    content: {
                        type: "string",
                        description: "Content to write"
                    }
                },
                required: ["path", "content"]
            }
        },
        {
            name: "list_directory",
            description: "List the contents of a directory",
            parameter_schema: {
                type: "object",
                properties: {
                    path: {
                        type: "string",
                        description: "Path to the directory"
                    }
                },
                required: ["path"]
            }
        },
        
        // Desktop Commander MCP Server Tools
        {
            name: "execute_command",
            description: "Execute a terminal command",
            parameter_schema: {
                type: "object",
                properties: {
                    command: {
                        type: "string",
                        description: "Command to execute"
                    }
                },
                required: ["command"]
            }
        },
        
        // GitHub MCP Server Tools
        {
            name: "create_github_issue",
            description: "Create an issue in GitHub",
            parameter_schema: {
                type: "object",
                properties: {
                    repository: {
                        type: "string",
                        description: "Repository name (format: owner/repo)"
                    },
                    title: {
                        type: "string",
                        description: "Issue title"
                    },
                    body: {
                        type: "string",
                        description: "Issue body"
                    },
                    labels: {
                        type: "array",
                        items: {
                            type: "string"
                        },
                        description: "Issue labels"
                    }
                },
                required: ["repository", "title"]
            }
        },
        {
            name: "create_github_pr",
            description: "Create a pull request in GitHub",
            parameter_schema: {
                type: "object",
                properties: {
                    repository: {
                        type: "string",
                        description: "Repository name (format: owner/repo)"
                    },
                    title: {
                        type: "string",
                        description: "PR title"
                    },
                    body: {
                        type: "string",
                        description: "PR body"
                    },
                    head: {
                        type: "string",
                        description: "Head branch"
                    },
                    base: {
                        type: "string",
                        description: "Base branch"
                    }
                },
                required: ["repository", "title", "head", "base"]
            }
        },
        
        // Wikipedia MCP Server Tools
        {
            name: "search_wikipedia",
            description: "Search Wikipedia for a topic",
            parameter_schema: {
                type: "object",
                properties: {
                    query: {
                        type: "string",
                        description: "Search query"
                    },
                    language: {
                        type: "string",
                        description: "Language code (e.g., en, de, fr)",
                        default: "en"
                    }
                },
                required: ["query"]
            }
        },
        
        // n8n Workflow Tools
        {
            name: "update_work_package",
            description: "Update a work package in OpenProject",
            parameter_schema: {
                type: "object",
                properties: {
                    id: {
                        type: "string",
                        description: "Work package ID"
                    },
                    subject: {
                        type: "string",
                        description: "Work package subject"
                    },
                    description: {
                        type: "string",
                        description: "Work package description"
                    },
                    status: {
                        type: "string",
                        description: "Work package status"
                    }
                },
                required: ["id"]
            }
        },
        {
            name: "sync_documentation",
            description: "Synchronize documentation between AFFiNE and GitHub",
            parameter_schema: {
                type: "object",
                properties: {
                    source: {
                        type: "string",
                        description: "Source document ID"
                    },
                    destination: {
                        type: "string",
                        description: "Destination path"
                    },
                    format: {
                        type: "string",
                        description: "Output format (md, html, pdf)",
                        enum: ["md", "html", "pdf"]
                    }
                },
                required: ["source", "destination"]
            }
        }
    ]
};
"""
            },
            "name": "List All Tools",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [850, 300]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.toolName}}",
                            "operation": "equal",
                            "value2": "create_github_issue"
                        }
                    ]
                }
            },
            "name": "Route Tool Call",
            "type": "n8n-nodes-base.switch",
            "typeVersion": 1,
            "position": [850, 500]
        },
        {
            "parameters": {
                "authentication": "githubApi",
                "resource": "issue",
                "owner": "={{$json.args.repository.split('/')[0]}}",
                "repository": "={{$json.args.repository.split('/')[1]}}",
                "title": "={{$json.args.title}}",
                "body": "={{$json.args.body}}",
                "labels": "={{$json.args.labels || []}}",
                "assignees": "={{$json.args.assignees || []}}"
            },
            "name": "Create GitHub Issue",
            "type": "n8n-nodes-base.github",
            "typeVersion": 1,
            "position": [1050, 400],
            "credentials": {
                "githubApi": {
                    "id": "1",
                    "name": "GitHub account"
                }
            }
        },
        {
            "parameters": {
                "url": "={{$json.args.repository.includes('/') ? `https://api.github.com/repos/${$json.args.repository}/pulls` : `https://api.github.com/repos/EcoSphereNetwork/${$json.args.repository}/pulls`}}",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "method": "POST",
                "sendBody": true,
                "bodyParameters": {
                    "parameters": [
                        {
                            "name": "title",
                            "value": "={{$json.args.title}}"
                        },
                        {
                            "name": "body",
                            "value": "={{$json.args.body}}"
                        },
                        {
                            "name": "head",
                            "value": "={{$json.args.head}}"
                        },
                        {
                            "name": "base",
                            "value": "={{$json.args.base || 'main'}}"
                        }
                    ]
                },
                "options": {}
            },
            "name": "Create GitHub PR",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 1,
            "position": [1050, 500],
            "credentials": {
                "httpHeaderAuth": {
                    "id": "2",
                    "name": "GitHub Auth"
                }
            }
        },
        {
            "parameters": {
                "url": "http://filesystem-mcp:3001/mcp",
                "authentication": "none",
                "method": "POST",
                "sendBody": true,
                "bodyParameters": {
                    "parameters": [
                        {
                            "name": "jsonrpc",
                            "value": "2.0"
                        },
                        {
                            "name": "id",
                            "value": "={{$json.requestId}}"
                        },
                        {
                            "name": "method",
                            "value": "mcp.callTool"
                        },
                        {
                            "name": "params",
                            "value": "={ \"name\": \"{{$json.toolName}}\", \"arguments\": {{$json.args}} }"
                        }
                    ]
                },
                "options": {}
            },
            "name": "Call Filesystem MCP",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 1,
            "position": [1050, 600]
        },
        {
            "parameters": {
                "url": "http://wikipedia-mcp:3008/mcp",
                "authentication": "none",
                "method": "POST",
                "sendBody": true,
                "bodyParameters": {
                    "parameters": [
                        {
                            "name": "jsonrpc",
                            "value": "2.0"
                        },
                        {
                            "name": "id",
                            "value": "={{$json.requestId}}"
                        },
                        {
                            "name": "method",
                            "value": "mcp.callTool"
                        },
                        {
                            "name": "params",
                            "value": "={ \"name\": \"{{$json.toolName}}\", \"arguments\": {{$json.args}} }"
                        }
                    ]
                },
                "options": {}
            },
            "name": "Call Wikipedia MCP",
            "type": "n8n-nodes-base.httpRequest",
            "typeVersion": 1,
            "position": [1050, 700]
        },
        {
            "parameters": {
                "functionCode": """
// Format the response based on the tool call result
let result;

if ($json.html_url) {
    // GitHub Issue or PR result
    result = {
        issue_url: $json.html_url,
        issue_number: $json.number,
        status: "success",
        message: `Created: ${$json.html_url}`
    };
} else if ($json.result) {
    // Direct MCP server result
    result = $json.result;
} else {
    // Default result
    result = {
        status: "success",
        data: $json
    };
}

return {
    jsonrpc: "2.0",
    id: $json.requestId || $node["Parse MCP Request"].json.requestId,
    result
};
"""
            },
            "name": "Format Response",
            "type": "n8n-nodes-base.function",
            "typeVersion": 1,
            "position": [1250, 500]
        },
        {
            "parameters": {
                "respondWith": "json",
                "responseBody": "={{$json}}",
                "options": {}
            },
            "name": "Respond To Webhook",
            "type": "n8n-nodes-base.respondToWebhook",
            "typeVersion": 1,
            "position": [1450, 400]
        }
    ],
    "connections": {
        "MCP Webhook": {
            "main": [
                [
                    {
                        "node": "Parse MCP Request",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Parse MCP Request": {
            "main": [
                [
                    {
                        "node": "Is List Tools?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is List Tools?": {
            "main": [
                [
                    {
                        "node": "List All Tools",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Is Call Tool?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is Call Tool?": {
            "main": [
                [
                    {
                        "node": "Route Tool Call",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Respond To Webhook",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "List All Tools": {
            "main": [
                [
                    {
                        "node": "Respond To Webhook",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Route Tool Call": {
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
                        "node": "Create GitHub PR",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Call Filesystem MCP",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Call Wikipedia MCP",
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
                        "node": "Format Response",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Create GitHub PR": {
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
        "Call Filesystem MCP": {
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
        "Call Wikipedia MCP": {
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
                        "node": "Respond To Webhook",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}

# Export the workflow
def get_workflow():
    """Return the enhanced MCP server workflow definition."""
    return ENHANCED_MCP_SERVER_WORKFLOW