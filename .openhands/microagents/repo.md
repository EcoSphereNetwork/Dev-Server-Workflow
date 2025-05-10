# Dev-Server-Workflow Repository Guidelines

## Project Overview
The Dev-Server-Workflow repository contains a comprehensive system for managing development workflows, integrating n8n automation, MCP (Message Control Protocol) servers, and AI-assisted tools. The system provides a unified interface for managing development tasks, automating workflows, and monitoring services.

## Architecture
- **Frontend**: React-based web application with Electron desktop integration
- **Backend**: Multiple MCP server implementations for different services
- **Workflows**: n8n workflow definitions for automation tasks
- **Docker**: Containerized deployment configurations for all components
- **CLI**: Command-line tools for management and configuration

## Key Components
1. **MCP Hub**: Central management system for MCP servers
2. **MCP Servers**:
   - Docker MCP: Manages Docker containers and services
   - n8n MCP: Integrates with n8n workflow automation
   - Prompt MCP: Handles prompt engineering and LLM interactions
   - LLM Cost Analyzer MCP: Analyzes and optimizes LLM usage costs
   - OpenHands MCP: Integrates with OpenHands AI capabilities
3. **Frontend Application**: Web and desktop interface for system management
4. **Workflow Definitions**: n8n workflows for various automation tasks
5. **Monitoring System**: Prometheus and Grafana for system monitoring

## Coding Conventions

### Python
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Implement comprehensive error handling with structured error classes
- Use structured logging with appropriate log levels
- Write docstrings for all public functions and classes
- Organize code into logical modules and packages

### JavaScript/TypeScript
- Use TypeScript for all new code
- Follow the project's ESLint configuration
- Use functional components with hooks for React components
- Implement proper error boundaries and loading states
- Use the design system components for UI consistency
- Follow the established directory structure

### General
- Keep functions small and focused on a single responsibility
- Write comprehensive unit tests for all new code
- Use meaningful variable and function names
- Add comments for complex logic
- Follow the existing project structure
- Ensure backward compatibility when modifying existing code

## Testing Requirements
- All Python code should have unit tests using pytest
- Frontend components should have Jest tests
- Integration tests should be added for critical workflows
- Maintain minimum 90% test coverage for new code
- Test error handling and edge cases
- Ensure tests are isolated and don't depend on external services

## Error Handling
- Use the structured error handling system in `src/core/error_handling.py`
- Categorize errors appropriately (configuration, network, validation, etc.)
- Include relevant context in error messages
- Implement proper recovery mechanisms where appropriate
- Log errors with appropriate severity levels

## Logging
- Use the structured logging system in `src/core/logging.py`
- Include relevant context in log messages
- Use appropriate log levels (debug, info, warning, error, critical)
- Avoid logging sensitive information
- Include correlation IDs for tracking related log entries

## Pull Request Guidelines
- PRs should address a single issue or feature
- Include a clear description of the changes
- Reference the issue being addressed
- Ensure all tests pass
- Update documentation as needed
- Add appropriate labels
- Follow the established branch naming convention

## Deployment Considerations
- Docker configurations should be updated for any new services
- Environment variables should be documented
- Consider backward compatibility
- Update the deployment documentation
- Ensure proper health checks are implemented
- Consider resource requirements and constraints

## Directory Structure
- `/src`: Source code for the application
  - `/src/mcp_hub`: MCP Hub implementation
  - `/src/mcp_servers`: MCP server implementations
  - `/src/workflows`: Workflow definitions
  - `/src/core`: Core utilities and shared code
- `/frontend`: Frontend application code
- `/cli`: Command-line interface tools
- `/docker`: Docker configurations
- `/tests`: Test code
- `/docs`: Documentation

When resolving issues, please follow these guidelines and maintain the existing code style and architecture. Focus on making minimal changes to address the specific issue while ensuring proper error handling, logging, and testing.

## Common Issues and Solutions
- Import errors: Check the import paths and ensure they follow the established patterns
- Docker configuration issues: Verify environment variables and volume mounts
- MCP server communication problems: Check network configuration and service discovery
- Frontend rendering issues: Verify component props and state management
- Workflow execution failures: Check n8n configuration and credentials

## Performance Considerations
- Optimize database queries for large datasets
- Implement caching where appropriate
- Consider asynchronous processing for long-running tasks
- Monitor resource usage (CPU, memory, network)
- Implement pagination for large result sets

## Security Best Practices
- Validate all user inputs
- Use environment variables for sensitive configuration
- Implement proper authentication and authorization
- Follow the principle of least privilege
- Sanitize data before displaying or storing
- Use secure communication protocols