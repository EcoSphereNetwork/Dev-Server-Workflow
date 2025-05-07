#!/bin/bash

# Dieses Skript korrigiert die Claude Desktop Konfigurationsdatei

CONFIG_DIR="$HOME/.config/Claude"
CONFIG_FILE="$CONFIG_DIR/claude_desktop_config.json"

# Erstelle Verzeichnis, falls es nicht existiert
mkdir -p "$CONFIG_DIR"

# Erstelle eine korrekte Konfigurationsdatei
cat > "$CONFIG_FILE" << 'EOF1'
{
  "mcpServers": {
    "filesystem": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-filesystem"
      ]
    },
    "brave-search": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-brave-search"
      ],
      "env": {
        "BRAVE_API_KEY": ""
      }
    },
    "github": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-github"
      ],
      "env": {
        "GITHUB_TOKEN": ""
      }
    },
    "memory": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-memory"
      ]
    },
    "everything": {
      "command": "npx",
      "args": [
        "-y",
        "@modelcontextprotocol/server-everything"
      ]
    },
    "openhands": {
      "sseUrl": "http://localhost:3000/mcp"
    }
  }
}
EOF1

echo "Claude Desktop Konfigurationsdatei wurde korrigiert."
echo "Bitte starte Claude Desktop neu."
