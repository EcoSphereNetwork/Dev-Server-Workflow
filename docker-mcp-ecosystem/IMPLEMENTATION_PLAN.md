# Implementationsplan für MCP-Server in Docker-Containern

## Übersicht

Dieser Plan beschreibt die Implementierung eines umfassenden MCP-Server-Ökosystems mit Integration von OpenHands als zentralem Verwaltungstool. Die Implementierung umfasst die Einrichtung verschiedener MCP-Server-Container, die Integration des Ollama-MCP-Bridge und die Konfiguration von OpenHands für die Verwaltung des gesamten Systems.

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
cd Dev-Server-Workflow/docker-mcp-ecosystem
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
```

### 2.4 SSL-Zertifikate generieren (für Entwicklung)

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx/ssl/server.key -out nginx/ssl/server.crt
```

### 2.5 Docker-Container starten

```bash
docker-compose up -d
```

### 2.6 Überprüfen der Container

```bash
docker-compose ps
```

## 3. Konfiguration der Komponenten

### 3.1 OpenHands

OpenHands ist auf Port 8080 konfiguriert und hat Zugriff auf:
- Alle MCP-Server
- Das lokale Dateisystem unter `/workspace`
- Die Docker-Socket für die Verwaltung von Containern

Zugriff auf OpenHands:
```
http://openhands.ecospherenet.work
```

### 3.2 n8n

n8n ist mit benutzerdefinierten MCP-Nodes konfiguriert, die die Interaktion mit den MCP-Servern ermöglichen.

Zugriff auf n8n:
```
http://n8n.ecospherenet.work
```

### 3.3 Ollama MCP Bridge

Die Ollama MCP Bridge ermöglicht die Verwendung von Ollama-Modellen über das MCP-Protokoll.

### 3.4 MCP-Server

Alle MCP-Server sind über OpenHands und direkt über ihre jeweiligen Endpunkte erreichbar.

## 4. Verwaltung und Monitoring

### 4.1 Container-Verwaltung

OpenHands kann zur Verwaltung der Docker-Container verwendet werden:

```
http://openhands.ecospherenet.work/docker
```

### 4.2 Logs anzeigen

```bash
docker-compose logs -f [service-name]
```

### 4.3 Container neustarten

```bash
docker-compose restart [service-name]
```

## 5. Integration mit externen Systemen

### 5.1 GitHub Integration

Die GitHub MCP-Server ermöglichen die Interaktion mit GitHub-Repositories.

### 5.2 GitLab Integration

Die GitLab MCP-Server ermöglichen die Interaktion mit GitLab-Projekten.

### 5.3 OpenProject Integration

OpenProject ist für Projektmanagement konfiguriert und kann über MCP-Server angesprochen werden.

### 5.4 AppFlowy Integration

AppFlowy ist für Notizen und Dokumentation konfiguriert und kann über MCP-Server angesprochen werden.

## 6. Sicherheitshinweise

### 6.1 API-Schlüssel

Alle API-Schlüssel sollten sicher in der `.env`-Datei gespeichert werden.

### 6.2 Netzwerkzugriff

Der Zugriff auf die MCP-Server sollte durch Firewalls und Zugriffskontrollen beschränkt werden.

### 6.3 Docker-Socket

Der Zugriff auf die Docker-Socket sollte beschränkt werden, da dies vollen Zugriff auf das Host-System ermöglichen kann.

## 7. Fehlerbehebung

### 7.1 Container startet nicht

Überprüfe die Logs:
```bash
docker-compose logs [service-name]
```

### 7.2 MCP-Server nicht erreichbar

Überprüfe die Netzwerkkonfiguration:
```bash
docker-compose exec nginx nginx -t
```

### 7.3 OpenHands kann nicht auf MCP-Server zugreifen

Überprüfe die OpenHands-Konfiguration:
```bash
docker-compose exec openhands cat /app/data/config.json
```

## 8. Erweiterung

### 8.1 Hinzufügen eines neuen MCP-Servers

1. Füge einen neuen Service zur `docker-compose.yml` hinzu
2. Aktualisiere die OpenHands-Konfiguration
3. Aktualisiere die Nginx-Konfiguration
4. Starte die Container neu

### 8.2 Aktualisierung bestehender MCP-Server

```bash
docker-compose pull [service-name]
docker-compose up -d [service-name]
```