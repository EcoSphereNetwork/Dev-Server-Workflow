FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source code
COPY . .

# Expose the MCP port
EXPOSE 3002

# Start the MCP server
CMD ["node", "server.js"]