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
n8n Setup - GitHub Workflow Definition

Dieses Modul enthält die Definition des GitHub-OpenProject Integrations-Workflows.
"""

# GitHub-OpenProject Integration Workflow
GITHUB_OPENPROJECT_WORKFLOW = {
    "name": "GitHub to OpenProject Integration",
    "nodes": [
        {
            "parameters": {
                "events": [
                    "issues:opened",
                    "pull_request:opened",
                    "push"
                ],
                "repository": "={{$json.repository}}",
                "owner": "={{$json.owner}}",
                "authentication": "accessToken"
            },
            "name": "GitHub Trigger",
            "type": "n8n-nodes-base.githubTrigger",
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
                            "value1": "={{$json.event}}",
                            "operation": "equal",
                            "value2": "issues"
                        }
                    ]
                }
            },
            "name": "Is Issue Event?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                300
            ]
        },
        {
            "parameters": {
                "url": "={{$json.host}}/api/v3/work_packages",
                "method": "POST",
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
                            "name": "subject",
                            "value": "={{$json.issue.title}}"
                        },
                        {
                            "name": "description.raw",
                            "value": "={{$json.issue.body}}\n\nGitHub Issue: {{$json.issue.html_url}}"
                        },
                        {
                            "name": "project",
                            "value": "={{ $json.linkData.project }}"
                        },
                        {
                            "name": "status",
                            "value": "={{ $json.linkData.status }}"
                        }
                    ]
                }
            },
            "name": "Create OpenProject Work Package",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                650,
                200
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.event}}",
                            "operation": "equal",
                            "value2": "pull_request"
                        }
                    ]
                }
            },
            "name": "Is PR Event?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                450
            ]
        },
        {
            "parameters": {
                "url": "={{ $json.host }}/api/v3/work_packages.json?filters=[{\"subject\":{\"operator\":\"~\",\"values\":[\"{{ $json.pull_request.title }}\"]}},{\"status_id\":{\"operator\":\"o\",\"values\":null}}]",
                "method": "GET",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth"
            },
            "name": "Find Related Work Package",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                650,
                450
            ]
        },
        {
            "parameters": {
                "url": "={{ $json.host }}/api/v3/work_packages/{{ $json.work_package_id }}",
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
                            "name": "statusComment",
                            "value": "GitHub Pull Request opened: {{ $json.pull_request.html_url }}"
                        },
                        {
                            "name": "status",
                            "value": "={{ $json.linkData.prStatus }}"
                        }
                    ]
                }
            },
            "name": "Update Work Package Status",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                850,
                450
            ]
        },
        {
            "parameters": {
                "functionCode": "// Define mapping between repositories and OpenProject projects\nconst repositoryMapping = {\n  'owner/repo-1': {\n    projectId: '1',\n    projectName: 'Project 1',\n    newIssueStatus: '1', // ID of status for new issues\n    inProgressStatus: '7', // ID of status for in progress\n    prStatus: '2', // ID for PR opened\n    resolvedStatus: '12', // ID for resolved\n    host: 'https://myopenproject.com'\n  },\n  // Add more repo mappings as needed\n};\n\n// Get the repository from the webhook payload\nconst repoFullName = `${$node[\"GitHub Trigger\"].json[\"repository_owner\"]}/${$node[\"GitHub Trigger\"].json[\"repository\"]}`;\n\n// Find the mapping for this repository or use a default\nconst mapping = repositoryMapping[repoFullName] || {\n  projectId: '1',\n  projectName: 'Default Project',\n  newIssueStatus: '1',\n  inProgressStatus: '7',\n  prStatus: '2',\n  resolvedStatus: '12',\n  host: 'https://myopenproject.com'\n};\n\n// Create a project link in the correct format for OpenProject API\nconst projectLink = {\n  \"_links\": {\n    \"project\": {\n      \"href\": `/api/v3/projects/${mapping.projectId}`\n    },\n    \"status\": {\n      \"href\": `/api/v3/statuses/${mapping.newIssueStatus}`\n    }\n  }\n};\n\n// Prepare the data for OpenProject\nconst result = {\n  ...item,\n  linkData: {\n    project: projectLink._links.project,\n    status: projectLink._links.status,\n    prStatus: `/api/v3/statuses/${mapping.prStatus}`,\n    inProgressStatus: `/api/v3/statuses/${mapping.inProgressStatus}`,\n    resolvedStatus: `/api/v3/statuses/${mapping.resolvedStatus}`,\n  },\n  host: mapping.host\n};\n\nreturn result;"
            },
            "name": "Map Repository to OpenProject",
            "type": "n8n-nodes-base.function",
            "position": [
                450,
                150
            ]
        },
        {
            "parameters": {
                "content": "=The GitHub issue {{$node[\"GitHub Trigger\"].json.issue.number}} has been created in OpenProject as work package {{$node[\"Create OpenProject Work Package\"].json.id}}.",
                "options": {}
            },
            "name": "Issue Created Notification",
            "type": "n8n-nodes-base.slack",
            "position": [
                850,
                200
            ]
        },
        {
            "parameters": {
                "functionCode": "// Extract Work Package ID from the search results\nlet workPackageId = null;\nif ($node[\"Find Related Work Package\"].json._embedded && \n    $node[\"Find Related Work Package\"].json._embedded.elements && \n    $node[\"Find Related Work Package\"].json._embedded.elements.length > 0) {\n  workPackageId = $node[\"Find Related Work Package\"].json._embedded.elements[0].id;\n}\n\nconst result = {\n  ...item,\n  work_package_id: workPackageId\n};\n\nreturn result;"
            },
            "name": "Extract Work Package ID",
            "type": "n8n-nodes-base.function",
            "position": [
                750,
                450
            ]
        },
        {
            "parameters": {
                "url": "https://api.github.com/repos/{{$json.repository_owner}}/{{$json.repository}}/issues/{{$json.issue.number}}/labels",
                "method": "POST",
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
                            "name": "labels",
                            "value": "[\"fix-me\"]"
                        }
                    ]
                }
            },
            "name": "Trigger OpenHands",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                850,
                300
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{$json.work_package_id !== null}}",
                            "value2": true
                        }
                    ]
                }
            },
            "name": "Work Package Found?",
            "type": "n8n-nodes-base.if",
            "position": [
                750,
                550
            ]
        },
        {
            "parameters": {
                "content": "=A GitHub Pull Request {{$node[\"GitHub Trigger\"].json.pull_request.number}} has been linked to OpenProject work package {{$node[\"Extract Work Package ID\"].json.work_package_id}}.",
                "options": {}
            },
            "name": "PR Linked Notification",
            "type": "n8n-nodes-base.slack",
            "position": [
                950,
                450
            ]
        }
    ],
    "connections": {
        "GitHub Trigger": {
            "main": [
                [
                    {
                        "node": "Is Issue Event?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is Issue Event?": {
            "main": [
                [
                    {
                        "node": "Map Repository to OpenProject",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Is PR Event?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Map Repository to OpenProject": {
            "main": [
                [
                    {
                        "node": "Create OpenProject Work Package",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Create OpenProject Work Package": {
            "main": [
                [
                    {
                        "node": "Issue Created Notification",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Trigger OpenHands",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is PR Event?": {
            "main": [
                [
                    {
                        "node": "Find Related Work Package",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Find Related Work Package": {
            "main": [
                [
                    {
                        "node": "Extract Work Package ID",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Extract Work Package ID": {
            "main": [
                [
                    {
                        "node": "Work Package Found?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Work Package Found?": {
            "main": [
                [
                    {
                        "node": "Update Work Package Status",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Update Work Package Status": {
            "main": [
                [
                    {
                        "node": "PR Linked Notification",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}
