# CLI-Anleitung

Diese Anleitung beschreibt die Verwendung der Befehlszeilenschnittstelle (CLI) des Dev-Server-Workflow-Systems.

## Überblick

Das Dev-Server-Workflow-System bietet zwei Hauptschnittstellen für die Verwaltung des Systems:

1. **Interaktive Benutzeroberfläche** (`cli/interactive_ui.sh`): Eine menübasierte Benutzeroberfläche für die einfache Verwaltung des Systems.
2. **Befehlszeilenschnittstelle** (`dev-server-cli.sh`): Eine Befehlszeilenschnittstelle für die Verwaltung des Systems über Befehle.

## Interaktive Benutzeroberfläche

Die interaktive Benutzeroberfläche bietet eine menübasierte Schnittstelle für die Verwaltung des Systems. Sie können die interaktive Benutzeroberfläche mit folgendem Befehl starten:

```bash
./cli/interactive_ui.sh
```

Die interaktive Benutzeroberfläche bietet folgende Funktionen:

- **Status anzeigen**: Zeigt den Status aller Komponenten an.
- **MCP-Server verwalten**: Verwaltet die MCP-Server (starten, stoppen, neustarten, Logs anzeigen).
- **n8n verwalten**: Verwaltet n8n (starten, stoppen, neustarten, Logs anzeigen, Workflows verwalten).
- **Logs anzeigen**: Zeigt die Logs aller Komponenten an.
- **Konfiguration**: Verwaltet die Konfiguration des Systems.
- **Monitoring**: Überwacht die Systemleistung und -gesundheit.
- **Backup und Wiederherstellung**: Erstellt und verwaltet Backups.
- **Installation**: Installiert und aktualisiert das System.
- **Dokumentation**: Zeigt die Dokumentation an.
- **Über**: Zeigt Informationen über das System an.

### Dialog-basierte Benutzeroberfläche

Wenn das `dialog`-Paket installiert ist, verwendet die interaktive Benutzeroberfläche eine Dialog-basierte Schnittstelle:

![Dialog-basierte Benutzeroberfläche](../assets/dialog-ui.png)

### Textbasierte Benutzeroberfläche

Wenn das `dialog`-Paket nicht installiert ist, verwendet die interaktive Benutzeroberfläche eine textbasierte Schnittstelle:

```
=== Dev-Server-Workflow ===

1. Status anzeigen
2. MCP-Server verwalten
3. n8n verwalten
4. Logs anzeigen
5. Konfiguration
6. Monitoring
7. Backup und Wiederherstellung
8. Installation
9. Dokumentation
10. Über
11. Beenden

Wählen Sie eine Option (1-11):
```

## Befehlszeilenschnittstelle

Die Befehlszeilenschnittstelle bietet eine Reihe von Befehlen für die Verwaltung des Systems. Sie können die Befehlszeilenschnittstelle mit folgendem Befehl verwenden:

```bash
./dev-server-cli.sh <befehl> [optionen]
```

### Verfügbare Befehle

#### Allgemeine Befehle

- `help`: Zeigt die Hilfe an.
- `ui`: Startet die interaktive Benutzeroberfläche.
- `status`: Zeigt den Status aller Komponenten an.

#### Komponenten verwalten

- `start <komponente>`: Startet eine Komponente und ihre Abhängigkeiten.
- `stop <komponente>`: Stoppt eine Komponente und ihre abhängigen Komponenten.
- `restart <komponente>`: Startet eine Komponente neu.
- `logs <komponente>`: Zeigt die Logs einer Komponente an.

#### Konfiguration verwalten

- `config`: Verwaltet die Konfiguration des Systems.
- `config list <typ> <datei>`: Listet alle Konfigurationsschlüssel auf.
- `config get <typ> <datei> <schlüssel>`: Ruft einen Konfigurationswert ab.
- `config save <typ> <datei> <schlüssel> <wert>`: Speichert einen Konfigurationswert.
- `config delete <typ> <datei> <schlüssel>`: Löscht einen Konfigurationsschlüssel.

#### Backup und Wiederherstellung

- `backup`: Erstellt ein Backup.
- `restore <backup>`: Stellt ein Backup wieder her.

#### Monitoring

- `monitor`: Überwacht die Systemleistung und -gesundheit.

### Beispiele

#### Status anzeigen

```bash
./dev-server-cli.sh status
```

Ausgabe:

```
=== Systemstatus ===

Datum: Do 8. Mai 22:30:42 UTC 2025
Hostname: dev-server
Kernel: 5.15.0-1041-azure

=== Docker Status ===

Docker Version: Docker version 24.0.5, build 24.0.5-0ubuntu1~22.04.1
Laufende Container: 5
Alle Container: 8
Images: 12
Volumes: 3
Networks: 2

=== MCP-Server Status ===

desktop-commander-mcp   Up 2 hours   0.0.0.0:3333->3333/tcp
filesystem-mcp          Up 2 hours   0.0.0.0:3334->3334/tcp
github-mcp              Up 2 hours   0.0.0.0:3335->3335/tcp
memory-mcp              Up 2 hours   0.0.0.0:3336->3336/tcp
prompt-mcp              Up 2 hours   0.0.0.0:3337->3337/tcp

=== n8n Status ===

n8n                     Up 2 hours   0.0.0.0:5678->5678/tcp
```

#### Komponente starten

```bash
./dev-server-cli.sh start n8n
```

Ausgabe:

```
[INFO] Starting component n8n...
[INFO] Component n8n started successfully
```

#### Komponente stoppen

```bash
./dev-server-cli.sh stop web-ui
```

Ausgabe:

```
[INFO] Stopping component web-ui...
Components depend on web-ui: 
Do you want to stop these components as well? (y/n) y
[INFO] Stopping component web-ui...
[INFO] Component web-ui stopped successfully
```

#### Logs anzeigen

```bash
./dev-server-cli.sh logs n8n
```

Ausgabe:

```
=== Logs für n8n ===

2025-05-08T22:30:00.000Z [INFO] n8n started successfully
2025-05-08T22:30:01.000Z [INFO] Workflow "GitHub to OpenProject" activated
2025-05-08T22:30:02.000Z [INFO] Workflow "Document Sync" activated
2025-05-08T22:30:03.000Z [INFO] Workflow "OpenHands Integration" activated
```

#### Konfiguration verwalten

```bash
# Konfiguration anzeigen
./dev-server-cli.sh config list env .env

# Konfigurationswert setzen
./dev-server-cli.sh config save env .env N8N_PORT 5678

# Konfigurationswert abrufen
./dev-server-cli.sh config get env .env N8N_PORT
```

#### Backup erstellen

```bash
./dev-server-cli.sh backup
```

Ausgabe:

```
[INFO] Creating backup backup_20250508_223045...
[INFO] Backup created: /workspace/Dev-Server-Workflow/backups/backup_20250508_223045.tar.gz
```

#### Backup wiederherstellen

```bash
./dev-server-cli.sh restore backup_20250508_223045.tar.gz
```

Ausgabe:

```
[INFO] Restoring backup backup_20250508_223045.tar.gz...
[INFO] Stopping all containers...
[INFO] Extracting backup...
[INFO] Restoring configuration...
[INFO] Backup restored successfully
[INFO] Start the containers to apply the changes
```

## Erweiterte Befehle

### Dependency Management

```bash
# Alle Komponenten und ihre Abhängigkeiten anzeigen
./src/common/dependency_manager.sh list

# Abhängigkeiten einer Komponente anzeigen
./src/common/dependency_manager.sh dependencies n8n

# Abhängige Komponenten anzeigen
./src/common/dependency_manager.sh dependents n8n

# Komponente starten (und ihre Abhängigkeiten)
./src/common/dependency_manager.sh start n8n

# Komponente stoppen (und ihre Abhängigen)
./src/common/dependency_manager.sh stop n8n

# Alle Komponenten starten
./src/common/dependency_manager.sh start-all

# Alle Komponenten stoppen
./src/common/dependency_manager.sh stop-all
```

### Konfigurationsmanagement

```bash
# Konfiguration laden
./cli/config_manager.sh load env /path/to/.env [prefix]

# Konfiguration speichern
./cli/config_manager.sh save env /path/to/.env KEY VALUE [create_if_missing]

# Konfigurationswert abrufen
./cli/config_manager.sh get env /path/to/.env KEY [default_value]

# Konfigurationsschlüssel auflisten
./cli/config_manager.sh list env /path/to/.env

# Konfigurationsschlüssel löschen
./cli/config_manager.sh delete env /path/to/.env KEY

# Alle Konfigurationen laden
./cli/config_manager.sh load-all
```

### Fehlerbehandlung

```bash
# Befehl überprüfen
./cli/error_handler.sh check_command "docker" "Docker ist nicht installiert"

# Datei überprüfen
./cli/error_handler.sh check_file "/path/to/file" "true"

# Verzeichnis überprüfen
./cli/error_handler.sh check_directory "/path/to/dir" "true"

# Eingabe validieren
./cli/error_handler.sh validate_input "input" "pattern" "Ungültiges Eingabeformat"

# Befehl mit Timeout ausführen
./cli/error_handler.sh execute_with_timeout "5s" "curl http://localhost:5678"

# Container-Status überprüfen
./cli/error_handler.sh check_container_running "n8n"

# Netzwerkverbindung überprüfen
./cli/error_handler.sh check_network "localhost" "5678" "5"
```

## Anpassung der CLI

Sie können die CLI an Ihre Bedürfnisse anpassen, indem Sie die folgenden Dateien bearbeiten:

- `dev-server-cli.sh`: Hauptskript für die Befehlszeilenschnittstelle
- `cli/interactive_ui.sh`: Skript für die interaktive Benutzeroberfläche
- `cli/config.sh`: Konfigurationsdatei für die CLI
- `cli/functions.sh`: Funktionen für die CLI

### Hinzufügen eines neuen Befehls

Um einen neuen Befehl zur CLI hinzuzufügen, bearbeiten Sie die Datei `dev-server-cli.sh` und fügen Sie einen neuen Fall zur `case`-Anweisung hinzu:

```bash
case "$COMMAND" in
    # ... bestehende Befehle ...
    
    neuer-befehl)
        # Implementierung des neuen Befehls
        echo "Neuer Befehl ausgeführt"
        ;;
    
    # ... weitere Befehle ...
esac
```

### Hinzufügen eines neuen Menüpunkts zur interaktiven Benutzeroberfläche

Um einen neuen Menüpunkt zur interaktiven Benutzeroberfläche hinzuzufügen, bearbeiten Sie die Datei `cli/interactive_ui.sh` und fügen Sie einen neuen Menüpunkt zum Hauptmenü hinzu:

```bash
show_main_menu_dialog() {
    local choice=$(dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Hauptmenü" \
        --menu "Wählen Sie eine Option:" 20 78 12 \
        # ... bestehende Menüpunkte ...
        "12" "Neuer Menüpunkt" \
        # ... weitere Menüpunkte ...
        3>&1 1>&2 2>&3)
    
    # Handle menu choice
    case "$choice" in
        # ... bestehende Fälle ...
        12) show_new_menu_dialog ;;
        # ... weitere Fälle ...
    esac
}

# Neue Funktion für den neuen Menüpunkt
show_new_menu_dialog() {
    # Implementierung des neuen Menüpunkts
    dialog --clear --backtitle "Dev-Server-Workflow" \
        --title "Neuer Menüpunkt" \
        --msgbox "Dies ist ein neuer Menüpunkt" 10 60
    
    # Zurück zum Hauptmenü
    show_main_menu_dialog
}
```

## Weitere Ressourcen

- [Installationsanleitung](../installation/comprehensive-guide.md)
- [Konfigurationsanleitung](../configuration/index.md)
- [Fehlerbehebungsanleitung](../troubleshooting/index.md)
- [Bash-Skript-Anleitung](https://tldp.org/LDP/abs/html/)
- [Dialog-Dokumentation](https://invisible-island.net/dialog/)