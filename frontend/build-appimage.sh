#!/bin/bash

# Basisverzeichnis
BASE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Lade die gemeinsame Bibliothek
source "$BASE_DIR/scripts/common/shell/common.sh"

# Lade Umgebungsvariablen aus .env-Datei
load_env_file "${BASE_DIR}/.env"


# Skript zum Erstellen eines AppImage für den Dev-Server-Workflow

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
  log_info "${GREEN}[BUILD]${NC} $1"
}

warn() {
  log_info "${YELLOW}[WARN]${NC} $1"
}

error() {
  log_info "${RED}[ERROR]${NC} $1"
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

# Installiere Abhängigkeiten
install_dependencies() {
  log "Installiere Abhängigkeiten..."
  npm install
}

# Baue die React-App
build_react_app() {
  log "Baue React-App..."
  npm run build
}

# Baue das AppImage
build_appimage() {
  log "Baue AppImage..."
  npm run electron:build -- --linux AppImage
}

# Hauptfunktion
main() {
  log "Starte Build-Prozess für Dev-Server-Workflow AppImage..."
  
  check_dependencies
  install_dependencies
  build_react_app
  build_appimage
  
  log "Build abgeschlossen. AppImage befindet sich im Verzeichnis 'dist'."
}

# Führe Hauptfunktion aus
main