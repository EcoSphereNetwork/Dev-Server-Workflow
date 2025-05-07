# Anleitung zur Einrichtung von MCP-Servern und OpenHands

Diese Anleitung hilft dir bei der Einrichtung von MCP-Servern für Claude Desktop und OpenHands.

## Voraussetzungen

- Node.js und npm installiert
- Docker und Docker Compose installiert
- Claude Desktop für Linux installiert

## Schritt 1: Einfaches Setup-Skript ausführen

1. Lade das Setup-Skript herunter:

```bash
wget https://raw.githubusercontent.com/username/repo/main/simple-mcp-setup.sh
# oder kopiere das Skript aus dieser Anleitung
```

2. Mache das Skript ausführbar:

```bash
chmod +x simple-mcp-setup.sh
```

3. Führe das Skript aus:

```bash
./simple-mcp-setup.sh
```

Das Skript wird:
- Die benötigten MCP-Server installieren
- Die Konfigurationsdateien für Claude Desktop erstellen
- Die Konfigurationsdateien für OpenHands erstellen
- Start-Skripte für OpenHands und den MCP-Inspektor erstellen

## Schritt 2: API-Keys konfigurieren

Bearbeite die Claude Desktop Konfigurationsdatei, um deine API-Keys hinzuzufügen:

```bash
nano ~/.config/Claude/claude_desktop_config.json
```

Füge deine API-Keys in die entsprechenden Felder ein:

```json
"env": {
  "GITHUB_TOKEN": "dein_github_token_hier"
}
```

## Schritt 3: OpenHands starten

Starte OpenHands mit dem erstellten Skript:

```bash
~/start-openhands.sh
```

## Schritt 4: Claude Desktop neu starten

Starte Claude Desktop neu, damit es die MCP-Server erkennt:

```bash
claude-desktop
```

## Schritt 5: MCP-Inspektor verwenden (optional)

Um zu überprüfen, ob die MCP-Server korrekt funktionieren, kannst du den MCP-Inspektor starten:

```bash
~/start-mcp-inspector.sh
```

Der MCP-Inspektor ist unter http://localhost:6274 erreichbar.

## Fehlerbehebung

### Claude Desktop erkennt die MCP-Server nicht

Überprüfe die Konfigurationsdatei:

```bash
cat ~/.config/Claude/claude_desktop_config.json
```

Stelle sicher, dass die Datei korrekt formatiert ist und keine Syntaxfehler enthält.

### OpenHands startet nicht

Überprüfe die Docker-Logs:

```bash
docker-compose -f ~/openhands-docker-compose.yml logs
```

### MCP-Server funktionieren nicht

Verwende den MCP-Inspektor, um zu überprüfen, ob die Server korrekt funktionieren:

```bash
~/start-mcp-inspector.sh
```

## Nützliche Befehle

- OpenHands starten: `~/start-openhands.sh`
- MCP-Inspektor starten: `~/start-mcp-inspector.sh`
- OpenHands stoppen: `docker-compose -f ~/openhands-docker-compose.yml down`
- MCP-Server neu installieren: `npm install -g @modelcontextprotocol/server-name`
