import {
	ICredentialType,
	INodeProperties,
} from 'n8n-workflow';

export class McpApi implements ICredentialType {
	name = 'mcpApi';
	displayName = 'MCP API';
	documentationUrl = 'https://github.com/EcoSphereNetwork/Dev-Server-Workflow';
	properties: INodeProperties[] = [
		{
			displayName: 'MCP Server URL',
			name: 'url',
			type: 'string',
			default: 'http://localhost:3001',
			placeholder: 'http://localhost:3001',
			description: 'URL of the MCP server',
			required: true,
		},
		{
			displayName: 'API Key',
			name: 'apiKey',
			type: 'string',
			typeOptions: {
				password: true,
			},
			default: '',
			description: 'API key for the MCP server (if required)',
		},
		{
			displayName: 'Server Type',
			name: 'serverType',
			type: 'options',
			options: [
				{
					name: 'GitHub',
					value: 'github',
				},
				{
					name: 'GitLab',
					value: 'gitlab',
				},
				{
					name: 'OpenProject',
					value: 'openproject',
				},
				{
					name: 'AppFlowy',
					value: 'appflowy',
				},
				{
					name: 'Other',
					value: 'other',
				},
			],
			default: 'github',
			description: 'Type of MCP server',
		},
	];
}