#!/bin/bash

# n8n-Workflow-Setup-Skript
# Dieses Skript richtet die n8n-Workflows für die MCP-Server ein.

# Farben
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Standardwerte
N8N_URL="http://n8n:5678"
N8N_API_KEY=""

# Hilfe-Funktion
function show_help {
    echo -e "${BLUE}n8n-Workflow-Setup-Skript${NC}"
    echo ""
    echo "Verwendung: $0 [Optionen]"
    echo ""
    echo "Optionen:"
    echo "  --n8n-url URL         Die URL der n8n-Instanz (Standard: http://n8n:5678)"
    echo "  --n8n-api-key KEY     Der API-Schlüssel für die n8n-Instanz (erforderlich)"
    echo "  --help                Zeigt diese Hilfe an"
    echo ""
    echo "Beispiele:"
    echo "  $0 --n8n-api-key YOUR_API_KEY                         # Richtet die n8n-Workflows ein"
    echo "  $0 --n8n-url http://localhost:5678 --n8n-api-key YOUR_API_KEY"
    echo ""
}

# Parameter verarbeiten
while [[ $# -gt 0 ]]; do
    case "$1" in
        --n8n-url)
            N8N_URL="$2"
            shift 2
            ;;
        --n8n-api-key)
            N8N_API_KEY="$2"
            shift 2
            ;;
        --help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unbekannte Option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Überprüfen, ob ein API-Schlüssel angegeben wurde
if [ -z "$N8N_API_KEY" ]; then
    echo -e "${RED}Fehler: Kein n8n-API-Schlüssel angegeben.${NC}"
    show_help
    exit 1
fi

# Verzeichnis zum Docker-Compose-Projekt wechseln
cd "$(dirname "$0")/.."

# Teste die Verbindung zur n8n-Instanz
echo -e "${BLUE}Teste Verbindung zur n8n-Instanz...${NC}"
if ! curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_URL/healthz" > /dev/null; then
    echo -e "${RED}Verbindung zur n8n-Instanz fehlgeschlagen.${NC}"
    exit 1
fi
echo -e "${GREEN}Verbindung zur n8n-Instanz erfolgreich.${NC}"

# Funktion zum Importieren eines Workflows
import_workflow() {
    local workflow_file="$1"
    local workflow_name=$(jq -r '.name' "$workflow_file")
    
    echo -e "${BLUE}Importiere Workflow $workflow_name...${NC}"
    
    # Prüfe, ob der Workflow bereits existiert
    local existing_workflow=$(curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_URL/api/v1/workflows?filter=$workflow_name" | jq -r '.data[] | select(.name == "'"$workflow_name"'") | .id')
    
    if [ -n "$existing_workflow" ]; then
        echo -e "${YELLOW}Workflow $workflow_name existiert bereits. Aktualisiere...${NC}"
        curl -s -X PUT -H "X-N8N-API-KEY: $N8N_API_KEY" -H "Content-Type: application/json" -d @"$workflow_file" "$N8N_URL/api/v1/workflows/$existing_workflow" > /dev/null
    else
        echo -e "${GREEN}Erstelle neuen Workflow $workflow_name...${NC}"
        curl -s -X POST -H "X-N8N-API-KEY: $N8N_API_KEY" -H "Content-Type: application/json" -d @"$workflow_file" "$N8N_URL/api/v1/workflows" > /dev/null
    fi
    
    echo -e "${GREEN}Workflow $workflow_name importiert.${NC}"
}

# Importiere alle Workflows
echo -e "${BLUE}Importiere alle n8n-Workflows...${NC}"

# Erstelle Verzeichnis für n8n-Workflows, falls es nicht existiert
mkdir -p n8n/workflows

# Importiere MCP-Server-Trigger-Workflow
cat > n8n/workflows/mcp-server-trigger.json << 'EOF'
{
  "name": "MCP-Server-Trigger",
  "nodes": [
    {
      "parameters": {
        "pollTimes": {
          "item": [
            {
              "mode": "everyX",
              "value": 5,
              "unit": "minutes"
            }
          ]
        },
        "url": "={{ $env.MCP_SERVERS[0].url }}/api/events",
        "authentication": "genericCredentialType",
        "genericAuthType": "httpHeaderAuth",
        "httpHeaderAuth": {
          "name": "X-API-Key",
          "value": "={{ $env.MCP_SERVERS[0].apiKey }}"
        },
        "options": {
          "response": {
            "response": {
              "fullResponse": true,
              "responseFormat": "json"
            }
          }
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [240, 300],
      "id": "mcp-events-poller"
    },
    {
      "parameters": {
        "mode": "jsonToJson",
        "jsonInput": "={{ $json.body.events }}",
        "options": {
          "dotNotation": true
        }
      },
      "type": "n8n-nodes-base.itemLists",
      "typeVersion": 1,
      "position": [460, 300],
      "id": "split-mcp-events"
    },
    {
      "parameters": {
        "mode": "jsonToJson",
        "jsonInput": "={{ $json }}",
        "options": {
          "dotNotation": true
        },
        "jsonOutput": "={\n  \"title\": $json.title || \"MCP Server Event: \" + $json.type,\n  \"description\": $json.description || $json.message || \"\",\n  \"source_type\": \"mcp_server\",\n  \"source_id\": $json.id,\n  \"server_name\": \"{{ $env.MCP_SERVERS[0].name }}\",\n  \"url\": $env.MCP_SERVERS[0].url + \"/events/\" + $json.id,\n  \"status\": $json.status || \"active\",\n  \"creator\": $json.user || \"system\",\n  \"severity\": $json.severity || \"info\",\n  \"timestamp\": $json.timestamp,\n  \"type\": $json.type,\n  \"components\": $json.components || [],\n  \"raw_data\": $json\n}"
      },
      "type": "n8n-nodes-base.itemBinary",
      "typeVersion": 1,
      "position": [660, 300],
      "id": "normalize-mcp-data"
    },
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "mcp-webhook",
        "responseMode": "lastNode",
        "options": {}
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [840, 300],
      "id": "mcp-webhook-out"
    }
  ],
  "connections": {
    "mcp-events-poller": {
      "main": [
        [
          {
            "node": "split-mcp-events",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "split-mcp-events": {
      "main": [
        [
          {
            "node": "normalize-mcp-data",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "normalize-mcp-data": {
      "main": [
        [
          {
            "node": "mcp-webhook-out",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {
    "executionOrder": "v1",
    "saveExecutionProgress": true,
    "saveManualExecutions": true
  },
  "tags": ["mcp", "trigger", "automation"]
}
EOF

# Importiere MCP-Server-Integration-Workflow
cat > n8n/workflows/mcp-server-integration.json << 'EOF'
{
  "name": "MCP-Server-Integration",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "mcp-endpoint",
        "options": {
          "responseMode": "responseNode"
        }
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300],
      "id": "mcp-endpoint-webhook"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.tool }}",
              "operation": "equal",
              "value2": "create_github_issue"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [460, 300],
      "id": "is-create-github-issue"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.tool }}",
              "operation": "equal",
              "value2": "update_work_package"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [460, 450],
      "id": "is-update-work-package"
    },
    {
      "parameters": {
        "conditions": {
          "string": [
            {
              "value1": "={{ $json.tool }}",
              "operation": "equal",
              "value2": "sync_documentation"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.if",
      "typeVersion": 1,
      "position": [460, 600],
      "id": "is-sync-documentation"
    },
    {
      "parameters": {
        "resource": "issue",
        "operation": "create",
        "owner": "={{ $json.arguments.owner }}",
        "repository": "={{ $json.arguments.repo }}",
        "title": "={{ $json.arguments.title }}",
        "body": "={{ $json.arguments.body }}",
        "additionalFields": {}
      },
      "type": "n8n-nodes-base.github",
      "typeVersion": 1,
      "position": [680, 300],
      "id": "create-github-issue"
    },
    {
      "parameters": {
        "url": "={{ $json.openProjectUrl }}/api/v3/work_packages/{{ $json.arguments.id }}",
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
              "value": "={{ $json.arguments.description || $json.existingDescription }}"
            },
            {
              "name": "status",
              "value": "={{ '/api/v3/statuses/' + ($json.arguments.status || $json.existingStatus) }}"
            }
          ]
        }
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [680, 450],
      "id": "update-work-package"
    },
    {
      "parameters": {
        "functionCode": "// Implementiert die Synchronisierung von Dokumenten zwischen AFFiNE und GitHub\nconst docId = $json.arguments.doc_id;\nconst githubPath = $json.arguments.github_path;\nconst owner = $json.arguments.owner;\nconst repo = $json.arguments.repo;\n\nconsole.log(`Syncing document ${docId} to GitHub ${owner}/${repo}/${githubPath}`);\n\n// Hier würde die tatsächliche Implementierung der Dokumentensynchronisierung erfolgen\n// In diesem Beispiel simulieren wir eine erfolgreiche Synchronisierung\nreturn {\n  json: {\n    status: \"success\",\n    doc_id: docId,\n    github_path: githubPath,\n    commit_sha: \"abc123\",\n    timestamp: new Date().toISOString()\n  }\n};"
      },
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [680, 600],
      "id": "sync-documentation"
    },
    {
      "parameters": {
        "content": "={{ $json }}",
        "options": {}
      },
      "type": "n8n-nodes-base.respondToWebhook",
      "typeVersion": 1,
      "position": [900, 450],
      "id": "mcp-response"
    },
    {
      "parameters": {
        "functionCode": "// Füge Konfiguration für OpenProject hinzu\nconst openProjectUrl = \"https://your-openproject-instance.com\";\n\nreturn {\n  ...item,\n  openProjectUrl\n};"
      },
      "type": "n8n-nodes-base.function",
      "typeVersion": 1,
      "position": [680, 380],
      "id": "add-openproject-config"
    }
  ],
  "connections": {
    "mcp-endpoint-webhook": {
      "main": [
        [
          {
            "node": "is-create-github-issue",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "is-create-github-issue": {
      "main": [
        [
          {
            "node": "create-github-issue",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "is-update-work-package",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "is-update-work-package": {
      "main": [
        [
          {
            "node": "add-openproject-config",
            "type": "main",
            "index": 0
          }
        ],
        [
          {
            "node": "is-sync-documentation",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "is-sync-documentation": {
      "main": [
        [
          {
            "node": "sync-documentation",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "create-github-issue": {
      "main": [
        [
          {
            "node": "mcp-response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "add-openproject-config": {
      "main": [
        [
          {
            "node": "update-work-package",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "update-work-package": {
      "main": [
        [
          {
            "node": "mcp-response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "sync-documentation": {
      "main": [
        [
          {
            "node": "mcp-response",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {
    "executionOrder": "v1",
    "saveExecutionProgress": true,
    "saveManualExecutions": true
  },
  "tags": ["mcp", "integration", "automation"]
}
EOF

# Importiere Brave-Search-Workflow
cat > n8n/workflows/brave-search-integration.json << 'EOF'
{
  "name": "Brave Search Integration",
  "nodes": [
    {
      "parameters": {
        "httpMethod": "POST",
        "path": "brave-search",
        "options": {}
      },
      "type": "n8n-nodes-base.webhook",
      "typeVersion": 1,
      "position": [240, 300],
      "id": "brave-search-webhook"
    },
    {
      "parameters": {
        "url": "http://brave-search-mcp:3001/mcp",
        "method": "POST",
        "jsonParameters": true,
        "bodyParametersJson": "={\n  \"jsonrpc\": \"2.0\",\n  \"id\": 1,\n  \"method\": \"mcp.callTool\",\n  \"params\": {\n    \"name\": \"search\",\n    \"arguments\": {\n      \"query\": $json.query,\n      \"count\": $json.count || 10\n    }\n  }\n}"
      },
      "type": "n8n-nodes-base.httpRequest",
      "typeVersion": 1,
      "position": [460, 300],
      "id": "brave-search-request"
    },
    {
      "parameters": {
        "mode": "jsonToJson",
        "jsonInput": "={{ $json.result }}",
        "options": {}
      },
      "type": "n8n-nodes-base.itemLists",
      "typeVersion": 1,
      "position": [680, 300],
      "id": "process-search-results"
    }
  ],
  "connections": {
    "brave-search-webhook": {
      "main": [
        [
          {
            "node": "brave-search-request",
            "type": "main",
            "index": 0
          }
        ]
      ]
    },
    "brave-search-request": {
      "main": [
        [
          {
            "node": "process-search-results",
            "type": "main",
            "index": 0
          }
        ]
      ]
    }
  },
  "active": true,
  "settings": {
    "executionOrder": "v1",
    "saveExecutionProgress": true,
    "saveManualExecutions": true
  },
  "tags": ["mcp", "brave", "search", "automation"]
}
EOF

# Importiere alle Workflows
import_workflow "n8n/workflows/mcp-server-trigger.json"
import_workflow "n8n/workflows/mcp-server-integration.json"
import_workflow "n8n/workflows/brave-search-integration.json"

echo -e "${GREEN}Alle n8n-Workflows wurden importiert.${NC}"