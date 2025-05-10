# Troubleshooting and Maintenance Guide

This guide provides comprehensive troubleshooting procedures and maintenance instructions for the Dev-Server-Workflow system.

## Table of Contents

- [Common Error Scenarios](#common-error-scenarios)
- [Diagnostic Procedures](#diagnostic-procedures)
- [Log Analysis Techniques](#log-analysis-techniques)
- [Maintenance Procedures](#maintenance-procedures)
- [Disaster Recovery](#disaster-recovery)
- [Troubleshooting Decision Trees](#troubleshooting-decision-trees)
- [Maintenance Checklists](#maintenance-checklists)

## Common Error Scenarios

### Docker Container Issues

#### Container Fails to Start

**Error Message:**
```
Error response from daemon: driver failed programming external connectivity on endpoint dev-server-workflow_n8n_1: Error starting userland proxy: listen tcp4 0.0.0.0:5678: bind: address already in use
```

**Solution:**
1. Check for processes using the port:
   ```bash
   sudo lsof -i :5678
   ```
2. Stop the conflicting process or change the port in `.env` file:
   ```
   N8N_PORT=5679
   ```
3. Restart the container:
   ```bash
   ./docker-start.sh restart
   ```

#### Container Exits Immediately

**Error Message:**
```
Container dev-server-workflow_mcp-hub_1 exited with code 1
```

**Solution:**
1. Check container logs:
   ```bash
   docker logs dev-server-workflow_mcp-hub_1
   ```
2. Verify environment variables:
   ```bash
   docker-compose config
   ```
3. Check for missing dependencies or configuration issues in the logs and fix them.

### n8n Workflow Issues

#### Workflow Execution Fails

**Error Message:**
```
Workflow execution failed: Error: getaddrinfo ENOTFOUND github-api.example.com
```

**Solution:**
1. Check the API endpoint configuration:
   ```bash
   docker exec -it dev-server-workflow_n8n_1 bash
   cat /home/node/.n8n/workflows/workflow_123.json | grep github-api
   ```
2. Verify network connectivity:
   ```bash
   docker exec -it dev-server-workflow_n8n_1 curl -v github-api.example.com
   ```
3. Update the workflow with the correct API endpoint.

#### Webhook Trigger Not Working

**Error Message:**
```
Webhook call failed: Error: Request failed with status code 404
```

**Solution:**
1. Verify the webhook URL:
   ```bash
   echo "http://${N8N_HOST}:${N8N_PORT}/webhook/path"
   ```
2. Check n8n logs for webhook registration:
   ```bash
   docker logs dev-server-workflow_n8n_1 | grep webhook
   ```
3. Ensure the webhook is properly configured in the workflow.
4. Check if n8n is accessible from the external service.

### MCP Server Issues

#### MCP Server Connection Failure

**Error Message:**
```
Failed to connect to MCP server: Error: connect ECONNREFUSED 127.0.0.1:3334
```

**Solution:**
1. Check if the MCP server is running:
   ```bash
   docker ps | grep docker-mcp
   ```
2. Verify network configuration:
   ```bash
   docker inspect dev-server-workflow_docker-mcp_1 | grep IPAddress
   ```
3. Check MCP server logs:
   ```bash
   docker logs dev-server-workflow_docker-mcp_1
   ```
4. Restart the MCP server:
   ```bash
   docker restart dev-server-workflow_docker-mcp_1
   ```

#### MCP Tool Execution Failure

**Error Message:**
```
Tool execution failed: Error: Authentication failed
```

**Solution:**
1. Check API key configuration:
   ```bash
   docker exec -it dev-server-workflow_mcp-hub_1 env | grep API_KEY
   ```
2. Verify the tool permissions:
   ```bash
   curl -H "X-API-Key: your-api-key" http://localhost:3000/api/v1/tools/permissions
   ```
3. Update the API key or permissions as needed.

### Frontend Issues

#### Web UI Not Loading

**Error Message:**
```
Failed to load resource: net::ERR_CONNECTION_REFUSED
```

**Solution:**
1. Check if the frontend server is running:
   ```bash
   docker ps | grep frontend
   ```
2. Verify the frontend configuration:
   ```bash
   docker exec -it dev-server-workflow_frontend_1 cat /app/.env
   ```
3. Check browser console for specific errors.
4. Restart the frontend service:
   ```bash
   docker restart dev-server-workflow_frontend_1
   ```

#### Authentication Failure

**Error Message:**
```
Authentication failed: Invalid credentials
```

**Solution:**
1. Verify user credentials:
   ```bash
   # Check if the user exists
   docker exec -it dev-server-workflow_n8n_1 n8n user list
   ```
2. Reset the user password:
   ```bash
   docker exec -it dev-server-workflow_n8n_1 n8n user update --email admin@example.com --password newpassword
   ```
3. Check authentication configuration:
   ```bash
   docker exec -it dev-server-workflow_n8n_1 env | grep AUTH
   ```

## Diagnostic Procedures

### System Health Check

Run a comprehensive health check of all components:

```bash
#!/bin/bash

echo "=== System Health Check ==="
echo ""

# Check Docker status
echo "Docker Status:"
docker info | grep "Server Version\|Containers\|Images"
echo ""

# Check container status
echo "Container Status:"
docker ps -a
echo ""

# Check disk space
echo "Disk Space:"
df -h
echo ""

# Check memory usage
echo "Memory Usage:"
free -h
echo ""

# Check CPU load
echo "CPU Load:"
uptime
echo ""

# Check n8n status
echo "n8n Status:"
curl -s http://localhost:5678/healthz || echo "n8n not responding"
echo ""

# Check MCP Hub status
echo "MCP Hub Status:"
curl -s http://localhost:3000/api/v1/health || echo "MCP Hub not responding"
echo ""

# Check Docker MCP status
echo "Docker MCP Status:"
curl -s http://localhost:3334/api/v1/health || echo "Docker MCP not responding"
echo ""

# Check n8n MCP status
echo "n8n MCP Status:"
curl -s http://localhost:3335/api/v1/health || echo "n8n MCP not responding"
echo ""

# Check Prometheus status
echo "Prometheus Status:"
curl -s http://localhost:9090/-/healthy || echo "Prometheus not responding"
echo ""

# Check Grafana status
echo "Grafana Status:"
curl -s http://localhost:3001/api/health || echo "Grafana not responding"
echo ""

echo "=== Health Check Complete ==="
```

Save this script as `health_check.sh`, make it executable with `chmod +x health_check.sh`, and run it to get a comprehensive health report.

### Network Diagnostics

Diagnose network connectivity issues between components:

```bash
#!/bin/bash

echo "=== Network Diagnostics ==="
echo ""

# Get container IPs
N8N_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dev-server-workflow_n8n_1)
MCP_HUB_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dev-server-workflow_mcp-hub_1)
DOCKER_MCP_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dev-server-workflow_docker-mcp_1)
N8N_MCP_IP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' dev-server-workflow_n8n-mcp_1)

echo "Container IPs:"
echo "n8n: $N8N_IP"
echo "MCP Hub: $MCP_HUB_IP"
echo "Docker MCP: $DOCKER_MCP_IP"
echo "n8n MCP: $N8N_MCP_IP"
echo ""

# Test connectivity from n8n to MCP Hub
echo "Testing n8n to MCP Hub connectivity:"
docker exec dev-server-workflow_n8n_1 curl -s http://$MCP_HUB_IP:3000/api/v1/health || echo "Connection failed"
echo ""

# Test connectivity from MCP Hub to Docker MCP
echo "Testing MCP Hub to Docker MCP connectivity:"
docker exec dev-server-workflow_mcp-hub_1 curl -s http://$DOCKER_MCP_IP:3334/api/v1/health || echo "Connection failed"
echo ""

# Test connectivity from MCP Hub to n8n MCP
echo "Testing MCP Hub to n8n MCP connectivity:"
docker exec dev-server-workflow_mcp-hub_1 curl -s http://$N8N_MCP_IP:3335/api/v1/health || echo "Connection failed"
echo ""

# Test connectivity from n8n to external services
echo "Testing n8n to external services:"
docker exec dev-server-workflow_n8n_1 curl -s https://api.github.com/zen || echo "GitHub API connection failed"
echo ""

echo "=== Network Diagnostics Complete ==="
```

Save this script as `network_diagnostics.sh`, make it executable, and run it to diagnose network connectivity issues.

### Database Diagnostics

If using an external PostgreSQL database for n8n:

```bash
#!/bin/bash

echo "=== Database Diagnostics ==="
echo ""

# Get database credentials from environment
DB_HOST=$(docker exec dev-server-workflow_n8n_1 env | grep DB_POSTGRESDB_HOST | cut -d= -f2)
DB_PORT=$(docker exec dev-server-workflow_n8n_1 env | grep DB_POSTGRESDB_PORT | cut -d= -f2)
DB_USER=$(docker exec dev-server-workflow_n8n_1 env | grep DB_POSTGRESDB_USER | cut -d= -f2)
DB_DATABASE=$(docker exec dev-server-workflow_n8n_1 env | grep DB_POSTGRESDB_DATABASE | cut -d= -f2)

echo "Database Configuration:"
echo "Host: $DB_HOST"
echo "Port: $DB_PORT"
echo "User: $DB_USER"
echo "Database: $DB_DATABASE"
echo ""

# Test database connection
echo "Testing database connection:"
docker exec dev-server-workflow_n8n_1 pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER || echo "Connection failed"
echo ""

# Check database size
echo "Database Size:"
docker exec dev-server-workflow_n8n_1 psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_DATABASE -c "SELECT pg_size_pretty(pg_database_size('$DB_DATABASE'));" || echo "Query failed"
echo ""

# Check table sizes
echo "Table Sizes:"
docker exec dev-server-workflow_n8n_1 psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_DATABASE -c "SELECT table_name, pg_size_pretty(pg_total_relation_size(table_name::text)) AS size FROM information_schema.tables WHERE table_schema='public' ORDER BY pg_total_relation_size(table_name::text) DESC LIMIT 10;" || echo "Query failed"
echo ""

# Check for long-running queries
echo "Long-running Queries:"
docker exec dev-server-workflow_n8n_1 psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_DATABASE -c "SELECT pid, now() - pg_stat_activity.query_start AS duration, query FROM pg_stat_activity WHERE state = 'active' AND now() - pg_stat_activity.query_start > interval '5 minutes';" || echo "Query failed"
echo ""

echo "=== Database Diagnostics Complete ==="
```

### Log Collection

Collect logs from all components for analysis:

```bash
#!/bin/bash

LOGS_DIR="./logs/$(date +%Y%m%d_%H%M%S)"
mkdir -p $LOGS_DIR

echo "Collecting logs to $LOGS_DIR..."

# Collect Docker logs
docker logs dev-server-workflow_n8n_1 > $LOGS_DIR/n8n.log 2>&1
docker logs dev-server-workflow_mcp-hub_1 > $LOGS_DIR/mcp-hub.log 2>&1
docker logs dev-server-workflow_docker-mcp_1 > $LOGS_DIR/docker-mcp.log 2>&1
docker logs dev-server-workflow_n8n-mcp_1 > $LOGS_DIR/n8n-mcp.log 2>&1
docker logs dev-server-workflow_prometheus_1 > $LOGS_DIR/prometheus.log 2>&1
docker logs dev-server-workflow_grafana_1 > $LOGS_DIR/grafana.log 2>&1
docker logs dev-server-workflow_prometheus-exporter_1 > $LOGS_DIR/prometheus-exporter.log 2>&1

# Collect system logs
journalctl -u docker.service --since "24 hours ago" > $LOGS_DIR/docker-service.log 2>&1
dmesg > $LOGS_DIR/dmesg.log 2>&1

# Collect container information
docker ps -a > $LOGS_DIR/docker-ps.log 2>&1
docker stats --no-stream > $LOGS_DIR/docker-stats.log 2>&1
docker network inspect dev-server-workflow_n8n-network > $LOGS_DIR/docker-network.log 2>&1

# Collect system information
top -b -n 1 > $LOGS_DIR/top.log 2>&1
free -h > $LOGS_DIR/memory.log 2>&1
df -h > $LOGS_DIR/disk.log 2>&1
netstat -tuln > $LOGS_DIR/netstat.log 2>&1

# Create a tar archive
tar -czf logs_$(date +%Y%m%d_%H%M%S).tar.gz -C $(dirname $LOGS_DIR) $(basename $LOGS_DIR)

echo "Logs collected and archived to logs_$(date +%Y%m%d_%H%M%S).tar.gz"
```

Save this script as `collect_logs.sh`, make it executable, and run it to collect logs from all components.

## Log Analysis Techniques

### Common Log Patterns

#### n8n Logs

**Workflow Execution:**
```
[2025-05-01 12:34:56.789] [INFO] - Workflow execution started for "GitHub to OpenProject" with ID 123
[2025-05-01 12:34:57.123] [INFO] - Workflow execution finished for "GitHub to OpenProject" with ID 123
```

**Error Pattern:**
```
[2025-05-01 12:34:56.789] [ERROR] - Workflow execution failed for "GitHub to OpenProject" with ID 123: Error: getaddrinfo ENOTFOUND github-api.example.com
```

**Authentication Issue:**
```
[2025-05-01 12:34:56.789] [ERROR] - Authentication failed for user admin@example.com: Invalid credentials
```

#### MCP Hub Logs

**Server Registration:**
```
[2025-05-01 12:34:56.789] [INFO] - MCP server registered: docker-mcp (http://docker-mcp:3334)
```

**Tool Execution:**
```
[2025-05-01 12:34:56.789] [INFO] - Tool execution started: create-container on docker-mcp
[2025-05-01 12:34:57.123] [INFO] - Tool execution completed: create-container on docker-mcp
```

**Error Pattern:**
```
[2025-05-01 12:34:56.789] [ERROR] - Failed to connect to MCP server docker-mcp: Error: connect ECONNREFUSED 172.18.0.3:3334
```

#### Docker MCP Logs

**Container Operation:**
```
[2025-05-01 12:34:56.789] [INFO] - Container created: web-server (abc123def456)
[2025-05-01 12:34:57.123] [INFO] - Container started: web-server (abc123def456)
```

**Error Pattern:**
```
[2025-05-01 12:34:56.789] [ERROR] - Failed to create container: Error: No such image: nginx:nonexistent
```

### Log Analysis Tools

#### Using grep for Log Analysis

Search for errors across all logs:

```bash
grep -r "ERROR" ./logs/
```

Find all occurrences of a specific error:

```bash
grep -r "ECONNREFUSED" ./logs/
```

Count occurrences of different error types:

```bash
grep -r "ERROR" ./logs/ | awk -F: '{print $3}' | sort | uniq -c | sort -nr
```

#### Using awk for Log Analysis

Extract workflow execution times:

```bash
awk '/Workflow execution started/ {start[$8]=$1" "$2} /Workflow execution finished/ {if (start[$8]) print $8, "Duration:", $1" "$2, "-", start[$8]}' ./logs/n8n.log
```

Calculate average execution time:

```bash
awk '/Workflow execution started/ {start[$8]=$1" "$2; gsub(/[\[\]]/,"",$1); gsub(/:/,"",$2); start_time[$8]=mktime(substr($1,1,4)" "substr($1,6,2)" "substr($1,9,2)" "substr($2,1,2)" "substr($2,3,2)" "substr($2,5,2))} /Workflow execution finished/ {if (start[$8]) {gsub(/[\[\]]/,"",$1); gsub(/:/,"",$2); end_time=mktime(substr($1,1,4)" "substr($1,6,2)" "substr($1,9,2)" "substr($2,1,2)" "substr($2,3,2)" "substr($2,5,2)); duration=end_time-start_time[$8]; sum+=duration; count++}} END {if (count>0) print "Average execution time:", sum/count, "seconds"}' ./logs/n8n.log
```

#### Using jq for JSON Log Analysis

If logs are in JSON format:

```bash
cat ./logs/mcp-hub.log | jq 'select(.level=="error")'
```

Count errors by type:

```bash
cat ./logs/mcp-hub.log | jq 'select(.level=="error") | .message' | sort | uniq -c | sort -nr
```

Extract specific fields:

```bash
cat ./logs/mcp-hub.log | jq 'select(.level=="info" and .message | contains("Tool execution")) | {timestamp: .timestamp, tool: .tool, server: .server, duration: .duration}'
```

## Maintenance Procedures

### Regular Maintenance Tasks

#### Weekly Maintenance

1. **Update Docker Images:**
   ```bash
   # Pull latest images
   docker-compose pull
   
   # Restart containers with new images
   ./docker-start.sh restart
   ```

2. **Check for Updates:**
   ```bash
   # Check for repository updates
   git fetch
   git log HEAD..origin/main --oneline
   
   # Apply updates if available
   git pull
   ./docker-start.sh restart
   ```

3. **Prune Docker Resources:**
   ```bash
   # Remove unused containers, networks, and images
   docker system prune -f
   ```

4. **Check Disk Space:**
   ```bash
   # Check disk usage
   df -h
   
   # Find large files
   find /var/lib/docker -type f -size +100M -exec ls -lh {} \;
   ```

5. **Review Logs:**
   ```bash
   # Check for errors in logs
   ./docker-start.sh logs | grep -i error
   ```

#### Monthly Maintenance

1. **Database Maintenance:**
   ```bash
   # Vacuum and analyze database
   docker exec -it dev-server-workflow_n8n_1 psql -h $DB_HOST -p $DB_PORT -U $DB_USER -d $DB_DATABASE -c "VACUUM ANALYZE;"
   ```

2. **Backup Verification:**
   ```bash
   # Verify backup integrity
   tar -tzf /path/to/backups/n8n_data_20250501_020000.tar.gz > /dev/null
   ```

3. **Security Updates:**
   ```bash
   # Update host system
   sudo apt update && sudo apt upgrade -y
   
   # Restart Docker
   sudo systemctl restart docker
   ```

4. **Performance Review:**
   ```bash
   # Generate performance report
   ./scripts/generate_performance_report.sh
   ```

5. **Workflow Optimization:**
   ```bash
   # Identify slow workflows
   docker exec -it dev-server-workflow_n8n_1 n8n execution:list --limit 100 --sortField finished --sortDirection desc
   ```

### System Updates

#### Updating n8n

1. Update the n8n version in `docker-compose.yml`:
   ```yaml
   n8n:
     image: n8nio/n8n:0.219.0  # Update to the desired version
   ```

2. Pull the new image and restart:
   ```bash
   docker-compose pull n8n
   docker-compose up -d n8n
   ```

3. Verify the update:
   ```bash
   docker exec -it dev-server-workflow_n8n_1 n8n --version
   ```

#### Updating MCP Servers

1. Rebuild the MCP server images:
   ```bash
   docker-compose build mcp-hub docker-mcp n8n-mcp
   ```

2. Restart the services:
   ```bash
   docker-compose up -d mcp-hub docker-mcp n8n-mcp
   ```

3. Verify the update:
   ```bash
   curl -s http://localhost:3000/api/v1/health | jq .version
   ```

### Database Migrations

If using an external PostgreSQL database for n8n:

1. Backup the database:
   ```bash
   PGPASSWORD=$DB_PASSWORD pg_dump -h $DB_HOST -U $DB_USER -d $DB_NAME -F c -f n8n_db_before_migration.dump
   ```

2. Stop n8n:
   ```bash
   docker-compose stop n8n
   ```

3. Update n8n to the new version:
   ```bash
   docker-compose pull n8n
   ```

4. Start n8n to run migrations:
   ```bash
   docker-compose up -d n8n
   ```

5. Verify the migration:
   ```bash
   docker logs dev-server-workflow_n8n_1 | grep -i migration
   ```

## Disaster Recovery

### Complete System Failure

In case of a complete system failure, follow these steps to recover:

1. **Restore the Host System:**
   - Reinstall the operating system if necessary
   - Install Docker and Docker Compose
   - Clone the repository:
     ```bash
     git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
     cd Dev-Server-Workflow
     ```

2. **Restore Configuration:**
   - Restore the `.env` file from backup
   - Verify the configuration:
     ```bash
     cat .env
     ```

3. **Restore Data:**
   - Create the necessary directories:
     ```bash
     mkdir -p /path/to/restore
     ```
   - Extract the backup archives:
     ```bash
     tar -xzf /path/to/backups/n8n_data_20250501_020000.tar.gz -C /path/to/restore/n8n_data
     tar -xzf /path/to/backups/prometheus_data_20250501_020000.tar.gz -C /path/to/restore/prometheus_data
     tar -xzf /path/to/backups/grafana_data_20250501_020000.tar.gz -C /path/to/restore/grafana_data
     ```

4. **Start the System:**
   - Start the containers with volume mounts:
     ```bash
     docker-compose -f docker-compose.yml -f docker-compose.restore.yml up -d
     ```
   - Verify the restoration:
     ```bash
     ./docker-start.sh status
     ```

5. **Restore Database (if applicable):**
   - Restore the PostgreSQL database:
     ```bash
     PGPASSWORD=$DB_PASSWORD pg_restore -h $DB_HOST -U $DB_USER -d $DB_NAME -c /path/to/backups/n8n_db_20250501_020000.dump
     ```

6. **Verify Functionality:**
   - Check all services:
     ```bash
     ./health_check.sh
     ```
   - Test key workflows:
     ```bash
     curl -X POST "http://localhost:3000/api/v1/execute" \
       -H "X-API-Key: your-api-key" \
       -H "Content-Type: application/json" \
       -d '{"tool": "test-connectivity", "server": "n8n-mcp"}'
     ```

### Data Corruption

In case of data corruption:

1. **Identify Corrupted Data:**
   - Check logs for corruption indicators:
     ```bash
     grep -r "corrupt" ./logs/
     ```
   - Verify database integrity:
     ```bash
     docker exec -it dev-server-workflow_n8n_1 psql -h $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT * FROM pg_stat_database WHERE datname = '$DB_NAME';"
     ```

2. **Stop Affected Services:**
   - Stop the affected service:
     ```bash
     docker-compose stop n8n
     ```

3. **Restore from Backup:**
   - Identify the most recent clean backup:
     ```bash
     ls -lt /path/to/backups/
     ```
   - Restore the data:
     ```bash
     docker run --rm -v dev-server-workflow_n8n_data:/target -v /path/to/backups:/backup alpine sh -c "rm -rf /target/* && tar -xzf /backup/n8n_data_20250501_020000.tar.gz -C /target"
     ```

4. **Restart Services:**
   - Start the affected service:
     ```bash
     docker-compose start n8n
     ```

5. **Verify Restoration:**
   - Check logs for successful startup:
     ```bash
     docker logs dev-server-workflow_n8n_1
     ```
   - Verify functionality:
     ```bash
     curl -s http://localhost:5678/healthz
     ```

## Troubleshooting Decision Trees

### Container Startup Issues

```
Container fails to start
├── Port conflict
│   ├── Check: sudo lsof -i :PORT
│   └── Solution: Change port in .env or stop conflicting process
├── Volume permission issue
│   ├── Check: ls -la /path/to/volume
│   └── Solution: Fix permissions with chown/chmod
├── Environment variable missing
│   ├── Check: docker-compose config
│   └── Solution: Add missing variable to .env
└── Image not found
    ├── Check: docker images
    └── Solution: docker-compose pull or docker-compose build
```

### Network Connectivity Issues

```
Network connectivity issue
├── Container not running
│   ├── Check: docker ps
│   └── Solution: Start the container
├── Container on wrong network
│   ├── Check: docker network inspect
│   └── Solution: Recreate container with correct network
├── Firewall blocking
│   ├── Check: sudo ufw status
│   └── Solution: Add firewall rule
├── DNS resolution issue
│   ├── Check: docker exec container nslookup host
│   └── Solution: Add entry to /etc/hosts or fix DNS
└── Service not listening
    ├── Check: docker exec container netstat -tuln
    └── Solution: Configure service to listen on correct interface
```

### Workflow Execution Issues

```
Workflow execution fails
├── Authentication issue
│   ├── Check: Credentials in workflow
│   └── Solution: Update credentials
├── External service unavailable
│   ├── Check: curl external-service
│   └── Solution: Fix connectivity or service
├── Rate limiting
│   ├── Check: Response headers for rate limit info
│   └── Solution: Implement backoff or increase limits
├── Data validation error
│   ├── Check: Input data format
│   └── Solution: Fix data format or add validation
└── Node.js memory limit
    ├── Check: docker stats for memory usage
    └── Solution: Increase NODE_OPTIONS memory limit
```

### Database Issues

```
Database issue
├── Connection failure
│   ├── Check: pg_isready -h host -p port -U user
│   └── Solution: Fix connection parameters or network
├── Authentication failure
│   ├── Check: Database credentials
│   └── Solution: Update credentials
├── Disk space full
│   ├── Check: df -h
│   └── Solution: Free up disk space or expand volume
├── High load
│   ├── Check: pg_stat_activity for long queries
│   └── Solution: Optimize queries or add indexes
└── Corruption
    ├── Check: Database logs for corruption messages
    └── Solution: Restore from backup
```

## Maintenance Checklists

### Daily Maintenance Checklist

- [ ] **Check System Status**
  - [ ] Run `./docker-start.sh status` to verify all containers are running
  - [ ] Check disk space with `df -h`
  - [ ] Monitor system load with `top` or `htop`

- [ ] **Review Logs**
  - [ ] Check for errors in container logs
  - [ ] Look for unusual patterns or warnings

- [ ] **Verify Backups**
  - [ ] Ensure daily backups completed successfully
  - [ ] Check backup size and integrity

- [ ] **Monitor Performance**
  - [ ] Check Grafana dashboards for anomalies
  - [ ] Review workflow execution times

### Weekly Maintenance Checklist

- [ ] **Update System**
  - [ ] Pull latest Docker images
  - [ ] Check for repository updates
  - [ ] Apply security patches

- [ ] **Clean Up Resources**
  - [ ] Prune unused Docker resources
  - [ ] Remove old logs and temporary files
  - [ ] Archive and compress old backups

- [ ] **Database Maintenance**
  - [ ] Check database size and growth
  - [ ] Identify large tables or indexes
  - [ ] Run VACUUM ANALYZE on PostgreSQL database

- [ ] **Security Audit**
  - [ ] Review access logs for suspicious activity
  - [ ] Check for unauthorized access attempts
  - [ ] Verify API key usage and permissions

- [ ] **Performance Optimization**
  - [ ] Identify slow workflows or operations
  - [ ] Optimize resource-intensive processes
  - [ ] Adjust resource allocations if needed

### Monthly Maintenance Checklist

- [ ] **Comprehensive Backup Test**
  - [ ] Perform a test restoration from backup
  - [ ] Verify data integrity after restoration
  - [ ] Document restoration procedure and results

- [ ] **Security Updates**
  - [ ] Update all system packages
  - [ ] Check for Docker security advisories
  - [ ] Review and update firewall rules

- [ ] **Documentation Review**
  - [ ] Update documentation with any changes
  - [ ] Review and update runbooks
  - [ ] Document new troubleshooting procedures

- [ ] **Capacity Planning**
  - [ ] Review resource usage trends
  - [ ] Project future resource needs
  - [ ] Plan for scaling or hardware upgrades

- [ ] **Disaster Recovery Test**
  - [ ] Simulate a failure scenario
  - [ ] Test recovery procedures
  - [ ] Update disaster recovery plan based on findings