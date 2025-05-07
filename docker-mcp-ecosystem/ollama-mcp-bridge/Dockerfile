FROM node:18-alpine

WORKDIR /app

# Installiere notwendige Pakete
RUN apk add --no-cache \
    curl \
    jq \
    bash

# Kopiere package.json und package-lock.json
COPY package*.json ./

# Installiere Abhängigkeiten
RUN npm ci --only=production

# Kopiere den Quellcode
COPY . .

# Kopiere Gesundheitscheck-Skript
COPY ./health-check.sh /app/health-check.sh
RUN chmod +x /app/health-check.sh

# Exponiere den MCP-Port
EXPOSE 3015

# Gesundheitscheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD /app/health-check.sh

# Starte den MCP-Server
CMD ["node", "server.js"]