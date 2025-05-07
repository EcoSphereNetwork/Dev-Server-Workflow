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
    new winston.transports.File({ filename: 'openproject-mcp-server.log' })
  ]
});

// Create Express app
const app = express();
const port = process.env.MCP_PORT || 3003;

// Configure middleware
app.use(cors());
app.use(bodyParser.json());

// Configure Redis client
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD || '',
});

// OpenProject API client
const openProjectClient = axios.create({
  baseURL: process.env.OPENPROJECT_API_URL || 'https://openproject.example.com/api/v3',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.OPENPROJECT_API_KEY}`
  }
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
      name: 'openproject_create_work_package',
      description: 'Create a new work package in OpenProject',
      parameter_schema: {
        type: 'object',
        properties: {
          project_id: {
            type: 'integer',
            description: 'The ID of the project'
          },
          subject: {
            type: 'string',
            description: 'The subject of the work package'
          },
          description: {
            type: 'string',
            description: 'The description of the work package'
          },
          type_id: {
            type: 'integer',
            description: 'The ID of the work package type (e.g., 1 for Task, 2 for Milestone, etc.)'
          },
          status_id: {
            type: 'integer',
            description: 'The ID of the status (e.g., 1 for New, 2 for In Progress, etc.)'
          },
          priority_id: {
            type: 'integer',
            description: 'The ID of the priority (e.g., 1 for Low, 2 for Normal, etc.)'
          },
          assigned_to_id: {
            type: 'integer',
            description: 'The ID of the user to assign the work package to'
          },
          due_date: {
            type: 'string',
            description: 'The due date of the work package (ISO 8601 format)'
          }
        },
        required: ['project_id', 'subject', 'type_id']
      }
    },
    {
      name: 'openproject_get_work_packages',
      description: 'Get work packages from OpenProject',
      parameter_schema: {
        type: 'object',
        properties: {
          project_id: {
            type: 'integer',
            description: 'The ID of the project'
          },
          status_id: {
            type: 'integer',
            description: 'Filter by status ID'
          },
          type_id: {
            type: 'integer',
            description: 'Filter by type ID'
          },
          assigned_to_id: {
            type: 'integer',
            description: 'Filter by assigned user ID'
          },
          subject: {
            type: 'string',
            description: 'Filter by subject (partial match)'
          },
          created_at: {
            type: 'string',
            description: 'Filter by creation date (ISO 8601 format)'
          },
          updated_at: {
            type: 'string',
            description: 'Filter by update date (ISO 8601 format)'
          },
          offset: {
            type: 'integer',
            description: 'Offset for pagination'
          },
          pageSize: {
            type: 'integer',
            description: 'Number of items per page'
          }
        },
        required: []
      }
    },
    {
      name: 'openproject_update_work_package',
      description: 'Update an existing work package in OpenProject',
      parameter_schema: {
        type: 'object',
        properties: {
          id: {
            type: 'integer',
            description: 'The ID of the work package to update'
          },
          subject: {
            type: 'string',
            description: 'The subject of the work package'
          },
          description: {
            type: 'string',
            description: 'The description of the work package'
          },
          status_id: {
            type: 'integer',
            description: 'The ID of the status'
          },
          priority_id: {
            type: 'integer',
            description: 'The ID of the priority'
          },
          assigned_to_id: {
            type: 'integer',
            description: 'The ID of the user to assign the work package to'
          },
          due_date: {
            type: 'string',
            description: 'The due date of the work package (ISO 8601 format)'
          }
        },
        required: ['id']
      }
    },
    {
      name: 'openproject_get_project',
      description: 'Get information about an OpenProject project',
      parameter_schema: {
        type: 'object',
        properties: {
          id: {
            type: 'integer',
            description: 'The ID of the project'
          }
        },
        required: ['id']
      }
    },
    {
      name: 'openproject_get_users',
      description: 'Get users from OpenProject',
      parameter_schema: {
        type: 'object',
        properties: {
          status: {
            type: 'string',
            enum: ['active', 'registered', 'locked', 'invited'],
            description: 'Filter by user status'
          },
          name: {
            type: 'string',
            description: 'Filter by name (partial match)'
          },
          offset: {
            type: 'integer',
            description: 'Offset for pagination'
          },
          pageSize: {
            type: 'integer',
            description: 'Number of items per page'
          }
        },
        required: []
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
    case 'openproject_create_work_package':
      return await createWorkPackage(args);
    case 'openproject_get_work_packages':
      return await getWorkPackages(args);
    case 'openproject_update_work_package':
      return await updateWorkPackage(args);
    case 'openproject_get_project':
      return await getProject(args);
    case 'openproject_get_users':
      return await getUsers(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// OpenProject API functions
async function createWorkPackage(args) {
  const { project_id, subject, description, type_id, status_id, priority_id, assigned_to_id, due_date } = args;
  
  if (!project_id || !subject || !type_id) {
    throw new Error('Project ID, subject, and type ID are required');
  }
  
  try {
    const payload = {
      _links: {
        project: {
          href: `/api/v3/projects/${project_id}`
        },
        type: {
          href: `/api/v3/types/${type_id}`
        }
      },
      subject,
      description: {
        raw: description || ''
      }
    };
    
    if (status_id) {
      payload._links.status = {
        href: `/api/v3/statuses/${status_id}`
      };
    }
    
    if (priority_id) {
      payload._links.priority = {
        href: `/api/v3/priorities/${priority_id}`
      };
    }
    
    if (assigned_to_id) {
      payload._links.assignee = {
        href: `/api/v3/users/${assigned_to_id}`
      };
    }
    
    if (due_date) {
      payload.dueDate = due_date;
    }
    
    const response = await openProjectClient.post('/work_packages', payload);
    
    return {
      success: true,
      work_package: {
        id: response.data.id,
        subject: response.data.subject,
        description: response.data.description?.raw || '',
        url: response.data._links.self.href,
        created_at: response.data.createdAt,
        updated_at: response.data.updatedAt
      }
    };
  } catch (error) {
    logger.error('Error creating OpenProject work package:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getWorkPackages(args) {
  const { project_id, status_id, type_id, assigned_to_id, subject, created_at, updated_at, offset, pageSize } = args;
  
  try {
    let filters = [];
    
    if (project_id) {
      filters.push({
        project: {
          operator: '=',
          values: [project_id.toString()]
        }
      });
    }
    
    if (status_id) {
      filters.push({
        status: {
          operator: '=',
          values: [status_id.toString()]
        }
      });
    }
    
    if (type_id) {
      filters.push({
        type: {
          operator: '=',
          values: [type_id.toString()]
        }
      });
    }
    
    if (assigned_to_id) {
      filters.push({
        assignee: {
          operator: '=',
          values: [assigned_to_id.toString()]
        }
      });
    }
    
    if (subject) {
      filters.push({
        subject: {
          operator: '~',
          values: [subject]
        }
      });
    }
    
    if (created_at) {
      filters.push({
        createdAt: {
          operator: '>=',
          values: [created_at]
        }
      });
    }
    
    if (updated_at) {
      filters.push({
        updatedAt: {
          operator: '>=',
          values: [updated_at]
        }
      });
    }
    
    const params = {
      offset: offset || 1,
      pageSize: pageSize || 10
    };
    
    if (filters.length > 0) {
      params.filters = JSON.stringify(filters);
    }
    
    const response = await openProjectClient.get('/work_packages', { params });
    
    return {
      success: true,
      work_packages: response.data._embedded.elements.map(wp => ({
        id: wp.id,
        subject: wp.subject,
        description: wp.description?.raw || '',
        url: wp._links.self.href,
        status: wp._links.status.title,
        type: wp._links.type.title,
        created_at: wp.createdAt,
        updated_at: wp.updatedAt
      })),
      total: response.data.total,
      count: response.data.count,
      offset: response.data.offset,
      pageSize: response.data.pageSize
    };
  } catch (error) {
    logger.error('Error getting OpenProject work packages:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function updateWorkPackage(args) {
  const { id, subject, description, status_id, priority_id, assigned_to_id, due_date } = args;
  
  if (!id) {
    throw new Error('Work package ID is required');
  }
  
  try {
    const payload = {};
    
    if (subject) {
      payload.subject = subject;
    }
    
    if (description) {
      payload.description = {
        raw: description
      };
    }
    
    if (status_id) {
      payload._links = payload._links || {};
      payload._links.status = {
        href: `/api/v3/statuses/${status_id}`
      };
    }
    
    if (priority_id) {
      payload._links = payload._links || {};
      payload._links.priority = {
        href: `/api/v3/priorities/${priority_id}`
      };
    }
    
    if (assigned_to_id) {
      payload._links = payload._links || {};
      payload._links.assignee = {
        href: `/api/v3/users/${assigned_to_id}`
      };
    }
    
    if (due_date) {
      payload.dueDate = due_date;
    }
    
    const response = await openProjectClient.patch(`/work_packages/${id}`, payload);
    
    return {
      success: true,
      work_package: {
        id: response.data.id,
        subject: response.data.subject,
        description: response.data.description?.raw || '',
        url: response.data._links.self.href,
        created_at: response.data.createdAt,
        updated_at: response.data.updatedAt
      }
    };
  } catch (error) {
    logger.error('Error updating OpenProject work package:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getProject(args) {
  const { id } = args;
  
  if (!id) {
    throw new Error('Project ID is required');
  }
  
  try {
    const response = await openProjectClient.get(`/projects/${id}`);
    
    return {
      success: true,
      project: {
        id: response.data.id,
        name: response.data.name,
        description: response.data.description?.raw || '',
        url: response.data._links.self.href,
        created_at: response.data.createdAt,
        updated_at: response.data.updatedAt
      }
    };
  } catch (error) {
    logger.error('Error getting OpenProject project:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getUsers(args) {
  const { status, name, offset, pageSize } = args;
  
  try {
    const params = {
      offset: offset || 1,
      pageSize: pageSize || 10
    };
    
    if (status) {
      params.status = status;
    }
    
    if (name) {
      params.name = name;
    }
    
    const response = await openProjectClient.get('/users', { params });
    
    return {
      success: true,
      users: response.data._embedded.elements.map(user => ({
        id: user.id,
        name: user.name,
        email: user.email,
        url: user._links.self.href,
        status: user.status,
        created_at: user.createdAt,
        updated_at: user.updatedAt
      })),
      total: response.data.total,
      count: response.data.count,
      offset: response.data.offset,
      pageSize: response.data.pageSize
    };
  } catch (error) {
    logger.error('Error getting OpenProject users:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

// Start the server
app.listen(port, () => {
  logger.info(`OpenProject MCP Server running on port ${port}`);
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