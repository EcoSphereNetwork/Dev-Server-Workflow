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
    new winston.transports.File({ filename: 'appflowy-mcp-server.log' })
  ]
});

// Create Express app
const app = express();
const port = process.env.MCP_PORT || 3004;

// Configure middleware
app.use(cors());
app.use(bodyParser.json());

// Configure Redis client
const redis = new Redis({
  host: process.env.REDIS_HOST || 'localhost',
  port: process.env.REDIS_PORT || 6379,
  password: process.env.REDIS_PASSWORD || '',
});

// AppFlowy API client
const appFlowyClient = axios.create({
  baseURL: process.env.APPFLOWY_API_URL || 'https://appflowy.example.com/api',
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${process.env.APPFLOWY_API_KEY}`
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
      name: 'appflowy_create_document',
      description: 'Create a new document in AppFlowy',
      parameter_schema: {
        type: 'object',
        properties: {
          workspace_id: {
            type: 'string',
            description: 'The ID of the workspace'
          },
          name: {
            type: 'string',
            description: 'The name of the document'
          },
          content: {
            type: 'string',
            description: 'The content of the document'
          },
          parent_id: {
            type: 'string',
            description: 'The ID of the parent folder (optional)'
          }
        },
        required: ['workspace_id', 'name']
      }
    },
    {
      name: 'appflowy_get_documents',
      description: 'Get documents from AppFlowy',
      parameter_schema: {
        type: 'object',
        properties: {
          workspace_id: {
            type: 'string',
            description: 'The ID of the workspace'
          },
          parent_id: {
            type: 'string',
            description: 'The ID of the parent folder (optional)'
          },
          page: {
            type: 'integer',
            description: 'Page number for pagination'
          },
          limit: {
            type: 'integer',
            description: 'Number of items per page'
          }
        },
        required: ['workspace_id']
      }
    },
    {
      name: 'appflowy_update_document',
      description: 'Update an existing document in AppFlowy',
      parameter_schema: {
        type: 'object',
        properties: {
          document_id: {
            type: 'string',
            description: 'The ID of the document to update'
          },
          name: {
            type: 'string',
            description: 'The new name of the document'
          },
          content: {
            type: 'string',
            description: 'The new content of the document'
          }
        },
        required: ['document_id']
      }
    },
    {
      name: 'appflowy_create_database',
      description: 'Create a new database in AppFlowy',
      parameter_schema: {
        type: 'object',
        properties: {
          workspace_id: {
            type: 'string',
            description: 'The ID of the workspace'
          },
          name: {
            type: 'string',
            description: 'The name of the database'
          },
          fields: {
            type: 'array',
            items: {
              type: 'object',
              properties: {
                name: {
                  type: 'string',
                  description: 'The name of the field'
                },
                type: {
                  type: 'string',
                  enum: ['text', 'number', 'select', 'multiselect', 'date', 'checkbox', 'url'],
                  description: 'The type of the field'
                },
                options: {
                  type: 'array',
                  items: {
                    type: 'string'
                  },
                  description: 'Options for select and multiselect fields'
                }
              },
              required: ['name', 'type']
            },
            description: 'The fields of the database'
          },
          parent_id: {
            type: 'string',
            description: 'The ID of the parent folder (optional)'
          }
        },
        required: ['workspace_id', 'name', 'fields']
      }
    },
    {
      name: 'appflowy_add_database_row',
      description: 'Add a row to an AppFlowy database',
      parameter_schema: {
        type: 'object',
        properties: {
          database_id: {
            type: 'string',
            description: 'The ID of the database'
          },
          values: {
            type: 'object',
            description: 'The values for the row (field name as key, field value as value)'
          }
        },
        required: ['database_id', 'values']
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
    case 'appflowy_create_document':
      return await createDocument(args);
    case 'appflowy_get_documents':
      return await getDocuments(args);
    case 'appflowy_update_document':
      return await updateDocument(args);
    case 'appflowy_create_database':
      return await createDatabase(args);
    case 'appflowy_add_database_row':
      return await addDatabaseRow(args);
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
}

// AppFlowy API functions
async function createDocument(args) {
  const { workspace_id, name, content, parent_id } = args;
  
  if (!workspace_id || !name) {
    throw new Error('Workspace ID and name are required');
  }
  
  try {
    const payload = {
      workspace_id,
      name,
      content: content || '',
      parent_id: parent_id || null
    };
    
    const response = await appFlowyClient.post('/documents', payload);
    
    return {
      success: true,
      document: {
        id: response.data.id,
        name: response.data.name,
        workspace_id: response.data.workspace_id,
        parent_id: response.data.parent_id,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      }
    };
  } catch (error) {
    logger.error('Error creating AppFlowy document:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function getDocuments(args) {
  const { workspace_id, parent_id, page, limit } = args;
  
  if (!workspace_id) {
    throw new Error('Workspace ID is required');
  }
  
  try {
    const params = {
      workspace_id,
      page: page || 1,
      limit: limit || 10
    };
    
    if (parent_id) {
      params.parent_id = parent_id;
    }
    
    const response = await appFlowyClient.get('/documents', { params });
    
    return {
      success: true,
      documents: response.data.documents.map(doc => ({
        id: doc.id,
        name: doc.name,
        workspace_id: doc.workspace_id,
        parent_id: doc.parent_id,
        created_at: doc.created_at,
        updated_at: doc.updated_at
      })),
      total: response.data.total,
      page: response.data.page,
      limit: response.data.limit
    };
  } catch (error) {
    logger.error('Error getting AppFlowy documents:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function updateDocument(args) {
  const { document_id, name, content } = args;
  
  if (!document_id) {
    throw new Error('Document ID is required');
  }
  
  try {
    const payload = {};
    
    if (name) {
      payload.name = name;
    }
    
    if (content) {
      payload.content = content;
    }
    
    const response = await appFlowyClient.patch(`/documents/${document_id}`, payload);
    
    return {
      success: true,
      document: {
        id: response.data.id,
        name: response.data.name,
        workspace_id: response.data.workspace_id,
        parent_id: response.data.parent_id,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      }
    };
  } catch (error) {
    logger.error('Error updating AppFlowy document:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function createDatabase(args) {
  const { workspace_id, name, fields, parent_id } = args;
  
  if (!workspace_id || !name || !fields) {
    throw new Error('Workspace ID, name, and fields are required');
  }
  
  try {
    const payload = {
      workspace_id,
      name,
      fields,
      parent_id: parent_id || null
    };
    
    const response = await appFlowyClient.post('/databases', payload);
    
    return {
      success: true,
      database: {
        id: response.data.id,
        name: response.data.name,
        workspace_id: response.data.workspace_id,
        parent_id: response.data.parent_id,
        fields: response.data.fields,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      }
    };
  } catch (error) {
    logger.error('Error creating AppFlowy database:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

async function addDatabaseRow(args) {
  const { database_id, values } = args;
  
  if (!database_id || !values) {
    throw new Error('Database ID and values are required');
  }
  
  try {
    const payload = {
      database_id,
      values
    };
    
    const response = await appFlowyClient.post(`/databases/${database_id}/rows`, payload);
    
    return {
      success: true,
      row: {
        id: response.data.id,
        database_id: response.data.database_id,
        values: response.data.values,
        created_at: response.data.created_at,
        updated_at: response.data.updated_at
      }
    };
  } catch (error) {
    logger.error('Error adding AppFlowy database row:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message
    };
  }
}

// Start the server
app.listen(port, () => {
  logger.info(`AppFlowy MCP Server running on port ${port}`);
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