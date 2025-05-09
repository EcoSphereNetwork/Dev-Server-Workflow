#!/bin/bash

# Konfigurationsmanagement-Funktionen für die Dev-Server CLI

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

# Funktion zum Setzen eines Konfigurationswerts
set_config() {
    local file="$1"
    local key="$2"
    local value="$3"
    
    echo -e "${BLUE}=== Setze Konfigurationswert ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    echo -e "${CYAN}Wert:${NC} $value"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if grep -q "^$key=" "$file"; then
        # Schlüssel existiert bereits, aktualisiere den Wert
        sed -i "s|^$key=.*|$key=$value|" "$file"
    else
        # Schlüssel existiert nicht, füge ihn hinzu
        echo "$key=$value" >> "$file"
    fi
    
    echo -e "${GREEN}✅ Konfigurationswert erfolgreich gesetzt${NC}"
}

# Funktion zum Abrufen eines Konfigurationswerts
get_config() {
    local file="$1"
    local key="$2"
    
    echo -e "${BLUE}=== Rufe Konfigurationswert ab ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    local value=$(grep "^$key=" "$file" | cut -d= -f2-)
    
    if [ -z "$value" ]; then
        echo -e "${YELLOW}⚠️ Schlüssel nicht gefunden: $key${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Wert:${NC} $value"
    fi
}

# Funktion zum Auskommentieren eines Konfigurationswerts
comment_config() {
    local file="$1"
    local key="$2"
    
    echo -e "${BLUE}=== Kommentiere Konfigurationswert aus ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if grep -q "^$key=" "$file"; then
        # Schlüssel existiert, kommentiere ihn aus
        sed -i "s|^$key=|#$key=|" "$file"
        echo -e "${GREEN}✅ Konfigurationswert erfolgreich auskommentiert${NC}"
    else
        echo -e "${YELLOW}⚠️ Schlüssel nicht gefunden: $key${NC}"
        return 1
    fi
}

# Funktion zum Einkommentieren eines Konfigurationswerts
uncomment_config() {
    local file="$1"
    local key="$2"
    
    echo -e "${BLUE}=== Kommentiere Konfigurationswert ein ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if grep -q "^#$key=" "$file"; then
        # Schlüssel ist auskommentiert, kommentiere ihn ein
        sed -i "s|^#$key=|$key=|" "$file"
        echo -e "${GREEN}✅ Konfigurationswert erfolgreich einkommentiert${NC}"
    else
        echo -e "${YELLOW}⚠️ Auskommentierter Schlüssel nicht gefunden: $key${NC}"
        return 1
    fi
}

# Funktion zum Setzen eines JSON-Konfigurationswerts
set_json_config() {
    local file="$1"
    local key="$2"
    local value="$3"
    
    echo -e "${BLUE}=== Setze JSON-Konfigurationswert ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    echo -e "${CYAN}Wert:${NC} $value"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq ist nicht installiert. Bitte installieren Sie jq.${NC}"
        return 1
    fi
    
    # Überprüfe, ob die Datei gültiges JSON enthält
    if ! jq . "$file" &> /dev/null; then
        echo -e "${RED}❌ Datei enthält kein gültiges JSON: $file${NC}"
        return 1
    fi
    
    # Setze den Wert
    local temp_file=$(mktemp)
    jq ".$key = $value" "$file" > "$temp_file"
    mv "$temp_file" "$file"
    
    echo -e "${GREEN}✅ JSON-Konfigurationswert erfolgreich gesetzt${NC}"
}

# Funktion zum Abrufen eines JSON-Konfigurationswerts
get_json_config() {
    local file="$1"
    local key="$2"
    
    echo -e "${BLUE}=== Rufe JSON-Konfigurationswert ab ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq ist nicht installiert. Bitte installieren Sie jq.${NC}"
        return 1
    fi
    
    # Überprüfe, ob die Datei gültiges JSON enthält
    if ! jq . "$file" &> /dev/null; then
        echo -e "${RED}❌ Datei enthält kein gültiges JSON: $file${NC}"
        return 1
    fi
    
    # Rufe den Wert ab
    local value=$(jq ".$key" "$file")
    
    if [ "$value" = "null" ]; then
        echo -e "${YELLOW}⚠️ Schlüssel nicht gefunden: $key${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Wert:${NC} $value"
    fi
}

# Funktion zum Setzen eines YAML-Konfigurationswerts
set_yaml_config() {
    local file="$1"
    local key="$2"
    local value="$3"
    
    echo -e "${BLUE}=== Setze YAML-Konfigurationswert ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    echo -e "${CYAN}Wert:${NC} $value"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if ! command -v yq &> /dev/null; then
        echo -e "${RED}❌ yq ist nicht installiert. Bitte installieren Sie yq.${NC}"
        return 1
    fi
    
    # Setze den Wert
    local temp_file=$(mktemp)
    yq eval ".$key = $value" "$file" > "$temp_file"
    mv "$temp_file" "$file"
    
    echo -e "${GREEN}✅ YAML-Konfigurationswert erfolgreich gesetzt${NC}"
}

# Funktion zum Abrufen eines YAML-Konfigurationswerts
get_yaml_config() {
    local file="$1"
    local key="$2"
    
    echo -e "${BLUE}=== Rufe YAML-Konfigurationswert ab ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if ! command -v yq &> /dev/null; then
        echo -e "${RED}❌ yq ist nicht installiert. Bitte installieren Sie yq.${NC}"
        return 1
    fi
    
    # Rufe den Wert ab
    local value=$(yq eval ".$key" "$file")
    
    if [ "$value" = "null" ]; then
        echo -e "${YELLOW}⚠️ Schlüssel nicht gefunden: $key${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Wert:${NC} $value"
    fi
}

# Funktion zum Setzen eines XML-Konfigurationswerts
set_xml_config() {
    local file="$1"
    local xpath="$2"
    local value="$3"
    
    echo -e "${BLUE}=== Setze XML-Konfigurationswert ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}XPath:${NC} $xpath"
    echo -e "${CYAN}Wert:${NC} $value"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if ! command -v xmlstarlet &> /dev/null; then
        echo -e "${RED}❌ xmlstarlet ist nicht installiert. Bitte installieren Sie xmlstarlet.${NC}"
        return 1
    fi
    
    # Setze den Wert
    local temp_file=$(mktemp)
    xmlstarlet ed -L -u "$xpath" -v "$value" "$file" > "$temp_file"
    mv "$temp_file" "$file"
    
    echo -e "${GREEN}✅ XML-Konfigurationswert erfolgreich gesetzt${NC}"
}

# Funktion zum Abrufen eines XML-Konfigurationswerts
get_xml_config() {
    local file="$1"
    local xpath="$2"
    
    echo -e "${BLUE}=== Rufe XML-Konfigurationswert ab ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}XPath:${NC} $xpath"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    if ! command -v xmlstarlet &> /dev/null; then
        echo -e "${RED}❌ xmlstarlet ist nicht installiert. Bitte installieren Sie xmlstarlet.${NC}"
        return 1
    fi
    
    # Rufe den Wert ab
    local value=$(xmlstarlet sel -t -v "$xpath" "$file")
    
    if [ -z "$value" ]; then
        echo -e "${YELLOW}⚠️ XPath nicht gefunden: $xpath${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Wert:${NC} $value"
    fi
}

# Funktion zum Setzen einer Umgebungsvariablen in einer .env-Datei
set_env_config() {
    local file="$1"
    local key="$2"
    local value="$3"
    
    echo -e "${BLUE}=== Setze Umgebungsvariable ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    echo -e "${CYAN}Wert:${NC} $value"
    
    if [ ! -f "$file" ]; then
        # Datei existiert nicht, erstelle sie
        touch "$file"
    fi
    
    if grep -q "^$key=" "$file"; then
        # Schlüssel existiert bereits, aktualisiere den Wert
        sed -i "s|^$key=.*|$key=$value|" "$file"
    else
        # Schlüssel existiert nicht, füge ihn hinzu
        echo "$key=$value" >> "$file"
    fi
    
    echo -e "${GREEN}✅ Umgebungsvariable erfolgreich gesetzt${NC}"
}

# Funktion zum Abrufen einer Umgebungsvariablen aus einer .env-Datei
get_env_config() {
    local file="$1"
    local key="$2"
    
    echo -e "${BLUE}=== Rufe Umgebungsvariable ab ===${NC}"
    echo -e "${CYAN}Datei:${NC} $file"
    echo -e "${CYAN}Schlüssel:${NC} $key"
    
    if [ ! -f "$file" ]; then
        echo -e "${RED}❌ Datei nicht gefunden: $file${NC}"
        return 1
    fi
    
    local value=$(grep "^$key=" "$file" | cut -d= -f2-)
    
    if [ -z "$value" ]; then
        echo -e "${YELLOW}⚠️ Schlüssel nicht gefunden: $key${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Wert:${NC} $value"
    fi
}

# Hauptfunktion
main() {
    local action="$1"
    local file="$2"
    local key="$3"
    local value="$4"
    local extra="$5"
    
    case "$action" in
        "set")
            set_config "$file" "$key" "$value"
            ;;
        "get")
            get_config "$file" "$key"
            ;;
        "comment")
            comment_config "$file" "$key"
            ;;
        "uncomment")
            uncomment_config "$file" "$key"
            ;;
        "set-json")
            set_json_config "$file" "$key" "$value"
            ;;
        "get-json")
            get_json_config "$file" "$key"
            ;;
        "set-yaml")
            set_yaml_config "$file" "$key" "$value"
            ;;
        "get-yaml")
            get_yaml_config "$file" "$key"
            ;;
        "set-xml")
            set_xml_config "$file" "$key" "$value"
            ;;
        "get-xml")
            get_xml_config "$file" "$key"
            ;;
        "set-env")
            set_env_config "$file" "$key" "$value"
            ;;
        "get-env")
            get_env_config "$file" "$key"
            ;;
        *)
            echo -e "${RED}Unbekannte Aktion: $action${NC}"
            echo "Verfügbare Aktionen: set, get, comment, uncomment, set-json, get-json, set-yaml, get-yaml, set-xml, get-xml, set-env, get-env"
            return 1
            ;;
    esac
}

# Führe die Hauptfunktion aus, wenn das Skript direkt ausgeführt wird
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    if [ $# -lt 3 ]; then
        echo -e "${RED}Unvollständige Parameter${NC}"
        echo "Verwendung: $0 <Aktion> <Datei> <Schlüssel> [Wert] [Extra]"
        echo "Verfügbare Aktionen: set, get, comment, uncomment, set-json, get-json, set-yaml, get-yaml, set-xml, get-xml, set-env, get-env"
        exit 1
    fi
    
    main "$@"
fi
