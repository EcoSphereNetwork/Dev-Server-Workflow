#!/bin/bash

SEARCH_DIR="."
SEARCH_PATTERN="src.core.config_manager"
NEW_IMPORT="from src.common.config_manager import ConfigManager, get_config_manager"

echo "🔍 Suche nach allen Python-Dateien mit Import von '$SEARCH_PATTERN'..."

FILES=$(grep -rl "$SEARCH_PATTERN" "$SEARCH_DIR" --include="*.py")

if [ -z "$FILES" ]; then
    echo "✅ Keine Dateien mit '$SEARCH_PATTERN' gefunden."
    exit 0
fi

echo "⚠️  Dateien mit verdächtigen Importen:"
echo "$FILES"
echo

# Bearbeite jede gefundene Datei
for FILE in $FILES; do
    echo "✏️  Bearbeite: $FILE"

    cp "$FILE" "$FILE.bak"  # Backup

    # Zeilenweise durchgehen, Import ersetzen, falls vorhanden
    awk -v new_import="$NEW_IMPORT" '
        BEGIN { replaced=0 }
        {
            if ($0 ~ /from[[:space:]]+src\.core\.config_manager[[:space:]]+import/) {
                print new_import
                replaced=1
            } else {
                print $0
            }
        }
        END {
            if (replaced) {
                print "✅ Import ersetzt."
            } else {
                print "ℹ️  Kein passender Import in Datei gefunden."
            }
        }
    ' "$FILE.bak" > "$FILE"

done

echo
echo "🚀 Alle relevanten Dateien wurden bearbeitet."
