#!/bin/bash

# Überprüfe, ob der MCP Inspector UI-Server läuft
if curl -s http://localhost:6274 > /dev/null; then
    # Überprüfe, ob der MCP Inspector Proxy-Server läuft
    if curl -s http://localhost:6277/health > /dev/null; then
        exit 0
    fi
fi

exit 1