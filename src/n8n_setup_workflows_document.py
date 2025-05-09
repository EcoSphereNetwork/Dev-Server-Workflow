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
n8n Setup - Document Workflow Definition

Dieses Modul enthält die Definition des Dokumenten-Synchronisierungs-Workflows.
"""

# Document Sync Workflow
DOCUMENT_SYNC_WORKFLOW = {
    "name": "Document Sync Workflow",
    "nodes": [
        {
            "parameters": {
                "path": "/webhook",
                "options": {}
            },
            "name": "Webhook",
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
                            "value2": "document_updated"
                        }
                    ]
                }
            },
            "name": "Is Document Update?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                300
            ]
        },
        {
            "parameters": {
                "url": "={{$json.documentApiUrl}}",
                "method": "GET",
                "authentication": "genericCredentialType",
                "options": {}
            },
            "name": "Fetch Document Content",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                650,
                200
            ]
        },
        {
            "parameters": {
                "functionCode": "// Process document content for synchronization\nconst documentContent = $node[\"Fetch Document Content\"].json;\n\n// Extract metadata\nconst metadata = {\n  title: documentContent.title || 'Untitled Document',\n  lastUpdated: documentContent.updatedAt || new Date().toISOString(),\n  author: documentContent.author || 'Unknown',\n  tags: documentContent.tags || []\n};\n\n// Format document for different destinations\nconst formattedContent = {\n  markdown: documentContent.content || '',\n  // Extract plain text if needed\n  plainText: documentContent.content ? documentContent.content.replace(/\\#|\\*|\\`|\\[|\\]|\\(|\\)|\\>/g, '') : '',\n  // Format as HTML if needed\n  html: documentContent.content ? convertMarkdownToHtml(documentContent.content) : '',\n};\n\n// Helper function for Markdown to HTML conversion (simplified)\nfunction convertMarkdownToHtml(markdown) {\n  // This is a very simplified conversion\n  let html = markdown;\n  // Headers\n  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');\n  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');\n  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');\n  // Bold and Italic\n  html = html.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');\n  html = html.replace(/\\*(.+?)\\*/g, '<em>$1</em>');\n  // Line breaks\n  html = html.replace(/\\n/g, '<br />');\n  return html;\n}\n\n// Return the processed document\nreturn {\n  ...item,\n  processedDocument: {\n    metadata,\n    content: formattedContent\n  }\n};"
            },
            "name": "Process Document",
            "type": "n8n-nodes-base.function",
            "position": [
                850,
                200
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.syncTarget}}",
                            "operation": "equal",
                            "value2": "github"
                        }
                    ]
                }
            },
            "name": "Sync to GitHub?",
            "type": "n8n-nodes-base.if",
            "position": [
                1050,
                200
            ]
        },
        {
            "parameters": {
                "owner": "={{$json.githubOwner}}",
                "repository": "={{$json.githubRepo}}",
                "filePath": "={{$json.githubPath}}",
                "content": "={{$json.processedDocument.content.markdown}}",
                "commitMessage": "Update documentation from AFFiNE/AppFlowy",
                "options": {}
            },
            "name": "Update GitHub Documentation",
            "type": "n8n-nodes-base.github",
            "position": [
                1250,
                100
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "string": [
                        {
                            "value1": "={{$json.syncTarget}}",
                            "operation": "equal",
                            "value2": "openproject"
                        }
                    ]
                }
            },
            "name": "Sync to OpenProject?",
            "type": "n8n-nodes-base.if",
            "position": [
                1050,
                350
            ]
        },
        {
            "parameters": {
                "url": "={{$json.openProjectUrl}}/api/v3/work_packages/{{$json.workPackageId}}",
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
                            "name": "description.raw",
                            "value": "={{$json.processedDocument.content.markdown}}"
                        }
                    ]
                }
            },
            "name": "Update OpenProject Work Package",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1250,
                350
            ]
        }
    ],
    "connections": {
        "Webhook": {
            "main": [
                [
                    {
                        "node": "Is Document Update?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is Document Update?": {
            "main": [
                [
                    {
                        "node": "Fetch Document Content",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Fetch Document Content": {
            "main": [
                [
                    {
                        "node": "Process Document",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Process Document": {
            "main": [
                [
                    {
                        "node": "Sync to GitHub?",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Sync to OpenProject?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Sync to GitHub?": {
            "main": [
                [
                    {
                        "node": "Update GitHub Documentation",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Sync to OpenProject?": {
            "main": [
                [
                    {
                        "node": "Update OpenProject Work Package",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}

# Erweiterte Dokumentensynchronisierung Workflow
DOCUMENT_SYNC_ENHANCED_WORKFLOW = {
    "name": "Erweiterte Dokumentensynchronisierung",
    "nodes": [
        {
            "parameters": {
                "path": "/document/webhook",
                "options": {}
            },
            "name": "Document Webhook",
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
                            "value1": "={{$json.source}}",
                            "operation": "equal",
                            "value2": "affine"
                        }
                    ]
                }
            },
            "name": "Is AFFiNE Source?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                300
            ]
        },
        {
            "parameters": {
                "url": "={{$json.documentApiUrl}}",
                "method": "GET",
                "authentication": "genericCredentialType",
                "options": {}
            },
            "name": "Fetch AFFiNE Document",
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
                            "value1": "={{$json.source}}",
                            "operation": "equal",
                            "value2": "appflowy"
                        }
                    ]
                }
            },
            "name": "Is AppFlowy Source?",
            "type": "n8n-nodes-base.if",
            "position": [
                450,
                450
            ]
        },
        {
            "parameters": {
                "url": "={{$json.documentApiUrl}}",
                "method": "GET",
                "authentication": "genericCredentialType",
                "options": {}
            },
            "name": "Fetch AppFlowy Document",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                650,
                450
            ]
        },
        {
            "parameters": {
                "functionCode": "// Verarbeite Dokument nach Quelle\nlet documentContent = {};\nlet contentType = \"\";\n\n// Bestimme die Quelle und extrahiere Inhalt\nif ($node[\"Is AFFiNE Source?\"].json) {\n  documentContent = $node[\"Fetch AFFiNE Document\"].json;\n  contentType = \"affine\";\n} else if ($node[\"Is AppFlowy Source?\"].json) {\n  documentContent = $node[\"Fetch AppFlowy Document\"].json;\n  contentType = \"appflowy\";\n} else {\n  // Unbekannte Quelle\n  return null;\n}\n\n// Extrahiere Metadaten\nconst metadata = {\n  title: documentContent.title || 'Untitled Document',\n  lastUpdated: documentContent.updatedAt || new Date().toISOString(),\n  author: documentContent.author || 'Unknown',\n  tags: documentContent.tags || [],\n  source: contentType,\n  documentId: documentContent.id || $json.documentId,\n  checksum: documentContent.checksum || null\n};\n\n// Format document for different destinations\nconst formattedContent = {\n  markdown: documentContent.content || '',\n  // Extrahiere Plaintext falls nötig\n  plainText: documentContent.content ? documentContent.content.replace(/\\#|\\*|\\`|\\[|\\]|\\(|\\)|\\>/g, '') : '',\n  // Formatiere als HTML falls nötig\n  html: documentContent.content ? convertMarkdownToHtml(documentContent.content) : '',\n};\n\n// Hilfsfunktion für Markdown zu HTML Konvertierung (vereinfacht)\nfunction convertMarkdownToHtml(markdown) {\n  // Dies ist eine sehr vereinfachte Konvertierung\n  let html = markdown;\n  // Headers\n  html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');\n  html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');\n  html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');\n  // Bold and Italic\n  html = html.replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>');\n  html = html.replace(/\\*(.+?)\\*/g, '<em>$1</em>');\n  // Line breaks\n  html = html.replace(/\\n/g, '<br />');\n  return html;\n}\n\n// Berechne eine Prüfsumme für Konfliktdetektion\nconst calculateChecksum = (str) => {\n  let hash = 0;\n  if (str.length === 0) return hash;\n  for (let i = 0; i < str.length; i++) {\n    const char = str.charCodeAt(i);\n    hash = ((hash << 5) - hash) + char;\n    hash = hash & hash;\n  }\n  return hash.toString();\n};\n\n// Aktualisiere die Prüfsumme\nmetadata.checksum = calculateChecksum(formattedContent.markdown);\n\n// Return the processed document\nreturn {\n  ...item,\n  processedDocument: {\n    metadata,\n    content: formattedContent\n  }\n};"
            },
            "name": "Process Document",
            "type": "n8n-nodes-base.function",
            "position": [
                850,
                300
            ]
        },
        {
            "parameters": {
                "url": "https://api.github.com/repos/{{$json.githubOwner}}/{{$json.githubRepo}}/contents/{{$json.githubPath}}",
                "method": "GET",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth",
                "options": {}
            },
            "name": "Get GitHub Document",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1050,
                150
            ]
        },
        {
            "parameters": {
                "functionCode": "// Check if document has changed\nconst githubDoc = $node[\"Get GitHub Document\"].json;\nconst processedDoc = $node[\"Process Document\"].json.processedDocument;\n\n// Decode base64 content from GitHub\nconst githubContent = githubDoc.content ? Buffer.from(githubDoc.content, 'base64').toString() : '';\n\n// Calculate checksum for GitHub content\nconst calculateChecksum = (str) => {\n  let hash = 0;\n  if (str.length === 0) return hash;\n  for (let i = 0; i < str.length; i++) {\n    const char = str.charCodeAt(i);\n    hash = ((hash << 5) - hash) + char;\n    hash = hash & hash;\n  }\n  return hash.toString();\n};\n\nconst githubChecksum = calculateChecksum(githubContent);\nconst docChecksum = processedDoc.metadata.checksum;\n\n// Detect conflicts (if both documents were updated)\nconst conflict = githubChecksum !== docChecksum && \n                githubContent !== processedDoc.content.markdown;\n\n// Resolve strategy: newest wins\nlet contentToUse = processedDoc.content.markdown;\nlet updateGitHub = true;\n\n// If there's a conflict, compare last update times\nif (conflict) {\n  const githubUpdated = new Date(githubDoc.updated_at || 0);\n  const docUpdated = new Date(processedDoc.metadata.lastUpdated || 0);\n  \n  // If GitHub is newer, don't update it\n  if (githubUpdated > docUpdated) {\n    updateGitHub = false;\n  }\n}\n\nreturn {\n  ...item,\n  githubSha: githubDoc.sha,\n  githubContent,\n  githubChecksum,\n  docChecksum,\n  conflict,\n  updateGitHub,\n  contentToUse\n};"
            },
            "name": "Check Document Changes",
            "type": "n8n-nodes-base.function",
            "position": [
                1250,
                150
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{$json.updateGitHub}}",
                            "value2": true
                        }
                    ]
                }
            },
            "name": "Should Update GitHub?",
            "type": "n8n-nodes-base.if",
            "position": [
                1450,
                150
            ]
        },
        {
            "parameters": {
                "resource": "file",
                "operation": "edit",
                "owner": "={{$json.githubOwner}}",
                "repository": "={{$json.githubRepo}}",
                "filePath": "={{$json.githubPath}}",
                "fileContent": "={{$json.contentToUse}}",
                "commitMessage": "={{$json.conflict ? \"Merge: Resolve document conflict\" : \"Update documentation from \" + $json.processedDocument.metadata.source}}",
                "additionalParameters": {
                    "sha": "={{$json.githubSha}}"
                }
            },
            "name": "Update GitHub File",
            "type": "n8n-nodes-base.github",
            "position": [
                1650,
                100
            ]
        },
        {
            "parameters": {
                "url": "={{$json.openProjectUrl}}/api/v3/work_packages/{{$json.workPackageId}}",
                "method": "GET",
                "authentication": "genericCredentialType",
                "genericAuthType": "httpHeaderAuth"
            },
            "name": "Get OpenProject Work Package",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1050,
                450
            ]
        },
        {
            "parameters": {
                "functionCode": "// Check if document has changed\nconst workPackage = $node[\"Get OpenProject Work Package\"].json;\nconst processedDoc = $node[\"Process Document\"].json.processedDocument;\n\n// Extract description from work package\nconst description = workPackage.description?.raw || '';\n\n// Calculate checksum for work package description\nconst calculateChecksum = (str) => {\n  let hash = 0;\n  if (str.length === 0) return hash;\n  for (let i = 0; i < str.length; i++) {\n    const char = str.charCodeAt(i);\n    hash = ((hash << 5) - hash) + char;\n    hash = hash & hash;\n  }\n  return hash.toString();\n};\n\nconst opChecksum = calculateChecksum(description);\nconst docChecksum = processedDoc.metadata.checksum;\n\n// Detect conflicts (if both documents were updated)\nconst conflict = opChecksum !== docChecksum && \n                description !== processedDoc.content.markdown;\n\n// Resolve strategy: newest wins\nlet contentToUse = processedDoc.content.markdown;\nlet updateOpenProject = true;\n\n// If there's a conflict, compare last update times\nif (conflict) {\n  const opUpdated = new Date(workPackage.updatedAt || 0);\n  const docUpdated = new Date(processedDoc.metadata.lastUpdated || 0);\n  \n  // If OpenProject is newer, don't update it\n  if (opUpdated > docUpdated) {\n    updateOpenProject = false;\n  }\n}\n\nreturn {\n  ...item,\n  workPackageContent: description,\n  opChecksum,\n  docChecksum,\n  conflict,\n  updateOpenProject,\n  contentToUse\n};"
            },
            "name": "Check Work Package Changes",
            "type": "n8n-nodes-base.function",
            "position": [
                1250,
                450
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{$json.updateOpenProject}}",
                            "value2": true
                        }
                    ]
                }
            },
            "name": "Should Update OpenProject?",
            "type": "n8n-nodes-base.if",
            "position": [
                1450,
                450
            ]
        },
        {
            "parameters": {
                "url": "={{$json.openProjectUrl}}/api/v3/work_packages/{{$json.workPackageId}}",
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
                            "name": "description.raw",
                            "value": "={{$json.contentToUse}}"
                        },
                        {
                            "name": "statusComment.raw",
                            "value": "={{$json.conflict ? \"Aktualisierte Dokumentation (Konflikt aufgelöst)\" : \"Aktualisierte Dokumentation von \" + $json.processedDocument.metadata.source}}"
                        }
                    ]
                }
            },
            "name": "Update Work Package",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1650,
                400
            ]
        },
        {
            "parameters": {
                "functionCode": "// Log conflicts for reporting\nconst hasConflict = $json.conflict;\nconst source = $json.processedDocument.metadata.source;\nconst docId = $json.processedDocument.metadata.documentId;\nconst title = $json.processedDocument.metadata.title;\n\nif (hasConflict) {\n  // Log conflict details\n  console.log(`Document conflict detected: ${title} (${docId}) from ${source}`);\n  console.log(`GitHub updated: ${$json.updateGitHub}, OpenProject updated: ${$json.updateOpenProject}`);\n  \n  // Prepare conflict notification\n  return {\n    ...item,\n    conflictNotification: {\n      title: `Document Conflict: ${title}`,\n      source: source,\n      documentId: docId,\n      time: new Date().toISOString(),\n      resolution: $json.updateGitHub ? 'Document version applied to GitHub' : 'GitHub version kept',\n      openProjectUpdate: $json.updateOpenProject ? 'Document version applied to OpenProject' : 'OpenProject version kept'\n    }\n  };\n} else {\n  // No conflict\n  return {\n    ...item,\n    conflictNotification: null\n  };\n}"
            },
            "name": "Handle Conflicts",
            "type": "n8n-nodes-base.function",
            "position": [
                1650,
                250
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{$json.conflictNotification !== null}}",
                            "value2": true
                        }
                    ]
                }
            },
            "name": "Has Conflict?",
            "type": "n8n-nodes-base.if",
            "position": [
                1850,
                250
            ]
        },
        {
            "parameters": {
                "content": "=Document synchronization conflict detected!\n\nTitle: {{$json.conflictNotification.title}}\nSource: {{$json.conflictNotification.source}}\nTime: {{$json.conflictNotification.time}}\n\nResolution:\n- GitHub: {{$json.conflictNotification.resolution}}\n- OpenProject: {{$json.conflictNotification.openProjectUpdate}}",
                "options": {}
            },
            "name": "Send Conflict Notification",
            "type": "n8n-nodes-base.slack",
            "position": [
                2050,
                250
            ]
        }
    ],
    "connections": {
        "Document Webhook": {
            "main": [
                [
                    {
                        "node": "Is AFFiNE Source?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is AFFiNE Source?": {
            "main": [
                [
                    {
                        "node": "Fetch AFFiNE Document",
                        "type": "main",
                        "index": 0
                    }
                ],
                [
                    {
                        "node": "Is AppFlowy Source?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Fetch AFFiNE Document": {
            "main": [
                [
                    {
                        "node": "Process Document",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Is AppFlowy Source?": {
            "main": [
                [
                    {
                        "node": "Fetch AppFlowy Document",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Fetch AppFlowy Document": {
            "main": [
                [
                    {
                        "node": "Process Document",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Process Document": {
            "main": [
                [
                    {
                        "node": "Get GitHub Document",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Get OpenProject Work Package",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Get GitHub Document": {
            "main": [
                [
                    {
                        "node": "Check Document Changes",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Check Document Changes": {
            "main": [
                [
                    {
                        "node": "Should Update GitHub?",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Handle Conflicts",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Should Update GitHub?": {
            "main": [
                [
                    {
                        "node": "Update GitHub File",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Get OpenProject Work Package": {
            "main": [
                [
                    {
                        "node": "Check Work Package Changes",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Check Work Package Changes": {
            "main": [
                [
                    {
                        "node": "Should Update OpenProject?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Should Update OpenProject?": {
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
        "Handle Conflicts": {
            "main": [
                [
                    {
                        "node": "Has Conflict?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Has Conflict?": {
            "main": [
                [
                    {
                        "node": "Send Conflict Notification",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}
