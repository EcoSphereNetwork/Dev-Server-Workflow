FROM node:18-alpine

WORKDIR /app

# Kopiere package.json und package-lock.json
COPY package*.json ./

# Installiere Abhängigkeiten
RUN npm ci --only=production

# Kopiere den Quellcode
COPY . .

# Exponiere den MCP-Port
EXPOSE 3015

# Starte den MCP-Server
CMD ["node", "server.js"]