FROM node:18-alpine

WORKDIR /app

# Installiere notwendige Pakete
RUN apk add --no-cache \
    curl \
    jq \
    docker-cli \
    bash

# Installiere OpenHands
RUN npm install -g @all-hands/openhands

# Erstelle Verzeichnisse
RUN mkdir -p /app/data /app/resolvers

# Kopiere den MCP-Resolver
COPY ./openhands-resolver-mcp /app/resolvers/openhands-resolver-mcp

# Installiere den MCP-Resolver
WORKDIR /app/resolvers/openhands-resolver-mcp
RUN npm install
RUN npm link

# Zurück zum Hauptverzeichnis
WORKDIR /app

# Kopiere Konfigurationsdateien
COPY ./openhands-config.json /app/data/config.json
COPY ./health-check.sh /app/health-check.sh
RUN chmod +x /app/health-check.sh

# Exponiere den Port
EXPOSE 8080

# Gesundheitscheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/health-check.sh

# Starte OpenHands
CMD ["openhands", "--port", "8080", "--config", "/app/data/config.json"]