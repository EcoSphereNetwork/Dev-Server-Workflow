#!/usr/bin/env python3

"""
GitHub Integration for MCP Servers

This script configures the GitHub integration for the MCP servers.
"""

import argparse
import json
import logging
import os
import sys
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('github-integration.log')
    ]
)
logger = logging.getLogger('github-integration')

def validate_github_token(token):
    """Validate the GitHub token by making a test API call."""
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get("https://api.github.com/user", headers=headers)
        
        if response.status_code == 200:
            user_data = response.json()
            logger.info(f"✅ GitHub token is valid. Authenticated as: {user_data['login']}")
            return True, user_data
        else:
            logger.error(f"❌ GitHub token validation failed: {response.status_code} - {response.text}")
            return False, None
    
    except Exception as e:
        logger.error(f"❌ Error validating GitHub token: {e}")
        return False, None

def check_token_permissions(token):
    """Check the permissions of the GitHub token."""
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        response = requests.get("https://api.github.com/user", headers=headers)
        
        if response.status_code == 200:
            # Get the scopes from the response headers
            scopes = response.headers.get("X-OAuth-Scopes", "").split(", ")
            
            logger.info(f"Token scopes: {scopes}")
            
            # Check if the token has the required scopes
            required_scopes = ["repo"]
            missing_scopes = [scope for scope in required_scopes if scope not in scopes]
            
            if missing_scopes:
                logger.warning(f"⚠️ Token is missing the following required scopes: {missing_scopes}")
                return False, missing_scopes
            else:
                logger.info("✅ Token has all required scopes")
                return True, []
        else:
            logger.error(f"❌ Failed to check token permissions: {response.status_code} - {response.text}")
            return False, []
    
    except Exception as e:
        logger.error(f"❌ Error checking token permissions: {e}")
        return False, []

def configure_github_webhook(token, repo_owner, repo_name, webhook_url, secret=None):
    """Configure a GitHub webhook for the repository."""
    try:
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        # Check if the webhook already exists
        response = requests.get(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks",
            headers=headers
        )
        
        if response.status_code == 200:
            hooks = response.json()
            for hook in hooks:
                if hook["config"]["url"] == webhook_url:
                    logger.info(f"✅ Webhook already exists for {repo_owner}/{repo_name}")
                    return True, hook["id"]
        
        # Create the webhook
        payload = {
            "name": "web",
            "active": True,
            "events": ["push", "pull_request", "issues", "issue_comment", "pull_request_review", "pull_request_review_comment"],
            "config": {
                "url": webhook_url,
                "content_type": "json"
            }
        }
        
        if secret:
            payload["config"]["secret"] = secret
        
        response = requests.post(
            f"https://api.github.com/repos/{repo_owner}/{repo_name}/hooks",
            headers=headers,
            json=payload
        )
        
        if response.status_code in (200, 201):
            hook_data = response.json()
            logger.info(f"✅ Webhook created for {repo_owner}/{repo_name} with ID: {hook_data['id']}")
            return True, hook_data["id"]
        else:
            logger.error(f"❌ Failed to create webhook: {response.status_code} - {response.text}")
            return False, None
    
    except Exception as e:
        logger.error(f"❌ Error creating webhook: {e}")
        return False, None

def update_env_file(env_file, github_token):
    """Update the .env file with the GitHub token."""
    try:
        # Read the current .env file
        if os.path.exists(env_file):
            with open(env_file, "r") as f:
                lines = f.readlines()
        else:
            lines = []
        
        # Update or add the GitHub token
        token_line_found = False
        for i, line in enumerate(lines):
            if line.startswith("GITHUB_TOKEN="):
                lines[i] = f"GITHUB_TOKEN={github_token}\n"
                token_line_found = True
                break
        
        if not token_line_found:
            lines.append(f"GITHUB_TOKEN={github_token}\n")
        
        # Write the updated .env file
        with open(env_file, "w") as f:
            f.writelines(lines)
        
        logger.info(f"✅ Updated {env_file} with GitHub token")
        return True
    
    except Exception as e:
        logger.error(f"❌ Error updating {env_file}: {e}")
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="GitHub Integration for MCP Servers")
    parser.add_argument("--github-token", required=True, help="GitHub personal access token")
    parser.add_argument("--repo", help="GitHub repository in the format owner/repo")
    parser.add_argument("--webhook-url", default="http://localhost:5678/webhook/github-to-openproject", help="Webhook URL")
    parser.add_argument("--webhook-secret", help="Webhook secret")
    parser.add_argument("--env-file", default="/workspace/Dev-Server-Workflow/docker-mcp-servers/.env", help="Path to the .env file")
    
    args = parser.parse_args()
    
    # Validate the GitHub token
    valid_token, user_data = validate_github_token(args.github_token)
    if not valid_token:
        logger.error("GitHub token validation failed. Please check your token and try again.")
        return 1
    
    # Check token permissions
    has_permissions, missing_scopes = check_token_permissions(args.github_token)
    if not has_permissions:
        logger.warning(f"GitHub token is missing required scopes: {missing_scopes}")
        logger.warning("Please update your token with the required scopes and try again.")
        logger.warning("You can create a new token at: https://github.com/settings/tokens")
    
    # Update the .env file
    if not update_env_file(args.env_file, args.github_token):
        logger.error("Failed to update .env file. Please update it manually.")
    
    # Configure GitHub webhook if repo is provided
    if args.repo:
        try:
            repo_parts = args.repo.split("/")
            if len(repo_parts) != 2:
                logger.error("Invalid repository format. Please use the format owner/repo.")
                return 1
            
            repo_owner, repo_name = repo_parts
            
            success, hook_id = configure_github_webhook(
                args.github_token,
                repo_owner,
                repo_name,
                args.webhook_url,
                args.webhook_secret
            )
            
            if not success:
                logger.error("Failed to configure GitHub webhook. Please configure it manually.")
        except Exception as e:
            logger.error(f"Error configuring GitHub webhook: {e}")
    
    logger.info("✅ GitHub integration completed!")
    logger.info(f"GitHub user: {user_data['login']}")
    logger.info(f"GitHub token: {args.github_token[:4]}...{args.github_token[-4:]}")
    
    if args.repo:
        logger.info(f"GitHub repository: {args.repo}")
        logger.info(f"Webhook URL: {args.webhook_url}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())