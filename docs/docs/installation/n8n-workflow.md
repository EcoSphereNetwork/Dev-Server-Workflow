# n8n Workflow Installation

This guide provides detailed instructions for installing and configuring n8n with the predefined workflows for GitHub, OpenProject, document synchronization, and OpenHands integration.

## Prerequisites

- Docker and Docker Compose installed
- Python 3.9 or higher
- Git installed
- GitHub token with appropriate permissions
- OpenProject API token (if using OpenProject integration)

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/EcoSphereNetwork/Dev-Server-Workflow.git
cd Dev-Server-Workflow
```

### 2. Configure Environment Variables

Copy the environment template:

```bash
cp src/env-template .env
```

Edit the `.env` file with your configuration:

```bash
# n8n Configuration
N8N_URL=http://localhost:5678
N8N_USER=admin
N8N_PASSWORD=password
N8N_API_KEY=your_api_key
N8N_ENCRYPTION_KEY=your_encryption_key_min_32_chars
N8N_HOST=localhost
N8N_PROTOCOL=http
N8N_DATA_FOLDER=./n8n_data

# GitHub/GitLab Configuration
GITHUB_TOKEN=your_github_token
GITLAB_TOKEN=your_gitlab_token

# OpenProject Configuration
OPENPROJECT_URL=https://your-openproject-instance.com
OPENPROJECT_TOKEN=your_openproject_token
OPENPROJECT_NEW_STATUS_ID=1
OPENPROJECT_IN_PROGRESS_STATUS_ID=7
OPENPROJECT_PR_CREATED_STATUS_ID=2
OPENPROJECT_RESOLVED_STATUS_ID=12

# Other integrations
DISCORD_WEBHOOK_URL=your_discord_webhook_url
LLM_API_KEY=your_llm_api_key
LLM_MODEL=anthropic/claude-3-5-sonnet-20240620
```

### 3. Install n8n and Workflows

Use the setup script to install n8n and configure the workflows:

```bash
# Install all workflows
python setup.py install --env-file .env

# Install specific workflows
python setup.py install --env-file .env --workflows github document openhands

# Install with MCP server
python setup.py install --env-file .env --mcp

# Skip n8n installation (if already installed)
python setup.py install --env-file .env --no-install
```

### 4. Verify Installation

Test the installation:

```bash
python setup.py test
```

Check if n8n is running:

```bash
./cli/dev-server.sh status
```

Access the n8n web interface at http://localhost:5678

### 5. Configure Webhooks

After installation, you'll need to configure webhooks to trigger the workflows:

#### GitHub Webhooks

1. Go to your GitHub repository settings
2. Navigate to Webhooks
3. Add a new webhook:
   - Payload URL: `http://your-n8n-url:5678/webhook/github`
   - Content type: `application/json`
   - Secret: Use the value from `WEBHOOK_SECRET` in your `.env` file
   - Events: Select `Issues`, `Pull requests`, and `Push`

#### OpenProject Webhooks

1. Go to your OpenProject administration
2. Navigate to API & Webhooks
3. Add a new webhook:
   - URL: `http://your-n8n-url:5678/webhook/openproject`
   - Secret: Use the value from `WEBHOOK_SECRET` in your `.env` file
   - Events: Select `Work package created`, `Work package updated`

## Available Workflows

| Workflow | Description | Required Credentials |
|----------|-------------|---------------------|
| GitHub-OpenProject | Syncs GitHub issues and PRs with OpenProject work packages | GitHub, OpenProject |
| Document Sync | Syncs documentation between AFFiNE/AppFlowy and GitHub | GitHub, AFFiNE/AppFlowy |
| OpenHands | Integrates OpenHands AI agent with GitHub and OpenProject | GitHub, OpenProject, LLM |
| Discord Notification | Sends notifications to Discord for GitHub events | GitHub, Discord |
| Time Tracking | Tracks time spent on GitHub PRs and updates OpenProject | GitHub, OpenProject |
| AI Summary | Generates AI summaries of GitHub PRs and issues | GitHub, LLM |
| MCP Server | Provides MCP server functionality for n8n workflows | GitHub, OpenProject |

## Manual Configuration

If you need to manually configure n8n:

### Starting n8n with Docker

```bash
docker run -d \
  --name n8n \
  -p 5678:5678 \
  -e N8N_USER=admin \
  -e N8N_PASS=password \
  -e N8N_ENCRYPTION_KEY=your_encryption_key_min_32_chars \
  -v $(pwd)/n8n_data:/home/node/.n8n \
  n8nio/n8n
```

### Creating API Key

1. Access the n8n web interface at http://localhost:5678
2. Log in with your credentials
3. Go to Settings > API
4. Create a new API key
5. Update your `.env` file with the new API key

### Importing Workflows Manually

1. Access the n8n web interface
2. Go to Workflows
3. Click Import from File
4. Select the workflow JSON file from `src/workflows/`

## Troubleshooting

### n8n Not Starting

Check the Docker logs:

```bash
docker logs n8n
```

Ensure the ports are not in use:

```bash
netstat -tuln | grep 5678
```

### Workflow Execution Failures

Check the n8n execution logs in the web interface:

1. Go to Executions
2. Find the failed execution
3. Click on it to see the error details

### API Key Issues

If you encounter API key issues:

1. Regenerate the API key in the n8n web interface
2. Update your `.env` file
3. Restart the setup:
   ```bash
   python setup.py install --env-file .env --no-install
   ```