import { INodeTypeData } from 'n8n-workflow';
import { Mcp } from './nodes/Mcp/Mcp.node';
import { McpTrigger } from './nodes/Mcp/McpTrigger.node';

export const nodeTypes: INodeTypeData = {
	Mcp,
	McpTrigger,
};