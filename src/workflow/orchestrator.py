"""
Workflow Orchestration System.

This module provides a workflow orchestration system for managing and executing
complex workflows across multiple MCP servers.
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union, cast

from src.core.error_handling import BaseError, ErrorCategory, ErrorHandler
from src.core.logging import get_logger
from src.core.performance import async_cached, async_profiled, async_timed

# Set up logging
logger = get_logger(__name__)


class WorkflowStatus(str, Enum):
    """Status of a workflow execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    PAUSED = "paused"


class NodeStatus(str, Enum):
    """Status of a workflow node execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowError(BaseError):
    """Base class for workflow errors."""
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        node_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            category=ErrorCategory.WORKFLOW,
            code="ERR_WORKFLOW",
            details={
                "workflow_id": workflow_id,
                "node_id": node_id,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.workflow_id = workflow_id
        self.node_id = node_id


class WorkflowNotFoundError(WorkflowError):
    """Error raised when a workflow is not found."""
    def __init__(self, workflow_id: str, **kwargs):
        super().__init__(
            f"Workflow with ID '{workflow_id}' not found",
            workflow_id=workflow_id,
            code="ERR_WORKFLOW_NOT_FOUND",
            **kwargs
        )


class WorkflowExecutionNotFoundError(WorkflowError):
    """Error raised when a workflow execution is not found."""
    def __init__(self, execution_id: str, **kwargs):
        super().__init__(
            f"Workflow execution with ID '{execution_id}' not found",
            code="ERR_WORKFLOW_EXECUTION_NOT_FOUND",
            details={"execution_id": execution_id, **kwargs.get("details", {})},
            **kwargs
        )


class WorkflowNodeNotFoundError(WorkflowError):
    """Error raised when a workflow node is not found."""
    def __init__(self, workflow_id: str, node_id: str, **kwargs):
        super().__init__(
            f"Node with ID '{node_id}' not found in workflow '{workflow_id}'",
            workflow_id=workflow_id,
            node_id=node_id,
            code="ERR_WORKFLOW_NODE_NOT_FOUND",
            **kwargs
        )


class WorkflowValidationError(WorkflowError):
    """Error raised when a workflow validation fails."""
    def __init__(self, message: str, workflow_id: Optional[str] = None, **kwargs):
        super().__init__(
            message,
            workflow_id=workflow_id,
            code="ERR_WORKFLOW_VALIDATION",
            **kwargs
        )


class WorkflowExecutionError(WorkflowError):
    """Error raised when a workflow execution fails."""
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        node_id: Optional[str] = None,
        execution_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            workflow_id=workflow_id,
            node_id=node_id,
            code="ERR_WORKFLOW_EXECUTION",
            details={
                "execution_id": execution_id,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.execution_id = execution_id


@dataclass
class WorkflowNode:
    """A node in a workflow."""
    id: str
    type: str
    name: str
    description: Optional[str] = None
    config: Dict[str, Any] = field(default_factory=dict)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    timeout: Optional[int] = None
    condition: Optional[str] = None
    position: Dict[str, int] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowDefinition:
    """Definition of a workflow."""
    id: str
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    nodes: Dict[str, WorkflowNode] = field(default_factory=dict)
    edges: List[Dict[str, str]] = field(default_factory=list)
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow definition to a dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "version": self.version,
            "nodes": {
                node_id: {
                    "id": node.id,
                    "type": node.type,
                    "name": node.name,
                    "description": node.description,
                    "config": node.config,
                    "inputs": node.inputs,
                    "outputs": node.outputs,
                    "dependencies": node.dependencies,
                    "retry_policy": node.retry_policy,
                    "timeout": node.timeout,
                    "condition": node.condition,
                    "position": node.position,
                    "metadata": node.metadata,
                }
                for node_id, node in self.nodes.items()
            },
            "edges": self.edges,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "tags": self.tags,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowDefinition":
        """Create a workflow definition from a dictionary."""
        nodes = {
            node_id: WorkflowNode(
                id=node_data["id"],
                type=node_data["type"],
                name=node_data["name"],
                description=node_data.get("description"),
                config=node_data.get("config", {}),
                inputs=node_data.get("inputs", {}),
                outputs=node_data.get("outputs", {}),
                dependencies=node_data.get("dependencies", []),
                retry_policy=node_data.get("retry_policy", {}),
                timeout=node_data.get("timeout"),
                condition=node_data.get("condition"),
                position=node_data.get("position", {}),
                metadata=node_data.get("metadata", {}),
            )
            for node_id, node_data in data.get("nodes", {}).items()
        }

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif not isinstance(created_at, datetime):
            created_at = datetime.now()

        updated_at = data.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif not isinstance(updated_at, datetime):
            updated_at = datetime.now()

        return cls(
            id=data["id"],
            name=data["name"],
            description=data.get("description"),
            version=data.get("version", "1.0.0"),
            nodes=nodes,
            edges=data.get("edges", []),
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
            created_at=created_at,
            updated_at=updated_at,
        )

    def validate(self) -> List[str]:
        """Validate the workflow definition.

        Returns:
            List of validation errors.
        """
        errors = []

        # Check for required fields
        if not self.id:
            errors.append("Workflow ID is required")
        if not self.name:
            errors.append("Workflow name is required")

        # Check for duplicate node IDs
        node_ids = set()
        for node_id, node in self.nodes.items():
            if node_id != node.id:
                errors.append(f"Node ID mismatch: {node_id} != {node.id}")
            if node_id in node_ids:
                errors.append(f"Duplicate node ID: {node_id}")
            node_ids.add(node_id)

        # Check for valid edges
        for edge in self.edges:
            source = edge.get("source")
            target = edge.get("target")
            if not source:
                errors.append(f"Edge missing source: {edge}")
            if not target:
                errors.append(f"Edge missing target: {edge}")
            if source and source not in self.nodes:
                errors.append(f"Edge source not found: {source}")
            if target and target not in self.nodes:
                errors.append(f"Edge target not found: {target}")

        # Check for cycles
        if self._has_cycle():
            errors.append("Workflow contains cycles")

        return errors

    def _has_cycle(self) -> bool:
        """Check if the workflow contains cycles."""
        # Build adjacency list
        adjacency_list = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                adjacency_list[source].append(target)

        # DFS to detect cycles
        visited = set()
        path = set()

        def dfs(node_id: str) -> bool:
            if node_id in path:
                return True
            if node_id in visited:
                return False

            visited.add(node_id)
            path.add(node_id)

            for neighbor in adjacency_list[node_id]:
                if dfs(neighbor):
                    return True

            path.remove(node_id)
            return False

        for node_id in self.nodes:
            if dfs(node_id):
                return True

        return False

    def get_node_dependencies(self, node_id: str) -> List[str]:
        """Get the dependencies of a node.

        Args:
            node_id: ID of the node.

        Returns:
            List of node IDs that this node depends on.
        """
        if node_id not in self.nodes:
            raise WorkflowNodeNotFoundError(self.id, node_id)

        # Get explicit dependencies
        dependencies = list(self.nodes[node_id].dependencies)

        # Add implicit dependencies from edges
        for edge in self.edges:
            if edge.get("target") == node_id:
                source = edge.get("source")
                if source and source not in dependencies:
                    dependencies.append(source)

        return dependencies

    def get_topological_order(self) -> List[str]:
        """Get the nodes in topological order.

        Returns:
            List of node IDs in topological order.
        """
        # Build adjacency list
        adjacency_list = {node_id: [] for node_id in self.nodes}
        for edge in self.edges:
            source = edge.get("source")
            target = edge.get("target")
            if source and target:
                adjacency_list[source].append(target)

        # Calculate in-degree of each node
        in_degree = {node_id: 0 for node_id in self.nodes}
        for node_id, neighbors in adjacency_list.items():
            for neighbor in neighbors:
                in_degree[neighbor] += 1

        # Start with nodes that have no dependencies
        queue = [node_id for node_id, degree in in_degree.items() if degree == 0]
        result = []

        # Process nodes in topological order
        while queue:
            node_id = queue.pop(0)
            result.append(node_id)

            for neighbor in adjacency_list[node_id]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        # Check if we visited all nodes
        if len(result) != len(self.nodes):
            raise WorkflowValidationError(
                "Workflow contains cycles", workflow_id=self.id
            )

        return result


@dataclass
class NodeExecution:
    """Execution of a workflow node."""
    node_id: str
    status: NodeStatus = NodeStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None
    retry_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class WorkflowExecution:
    """Execution of a workflow."""
    id: str
    workflow_id: str
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    inputs: Dict[str, Any] = field(default_factory=dict)
    outputs: Dict[str, Any] = field(default_factory=dict)
    node_executions: Dict[str, NodeExecution] = field(default_factory=dict)
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the workflow execution to a dictionary."""
        return {
            "id": self.id,
            "workflow_id": self.workflow_id,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "inputs": self.inputs,
            "outputs": self.outputs,
            "node_executions": {
                node_id: {
                    "node_id": node_exec.node_id,
                    "status": node_exec.status,
                    "started_at": node_exec.started_at.isoformat() if node_exec.started_at else None,
                    "completed_at": node_exec.completed_at.isoformat() if node_exec.completed_at else None,
                    "inputs": node_exec.inputs,
                    "outputs": node_exec.outputs,
                    "error": node_exec.error,
                    "retry_count": node_exec.retry_count,
                    "metadata": node_exec.metadata,
                }
                for node_id, node_exec in self.node_executions.items()
            },
            "error": self.error,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "WorkflowExecution":
        """Create a workflow execution from a dictionary."""
        node_executions = {}
        for node_id, node_exec_data in data.get("node_executions", {}).items():
            started_at = node_exec_data.get("started_at")
            if isinstance(started_at, str):
                started_at = datetime.fromisoformat(started_at)

            completed_at = node_exec_data.get("completed_at")
            if isinstance(completed_at, str):
                completed_at = datetime.fromisoformat(completed_at)

            node_executions[node_id] = NodeExecution(
                node_id=node_exec_data["node_id"],
                status=NodeStatus(node_exec_data.get("status", NodeStatus.PENDING)),
                started_at=started_at,
                completed_at=completed_at,
                inputs=node_exec_data.get("inputs", {}),
                outputs=node_exec_data.get("outputs", {}),
                error=node_exec_data.get("error"),
                retry_count=node_exec_data.get("retry_count", 0),
                metadata=node_exec_data.get("metadata", {}),
            )

        created_at = data.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif not isinstance(created_at, datetime):
            created_at = datetime.now()

        started_at = data.get("started_at")
        if isinstance(started_at, str):
            started_at = datetime.fromisoformat(started_at)

        completed_at = data.get("completed_at")
        if isinstance(completed_at, str):
            completed_at = datetime.fromisoformat(completed_at)

        return cls(
            id=data["id"],
            workflow_id=data["workflow_id"],
            status=WorkflowStatus(data.get("status", WorkflowStatus.PENDING)),
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            inputs=data.get("inputs", {}),
            outputs=data.get("outputs", {}),
            node_executions=node_executions,
            error=data.get("error"),
            metadata=data.get("metadata", {}),
        )


class NodeExecutor:
    """Base class for node executors."""

    def __init__(self, node_type: str):
        """Initialize the node executor.

        Args:
            node_type: Type of node this executor handles.
        """
        self.node_type = node_type

    async def execute(
        self,
        node: WorkflowNode,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute the node.

        Args:
            node: The node to execute.
            inputs: Input values for the node.
            context: Execution context.

        Returns:
            Output values from the node.
        """
        raise NotImplementedError("Subclasses must implement execute()")

    def can_execute(self, node: WorkflowNode) -> bool:
        """Check if this executor can execute the given node.

        Args:
            node: The node to check.

        Returns:
            True if this executor can execute the node, False otherwise.
        """
        return node.type == self.node_type


class WorkflowOrchestrator:
    """Orchestrates workflow executions."""

    def __init__(self):
        """Initialize the workflow orchestrator."""
        self.workflows: Dict[str, WorkflowDefinition] = {}
        self.executions: Dict[str, WorkflowExecution] = {}
        self.node_executors: Dict[str, NodeExecutor] = {}
        self._execution_tasks: Dict[str, asyncio.Task] = {}

    def register_workflow(self, workflow: WorkflowDefinition) -> None:
        """Register a workflow.

        Args:
            workflow: The workflow to register.

        Raises:
            WorkflowValidationError: If the workflow is invalid.
        """
        # Validate the workflow
        errors = workflow.validate()
        if errors:
            raise WorkflowValidationError(
                f"Invalid workflow: {', '.join(errors)}",
                workflow_id=workflow.id,
            )

        # Register the workflow
        self.workflows[workflow.id] = workflow
        logger.info(f"Registered workflow: {workflow.id} ({workflow.name})")

    def register_node_executor(self, executor: NodeExecutor) -> None:
        """Register a node executor.

        Args:
            executor: The node executor to register.
        """
        self.node_executors[executor.node_type] = executor
        logger.info(f"Registered node executor for type: {executor.node_type}")

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition:
        """Get a workflow by ID.

        Args:
            workflow_id: ID of the workflow.

        Returns:
            The workflow definition.

        Raises:
            WorkflowNotFoundError: If the workflow is not found.
        """
        workflow = self.workflows.get(workflow_id)
        if not workflow:
            raise WorkflowNotFoundError(workflow_id)
        return workflow

    def get_execution(self, execution_id: str) -> WorkflowExecution:
        """Get a workflow execution by ID.

        Args:
            execution_id: ID of the execution.

        Returns:
            The workflow execution.

        Raises:
            WorkflowExecutionNotFoundError: If the execution is not found.
        """
        execution = self.executions.get(execution_id)
        if not execution:
            raise WorkflowExecutionNotFoundError(execution_id)
        return execution

    @async_profiled
    async def execute_workflow(
        self,
        workflow_id: str,
        inputs: Dict[str, Any] = None,
        execution_id: Optional[str] = None,
        metadata: Dict[str, Any] = None,
    ) -> str:
        """Execute a workflow.

        Args:
            workflow_id: ID of the workflow to execute.
            inputs: Input values for the workflow.
            execution_id: Optional ID for the execution. If not provided, a new ID will be generated.
            metadata: Optional metadata for the execution.

        Returns:
            ID of the workflow execution.

        Raises:
            WorkflowNotFoundError: If the workflow is not found.
        """
        # Get the workflow
        workflow = self.get_workflow(workflow_id)

        # Create execution ID if not provided
        if not execution_id:
            execution_id = str(uuid.uuid4())

        # Create execution record
        execution = WorkflowExecution(
            id=execution_id,
            workflow_id=workflow_id,
            inputs=inputs or {},
            metadata=metadata or {},
        )
        self.executions[execution_id] = execution

        # Start execution in background
        task = asyncio.create_task(self._execute_workflow(execution))
        self._execution_tasks[execution_id] = task

        logger.info(f"Started workflow execution: {execution_id} ({workflow.name})")
        return execution_id

    @async_timed
    async def _execute_workflow(self, execution: WorkflowExecution) -> None:
        """Execute a workflow.

        Args:
            execution: The workflow execution.
        """
        try:
            # Get the workflow
            workflow = self.get_workflow(execution.workflow_id)

            # Update execution status
            execution.status = WorkflowStatus.RUNNING
            execution.started_at = datetime.now()

            # Initialize node executions
            for node_id, node in workflow.nodes.items():
                execution.node_executions[node_id] = NodeExecution(node_id=node_id)

            # Get nodes in topological order
            node_order = workflow.get_topological_order()

            # Execute nodes in order
            context = {
                "workflow_id": workflow.id,
                "execution_id": execution.id,
                "inputs": execution.inputs,
                "metadata": execution.metadata,
            }

            for node_id in node_order:
                node = workflow.nodes[node_id]
                node_execution = execution.node_executions[node_id]

                # Check if we should execute this node
                if not await self._should_execute_node(node, execution, context):
                    node_execution.status = NodeStatus.SKIPPED
                    continue

                # Get node inputs
                node_inputs = await self._resolve_node_inputs(node, execution, context)
                node_execution.inputs = node_inputs

                # Execute the node
                try:
                    node_execution.status = NodeStatus.RUNNING
                    node_execution.started_at = datetime.now()

                    # Get the node executor
                    executor = self.node_executors.get(node.type)
                    if not executor:
                        raise WorkflowExecutionError(
                            f"No executor found for node type: {node.type}",
                            workflow_id=workflow.id,
                            node_id=node_id,
                            execution_id=execution.id,
                        )

                    # Execute the node
                    node_outputs = await executor.execute(node, node_inputs, context)
                    node_execution.outputs = node_outputs
                    node_execution.status = NodeStatus.COMPLETED
                    node_execution.completed_at = datetime.now()

                    # Update context with node outputs
                    context[f"node_{node_id}_outputs"] = node_outputs

                except Exception as e:
                    # Handle node execution error
                    error_dict = ErrorHandler.handle_error(e, log_error=True, raise_error=False)
                    node_execution.status = NodeStatus.FAILED
                    node_execution.completed_at = datetime.now()
                    node_execution.error = error_dict

                    # Check if we should retry
                    if await self._should_retry_node(node, node_execution):
                        # Increment retry count
                        node_execution.retry_count += 1
                        node_execution.status = NodeStatus.PENDING
                        node_execution.started_at = None
                        node_execution.completed_at = None
                        node_execution.error = None

                        # Wait for retry delay
                        retry_delay = self._get_retry_delay(node, node_execution)
                        if retry_delay > 0:
                            await asyncio.sleep(retry_delay)

                        # Retry the node
                        node_id_index = node_order.index(node_id)
                        node_order.insert(node_id_index + 1, node_id)
                        continue
                    else:
                        # Node failed, check if workflow should fail
                        if node.metadata.get("critical", False):
                            raise WorkflowExecutionError(
                                f"Critical node failed: {node_id}",
                                workflow_id=workflow.id,
                                node_id=node_id,
                                execution_id=execution.id,
                                cause=e,
                            )

            # Resolve workflow outputs
            execution.outputs = await self._resolve_workflow_outputs(workflow, execution, context)
            execution.status = WorkflowStatus.COMPLETED
            execution.completed_at = datetime.now()

            logger.info(f"Completed workflow execution: {execution.id} ({workflow.name})")

        except Exception as e:
            # Handle workflow execution error
            error_dict = ErrorHandler.handle_error(e, log_error=True, raise_error=False)
            execution.status = WorkflowStatus.FAILED
            execution.completed_at = datetime.now()
            execution.error = error_dict

            logger.error(f"Failed workflow execution: {execution.id} ({execution.workflow_id})")

        finally:
            # Clean up
            if execution.id in self._execution_tasks:
                del self._execution_tasks[execution.id]

    async def _should_execute_node(
        self,
        node: WorkflowNode,
        execution: WorkflowExecution,
        context: Dict[str, Any],
    ) -> bool:
        """Check if a node should be executed.

        Args:
            node: The node to check.
            execution: The workflow execution.
            context: Execution context.

        Returns:
            True if the node should be executed, False otherwise.
        """
        # Check if the node has a condition
        if node.condition:
            try:
                # Evaluate the condition
                condition_result = eval(node.condition, {"__builtins__": {}}, context)
                return bool(condition_result)
            except Exception as e:
                logger.warning(f"Error evaluating condition for node {node.id}: {e}")
                return False

        # Check if all dependencies are completed
        workflow = self.get_workflow(execution.workflow_id)
        dependencies = workflow.get_node_dependencies(node.id)
        for dep_id in dependencies:
            dep_execution = execution.node_executions.get(dep_id)
            if not dep_execution or dep_execution.status != NodeStatus.COMPLETED:
                return False

        return True

    async def _should_retry_node(
        self,
        node: WorkflowNode,
        node_execution: NodeExecution,
    ) -> bool:
        """Check if a node should be retried.

        Args:
            node: The node to check.
            node_execution: The node execution.

        Returns:
            True if the node should be retried, False otherwise.
        """
        # Check if retries are enabled
        retry_policy = node.retry_policy
        if not retry_policy:
            return False

        # Check if we've reached the maximum retries
        max_retries = retry_policy.get("max_retries", 0)
        if node_execution.retry_count >= max_retries:
            return False

        # Check if the error is retryable
        if node_execution.error:
            error_code = node_execution.error.get("code", "")
            non_retryable_errors = retry_policy.get("non_retryable_errors", [])
            if error_code in non_retryable_errors:
                return False

        return True

    def _get_retry_delay(
        self,
        node: WorkflowNode,
        node_execution: NodeExecution,
    ) -> float:
        """Get the retry delay for a node.

        Args:
            node: The node.
            node_execution: The node execution.

        Returns:
            Retry delay in seconds.
        """
        retry_policy = node.retry_policy
        if not retry_policy:
            return 0

        # Get base delay
        base_delay = retry_policy.get("base_delay", 1.0)

        # Apply backoff
        backoff_multiplier = retry_policy.get("backoff_multiplier", 2.0)
        delay = base_delay * (backoff_multiplier ** node_execution.retry_count)

        # Apply jitter
        jitter = retry_policy.get("jitter", 0.0)
        if jitter > 0:
            import random
            delay = delay * (1 + random.uniform(-jitter, jitter))

        # Apply max delay
        max_delay = retry_policy.get("max_delay", float("inf"))
        delay = min(delay, max_delay)

        return delay

    async def _resolve_node_inputs(
        self,
        node: WorkflowNode,
        execution: WorkflowExecution,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve inputs for a node.

        Args:
            node: The node.
            execution: The workflow execution.
            context: Execution context.

        Returns:
            Resolved input values.
        """
        inputs = {}

        # Process each input
        for input_name, input_spec in node.inputs.items():
            # If the input is a string, it's a reference to another node's output
            if isinstance(input_spec, str):
                # Check if it's a workflow input
                if input_spec.startswith("workflow.inputs."):
                    input_path = input_spec[len("workflow.inputs."):]
                    input_value = execution.inputs.get(input_path)
                    inputs[input_name] = input_value
                # Check if it's a node output
                elif input_spec.startswith("node."):
                    parts = input_spec.split(".")
                    if len(parts) >= 3:
                        ref_node_id = parts[1]
                        output_name = parts[2]
                        ref_node_execution = execution.node_executions.get(ref_node_id)
                        if ref_node_execution and ref_node_execution.status == NodeStatus.COMPLETED:
                            input_value = ref_node_execution.outputs.get(output_name)
                            inputs[input_name] = input_value
                # Check if it's a context value
                elif input_spec.startswith("context."):
                    context_path = input_spec[len("context."):]
                    input_value = context.get(context_path)
                    inputs[input_name] = input_value
                else:
                    # Treat as a literal value
                    inputs[input_name] = input_spec
            else:
                # Use the input spec as a literal value
                inputs[input_name] = input_spec

        return inputs

    async def _resolve_workflow_outputs(
        self,
        workflow: WorkflowDefinition,
        execution: WorkflowExecution,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Resolve outputs for a workflow.

        Args:
            workflow: The workflow.
            execution: The workflow execution.
            context: Execution context.

        Returns:
            Resolved output values.
        """
        outputs = {}

        # Process each output
        for output_name, output_spec in workflow.outputs.items():
            # If the output is a string, it's a reference to a node's output
            if isinstance(output_spec, str):
                # Check if it's a node output
                if output_spec.startswith("node."):
                    parts = output_spec.split(".")
                    if len(parts) >= 3:
                        node_id = parts[1]
                        output_key = parts[2]
                        node_execution = execution.node_executions.get(node_id)
                        if node_execution and node_execution.status == NodeStatus.COMPLETED:
                            output_value = node_execution.outputs.get(output_key)
                            outputs[output_name] = output_value
                # Check if it's a context value
                elif output_spec.startswith("context."):
                    context_path = output_spec[len("context."):]
                    output_value = context.get(context_path)
                    outputs[output_name] = output_value
                else:
                    # Treat as a literal value
                    outputs[output_name] = output_spec
            else:
                # Use the output spec as a literal value
                outputs[output_name] = output_spec

        return outputs

    async def cancel_execution(self, execution_id: str) -> None:
        """Cancel a workflow execution.

        Args:
            execution_id: ID of the execution to cancel.

        Raises:
            WorkflowExecutionNotFoundError: If the execution is not found.
        """
        # Get the execution
        execution = self.get_execution(execution_id)

        # Check if the execution is already completed
        if execution.status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELED,
        ]:
            return

        # Cancel the execution
        execution.status = WorkflowStatus.CANCELED
        execution.completed_at = datetime.now()

        # Cancel the execution task
        task = self._execution_tasks.get(execution_id)
        if task:
            task.cancel()
            del self._execution_tasks[execution_id]

        logger.info(f"Canceled workflow execution: {execution_id}")

    async def pause_execution(self, execution_id: str) -> None:
        """Pause a workflow execution.

        Args:
            execution_id: ID of the execution to pause.

        Raises:
            WorkflowExecutionNotFoundError: If the execution is not found.
            WorkflowExecutionError: If the execution cannot be paused.
        """
        # Get the execution
        execution = self.get_execution(execution_id)

        # Check if the execution is already completed
        if execution.status in [
            WorkflowStatus.COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELED,
        ]:
            raise WorkflowExecutionError(
                f"Cannot pause execution with status: {execution.status}",
                execution_id=execution_id,
            )

        # Pause the execution
        execution.status = WorkflowStatus.PAUSED

        logger.info(f"Paused workflow execution: {execution_id}")

    async def resume_execution(self, execution_id: str) -> None:
        """Resume a paused workflow execution.

        Args:
            execution_id: ID of the execution to resume.

        Raises:
            WorkflowExecutionNotFoundError: If the execution is not found.
            WorkflowExecutionError: If the execution cannot be resumed.
        """
        # Get the execution
        execution = self.get_execution(execution_id)

        # Check if the execution is paused
        if execution.status != WorkflowStatus.PAUSED:
            raise WorkflowExecutionError(
                f"Cannot resume execution with status: {execution.status}",
                execution_id=execution_id,
            )

        # Resume the execution
        execution.status = WorkflowStatus.RUNNING

        # Start execution in background
        task = asyncio.create_task(self._execute_workflow(execution))
        self._execution_tasks[execution_id] = task

        logger.info(f"Resumed workflow execution: {execution_id}")

    def list_workflows(self) -> List[Dict[str, Any]]:
        """List all registered workflows.

        Returns:
            List of workflow definitions.
        """
        return [workflow.to_dict() for workflow in self.workflows.values()]

    def list_executions(
        self,
        workflow_id: Optional[str] = None,
        status: Optional[WorkflowStatus] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[Dict[str, Any]]:
        """List workflow executions.

        Args:
            workflow_id: Optional workflow ID to filter by.
            status: Optional status to filter by.
            limit: Maximum number of executions to return.
            offset: Offset for pagination.

        Returns:
            List of workflow executions.
        """
        executions = list(self.executions.values())

        # Apply filters
        if workflow_id:
            executions = [e for e in executions if e.workflow_id == workflow_id]
        if status:
            executions = [e for e in executions if e.status == status]

        # Sort by created_at (newest first)
        executions.sort(key=lambda e: e.created_at, reverse=True)

        # Apply pagination
        executions = executions[offset:offset + limit]

        return [execution.to_dict() for execution in executions]


# Create a global orchestrator instance
orchestrator = WorkflowOrchestrator()


# Node executor implementations
class HttpNodeExecutor(NodeExecutor):
    """Executor for HTTP request nodes."""

    def __init__(self):
        """Initialize the HTTP node executor."""
        super().__init__("http")

    @async_timed
    async def execute(
        self,
        node: WorkflowNode,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute an HTTP request.

        Args:
            node: The node to execute.
            inputs: Input values for the node.
            context: Execution context.

        Returns:
            Output values from the node.
        """
        import aiohttp

        # Get request parameters
        url = inputs.get("url") or node.config.get("url")
        method = (inputs.get("method") or node.config.get("method", "GET")).upper()
        headers = inputs.get("headers") or node.config.get("headers", {})
        params = inputs.get("params") or node.config.get("params", {})
        data = inputs.get("data") or node.config.get("data")
        json_data = inputs.get("json") or node.config.get("json")
        timeout = inputs.get("timeout") or node.config.get("timeout", 30)

        # Make the request
        async with aiohttp.ClientSession() as session:
            async with session.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                data=data,
                json=json_data,
                timeout=timeout,
            ) as response:
                # Read response
                response_text = await response.text()
                try:
                    response_json = await response.json()
                except:
                    response_json = None

                # Return response data
                return {
                    "status": response.status,
                    "headers": dict(response.headers),
                    "text": response_text,
                    "json": response_json,
                }


class PythonNodeExecutor(NodeExecutor):
    """Executor for Python code nodes."""

    def __init__(self):
        """Initialize the Python node executor."""
        super().__init__("python")

    @async_timed
    async def execute(
        self,
        node: WorkflowNode,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute Python code.

        Args:
            node: The node to execute.
            inputs: Input values for the node.
            context: Execution context.

        Returns:
            Output values from the node.
        """
        # Get the code to execute
        code = inputs.get("code") or node.config.get("code", "")

        # Create a safe globals dictionary
        safe_globals = {
            "inputs": inputs,
            "context": context,
            "print": print,
            "logger": logger,
        }

        # Add allowed modules
        allowed_modules = node.config.get("allowed_modules", [])
        for module_name in allowed_modules:
            try:
                module = __import__(module_name)
                safe_globals[module_name] = module
            except ImportError:
                logger.warning(f"Failed to import module: {module_name}")

        # Execute the code
        local_vars = {}
        exec(code, safe_globals, local_vars)

        # Get the outputs
        outputs = local_vars.get("outputs", {})
        if not isinstance(outputs, dict):
            outputs = {"result": outputs}

        return outputs


class DelayNodeExecutor(NodeExecutor):
    """Executor for delay nodes."""

    def __init__(self):
        """Initialize the delay node executor."""
        super().__init__("delay")

    @async_timed
    async def execute(
        self,
        node: WorkflowNode,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a delay.

        Args:
            node: The node to execute.
            inputs: Input values for the node.
            context: Execution context.

        Returns:
            Output values from the node.
        """
        # Get the delay duration
        duration = inputs.get("duration") or node.config.get("duration", 1)
        try:
            duration = float(duration)
        except (ValueError, TypeError):
            duration = 1

        # Wait for the specified duration
        await asyncio.sleep(duration)

        # Return the inputs as outputs
        return {"inputs": inputs, "duration": duration}


class ConditionalNodeExecutor(NodeExecutor):
    """Executor for conditional nodes."""

    def __init__(self):
        """Initialize the conditional node executor."""
        super().__init__("conditional")

    @async_timed
    async def execute(
        self,
        node: WorkflowNode,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a conditional node.

        Args:
            node: The node to execute.
            inputs: Input values for the node.
            context: Execution context.

        Returns:
            Output values from the node.
        """
        # Get the condition
        condition = inputs.get("condition") or node.config.get("condition", "True")

        # Evaluate the condition
        condition_result = False
        try:
            # Create a safe globals dictionary
            safe_globals = {
                "inputs": inputs,
                "context": context,
            }
            condition_result = bool(eval(condition, safe_globals))
        except Exception as e:
            logger.warning(f"Error evaluating condition: {e}")

        # Get the true and false branches
        true_branch = inputs.get("true_branch") or node.config.get("true_branch", {})
        false_branch = inputs.get("false_branch") or node.config.get("false_branch", {})

        # Return the result and the selected branch
        if condition_result:
            return {
                "result": True,
                "output": true_branch,
            }
        else:
            return {
                "result": False,
                "output": false_branch,
            }


class TransformNodeExecutor(NodeExecutor):
    """Executor for data transformation nodes."""

    def __init__(self):
        """Initialize the transform node executor."""
        super().__init__("transform")

    @async_timed
    async def execute(
        self,
        node: WorkflowNode,
        inputs: Dict[str, Any],
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a data transformation.

        Args:
            node: The node to execute.
            inputs: Input values for the node.
            context: Execution context.

        Returns:
            Output values from the node.
        """
        # Get the transformation type
        transform_type = inputs.get("type") or node.config.get("type", "map")

        # Get the data to transform
        data = inputs.get("data")
        if data is None:
            return {"result": None}

        # Apply the transformation
        if transform_type == "map":
            # Get the mapping function
            mapping = inputs.get("mapping") or node.config.get("mapping", {})
            if callable(mapping):
                # If mapping is a function, apply it to each item
                if isinstance(data, list):
                    result = [mapping(item) for item in data]
                else:
                    result = mapping(data)
            elif isinstance(mapping, dict):
                # If mapping is a dictionary, apply it as a template
                if isinstance(data, list):
                    result = []
                    for item in data:
                        mapped_item = {}
                        for key, value in mapping.items():
                            if isinstance(value, str) and value.startswith("$."):
                                # Extract value from the item using JSONPath
                                path = value[2:].split(".")
                                item_value = item
                                for p in path:
                                    if isinstance(item_value, dict) and p in item_value:
                                        item_value = item_value[p]
                                    else:
                                        item_value = None
                                        break
                                mapped_item[key] = item_value
                            else:
                                mapped_item[key] = value
                        result.append(mapped_item)
                else:
                    result = {}
                    for key, value in mapping.items():
                        if isinstance(value, str) and value.startswith("$."):
                            # Extract value from the data using JSONPath
                            path = value[2:].split(".")
                            item_value = data
                            for p in path:
                                if isinstance(item_value, dict) and p in item_value:
                                    item_value = item_value[p]
                                else:
                                    item_value = None
                                    break
                            result[key] = item_value
                        else:
                            result[key] = value
            else:
                result = data
        elif transform_type == "filter":
            # Get the filter function or condition
            filter_condition = inputs.get("condition") or node.config.get("condition")
            if not filter_condition:
                result = data
            elif callable(filter_condition):
                # If filter is a function, apply it to each item
                if isinstance(data, list):
                    result = [item for item in data if filter_condition(item)]
                else:
                    result = data if filter_condition(data) else None
            elif isinstance(filter_condition, str):
                # If filter is a string, evaluate it as a condition
                if isinstance(data, list):
                    result = []
                    for item in data:
                        try:
                            # Create a safe globals dictionary
                            safe_globals = {
                                "item": item,
                                "inputs": inputs,
                                "context": context,
                            }
                            if eval(filter_condition, safe_globals):
                                result.append(item)
                        except Exception as e:
                            logger.warning(f"Error evaluating filter condition: {e}")
                else:
                    try:
                        # Create a safe globals dictionary
                        safe_globals = {
                            "item": data,
                            "inputs": inputs,
                            "context": context,
                        }
                        result = data if eval(filter_condition, safe_globals) else None
                    except Exception as e:
                        logger.warning(f"Error evaluating filter condition: {e}")
                        result = None
            else:
                result = data
        elif transform_type == "reduce":
            # Get the reduce function and initial value
            reduce_function = inputs.get("function") or node.config.get("function")
            initial_value = inputs.get("initial_value") or node.config.get("initial_value")

            if not isinstance(data, list):
                result = data
            elif not reduce_function:
                result = data
            elif callable(reduce_function):
                # If reduce_function is a function, use it directly
                from functools import reduce
                result = reduce(reduce_function, data, initial_value)
            elif isinstance(reduce_function, str):
                # If reduce_function is a string, evaluate it as a lambda
                try:
                    # Create a safe globals dictionary
                    safe_globals = {
                        "inputs": inputs,
                        "context": context,
                    }
                    # Define the reducer function
                    def reducer(acc, item):
                        safe_globals["acc"] = acc
                        safe_globals["item"] = item
                        return eval(reduce_function, safe_globals)

                    # Apply the reducer
                    from functools import reduce
                    result = reduce(reducer, data, initial_value)
                except Exception as e:
                    logger.warning(f"Error evaluating reduce function: {e}")
                    result = data
            else:
                result = data
        else:
            # Unknown transformation type
            result = data

        return {"result": result}


# Register node executors
orchestrator.register_node_executor(HttpNodeExecutor())
orchestrator.register_node_executor(PythonNodeExecutor())
orchestrator.register_node_executor(DelayNodeExecutor())
orchestrator.register_node_executor(ConditionalNodeExecutor())
orchestrator.register_node_executor(TransformNodeExecutor())