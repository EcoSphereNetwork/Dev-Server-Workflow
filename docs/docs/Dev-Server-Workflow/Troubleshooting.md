# Fehlerbehebung

Diese Anleitung hilft Ihnen bei der Behebung häufiger Probleme mit der n8n Workflow Integration.

## Allgemeine Probleme

### Python-Modul-Import-Fehler

**Problem**: `ModuleNotFoundError: No module named 'n8n_setup_utils'` oder ähnliche Fehler.

**Lösung**:
1. Stellen Sie sicher, dass Sie das Skript aus dem richtigen Verzeichnis ausführen:
   ```bash
   cd /pfad/zu/Dev-Server-Workflow
   python setup.py install
   ```

2. Wenn das Problem weiterhin besteht, versuchen Sie, das Skript direkt auszuführen:
   ```bash
   cd /pfad/zu/Dev-Server-Workflow/src
   python n8n-setup-main.py --env-file ../.env
   ```

### Abhängigkeitsprobleme

**Problem**: Fehlende Python-Abhängigkeiten.

**Lösung**:
1. Installieren Sie die erforderlichen Abhängigkeiten:
   ```bash
   pip install requests aiohttp
   ```

2. Wenn Sie den MCP-Server verwenden, stellen Sie sicher, dass aiohttp installiert ist:
   ```bash
   pip install aiohttp
   ```

## n8n-Installation

### Docker-Probleme

**Problem**: n8n kann nicht mit Docker installiert werden.

**Lösung**:
1. Überprüfen Sie, ob Docker und Docker Compose installiert sind:
   ```bash
   docker --version
   docker-compose --version
   ```

2. Stellen Sie sicher, dass der Docker-Daemon läuft:
   ```bash
   systemctl status docker
   ```

3. Versuchen Sie, n8n manuell zu installieren:
   ```bash
   docker-compose up -d
   ```

### API-Key-Probleme

**Problem**: Kann keinen API-Key für n8n erhalten.

**Lösung**:
1. Stellen Sie sicher, dass n8n läuft:
   ```bash
   docker ps | grep n8n
   ```

2. Überprüfen Sie die n8n-Logs auf Fehler:
   ```bash
   docker logs n8n
   ```

3. Generieren Sie einen API-Key manuell in der n8n-Benutzeroberfläche:
   - Öffnen Sie n8n im Browser (standardmäßig http://localhost:5678)
   - Gehen Sie zu Einstellungen > API
   - Generieren Sie einen neuen API-Key
   - Fügen Sie den API-Key in Ihre `.env`-Datei ein

## Workflow-Probleme

### Workflow-Erstellung schlägt fehl

**Problem**: Workflows können nicht erstellt werden.

**Lösung**:
1. Überprüfen Sie, ob n8n läuft und erreichbar ist:
   ```bash
   curl http://localhost:5678/healthz
   ```

2. Stellen Sie sicher, dass der API-Key korrekt ist:
   ```bash
   grep N8N_API_KEY .env
   ```

3. Überprüfen Sie die n8n-Logs auf Fehler:
   ```bash
   docker logs n8n
   ```

### Workflow-Aktivierung schlägt fehl

**Problem**: Workflows können nicht aktiviert werden.

**Lösung**:
1. Überprüfen Sie, ob die Workflows erstellt wurden:
   ```bash
   curl -H "X-N8N-API-KEY: IHR_API_KEY" http://localhost:5678/rest/workflows
   ```

2. Stellen Sie sicher, dass alle erforderlichen Credentials eingerichtet sind:
   ```bash
   curl -H "X-N8N-API-KEY: IHR_API_KEY" http://localhost:5678/rest/credentials
   ```

3. Versuchen Sie, den Workflow manuell in der n8n-Benutzeroberfläche zu aktivieren.

## MCP-Server-Probleme

### MCP-Server startet nicht

**Problem**: Der MCP-Server kann nicht gestartet werden.

**Lösung**:
1. Stellen Sie sicher, dass aiohttp installiert ist:
   ```bash
   pip install aiohttp
   ```

2. Überprüfen Sie, ob die MCP-Server-Datei ausführbar ist:
   ```bash
   chmod +x src/n8n-mcp-server.py
   ```

3. Versuchen Sie, den MCP-Server manuell zu starten:
   ```bash
   N8N_URL=http://localhost:5678 N8N_API_KEY=IHR_API_KEY python src/n8n-mcp-server.py
   ```

### OpenHands-Integration funktioniert nicht

**Problem**: OpenHands kann nicht mit dem MCP-Server kommunizieren.

**Lösung**:
1. Überprüfen Sie die OpenHands-Konfigurationsdatei:
   ```bash
   cat src/openhands-mcp-config.json
   ```

2. Stellen Sie sicher, dass der Pfad zum MCP-Server korrekt ist:
   ```bash
   ls -la src/n8n-mcp-server.py
   ```

3. Überprüfen Sie, ob der MCP-Server läuft:
   ```bash
   ps aux | grep n8n-mcp-server
   ```

4. Testen Sie den MCP-Server manuell:
   ```bash
   python src/test-mcp-server.py
   ```

## Credential-Probleme

### GitHub-Credential-Probleme

**Problem**: GitHub-Credentials können nicht eingerichtet werden.

**Lösung**:
1. Überprüfen Sie, ob der GitHub-Token korrekt ist:
   ```bash
   grep GITHUB_TOKEN .env
   ```

2. Stellen Sie sicher, dass der Token die erforderlichen Berechtigungen hat:
   - `repo` für Repository-Zugriff
   - `workflow` für Workflow-Zugriff

3. Versuchen Sie, die Credentials manuell in der n8n-Benutzeroberfläche einzurichten.

### OpenProject-Credential-Probleme

**Problem**: OpenProject-Credentials können nicht eingerichtet werden.

**Lösung**:
1. Überprüfen Sie, ob die OpenProject-URL und der Token korrekt sind:
   ```bash
   grep OPENPROJECT .env
   ```

2. Stellen Sie sicher, dass die OpenProject-Instanz erreichbar ist:
   ```bash
   curl -H "Authorization: Bearer IHR_TOKEN" https://ihre-openproject-instanz.com/api/v3/projects
   ```

3. Versuchen Sie, die Credentials manuell in der n8n-Benutzeroberfläche einzurichten.

## Weitere Hilfe

Wenn Sie weiterhin Probleme haben, können Sie:

1. Die Logs überprüfen:
   ```bash
   docker logs n8n
   ```

2. Das Skript mit mehr Debug-Informationen ausführen:
   ```bash
   LOG_LEVEL=debug python setup.py install
   ```

3. Ein Issue im GitHub-Repository erstellen:
   [https://github.com/EcoSphereNetwork/Dev-Server-Workflow/issues](https://github.com/EcoSphereNetwork/Dev-Server-Workflow/issues)