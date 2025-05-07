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
    new winston.transports.File({ filename: 'gitlab-mcp-server.log' })
  ]
});

// Create Express app
const app = express();
const port = process.env.MCP_PORT || 3002;

// Configure middleware
app.use(cors());
app.use(bodyParser.json());

// Configure Redis client
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD || '',
});

// GitLab API client
const gitlabClient = axios.create({
  baseURL: process.env.GITLAB_API_URL || 'https://gitlab.com/api/v4',
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
      name: 'gitlab_create_issue',
      description: 'Create a new issue in a GitLab project',
      parameter_schema: {
        type: 'object',
        properties: {
          project_id: {
            type: 'string',
            description: 'The ID or URL-encoded path of the project'
          },
          title: {
            type: 'string',
            description: 'The title of the issue'
          },
          description: {
            type: 'string',
            description: 'The description of the issue'
          },
          labels: {
            type: 'string',
            description: 'Comma-separated label names for the issue'
          },
          assignee_ids: {
            type: 'array',
            items: {
              type: 'integer'
            },
            description: 'The ID of the users to assign the issue to'
          },
          milestone_id: {
            type: 'integer',
            description: 'The global ID of a milestone to assign the issue to'
          },
          due_date: {
            type: 'string',
            description: 'Date string in the format YYYY-MM-DD'
          }
        },
        required: ['project_id', 'title']
      }
    },
    {
      name: 'gitlab_get_issues',
      description: 'Get issues from a GitLab project',
      parameter_schema: {
        type: 'object',
        properties: {
          project_id: {
            type: 'string',
            description: 'The ID or URL-encoded path of the project'
          },
          state: {
            type: 'string',
            enum: ['opened', 'closed', 'all'],
            description: 'Return all issues or just those that are opened or closed'
          },
          labels: {
            type: 'string',
            description: 'Comma-separated list of label names'
          },
          milestone: {
            type: 'string',
            description: 'The milestone title'
          },
          scope: {
            type: 'string',
            enum: ['created_by_me', 'assigned_to_me', 'all'],
            description: 'Return issues for the given scope'
          },
          per_page: {
            type: 'integer',
            description: 'Number of items to list per page'
          },
          page: {
            type: 'integer',
            description: 'Page number'
          }
        },
        required: ['project_id']
      }
    },
    {
      name: 'gitlab_create_merge_request',
      description: 'Create a new merge request in a GitLab project',
      parameter_schema: {
        type: 'object',
        properties: {
          project_id: {
            type: 'string',
            description: 'The ID or URL-encoded path of the project'
          },
          source_branch: {
            type: 'string',
            description: 'The source branch'
          },
          target_branch: {
            type: 'string',
            description: 'The target branch'
          },
          title: {
            type: 'string',
            description: 'Title of the merge request'
          },
          description: {
            type: 'string',
            description: 'Description of the merge request'
          },
          assignee_id: {
            type: 'integer',
            description: 'Assignee user ID'
          },
          labels: {
            type: 'string',
            description: 'Labels for MR as a comma-separated list'
          },
          remove_source_branch: {
            type: 'boolean',
            description: 'Flag indicating if a merge request should remove the source branch when merging'
          }
        },
        required: ['project_id', 'source_branch', 'target_branch', 'title']
      }
    },
    {
      name: 'gitlab_get_project',
      description: 'Get information about a GitLab project',
      parameter_schema: {
        type: 'object',
        properties: {
          project_id: {
            type: 'string',
            description: 'The ID or URL-encoded path of the project'
          }
        },
        required: ['project_id']
      }
    },
    {
      name: 'gitlab_get_file_content',
      description: 'Get the content of a file from a GitLab project',
      parameter_schema: {
        type: 'object',
        properties: {
          project_id: {
            type: 'string',
            description: 'The ID or URL-encoded path of the project'
          },
          file_path: {
            type: 'string',
            description: 'The path to the file'
          },
          ref: {
            type: 'string',
            description: 'The name of the branch, tag or commit'
          }
        },
        required: ['project_id', 'file_path']
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
    case 'gitlab_create_issue':
      return await createIssue(args);
    case 'gitlab_get_issues':
      return await getIssues(args);
    case 'gitlab_create_merge_request':
      return await createMergeRequest(args);
    case 'gitlab_get_project':
      return await getProject(args);
    case 'gitlab_get_file_content':
      return await getFileContent(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// GitLab API functions
async function createIssue(args) {
  const { project_id, title, description, labels, assignee_ids, milestone_id, due_date } = args;
  
  if (!project_id) {
    throw new Error('Project ID is required');
  }
  
  if (!title) {
    throw new Error('Title is required');
  }
  
  try {
    const response = await gitlabClient.post(`/projects/${encodeURIComponent(project_id)}/issues`, {
      title,
      description,
      labels,
      assignee_ids,
      milestone_id,
      due_date
    }, {
      headers: {
        'PRIVATE-TOKEN': process.env.GITLAB_TOKEN
      }
    });
    
    return {
      success: true,
      issue: {
        iid: response.data.iid,
        id: response.data.id,
        url: response.data.web_url,
        title: response.data.title,
        state: response.data.state
      }
    };
  } catch (error) {
    logger.error('Error creating GitLab issue:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getIssues(args) {
  const { project_id, state, labels, milestone, scope, per_page, page } = args;
  
  if (!project_id) {
    throw new Error('Project ID is required');
  }
  
  try {
    const response = await gitlabClient.get(`/projects/${encodeURIComponent(project_id)}/issues`, {
      params: {
        state,
        labels,
        milestone,
        scope,
        per_page,
        page
      },
      headers: {
        'PRIVATE-TOKEN': process.env.GITLAB_TOKEN
      }
    });
    
    return {
      success: true,
      issues: response.data.map(issue => ({
        iid: issue.iid,
        id: issue.id,
        url: issue.web_url,
        title: issue.title,
        state: issue.state,
        created_at: issue.created_at,
        updated_at: issue.updated_at,
        labels: issue.labels,
        assignees: issue.assignees.map(assignee => assignee.username)
      }))
    };
  } catch (error) {
    logger.error('Error getting GitLab issues:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function createMergeRequest(args) {
  const { project_id, source_branch, target_branch, title, description, assignee_id, labels, remove_source_branch } = args;
  
  if (!project_id || !source_branch || !target_branch || !title) {
    throw new Error('Project ID, source branch, target branch, and title are required');
  }
  
  try {
    const response = await gitlabClient.post(`/projects/${encodeURIComponent(project_id)}/merge_requests`, {
      source_branch,
      target_branch,
      title,
      description,
      assignee_id,
      labels,
      remove_source_branch
    }, {
      headers: {
        'PRIVATE-TOKEN': process.env.GITLAB_TOKEN
      }
    });
    
    return {
      success: true,
      merge_request: {
        iid: response.data.iid,
        id: response.data.id,
        url: response.data.web_url,
        title: response.data.title,
        state: response.data.state
      }
    };
  } catch (error) {
    logger.error('Error creating GitLab merge request:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getProject(args) {
  const { project_id } = args;
  
  if (!project_id) {
    throw new Error('Project ID is required');
  }
  
  try {
    const response = await gitlabClient.get(`/projects/${encodeURIComponent(project_id)}`, {
      headers: {
        'PRIVATE-TOKEN': process.env.GITLAB_TOKEN
      }
    });
    
    return {
      success: true,
      project: {
        id: response.data.id,
        name: response.data.name,
        path: response.data.path,
        path_with_namespace: response.data.path_with_namespace,
        description: response.data.description,
        url: response.data.web_url,
        stars: response.data.star_count,
        forks: response.data.forks_count,
        open_issues_count: response.data.open_issues_count,
        default_branch: response.data.default_branch,
        created_at: response.data.created_at,
        last_activity_at: response.data.last_activity_at
      }
    };
  } catch (error) {
    logger.error('Error getting GitLab project:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getFileContent(args) {
  const { project_id, file_path, ref } = args;
  
  if (!project_id || !file_path) {
    throw new Error('Project ID and file path are required');
  }
  
  try {
    const response = await gitlabClient.get(`/projects/${encodeURIComponent(project_id)}/repository/files/${encodeURIComponent(file_path)}`, {
      params: {
        ref: ref || 'master'
      },
      headers: {
        'PRIVATE-TOKEN': process.env.GITLAB_TOKEN
      }
    });
    
    return {
      success: true,
      file: {
        file_name: response.data.file_name,
        file_path: response.data.file_path,
        content: Buffer.from(response.data.content, 'base64').toString('utf-8'),
        ref: response.data.ref,
        blob_id: response.data.blob_id,
        commit_id: response.data.commit_id,
        last_commit_id: response.data.last_commit_id
      }
    };
  } catch (error) {
    logger.error('Error getting GitLab file content:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

// Start the server
app.listen(port, () => {
  logger.info(`GitLab MCP Server running on port ${port}`);
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