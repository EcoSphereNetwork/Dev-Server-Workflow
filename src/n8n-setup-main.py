#!/usr/bin/env python3
"""
n8n Setup - Hauptskript

Dieses Skript dient als Einstiegspunkt für die Installation und Konfiguration von n8n
mit Workflows für AFFiNE, AppFlowy, GitLab/GitHub, OpenProject und OpenHands.

Verwendung:
python n8n_setup_main.py --install --env-file .env
"""

import os
import argparse
import time
import subprocess
from pathlib import Path

# Import der Modulskripte
from n8n_setup_utils import load_env_file, create_workflow, create_credential
from n8n_setup_install import install_n8n_docker, get_n8n_api_key
from n8n_setup_credentials import setup_github_credential, setup_openproject_credential
from n8n_setup_workflows import (
    GITHUB_OPENPROJECT_WORKFLOW,
    DOCUMENT_SYNC_WORKFLOW,
    OPENHANDS_WORKFLOW,
    DISCORD_NOTIFICATION_WORKFLOW,
    TIME_TRACKING_WORKFLOW,
    AI_SUMMARY_WORKFLOW
)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Set up n8n with integrated workflows')
    parser.add_argument('--n8n-url', default='http://localhost:5678', help='URL of the n8n instance')
    parser.add_argument('--api-key', help='n8n API key')
    parser.add_argument('--github-token', help='GitHub token for repository access')
    parser.add_argument('--openproject-url', help='OpenProject instance URL')
    parser.add_argument('--openproject-token', help='OpenProject API token')
    parser.add_argument('--install', action='store_true', help='Install n8n locally using Docker')
    parser.add_argument('--env-file', help='Path to .env file with configurations')
    parser.add_argument('--workflows', nargs='+', choices=[
        'github', 'document', 'openhands', 'discord', 'timetracking', 'ai'
    ], default=['github', 'document', 'openhands'], help='Specific workflows to install')
    return parser.parse_args()

def main():
    """Main function."""
    args = parse_args()
    
    # Load environment variables from .env file if provided
    env_vars = load_env_file(args.env_file)
    
    # Use command line arguments or fall back to .env variables
    n8n_url = args.n8n_url or env_vars.get('N8N_URL', 'http://localhost:5678')
    api_key = args.api_key or env_vars.get('N8N_API_KEY')
    github_token = args.github_token or env_vars.get('GITHUB_TOKEN')
    openproject_url = args.openproject_url or env_vars.get('OPENPROJECT_URL')
    openproject_token = args.openproject_token or env_vars.get('OPENPROJECT_TOKEN')
    
    # Install n8n if requested
    if args.install:
        install_n8n_docker()
        
        # If API key was not provided, try to get one
        if not api_key and 'N8N_USER' in env_vars and 'N8N_PASSWORD' in env_vars:
            print("Waiting for n8n to fully start up before getting API key...")
            time.sleep(10)  # Wait a bit more for n8n to fully initialize
            
            try:
                api_key = get_n8n_api_key(
                    n8n_url, 
                    env_vars.get('N8N_USER', 'admin'),
                    env_vars.get('N8N_PASSWORD', 'password')
                )
                print(f"Got API key: {api_key}")
            except Exception as e:
                print(f"Failed to get API key: {str(e)}")
    
    if not api_key:
        print("No API key provided. Please provide an API key to create workflows.")
        return
    
    print("Setting up credentials...")
    # Set up credentials
    github_cred = None
    openproject_cred = None
    
    if github_token:
        github_cred = setup_github_credential(n8n_url, api_key, github_token)
        if github_cred:
            print(f"Created GitHub credential with ID: {github_cred['id']}")
    else:
        print("No GitHub token provided. Skipping GitHub credential setup.")
    
    if openproject_token:
        openproject_cred = setup_openproject_credential(n8n_url, api_key, openproject_token)
        if openproject_cred:
            print(f"Created OpenProject credential with ID: {openproject_cred['id']}")
    else:
        print("No OpenProject token provided. Skipping OpenProject credential setup.")
    
    print("Creating workflows...")
    
    # GitHub-OpenProject Integration
    if 'github' in args.workflows:
        workflow_data = GITHUB_OPENPROJECT_WORKFLOW
        if github_cred:
            # Update GitHub credentials in workflow
            update_github_credentials(workflow_data, github_cred['id'])
        
        if openproject_cred and openproject_url:
            # Update OpenProject credentials in workflow
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        github_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if github_workflow:
            print(f"Created GitHub-OpenProject integration workflow with ID: {github_workflow['id']}")
    
    # Document Sync Workflow
    if 'document' in args.workflows:
        workflow_data = DOCUMENT_SYNC_WORKFLOW
        if openproject_cred and openproject_url:
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        document_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if document_workflow:
            print(f"Created Document Sync workflow with ID: {document_workflow['id']}")
    
    # OpenHands Integration Workflow
    if 'openhands' in args.workflows:
        workflow_data = OPENHANDS_WORKFLOW
        if openproject_cred and openproject_url:
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        openhands_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if openhands_workflow:
            print(f"Created OpenHands integration workflow with ID: {openhands_workflow['id']}")
    
    # Discord Notification Workflow
    if 'discord' in args.workflows:
        workflow_data = DISCORD_NOTIFICATION_WORKFLOW
        if github_cred:
            update_github_credentials(workflow_data, github_cred['id'])
            
        discord_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if discord_workflow:
            print(f"Created Discord notification workflow with ID: {discord_workflow['id']}")
    
    # Time Tracking Workflow
    if 'timetracking' in args.workflows:
        workflow_data = TIME_TRACKING_WORKFLOW
        if github_cred:
            update_github_credentials(workflow_data, github_cred['id'])
        
        if openproject_cred and openproject_url:
            update_openproject_credentials(workflow_data, openproject_cred['id'], openproject_url)
            
        time_tracking_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if time_tracking_workflow:
            print(f"Created Time Tracking workflow with ID: {time_tracking_workflow['id']}")
    
    # AI Summary Workflow
    if 'ai' in args.workflows:
        workflow_data = AI_SUMMARY_WORKFLOW
        if github_cred:
            update_github_credentials(workflow_data, github_cred['id'])
            
        ai_workflow = create_workflow(n8n_url, api_key, workflow_data)
        if ai_workflow:
            print(f"Created AI Summary workflow with ID: {ai_workflow['id']}")
    
    print("\nWorkflow setup complete!")
    print(f"You can access your n8n instance at: {n8n_url}")
    
    # Display webhook URLs for integration
    if 'document' in args.workflows:
        webhook_node = next((node for node in DOCUMENT_SYNC_WORKFLOW['nodes'] 
                             if node.get('type') == 'n8n-nodes-base.webhook'), None)
        if webhook_node:
            webhook_path = webhook_node.get('parameters', {}).get('path', '/webhook')
            print(f"\nDocument Sync Webhook URL: {n8n_url}{webhook_path}")
            print("Use this URL to integrate with AFFiNE/AppFlowy.")
    
    if 'openhands' in args.workflows:
        webhook_node = next((node for node in OPENHANDS_WORKFLOW['nodes'] 
                             if node.get('type') == 'n8n-nodes-base.webhook'), None)
        if webhook_node:
            webhook_path = webhook_node.get('parameters', {}).get('path', '/openhands/webhook')
            print(f"\nOpenHands Webhook URL: {n8n_url}{webhook_path}")
            print("Use this URL to receive notifications from OpenHands.")
    
    print("\nNext steps:")
    print("1. Configure your GitHub repositories to send webhooks to n8n")
    print("2. Set up webhook endpoints in AFFiNE/AppFlowy to notify n8n of document updates")
    print("3. Configure OpenHands to notify n8n when PRs are created")

def update_github_credentials(workflow_data, credential_id):
    """Update GitHub credentials in the workflow."""
    for node in workflow_data['nodes']:
        if node.get('type') in ['n8n-nodes-base.github', 'n8n-nodes-base.githubTrigger']:
            node['credentials'] = {
                'githubApi': credential_id
            }

def update_openproject_credentials(workflow_data, credential_id, openproject_url):
    """Update OpenProject credentials in the workflow."""
    for node in workflow_data['nodes']:
        if (node.get('type') == 'n8n-nodes-base.httpRequest' and 
            'parameters' in node and 
            'url' in node['parameters'] and 
            isinstance(node['parameters']['url'], str) and
            node['parameters']['url'].startswith(openproject_url)):
            node['credentials'] = {
                'httpHeaderAuth': credential_id
            }

if __name__ == "__main__":
    main()
