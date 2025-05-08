#!/bin/bash

# Überprüfe, ob die Ollama-MCP-Bridge läuft
if curl -s http://localhost:8000/health > /dev/null; then
    exit 0
else
    exit 1
fi