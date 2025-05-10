# n8n Integration Layer for MCP Servers

This directory contains the implementation of the n8n integration layer for MCP servers, enabling bidirectional communication between MCP servers and n8n workflow automation.

## Components

### 1. n8n Integration Layer (`n8n_integration.py`)

The core integration layer that provides:

- Bidirectional communication with n8n
- Authentication and authorization
- Webhook handling for n8n triggers
- Status reporting and monitoring
- Workflow execution and management
- Caching for performance optimization

### 2. Enhanced n8n MCP Server (`n8n_mcp_server_enhanced.py`)

An enhanced MCP server implementation that uses the integration layer to:

- Expose n8n workflows as MCP tools
- Handle tool calls by executing n8n workflows
- Track workflow executions
- Provide status information
- Handle webhooks from n8n

### 3. Test Script (`test_n8n_integration.py`)

A test script to verify the functionality of the integration layer.

## Usage

### Environment Variables

The integration layer uses the following environment variables:

- `N8N_URL`: URL of the n8n instance (default: `http://localhost:5678`)
- `N8N_API_KEY`: API key for n8n
- `N8N_WEBHOOK_SECRET`: Secret for webhook validation

### Running the Enhanced MCP Server

```bash
python src/mcp/n8n_mcp_server_enhanced.py --n8n-url http://localhost:5678 --api-key your-api-key
```

### Testing the Integration Layer

```bash
python src/mcp/test_n8n_integration.py
```

## Features

### Workflow Management

- List workflows from n8n
- Get workflow details
- Import workflow templates
- Export workflows as templates
- Sync workflows to the orchestrator

### Workflow Execution

- Execute workflows with input data
- Track execution status
- Get execution results
- Handle execution errors

### Webhook Handling

- Register webhook handlers
- Validate webhook signatures
- Process webhook payloads
- Trigger actions based on webhooks

### Caching

- Cache workflow information
- Cache execution results
- Configurable cache TTL
- Automatic cache invalidation

### Monitoring

- Track execution metrics
- Monitor connection status
- Report error rates
- Provide status information

## Integration with MCP

The integration layer allows MCP servers to:

1. Discover n8n workflows and expose them as tools
2. Execute workflows when tools are called
3. Receive notifications when workflows complete
4. Track workflow execution status
5. Provide status information to clients

## Security

The integration layer includes:

- API key authentication for n8n
- Webhook signature validation
- Error handling and logging
- Rate limiting and throttling

## Error Handling

The integration layer provides structured error handling with:

- Specific error types for different failure modes
- Detailed error information
- Logging of errors
- Retry mechanisms for transient failures

## Performance Optimization

The integration layer includes:

- Caching of workflow information
- Connection pooling
- Asynchronous execution
- Batch processing where applicable