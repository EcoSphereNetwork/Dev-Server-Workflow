# Deployment and Operations Guide

This guide provides comprehensive instructions for deploying and operating the Dev-Server-Workflow system in various environments.

## Table of Contents

- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
  - [Docker Installation](#docker-installation)
  - [Direct Installation](#direct-installation)
  - [AppImage Installation](#appimage-installation)
- [Configuration](#configuration)
- [Scaling and Performance Tuning](#scaling-and-performance-tuning)
- [Backup and Recovery](#backup-and-recovery)
- [Monitoring and Alerting](#monitoring-and-alerting)
- [Security Best Practices](#security-best-practices)
- [Deployment Checklists](#deployment-checklists)

## System Requirements

### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 4GB
- **Disk Space**: 10GB
- **Operating System**: Ubuntu 20.04+, Debian 11+, CentOS 8+, or any modern Linux distribution
- **Docker**: Version 20.10.0 or higher (for Docker installation)
- **Python**: Version 3.9 or higher (for direct installation)
- **Node.js**: Version 16.0.0 or higher (for direct installation)

### Recommended Requirements

- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Disk Space**: 20GB+
- **Network**: 100Mbps+ connection
- **Operating System**: Ubuntu 22.04 LTS

### Additional Requirements for Production

- **Load Balancer**: For high-availability setups
- **Database**: External PostgreSQL 13+ for n8n persistence
- **Object Storage**: S3-compatible storage for backups and artifacts
- **Monitoring**: Prometheus and Grafana for system monitoring
- **Logging**: ELK stack or similar for centralized logging

## Installation Methods

### Docker Installation

The Docker installation is the recommended method for most deployments, as it provides a consistent environment and simplifies updates.

#### Prerequisites

1. Install Docker and Docker Compose:

```bash
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.18.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

2. Clone the repository:

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

#### Standard Installation

1. Create and configure the environment file:

```bash
cp .env.example .env
# Edit the .env file with your configuration
nano .env
```

2. Start the containers:

```bash
./docker-start.sh start
```

3. Run the setup script:

```bash
./docker-start.sh setup
```

4. Verify the installation:

```bash
./docker-start.sh status
```

#### Production Installation

For production environments, use the production configuration:

```bash
cp .env.example .env.production
# Edit the .env.production file with your production configuration
nano .env.production

# Start with production configuration
./docker-start.sh start --production --env-file .env.production
```

#### Docker Compose Configuration

The Docker Compose configuration is split into multiple files:

- `docker-compose.yml`: Base configuration for development
- `docker-compose.production.yml`: Production-specific configuration
- `docker-compose.web-ui.yml`: Configuration for the web UI only

You can customize these files to suit your needs.

### Direct Installation

Direct installation is useful for development or when Docker is not available.

#### Prerequisites

1. Install Python 3.9+ and Node.js 16+:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs npm

# CentOS/RHEL
sudo dnf install -y python39 python39-pip nodejs
```

2. Clone the repository:

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

#### Installation Steps

1. Create a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install Python dependencies:

```bash
pip install -r requirements.txt
```

3. Install Node.js dependencies:

```bash
cd frontend
npm install
cd ..
```

4. Create and configure the environment file:

```bash
cp src/env-template .env
# Edit the .env file with your configuration
nano .env
```

5. Run the setup script:

```bash
python setup.py install --env-file .env
```

6. Start the services:

```bash
# Start MCP servers
./start-mcp-servers.sh

# Start web UI
./start-web-ui.sh
```

### AppImage Installation

AppImage installation provides a portable, self-contained application that can be run without installation.

#### Web AppImage

1. Download the latest Web AppImage:

```bash
wget https://github.com/EcoSphereNetwork/Dev-Server-Workflow/releases/latest/download/Dev-Server-Workflow-Web-x86_64.AppImage
```

2. Make it executable:

```bash
chmod +x Dev-Server-Workflow-Web-x86_64.AppImage
```

3. Run the AppImage:

```bash
./Dev-Server-Workflow-Web-x86_64.AppImage
```

#### Electron AppImage

1. Download the latest Electron AppImage:

```bash
wget https://github.com/EcoSphereNetwork/Dev-Server-Workflow/releases/latest/download/Dev-Server-Workflow-Electron-x86_64.AppImage
```

2. Make it executable:

```bash
chmod +x Dev-Server-Workflow-Electron-x86_64.AppImage
```

3. Run the AppImage:

```bash
./Dev-Server-Workflow-Electron-x86_64.AppImage
```

## Configuration

### Environment Variables

The system is configured using environment variables, which can be set in the `.env` file or directly in the environment.

#### Core Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `N8N_HOST` | Hostname for n8n | `localhost` | No |
| `N8N_PORT` | Port for n8n | `5678` | No |
| `N8N_ENCRYPTION_KEY` | Encryption key for n8n | `n8n-encryption-key` | Yes |
| `N8N_BASIC_AUTH_USER` | Username for n8n basic auth | `admin` | No |
| `N8N_BASIC_AUTH_PASSWORD` | Password for n8n basic auth | `password` | Yes |
| `N8N_API_KEY` | API key for n8n | - | Yes |
| `MCP_HUB_PORT` | Port for MCP Hub | `3000` | No |
| `GRAFANA_ADMIN_USER` | Username for Grafana | `admin` | No |
| `GRAFANA_ADMIN_PASSWORD` | Password for Grafana | `admin` | Yes |

#### External Service Configuration

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `GITHUB_API_TOKEN` | GitHub API token | - | No |
| `GITLAB_API_TOKEN` | GitLab API token | - | No |
| `OPENPROJECT_API_KEY` | OpenProject API key | - | No |
| `DISCORD_WEBHOOK_URL` | Discord webhook URL | - | No |
| `LLM_API_KEY` | API key for LLM service | - | No |

### Configuration Files

In addition to environment variables, the system uses several configuration files:

- `config/services.json`: Configuration for external services
- `config/workflows.json`: Configuration for n8n workflows
- `config/monitoring.json`: Configuration for monitoring and alerting
- `docker/prometheus/prometheus.yml`: Prometheus configuration
- `docker/grafana/provisioning/`: Grafana provisioning files

## Scaling and Performance Tuning

### Horizontal Scaling

The system can be horizontally scaled by running multiple instances of the services behind a load balancer.

#### Docker Swarm

1. Initialize a Docker Swarm:

```bash
docker swarm init
```

2. Deploy the stack:

```bash
docker stack deploy -c docker-compose.production.yml dev-server
```

3. Scale services as needed:

```bash
docker service scale dev-server_n8n=3 dev-server_mcp-hub=2
```

#### Kubernetes

1. Apply the Kubernetes manifests:

```bash
kubectl apply -f kubernetes/
```

2. Scale deployments as needed:

```bash
kubectl scale deployment n8n --replicas=3
kubectl scale deployment mcp-hub --replicas=2
```

### Vertical Scaling

Vertical scaling can be achieved by adjusting resource limits in the Docker Compose or Kubernetes configuration.

#### Docker Compose

```yaml
services:
  n8n:
    # ...
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 4G
        reservations:
          cpus: '1'
          memory: 2G
```

#### Kubernetes

```yaml
resources:
  limits:
    cpu: 2
    memory: 4Gi
  requests:
    cpu: 1
    memory: 2Gi
```

### Performance Tuning

#### n8n Performance

- Increase `EXECUTIONS_PROCESS` to `main` for better performance
- Use external PostgreSQL database for better reliability
- Adjust `N8N_METRICS_ENABLED` and `N8N_METRICS_INTERVAL` for monitoring

#### MCP Server Performance

- Adjust `MCP_SERVER_MAX_CONNECTIONS` for higher concurrency
- Set `MCP_SERVER_TIMEOUT` to an appropriate value for your workloads
- Enable `MCP_SERVER_CACHE_ENABLED` for better performance

#### Frontend Performance

- Enable production mode with `VITE_ENV=production`
- Adjust `VITE_API_CACHE_TTL` for API response caching
- Set appropriate `VITE_WEBSOCKET_RECONNECT_INTERVAL` for WebSocket reconnection

## Backup and Recovery

### Backup Strategy

#### Docker Volume Backups

1. Create a backup script:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Stop containers
./docker-start.sh stop

# Backup volumes
docker run --rm -v dev-server-workflow_n8n_data:/source -v $BACKUP_DIR:/backup alpine tar -czf /backup/n8n_data_$DATE.tar.gz -C /source .
docker run --rm -v dev-server-workflow_prometheus_data:/source -v $BACKUP_DIR:/backup alpine tar -czf /backup/prometheus_data_$DATE.tar.gz -C /source .
docker run --rm -v dev-server-workflow_grafana_data:/source -v $BACKUP_DIR:/backup alpine tar -czf /backup/grafana_data_$DATE.tar.gz -C /source .

# Start containers
./docker-start.sh start

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.tar.gz" -type f -mtime +7 -delete
```

2. Make the script executable and add it to cron:

```bash
chmod +x backup.sh
crontab -e
# Add the following line to run daily at 2 AM
0 2 * * * /path/to/backup.sh
```

#### Database Backups

If using an external PostgreSQL database:

```bash
#!/bin/bash
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="n8n"
DB_USER="n8n"
DB_HOST="localhost"

# Backup database
PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -F c -f $BACKUP_DIR/n8n_db_$DATE.dump

# Cleanup old backups (keep last 7 days)
find $BACKUP_DIR -name "*.dump" -type f -mtime +7 -delete
```

### Recovery Procedures

#### Docker Volume Recovery

1. Stop containers:

```bash
./docker-start.sh stop
```

2. Restore volumes:

```bash
docker run --rm -v dev-server-workflow_n8n_data:/target -v /path/to/backups:/backup alpine sh -c "rm -rf /target/* && tar -xzf /backup/n8n_data_20250501_020000.tar.gz -C /target"
docker run --rm -v dev-server-workflow_prometheus_data:/target -v /path/to/backups:/backup alpine sh -c "rm -rf /target/* && tar -xzf /backup/prometheus_data_20250501_020000.tar.gz -C /target"
docker run --rm -v dev-server-workflow_grafana_data:/target -v /path/to/backups:/backup alpine sh -c "rm -rf /target/* && tar -xzf /backup/grafana_data_20250501_020000.tar.gz -C /target"
```

3. Start containers:

```bash
./docker-start.sh start
```

#### Database Recovery

If using an external PostgreSQL database:

```bash
PGPASSWORD=$DB_PASSWORD pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME -c /path/to/backups/n8n_db_20250501_020000.dump
```

## Monitoring and Alerting

### Prometheus and Grafana Setup

The system includes Prometheus for metrics collection and Grafana for visualization.

#### Accessing Monitoring

- Prometheus: http://localhost:9090
- Grafana: http://localhost:3001 (default credentials: admin/admin)

#### Available Dashboards

1. **System Overview**: General system metrics
2. **n8n Workflows**: n8n workflow execution metrics
3. **MCP Servers**: MCP server performance metrics
4. **Docker Containers**: Container resource usage

#### Alert Configuration

Alerts are configured in Prometheus and can be sent to various channels:

1. Edit the alert rules in `docker/prometheus/alert_rules.yml`:

```yaml
groups:
  - name: example
    rules:
      - alert: HighCPUUsage
        expr: system_cpu_usage > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is above 80% for more than 5 minutes"
```

2. Configure alert receivers in `docker/alertmanager/config.yml`:

```yaml
receivers:
  - name: 'email'
    email_configs:
      - to: 'admin@example.com'
  - name: 'slack'
    slack_configs:
      - api_url: 'https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX'
        channel: '#alerts'
```

### Log Management

Logs are collected and centralized using Fluentd, Elasticsearch, and Kibana.

#### Accessing Logs

- Kibana: http://localhost:5601

#### Log Queries

Common log queries:

- Error logs: `log_level:error`
- n8n workflow failures: `service:n8n AND message:*failed*`
- MCP server errors: `service:mcp-* AND log_level:error`

## Security Best Practices

### Network Security

1. Use a reverse proxy (e.g., Nginx) with HTTPS:

```nginx
server {
    listen 443 ssl;
    server_name dev-server.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

2. Configure firewall rules:

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

### Authentication and Authorization

1. Use strong passwords for all services
2. Enable two-factor authentication where available
3. Use API keys with limited permissions
4. Regularly rotate credentials

### Data Protection

1. Enable encryption for sensitive data:
   - Set a strong `N8N_ENCRYPTION_KEY`
   - Use encrypted volumes for persistent data

2. Implement proper backup encryption:

```bash
# Encrypt backup files
gpg --symmetric --cipher-algo AES256 /path/to/backups/n8n_data_20250501_020000.tar.gz
```

### Container Security

1. Run containers with non-root users:

```yaml
services:
  n8n:
    # ...
    user: "1000:1000"
```

2. Use read-only file systems where possible:

```yaml
services:
  n8n:
    # ...
    read_only: true
    tmpfs:
      - /tmp
```

3. Scan container images for vulnerabilities:

```bash
docker scan n8nio/n8n:latest
```

## Deployment Checklists

### Pre-Deployment Checklist

- [ ] System requirements verified
- [ ] Network configuration checked
- [ ] Required ports available
- [ ] Storage capacity sufficient
- [ ] Backup strategy defined
- [ ] Monitoring solution prepared
- [ ] Security measures reviewed

### Deployment Checklist

- [ ] Repository cloned
- [ ] Environment variables configured
- [ ] Docker and Docker Compose installed (for Docker deployment)
- [ ] Python and Node.js installed (for direct deployment)
- [ ] Database prepared (if using external database)
- [ ] Containers started and running
- [ ] Setup script executed successfully
- [ ] Services accessible on expected ports
- [ ] Initial configuration completed

### Post-Deployment Checklist

- [ ] All services running correctly
- [ ] Monitoring and alerting configured
- [ ] Backup system tested
- [ ] Security measures verified
- [ ] Performance baseline established
- [ ] Documentation updated with environment-specific details
- [ ] User access configured
- [ ] Initial workflows tested

### Troubleshooting Common Deployment Issues

#### Container Startup Failures

**Issue**: Containers fail to start or exit immediately.

**Solution**:
1. Check container logs:
   ```bash
   docker logs dev-server-workflow_n8n_1
   ```
2. Verify environment variables:
   ```bash
   docker-compose config
   ```
3. Check for port conflicts:
   ```bash
   netstat -tuln | grep 5678
   ```

#### Network Connectivity Issues

**Issue**: Services cannot communicate with each other.

**Solution**:
1. Check Docker network:
   ```bash
   docker network inspect dev-server-workflow_n8n-network
   ```
2. Verify container DNS resolution:
   ```bash
   docker exec dev-server-workflow_n8n_1 ping mcp-hub
   ```
3. Check for firewall issues:
   ```bash
   sudo ufw status
   ```

#### Database Connection Issues

**Issue**: n8n cannot connect to the database.

**Solution**:
1. Verify database credentials:
   ```bash
   docker exec dev-server-workflow_n8n_1 env | grep DB_
   ```
2. Check database accessibility:
   ```bash
   docker exec dev-server-workflow_n8n_1 nc -zv postgres 5432
   ```
3. Check database logs:
   ```bash
   docker logs dev-server-workflow_postgres_1
   ```