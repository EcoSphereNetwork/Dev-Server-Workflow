FROM node:18-alpine

WORKDIR /app

# Installiere Docker CLI
RUN apk add --no-cache docker-cli

# Installiere OpenHands
RUN npm install -g @all-hands/openhands

# Kopiere den MCP-Resolver
COPY ./openhands-resolver-mcp /app/openhands-resolver-mcp

# Installiere den MCP-Resolver
WORKDIR /app/openhands-resolver-mcp
RUN npm install
RUN npm link

# Zurück zum Hauptverzeichnis
WORKDIR /app

# Erstelle Konfigurationsverzeichnis
RUN mkdir -p /app/data

# Erstelle Konfigurationsdatei
RUN echo '{"resolvers": ["openhands-resolver-mcp"]}' > /app/data/config.json

# Exponiere den Port
EXPOSE 8080

# Starte OpenHands
CMD ["openhands", "--port", "8080", "--config", "/app/data/config.json"]