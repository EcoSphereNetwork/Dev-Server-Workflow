#!/bin/bash

# Skript zum Starten der MCP-Server

# Konfiguration
N8N_URL=${N8N_URL:-"http://localhost:5678"}
N8N_API_KEY=${N8N_API_KEY:-"test-api-key"}
MCP_HTTP_PORT=${MCP_HTTP_PORT:-3456}
LOG_DIR="/tmp/mcp-logs"

# Erstelle Log-Verzeichnis
mkdir -p "$LOG_DIR"

# Funktion zum Starten eines MCP-Servers
start_mcp_server() {
    local name=$1
    local command=$2
    local args=$3
    local log_file="$LOG_DIR/$name.log"
    
    echo "Starte MCP-Server: $name"
    echo "Befehl: $command $args"
    echo "Log-Datei: $log_file"
    
    # Starte den Server im Hintergrund
    eval "$command $args > $log_file 2>&1 &"
    local pid=$!
    
    echo "PID: $pid"
    echo "$pid" > "$LOG_DIR/$name.pid"
    
    # Warte kurz, um zu prüfen, ob der Server gestartet ist
    sleep 2
    if ! kill -0 $pid 2>/dev/null; then
        echo "Fehler: Server $name konnte nicht gestartet werden"
        cat "$log_file"
        return 1
    fi
    
    echo "Server $name erfolgreich gestartet"
    return 0
}

# Funktion zum Stoppen eines MCP-Servers
stop_mcp_server() {
    local name=$1
    local pid_file="$LOG_DIR/$name.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        echo "Stoppe MCP-Server: $name (PID: $pid)"
        
        # Sende SIGTERM an den Prozess
        kill $pid 2>/dev/null || true
        
        # Warte kurz und prüfe, ob der Prozess beendet ist
        sleep 2
        if kill -0 $pid 2>/dev/null; then
            echo "Server reagiert nicht, sende SIGKILL"
            kill -9 $pid 2>/dev/null || true
        fi
        
        rm -f "$pid_file"
        echo "Server $name gestoppt"
    else
        echo "Kein PID-File für Server $name gefunden"
    fi
}

# Funktion zum Stoppen aller MCP-Server
stop_all_servers() {
    echo "Stoppe alle MCP-Server..."
    
    for pid_file in "$LOG_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            local name=$(basename "$pid_file" .pid)
            stop_mcp_server "$name"
        fi
    done
    
    echo "Alle Server gestoppt"
}

# Registriere Signal-Handler
trap stop_all_servers EXIT

# Stoppe alle laufenden Server
stop_all_servers

# Starte den n8n MCP-Server im HTTP-Modus
start_mcp_server "n8n-mcp" "python" "/workspace/improved-n8n-mcp-server.py --mode http --http-port $MCP_HTTP_PORT --n8n-url $N8N_URL --api-key $N8N_API_KEY"

# Installiere und starte den Filesystem MCP-Server
if ! command -v npx &> /dev/null; then
    echo "npx nicht gefunden, installiere @modelcontextprotocol/server-filesystem..."
    npm install -g @modelcontextprotocol/server-filesystem
fi

# Starte den Filesystem MCP-Server
start_mcp_server "filesystem-mcp" "npx" "-y @modelcontextprotocol/server-filesystem --port 3457"

echo "Alle MCP-Server gestartet"
echo "n8n MCP-Server: http://localhost:$MCP_HTTP_PORT/mcp"
echo "Filesystem MCP-Server: stdio (PID in $LOG_DIR/filesystem-mcp.pid)"
echo ""
echo "Drücke STRG+C, um alle Server zu beenden"

# Halte das Skript am Laufen
while true; do
    sleep 1
done
