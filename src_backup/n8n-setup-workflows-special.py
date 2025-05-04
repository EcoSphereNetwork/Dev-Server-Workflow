#!/usr/bin/env python3
"""
n8n Setup - Spezial-Workflows Definitionen

Dieses Modul enthält die Definitionen für erweiterte Workflows:
- Discord-Benachrichtigungen
- Zeit-Tracking
- KI-gestützte Zusammenfassungen
"""

# Discord Notification Workflow
DISCORD_NOTIFICATION_WORKFLOW = {
    "name": "Discord Benachrichtigungen",
    "nodes": [
        {
            "parameters": {
                "events": [
                    "issues:opened",
                    "issues:closed",
                    "pull_request:opened",
                    "pull_request:closed",
                    "pull_request:merged"
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
                "functionCode": "// Bestimme den Event-Typ und formatiere die Nachricht entsprechend\nconst event = $node[\"GitHub Trigger\"].json.event;\nconst repo = $node[\"GitHub Trigger\"].json.repository;\nconst repoOwner = $node[\"GitHub Trigger\"].json.repository_owner;\nconst repoFullName = `${repoOwner}/${repo}`;\n\nlet message = \"\";\nlet title = \"\";\nlet color = 0;\nlet url = \"\";\nlet description = \"\";\nlet mentions = \"\";\n\n// Zuweisung von Rollen zu Benutzern für Benachrichtigungen\nconst roleMapping = {\n  \"project-manager\": \"<@&123456789>\",\n  \"developer\": \"<@&234567890>\",\n  \"reviewer\": \"<@&345678901>\"\n};\n\n// Bestimme die zu benachrichtigenden Rollen basierend auf dem Event\nswitch(event) {\n  case \"issues:opened\":\n    const issue = $node[\"GitHub Trigger\"].json.issue;\n    title = `🔴 Neues Issue: ${issue.title}`;\n    color = 15548997; // Rot\n    url = issue.html_url;\n    description = `**Beschreibung:** ${issue.body.substring(0, 200)}${issue.body.length > 200 ? '...' : ''}`;\n    mentions = roleMapping[\"project-manager\"];\n    break;\n    \n  case \"issues:closed\":\n    const closedIssue = $node[\"GitHub Trigger\"].json.issue;\n    title = `🟢 Issue geschlossen: ${closedIssue.title}`;\n    color = 5763719; // Grün\n    url = closedIssue.html_url;\n    description = `**Schließer:** ${$node[\"GitHub Trigger\"].json.sender.login}`;\n    break;\n    \n  case \"pull_request:opened\":\n    const pr = $node[\"GitHub Trigger\"].json.pull_request;\n    title = `🟣 Neuer Pull Request: ${pr.title}`;\n    color = 10181046; // Lila\n    url = pr.html_url;\n    description = `**Beschreibung:** ${pr.body.substring(0, 200)}${pr.body.length > 200 ? '...' : ''}`;\n    mentions = roleMapping[\"reviewer\"];\n    break;\n    \n  case \"pull_request:merged\":\n    const mergedPr = $node[\"GitHub Trigger\"].json.pull_request;\n    title = `🔵 Pull Request gemerged: ${mergedPr.title}`;\n    color = 3447003; // Blau\n    url = mergedPr.html_url;\n    description = `**Merged von:** ${$node[\"GitHub Trigger\"].json.sender.login}`;\n    break;\n}\n\n// Erstelle Discord Embed\nconst embed = {\n  title: title,\n  url: url,\n  color: color,\n  description: description,\n  fields: [\n    {\n      name: \"Repository\",\n      value: repoFullName\n    }\n  ],\n  timestamp: new Date().toISOString()\n};\n\nreturn {\n  json: {\n    embeds: [embed],\n    content: mentions ? `${mentions} Neue Benachrichtigung!` : \"Neue Benachrichtigung!\"\n  }\n};"
            },
            "name": "Format Discord Message",
            "type": "n8n-nodes-base.function",
            "position": [
                450,
                300
            ]
        },
        {
            "parameters": {
                "url": "={{$json.discordWebhookUrl}}",
                "jsonParameters": true,
                "options": {
                    "response": {
                        "fullResponse": false
                    }
                },
                "bodyContentType": "json",
                "bodyParametersJson": "={{ JSON.stringify($node[\"Format Discord Message\"].json) }}"
            },
            "name": "Send to Discord",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                650,
                300
            ]
        }
    ],
    "connections": {
        "GitHub Trigger": {
            "main": [
                [
                    {
                        "node": "Format Discord Message",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Format Discord Message": {
            "main": [
                [
                    {
                        "node": "Send to Discord",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}

# Zeit-Tracking Workflow
TIME_TRACKING_WORKFLOW = {
    "name": "Zeit-Tracking Integration",
    "nodes": [
        {
            "parameters": {
                "events": [
                    "push"
                ],
                "repository": "={{$json.repository}}",
                "owner": "={{$json.owner}}",
                "authentication": "accessToken"
            },
            "name": "GitHub Push Trigger",
            "type": "n8n-nodes-base.githubTrigger",
            "position": [
                250,
                300
            ]
        },
        {
            "parameters": {
                "functionCode": "// Extrahiere Zeit-Tracking-Informationen aus den Commit-Nachrichten\nconst commits = $node[\"GitHub Push Trigger\"].json.commits || [];\nlet timeTrackingData = [];\n\n// Regulärer Ausdruck für Zeit-Tracking-Muster\n// Format: #time 2h30m OP#123 oder #time 2.5h OP#123\nconst timeTrackingRegex = /#time\\s+((?:\\d+(?:\\.\\d+)?[hm]\\s*)+)\\s*(?:OP#(\\d+)|WP#(\\d+))?/i;\n\nfor (const commit of commits) {\n  const match = commit.message.match(timeTrackingRegex);\n  \n  if (match) {\n    // Zeit extrahieren und in Stunden umrechnen\n    const timeStr = match[1];\n    let hours = 0;\n    \n    // Stunden extrahieren\n    const hoursMatch = timeStr.match(/(\\d+(?:\\.\\d+)?)h/i);\n    if (hoursMatch) {\n      hours += parseFloat(hoursMatch[1]);\n    }\n    \n    // Minuten extrahieren und in Stunden umrechnen\n    const minutesMatch = timeStr.match(/(\\d+)m/i);\n    if (minutesMatch) {\n      hours += parseFloat(minutesMatch[1]) / 60;\n    }\n    \n    // Arbeitspaket-ID extrahieren oder null wenn nicht angegeben\n    const workPackageId = match[2] || match[3] || null;\n    \n    timeTrackingData.push({\n      commitId: commit.id,\n      author: commit.author.name,\n      email: commit.author.email,\n      message: commit.message,\n      timestamp: commit.timestamp,\n      timeSpent: hours,\n      workPackageId: workPackageId\n    });\n  }\n}\n\n// Nur Commits mit Zeit-Tracking zurückgeben\nif (timeTrackingData.length > 0) {\n  return {\n    json: {\n      timeTrackingData,\n      repository: $node[\"GitHub Push Trigger\"].json.repository,\n      repository_owner: $node[\"GitHub Push Trigger\"].json.repository_owner\n    }\n  };\n} else {\n  // Kein Zeit-Tracking gefunden, Workflow beenden\n  return null;\n}"
            },
            "name": "Extract Time Tracking",
            "type": "n8n-nodes-base.function",
            "position": [
                450,
                300
            ]
        },
        {
            "parameters": {
                "conditions": {
                    "boolean": [
                        {
                            "value1": "={{$json.timeTrackingData.length > 0}}",
                            "value2": true
                        }
                    ]
                }
            },
            "name": "Has Time Data?",
            "type": "n8n-nodes-base.if",
            "position": [
                650,
                300
            ]
        },
        {
            "parameters": {
                "url": "={{ $json.openProjectUrl }}/api/v3/time_entries",
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
                            "name": "_links.workPackage.href",
                            "value": "={{'/api/v3/work_packages/' + $json.item.workPackageId}}"
                        },
                        {
                            "name": "hours",
                            "value": "={{$json.item.timeSpent}}"
                        },
                        {
                            "name": "comment.raw",
                            "value": "={{\"Zeit erfasst aus Commit \" + $json.item.commitId.substring(0, 8) + \": \" + $json.item.message}}"
                        },
                        {
                            "name": "spentOn",
                            "value": "={{$json.item.timestamp ? $json.item.timestamp.split('T')[0] : new Date().toISOString().split('T')[0]}}"
                        }
                    ]
                }
            },
            "name": "Create Time Entry",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                850,
                200
            ]
        },
        {
            "parameters": {
                "batchSize": 1,
                "options": {}
            },
            "name": "Split Time Entries",
            "type": "n8n-nodes-base.splitInBatches",
            "position": [
                650,
                100
            ]
        },
        {
            "parameters": {
                "functionCode": "// Mappe Repository zu OpenProject-Projekten\nconst repositoryMapping = {\n  'owner/repo-1': {\n    projectId: '1',\n    projectName: 'Project 1',\n    defaultWorkPackage: '123', // Standard-Arbeitspaket, falls keines angegeben\n    host: 'https://myopenproject.com'\n  },\n  // Weitere Repository-Mappings hinzufügen\n};\n\n// Repository-Name aus den Eingabedaten extrahieren\nconst repoFullName = `${$node[\"Extract Time Tracking\"].json.repository_owner}/${$node[\"Extract Time Tracking\"].json.repository}`;\n\n// Mapping für dieses Repository finden oder Default verwenden\nconst mapping = repositoryMapping[repoFullName] || {\n  projectId: '1',\n  projectName: 'Default Project',\n  defaultWorkPackage: '1',\n  host: 'https://myopenproject.com'\n};\n\n// Zeit-Tracking-Daten durchgehen und mit OpenProject-Kontext anreichern\nconst timeTrackingWithContext = $node[\"Extract Time Tracking\"].json.timeTrackingData.map(item => {\n  return {\n    ...item,\n    // Falls keine Arbeitspaket-ID angegeben wurde, Standard-Arbeitspaket verwenden\n    workPackageId: item.workPackageId || mapping.defaultWorkPackage,\n    projectId: mapping.projectId,\n    projectName: mapping.projectName,\n    openProjectUrl: mapping.host\n  };\n});\n\nreturn {\n  json: {\n    timeTrackingData: timeTrackingWithContext,\n    openProjectUrl: mapping.host\n  }\n};"
            },
            "name": "Map to OpenProject",
            "type": "n8n-nodes-base.function",
            "position": [
                450,
                100
            ]
        }
    ],
    "connections": {
        "GitHub Push Trigger": {
            "main": [
                [
                    {
                        "node": "Extract Time Tracking",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Extract Time Tracking": {
            "main": [
                [
                    {
                        "node": "Has Time Data?",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Has Time Data?": {
            "main": [
                [
                    {
                        "node": "Map to OpenProject",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Map to OpenProject": {
            "main": [
                [
                    {
                        "node": "Split Time Entries",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Split Time Entries": {
            "main": [
                [
                    {
                        "node": "Create Time Entry",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}

# KI-gestützte Zusammenfassungen Workflow
AI_SUMMARY_WORKFLOW = {
    "name": "KI-gestützte Zusammenfassungen",
    "nodes": [
        {
            "parameters": {
                "rule": {
                    "interval": [
                        {
                            "triggerAtHour": 9,
                            "triggerAtMinute": 0,
                            "triggerOnDays": [
                                1 # Montag
                            ]
                        }
                    ]
                }
            },
            "name": "Weekly Schedule",
            "type": "n8n-nodes-base.cron",
            "position": [
                250,
                300
            ]
        },
        {
            "parameters": {
                "resource": "repository",
                "operation": "getIssues",
                "owner": "={{$json.owner}}",
                "repository": "={{$json.repository}}",
                "getAll": true,
                "filters": {
                    "state": "all",
                    "since": "={{ $today = new Date(); $lastWeek = new Date($today); $lastWeek.setDate($lastWeek.getDate() - 7); $lastWeek.toISOString() }}"
                },
                "additionalFields": {}
            },
            "name": "Get Recent Issues",
            "type": "n8n-nodes-base.github",
            "position": [
                450,
                200
            ]
        },
        {
            "parameters": {
                "resource": "repository",
                "operation": "getPullRequests",
                "owner": "={{$json.owner}}",
                "repository": "={{$json.repository}}",
                "getAll": true,
                "filters": {
                    "state": "all",
                    "sort": "created",
                    "direction": "desc"
                },
                "additionalFields": {}
            },
            "name": "Get Recent PRs",
            "type": "n8n-nodes-base.github",
            "position": [
                450,
                350
            ]
        },
        {
            "parameters": {
                "functionCode": "// Repository-Konfiguration\nconst repositories = [\n  { owner: 'owner1', repository: 'repo1' },\n  { owner: 'owner1', repository: 'repo2' },\n  // Weitere Repositories hinzufügen\n];\n\nreturn repositories.map(repo => ({ json: repo }));"
            },
            "name": "Repository Config",
            "type": "n8n-nodes-base.function",
            "position": [
                250,
                150
            ]
        },
        {
            "parameters": {
                "functionCode": "// Sammle und formatiere die Daten für die Zusammenfassung\nconst issues = $node[\"Get Recent Issues\"].json.all || [];\nconst pullRequests = $node[\"Get Recent PRs\"].json.all || [];\n\n// Nur PRs der letzten Woche filtern\nconst lastWeek = new Date();\nlastWeek.setDate(lastWeek.getDate() - 7);\n\nconst recentPRs = pullRequests.filter(pr => {\n  const prDate = new Date(pr.created_at);\n  return prDate >= lastWeek;\n});\n\n// Formatiere die Daten für den Prompt\nconst repoData = {\n  owner: $node[\"Repository Config\"].json.owner,\n  repository: $node[\"Repository Config\"].json.repository,\n  issues: issues.map(issue => ({\n    number: issue.number,\n    title: issue.title,\n    state: issue.state,\n    created_at: issue.created_at,\n    closed_at: issue.closed_at,\n    url: issue.html_url,\n    user: issue.user.login\n  })),\n  pullRequests: recentPRs.map(pr => ({\n    number: pr.number,\n    title: pr.title,\n    state: pr.state,\n    created_at: pr.created_at,\n    merged_at: pr.merged_at,\n    url: pr.html_url,\n    user: pr.user.login\n  }))\n};\n\n// Formatiere den Prompt für OpenHands\nconst today = new Date();\nconst datePeriod = `${new Date(lastWeek).toISOString().split('T')[0]} bis ${today.toISOString().split('T')[0]}`;\n\nconst prompt = `Erstelle eine Zusammenfassung der Aktivitäten im Repository ${repoData.owner}/${repoData.repository} für den Zeitraum ${datePeriod}.\n\n## Issues:\n${JSON.stringify(repoData.issues, null, 2)}\n\n## Pull Requests:\n${JSON.stringify(repoData.pullRequests, null, 2)}\n\nGestalte die Zusammenfassung in folgendem Format:\n1. Übersicht der wichtigsten Aktivitäten\n2. Neue Issues (mit Kategorisierung nach Typen)\n3. Geschlossene Issues\n4. Neue Pull Requests und deren Status\n5. Erkennbare Trends und mögliche Blocker\n6. Empfehlungen für das Team\n\nFasse die Daten prägnant und verständlich zusammen und hebe wichtige Punkte hervor.`;\n\nreturn {\n  json: {\n    repository: $node[\"Repository Config\"].json.repository,\n    owner: $node[\"Repository Config\"].json.owner,\n    datePeriod,\n    prompt\n  }\n};"
            },
            "name": "Prepare AI Prompt",
            "type": "n8n-nodes-base.function",
            "position": [
                650,
                300
            ]
        },
        {
            "parameters": {
                "url": "https://api.openhandsai.com/v1/generate",
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
                            "name": "model",
                            "value": "={{$json.llmModel || \"anthropic/claude-3-5-sonnet-20240620\"}}"
                        },
                        {
                            "name": "prompt",
                            "value": "={{$json.prompt}}"
                        },
                        {
                            "name": "max_tokens",
                            "value": "1500"
                        }
                    ]
                }
            },
            "name": "Generate Summary",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                850,
                300
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
                            "value": "=Wöchentliche Zusammenfassung: {{$json.owner}}/{{$json.repository}} ({{$json.datePeriod}})"
                        },
                        {
                            "name": "content",
                            "value": "={{$node[\"Generate Summary\"].json.content || $node[\"Generate Summary\"].json.completion || $node[\"Generate Summary\"].json.text}}"
                        },
                        {
                            "name": "workspace",
                            "value": "={{$json.affineWorkspace}}"
                        }
                    ]
                }
            },
            "name": "Create AFFiNE Document",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1050,
                200
            ]
        },
        {
            "parameters": {
                "url": "={{ $json.openProjectUrl }}/api/v3/posts",
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
                            "name": "_links.project.href",
                            "value": "={{'/api/v3/projects/' + $json.openProjectProjectId}}"
                        },
                        {
                            "name": "subject",
                            "value": "=Wöchentliche Zusammenfassung: {{$json.owner}}/{{$json.repository}} ({{$json.datePeriod}})"
                        },
                        {
                            "name": "content.raw",
                            "value": "={{$node[\"Generate Summary\"].json.content || $node[\"Generate Summary\"].json.completion || $node[\"Generate Summary\"].json.text}}"
                        }
                    ]
                }
            },
            "name": "Create OpenProject News",
            "type": "n8n-nodes-base.httpRequest",
            "position": [
                1050,
                400
            ]
        },
        {
            "parameters": {
                "functionCode": "// Füge Kontext für AFFiNE und OpenProject hinzu\nreturn {\n  ...item,\n  affineApiUrl: \"https://your-affine-instance.com/api/documents\",\n  affineWorkspace: \"default\",\n  openProjectUrl: \"https://your-openproject-instance.com\",\n  openProjectProjectId: \"1\", // ID des OpenProject-Projekts\n  llmModel: \"anthropic/claude-3-5-sonnet-20240620\"\n};"
            },
            "name": "Add Integration Context",
            "type": "n8n-nodes-base.function",
            "position": [
                850,
                150
            ]
        }
    ],
    "connections": {
        "Weekly Schedule": {
            "main": [
                [
                    {
                        "node": "Repository Config",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Repository Config": {
            "main": [
                [
                    {
                        "node": "Get Recent Issues",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Get Recent PRs",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Get Recent Issues": {
            "main": [
                [
                    {
                        "node": "Prepare AI Prompt",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Get Recent PRs": {
            "main": [
                [
                    {
                        "node": "Prepare AI Prompt",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Prepare AI Prompt": {
            "main": [
                [
                    {
                        "node": "Generate Summary",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        },
        "Generate Summary": {
            "main": [
                [
                    {
                        "node": "Add Integration Context",
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
                        "node": "Create AFFiNE Document",
                        "type": "main",
                        "index": 0
                    },
                    {
                        "node": "Create OpenProject News",
                        "type": "main",
                        "index": 0
                    }
                ]
            ]
        }
    }
}
