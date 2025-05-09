#!/bin/bash

# Dieses Skript ersetzt alle Vorkommen von "docker compose" durch "docker compose" in allen Dateien

# Setze strikte Fehlerbehandlung
set -euo pipefail

# Farben für die Ausgabe
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Ersetze 'docker compose' durch 'docker compose' in allen Dateien...${NC}"

# Finde alle Dateien, die "docker compose" enthalten
FILES=$(find /workspace/Dev-Server-Workflow -type f -name "*.sh" -o -name "*.md" | xargs grep -l "docker compose" | sort)

# Zähler für geänderte Dateien und Ersetzungen
CHANGED_FILES=0
REPLACEMENTS=0

# Durchlaufe alle Dateien
for FILE in $FILES; do
    # Überspringe Dateien, die nicht existieren oder nicht lesbar sind
    if [ ! -f "$FILE" ] || [ ! -r "$FILE" ]; then
        echo -e "${RED}Datei $FILE existiert nicht oder ist nicht lesbar. Überspringe...${NC}"
        continue
    fi

    # Zähle die Anzahl der Vorkommen von "docker compose" in der Datei
    COUNT=$(grep -c "docker compose" "$FILE" || true)
    
    if [ "$COUNT" -gt 0 ]; then
        echo -e "${YELLOW}Bearbeite $FILE ($COUNT Vorkommen)...${NC}"
        
        # Ersetze "docker compose" durch "docker compose", aber nicht in URLs oder Pfaden
        # Wir verwenden sed mit einem komplexen Muster, um nur eigenständige "docker compose" Befehle zu ersetzen
        
        # Für Linux (GNU sed)
        if sed --version 2>&1 | grep -q "GNU sed"; then
            # Ersetze "docker compose" durch "docker compose", aber nicht in URLs oder Pfaden
            sed -i 's/\(^\|[^[:alnum:]/-]\)docker compose\([^[:alnum:]/-]\|$\)/\1docker compose\2/g' "$FILE"
            
            # Ersetze auch "docker compose" am Anfang der Zeile
            sed -i 's/^docker compose /docker compose /g' "$FILE"
        else
            # Für macOS (BSD sed)
            sed -i '' 's/\(^\|[^[:alnum:]/-]\)docker compose\([^[:alnum:]/-]\|$\)/\1docker compose\2/g' "$FILE"
            
            # Ersetze auch "docker compose" am Anfang der Zeile
            sed -i '' 's/^docker compose /docker compose /g' "$FILE"
        fi
        
        # Zähle die Anzahl der verbleibenden Vorkommen von "docker compose" in der Datei
        REMAINING=$(grep -c "docker compose" "$FILE" || true)
        REPLACED=$((COUNT - REMAINING))
        
        echo -e "${GREEN}$REPLACED Ersetzungen in $FILE durchgeführt.${NC}"
        
        # Aktualisiere die Zähler
        CHANGED_FILES=$((CHANGED_FILES + 1))
        REPLACEMENTS=$((REPLACEMENTS + REPLACED))
    fi
done

echo -e "${GREEN}Fertig! $REPLACEMENTS Ersetzungen in $CHANGED_FILES Dateien durchgeführt.${NC}"