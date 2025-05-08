# Erweiterte CLI-Befehle

Der Dev-Server-Workflow bietet eine Reihe erweiterter CLI-Befehle, die über die Grundfunktionen hinausgehen. Diese Befehle ermöglichen ein umfassendes Management von Paketen, Konfigurationen und Monitoring-Funktionen.

## Paketmanagement

Der `package`-Befehl ermöglicht die Verwaltung von Paketen mit verschiedenen Paketmanagern.

### Syntax

```bash
./dev-server.sh package [Aktion] [Paket] [Manager] [Optionen]
```

### Aktionen

- `install`: Installiert ein Paket
- `uninstall`: Deinstalliert ein Paket
- `update`: Aktualisiert die Paketlisten
- `upgrade`: Aktualisiert ein Paket oder alle Pakete
- `check`: Prüft, ob ein Paket installiert ist

### Manager

- `apt`: APT-Paketmanager (Debian/Ubuntu)
- `pip`: Python-Paketmanager
- `pip3`: Python 3-Paketmanager
- `npm`: Node.js-Paketmanager
- `npx`: Node.js-Paketausführer
- `dpkg`: Debian-Paketmanager

### Beispiele

```bash
# Installieren eines Pakets mit apt
./dev-server.sh package install jq apt

# Installieren eines Pakets mit pip
./dev-server.sh package install requests pip

# Aktualisieren der apt-Paketlisten
./dev-server.sh package update apt

# Aktualisieren aller Pakete mit apt
./dev-server.sh package upgrade apt

# Prüfen, ob ein Paket installiert ist
./dev-server.sh package check jq apt
```

## Konfigurationsmanagement

Der `configure`-Befehl ermöglicht die Verwaltung von Konfigurationsdateien in verschiedenen Formaten.

### Syntax

```bash
./dev-server.sh configure [Aktion] [Datei] [Schlüssel] [Wert] [Extra]
```

### Aktionen

- `set`: Setzt einen Wert in einer Konfigurationsdatei
- `get`: Liest einen Wert aus einer Konfigurationsdatei
- `comment`: Kommentiert einen Wert in einer Konfigurationsdatei aus
- `uncomment`: Entfernt den Kommentar von einem Wert in einer Konfigurationsdatei
- `set-json`: Setzt einen Wert in einer JSON-Datei
- `get-json`: Liest einen Wert aus einer JSON-Datei
- `set-yaml`: Setzt einen Wert in einer YAML-Datei
- `get-yaml`: Liest einen Wert aus einer YAML-Datei
- `set-xml`: Setzt einen Wert in einer XML-Datei
- `get-xml`: Liest einen Wert aus einer XML-Datei
- `set-env`: Setzt eine Umgebungsvariable in einer .env-Datei
- `get-env`: Liest eine Umgebungsvariable aus einer .env-Datei

### Beispiele

```bash
# Setzen eines Werts in einer Konfigurationsdatei
./dev-server.sh configure set /path/to/config.conf key value

# Lesen eines Werts aus einer Konfigurationsdatei
./dev-server.sh configure get /path/to/config.conf key

# Setzen eines Werts in einer JSON-Datei
./dev-server.sh configure set-json /path/to/config.json key '"value"'

# Lesen eines Werts aus einer JSON-Datei
./dev-server.sh configure get-json /path/to/config.json .key

# Setzen einer Umgebungsvariable in einer .env-Datei
./dev-server.sh configure set-env /path/to/.env KEY value
```

## Monitoring-Funktionen

Der `monitor`-Befehl ermöglicht die Überwachung von Diensten, Ressourcen und Containern.

### Syntax

```bash
./dev-server.sh monitor [Aktion] [Argumente...]
```

### Aktionen

- `check-service`: Prüft den Status eines Dienstes
- `get-logs`: Zeigt die Logs eines Dienstes an
- `check-disk`: Prüft die Festplattennutzung
- `check-memory`: Prüft die Speichernutzung
- `check-cpu`: Prüft die CPU-Auslastung
- `check-port`: Prüft, ob ein Port verfügbar ist
- `check-url`: Prüft, ob eine URL verfügbar ist
- `check-container`: Prüft den Zustand eines Docker-Containers
- `container-stats`: Zeigt Statistiken eines Docker-Containers an
- `check-prometheus`: Führt eine Prometheus-Abfrage aus

### Beispiele

```bash
# Prüfen des Status eines Dienstes
./dev-server.sh monitor check-service nginx systemd

# Anzeigen der Logs eines Dienstes
./dev-server.sh monitor get-logs nginx systemd 100

# Prüfen der Festplattennutzung
./dev-server.sh monitor check-disk /var 90

# Prüfen der Speichernutzung
./dev-server.sh monitor check-memory 90

# Prüfen, ob ein Port verfügbar ist
./dev-server.sh monitor check-port 8080 localhost

# Prüfen, ob eine URL verfügbar ist
./dev-server.sh monitor check-url http://localhost:8080

# Prüfen des Zustands eines Docker-Containers
./dev-server.sh monitor check-container my-container

# Anzeigen von Statistiken eines Docker-Containers
./dev-server.sh monitor container-stats my-container

# Ausführen einer Prometheus-Abfrage
./dev-server.sh monitor check-prometheus http://localhost:9090 'up'
```

## KI-Assistent

Der `ai`-Befehl ermöglicht die Interaktion mit einem KI-Assistenten, der natürliche Sprache in CLI-Befehle übersetzen oder Fragen zum Projekt beantworten kann.

### Syntax

```bash
./dev-server.sh ai [Prompt]
```

### Beispiele

```bash
# Ausführen eines Befehls in natürlicher Sprache
./dev-server.sh ai "Starte den Docker MCP Server"

# Stellen einer Frage zum Projekt
./dev-server.sh ai "Wie kann ich den Monitoring-Stack konfigurieren?"
```

Der KI-Assistent kann:

1. **Befehle übersetzen**: Natürliche Sprache in CLI-Befehle übersetzen und ausführen
2. **Fragen beantworten**: Fragen zum Projekt beantworten
3. **Hilfe leisten**: Bei der Verwendung der CLI-Befehle helfen

## Interaktives Menü

Der `menu`-Befehl öffnet ein interaktives Menü, das alle verfügbaren Befehle und Optionen anzeigt.

### Syntax

```bash
./dev-server.sh menu
```

Das interaktive Menü bietet eine benutzerfreundliche Oberfläche für alle CLI-Befehle und ermöglicht die einfache Auswahl von Optionen ohne Kenntnis der genauen Befehlssyntax.