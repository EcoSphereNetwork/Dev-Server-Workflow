#!/bin/bash

# Skript zum Starten der Electron-App für den Dev-Server-Workflow

# Setze Fehlermodus
set -e

# Verzeichnisse
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Farben für Ausgabe
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Hilfsfunktion für Ausgabe
log() {
  echo -e "${GREEN}[START]${NC} $1"
}

warn() {
  echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
  echo -e "${RED}[ERROR]${NC} $1"
  exit 1
}

# Prüfe, ob alle benötigten Tools installiert sind
check_dependencies() {
  log "Prüfe Abhängigkeiten..."
  
  if ! command -v node &> /dev/null; then
    error "Node.js ist nicht installiert. Bitte installieren Sie Node.js."
  fi
  
  if ! command -v npm &> /dev/null; then
    error "npm ist nicht installiert. Bitte installieren Sie npm."
  fi
}

# Installiere Abhängigkeiten, falls nötig
install_dependencies() {
  if [ ! -d "node_modules" ]; then
    log "Installiere Abhängigkeiten..."
    npm install
  else
    log "Abhängigkeiten bereits installiert."
  fi
}

# Starte die Electron-App im Entwicklungsmodus
start_dev_mode() {
  log "Starte Electron-App im Entwicklungsmodus..."
  npm run electron:dev
}

# Starte die Electron-App direkt
start_electron() {
  log "Starte Electron-App..."
  npm run electron:start
}

# Hauptfunktion
main() {
  log "Starte Dev-Server-Workflow Electron-App..."
  
  check_dependencies
  install_dependencies
  
  # Prüfe, ob die App im Entwicklungsmodus gestartet werden soll
  if [ "$1" == "--dev" ]; then
    start_dev_mode
  else
    start_electron
  fi
}

# Führe Hauptfunktion aus
main "$@"