# Docker MCP Server

Ein MCP-Server für Docker-Operationen.

## Übersicht

Der Docker MCP Server bietet eine MCP-konforme Schnittstelle für Docker-Operationen. Er ermöglicht es, Docker-Container, -Images, -Netzwerke und -Volumes über das Model Context Protocol (MCP) zu verwalten.

## Installation

### Voraussetzungen

- Python 3.8 oder höher
- Docker
- FastAPI
- Pydantic
- Docker Python SDK

### Installation der Abhängigkeiten

```bash
pip install fastapi uvicorn pydantic docker
```

### Konfiguration

Die Konfiguration erfolgt über Umgebungsvariablen oder eine `.env`-Datei. Die folgenden Umgebungsvariablen werden unterstützt:

- `DOCKER_MCP_HOST`: Host, auf dem der Server läuft (Standard: `0.0.0.0`)
- `DOCKER_MCP_PORT`: Port, auf dem der Server läuft (Standard: `3458`)
- `DOCKER_MCP_DEBUG`: Debug-Modus (Standard: `False`)
- `DOCKER_MCP_LOG_LEVEL`: Log-Level (Standard: `INFO`)
- `DOCKER_MCP_LOG_FILE`: Pfad zur Log-Datei (Standard: `logs/docker_mcp.log`)
- `DOCKER_MCP_AUTH_ENABLED`: Ob die Authentifizierung aktiviert ist (Standard: `False`)
- `DOCKER_MCP_AUTH_TOKEN`: Authentifizierungstoken (Standard: `None`)
- `DOCKER_MCP_AUDIT_ENABLED`: Ob die Audit-Protokollierung aktiviert ist (Standard: `True`)
- `DOCKER_MCP_AUDIT_LOG_FILE`: Pfad zur Audit-Log-Datei (Standard: `logs/docker_mcp_audit.log`)
- `DOCKER_MCP_METRICS_ENABLED`: Ob die Metriken-Erfassung aktiviert ist (Standard: `True`)
- `DOCKER_MCP_METRICS_ENDPOINT`: Endpunkt für Metriken (Standard: `/metrics`)
- `DOCKER_HOST`: Docker-Host (Standard: `None`)
- `DOCKER_API_VERSION`: Docker-API-Version (Standard: `None`)
- `DOCKER_TLS_VERIFY`: Ob TLS-Verifizierung aktiviert ist (Standard: `False`)
- `DOCKER_CERT_PATH`: Pfad zu Docker-Zertifikaten (Standard: `None`)

## Verwendung

### Starten des Servers

#### Als HTTP-Server

```bash
./scripts/start-docker-mcp-server.sh
```

#### Als MCP-Server

```bash
./scripts/start-docker-mcp-server-mcp.sh
```

### API-Endpunkte

#### Gesundheitscheck

```
GET /health
```

#### Metriken

```
GET /metrics
```

#### Container

```
GET /containers
GET /containers/{container_id}
POST /containers/{container_id}/start
POST /containers/{container_id}/stop
POST /containers/{container_id}/restart
DELETE /containers/{container_id}
```

#### Images

```
GET /images
GET /images/{image_id}
POST /images/{image_name}/pull
DELETE /images/{image_id}
```

#### Netzwerke

```
GET /networks
GET /networks/{network_id}
```

#### Volumes

```
GET /volumes
GET /volumes/{volume_id}
```

### MCP-Tools

#### Container

- `list_containers`: Liste alle Docker-Container auf
- `get_container`: Erhalte einen Docker-Container
- `start_container`: Starte einen Docker-Container
- `stop_container`: Stoppe einen Docker-Container
- `restart_container`: Starte einen Docker-Container neu
- `remove_container`: Entferne einen Docker-Container

#### Images

- `list_images`: Liste alle Docker-Images auf
- `get_image`: Erhalte ein Docker-Image
- `pull_image`: Ziehe ein Docker-Image
- `remove_image`: Entferne ein Docker-Image

#### Netzwerke

- `list_networks`: Liste alle Docker-Netzwerke auf
- `get_network`: Erhalte ein Docker-Netzwerk

#### Volumes

- `list_volumes`: Liste alle Docker-Volumes auf
- `get_volume`: Erhalte ein Docker-Volume

## Beispiele

### Auflisten aller Container

```bash
curl -X GET http://localhost:3458/containers
```

### Starten eines Containers

```bash
curl -X POST http://localhost:3458/containers/my-container/start
```

### Auflisten aller Container über MCP

```bash
curl -X POST http://localhost:3458/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "list_containers",
      "arguments": {
        "all": true
      }
    }
  }'
```

### Starten eines Containers über MCP

```bash
curl -X POST http://localhost:3458/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "mcp.callTool",
    "params": {
      "name": "start_container",
      "arguments": {
        "container_id": "my-container"
      }
    }
  }'
```

## Entwicklung

### Projektstruktur

```
docker_mcp/
├── api/
│   ├── __init__.py
│   └── router.py
├── core/
│   ├── __init__.py
│   ├── auth.py
│   ├── audit.py
│   ├── config.py
│   ├── docker_executor.py
│   └── metrics.py
├── models/
│   ├── __init__.py
│   └── docker.py
├── utils/
│   ├── __init__.py
│   └── logger.py
├── __init__.py
├── main.py
└── mcp_interface.py
```

### Tests

```bash
pytest tests/mcp_servers/docker_mcp/
```

## Lizenz

MIT