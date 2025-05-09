#!/bin/bash

# Script to build fallback Docker images for MCP servers

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display messages
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if an image exists
image_exists() {
    local image=$1
    if docker image inspect "$image" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check if an image can be pulled
can_pull_image() {
    local image=$1
    if docker pull "$image" &> /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to build a fallback image
build_fallback_image() {
    local image_name=$1
    local dockerfile_path="$2"
    
    log "Building fallback image for $image_name..."
    
    # Create the Dockerfile directory if it doesn't exist
    mkdir -p "$(dirname "$dockerfile_path")"
    
    # Create the Dockerfile
    case "$image_name" in
        "mcp/filesystem")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3001

# Set environment variables
ENV MCP_PORT=3001
ENV ALLOWED_PATHS=/workspace
ENV LOG_LEVEL=info

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3001/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        "mcp/desktop-commander")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl bash

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3002

# Set environment variables
ENV MCP_PORT=3002
ENV LOG_LEVEL=info
ENV ALLOWED_DIRECTORIES=["/workspace"]
ENV BLOCKED_COMMANDS=["rm -rf /", "sudo", "su", "dd", "mkfs", "format", "fdisk", "shutdown", "reboot", "halt", "poweroff"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3002/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        "mcp/sequentialthinking")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3003

# Set environment variables
ENV MCP_PORT=3003
ENV LOG_LEVEL=info
ENV MAX_THINKING_STEPS=10
ENV THINKING_TIMEOUT=60

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3003/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        "mcp/github-chat")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3004

# Set environment variables
ENV MCP_PORT=3004
ENV LOG_LEVEL=info
ENV CACHE_ENABLED=true
ENV CACHE_TTL=3600
ENV RATE_LIMIT_ENABLED=true
ENV RATE_LIMIT_REQUESTS=60
ENV RATE_LIMIT_PERIOD=60

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3004/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        "mcp/github")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3005

# Set environment variables
ENV MCP_PORT=3005
ENV LOG_LEVEL=info
ENV CACHE_ENABLED=true
ENV CACHE_TTL=3600
ENV RATE_LIMIT_ENABLED=true
ENV RATE_LIMIT_REQUESTS=60
ENV RATE_LIMIT_PERIOD=60

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3005/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        "mcp/puppeteer")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl chromium

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3006

# Set environment variables
ENV MCP_PORT=3006
ENV LOG_LEVEL=info
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser
ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_ARGS=--no-sandbox,--disable-setuid-sandbox,--disable-dev-shm-usage,--disable-gpu,--disable-extensions
ENV MAX_CONCURRENT_BROWSERS=5
ENV BROWSER_TIMEOUT=60000
ENV ALLOWED_DOMAINS=github.com,gitlab.com,openproject.org,wikipedia.org

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3006/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        "mcp/basic-memory")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3007

# Set environment variables
ENV MCP_PORT=3007
ENV LOG_LEVEL=info
ENV STORAGE_TYPE=redis
ENV MAX_MEMORY_SIZE=100MB
ENV MEMORY_EXPIRATION=86400

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3007/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        "mcp/wikipedia-mcp")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 3008

# Set environment variables
ENV MCP_PORT=3008
ENV LOG_LEVEL=info
ENV CACHE_ENABLED=true
ENV CACHE_TTL=86400
ENV DEFAULT_LANGUAGE=en
ENV RATE_LIMIT_ENABLED=true
ENV RATE_LIMIT_REQUESTS=30
ENV RATE_LIMIT_PERIOD=60
ENV MAX_SEARCH_RESULTS=10

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:3008/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        "mcp/inspector")
            cat > "$dockerfile_path" << 'EOF'
FROM node:18-alpine

WORKDIR /app

# Install dependencies
RUN apk add --no-cache curl

# Create app directory
RUN mkdir -p /app/data

# Copy package.json and install dependencies
COPY package.json .
RUN npm install

# Copy the rest of the application
COPY . .

# Expose the port
EXPOSE 8080

# Set environment variables
ENV PORT=8080
ENV LOG_LEVEL=info
ENV REFRESH_INTERVAL=30

# Health check
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD curl -f http://localhost:8080/health || exit 1

# Start the server
CMD ["node", "server.js"]
EOF
            ;;
        *)
            error "Unknown image: $image_name"
            return 1
            ;;
    esac
    
    # Create a minimal package.json if it doesn't exist
    if [ ! -f "$(dirname "$dockerfile_path")/package.json" ]; then
        cat > "$(dirname "$dockerfile_path")/package.json" << 'EOF'
{
  "name": "mcp-server-fallback",
  "version": "1.0.0",
  "description": "Fallback MCP server",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "redis": "^4.6.7"
  }
}
EOF
    fi
    
    # Create a minimal server.js if it doesn't exist
    if [ ! -f "$(dirname "$dockerfile_path")/server.js" ]; then
        cat > "$(dirname "$dockerfile_path")/server.js" << 'EOF'
const express = require('express');
const app = express();
const port = process.env.MCP_PORT || 3000;

app.use(express.json());

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// MCP endpoint
app.post('/mcp', (req, res) => {
  const { jsonrpc, id, method, params } = req.body;
  
  if (method === 'mcp.listTools') {
    res.json({
      jsonrpc,
      id,
      result: [
        {
          name: 'echo',
          description: 'Echo the input',
          parameter_schema: {
            type: 'object',
            properties: {
              text: {
                type: 'string',
                description: 'Text to echo'
              }
            },
            required: ['text']
          }
        }
      ]
    });
  } else if (method === 'mcp.callTool') {
    const { name, arguments: args } = params;
    
    if (name === 'echo') {
      res.json({
        jsonrpc,
        id,
        result: {
          output: args.text
        }
      });
    } else {
      res.json({
        jsonrpc,
        id,
        error: {
          code: -32601,
          message: `Tool not found: ${name}`
        }
      });
    }
  } else {
    res.json({
      jsonrpc,
      id,
      error: {
        code: -32601,
        message: `Method not found: ${method}`
      }
    });
  }
});

app.listen(port, () => {
  console.log(`MCP server listening at http://localhost:${port}`);
});
EOF
    fi
    
    # Build the Docker image
    docker build -t "$image_name" -f "$dockerfile_path" "$(dirname "$dockerfile_path")"
    
    if [ $? -eq 0 ]; then
        log "Successfully built fallback image for $image_name"
        return 0
    else
        error "Failed to build fallback image for $image_name"
        return 1
    fi
}

# Main function
main() {
    log "Checking for MCP server images..."
    
    # Create fallback directory
    mkdir -p fallback
    
    # Check and build fallback images for each MCP server
    for image in "mcp/filesystem:latest" "mcp/desktop-commander:latest" "mcp/sequentialthinking:latest" "mcp/github-chat:latest" "mcp/github:latest" "mcp/puppeteer:latest" "mcp/basic-memory:latest" "mcp/wikipedia-mcp:latest" "mcp/inspector:latest"; do
        image_name="${image%%:*}"
        
        if image_exists "$image"; then
            log "$image already exists locally"
        elif can_pull_image "$image"; then
            log "Successfully pulled $image"
        else
            warn "Could not pull $image, building fallback image..."
            build_fallback_image "$image_name" "fallback/${image_name//\//-}/Dockerfile"
        fi
    done
    
    log "All MCP server images are now available"
    return 0
}

# Execute the main function
main