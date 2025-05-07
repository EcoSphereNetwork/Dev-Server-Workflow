FROM node:22-alpine

WORKDIR /app

# Installiere notwendige Pakete
RUN apk add --no-cache \
    curl \
    jq \
    bash

# Installiere MCP Inspector
RUN npm install -g @modelcontextprotocol/inspector

# Erstelle Konfigurationsverzeichnis
RUN mkdir -p /app/config

# Kopiere Konfigurationsdateien
COPY ./config.json /app/config/config.json
COPY ./health-check.sh /app/health-check.sh
RUN chmod +x /app/health-check.sh

# Exponiere die Ports für UI und Proxy
EXPOSE 6274 6277

# Gesundheitscheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/health-check.sh

# Starte den MCP Inspector
CMD ["npx", "@modelcontextprotocol/inspector", "--config", "/app/config/config.json"]