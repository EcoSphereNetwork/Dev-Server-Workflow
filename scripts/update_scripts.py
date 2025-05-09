#!/usr/bin/env python3
"""
Skript zum Aktualisieren aller Shell-Skripte, um die neue gemeinsame Bibliothek zu verwenden.
"""

import os
import re
import sys
from pathlib import Path
import argparse
import logging
import shutil
from datetime import datetime

# Konfiguriere Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('update-scripts')

# Basisverzeichnis
BASE_DIR = Path(__file__).resolve().parent.parent

# Muster für die Erkennung von Shell-Skripten
SHEBANG_PATTERN = re.compile(r'^#!.*(/bin/bash|/bin/sh)')
SOURCE_PATTERN = re.compile(r'source\s+"([^"]+)"')
IMPORT_PATTERN = re.compile(r'import\s+([a-zA-Z0-9_.]+)')

# Neue Header für Shell-Skripte
NEW_SHELL_HEADER = '''#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"

'''

# Neue Header für Python-Skripte
NEW_PYTHON_HEADER = '''#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Füge das Verzeichnis der gemeinsamen Bibliothek zum Pfad hinzu
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR / "scripts" / "common" / "python"))

# Importiere die gemeinsame Bibliothek
from common import (
    setup_logging, ConfigManager, DockerUtils, ProcessManager,
    NetworkUtils, SystemUtils, parse_arguments
)

# Konfiguriere Logging
logger = setup_logging("INFO")

# Lade Konfiguration
config_manager = ConfigManager()
config = config_manager.load_env_file(".env")

'''

def is_shell_script(file_path):
    """
    Überprüfe, ob eine Datei ein Shell-Skript ist.
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        bool: True, wenn die Datei ein Shell-Skript ist, sonst False
    """
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            return bool(SHEBANG_PATTERN.match(first_line))
    except Exception:
        return False

def is_python_script(file_path):
    """
    Überprüfe, ob eine Datei ein Python-Skript ist.
    
    Args:
        file_path: Pfad zur Datei
        
    Returns:
        bool: True, wenn die Datei ein Python-Skript ist, sonst False
    """
    try:
        with open(file_path, 'r') as f:
            first_line = f.readline().strip()
            return first_line.startswith('#!/usr/bin/env python') or first_line.startswith('#!python')
    except Exception:
        return False

def update_shell_script(file_path, dry_run=False):
    """
    Aktualisiere ein Shell-Skript, um die neue gemeinsame Bibliothek zu verwenden.
    
    Args:
        file_path: Pfad zum Shell-Skript
        dry_run: Ob die Änderungen nur angezeigt, aber nicht gespeichert werden sollen
        
    Returns:
        bool: True, wenn das Skript aktualisiert wurde, sonst False
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Überprüfe, ob das Skript bereits die neue Bibliothek verwendet
        if 'source "$BASE_DIR/scripts/common/shell/common.sh"' in content:
            logger.info(f"Skript {file_path} verwendet bereits die neue Bibliothek.")
            return False
        
        # Erstelle ein Backup
        backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if not dry_run:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup erstellt: {backup_path}")
        
        # Ersetze alte Bibliotheksimporte
        new_content = content
        
        # Ersetze alte Logging-Funktionen
        new_content = re.sub(r'echo\s+"([^"]+)"', r'log_info "\1"', new_content)
        new_content = re.sub(r'echo\s+-e\s+"([^"]+)"', r'log_info "\1"', new_content)
        
        # Ersetze alte Bibliotheksimporte
        source_matches = SOURCE_PATTERN.findall(new_content)
        for source in source_matches:
            if 'common' in source or 'mcp_common.sh' in source:
                new_content = new_content.replace(f'source "{source}"', 'source "$BASE_DIR/scripts/common/shell/common.sh"')
        
        # Füge den neuen Header hinzu, wenn er nicht bereits vorhanden ist
        if 'source "$BASE_DIR/scripts/common/shell/common.sh"' not in new_content:
            # Entferne den alten Shebang
            new_content = re.sub(r'^#!.*(/bin/bash|/bin/sh).*\n', '', new_content)
            
            # Füge den neuen Header hinzu
            new_content = NEW_SHELL_HEADER + new_content
        
        if dry_run:
            logger.info(f"Würde {file_path} aktualisieren:")
            logger.info(f"--- Alte Version ---\n{content[:500]}...\n")
            logger.info(f"--- Neue Version ---\n{new_content[:500]}...\n")
        else:
            with open(file_path, 'w') as f:
                f.write(new_content)
            logger.info(f"Skript {file_path} aktualisiert.")
        
        return True
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren von {file_path}: {e}")
        return False

def update_python_script(file_path, dry_run=False):
    """
    Aktualisiere ein Python-Skript, um die neue gemeinsame Bibliothek zu verwenden.
    
    Args:
        file_path: Pfad zum Python-Skript
        dry_run: Ob die Änderungen nur angezeigt, aber nicht gespeichert werden sollen
        
    Returns:
        bool: True, wenn das Skript aktualisiert wurde, sonst False
    """
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        # Überprüfe, ob das Skript bereits die neue Bibliothek verwendet
        if 'from common import' in content:
            logger.info(f"Skript {file_path} verwendet bereits die neue Bibliothek.")
            return False
        
        # Erstelle ein Backup
        backup_path = f"{file_path}.bak.{datetime.now().strftime('%Y%m%d%H%M%S')}"
        if not dry_run:
            shutil.copy2(file_path, backup_path)
            logger.info(f"Backup erstellt: {backup_path}")
        
        # Ersetze alte Bibliotheksimporte
        new_content = content
        
        # Ersetze alte Logging-Funktionen
        new_content = re.sub(r'print\("([^"]+)"\)', r'logger.info("\1")', new_content)
        
        # Ersetze alte Bibliotheksimporte
        import_matches = IMPORT_PATTERN.findall(new_content)
        common_imports = []
        for imp in import_matches:
            if 'config_manager' in imp or 'docker_utils' in imp:
                common_imports.append(imp)
        
        # Füge den neuen Header hinzu, wenn er nicht bereits vorhanden ist
        if 'from common import' not in new_content:
            # Entferne den alten Shebang
            new_content = re.sub(r'^#!.*python.*\n', '', new_content)
            
            # Füge den neuen Header hinzu
            new_content = NEW_PYTHON_HEADER + new_content
        
        if dry_run:
            logger.info(f"Würde {file_path} aktualisieren:")
            logger.info(f"--- Alte Version ---\n{content[:500]}...\n")
            logger.info(f"--- Neue Version ---\n{new_content[:500]}...\n")
        else:
            with open(file_path, 'w') as f:
                f.write(new_content)
            logger.info(f"Skript {file_path} aktualisiert.")
        
        return True
    except Exception as e:
        logger.error(f"Fehler beim Aktualisieren von {file_path}: {e}")
        return False

def find_and_update_scripts(directory, shell=True, python=True, dry_run=False):
    """
    Finde und aktualisiere alle Skripte in einem Verzeichnis.
    
    Args:
        directory: Verzeichnis, in dem gesucht werden soll
        shell: Ob Shell-Skripte aktualisiert werden sollen
        python: Ob Python-Skripte aktualisiert werden sollen
        dry_run: Ob die Änderungen nur angezeigt, aber nicht gespeichert werden sollen
        
    Returns:
        Tuple[int, int]: (Anzahl der aktualisierten Skripte, Anzahl der gefundenen Skripte)
    """
    updated = 0
    found = 0
    
    for root, dirs, files in os.walk(directory):
        # Überspringe versteckte Verzeichnisse und Verzeichnisse mit generierten Dateien
        dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '__pycache__']]
        
        for file in files:
            file_path = os.path.join(root, file)
            
            # Überspringe Backup-Dateien
            if file.endswith('.bak'):
                continue
            
            if shell and file.endswith('.sh') and is_shell_script(file_path):
                found += 1
                if update_shell_script(file_path, dry_run):
                    updated += 1
            
            if python and file.endswith('.py') and is_python_script(file_path):
                found += 1
                if update_python_script(file_path, dry_run):
                    updated += 1
    
    return updated, found

def main():
    """
    Hauptfunktion.
    """
    parser = argparse.ArgumentParser(description='Aktualisiere Skripte, um die neue gemeinsame Bibliothek zu verwenden.')
    parser.add_argument('--directory', '-d', default=str(BASE_DIR), help='Verzeichnis, in dem gesucht werden soll')
    parser.add_argument('--shell-only', action='store_true', help='Nur Shell-Skripte aktualisieren')
    parser.add_argument('--python-only', action='store_true', help='Nur Python-Skripte aktualisieren')
    parser.add_argument('--dry-run', action='store_true', help='Änderungen nur anzeigen, aber nicht speichern')
    parser.add_argument('--verbose', '-v', action='store_true', help='Ausführliche Ausgabe')
    
    args = parser.parse_args()
    
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    shell = not args.python_only
    python = not args.shell_only
    
    logger.info(f"Suche nach Skripten in {args.directory}...")
    logger.info(f"Shell-Skripte: {'Ja' if shell else 'Nein'}")
    logger.info(f"Python-Skripte: {'Ja' if python else 'Nein'}")
    logger.info(f"Dry-Run: {'Ja' if args.dry_run else 'Nein'}")
    
    updated, found = find_and_update_scripts(args.directory, shell, python, args.dry_run)
    
    logger.info(f"Gefundene Skripte: {found}")
    logger.info(f"Aktualisierte Skripte: {updated}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())