import {
	IExecuteFunctions,
	INodeExecutionData,
	INodeType,
	INodeTypeDescription,
	NodeOperationError,
} from 'n8n-workflow';

import axios from 'axios';

export class Mcp implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'MCP',
		name: 'mcp',
		icon: 'file:mcp.svg',
		group: ['transform'],
		version: 1,
		subtitle: '={{$parameter["operation"] + ": " + $parameter["resource"]}}',
		description: 'Interact with MCP servers',
		defaults: {
			name: 'MCP',
		},
		inputs: ['main'],
		outputs: ['main'],
		credentials: [
			{
				name: 'mcpApi',
				required: true,
			},
		],
		properties: [
			{
				displayName: 'Operation',
				name: 'operation',
				type: 'options',
				noDataExpression: true,
				options: [
					{
						name: 'List Tools',
						value: 'listTools',
						description: 'List available tools on the MCP server',
						action: 'List available tools on the MCP server',
					},
					{
						name: 'Call Tool',
						value: 'callTool',
						description: 'Call a tool on the MCP server',
						action: 'Call a tool on the MCP server',
					},
				],
				default: 'listTools',
			},
			{
				displayName: 'Tool Name',
				name: 'toolName',
				type: 'string',
				default: '',
				required: true,
				displayOptions: {
					show: {
						operation: ['callTool'],
					},
				},
				description: 'Name of the tool to call',
			},
			{
				displayName: 'Arguments',
				name: 'arguments',
				type: 'json',
				default: '{}',
				displayOptions: {
					show: {
						operation: ['callTool'],
					},
				},
				description: 'Arguments to pass to the tool (as JSON object)',
			},
		],
	};

	async execute(this: IExecuteFunctions): Promise<INodeExecutionData[][]> {
		const items = this.getInputData();
		const returnData: INodeExecutionData[] = [];
		const operation = this.getNodeParameter('operation', 0) as string;
		const credentials = await this.getCredentials('mcpApi');

		const url = credentials.url as string;
		const apiKey = credentials.apiKey as string;

		for (let i = 0; i < items.length; i++) {
			try {
				if (operation === 'listTools') {
					// List available tools
					const response = await axios.post(
						`${url}/mcp`,
						{
							jsonrpc: '2.0',
							id: Date.now(),
							method: 'mcp.listTools',
						},
						{
							headers: {
								'Content-Type': 'application/json',
								...(apiKey ? { 'X-API-Key': apiKey } : {}),
							},
						},
					);

					if (response.data.error) {
						throw new NodeOperationError(this.getNode(), `MCP Error: ${response.data.error.message}`);
					}

					returnData.push({
						json: {
							tools: response.data.result,
						},
					});
				} else if (operation === 'callTool') {
					// Call a tool
					const toolName = this.getNodeParameter('toolName', i) as string;
					const argumentsJson = this.getNodeParameter('arguments', i) as string;
					let toolArguments;

					try {
						toolArguments = JSON.parse(argumentsJson);
					} catch (error) {
						throw new NodeOperationError(this.getNode(), 'Invalid JSON in arguments field');
					}

					const response = await axios.post(
						`${url}/mcp`,
						{
							jsonrpc: '2.0',
							id: Date.now(),
							method: 'mcp.callTool',
							params: {
								name: toolName,
								arguments: toolArguments,
							},
						},
						{
							headers: {
								'Content-Type': 'application/json',
								...(apiKey ? { 'X-API-Key': apiKey } : {}),
							},
						},
					);

					if (response.data.error) {
						throw new NodeOperationError(this.getNode(), `MCP Error: ${response.data.error.message}`);
					}

					returnData.push({
						json: response.data.result,
					});
				}
			} catch (error) {
				if (this.continueOnFail()) {
					returnData.push({
						json: {
							error: error.message,
						},
					});
					continue;
				}
				throw error;
			}
		}

		return [returnData];
	}
}