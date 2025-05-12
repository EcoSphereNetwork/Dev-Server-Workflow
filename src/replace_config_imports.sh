#!/bin/bash

SEARCH_DIR="."
OLD_IMPORT="from core.config_manager import ConfigManager, get_config_manager"
NEW_IMPORT="from common.config_manager import ConfigManager, get_config_manager"

echo "🔍 Durchsuche Python-Dateien in '$SEARCH_DIR' nach veralteten Importen..."

# Finde alle betroffenen Dateien
FILES=$(grep -rl "$OLD_IMPORT" "$SEARCH_DIR" --include="*.py")

if [ -z "$FILES" ]; then
    echo "✅ Keine Dateien mit dem alten Import gefunden."
    exit 0
fi

echo "⚠️  Veralteter Import gefunden in:"
echo "$FILES"
echo

# Jede Datei bearbeiten
for FILE in $FILES; do
    echo "✏️  Bearbeite: $FILE"

    # Backup erstellen
    cp "$FILE" "$FILE.bak"

    # Ersetze die Import-Zeile
    sed -i "s|$OLD_IMPORT|$NEW_IMPORT|g" "$FILE"

    echo "✅ Ersetzt in $FILE (Backup: $FILE.bak)"
done

echo
echo "🚀 Fertig! Alle veralteten Importe wurden ersetzt."
