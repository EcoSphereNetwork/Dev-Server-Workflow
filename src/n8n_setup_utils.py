#!/usr/bin/env python3
"""
n8n Setup - Hilfsfunktionen

Dieses Modul enthält gemeinsam genutzte Hilfsfunktionen für die n8n Setup-Skripte.
"""

import os
import json
import requests

def load_env_file(env_file):
    """Load environment variables from .env file."""
    if not env_file or not os.path.isfile(env_file):
        return {}
    
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            key, value = line.split('=', 1)
            env_vars[key.strip()] = value.strip().strip('"\'')
    
    return env_vars

def create_workflow(n8n_url, api_key, workflow_data):
    """Create a workflow in n8n."""
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f"{n8n_url}/rest/workflows",
        headers=headers,
        json=workflow_data
    )
    
    if response.status_code != 200:
        print(f"Failed to create workflow: {response.text}")
        return None
    
    return response.json()

def create_credential(n8n_url, api_key, credential_data):
    """Create a credential in n8n."""
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f"{n8n_url}/rest/credentials",
        headers=headers,
        json=credential_data
    )
    
    if response.status_code != 200:
        print(f"Failed to create credential: {response.text}")
        return None
    
    return response.json()

def update_workflow(n8n_url, api_key, workflow_id, workflow_data):
    """Update an existing workflow in n8n."""
    headers = {
        'X-N8N-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    response = requests.put(
        f"{n8n_url}/rest/workflows/{workflow_id}",
        headers=headers,
        json=workflow_data
    )
    
    if response.status_code != 200:
        print(f"Failed to update workflow: {response.text}")
        return None
    
    return response.json()

def get_workflows(n8n_url, api_key):
    """Get all workflows from n8n."""
    headers = {
        'X-N8N-API-KEY': api_key
    }
    
    response = requests.get(
        f"{n8n_url}/rest/workflows",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get workflows: {response.text}")
        return None
    
    return response.json()

def get_credentials(n8n_url, api_key):
    """Get all credentials from n8n."""
    headers = {
        'X-N8N-API-KEY': api_key
    }
    
    response = requests.get(
        f"{n8n_url}/rest/credentials",
        headers=headers
    )
    
    if response.status_code != 200:
        print(f"Failed to get credentials: {response.text}")
        return None
    
    return response.json()

def find_credential_by_name(n8n_url, api_key, name):
    """Find a credential by name."""
    credentials = get_credentials(n8n_url, api_key)
    if not credentials:
        return None
    
    for credential in credentials:
        if credential.get('name') == name:
            return credential
    
    return None

def find_workflow_by_name(n8n_url, api_key, name):
    """Find a workflow by name."""
    workflows = get_workflows(n8n_url, api_key)
    if not workflows:
        return None
    
    for workflow in workflows:
        if workflow.get('name') == name:
            return workflow
    
    return None

def activate_workflow(n8n_url, api_key, workflow_id, active=True):
    """Activate or deactivate a workflow.
    
    Args:
        n8n_url: URL of the n8n instance
        api_key: n8n API key
        workflow_id: ID of the workflow to activate/deactivate
        active: True to activate, False to deactivate
        
    Returns:
        True if successful, False otherwise
    """
    try:
        if not workflow_id:
            print("Error: Workflow ID is required to activate/deactivate a workflow")
            return False
            
        headers = {
            'X-N8N-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        
        data = {
            'active': active
        }
        
        # Überprüfe zuerst den aktuellen Status des Workflows
        status_response = requests.get(
            f"{n8n_url}/rest/workflows/{workflow_id}",
            headers=headers
        )
        
        if status_response.status_code != 200:
            print(f"Failed to get workflow status: {status_response.text}")
            return False
            
        current_status = status_response.json().get('active', False)
        
        # Wenn der Workflow bereits im gewünschten Status ist, nichts tun
        if current_status == active:
            print(f"Workflow is already {'active' if active else 'inactive'}")
            return True
        
        # Aktiviere/Deaktiviere den Workflow
        response = requests.patch(
            f"{n8n_url}/rest/workflows/{workflow_id}/activate",
            headers=headers,
            json=data
        )
        
        if response.status_code != 200:
            print(f"Failed to {'activate' if active else 'deactivate'} workflow: {response.text}")
            return False
        
        print(f"Successfully {'activated' if active else 'deactivated'} workflow")
        return True
        
    except Exception as e:
        print(f"Error {'activating' if active else 'deactivating'} workflow: {str(e)}")
        return False
