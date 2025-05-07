const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const axios = require('axios');
const Redis = require('ioredis');
const winston = require('winston');
const dotenv = require('dotenv');

// Load environment variables
dotenv.config();

// Configure logger
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.json()
  ),
  transports: [
    new winston.transports.Console(),
    new winston.transports.File({ filename: 'github-mcp-server.log' })
  ]
});

// Create Express app
const app = express();
const port = process.env.MCP_PORT || 3001;

// Configure middleware
app.use(cors());
app.use(bodyParser.json());

// Configure Redis client
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD || '',
});

// GitHub API client
const githubClient = axios.create({
  baseURL: process.env.GITHUB_API_URL || 'https://api.github.com',
  timeout: 10000,
});

// MCP Protocol implementation
app.post('/mcp', async (req, res) => {
  try {
    const { jsonrpc, id, method, params } = req.body;

    // Validate JSON-RPC request
    if (jsonrpc !== '2.0' || !id || !method) {
      return res.status(400).json({
        jsonrpc: '2.0',
        id: id || null,
        error: {
          code: -32600,
          message: 'Invalid Request'
        }
      });
    }

    // Handle MCP methods
    let result;
    switch (method) {
      case 'mcp.listTools':
        result = await handleListTools();
        break;
      case 'mcp.callTool':
        result = await handleCallTool(params);
        break;
      default:
        return res.status(400).json({
          jsonrpc: '2.0',
          id,
          error: {
            code: -32601,
            message: `Method not found: ${method}`
          }
        });
    }

    // Return JSON-RPC response
    return res.json({
      jsonrpc: '2.0',
      id,
      result
    });
  } catch (error) {
    logger.error('Error processing MCP request:', error);
    return res.status(500).json({
      jsonrpc: '2.0',
      id: req.body.id || null,
      error: {
        code: -32603,
        message: 'Internal error',
        data: error.message
      }
    });
  }
});

// Handle mcp.listTools method
async function handleListTools() {
  return [
    {
      name: 'github_create_issue',
      description: 'Create a new issue in a GitHub repository',
      parameter_schema: {
        type: 'object',
        properties: {
          repository: {
            type: 'string',
            description: 'The repository in format owner/repo'
          },
          title: {
            type: 'string',
            description: 'The title of the issue'
          },
          body: {
            type: 'string',
            description: 'The body content of the issue'
          },
          labels: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'Labels to add to the issue'
          },
          assignees: {
            type: 'array',
            items: {
              type: 'string'
            },
            description: 'GitHub usernames to assign to the issue'
          }
        },
        required: ['repository', 'title']
      }
    },
    {
      name: 'github_get_issues',
      description: 'Get issues from a GitHub repository',
      parameter_schema: {
        type: 'object',
        properties: {
          repository: {
            type: 'string',
            description: 'The repository in format owner/repo'
          },
          state: {
            type: 'string',
            enum: ['open', 'closed', 'all'],
            description: 'The state of issues to return'
          },
          labels: {
            type: 'string',
            description: 'Comma-separated list of label names'
          },
          sort: {
            type: 'string',
            enum: ['created', 'updated', 'comments'],
            description: 'What to sort results by'
          },
          direction: {
            type: 'string',
            enum: ['asc', 'desc'],
            description: 'The direction of the sort'
          },
          since: {
            type: 'string',
            description: 'Only issues updated at or after this time (ISO 8601 format)'
          },
          per_page: {
            type: 'integer',
            description: 'Results per page (max 100)'
          },
          page: {
            type: 'integer',
            description: 'Page number of the results'
          }
        },
        required: ['repository']
      }
    },
    {
      name: 'github_create_pull_request',
      description: 'Create a new pull request in a GitHub repository',
      parameter_schema: {
        type: 'object',
        properties: {
          repository: {
            type: 'string',
            description: 'The repository in format owner/repo'
          },
          title: {
            type: 'string',
            description: 'The title of the pull request'
          },
          body: {
            type: 'string',
            description: 'The body content of the pull request'
          },
          head: {
            type: 'string',
            description: 'The name of the branch where your changes are implemented'
          },
          base: {
            type: 'string',
            description: 'The name of the branch you want the changes pulled into'
          },
          draft: {
            type: 'boolean',
            description: 'Whether to create a draft pull request'
          }
        },
        required: ['repository', 'title', 'head', 'base']
      }
    },
    {
      name: 'github_get_repository',
      description: 'Get information about a GitHub repository',
      parameter_schema: {
        type: 'object',
        properties: {
          repository: {
            type: 'string',
            description: 'The repository in format owner/repo'
          }
        },
        required: ['repository']
      }
    },
    {
      name: 'github_get_file_content',
      description: 'Get the content of a file from a GitHub repository',
      parameter_schema: {
        type: 'object',
        properties: {
          repository: {
            type: 'string',
            description: 'The repository in format owner/repo'
          },
          path: {
            type: 'string',
            description: 'The path to the file'
          },
          ref: {
            type: 'string',
            description: 'The name of the commit/branch/tag'
          }
        },
        required: ['repository', 'path']
      }
    }
  ];
}

// Handle mcp.callTool method
async function handleCallTool(params) {
  const { name, arguments: args } = params;

  if (!name) {
    throw new Error('Tool name is required');
  }

  switch (name) {
    case 'github_create_issue':
      return await createIssue(args);
    case 'github_get_issues':
      return await getIssues(args);
    case 'github_create_pull_request':
      return await createPullRequest(args);
    case 'github_get_repository':
      return await getRepository(args);
    case 'github_get_file_content':
      return await getFileContent(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// GitHub API functions
async function createIssue(args) {
  const { repository, title, body, labels, assignees } = args;
  
  if (!repository) {
    throw new Error('Repository is required');
  }
  
  if (!title) {
    throw new Error('Title is required');
  }
  
  const [owner, repo] = repository.split('/');
  
  try {
    const response = await githubClient.post(`/repos/${owner}/${repo}/issues`, {
      title,
      body,
      labels,
      assignees
    }, {
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    return {
      success: true,
      issue: {
        number: response.data.number,
        url: response.data.html_url,
        title: response.data.title,
        state: response.data.state
      }
    };
  } catch (error) {
    logger.error('Error creating GitHub issue:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getIssues(args) {
  const { repository, state, labels, sort, direction, since, per_page, page } = args;
  
  if (!repository) {
    throw new Error('Repository is required');
  }
  
  const [owner, repo] = repository.split('/');
  
  try {
    const response = await githubClient.get(`/repos/${owner}/${repo}/issues`, {
      params: {
        state,
        labels,
        sort,
        direction,
        since,
        per_page,
        page
      },
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    return {
      success: true,
      issues: response.data.map(issue => ({
        number: issue.number,
        url: issue.html_url,
        title: issue.title,
        state: issue.state,
        created_at: issue.created_at,
        updated_at: issue.updated_at,
        labels: issue.labels.map(label => label.name),
        assignees: issue.assignees.map(assignee => assignee.login)
      }))
    };
  } catch (error) {
    logger.error('Error getting GitHub issues:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function createPullRequest(args) {
  const { repository, title, body, head, base, draft } = args;
  
  if (!repository) {
    throw new Error('Repository is required');
  }
  
  if (!title || !head || !base) {
    throw new Error('Title, head, and base are required');
  }
  
  const [owner, repo] = repository.split('/');
  
  try {
    const response = await githubClient.post(`/repos/${owner}/${repo}/pulls`, {
      title,
      body,
      head,
      base,
      draft: draft || false
    }, {
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    return {
      success: true,
      pull_request: {
        number: response.data.number,
        url: response.data.html_url,
        title: response.data.title,
        state: response.data.state
      }
    };
  } catch (error) {
    logger.error('Error creating GitHub pull request:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getRepository(args) {
  const { repository } = args;
  
  if (!repository) {
    throw new Error('Repository is required');
  }
  
  const [owner, repo] = repository.split('/');
  
  try {
    const response = await githubClient.get(`/repos/${owner}/${repo}`, {
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    return {
      success: true,
      repository: {
        name: response.data.name,
        full_name: response.data.full_name,
        description: response.data.description,
        url: response.data.html_url,
        stars: response.data.stargazers_count,
        forks: response.data.forks_count,
        open_issues: response.data.open_issues_count,
        default_branch: response.data.default_branch,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      }
    };
  } catch (error) {
    logger.error('Error getting GitHub repository:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getFileContent(args) {
  const { repository, path, ref } = args;
  
  if (!repository || !path) {
    throw new Error('Repository and path are required');
  }
  
  const [owner, repo] = repository.split('/');
  
  try {
    const response = await githubClient.get(`/repos/${owner}/${repo}/contents/${path}`, {
      params: {
        ref: ref || undefined
      },
      headers: {
        'Authorization': `token ${process.env.GITHUB_TOKEN}`,
        'Accept': 'application/vnd.github.v3+json'
      }
    });
    
    return {
      success: true,
      file: {
        name: response.data.name,
        path: response.data.path,
        content: Buffer.from(response.data.content, 'base64').toString('utf-8'),
        sha: response.data.sha
      }
    };
  } catch (error) {
    logger.error('Error getting GitHub file content:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

// Start the server
app.listen(port, () => {
  logger.info(`GitHub MCP Server running on port ${port}`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  logger.info('SIGTERM signal received: closing HTTP server');
  redis.quit();
  process.exit(0);
});

process.on('SIGINT', () => {
  logger.info('SIGINT signal received: closing HTTP server');
  redis.quit();
  process.exit(0);
});