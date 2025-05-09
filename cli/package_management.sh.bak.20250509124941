#!/bin/bash

# Paketmanagement-Funktionen für die Dev-Server CLI

# Lade Konfiguration
source "$(dirname "$0")/config.sh"

# Farben für die Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Funktion zum Installieren eines Pakets
install_package() {
    local package="$1"
    local manager="$2"
    local options="$3"
    
    echo -e "${BLUE}=== Installiere Paket ===${NC}"
    echo -e "${CYAN}Paket:${NC} $package"
    echo -e "${CYAN}Manager:${NC} $manager"
    echo -e "${CYAN}Optionen:${NC} $options"
    
    case "$manager" in
        "apt")
            echo -e "${YELLOW}Führe aus: sudo apt-get install -y $package $options${NC}"
            sudo apt-get update
            sudo apt-get install -y $package $options
            ;;
        "pip")
            echo -e "${YELLOW}Führe aus: pip install $package $options${NC}"
            pip install $package $options
            ;;
        "pip3")
            echo -e "${YELLOW}Führe aus: pip3 install $package $options${NC}"
            pip3 install $package $options
            ;;
        "npm")
            echo -e "${YELLOW}Führe aus: npm install $package $options${NC}"
            npm install $package $options
            ;;
        "npx")
            echo -e "${YELLOW}Führe aus: npx $package $options${NC}"
            npx $package $options
            ;;
        "dpkg")
            echo -e "${YELLOW}Führe aus: sudo dpkg -i $package${NC}"
            sudo dpkg -i $package
            ;;
        *)
            echo -e "${RED}Unbekannter Paketmanager: $manager${NC}"
            echo "Verfügbare Paketmanager: apt, pip, pip3, npm, npx, dpkg"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Paket $package erfolgreich installiert${NC}"
    else
        echo -e "${RED}❌ Fehler beim Installieren von Paket $package${NC}"
        return 1
    fi
}

# Funktion zum Deinstallieren eines Pakets
uninstall_package() {
    local package="$1"
    local manager="$2"
    local options="$3"
    
    echo -e "${BLUE}=== Deinstalliere Paket ===${NC}"
    echo -e "${CYAN}Paket:${NC} $package"
    echo -e "${CYAN}Manager:${NC} $manager"
    echo -e "${CYAN}Optionen:${NC} $options"
    
    case "$manager" in
        "apt")
            echo -e "${YELLOW}Führe aus: sudo apt-get remove -y $package $options${NC}"
            sudo apt-get remove -y $package $options
            ;;
        "pip")
            echo -e "${YELLOW}Führe aus: pip uninstall -y $package $options${NC}"
            pip uninstall -y $package $options
            ;;
        "pip3")
            echo -e "${YELLOW}Führe aus: pip3 uninstall -y $package $options${NC}"
            pip3 uninstall -y $package $options
            ;;
        "npm")
            echo -e "${YELLOW}Führe aus: npm uninstall $package $options${NC}"
            npm uninstall $package $options
            ;;
        "dpkg")
            echo -e "${YELLOW}Führe aus: sudo dpkg -r $package${NC}"
            sudo dpkg -r $package
            ;;
        *)
            echo -e "${RED}Unbekannter Paketmanager: $manager${NC}"
            echo "Verfügbare Paketmanager: apt, pip, pip3, npm, dpkg"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Paket $package erfolgreich deinstalliert${NC}"
    else
        echo -e "${RED}❌ Fehler beim Deinstallieren von Paket $package${NC}"
        return 1
    fi
}

# Funktion zum Aktualisieren eines Pakets
update_package() {
    local package="$1"
    local manager="$2"
    local options="$3"
    
    echo -e "${BLUE}=== Aktualisiere Paket ===${NC}"
    echo -e "${CYAN}Paket:${NC} $package"
    echo -e "${CYAN}Manager:${NC} $manager"
    echo -e "${CYAN}Optionen:${NC} $options"
    
    case "$manager" in
        "apt")
            echo -e "${YELLOW}Führe aus: sudo apt-get update && sudo apt-get install --only-upgrade -y $package $options${NC}"
            sudo apt-get update
            sudo apt-get install --only-upgrade -y $package $options
            ;;
        "pip")
            echo -e "${YELLOW}Führe aus: pip install --upgrade $package $options${NC}"
            pip install --upgrade $package $options
            ;;
        "pip3")
            echo -e "${YELLOW}Führe aus: pip3 install --upgrade $package $options${NC}"
            pip3 install --upgrade $package $options
            ;;
        "npm")
            echo -e "${YELLOW}Führe aus: npm update $package $options${NC}"
            npm update $package $options
            ;;
        "dpkg")
            echo -e "${RED}Direkte Aktualisierung mit dpkg nicht möglich. Bitte deinstallieren und neu installieren.${NC}"
            return 1
            ;;
        *)
            echo -e "${RED}Unbekannter Paketmanager: $manager${NC}"
            echo "Verfügbare Paketmanager: apt, pip, pip3, npm, dpkg"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Paket $package erfolgreich aktualisiert${NC}"
    else
        echo -e "${RED}❌ Fehler beim Aktualisieren von Paket $package${NC}"
        return 1
    fi
}

# Funktion zum Aktualisieren aller Pakete
upgrade_package() {
    local manager="$1"
    local options="$2"
    
    echo -e "${BLUE}=== Aktualisiere alle Pakete ===${NC}"
    echo -e "${CYAN}Manager:${NC} $manager"
    echo -e "${CYAN}Optionen:${NC} $options"
    
    case "$manager" in
        "apt")
            echo -e "${YELLOW}Führe aus: sudo apt-get update && sudo apt-get upgrade -y $options${NC}"
            sudo apt-get update
            sudo apt-get upgrade -y $options
            ;;
        "pip")
            echo -e "${YELLOW}Führe aus: pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install --upgrade${NC}"
            pip list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip install --upgrade
            ;;
        "pip3")
            echo -e "${YELLOW}Führe aus: pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install --upgrade${NC}"
            pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install --upgrade
            ;;
        "npm")
            echo -e "${YELLOW}Führe aus: npm update -g $options${NC}"
            npm update -g $options
            ;;
        *)
            echo -e "${RED}Unbekannter Paketmanager: $manager${NC}"
            echo "Verfügbare Paketmanager: apt, pip, pip3, npm"
            return 1
            ;;
    esac
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Alle Pakete erfolgreich aktualisiert${NC}"
    else
        echo -e "${RED}❌ Fehler beim Aktualisieren aller Pakete${NC}"
        return 1
    fi
}

# Funktion zum Überprüfen eines Pakets
check_package() {
    local package="$1"
    local manager="$2"
    
    echo -e "${BLUE}=== Überprüfe Paket ===${NC}"
    echo -e "${CYAN}Paket:${NC} $package"
    echo -e "${CYAN}Manager:${NC} $manager"
    
    case "$manager" in
        "apt")
            echo -e "${YELLOW}Führe aus: dpkg -l | grep $package${NC}"
            if dpkg -l | grep -q "$package"; then
                echo -e "${GREEN}✅ Paket $package ist installiert${NC}"
                dpkg -l | grep "$package"
            else
                echo -e "${RED}❌ Paket $package ist nicht installiert${NC}"
                return 1
            fi
            ;;
        "pip")
            echo -e "${YELLOW}Führe aus: pip show $package${NC}"
            if pip show "$package" &> /dev/null; then
                echo -e "${GREEN}✅ Paket $package ist installiert${NC}"
                pip show "$package"
            else
                echo -e "${RED}❌ Paket $package ist nicht installiert${NC}"
                return 1
            fi
            ;;
        "pip3")
            echo -e "${YELLOW}Führe aus: pip3 show $package${NC}"
            if pip3 show "$package" &> /dev/null; then
                echo -e "${GREEN}✅ Paket $package ist installiert${NC}"
                pip3 show "$package"
            else
                echo -e "${RED}❌ Paket $package ist nicht installiert${NC}"
                return 1
            fi
            ;;
        "npm")
            echo -e "${YELLOW}Führe aus: npm list $package${NC}"
            if npm list "$package" 2>/dev/null | grep -q "$package"; then
                echo -e "${GREEN}✅ Paket $package ist installiert${NC}"
                npm list "$package"
            else
                echo -e "${RED}❌ Paket $package ist nicht installiert${NC}"
                return 1
            fi
            ;;
        "dpkg")
            echo -e "${YELLOW}Führe aus: dpkg -l | grep $package${NC}"
            if dpkg -l | grep -q "$package"; then
                echo -e "${GREEN}✅ Paket $package ist installiert${NC}"
                dpkg -l | grep "$package"
            else
                echo -e "${RED}❌ Paket $package ist nicht installiert${NC}"
                return 1
            fi
            ;;
        *)
            echo -e "${RED}Unbekannter Paketmanager: $manager${NC}"
            echo "Verfügbare Paketmanager: apt, pip, pip3, npm, dpkg"
            return 1
            ;;
    esac
}

# Hauptfunktion
main() {
    local action="$1"
    local package="$2"
    local manager="$3"
    shift 3
    local options="$@"
    
    case "$action" in
        "install")
            install_package "$package" "$manager" "$options"
            ;;
        "uninstall")
            uninstall_package "$package" "$manager" "$options"
            ;;
        "update")
            update_package "$package" "$manager" "$options"
            ;;
        "upgrade")
            upgrade_package "$manager" "$options"
            ;;
        "check")
            check_package "$package" "$manager"
            ;;
        *)
            echo -e "${RED}Unbekannte Aktion: $action${NC}"
            echo "Verfügbare Aktionen: install, uninstall, update, upgrade, check"
            return 1
            ;;
    esac
}

# Führe die Hauptfunktion aus, wenn das Skript direkt ausgeführt wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -lt 3 ]; then
        echo -e "${RED}Unvollständige Parameter${NC}"
        echo "Verwendung: $0 <Aktion> <Paket> <Manager> [Optionen]"
        echo "Verfügbare Aktionen: install, uninstall, update, upgrade, check"
        echo "Verfügbare Paketmanager: apt, pip, pip3, npm, npx, dpkg"
        exit 1
    fi
    
    main "$@"
fi
