#!/bin/bash

# Überprüfe, ob der MCP-Server läuft
if curl -s http://localhost:3015/health > /dev/null; then
    exit 0
else
    exit 1
fi