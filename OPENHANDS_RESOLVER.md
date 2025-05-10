# OpenHands Issue Resolver Setup

This repository is configured to use the OpenHands Issue Resolver to automatically address issues. The resolver can be triggered by adding the `fix-me` label to an issue or by mentioning `@openhands-agent` in a comment.

## Setup Instructions

### GitHub Setup

1. **Configure Repository Permissions**:
   - Go to Settings -> Actions -> General -> Workflow permissions
   - Select "Read and write permissions"
   - Enable "Allow Github Actions to create and approve pull requests"

2. **Set up GitHub Secrets**:
   - Go to Settings -> Secrets and variables -> Actions
   - Add the following required secrets:
     - `LLM_API_KEY`: Your LLM API key (Claude API recommended)
   - Add the following optional secrets:
     - `PAT_TOKEN`: A personal access token with read/write scope for "contents", "issues", "pull requests", and "workflows"
     - `LLM_MODEL`: The LLM model to use (default: "anthropic/claude-3-5-sonnet-20241022")
     - `LLM_BASE_URL`: Base URL for LLM API (only if using a proxy)

3. **Set up GitHub Variables** (optional):
   - Go to Settings -> Secrets and variables -> Actions -> Variables
   - Add the following optional variables:
     - `OPENHANDS_MAX_ITER`: Maximum number of iterations (default: 10)
     - `OPENHANDS_MACRO`: Custom trigger word (default: "@openhands-agent")
     - `TARGET_BRANCH`: Target branch for pull requests (default: "main")

### GitLab Setup

1. **Configure GitLab CI/CD Variables**:
   - Go to Settings -> CI/CD -> Variables
   - Add the following required variables:
     - `GITLAB_TOKEN`: Your GitLab personal access token
     - `LLM_API_KEY`: Your LLM API key
   - Add the following optional variables:
     - `LLM_MODEL`: The LLM model to use
     - `LLM_BASE_URL`: Base URL for LLM API (only if using a proxy)
     - `OPENHANDS_MAX_ITER`: Maximum number of iterations
     - `OPENHANDS_MACRO`: Custom trigger word
     - `TARGET_BRANCH`: Target branch for merge requests
     - `GIT_USERNAME`: Your GitLab username
     - `GITLAB_URL`: Your GitLab instance URL (for self-hosted instances)

2. **Configure GitLab Webhooks**:
   - Go to Settings -> Webhooks
   - Add a webhook for issue events and comments
   - Set the URL to your GitLab CI/CD pipeline trigger URL

## Usage

### Using the `fix-me` Label

1. Create or select an issue you want the AI to resolve
2. Add the `fix-me` label to the issue
3. The OpenHands agent will:
   - Analyze the issue and attempt to resolve it
   - Create a draft pull request (GitHub) or merge request (GitLab) with the proposed solution
   - Comment on the issue with the results
   - Remove the `fix-me` label once processed

### Using `@openhands-agent` Mention

1. Create a comment on an issue containing `@openhands-agent`
2. The OpenHands agent will:
   - Analyze the specific comment and attempt to resolve the issue
   - Create a draft pull request (GitHub) or merge request (GitLab) with the proposed solution
   - Comment on the issue with the results

### Iterative Resolution

1. Review the pull request or merge request created by the agent
2. Provide feedback in comments
3. Mention `@openhands-agent` in your comment for further iterations
4. The agent will refine the solution based on your feedback

## Customization

The repository includes a custom instructions file at `.openhands/microagents/repo.md` that provides context-specific guidance to the agent. You can modify this file to include:

- Project-specific context and architecture
- Coding conventions and style guides
- Testing requirements
- Pull request guidelines
- Common issues and solutions

## Troubleshooting

If you encounter issues with the OpenHands Issue Resolver:

1. Check the GitHub Actions or GitLab CI/CD logs for error messages
2. Verify that all required secrets and variables are correctly set
3. Ensure the repository has the necessary permissions configured
4. Check that the issue has the `fix-me` label or contains the trigger phrase
5. Verify API key permissions and validity

## Best Practices

1. Start with simple, well-defined issues to help the agent learn the codebase
2. Provide clear issue descriptions with expected behavior
3. Use the repository microagent file to give context-specific guidance
4. Follow up with specific feedback in PR comments
5. Set appropriate model parameters based on the complexity of your codebase