#!/bin/bash

# Verbessertes Hauptinstallationsskript für das gesamte Dev-Server-Workflow-Projekt
# Überprüft Paketversionen und richtet Aliase ein

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Funktion zum Anzeigen von Nachrichten
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

saschi@server1:/tmp/acme-test$ cd /opt/n8n
sudo docker-compose down
sudo docker-compose up -d
sudo: docker-compose: Befehl nicht gefunden
sudo: docker-compose: Befehl nicht gefunden
saschi@server1:/opt/n8n$ sudo docker compose down
WARN[0000] /opt/n8n/docker-compose.yml: the attribute version is obsolete, it will be ignored, please remove it to avoid potential confusion 
[+] Running 2/2
 ✔ Container n8n-n8n-1  Removed                                            1.6s 
 ✔ Network n8n_default  Removed   

Wie stelle ich in meinem ubuntu 22 ein, das beide kommandos, docker-compose und docker compose den befehl ausführen?
Bearbeiten

Es scheint, dass auf Ihrem Ubuntu 22.04 System der Befehl docker-compose nicht gefunden wird, während docker compose funktioniert. Dies liegt daran, dass Docker inzwischen den Compose-Befehl als Unterfunktion von Docker integriert hat (docker compose), während das separate docker-compose Tool nicht installiert ist.

Um beide Befehle verwenden zu können, gibt es zwei Lösungswege:

    Ein Alias erstellen: Sie können einen Alias in Ihrer Shell-Konfiguration hinzufügen:

bash

echo 'alias docker-compose="docker compose"' >> ~/.bashrc
source ~/.bashrc

Dies leitet alle docker-compose Aufrufe an docker compose weiter.
Docker Compose Plugin installieren: Alternativ können Sie das separate Docker Compose-Plugin installieren:

bash

sudo apt update
sudo apt install docker-compose-plugin

Oder wenn Sie die eigenständige Version bevorzugen:

    bash

    sudo apt update
    sudo apt install docker-compose

Die erste Methode (Alias) ist einfacher und sicherer, da Sie immer die bereits installierte Version von Docker Compose verwenden. Die zweite Methode installiert zusätzliche Software, die möglicherweise gewartet werden muss.

Nach der Einrichtung sollten beide Befehle wie gewünscht funktionieren.
EcoSphereNetwork/Dev-Server-Workflow

main

GITHUB

Ich möchte meine scripte überarbeiten. sie sollen prüfen, welche pakete und wwelche versionen bereits installiert sind und dann entsprechend die benötigten installationen durchführen. für docker compose soll ein alias angelegt werden. welche dateien von mir müssen überarbeitet werden? kann du das für mich tun und mir jeweils die vollständig überarbeitete version geben?
Bearbeiten

Nach Durchsicht Ihrer Dokumente sehe ich, dass mehrere Skripte überarbeitet werden sollten, um Paketversionen zu prüfen und einen Alias für Docker Compose einzurichten. Die Hauptdateien, die überarbeitet werden müssen, sind:

    scripts/install-mcp-servers.sh - Installationsskript für MCP-Server
    scripts/start-mcp-servers.sh - Skript zum Starten der MCP-Server
    scripts/install-all.sh - Hauptinstallationsskript für das gesamte Projekt
    start-web-ui.sh - Skript zum Starten der Web-UI
    dev-server-cli.sh - Das CLI-Hauptskript

Ich werde diese Dateien für Sie überarbeiten und eine vollständige, aktualisierte Version von jeder bereitstellen.
1. scripts/install-mcp-servers.sh (überarbeitet)
2. scripts/start-mcp-servers.sh (überarbeitet)

Continue
Bearbeiten

Ich werde mit der Überarbeitung der Skripte fortfahren. Hier ist die Fortsetzung von start-mcp-servers.sh und dann die weiteren Skripte.
3. scripts/install-all.sh (überarbeitet)

Continue
Bearbeiten

Ich werde mit der Überarbeitung von install-all.sh fortfahren und dann die restlichen Skripte fertigstellen.
4. start-web-ui.sh (überarbeitet)
5. dev-server-cli.sh (überarbeitet)

Weiter
Bearbeiten

Ich werde das letzte Skript dev-server-cli.sh jetzt überarbeiten.
Zusammenfassung der Änderungen

Ich habe alle fünf Skripte erfolgreich überarbeitet, um Paketversionen zu prüfen und einen Alias für Docker Compose einzurichten. Hier ist eine Zusammenfassung der wichtigsten Verbesserungen in jedem Skript:

    install-mcp-servers.sh:
        Hinzufügung von Funktionen zur Überprüfung installierter Pakete und deren Versionen
        Implementierung einer Funktion zum Einrichten eines Alias für docker-compose
        Verbesserung der Erkennung und Installation von Systemabhängigkeiten
        Fehlerbehandlung und bessere Benutzerführung
    start-mcp-servers.sh:
        Prüfung der Docker- un

Weiter
Bearbeiten

Hier ist die vollständige Zusammenfassung der Änderungen:
Zusammenfassung der Änderungen

Ich habe alle fünf Skripte erfolgreich überarbeitet, um Paketversionen zu prüfen und einen Alias für Docker Compose einzurichten. Hier ist eine Zusammenfassung der wichtigsten Verbesserungen in jedem Skript:

    install-mcp-servers.sh:
        Hinzufügung von Funktionen zur Überprüfung installierter Pakete und deren Versionen
        Implementierung einer Funktion zum Einrichten eines Alias für docker-compose
        Verbesserung der Erkennung und Installation von Systemabhängigkeiten
        Fehlerbehandlung und bessere Benutzerführung
    start-mcp-servers.sh:
        Prüfung der Docker- und Docker Compose-Versionen
        Einrichtung des docker-compose Alias für eine bessere Kompatibilität
        Verbesserte Logging-Funktionalität
        Hinzufügen von detaillierten Serverstatus-Prüfungen
    install-all.sh:
        Umfassende Prüfung und Installation aller Abhängigkeiten
        Verbesserte Versionserkennung und Aktualisierungsvorschläge
        Zuverlässigere n8n-Installation mit Versionsüberprüfung
        Automatische Einrichtung des docker-compose Alias
    start-web-ui.sh:
        Verbesserte Docker und Docker Compose-Versionsüberprüfung
        Intelligente Erkennung und Verwendung des passenden Docker Compose-Befehls
        Automatische Installation fehlender Pakete wie OpenSSL
        Einrichtung des docker-compose Alias für die aktuelle Sitzung
    dev-server-cli.sh:
        Umfassendere Abhängigkeitsprüfungen für alle benötigten Komponenten
        Dynamische Erkennung und Verwendung des passenden Docker Compose-Befehls
        Neue Optionen für Abhängigkeitsprüfung (--check-deps) und Alias-Einrichtung (--setup-alias)
        Verbesserte Komponentenverwaltung mit detaillierten Statusberichten

Alle Skripte verfügen jetzt über:

    Eine Funktion check_version() zum Überprüfen installierter Paketversionen
    Eine Funktion setup_docker_compose_alias() zum Einrichten eines Alias für docker-compose
    Automatische Erkennung des Betriebssystems für bessere Kompatibilität
    Verbessertes Fehlerbehandlung und Logging
    Detailliertere Benutzerführung mit farbigen Ausgaben

Diese Verbesserungen machen Ihre Skripte robuster und benutzerfreundlicher, indem sie:

    Automatisch fehlende Abhängigkeiten identifizieren und installieren
    Veraltete Versionen erkennen und Aktualisierungsvorschläge machen
    Die Kompatibilität zwischen docker-compose und docker compose sicherstellen
    Detaillierte Anweisungen für den Benutzer bereitstellen

Damit sollten Ihre Skripte nun in einer Vielzahl von Umgebungen besser funktionieren und dem Benutzer eine klarere Anleitung geben, falls etwas nicht wie erwartet funktioniert.

saschi@server1:~/Dev-Server-Workflow/scripts$ sudo ./install-all.sh
[sudo] Passwort für saschi: 
./install-all.sh: Zeile 45: Syntaxfehler beim unerwarteten Wort »}«
./install-all.sh: Zeile 45: `    }'
Bearbeiten

Es gibt einen Syntaxfehler in der Datei install-all.sh. Der Fehler liegt in der check_version()-Funktion, wo eine schließende geschweifte Klammer } ohne passende öffnende Klammer erscheint. Ich werde den Fehler beheben und Ihnen den korrigierten Code für die Funktion zeigen.

Das Problem liegt in Zeile 45, wo der Vergleich der Versionen fehlerhaft ist. Die Funktion verwendet geschweifte Klammern an einer Stelle, wo sie nicht hingehören.

Hier ist die korrigierte Version der betroffenen Funktion:

bash

# Funktion zum Überprüfen einer Paketversion
check_version() {
    local package=$1
    local min_version=$2
    local version_cmd=$3
    local version_regex=$4

    if ! command -v "$package" &> /dev/null; then
        return 1
    fi

    local version_output
    version_output=$($version_cmd)
    local current_version
    current_version=$(echo "$version_output" | grep -oE "$version_regex" | head -1)

    if [ -z "$current_version" ]; then
        warn "Konnte die Version von $package nicht ermitteln."
        return 2
    fi

    if [ "$(printf '%s\n' "$min_version" "$current_version" | sort -V | head -n1)" != "$min_version" ]; then
        log "$package Version $current_version gefunden (Minimum: $min_version)."
        return 0
    else
        warn "$package Version $current_version ist älter als die benötigte Version $min_version."
        return 3
    fi
}

# Funktion zum Einrichten eines Alias für docker-compose
setup_docker_compose_alias() {
    # Prüfen, ob docker compose Befehl verfügbar ist
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Prüfen, ob docker-compose Befehl verfügbar ist
        if ! command -v docker-compose &> /dev/null; then
            log "Richte Alias für docker-compose ein..."
            
            # Prüfen, welche Shell verwendet wird
            local shell_rc
            if [ -n "$ZSH_VERSION" ]; then
                shell_rc="$HOME/.zshrc"
            elif [ -n "$BASH_VERSION" ]; then
                shell_rc="$HOME/.bashrc"
            else
                # Standardmäßig .bashrc verwenden
                shell_rc="$HOME/.bashrc"
            fi
            
            # Prüfen, ob der Alias bereits existiert
            if ! grep -q "alias docker-compose='docker compose'" "$shell_rc"; then
                echo 'alias docker-compose="docker compose"' >> "$shell_rc"
                log "Alias zu $shell_rc hinzugefügt."
                log "Bitte führen Sie 'source $shell_rc' aus, oder starten Sie ein neues Terminal, um den Alias zu aktivieren."
                
                # Temporär für die aktuelle Sitzung einrichten
                alias docker-compose="docker compose"
                log "Alias temporär für die aktuelle Sitzung eingerichtet."
            else
                log "Alias existiert bereits in $shell_rc."
            fi
        else
            log "docker-compose Befehl ist bereits verfügbar."
        fi
    else
        warn "Docker Compose Plugin ist nicht installiert. Kann keinen Alias einrichten."
    fi
}

# Funktion zum Überprüfen, ob Docker installiert ist
check_docker() {
    log "Überprüfe Docker-Installation..."
    
    if ! command -v docker &> /dev/null; then
        warn "Docker ist nicht installiert. Versuche, es zu installieren..."
        
        # Erkennen des Betriebssystems und der Paketmanager
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        else
            OS=$(uname -s)
        fi
        
        case $OS in
            ubuntu|debian|linuxmint)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Docker mit apt..."
                sudo apt-get update
                sudo apt-get install -y apt-transport-https ca-certificates curl gnupg lsb-release
                curl -fsSL https://download.docker.com/linux/"$OS"/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
                echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/$OS $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
                sudo apt-get update
                sudo apt-get install -y docker-ce docker-ce-cli containerd.io
                ;;
            fedora|centos|rhel)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Docker mit dnf/yum..."
                sudo dnf -y install dnf-plugins-core
                sudo dnf config-manager --add-repo https://download.docker.com/linux/fedora/docker-ce.repo
                sudo dnf -y install docker-ce docker-ce-cli containerd.io
                ;;
            arch|manjaro)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Docker mit pacman..."
                sudo pacman -Sy docker
                ;;
            *)
                error "Nicht unterstütztes Betriebssystem: $OS"
                error "Bitte installieren Sie Docker manuell: https://docs.docker.com/engine/install/"
                return 1
                ;;
        esac
        
        # Starte Docker
        sudo systemctl start docker
        sudo systemctl enable docker
        
        # Füge den aktuellen Benutzer zur Docker-Gruppe hinzu
        sudo usermod -aG docker "$USER"
        
        log "Docker wurde installiert. Bitte starten Sie die Shell neu, um die Docker-Gruppe zu aktivieren."
        log "Führen Sie dann dieses Skript erneut aus."
        exit 0
    fi
    
    # Überprüfe die Docker-Version
    check_version "docker" "20.10.0" "docker --version" "([0-9]+\.[0-9]+\.[0-9]+)"
    if [ $? -eq 0 ]; then
        log "Docker ist installiert und ausreichend aktuell."
    else
        warn "Docker ist installiert, aber möglicherweise nicht ausreichend aktuell."
        warn "Es wird empfohlen, Docker auf mindestens Version 20.10.0 zu aktualisieren."
    fi
    
    return 0
}

# Funktion zum Überprüfen, ob Docker Compose installiert ist
check_docker_compose() {
    log "Überprüfe Docker Compose-Installation..."
    
    # Prüfe zunächst das neue Docker-Compose-Plugin
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin ist installiert."
        
        # Versuche, die Version zu ermitteln
        docker_compose_version=$(docker compose version --short 2>/dev/null || docker compose version 2>/dev/null | grep -oE "v?[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        
        if [ -n "$docker_compose_version" ]; then
            # Entferne ein mögliches 'v' am Anfang
            docker_compose_version=${docker_compose_version#v}
            log "Docker Compose Plugin Version: $docker_compose_version"
            
            # Richte den Alias ein
            setup_docker_compose_alias
            
            return 0
        fi
    fi
    
    # Prüfe das eigenständige Docker-Compose-Binary
    if command -v docker-compose &> /dev/null; then
        log "Eigenständiges Docker Compose ist installiert."
        
        docker_compose_version=$(docker-compose --version | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        if [ -n "$docker_compose_version" ]; then
            log "Docker Compose Version: $docker_compose_version"
            
            # Vergleiche mit der Mindestversion
            if [ "$(printf '%s\n' "1.29.0" "$docker_compose_version" | sort -V | head -n1)" != "1.29.0" ]; then
                log "Docker Compose ist ausreichend aktuell."
                return 0
            else
                warn "Docker Compose Version ist älter als 1.29.0. Ein Update wird empfohlen."
            fi
        fi
    fi
    
    # Wenn wir hier ankommen, müssen wir Docker Compose installieren oder aktualisieren
    warn "Docker Compose ist nicht installiert oder zu alt. Versuche zu installieren/aktualisieren..."
    
    # Erkennen des Betriebssystems und der Paketmanager
    if [ -f /etc/os-release ]; then
        . /etc/os-release
        OS=$ID
    else
        OS=$(uname -s)
    fi
    
    case $OS in
        ubuntu|debian|linuxmint)
            log "Erkanntes Betriebssystem: $OS"
            log "Installiere Docker Compose Plugin mit apt..."
            sudo apt-get update
            sudo apt-get install -y docker-compose-plugin
            ;;
        fedora|centos|rhel)
            log "Erkanntes Betriebssystem: $OS"
            log "Installiere Docker Compose Plugin mit dnf..."
            sudo dnf -y install docker-compose-plugin
            ;;
        arch|manjaro)
            log "Erkanntes Betriebssystem: $OS"
            log "Installiere Docker Compose mit pacman..."
            sudo pacman -Sy docker-compose
            ;;
        *)
            # Fallback auf das Docker-Compose-Binary
            log "Installiere Docker Compose Binary direkt..."
            COMPOSE_VERSION="v2.20.3"
            sudo curl -L "https://github.com/docker/compose/releases/download/${COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
            log "Docker Compose $COMPOSE_VERSION wurde installiert."
            ;;
    esac
    
    # Prüfe, ob die Installation erfolgreich war
    if command -v docker &> /dev/null && docker compose version &> /dev/null; then
        log "Docker Compose Plugin wurde erfolgreich installiert."
        # Richte den Alias ein
        setup_docker_compose_alias
        return 0
    elif command -v docker-compose &> /dev/null; then
        log "Eigenständiges Docker Compose wurde erfolgreich installiert."
        return 0
    else
        error "Docker Compose konnte nicht installiert werden. Bitte installieren Sie Docker Compose manuell."
        return 1
    fi
}

# Funktion zum Starten des Docker-Daemons
start_docker_daemon() {
    log "Überprüfe, ob der Docker-Daemon läuft..."
    
    if ! docker info &> /dev/null; then
        warn "Docker-Daemon läuft nicht. Versuche, ihn zu starten..."
        
        if command -v systemctl &> /dev/null; then
            sudo systemctl start docker
        elif command -v service &> /dev/null; then
            sudo service docker start
        else
            # Direkter Start des Docker-Daemons im Hintergrund
            sudo dockerd > /tmp/docker.log 2>&1 &
            sleep 5
        fi
        
        if ! docker info &> /dev/null; then
            error "Konnte den Docker-Daemon nicht starten. Bitte starten Sie ihn manuell."
            error "Verwenden Sie 'sudo systemctl start docker' oder 'sudo service docker start'."
            return 1
        fi
        
        log "Docker-Daemon wurde gestartet."
    else
        log "Docker-Daemon läuft bereits."
    fi
    
    return 0
}

# Funktion zum Installieren von n8n
install_n8n() {
    log "Installiere n8n..."
    
    # Überprüfe, ob n8n bereits installiert ist
    if command -v n8n &> /dev/null; then
        n8n_version=$(n8n --version 2>/dev/null | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
        log "n8n ist bereits installiert (Version: $n8n_version)."
        
        # Überprüfe, ob ein Update erforderlich ist
        if [ "$(printf '%s\n' "0.225.0" "$n8n_version" | sort -V | head -n1)" != "0.225.0" ]; then
            log "n8n Version ist ausreichend aktuell."
            return 0
        else
            warn "n8n Version ist veraltet. Ein Update wird empfohlen."
            
            # Frage den Benutzer, ob n8n aktualisiert werden soll
            read -p "Möchten Sie n8n aktualisieren? (j/n) " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Jj]$ ]]; then
                log "Aktualisiere n8n..."
                # Verwende npm, wenn es installiert ist
                if command -v npm &> /dev/null; then
                    npm update -g n8n
                else
                    warn "npm ist nicht installiert. Bitte installieren Sie npm und aktualisieren Sie n8n manuell."
                    return 1
                fi
            else
                log "n8n wird nicht aktualisiert."
                return 0
            fi
        fi
    else
        # Prüfe, ob npm installiert ist
        if ! command -v npm &> /dev/null; then
            warn "npm ist nicht installiert. Versuche, es zu installieren..."
            
            # Erkennen des Betriebssystems und der Paketmanager
            if [ -f /etc/os-release ]; then
                . /etc/os-release
                OS=$ID
            else
                OS=$(uname -s)
            fi
            
            case $OS in
                ubuntu|debian|linuxmint)
                    log "Erkanntes Betriebssystem: $OS"
                    log "Installiere npm mit apt..."
                    sudo apt-get update
                    sudo apt-get install -y nodejs npm
                    ;;
                fedora|centos|rhel)
                    log "Erkanntes Betriebssystem: $OS"
                    log "Installiere npm mit dnf..."
                    sudo dnf -y install nodejs npm
                    ;;
                arch|manjaro)
                    log "Erkanntes Betriebssystem: $OS"
                    log "Installiere npm mit pacman..."
                    sudo pacman -Sy nodejs npm
                    ;;
                *)
                    error "Nicht unterstütztes Betriebssystem: $OS"
                    error "Bitte installieren Sie npm manuell und führen Sie dann dieses Skript erneut aus."
                    return 1
                    ;;
            esac
        fi
        
        # Installiere n8n
        log "Installiere n8n über npm..."
        npm install -g n8n
        
        # Überprüfe, ob die Installation erfolgreich war
        if command -v n8n &> /dev/null; then
            n8n_version=$(n8n --version 2>/dev/null | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
            log "n8n wurde erfolgreich installiert (Version: $n8n_version)."
            return 0
        else
            error "n8n konnte nicht installiert werden. Bitte installieren Sie n8n manuell."
            return 1
        fi
    fi
    
    return 0
}

# Funktion zum Anzeigen des Fortschritts
show_progress() {
    local step=$1
    local total=$2
    local description=$3
    
    echo -e "${BLUE}[${step}/${total}]${NC} ${description}"
}

# Funktion zum Überprüfen und Installieren von Python-Abhängigkeiten
check_python_dependencies() {
    log "Überprüfe Python-Installation und Abhängigkeiten..."
    
    # Prüfe Python-Version
    if ! command -v python3 &> /dev/null; then
        warn "Python 3 ist nicht installiert. Versuche zu installieren..."
        
        # Erkennen des Betriebssystems und der Paketmanager
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        else
            OS=$(uname -s)
        fi
        
        case $OS in
            ubuntu|debian|linuxmint)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Python 3 mit apt..."
                sudo apt-get update
                sudo apt-get install -y python3 python3-pip python3-venv
                ;;
            fedora|centos|rhel)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Python 3 mit dnf..."
                sudo dnf -y install python3 python3-pip python3-devel
                ;;
            arch|manjaro)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere Python 3 mit pacman..."
                sudo pacman -Sy python python-pip
                ;;
            *)
                error "Nicht unterstütztes Betriebssystem: $OS"
                error "Bitte installieren Sie Python 3 manuell."
                return 1
                ;;
        esac
    fi
    
    # Prüfe Python-Version
    python_version=$(python3 --version 2>&1 | grep -oE "[0-9]+\.[0-9]+\.[0-9]+" | head -1)
    if [ -n "$python_version" ]; then
        log "Python Version: $python_version"
        
        # Vergleiche mit der Mindestversion
        if [ "$(printf '%s\n' "3.6.0" "$python_version" | sort -V | head -n1)" != "3.6.0" ]; then
            log "Python ist ausreichend aktuell."
        else
            warn "Python Version ist älter als 3.6.0. Ein Update wird empfohlen."
        fi
    fi
    
    # Prüfe pip-Installation
    if ! command -v pip3 &> /dev/null; then
        warn "pip3 ist nicht installiert. Versuche zu installieren..."
        
        # Erkennen des Betriebssystems und der Paketmanager
        if [ -f /etc/os-release ]; then
            . /etc/os-release
            OS=$ID
        else
            OS=$(uname -s)
        fi
        
        case $OS in
            ubuntu|debian|linuxmint)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere pip3 mit apt..."
                sudo apt-get update
                sudo apt-get install -y python3-pip
                ;;
            fedora|centos|rhel)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere pip3 mit dnf..."
                sudo dnf -y install python3-pip
                ;;
            arch|manjaro)
                log "Erkanntes Betriebssystem: $OS"
                log "Installiere pip mit pacman..."
                sudo pacman -Sy python-pip
                ;;
            *)
                # Fallback auf get-pip.py
                log "Installiere pip mit get-pip.py..."
                curl -sSL https://bootstrap.pypa.io/get-pip.py -o get-pip.py
                python3 get-pip.py --user
                rm get-pip.py
                ;;
        esac
    fi
    
    # Installiere benötigte Python-Pakete
    log "Installiere benötigte Python-Pakete..."
    pip3 install --user requests pyyaml
    
    return 0
}
