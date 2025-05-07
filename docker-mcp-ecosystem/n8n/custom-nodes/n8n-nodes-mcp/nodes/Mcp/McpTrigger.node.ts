import {
	INodeType,
	INodeTypeDescription,
	ITriggerFunctions,
	ITriggerResponse,
	NodeOperationError,
} from 'n8n-workflow';

import axios from 'axios';

export class McpTrigger implements INodeType {
	description: INodeTypeDescription = {
		displayName: 'MCP Trigger',
		name: 'mcpTrigger',
		icon: 'file:mcp.svg',
		group: ['trigger'],
		version: 1,
		description: 'Starts the workflow when an MCP server sends an event',
		defaults: {
			name: 'MCP Trigger',
		},
		inputs: [],
		outputs: ['main'],
		credentials: [
			{
				name: 'mcpApi',
				required: true,
			},
		],
		properties: [
			{
				displayName: 'Polling Interval',
				name: 'pollInterval',
				type: 'number',
				default: 10,
				description: 'How often to poll for new events (in seconds)',
			},
			{
				displayName: 'Event Types',
				name: 'eventTypes',
				type: 'multiOptions',
				options: [
					{
						name: 'All Events',
						value: 'all',
						description: 'Trigger on all events',
					},
					{
						name: 'GitHub Events',
						value: 'github',
						description: 'Trigger on GitHub events',
					},
					{
						name: 'GitLab Events',
						value: 'gitlab',
						description: 'Trigger on GitLab events',
					},
					{
						name: 'OpenProject Events',
						value: 'openproject',
						description: 'Trigger on OpenProject events',
					},
					{
						name: 'AppFlowy Events',
						value: 'appflowy',
						description: 'Trigger on AppFlowy events',
					},
				],
				default: ['all'],
				description: 'The events to listen for',
			},
		],
	};

	async trigger(this: ITriggerFunctions): Promise<ITriggerResponse> {
		const credentials = await this.getCredentials('mcpApi');
		const pollInterval = this.getNodeParameter('pollInterval', 0) as number;
		const eventTypes = this.getNodeParameter('eventTypes', 0) as string[];

		const url = credentials.url as string;
		const apiKey = credentials.apiKey as string;
		const serverType = credentials.serverType as string;

		if (!url) {
			throw new NodeOperationError(this.getNode(), 'MCP Server URL is required');
		}

		// Function to poll for events
		const pollEvents = async () => {
			try {
				// Check if the MCP server has an events endpoint
				const response = await axios.post(
					`${url}/mcp`,
					{
						jsonrpc: '2.0',
						id: Date.now(),
						method: 'mcp.getEvents',
						params: {
							types: eventTypes.includes('all') ? [] : eventTypes,
							since: new Date(Date.now() - pollInterval * 1000).toISOString(),
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
					this.logger.error(`MCP Error: ${response.data.error.message}`);
					return;
				}

				const events = response.data.result || [];

				if (events.length > 0) {
					this.logger.debug(`Received ${events.length} events from MCP server`);

					// Emit each event
					for (const event of events) {
						this.emit([this.helpers.returnJsonArray([event])]);
					}
				}
			} catch (error) {
				this.logger.error(`Error polling MCP server: ${error.message}`);
			}
		};

		// Start polling
		const intervalId = setInterval(pollEvents, pollInterval * 1000);

		// Function to stop polling
		async function closeFunction() {
			clearInterval(intervalId);
		}

		// Return the trigger response
		return {
			closeFunction,
		};
	}
}