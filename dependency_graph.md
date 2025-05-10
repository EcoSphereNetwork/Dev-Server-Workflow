# Dependency Graph

This document provides a comprehensive overview of the dependencies between components in the Dev-Server-Workflow repository.

## Visual Dependency Graph

![Dependency Graph](dependency_graph.png)

## Component Dependencies

### setup

Dependencies:

- None

### setup_package

Dependencies:

- setuptools (external)

### src.openhands.cli

Dependencies:

- .agent (external)
- common (external)

### src.openhands.__init__

Dependencies:

- None

### src.openhands.agent

Dependencies:

- ..common.config_manager (external)
- ..mcp.client (external)
- requests (external)

### src.monitoring.prometheus_exporter

Dependencies:

- common (external)

### src.test-mcp-server

Dependencies:

- None

### src.n8n_setup_install

Dependencies:

- None

### src.llm_cost_analyzer.llm_cost_analyzer.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src.llm_cost_analyzer.llm_cost_analyzer.models.__init__

Dependencies:

- None

### src.llm_cost_analyzer.llm_cost_analyzer.models.llm

Dependencies:

- pydantic (external)

### src.llm_cost_analyzer.llm_cost_analyzer.utils.logger

Dependencies:

- ..core.config (external)

### src.llm_cost_analyzer.llm_cost_analyzer.utils.__init__

Dependencies:

- None

### src.llm_cost_analyzer.llm_cost_analyzer.api.router

Dependencies:

- .endpoints (external)
- fastapi (external)

### src.llm_cost_analyzer.llm_cost_analyzer.api.__init__

Dependencies:

- None

### src.llm_cost_analyzer.llm_cost_analyzer.api.endpoints.analyze

Dependencies:

- ...core.llm_selector (external)
- fastapi (external)
- pydantic (external)

### src.llm_cost_analyzer.llm_cost_analyzer.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src.llm_cost_analyzer.llm_cost_analyzer.api.endpoints.estimate

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- fastapi (external)
- pydantic (external)

### src.llm_cost_analyzer.llm_cost_analyzer.api.endpoints.__init__

Dependencies:

- None

### src.llm_cost_analyzer.llm_cost_analyzer.__init__

Dependencies:

- None

### src.llm_cost_analyzer.llm_cost_analyzer.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)

### src.llm_cost_analyzer.llm_cost_analyzer.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src.llm_cost_analyzer.llm_cost_analyzer.core.__init__

Dependencies:

- None

### src.llm_cost_analyzer.llm_cost_analyzer.core.llm_selector

Dependencies:

- ..models.llm (external)
- .config (external)

### src.mcp.mcp-client

Dependencies:

- aiohttp (external)
- common (external)

### src.mcp.interfaces.mcp_server_interface

Dependencies:

- .mcp_tool (external)

### src.mcp.interfaces.mcp_tool

Dependencies:


### src.mcp.interfaces.__init__

Dependencies:

- .mcp_server_interface (external)
- .mcp_tool (external)

### src.mcp.base_mcp_server_improved

Dependencies:

- aiohttp (external)
- common (external)
- interfaces (external)
- signal (external)

### src.mcp.n8n_mcp_server

Dependencies:

- aiohttp (external)
- common (external)
- signal (external)

### src.mcp.servers.openhands.openhands_mcp_server

Dependencies:

- [src.core.config_manager](#src.core.config_manager)
- [src.core.logger](#src.core.logger)
- [src.core.utils.docker_utils](#src.core.utils.docker_utils)
- [src.core.utils.network_utils](#src.core.utils.network_utils)
- [src.core.utils.process_utils](#src.core.utils.process_utils)
- [src.core.utils.system_utils](#src.core.utils.system_utils)
- src.mcp_servers.base.base_mcp_server (external)
- src.openhands (external)

### src.mcp.servers.openhands.__init__

Dependencies:

- None

### src.mcp.servers.n8n.n8n_mcp_server

Dependencies:

- [src.core.config_manager](#src.core.config_manager)
- [src.core.logger](#src.core.logger)
- [src.core.utils.docker_utils](#src.core.utils.docker_utils)
- [src.core.utils.network_utils](#src.core.utils.network_utils)
- [src.core.utils.process_utils](#src.core.utils.process_utils)
- [src.core.utils.system_utils](#src.core.utils.system_utils)
- src.mcp_servers.base.base_mcp_server (external)

### src.mcp.servers.n8n.__init__

Dependencies:

- None

### src.mcp.servers.prompt.__init__

Dependencies:

- None

### src.mcp.servers.__init__

Dependencies:

- None

### src.mcp.servers.generator.__init__

Dependencies:

- None

### src.mcp.servers.llm_cost.__init__

Dependencies:

- None

### src.mcp.servers.docker.docker_mcp_server

Dependencies:

- [src.core.config_manager](#src.core.config_manager)
- [src.core.logger](#src.core.logger)
- [src.core.utils.docker_utils](#src.core.utils.docker_utils)
- [src.core.utils.network_utils](#src.core.utils.network_utils)
- [src.core.utils.process_utils](#src.core.utils.process_utils)
- [src.core.utils.system_utils](#src.core.utils.system_utils)
- src.mcp_servers.base.base_mcp_server (external)

### src.mcp.servers.docker.__init__

Dependencies:

- None

### src.mcp.generator_server

Dependencies:

- common (external)

### src.mcp.docker_mcp_server_improved

Dependencies:

- base_mcp_server (external)
- common (external)

### src.mcp.utils

Dependencies:

- ..common.docker_utils (external)
- .client (external)
- .error_handling (external)

### src.mcp.test-mcp-integration

Dependencies:

- common (external)
- mcp_client (external)

### src.mcp.base.base_mcp_server

Dependencies:

- aiohttp (external)
- signal (external)
- [src.core.config_manager](#src.core.config_manager)
- [src.core.logger](#src.core.logger)
- [src.core.utils.docker_utils](#src.core.utils.docker_utils)
- [src.core.utils.network_utils](#src.core.utils.network_utils)
- [src.core.utils.process_utils](#src.core.utils.process_utils)
- [src.core.utils.system_utils](#src.core.utils.system_utils)
- src.mcp_servers.base.mcp_server_interface (external)
- src.mcp_servers.base.mcp_tool (external)

### src.mcp.base.__init__

Dependencies:

- None

### src.mcp.n8n_mcp_server_improved

Dependencies:

- base_mcp_server (external)
- common (external)

### src.mcp.openhands_server_improved

Dependencies:

- base_mcp_server (external)
- common (external)

### src.n8n_setup_workflows_mcp_enhanced

Dependencies:

- None

### src.mcp_servers.n8n_mcp_server.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- uvicorn (external)

### src.mcp_servers.n8n_mcp_server.mcp_interface

Dependencies:

- .core.audit (external)
- .core.auth (external)
- .core.metrics (external)
- .core.n8n_client (external)
- .utils.logger (external)
- src.mcp_servers.base.base_mcp_server (external)
- src.mcp_servers.base.mcp_tool (external)

### src.mcp_servers.n8n_mcp_server.models.__init__

Dependencies:

- None

### src.mcp_servers.n8n_mcp_server.models.workflow

Dependencies:

- pydantic (external)

### src.mcp_servers.n8n_mcp_server.utils.logger

Dependencies:

- ..core.config (external)

### src.mcp_servers.n8n_mcp_server.utils.__init__

Dependencies:

- None

### src.mcp_servers.n8n_mcp_server.api.router

Dependencies:

- ..core.audit (external)
- ..core.auth (external)
- ..core.metrics (external)
- ..core.n8n_client (external)
- ..models.workflow (external)
- ..utils.logger (external)
- fastapi (external)

### src.mcp_servers.n8n_mcp_server.api.__init__

Dependencies:

- None

### src.mcp_servers.n8n_mcp_server.n8n_mcp_server

Dependencies:

- aiohttp (external)
- common (external)
- signal (external)

### src.mcp_servers.n8n_mcp_server.__init__

Dependencies:

- None

### src.mcp_servers.n8n_mcp_server.utils

Dependencies:

- ..common.docker_utils (external)
- .client (external)
- .error_handling (external)

### src.mcp_servers.n8n_mcp_server.core.config

Dependencies:

- pydantic (external)

### src.mcp_servers.n8n_mcp_server.core.n8n_client

Dependencies:

- ..core.config (external)
- ..utils.logger (external)
- aiohttp (external)

### src.mcp_servers.n8n_mcp_server.core.audit

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src.mcp_servers.n8n_mcp_server.core.__init__

Dependencies:

- None

### src.mcp_servers.n8n_mcp_server.core.auth

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src.mcp_servers.n8n_mcp_server.core.metrics

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src.mcp_servers.docker_mcp.handlers

Dependencies:

- .docker_executor (external)
- mcp.types (external)
- yaml (external)

### src.mcp_servers.docker_mcp.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- uvicorn (external)

### src.mcp_servers.docker_mcp.mcp_interface

Dependencies:

- .core.audit (external)
- .core.auth (external)
- .core.docker_executor (external)
- .core.metrics (external)
- .utils.logger (external)
- src.mcp_servers.base.base_mcp_server (external)
- src.mcp_servers.base.mcp_tool (external)

### src.mcp_servers.docker_mcp.models.docker

Dependencies:

- pydantic (external)

### src.mcp_servers.docker_mcp.models.__init__

Dependencies:

- None

### src.mcp_servers.docker_mcp.utils.logger

Dependencies:

- ..core.config (external)

### src.mcp_servers.docker_mcp.utils.__init__

Dependencies:

- None

### src.mcp_servers.docker_mcp.api.router

Dependencies:

- ..core.audit (external)
- ..core.auth (external)
- ..core.docker_executor (external)
- ..core.metrics (external)
- ..models.docker (external)
- ..utils.logger (external)
- fastapi (external)
- fastapi.responses (external)

### src.mcp_servers.docker_mcp.api.__init__

Dependencies:

- None

### src.mcp_servers.docker_mcp.server

Dependencies:

- .audit (external)
- .auth (external)
- .handlers (external)
- .http_server (external)
- .metrics (external)
- mcp.server (external)
- mcp.server.models (external)
- mcp.server.stdio (external)
- mcp.types (external)
- as (external)
- signal (external)

### src.mcp_servers.docker_mcp.audit

Dependencies:


### src.mcp_servers.docker_mcp.__init__

Dependencies:

- .server (external)

### src.mcp_servers.docker_mcp.http_server

Dependencies:

- aiohttp (external)

### src.mcp_servers.docker_mcp.auth

Dependencies:


### src.mcp_servers.docker_mcp.docker_executor

Dependencies:


### src.mcp_servers.docker_mcp.metrics

Dependencies:

- prometheus_client (external)

### src.mcp_servers.docker_mcp.core.config

Dependencies:

- pydantic (external)

### src.mcp_servers.docker_mcp.core.audit

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src.mcp_servers.docker_mcp.core.__init__

Dependencies:

- None

### src.mcp_servers.docker_mcp.core.auth

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src.mcp_servers.docker_mcp.core.docker_executor

Dependencies:

- ..core.config (external)
- ..utils.logger (external)
- docker (external)

### src.mcp_servers.docker_mcp.core.metrics

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.models.__init__

Dependencies:

- None

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.models.template

Dependencies:

- pydantic (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.models.llm

Dependencies:

- pydantic (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.models.chat

Dependencies:

- pydantic (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.utils.logger

Dependencies:

- ..core.config (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.utils.__init__

Dependencies:

- None

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.router

Dependencies:

- .endpoints (external)
- fastapi (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.__init__

Dependencies:

- None

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.optimize

Dependencies:

- ...core.prompt_optimizer (external)
- ...core.template_manager (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.cost

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- ...core.template_manager (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.__init__

Dependencies:

- None

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.templates

Dependencies:

- ...core.template_manager (external)
- ...models.template (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.chat

Dependencies:

- ...core.llm_selector (external)
- ...core.memory_manager (external)
- ...core.template_manager (external)
- ...models.chat (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.templates.__init__

Dependencies:

- None

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.__init__

Dependencies:

- None

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.memory_manager

Dependencies:

- ..models.chat (external)
- .config (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)
- .template_manager (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.prompt_optimizer

Dependencies:

- ..models.template (external)
- .template_manager (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.template_manager

Dependencies:

- ..models.template (external)
- .config (external)
- promplate (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.__init__

Dependencies:

- None

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.llm_selector

Dependencies:

- ..models.llm (external)
- ..models.template (external)
- .config (external)

### src.mcp_servers.prompt_mcp_server.prompt_mcp_server.memory.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.models.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.models.llm

Dependencies:

- pydantic (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.utils.logger

Dependencies:

- ..core.config (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.utils.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.router

Dependencies:

- .endpoints (external)
- fastapi (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.endpoints.analyze

Dependencies:

- ...core.llm_selector (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.endpoints.estimate

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.endpoints.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.core.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.core.llm_selector

Dependencies:

- ..models.llm (external)
- .config (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .core.llm_selector (external)
- .core.task_cost_estimator (external)
- .mcp_interface (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.mcp_interface

Dependencies:

- .core.llm_selector (external)
- .core.task_cost_estimator (external)
- fastapi (external)
- websockets (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.models.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.models.llm

Dependencies:

- pydantic (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.utils.logger

Dependencies:

- ..core.config (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.utils.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.router

Dependencies:

- ..mcp_interface (external)
- .endpoints (external)
- fastapi (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.endpoints.analyze

Dependencies:

- ...core.llm_selector (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.endpoints.estimate

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- fastapi (external)
- pydantic (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.endpoints.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.core.__init__

Dependencies:

- None

### src.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.core.llm_selector

Dependencies:

- ..models.llm (external)
- .config (external)

### src.n8n_setup_workflows_github

Dependencies:

- None

### src.llm_selector.test_llm_selector

Dependencies:

- common (external)
- llm_selector (external)

### src.llm_selector.llm_selector_api

Dependencies:

- common (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- llm_selector (external)
- pydantic (external)
- uvicorn (external)

### src.llm_selector.llm_selector

Dependencies:

- common (external)
- requests (external)

### src.llm_selector.llm_selector_client

Dependencies:

- common (external)
- requests (external)

### src.n8n_setup_utils

Dependencies:

- None

### src.common.docker_utils

Dependencies:


### src.common.config_manager

Dependencies:

- yaml (external)

### src.common.__init__

Dependencies:

- None

### src.n8n_setup_credentials

Dependencies:

- None

### src.n8n_setup_workflows_document

Dependencies:

- None

### src.__init__

Dependencies:

- None

### src.n8n_setup_workflows_special

Dependencies:

- None

### src.n8n_setup_main

Dependencies:

- None

### src.n8n_setup_workflows

Dependencies:

- None

### src.prompt_mcp_server.prompt_mcp_server.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src.prompt_mcp_server.prompt_mcp_server.models.__init__

Dependencies:

- None

### src.prompt_mcp_server.prompt_mcp_server.models.template

Dependencies:

- pydantic (external)

### src.prompt_mcp_server.prompt_mcp_server.models.llm

Dependencies:

- pydantic (external)

### src.prompt_mcp_server.prompt_mcp_server.models.chat

Dependencies:

- pydantic (external)

### src.prompt_mcp_server.prompt_mcp_server.utils.logger

Dependencies:

- ..core.config (external)

### src.prompt_mcp_server.prompt_mcp_server.utils.__init__

Dependencies:

- None

### src.prompt_mcp_server.prompt_mcp_server.api.router

Dependencies:

- .endpoints (external)
- fastapi (external)

### src.prompt_mcp_server.prompt_mcp_server.api.__init__

Dependencies:

- None

### src.prompt_mcp_server.prompt_mcp_server.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src.prompt_mcp_server.prompt_mcp_server.api.endpoints.optimize

Dependencies:

- ...core.prompt_optimizer (external)
- ...core.template_manager (external)
- fastapi (external)
- pydantic (external)

### src.prompt_mcp_server.prompt_mcp_server.api.endpoints.cost

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- ...core.template_manager (external)
- fastapi (external)
- pydantic (external)

### src.prompt_mcp_server.prompt_mcp_server.api.endpoints.__init__

Dependencies:

- None

### src.prompt_mcp_server.prompt_mcp_server.api.endpoints.templates

Dependencies:

- ...core.template_manager (external)
- ...models.template (external)
- fastapi (external)
- pydantic (external)

### src.prompt_mcp_server.prompt_mcp_server.api.endpoints.chat

Dependencies:

- ...core.llm_selector (external)
- ...core.memory_manager (external)
- ...core.template_manager (external)
- ...models.chat (external)
- fastapi (external)
- pydantic (external)

### src.prompt_mcp_server.prompt_mcp_server.templates.__init__

Dependencies:

- None

### src.prompt_mcp_server.prompt_mcp_server.__init__

Dependencies:

- None

### src.prompt_mcp_server.prompt_mcp_server.core.memory_manager

Dependencies:

- ..models.chat (external)
- .config (external)

### src.prompt_mcp_server.prompt_mcp_server.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)
- .template_manager (external)

### src.prompt_mcp_server.prompt_mcp_server.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src.prompt_mcp_server.prompt_mcp_server.core.prompt_optimizer

Dependencies:

- ..models.template (external)
- .template_manager (external)

### src.prompt_mcp_server.prompt_mcp_server.core.template_manager

Dependencies:

- ..models.template (external)
- .config (external)
- promplate (external)

### src.prompt_mcp_server.prompt_mcp_server.core.__init__

Dependencies:

- None

### src.prompt_mcp_server.prompt_mcp_server.core.llm_selector

Dependencies:

- ..models.llm (external)
- ..models.template (external)
- .config (external)

### src.prompt_mcp_server.prompt_mcp_server.memory.__init__

Dependencies:

- None

### src.generate_docker_mcp_config

Dependencies:

- None

### src.core.utils.docker_utils

Dependencies:

- ..core.logger (external)

### src.core.utils.process_utils

Dependencies:

- ..core.logger (external)
- psutil (external)
- signal (external)

### src.core.utils.__init__

Dependencies:

- .docker_utils (external)
- .network_utils (external)
- .process_utils (external)
- .system_utils (external)

### src.core.utils.system_utils

Dependencies:

- ..core.logger (external)

### src.core.utils.network_utils

Dependencies:

- ..core.logger (external)
- requests (external)

### src.core.config.__init__

Dependencies:

- None

### src.core.constants

Dependencies:


### src.core.logger

Dependencies:

- .constants (external)

### src.core.config_manager

Dependencies:

- .constants (external)
- .logger (external)
- yaml (external)

### src.core.__init__

Dependencies:

- .config_manager (external)
- .constants (external)
- .logger (external)

### src.core.logging.__init__

Dependencies:

- None

### src.web_ui.server

Dependencies:

- aiohttp (external)
- aiohttp_cors (external)
- common (external)

### src.n8n_setup_workflows_openhands

Dependencies:

- None

### src.mcp_hub.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- uvicorn (external)

### src.mcp_hub.models.server

Dependencies:

- pydantic (external)

### src.mcp_hub.models.__init__

Dependencies:

- None

### src.mcp_hub.hub_manager

Dependencies:

- .installer (external)
- .registry (external)

### src.mcp_hub.utils.logger

Dependencies:

- ..core.config (external)

### src.mcp_hub.utils.__init__

Dependencies:

- None

### src.mcp_hub.api.router

Dependencies:

- ..core.manager (external)
- ..models.server (external)
- fastapi (external)

### src.mcp_hub.api.__init__

Dependencies:

- None

### src.mcp_hub.cli

Dependencies:

- .hub_manager (external)

### src.mcp_hub.__init__

Dependencies:

- .hub_manager (external)
- .installer (external)
- .registry (external)

### src.mcp_hub.registry

Dependencies:

- requests (external)

### src.mcp_hub.cli_new

Dependencies:

- .core.manager (external)
- .models.server (external)
- .utils.logger (external)
- typer (external)

### src.mcp_hub.core.config

Dependencies:

- pydantic (external)

### src.mcp_hub.core.__init__

Dependencies:

- None

### src.mcp_hub.core.registry

Dependencies:

- ..core.config (external)
- ..models.server (external)
- ..utils.logger (external)
- aiohttp (external)
- requests (external)

### src.mcp_hub.core.manager

Dependencies:

- ..core.config (external)
- ..core.installer (external)
- ..core.registry (external)
- ..models.server (external)
- ..utils.logger (external)

### src.mcp_hub.core.installer

Dependencies:

- ..core.config (external)
- ..models.server (external)
- ..utils.logger (external)
- aiohttp (external)
- docker (external)

### src.mcp_hub.installer

Dependencies:

- requests (external)

### src.n8n_setup_workflows_mcp

Dependencies:

- None

### src.diagnostic

Dependencies:

- None

### tests.test_integration

Dependencies:

- common (external)
- requests (external)

### tests.test_n8n_setup

Dependencies:

- common (external)
- [src.n8n_setup_credentials](#src.n8n_setup_credentials)
- [src.n8n_setup_install](#src.n8n_setup_install)
- [src.n8n_setup_utils](#src.n8n_setup_utils)

### tests.conftest

Dependencies:

- pytest (external)

### tests.mcp_servers.n8n_mcp_server.test_n8n_client

Dependencies:

- pytest (external)
- [src.mcp_servers.n8n_mcp_server.core.n8n_client](#src.mcp_servers.n8n_mcp_server.core.n8n_client)

### tests.mcp_servers.docker_mcp.test_docker_executor

Dependencies:

- pytest (external)
- [src.mcp_servers.docker_mcp.core.docker_executor](#src.mcp_servers.docker_mcp.core.docker_executor)

### tests.test_mcp_server

Dependencies:

- common (external)
- src.n8n_mcp_server (external)

### tests.test_main

Dependencies:

- click.testing (external)
- src.main (external)

### tests.mcp_hub.test_registry

Dependencies:

- pytest (external)
- [src.mcp_hub.core.registry](#src.mcp_hub.core.registry)
- [src.mcp_hub.models.server](#src.mcp_hub.models.server)

### examples.parallel_openhands_tasks

Dependencies:

- common (external)
- src.mcp.client (external)

### examples.generator_example

Dependencies:

- common (external)
- src.mcp.client (external)

### examples.openhands_n8n_integration

Dependencies:

- common (external)
- src.mcp.client (external)
- [src.openhands.agent](#src.openhands.agent)

### test-setup

Dependencies:

- common (external)

### docker-mcp-ecosystem.generate-openhands-config

Dependencies:

- common (external)
- toml (external)
- yaml (external)

### docker-mcp-ecosystem.monitor-mcp-servers

Dependencies:

- common (external)
- requests (external)
- signal (external)
- tabulate (external)

### scripts.import-workflows

Dependencies:

- common (external)
- requests (external)

### scripts.update-mcp-config

Dependencies:

- common (external)

### scripts.update_scripts

Dependencies:

- common (external)

### scripts.reorganize_standalone

Dependencies:

- common (external)

### scripts.integrate-mcp-with-n8n

Dependencies:

- common (external)

### scripts.test-mcp-servers-improved

Dependencies:

- aiohttp (external)
- common (external)

### scripts.reorganize

Dependencies:

- common (external)
- git (external)
- pydantic (external)
- requests (external)
- rich (external)
- rich.console (external)
- rich.logging (external)
- rich.progress (external)
- rich.prompt (external)
- toml (external)

### scripts.common.python.utils.docker_utils

Dependencies:

- ..core.logger (external)

### scripts.common.python.utils.process_utils

Dependencies:

- ..core.logger (external)
- psutil (external)
- signal (external)

### scripts.common.python.utils.__init__

Dependencies:

- .docker_utils (external)
- .network_utils (external)
- .process_utils (external)
- .system_utils (external)

### scripts.common.python.utils.system_utils

Dependencies:

- ..core.logger (external)

### scripts.common.python.utils.network_utils

Dependencies:

- ..core.logger (external)
- requests (external)

### scripts.common.python.common

Dependencies:

- signal (external)
- yaml (external)

### scripts.common.python.core.constants

Dependencies:


### scripts.common.python.core.logger

Dependencies:

- .constants (external)

### scripts.common.python.core.config_manager

Dependencies:

- .constants (external)
- .logger (external)
- yaml (external)

### scripts.common.python.core.__init__

Dependencies:

- .config_manager (external)
- .constants (external)
- .logger (external)

### scripts.generate-common-config

Dependencies:

- common (external)
- yaml (external)

### scripts.github-integration

Dependencies:

- common (external)
- requests (external)

### scripts.integrate-mcp-with-openhands

Dependencies:

- common (external)

### scripts.test-mcp-servers

Dependencies:

- common (external)

### scripts.test-implementations

Dependencies:

- common (external)
- requests (external)

### scripts.monitor-mcp-servers

Dependencies:

- aiohttp (external)
- common (external)

### docker-mcp-servers.n8n-mcp-integration

Dependencies:

- common (external)
- requests (external)

### docker-mcp-servers.openhands-mcp-integration

Dependencies:

- common (external)

### docker-mcp-servers.test-mcp-servers

Dependencies:

- common (external)
- requests (external)

### docker-mcp-servers.monitor-mcp-servers

Dependencies:

- common (external)
- requests (external)

### test-workflows

Dependencies:

- common (external)

### src_backup.openhands.cli

Dependencies:

- .agent (external)
- common (external)

### src_backup.openhands.__init__

Dependencies:

- None

### src_backup.openhands.agent

Dependencies:

- ..common.config_manager (external)
- ..mcp.client (external)
- requests (external)

### src_backup.monitoring.prometheus_exporter

Dependencies:

- common (external)

### src_backup.test-mcp-server

Dependencies:

- common (external)

### src_backup.n8n_setup_install

Dependencies:

- common (external)
- common.docker_utils (external)
- requests (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.models.__init__

Dependencies:

- None

### src_backup.llm_cost_analyzer.llm_cost_analyzer.models.llm

Dependencies:

- pydantic (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.utils.logger

Dependencies:

- ..core.config (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.utils.__init__

Dependencies:

- None

### src_backup.llm_cost_analyzer.llm_cost_analyzer.api.router

Dependencies:

- .endpoints (external)
- fastapi (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.api.__init__

Dependencies:

- None

### src_backup.llm_cost_analyzer.llm_cost_analyzer.api.endpoints.analyze

Dependencies:

- ...core.llm_selector (external)
- fastapi (external)
- pydantic (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.api.endpoints.estimate

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- fastapi (external)
- pydantic (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.api.endpoints.__init__

Dependencies:

- None

### src_backup.llm_cost_analyzer.llm_cost_analyzer.__init__

Dependencies:

- None

### src_backup.llm_cost_analyzer.llm_cost_analyzer.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src_backup.llm_cost_analyzer.llm_cost_analyzer.core.__init__

Dependencies:

- None

### src_backup.llm_cost_analyzer.llm_cost_analyzer.core.llm_selector

Dependencies:

- ..models.llm (external)
- .config (external)

### src_backup.mcp.mcp-client

Dependencies:

- aiohttp (external)
- common (external)

### src_backup.mcp.interfaces.mcp_server_interface

Dependencies:

- .mcp_tool (external)

### src_backup.mcp.interfaces.mcp_tool

Dependencies:


### src_backup.mcp.interfaces.__init__

Dependencies:

- .mcp_server_interface (external)
- .mcp_tool (external)

### src_backup.mcp.base_mcp_server_improved

Dependencies:

- aiohttp (external)
- common (external)
- interfaces (external)
- signal (external)

### src_backup.mcp.n8n_mcp_server

Dependencies:

- aiohttp (external)
- common (external)
- signal (external)

### src_backup.mcp.servers.openhands.openhands_mcp_server

Dependencies:

- [src.core.config_manager](#src.core.config_manager)
- [src.core.logger](#src.core.logger)
- [src.core.utils.docker_utils](#src.core.utils.docker_utils)
- [src.core.utils.network_utils](#src.core.utils.network_utils)
- [src.core.utils.process_utils](#src.core.utils.process_utils)
- [src.core.utils.system_utils](#src.core.utils.system_utils)
- src.mcp_servers.base.base_mcp_server (external)
- src.openhands (external)

### src_backup.mcp.servers.openhands.__init__

Dependencies:

- None

### src_backup.mcp.servers.n8n.n8n_mcp_server

Dependencies:

- [src.core.config_manager](#src.core.config_manager)
- [src.core.logger](#src.core.logger)
- [src.core.utils.docker_utils](#src.core.utils.docker_utils)
- [src.core.utils.network_utils](#src.core.utils.network_utils)
- [src.core.utils.process_utils](#src.core.utils.process_utils)
- [src.core.utils.system_utils](#src.core.utils.system_utils)
- src.mcp_servers.base.base_mcp_server (external)

### src_backup.mcp.servers.n8n.__init__

Dependencies:

- None

### src_backup.mcp.servers.prompt.__init__

Dependencies:

- None

### src_backup.mcp.servers.__init__

Dependencies:

- None

### src_backup.mcp.servers.generator.__init__

Dependencies:

- None

### src_backup.mcp.servers.llm_cost.__init__

Dependencies:

- None

### src_backup.mcp.servers.docker.docker_mcp_server

Dependencies:

- [src.core.config_manager](#src.core.config_manager)
- [src.core.logger](#src.core.logger)
- [src.core.utils.docker_utils](#src.core.utils.docker_utils)
- [src.core.utils.network_utils](#src.core.utils.network_utils)
- [src.core.utils.process_utils](#src.core.utils.process_utils)
- [src.core.utils.system_utils](#src.core.utils.system_utils)
- src.mcp_servers.base.base_mcp_server (external)

### src_backup.mcp.servers.docker.__init__

Dependencies:

- None

### src_backup.mcp.generator_server

Dependencies:

- common (external)

### src_backup.mcp.docker_mcp_server_improved

Dependencies:

- base_mcp_server (external)
- common (external)

### src_backup.mcp.utils

Dependencies:

- ..common.docker_utils (external)
- .client (external)
- .error_handling (external)

### src_backup.mcp.test-mcp-integration

Dependencies:

- common (external)
- mcp_client (external)

### src_backup.mcp.base.base_mcp_server

Dependencies:

- aiohttp (external)
- signal (external)
- [src.core.config_manager](#src.core.config_manager)
- [src.core.logger](#src.core.logger)
- [src.core.utils.docker_utils](#src.core.utils.docker_utils)
- [src.core.utils.network_utils](#src.core.utils.network_utils)
- [src.core.utils.process_utils](#src.core.utils.process_utils)
- [src.core.utils.system_utils](#src.core.utils.system_utils)
- src.mcp_servers.base.mcp_server_interface (external)
- src.mcp_servers.base.mcp_tool (external)

### src_backup.mcp.base.__init__

Dependencies:

- None

### src_backup.mcp.n8n_mcp_server_improved

Dependencies:

- base_mcp_server (external)
- common (external)

### src_backup.mcp.openhands_server_improved

Dependencies:

- base_mcp_server (external)
- common (external)

### src_backup.n8n_setup_workflows_mcp_enhanced

Dependencies:

- common (external)

### src_backup.mcp_servers.n8n_mcp_server.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- uvicorn (external)

### src_backup.mcp_servers.n8n_mcp_server.mcp_interface

Dependencies:

- .core.audit (external)
- .core.auth (external)
- .core.metrics (external)
- .core.n8n_client (external)
- .utils.logger (external)
- src.mcp_servers.base.base_mcp_server (external)
- src.mcp_servers.base.mcp_tool (external)

### src_backup.mcp_servers.n8n_mcp_server.models.__init__

Dependencies:

- None

### src_backup.mcp_servers.n8n_mcp_server.models.workflow

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.n8n_mcp_server.utils.logger

Dependencies:

- ..core.config (external)

### src_backup.mcp_servers.n8n_mcp_server.utils.__init__

Dependencies:

- None

### src_backup.mcp_servers.n8n_mcp_server.api.router

Dependencies:

- ..core.audit (external)
- ..core.auth (external)
- ..core.metrics (external)
- ..core.n8n_client (external)
- ..models.workflow (external)
- ..utils.logger (external)
- fastapi (external)

### src_backup.mcp_servers.n8n_mcp_server.api.__init__

Dependencies:

- None

### src_backup.mcp_servers.n8n_mcp_server.n8n_mcp_server

Dependencies:

- aiohttp (external)
- common (external)
- signal (external)

### src_backup.mcp_servers.n8n_mcp_server.__init__

Dependencies:

- None

### src_backup.mcp_servers.n8n_mcp_server.utils

Dependencies:

- ..common.docker_utils (external)
- .client (external)
- .error_handling (external)

### src_backup.mcp_servers.n8n_mcp_server.core.config

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.n8n_mcp_server.core.n8n_client

Dependencies:

- ..core.config (external)
- ..utils.logger (external)
- aiohttp (external)

### src_backup.mcp_servers.n8n_mcp_server.core.audit

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src_backup.mcp_servers.n8n_mcp_server.core.__init__

Dependencies:

- None

### src_backup.mcp_servers.n8n_mcp_server.core.auth

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src_backup.mcp_servers.n8n_mcp_server.core.metrics

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src_backup.mcp_servers.docker_mcp.handlers

Dependencies:

- .docker_executor (external)
- mcp.types (external)
- yaml (external)

### src_backup.mcp_servers.docker_mcp.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- uvicorn (external)

### src_backup.mcp_servers.docker_mcp.mcp_interface

Dependencies:

- .core.audit (external)
- .core.auth (external)
- .core.docker_executor (external)
- .core.metrics (external)
- .utils.logger (external)
- src.mcp_servers.base.base_mcp_server (external)
- src.mcp_servers.base.mcp_tool (external)

### src_backup.mcp_servers.docker_mcp.models.docker

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.docker_mcp.models.__init__

Dependencies:

- None

### src_backup.mcp_servers.docker_mcp.utils.logger

Dependencies:

- ..core.config (external)

### src_backup.mcp_servers.docker_mcp.utils.__init__

Dependencies:

- None

### src_backup.mcp_servers.docker_mcp.api.router

Dependencies:

- ..core.audit (external)
- ..core.auth (external)
- ..core.docker_executor (external)
- ..core.metrics (external)
- ..models.docker (external)
- ..utils.logger (external)
- fastapi (external)
- fastapi.responses (external)

### src_backup.mcp_servers.docker_mcp.api.__init__

Dependencies:

- None

### src_backup.mcp_servers.docker_mcp.server

Dependencies:

- .audit (external)
- .auth (external)
- .handlers (external)
- .http_server (external)
- .metrics (external)
- mcp.server (external)
- mcp.server.models (external)
- mcp.server.stdio (external)
- mcp.types (external)
- as (external)
- signal (external)

### src_backup.mcp_servers.docker_mcp.audit

Dependencies:


### src_backup.mcp_servers.docker_mcp.__init__

Dependencies:

- .server (external)

### src_backup.mcp_servers.docker_mcp.http_server

Dependencies:

- aiohttp (external)

### src_backup.mcp_servers.docker_mcp.auth

Dependencies:


### src_backup.mcp_servers.docker_mcp.docker_executor

Dependencies:


### src_backup.mcp_servers.docker_mcp.metrics

Dependencies:

- prometheus_client (external)

### src_backup.mcp_servers.docker_mcp.core.config

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.docker_mcp.core.audit

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src_backup.mcp_servers.docker_mcp.core.__init__

Dependencies:

- None

### src_backup.mcp_servers.docker_mcp.core.auth

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src_backup.mcp_servers.docker_mcp.core.docker_executor

Dependencies:

- ..core.config (external)
- ..utils.logger (external)
- docker (external)

### src_backup.mcp_servers.docker_mcp.core.metrics

Dependencies:

- ..core.config (external)
- ..utils.logger (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.models.__init__

Dependencies:

- None

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.models.template

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.models.llm

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.models.chat

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.utils.logger

Dependencies:

- ..core.config (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.utils.__init__

Dependencies:

- None

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.router

Dependencies:

- .endpoints (external)
- fastapi (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.__init__

Dependencies:

- None

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.optimize

Dependencies:

- ...core.prompt_optimizer (external)
- ...core.template_manager (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.cost

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- ...core.template_manager (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.__init__

Dependencies:

- None

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.templates

Dependencies:

- ...core.template_manager (external)
- ...models.template (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.api.endpoints.chat

Dependencies:

- ...core.llm_selector (external)
- ...core.memory_manager (external)
- ...core.template_manager (external)
- ...models.chat (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.templates.__init__

Dependencies:

- None

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.__init__

Dependencies:

- None

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.memory_manager

Dependencies:

- ..models.chat (external)
- .config (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)
- .template_manager (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.prompt_optimizer

Dependencies:

- ..models.template (external)
- .template_manager (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.template_manager

Dependencies:

- ..models.template (external)
- .config (external)
- promplate (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.__init__

Dependencies:

- None

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.core.llm_selector

Dependencies:

- ..models.llm (external)
- ..models.template (external)
- .config (external)

### src_backup.mcp_servers.prompt_mcp_server.prompt_mcp_server.memory.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.models.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.models.llm

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.utils.logger

Dependencies:

- ..core.config (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.utils.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.router

Dependencies:

- .endpoints (external)
- fastapi (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.endpoints.analyze

Dependencies:

- ...core.llm_selector (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.endpoints.estimate

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.api.endpoints.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.core.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer.core.llm_selector

Dependencies:

- ..models.llm (external)
- .config (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .core.llm_selector (external)
- .core.task_cost_estimator (external)
- .mcp_interface (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.mcp_interface

Dependencies:

- .core.llm_selector (external)
- .core.task_cost_estimator (external)
- fastapi (external)
- websockets (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.models.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.models.llm

Dependencies:

- pydantic (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.utils.logger

Dependencies:

- ..core.config (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.utils.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.router

Dependencies:

- ..mcp_interface (external)
- .endpoints (external)
- fastapi (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.endpoints.analyze

Dependencies:

- ...core.llm_selector (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.endpoints.estimate

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- fastapi (external)
- pydantic (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.api.endpoints.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.core.__init__

Dependencies:

- None

### src_backup.mcp_servers.llm_cost_analyzer_mcp.llm_cost_analyzer_mcp.core.llm_selector

Dependencies:

- ..models.llm (external)
- .config (external)

### src_backup.n8n_setup_workflows_github

Dependencies:

- common (external)

### src_backup.llm_selector.test_llm_selector

Dependencies:

- common (external)
- llm_selector (external)

### src_backup.llm_selector.llm_selector_api

Dependencies:

- common (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- llm_selector (external)
- pydantic (external)
- uvicorn (external)

### src_backup.llm_selector.llm_selector

Dependencies:

- common (external)
- requests (external)

### src_backup.llm_selector.llm_selector_client

Dependencies:

- common (external)
- requests (external)

### src_backup.n8n_setup_utils

Dependencies:

- common (external)
- requests (external)

### src_backup.common.docker_utils

Dependencies:


### src_backup.common.config_manager

Dependencies:

- yaml (external)

### src_backup.common.__init__

Dependencies:

- None

### src_backup.n8n_setup_credentials

Dependencies:

- common (external)
- n8n_setup_utils (external)
- requests (external)

### src_backup.n8n_setup_workflows_document

Dependencies:

- common (external)

### src_backup.__init__

Dependencies:

- None

### src_backup.n8n_setup_workflows_special

Dependencies:

- common (external)

### src_backup.n8n_setup_main

Dependencies:

- common (external)
- n8n_setup_credentials (external)
- n8n_setup_install (external)
- n8n_setup_utils (external)
- n8n_setup_workflows (external)

### src_backup.n8n_setup_workflows

Dependencies:

- common (external)
- n8n_setup_workflows_document (external)
- n8n_setup_workflows_github (external)
- n8n_setup_workflows_mcp (external)
- n8n_setup_workflows_openhands (external)
- n8n_setup_workflows_special (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- fastapi.responses (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.models.__init__

Dependencies:

- None

### src_backup.prompt_mcp_server.prompt_mcp_server.models.template

Dependencies:

- pydantic (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.models.llm

Dependencies:

- pydantic (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.models.chat

Dependencies:

- pydantic (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.utils.logger

Dependencies:

- ..core.config (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.utils.__init__

Dependencies:

- None

### src_backup.prompt_mcp_server.prompt_mcp_server.api.router

Dependencies:

- .endpoints (external)
- fastapi (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.api.__init__

Dependencies:

- None

### src_backup.prompt_mcp_server.prompt_mcp_server.api.endpoints.models

Dependencies:

- ...core.llm_selector (external)
- ...models.llm (external)
- fastapi (external)
- pydantic (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.api.endpoints.optimize

Dependencies:

- ...core.prompt_optimizer (external)
- ...core.template_manager (external)
- fastapi (external)
- pydantic (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.api.endpoints.cost

Dependencies:

- ...core.llm_selector (external)
- ...core.task_cost_estimator (external)
- ...core.template_manager (external)
- fastapi (external)
- pydantic (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.api.endpoints.__init__

Dependencies:

- None

### src_backup.prompt_mcp_server.prompt_mcp_server.api.endpoints.templates

Dependencies:

- ...core.template_manager (external)
- ...models.template (external)
- fastapi (external)
- pydantic (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.api.endpoints.chat

Dependencies:

- ...core.llm_selector (external)
- ...core.memory_manager (external)
- ...core.template_manager (external)
- ...models.chat (external)
- fastapi (external)
- pydantic (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.templates.__init__

Dependencies:

- None

### src_backup.prompt_mcp_server.prompt_mcp_server.__init__

Dependencies:

- None

### src_backup.prompt_mcp_server.prompt_mcp_server.core.memory_manager

Dependencies:

- ..models.chat (external)
- .config (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.core.task_cost_estimator

Dependencies:

- ..models.llm (external)
- .llm_selector (external)
- .template_manager (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.core.config

Dependencies:

- pydantic (external)
- pydantic_settings (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.core.prompt_optimizer

Dependencies:

- ..models.template (external)
- .template_manager (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.core.template_manager

Dependencies:

- ..models.template (external)
- .config (external)
- promplate (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.core.__init__

Dependencies:

- None

### src_backup.prompt_mcp_server.prompt_mcp_server.core.llm_selector

Dependencies:

- ..models.llm (external)
- ..models.template (external)
- .config (external)

### src_backup.prompt_mcp_server.prompt_mcp_server.memory.__init__

Dependencies:

- None

### src_backup.generate_docker_mcp_config

Dependencies:

- common (external)

### src_backup.core.utils.docker_utils

Dependencies:

- ..core.logger (external)

### src_backup.core.utils.process_utils

Dependencies:

- ..core.logger (external)
- psutil (external)
- signal (external)

### src_backup.core.utils.__init__

Dependencies:

- .docker_utils (external)
- .network_utils (external)
- .process_utils (external)
- .system_utils (external)

### src_backup.core.utils.system_utils

Dependencies:

- ..core.logger (external)

### src_backup.core.utils.network_utils

Dependencies:

- ..core.logger (external)
- requests (external)

### src_backup.core.config.__init__

Dependencies:

- None

### src_backup.core.constants

Dependencies:


### src_backup.core.logger

Dependencies:

- .constants (external)

### src_backup.core.config_manager

Dependencies:

- .constants (external)
- .logger (external)
- yaml (external)

### src_backup.core.__init__

Dependencies:

- .config_manager (external)
- .constants (external)
- .logger (external)

### src_backup.core.logging.__init__

Dependencies:

- None

### src_backup.web_ui.server

Dependencies:

- aiohttp (external)
- aiohttp_cors (external)
- common (external)

### src_backup.n8n_setup_workflows_openhands

Dependencies:

- common (external)

### src_backup.mcp_hub.main

Dependencies:

- .api.router (external)
- .core.config (external)
- .utils.logger (external)
- fastapi (external)
- fastapi.middleware.cors (external)
- uvicorn (external)

### src_backup.mcp_hub.models.server

Dependencies:

- pydantic (external)

### src_backup.mcp_hub.models.__init__

Dependencies:

- None

### src_backup.mcp_hub.hub_manager

Dependencies:

- .installer (external)
- .registry (external)

### src_backup.mcp_hub.utils.logger

Dependencies:

- ..core.config (external)

### src_backup.mcp_hub.utils.__init__

Dependencies:

- None

### src_backup.mcp_hub.api.router

Dependencies:

- ..core.manager (external)
- ..models.server (external)
- fastapi (external)

### src_backup.mcp_hub.api.__init__

Dependencies:

- None

### src_backup.mcp_hub.cli

Dependencies:

- .hub_manager (external)

### src_backup.mcp_hub.__init__

Dependencies:

- .hub_manager (external)
- .installer (external)
- .registry (external)

### src_backup.mcp_hub.registry

Dependencies:

- requests (external)

### src_backup.mcp_hub.cli_new

Dependencies:

- .core.manager (external)
- .models.server (external)
- .utils.logger (external)
- typer (external)

### src_backup.mcp_hub.core.config

Dependencies:

- pydantic (external)

### src_backup.mcp_hub.core.__init__

Dependencies:

- None

### src_backup.mcp_hub.core.registry

Dependencies:

- ..core.config (external)
- ..models.server (external)
- ..utils.logger (external)
- aiohttp (external)
- requests (external)

### src_backup.mcp_hub.core.manager

Dependencies:

- ..core.config (external)
- ..core.installer (external)
- ..core.registry (external)
- ..models.server (external)
- ..utils.logger (external)

### src_backup.mcp_hub.core.installer

Dependencies:

- ..core.config (external)
- ..models.server (external)
- ..utils.logger (external)
- aiohttp (external)
- docker (external)

### src_backup.mcp_hub.installer

Dependencies:

- requests (external)

### src_backup.n8n_setup_workflows_mcp

Dependencies:

- common (external)

### src_backup.diagnostic

Dependencies:

- common (external)
- requests (external)

