# Implementationsplan für verbessertes MCP-Server-Ökosystem

## Übersicht

Dieser Plan beschreibt die Implementierung eines verbesserten MCP-Server-Ökosystems mit Integration von OpenHands als zentralem Verwaltungstool. Die Implementierung umfasst die Einrichtung verschiedener MCP-Server-Container, die Integration des Ollama-MCP-Bridge und die Konfiguration von OpenHands für die Verwaltung des gesamten Systems.

## 1. Vorbereitung

### 1.1 Systemanforderungen

- Docker und Docker Compose
- Mindestens 8 GB RAM
- Mindestens 50 GB freier Festplattenspeicher
- Linux-Betriebssystem (empfohlen)

### 1.2 Domain-Konfiguration

Folgende Domains müssen auf den Server zeigen:
- openproject.eocspherenet.work
- gitlab.ecospherenet.work
- appflowy.ecospherenet.work
- n8n.ecospherenet.work
- openhands.ecospherenet.work
- mcp.ecospherenet.work

## 2. Implementationsschritte

### 2.1 Repository klonen

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow/docker-mcp-ecosystem-improved
```

### 2.2 Umgebungsvariablen konfigurieren

```bash
cp .env.example .env
# Bearbeite die .env-Datei mit deinen API-Zugangsdaten
```

### 2.3 Verzeichnisstruktur erstellen

```bash
mkdir -p nginx/ssl
mkdir -p gitlab/{config,logs,data}
mkdir -p openproject/{assets,pgdata}
mkdir -p ollama-mcp-bridge/logs
```

### 2.4 SSL-Zertifikate generieren (für Entwicklung)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/server.key -out nginx/ssl/server.crt
```

### 2.5 Ollama-Modelle vorbereiten

```bash
# Stelle sicher, dass Ollama installiert ist
curl -fsSL https://ollama.com/install.sh | sh

# Lade die benötigten Modelle herunter
ollama pull qwen2.5-coder:7b-instruct
ollama pull llama3:8b
ollama pull mistral:7b-instruct-v0.2
```

### 2.6 Docker-Container starten

```bash
docker-compose up -d
```

### 2.7 Überprüfen der Container

```bash
docker-compose ps
```

## 3. Konfiguration der Komponenten

### 3.1 OpenHands

OpenHands ist auf Port 8080 konfiguriert und hat Zugriff auf:
- Alle MCP-Server
- Das lokale Dateisystem unter `/workspace`
- Die Docker-API über den Docker-Socket-Proxy

Zugriff auf OpenHands:
```
http://openhands.ecospherenet.work
```

### 3.2 Desktop Commander

Der Desktop Commander MCP-Server ist für Dateisystem- und Terminaloperationen konfiguriert:
- Erlaubte Verzeichnisse: `/workspace`
- Blockierte Befehle: `rm -rf /`, `sudo`, `su`

### 3.3 Ollama-MCP-Bridge

Die Ollama-MCP-Bridge ist für die Verwendung lokaler LLMs konfiguriert:
- Standardmodell: `qwen2.5-coder:7b-instruct`
- Temperatur: 0.7
- Maximale Token: 4096
- Tool-Erkennung: Aktiviert
- Fehlerbehandlung: Aktiviert

### 3.4 n8n

n8n ist mit benutzerdefinierten MCP-Nodes konfiguriert, die die Interaktion mit den MCP-Servern ermöglichen.

Zugriff auf n8n:
```
http://n8n.ecospherenet.work
```

## 4. Sicherheitsmaßnahmen

### 4.1 Docker-Socket-Proxy

Der Docker-Socket-Proxy beschränkt den Zugriff auf die Docker-API auf bestimmte Endpunkte:
- Erlaubte Endpunkte: `containers`, `images`, `networks`, `volumes`
- Blockierte Endpunkte: `exec`, `post`

### 4.2 Container-Härtung

Die Container sind mit verschiedenen Sicherheitsoptionen konfiguriert:
- `no-new-privileges`: Verhindert, dass Prozesse neue Privilegien erlangen
- `cap_drop`: Entfernt alle Capabilities
- `cap_add`: Fügt nur die minimal notwendigen Capabilities hinzu

### 4.3 Nginx-Sicherheit

Die Nginx-Konfiguration enthält verschiedene Sicherheitsmaßnahmen:
- HTTP-Sicherheitsheader
- SSL-Konfiguration
- Zugriffsbeschränkungen

## 5. Überwachung und Wartung

### 5.1 Gesundheitschecks

Alle Container verfügen über Gesundheitschecks, die regelmäßig die Verfügbarkeit überprüfen.

Überprüfen der Gesundheitschecks:
```bash
docker-compose ps
```

### 5.2 Logs

Die Logs der Container können mit folgendem Befehl angezeigt werden:
```bash
docker-compose logs [service-name]
```

### 5.3 Aktualisierung

Die Container können mit folgendem Befehl aktualisiert werden:
```bash
docker-compose pull
docker-compose up -d
```

## 6. Erweiterung

### 6.1 Hinzufügen eines neuen MCP-Servers

1. Füge einen neuen Service zur `docker-compose.yml` hinzu
2. Aktualisiere die OpenHands-Konfiguration in `openhands/openhands-config.json`
3. Aktualisiere die Ollama-MCP-Bridge-Konfiguration in `ollama-mcp-bridge/bridge_config.json`
4. Aktualisiere die Nginx-Konfiguration in `nginx/conf.d/default.conf`
5. Starte die Container neu: `docker-compose up -d`

### 6.2 Hinzufügen eines neuen Ollama-Modells

1. Lade das Modell herunter: `ollama pull [model-name]`
2. Aktualisiere die Ollama-MCP-Bridge-Konfiguration in `ollama-mcp-bridge/bridge_config.json`
3. Starte die Ollama-MCP-Bridge neu: `docker-compose restart ollama-mcp-bridge`

## 7. Fehlerbehebung

### 7.1 Container startet nicht

Überprüfe die Logs:
```bash
docker-compose logs [service-name]
```

### 7.2 Gesundheitschecks schlagen fehl

Überprüfe den Status der Gesundheitschecks:
```bash
docker-compose ps
```

### 7.3 OpenHands kann nicht auf MCP-Server zugreifen

Überprüfe die OpenHands-Konfiguration:
```bash
docker-compose exec openhands cat /app/data/config.json
```

### 7.4 Ollama-MCP-Bridge kann nicht auf Ollama zugreifen

Überprüfe die Ollama-MCP-Bridge-Konfiguration:
```bash
docker-compose exec ollama-mcp-bridge cat /app/bridge_config.json
```

### 7.5 Nginx-Konfiguration ist fehlerhaft

Überprüfe die Nginx-Konfiguration:
```bash
docker-compose exec nginx nginx -t
```