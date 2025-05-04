#!/usr/bin/env python3
"""
n8n Setup - OpenHands Workflow Definition

Dieses Modul enthält die Definition des OpenHands-Integrations-Workflows.
"""

# OpenHands Integration Workflow
OPENHANDS_WORKFLOW = {
    "name": "OpenHands Integration Workflow",
    "nodes": [
        {
            "parameters": {
                "path": "/openhands/webhook",
                "options": {}
            },
            "name": "OpenHands Webhook",
            "type": "n8n-nodes-base.webhook",
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
                            "value2": "pr_created"
                        }
                    ]
                }
            },
            "name": "Is PR Created?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                300
            ]
        },
        {
            "parameters": {
                "url": "={{$json.openProjectUrl}}/api/v3/work_packages.json?filters=[{\"description\":{\"operator\":\"~\",\"values\":[\"{{$json.issueNumber}}\"]}},{\"status_id\":{\"operator\":\"o\",\"values\":null}}]",
                "method": "GET",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth"
            },
            "name": "Find Related Work Package",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                650,
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
                850,
                200
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
                1050,
                200
            ]
        },
        {
            "parameters": {
                "url": "={{$json.openProjectUrl}}/api/v3/work_packages/{{$json.work_package_id}}",
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
                            "value": "OpenHands has created a Pull Request: {{$json.prUrl}}"
                        },
                        {
                            "name": "status",
                            "value": "={{$json.statusMapping.prCreated}}"
                        }
                    ]
                }
            },
            "name": "Update Work Package",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1250,
                100
            ]
        },
        {
            "parameters": {
                "url": "={{$json.affineApiUrl}}",
                "method": "POST",
                "authentication": "genericCredentialType",
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
                            "name": "title",
                            "value": "PR Review: {{$json.prTitle}}"
                        },
                        {
                            "name": "content",
                            "value": "# Pull Request Review\n\n**Issue:** {{$json.issueNumber}}\n\n**PR:** {{$json.prUrl}}\n\n**Created by OpenHands**\n\n## Changes\n\n{{$json.prDescription}}\n\n## Files Changed\n\n{{$json.filesChanged}}"
                        }
                    ]
                }
            },
            "name": "Create AFFiNE Document",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1250,
                300
            ]
        },
        {
            "parameters": {
                "url": "{{$json.discordWebhookUrl}}",
                "options": {
                    "additionalHeaders": {
                        "values": {
                            "Content-Type": "application/json"
                        }
                    }
                },
                "jsonParameters": true,
                "method": "POST",
                "bodyParametersJson": "{\n  \"embeds\": [\n    {\n      \"title\": \"OpenHands hat einen Pull Request erstellt\",\n      \"description\": \"OpenHands hat automatisch einen Pull Request erstellt, um das Issue #{{$json.issueNumber}} zu lösen.\",\n      \"color\": 5793266,\n      \"fields\": [\n        {\n          \"name\": \"Issue\",\n          \"value\": \"#{{$json.issueNumber}} - {{$json.issueTitle}}\",\n          \"inline\": false\n        },\n        {\n          \"name\": \"Pull Request\",\n          \"value\": \"[{{$json.prTitle}}]({{$json.prUrl}})\",\n          \"inline\": false\n        },\n        {\n          \"name\": \"Repository\",\n          \"value\": \"{{$json.repository}}\",\n          \"inline\": true\n        },\n        {\n          \"name\": \"Branch\",\n          \"value\": \"{{$json.branch}}\",\n          \"inline\": true\n        }\n      ],\n      \"timestamp\": \"{{$now}}\"\n    }\n  ]\n}"
            },
            "name": "Send Discord Notification",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1250,
                500
            ]
        },
        {
            "parameters": {
                "functionCode": "// Add status mapping for OpenProject\nconst statusMapping = {\n  prCreated: \"/api/v3/statuses/2\", // 2 = In Progress (default, can be overridden)\n  prMerged: \"/api/v3/statuses/12\", // 12 = Resolved (default, can be overridden)\n  prClosed: \"/api/v3/statuses/5\" // 5 = Closed (default, can be overridden)\n};\n\n// Add integration URLs\nconst integrationUrls = {\n  openProjectUrl: \"https://your-openproject-instance.com\", // Will be overridden by env vars\n  affineApiUrl: \"https://your-affine-instance.com/api/documents\", // Will be overridden by env vars\n  discordWebhookUrl: \"https://discord.com/api/webhooks/your-webhook-url\" // Will be overridden by env vars\n};\n\n// Merge with incoming data\nreturn {\n  ...item,\n  statusMapping,\n  ...integrationUrls,\n  // Generate timestamp for Discord message\n  now: new Date().toISOString()\n};"
            },
            "name": "Add Integration Context",
            "type": "n8n-nodes-base.function",
            "position": [
                850,
                400
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.event}}",
                            "operation": "equal",
                            "value2": "pr_merged"
                        }
                    ]
                }
            },
            "name": "Is PR Merged?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                450
            ]
        },
        {
            "parameters": {
                "url": "={{$json.openProjectUrl}}/api/v3/work_packages/{{$json.work_package_id}}",
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
                            "value": "OpenHands PR merged: {{$json.prUrl}}"
                        },
                        {
                            "name": "status",
                            "value": "={{$json.statusMapping.prMerged}}"
                        }
                    ]
                }
            },
            "name": "Update Work Package (Merged)",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1050,
                550
            ]
        }
    ],
    "connections": {
        "OpenHands Webhook": {
            "main": [
                [
                    {
                        "node": "Is PR Created?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is PR Created?": {
            "main": [
                [
                    {
                        "node": "Find Related Work Package",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Is PR Merged?",
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
                    },
                    {
                        "node": "Add Integration Context",
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
                        "node": "Update Work Package",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Create AFFiNE Document",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Send Discord Notification",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is PR Merged?": {
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
        "Add Integration Context": {
            "main": [
                [
                    {
                        "node": "Work Package Found?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}
