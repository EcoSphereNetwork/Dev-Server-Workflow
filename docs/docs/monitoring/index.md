# Monitoring Stack

The Dev-Server-Workflow includes a comprehensive monitoring stack based on Prometheus, Grafana, and Alertmanager. This stack allows you to monitor the health and performance of all components in the system.

## Components

### Prometheus

[Prometheus](https://prometheus.io/) is an open-source systems monitoring and alerting toolkit. It collects metrics from configured targets at given intervals, evaluates rule expressions, displays the results, and can trigger alerts when specified conditions are observed.

### Grafana

[Grafana](https://grafana.com/) is an open-source platform for monitoring and observability. It allows you to query, visualize, alert on, and understand your metrics no matter where they are stored.

### Alertmanager

[Alertmanager](https://prometheus.io/docs/alerting/latest/alertmanager/) handles alerts sent by client applications such as the Prometheus server. It takes care of deduplicating, grouping, and routing them to the correct receiver integration such as email, PagerDuty, or OpsGenie.

## Getting Started

### Starting the Monitoring Stack

To start the monitoring stack, run:

```bash
./cli/dev-server.sh start monitoring
```

Or use the dedicated script:

```bash
./cli/monitoring.sh start
```

### Accessing the Dashboards

Once the monitoring stack is running, you can access the dashboards at:

- Grafana: [http://localhost:3000](http://localhost:3000) (default credentials: admin/admin)
- Prometheus: [http://localhost:9090](http://localhost:9090)
- Alertmanager: [http://localhost:9093](http://localhost:9093)

### Stopping the Monitoring Stack

To stop the monitoring stack, run:

```bash
./cli/dev-server.sh stop monitoring
```

Or use the dedicated script:

```bash
./cli/monitoring.sh stop
```

## Available Dashboards

### Docker MCP Dashboard

The Docker MCP dashboard provides insights into the Docker MCP server operations, including:

- Tool execution rates and durations
- Container counts (running, stopped, total)
- Network and compose stack counts
- Tool usage distribution
- Authentication attempts

### n8n Dashboard

The n8n dashboard provides insights into the n8n workflow engine, including:

- Workflow execution rates and durations
- Active workflows
- Error rates
- Resource usage

## Alerting

The monitoring stack includes alerting capabilities through Alertmanager. Alerts are configured to notify you when:

- A component is down
- Error rates exceed thresholds
- Resource usage is high

Alerts can be sent to various channels, including:

- Email
- Slack
- PagerDuty
- Webhook (e.g., to n8n for automated remediation)

## Customizing the Monitoring Stack

### Adding New Dashboards

To add a new dashboard to Grafana, you can:

1. Create a JSON file in the `docker/grafana/dashboards` directory
2. Restart the monitoring stack

### Modifying Alerting Rules

To modify alerting rules:

1. Edit the rules in the `docker/prometheus/rules` directory
2. Restart the monitoring stack

### Adding New Metrics

To add new metrics to Prometheus:

1. Expose metrics from your application
2. Add a new scrape configuration to `docker/prometheus/prometheus.yml`
3. Restart the monitoring stack