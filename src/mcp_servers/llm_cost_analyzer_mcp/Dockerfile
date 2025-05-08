FROM python:3.10-slim

WORKDIR /app

# Installiere Systemabhängigkeiten
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Installiere Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Kopiere Poetry-Konfigurationsdateien
COPY pyproject.toml poetry.lock* /app/

# Konfiguriere Poetry, keine virtuelle Umgebung zu verwenden
RUN poetry config virtualenvs.create false

# Installiere Abhängigkeiten
RUN poetry install --no-dev --no-interaction --no-ansi

# Kopiere den Rest der Anwendung
COPY . /app/

# Setze Umgebungsvariablen
ENV PYTHONPATH=/app
ENV MCP_ENABLED=true
ENV MCP_SERVER_ID=llm-cost-analyzer
ENV MCP_SERVER_NAME="LLM Cost Analyzer"

# Exponiere Port
EXPOSE 8000

# Starte die Anwendung
CMD ["uvicorn", "llm_cost_analyzer_mcp.main:app", "--host", "0.0.0.0", "--port", "8000"]