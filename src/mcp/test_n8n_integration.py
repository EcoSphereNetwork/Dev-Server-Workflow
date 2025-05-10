#!/usr/bin/env python3
"""
Test script for the n8n integration layer.

This script tests the functionality of the n8n integration layer.
"""

import os
import sys
import json
import asyncio
import logging
from pathlib import Path

# Add the parent directory to the path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

# Import the integration module
from mcp.n8n_integration import N8nIntegration, initialize_integration

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("test-n8n-integration")


async def test_connection():
    """Test connection to n8n."""
    logger.info("Testing connection to n8n...")
    
    # Create integration instance
    integration = N8nIntegration()
    
    try:
        # Connect to n8n
        await integration.connect()
        logger.info("✅ Connection successful")
        
        # Get status
        status = await integration.get_status()
        logger.info(f"Status: {json.dumps(status, indent=2)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Connection failed: {e}")
        return False


async def test_workflows():
    """Test workflow operations."""
    logger.info("Testing workflow operations...")
    
    # Create integration instance
    integration = N8nIntegration()
    
    try:
        # Connect to n8n
        await integration.connect()
        
        # Get all workflows
        workflows = await integration.get_workflows()
        logger.info(f"Found {len(workflows)} workflows")
        
        if workflows:
            # Get details of the first workflow
            workflow_id = workflows[0]["id"]
            workflow = await integration.get_workflow(workflow_id)
            logger.info(f"Workflow details: {workflow['name']}")
            
            # Export as template
            template = await integration.export_workflow_to_template(workflow_id)
            logger.info(f"Exported workflow as template: {template.name}")
            
            # Sync to orchestrator
            orchestrator_id = await integration.sync_workflow_to_orchestrator(workflow_id)
            logger.info(f"Synced workflow to orchestrator: {orchestrator_id}")
        
        logger.info("✅ Workflow operations successful")
        return True
    except Exception as e:
        logger.error(f"❌ Workflow operations failed: {e}")
        return False


async def test_webhook():
    """Test webhook functionality."""
    logger.info("Testing webhook functionality...")
    
    # Create integration instance
    integration = N8nIntegration()
    
    try:
        # Connect to n8n
        await integration.connect()
        
        # Define a webhook handler
        async def webhook_handler(data):
            logger.info(f"Webhook received: {json.dumps(data, indent=2)}")
            return {"processed": True}
        
        # Register webhook handler
        webhook_id = await integration.register_webhook("*", "webhook", webhook_handler)
        logger.info(f"Registered webhook handler: {webhook_id}")
        
        # Simulate a webhook call
        webhook_data = {
            "workflowId": "test-workflow",
            "executionId": "test-execution",
            "eventType": "webhook",
            "timestamp": "2023-01-01T00:00:00Z",
            "payload": {"message": "Hello from webhook"}
        }
        
        result = await integration.handle_webhook(webhook_data, {})
        logger.info(f"Webhook result: {json.dumps(result, indent=2)}")
        
        # Unregister webhook handler
        await integration.unregister_webhook(webhook_id)
        logger.info(f"Unregistered webhook handler: {webhook_id}")
        
        logger.info("✅ Webhook functionality successful")
        return True
    except Exception as e:
        logger.error(f"❌ Webhook functionality failed: {e}")
        return False


async def main():
    """Run all tests."""
    logger.info("Starting n8n integration tests...")
    
    # Run tests
    connection_ok = await test_connection()
    if connection_ok:
        await test_workflows()
        await test_webhook()
    
    logger.info("Tests completed")


if __name__ == "__main__":
    asyncio.run(main())