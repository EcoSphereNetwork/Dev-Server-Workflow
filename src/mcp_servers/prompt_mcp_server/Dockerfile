FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* /app/

# Configure poetry to not use a virtual environment
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-dev --no-interaction --no-ansi

# Copy the rest of the application
COPY . /app/

# Create directories
RUN mkdir -p /app/data/templates /app/data/chroma

# Set environment variables
ENV PYTHONPATH=/app
ENV TEMPLATES_DIRECTORY=/app/data/templates
ENV CHROMA_PERSIST_DIRECTORY=/app/data/chroma

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "prompt_mcp_server.main:app", "--host", "0.0.0.0", "--port", "8000"]