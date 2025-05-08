FROM python:3.9-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY src/ /app/src/

# Create logs directory
RUN mkdir -p /app/logs

# Set environment variables
ENV PYTHONPATH=/app
ENV MCP_SERVER_PORT=3333
ENV MCP_SERVER_HOST=0.0.0.0

# Expose port
EXPOSE 3333

# Run the MCP server
CMD ["python", "src/mcp_server_enhanced.py"]