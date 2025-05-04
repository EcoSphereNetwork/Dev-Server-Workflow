# Dockerfile for n8n Workflow Integration
FROM python:3.10-slim

WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage cache layer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ ./src/
COPY setup.py .
COPY test-setup.py .

# Make scripts executable
RUN chmod +x src/n8n-mcp-server.py
RUN chmod +x setup.py

# Default port for MCP server
EXPOSE 3000

# Start command (can be overridden)
CMD ["python", "src/n8n-mcp-server.py"]
