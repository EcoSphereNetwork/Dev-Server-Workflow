# MCP-Server OpenHands Integration

Diese Dokumentation beschreibt, wie die MCP-Server mit OpenHands integriert werden können.

## Übersicht

Die MCP-Server (Model Context Protocol) bieten erweiterte Funktionen für KI-Agenten wie OpenHands. Durch die Integration der MCP-Server mit OpenHands können Sie die Fähigkeiten des Agenten erheblich erweitern, z.B. mit:

- Dateisystemoperationen
- Ausführung von Befehlen
- GitHub-Integration
- Web-Browsing
- Speicherfunktionen
- Wikipedia-Suche
- und mehr

## Voraussetzungen

- Docker und Docker Compose
- Python 3.8 oder höher
- Die MCP-Server müssen laufen (siehe [README.md](README.md))
- OpenHands-Installation (optional, das Skript kann auch eine Docker-basierte Installation einrichten)

## Schnellstart

1. Starten Sie die MCP-Server:
   ```bash
   ./start-mcp-ecosystem.sh
   ```

2. Führen Sie das Integrationsskript aus:
   ```bash
   ./integrate-with-openhands.sh
   ```

3. Folgen Sie den Anweisungen auf dem Bildschirm, um die Integration abzuschließen.

## Manuelle Integration

Wenn Sie die Integration manuell durchführen möchten, folgen Sie diesen Schritten:

### 1. Generieren Sie die OpenHands-Konfiguration

```bash
./generate-openhands-config.py --github-token YOUR_GITHUB_TOKEN --output ~/.config/openhands/config.toml
```

### 2. Starten Sie OpenHands mit der generierten Konfiguration

```bash
docker run -d \
  --name openhands \
  -p 3000:3000 \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v ~/.openhands-state:/.openhands-state \
  -v ~/.config/openhands:/config \
  -v ~/workspace:/workspace \
  --network mcp-network \
  -e CONFIG_PATH=/config/config.toml \
  -e GITHUB_TOKEN=YOUR_GITHUB_TOKEN \
  docker.all-hands.dev/all-hands-ai/openhands:0.36
```

## Konfigurationsoptionen

Die OpenHands-Konfiguration für MCP-Server verwendet das TOML-Format und enthält die folgenden Hauptabschnitte:

```toml
[mcp]
# SSE-Server - Externe Server, die über Server-Sent Events kommunizieren
sse_servers = [
    "http://mcp-filesystem:3001/mcp",
    # Weitere Server...
]

# Stdio-Server - Lokale Prozesse, die über Standard-Ein-/Ausgabe kommunizieren
stdio_servers = [
    # Beispiel für einen Stdio-Server
    {
        name = "filesystem-fallback",
        command = "npx",
        args = ["-y", "@modelcontextprotocol/server-filesystem"]
    },
    # Weitere Server...
]
```

## Fehlerbehebung

### MCP-Server sind nicht erreichbar

Wenn OpenHands die MCP-Server nicht erreichen kann, stellen Sie sicher, dass:

1. Die MCP-Server laufen:
   ```bash
   docker ps | grep mcp
   ```

2. OpenHands im selben Docker-Netzwerk wie die MCP-Server läuft:
   ```bash
   docker network inspect mcp-network
   ```

3. Die URLs in der OpenHands-Konfiguration korrekt sind:
   ```bash
   cat ~/.config/openhands/config.toml
   ```

### OpenHands startet nicht

Wenn OpenHands nicht startet, prüfen Sie die Logs:

```bash
docker logs openhands
```

## Weitere Ressourcen

- [OpenHands Dokumentation](https://docs.all-hands.dev/)
- [Model Context Protocol (MCP) Dokumentation](https://modelcontextprotocol.io/)
- [MCP in OpenHands](https://docs.all-hands.dev/modules/usage/mcp)