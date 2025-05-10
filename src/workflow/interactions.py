"""
Complex Workflow Interactions.

This module provides optimized utilities for handling complex interactions
between workflows, including cross-workflow communication, data sharing,
and synchronization.
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
from src.workflow.orchestrator import (
    NodeStatus, WorkflowDefinition, WorkflowError, WorkflowExecution,
    WorkflowExecutionError, WorkflowNotFoundError, WorkflowStatus, orchestrator
)

# Set up logging
logger = get_logger(__name__)


class InteractionError(WorkflowError):
    """Error raised during workflow interactions."""
    def __init__(
        self,
        message: str,
        workflow_id: Optional[str] = None,
        node_id: Optional[str] = None,
        interaction_id: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            workflow_id=workflow_id,
            node_id=node_id,
            code="ERR_WORKFLOW_INTERACTION",
            details={
                "interaction_id": interaction_id,
                **kwargs.get("details", {})
            },
            **kwargs
        )
        self.interaction_id = interaction_id


class InteractionType(str, Enum):
    """Type of workflow interaction."""
    DATA_SHARING = "data_sharing"
    EVENT = "event"
    SYNCHRONIZATION = "synchronization"
    COORDINATION = "coordination"
    DELEGATION = "delegation"


class InteractionStatus(str, Enum):
    """Status of a workflow interaction."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMEOUT = "timeout"


@dataclass
class InteractionConfig:
    """Configuration for a workflow interaction."""
    id: str
    type: InteractionType
    source_workflow_id: str
    target_workflow_id: str
    data_mapping: Dict[str, str] = field(default_factory=dict)
    timeout: Optional[int] = None
    retry_policy: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class InteractionContext:
    """Context for a workflow interaction."""
    id: str
    config_id: str
    source_execution_id: str
    target_execution_id: Optional[str] = None
    status: InteractionStatus = InteractionStatus.PENDING
    data: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Dict[str, Any]] = None
    error: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None


class WorkflowInteractionManager:
    """Manager for workflow interactions."""

    def __init__(self):
        """Initialize the workflow interaction manager."""
        self.configs: Dict[str, InteractionConfig] = {}
        self.contexts: Dict[str, InteractionContext] = {}
        self._event_handlers: Dict[str, List[Callable]] = {}
        self._data_cache: Dict[str, Dict[str, Any]] = {}
        self._locks: Dict[str, asyncio.Lock] = {}
        self._active_interactions: Dict[str, asyncio.Task] = {}

    def register_interaction(self, config: InteractionConfig) -> None:
        """Register a workflow interaction configuration.

        Args:
            config: Interaction configuration.
        """
        self.configs[config.id] = config
        logger.info(f"Registered workflow interaction: {config.id}")

    def unregister_interaction(self, config_id: str) -> None:
        """Unregister a workflow interaction configuration.

        Args:
            config_id: ID of the interaction configuration.
        """
        if config_id in self.configs:
            del self.configs[config_id]
            logger.info(f"Unregistered workflow interaction: {config_id}")

    def get_interaction_config(self, config_id: str) -> InteractionConfig:
        """Get an interaction configuration by ID.

        Args:
            config_id: ID of the interaction configuration.

        Returns:
            Interaction configuration.

        Raises:
            InteractionError: If the configuration is not found.
        """
        config = self.configs.get(config_id)
        if not config:
            raise InteractionError(f"Interaction configuration not found: {config_id}")
        return config

    def get_interaction_context(self, context_id: str) -> InteractionContext:
        """Get an interaction context by ID.

        Args:
            context_id: ID of the interaction context.

        Returns:
            Interaction context.

        Raises:
            InteractionError: If the context is not found.
        """
        context = self.contexts.get(context_id)
        if not context:
            raise InteractionError(f"Interaction context not found: {context_id}")
        return context

    def list_interactions(
        self,
        workflow_id: Optional[str] = None,
        type: Optional[InteractionType] = None,
    ) -> List[InteractionConfig]:
        """List interaction configurations.

        Args:
            workflow_id: Optional workflow ID to filter by.
            type: Optional interaction type to filter by.

        Returns:
            List of interaction configurations.
        """
        configs = list(self.configs.values())

        if workflow_id:
            configs = [
                config for config in configs
                if config.source_workflow_id == workflow_id or config.target_workflow_id == workflow_id
            ]

        if type:
            configs = [config for config in configs if config.type == type]

        return configs

    def list_contexts(
        self,
        config_id: Optional[str] = None,
        status: Optional[InteractionStatus] = None,
    ) -> List[InteractionContext]:
        """List interaction contexts.

        Args:
            config_id: Optional configuration ID to filter by.
            status: Optional status to filter by.

        Returns:
            List of interaction contexts.
        """
        contexts = list(self.contexts.values())

        if config_id:
            contexts = [context for context in contexts if context.config_id == config_id]

        if status:
            contexts = [context for context in contexts if context.status == status]

        return contexts

    @async_timed
    async def start_interaction(
        self,
        config_id: str,
        source_execution_id: str,
        data: Optional[Dict[str, Any]] = None,
        context_id: Optional[str] = None,
    ) -> str:
        """Start a workflow interaction.

        Args:
            config_id: ID of the interaction configuration.
            source_execution_id: ID of the source workflow execution.
            data: Optional data for the interaction.
            context_id: Optional ID for the interaction context.

        Returns:
            ID of the interaction context.

        Raises:
            InteractionError: If the interaction fails to start.
        """
        # Get the interaction configuration
        config = self.get_interaction_config(config_id)

        # Create a context ID if not provided
        if not context_id:
            context_id = str(uuid.uuid4())

        # Create the interaction context
        context = InteractionContext(
            id=context_id,
            config_id=config_id,
            source_execution_id=source_execution_id,
            data=data or {},
        )
        self.contexts[context_id] = context

        # Start the interaction in the background
        task = asyncio.create_task(self._execute_interaction(context))
        self._active_interactions[context_id] = task

        logger.info(f"Started workflow interaction: {context_id}")
        return context_id

    @async_profiled
    async def _execute_interaction(self, context: InteractionContext) -> None:
        """Execute a workflow interaction.

        Args:
            context: Interaction context.
        """
        try:
            # Get the interaction configuration
            config = self.get_interaction_config(context.config_id)

            # Update context status
            context.status = InteractionStatus.ACTIVE
            context.updated_at = datetime.now()

            # Get the source workflow execution
            try:
                source_execution = orchestrator.get_execution(context.source_execution_id)
            except Exception as e:
                raise InteractionError(
                    f"Failed to get source workflow execution: {e}",
                    workflow_id=config.source_workflow_id,
                    interaction_id=context.id,
                    cause=e,
                )

            # Process the interaction based on its type
            if config.type == InteractionType.DATA_SHARING:
                await self._handle_data_sharing(context, config, source_execution)
            elif config.type == InteractionType.EVENT:
                await self._handle_event(context, config, source_execution)
            elif config.type == InteractionType.SYNCHRONIZATION:
                await self._handle_synchronization(context, config, source_execution)
            elif config.type == InteractionType.COORDINATION:
                await self._handle_coordination(context, config, source_execution)
            elif config.type == InteractionType.DELEGATION:
                await self._handle_delegation(context, config, source_execution)
            else:
                raise InteractionError(
                    f"Unsupported interaction type: {config.type}",
                    workflow_id=config.source_workflow_id,
                    interaction_id=context.id,
                )

            # Update context status
            context.status = InteractionStatus.COMPLETED
            context.updated_at = datetime.now()
            context.completed_at = datetime.now()

            logger.info(f"Completed workflow interaction: {context.id}")

        except Exception as e:
            # Handle interaction error
            error_dict = ErrorHandler.handle_error(e, log_error=True, raise_error=False)
            context.status = InteractionStatus.FAILED
            context.updated_at = datetime.now()
            context.completed_at = datetime.now()
            context.error = error_dict

            logger.error(f"Failed workflow interaction: {context.id}")

        finally:
            # Clean up
            if context.id in self._active_interactions:
                del self._active_interactions[context.id]

    async def _handle_data_sharing(
        self,
        context: InteractionContext,
        config: InteractionConfig,
        source_execution: WorkflowExecution,
    ) -> None:
        """Handle a data sharing interaction.

        Args:
            context: Interaction context.
            config: Interaction configuration.
            source_execution: Source workflow execution.

        Raises:
            InteractionError: If the data sharing fails.
        """
        # Map data from source execution to target
        mapped_data = {}
        for target_key, source_path in config.data_mapping.items():
            # Parse the source path
            parts = source_path.split(".")
            if len(parts) < 2:
                continue

            # Get the data from the source execution
            if parts[0] == "inputs":
                value = source_execution.inputs.get(parts[1])
            elif parts[0] == "outputs":
                value = source_execution.outputs.get(parts[1])
            elif parts[0] == "node":
                if len(parts) < 3:
                    continue
                node_id = parts[1]
                output_key = parts[2]
                node_execution = source_execution.node_executions.get(node_id)
                if node_execution and node_execution.status == NodeStatus.COMPLETED:
                    value = node_execution.outputs.get(output_key)
                else:
                    value = None
            else:
                value = None

            # Add the value to the mapped data
            mapped_data[target_key] = value

        # Store the mapped data in the cache
        cache_key = f"data_sharing:{config.id}:{context.id}"
        self._data_cache[cache_key] = mapped_data

        # Update the context with the result
        context.result = {
            "data": mapped_data,
            "cache_key": cache_key,
        }

    async def _handle_event(
        self,
        context: InteractionContext,
        config: InteractionConfig,
        source_execution: WorkflowExecution,
    ) -> None:
        """Handle an event interaction.

        Args:
            context: Interaction context.
            config: Interaction configuration.
            source_execution: Source workflow execution.

        Raises:
            InteractionError: If the event handling fails.
        """
        # Create the event data
        event_data = {
            "interaction_id": context.id,
            "source_workflow_id": config.source_workflow_id,
            "source_execution_id": context.source_execution_id,
            "target_workflow_id": config.target_workflow_id,
            "timestamp": datetime.now().isoformat(),
            "data": context.data,
        }

        # Add mapped data from the source execution
        for target_key, source_path in config.data_mapping.items():
            # Parse the source path
            parts = source_path.split(".")
            if len(parts) < 2:
                continue

            # Get the data from the source execution
            if parts[0] == "inputs":
                value = source_execution.inputs.get(parts[1])
            elif parts[0] == "outputs":
                value = source_execution.outputs.get(parts[1])
            elif parts[0] == "node":
                if len(parts) < 3:
                    continue
                node_id = parts[1]
                output_key = parts[2]
                node_execution = source_execution.node_executions.get(node_id)
                if node_execution and node_execution.status == NodeStatus.COMPLETED:
                    value = node_execution.outputs.get(output_key)
                else:
                    value = None
            else:
                value = None

            # Add the value to the event data
            event_data[target_key] = value

        # Trigger event handlers
        event_type = config.metadata.get("event_type", "workflow.interaction")
        await self._trigger_event(event_type, event_data)

        # Update the context with the result
        context.result = {
            "event_type": event_type,
            "event_data": event_data,
        }

    async def _handle_synchronization(
        self,
        context: InteractionContext,
        config: InteractionConfig,
        source_execution: WorkflowExecution,
    ) -> None:
        """Handle a synchronization interaction.

        Args:
            context: Interaction context.
            config: Interaction configuration.
            source_execution: Source workflow execution.

        Raises:
            InteractionError: If the synchronization fails.
        """
        # Get or create a lock for the target workflow
        lock_key = f"sync:{config.target_workflow_id}"
        if lock_key not in self._locks:
            self._locks[lock_key] = asyncio.Lock()
        lock = self._locks[lock_key]

        # Acquire the lock
        async with lock:
            # Check if the target workflow is already running
            target_executions = orchestrator.list_executions(
                workflow_id=config.target_workflow_id,
                status=WorkflowStatus.RUNNING,
                limit=1,
            )

            if target_executions:
                # Wait for the target workflow to complete
                target_execution_id = target_executions[0]["id"]
                try:
                    # Poll for completion
                    max_wait = config.timeout or 300  # Default to 5 minutes
                    start_time = time.time()
                    while time.time() - start_time < max_wait:
                        target_execution = orchestrator.get_execution(target_execution_id)
                        if target_execution.status in [
                            WorkflowStatus.COMPLETED,
                            WorkflowStatus.FAILED,
                            WorkflowStatus.CANCELED,
                        ]:
                            break
                        await asyncio.sleep(1)
                    else:
                        raise InteractionError(
                            f"Timeout waiting for target workflow to complete: {target_execution_id}",
                            workflow_id=config.target_workflow_id,
                            interaction_id=context.id,
                        )
                except Exception as e:
                    raise InteractionError(
                        f"Failed to wait for target workflow: {e}",
                        workflow_id=config.target_workflow_id,
                        interaction_id=context.id,
                        cause=e,
                    )

            # Map data from source execution
            inputs = {}
            for target_key, source_path in config.data_mapping.items():
                # Parse the source path
                parts = source_path.split(".")
                if len(parts) < 2:
                    continue

                # Get the data from the source execution
                if parts[0] == "inputs":
                    value = source_execution.inputs.get(parts[1])
                elif parts[0] == "outputs":
                    value = source_execution.outputs.get(parts[1])
                elif parts[0] == "node":
                    if len(parts) < 3:
                        continue
                    node_id = parts[1]
                    output_key = parts[2]
                    node_execution = source_execution.node_executions.get(node_id)
                    if node_execution and node_execution.status == NodeStatus.COMPLETED:
                        value = node_execution.outputs.get(output_key)
                    else:
                        value = None
                else:
                    value = None

                # Add the value to the inputs
                inputs[target_key] = value

            # Execute the target workflow
            try:
                target_execution_id = await orchestrator.execute_workflow(
                    workflow_id=config.target_workflow_id,
                    inputs=inputs,
                    metadata={
                        "interaction_id": context.id,
                        "source_workflow_id": config.source_workflow_id,
                        "source_execution_id": context.source_execution_id,
                    },
                )
                context.target_execution_id = target_execution_id
            except Exception as e:
                raise InteractionError(
                    f"Failed to execute target workflow: {e}",
                    workflow_id=config.target_workflow_id,
                    interaction_id=context.id,
                    cause=e,
                )

            # Wait for the target workflow to complete
            try:
                # Poll for completion
                max_wait = config.timeout or 300  # Default to 5 minutes
                start_time = time.time()
                while time.time() - start_time < max_wait:
                    target_execution = orchestrator.get_execution(target_execution_id)
                    if target_execution.status in [
                        WorkflowStatus.COMPLETED,
                        WorkflowStatus.FAILED,
                        WorkflowStatus.CANCELED,
                    ]:
                        break
                    await asyncio.sleep(1)
                else:
                    raise InteractionError(
                        f"Timeout waiting for target workflow to complete: {target_execution_id}",
                        workflow_id=config.target_workflow_id,
                        interaction_id=context.id,
                    )

                # Check if the target workflow completed successfully
                if target_execution.status != WorkflowStatus.COMPLETED:
                    raise InteractionError(
                        f"Target workflow failed: {target_execution.error}",
                        workflow_id=config.target_workflow_id,
                        interaction_id=context.id,
                    )

                # Update the context with the result
                context.result = {
                    "target_execution_id": target_execution_id,
                    "target_outputs": target_execution.outputs,
                }
            except Exception as e:
                raise InteractionError(
                    f"Failed to wait for target workflow: {e}",
                    workflow_id=config.target_workflow_id,
                    interaction_id=context.id,
                    cause=e,
                )

    async def _handle_coordination(
        self,
        context: InteractionContext,
        config: InteractionConfig,
        source_execution: WorkflowExecution,
    ) -> None:
        """Handle a coordination interaction.

        Args:
            context: Interaction context.
            config: Interaction configuration.
            source_execution: Source workflow execution.

        Raises:
            InteractionError: If the coordination fails.
        """
        # Get the coordination point from metadata
        coordination_point = config.metadata.get("coordination_point")
        if not coordination_point:
            raise InteractionError(
                "Missing coordination point in metadata",
                workflow_id=config.source_workflow_id,
                interaction_id=context.id,
            )

        # Get or create a lock for the coordination point
        lock_key = f"coord:{coordination_point}"
        if lock_key not in self._locks:
            self._locks[lock_key] = asyncio.Lock()
        lock = self._locks[lock_key]

        # Get the coordination data
        coordination_data = {
            "interaction_id": context.id,
            "source_workflow_id": config.source_workflow_id,
            "source_execution_id": context.source_execution_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Add mapped data from the source execution
        for target_key, source_path in config.data_mapping.items():
            # Parse the source path
            parts = source_path.split(".")
            if len(parts) < 2:
                continue

            # Get the data from the source execution
            if parts[0] == "inputs":
                value = source_execution.inputs.get(parts[1])
            elif parts[0] == "outputs":
                value = source_execution.outputs.get(parts[1])
            elif parts[0] == "node":
                if len(parts) < 3:
                    continue
                node_id = parts[1]
                output_key = parts[2]
                node_execution = source_execution.node_executions.get(node_id)
                if node_execution and node_execution.status == NodeStatus.COMPLETED:
                    value = node_execution.outputs.get(output_key)
                else:
                    value = None
            else:
                value = None

            # Add the value to the coordination data
            coordination_data[target_key] = value

        # Acquire the lock
        async with lock:
            # Store the coordination data in the cache
            cache_key = f"coord:{coordination_point}:{context.id}"
            self._data_cache[cache_key] = coordination_data

            # Get all coordination data for this point
            coordination_data_list = []
            for key, data in self._data_cache.items():
                if key.startswith(f"coord:{coordination_point}:"):
                    coordination_data_list.append(data)

            # Check if we have all required participants
            required_participants = config.metadata.get("required_participants", 1)
            if len(coordination_data_list) >= required_participants:
                # Trigger the target workflow if specified
                if config.target_workflow_id:
                    try:
                        # Prepare inputs for the target workflow
                        inputs = {
                            "coordination_point": coordination_point,
                            "coordination_data": coordination_data_list,
                            "metadata": config.metadata,
                        }

                        # Execute the target workflow
                        target_execution_id = await orchestrator.execute_workflow(
                            workflow_id=config.target_workflow_id,
                            inputs=inputs,
                            metadata={
                                "interaction_id": context.id,
                                "coordination_point": coordination_point,
                            },
                        )
                        context.target_execution_id = target_execution_id

                        # Wait for the target workflow to complete
                        max_wait = config.timeout or 300  # Default to 5 minutes
                        start_time = time.time()
                        while time.time() - start_time < max_wait:
                            target_execution = orchestrator.get_execution(target_execution_id)
                            if target_execution.status in [
                                WorkflowStatus.COMPLETED,
                                WorkflowStatus.FAILED,
                                WorkflowStatus.CANCELED,
                            ]:
                                break
                            await asyncio.sleep(1)
                        else:
                            raise InteractionError(
                                f"Timeout waiting for target workflow to complete: {target_execution_id}",
                                workflow_id=config.target_workflow_id,
                                interaction_id=context.id,
                            )

                        # Update the context with the result
                        context.result = {
                            "coordination_point": coordination_point,
                            "coordination_data": coordination_data_list,
                            "target_execution_id": target_execution_id,
                            "target_outputs": target_execution.outputs,
                        }
                    except Exception as e:
                        raise InteractionError(
                            f"Failed to execute target workflow: {e}",
                            workflow_id=config.target_workflow_id,
                            interaction_id=context.id,
                            cause=e,
                        )
                else:
                    # Just store the coordination result
                    context.result = {
                        "coordination_point": coordination_point,
                        "coordination_data": coordination_data_list,
                    }

                # Clean up coordination data
                for key in list(self._data_cache.keys()):
                    if key.startswith(f"coord:{coordination_point}:"):
                        del self._data_cache[key]
            else:
                # Not enough participants yet
                context.result = {
                    "coordination_point": coordination_point,
                    "coordination_data": coordination_data_list,
                    "required_participants": required_participants,
                    "current_participants": len(coordination_data_list),
                    "waiting": True,
                }

    async def _handle_delegation(
        self,
        context: InteractionContext,
        config: InteractionConfig,
        source_execution: WorkflowExecution,
    ) -> None:
        """Handle a delegation interaction.

        Args:
            context: Interaction context.
            config: Interaction configuration.
            source_execution: Source workflow execution.

        Raises:
            InteractionError: If the delegation fails.
        """
        # Map data from source execution
        inputs = {}
        for target_key, source_path in config.data_mapping.items():
            # Parse the source path
            parts = source_path.split(".")
            if len(parts) < 2:
                continue

            # Get the data from the source execution
            if parts[0] == "inputs":
                value = source_execution.inputs.get(parts[1])
            elif parts[0] == "outputs":
                value = source_execution.outputs.get(parts[1])
            elif parts[0] == "node":
                if len(parts) < 3:
                    continue
                node_id = parts[1]
                output_key = parts[2]
                node_execution = source_execution.node_executions.get(node_id)
                if node_execution and node_execution.status == NodeStatus.COMPLETED:
                    value = node_execution.outputs.get(output_key)
                else:
                    value = None
            else:
                value = None

            # Add the value to the inputs
            inputs[target_key] = value

        # Add delegation metadata
        inputs["_delegation"] = {
            "interaction_id": context.id,
            "source_workflow_id": config.source_workflow_id,
            "source_execution_id": context.source_execution_id,
            "timestamp": datetime.now().isoformat(),
        }

        # Execute the target workflow
        try:
            target_execution_id = await orchestrator.execute_workflow(
                workflow_id=config.target_workflow_id,
                inputs=inputs,
                metadata={
                    "interaction_id": context.id,
                    "source_workflow_id": config.source_workflow_id,
                    "source_execution_id": context.source_execution_id,
                    "delegation": True,
                },
            )
            context.target_execution_id = target_execution_id
        except Exception as e:
            raise InteractionError(
                f"Failed to execute target workflow: {e}",
                workflow_id=config.target_workflow_id,
                interaction_id=context.id,
                cause=e,
            )

        # Wait for the target workflow to complete
        try:
            # Poll for completion
            max_wait = config.timeout or 300  # Default to 5 minutes
            start_time = time.time()
            while time.time() - start_time < max_wait:
                target_execution = orchestrator.get_execution(target_execution_id)
                if target_execution.status in [
                    WorkflowStatus.COMPLETED,
                    WorkflowStatus.FAILED,
                    WorkflowStatus.CANCELED,
                ]:
                    break
                await asyncio.sleep(1)
            else:
                raise InteractionError(
                    f"Timeout waiting for target workflow to complete: {target_execution_id}",
                    workflow_id=config.target_workflow_id,
                    interaction_id=context.id,
                )

            # Check if the target workflow completed successfully
            if target_execution.status != WorkflowStatus.COMPLETED:
                raise InteractionError(
                    f"Target workflow failed: {target_execution.error}",
                    workflow_id=config.target_workflow_id,
                    interaction_id=context.id,
                )

            # Update the context with the result
            context.result = {
                "target_execution_id": target_execution_id,
                "target_outputs": target_execution.outputs,
            }
        except Exception as e:
            raise InteractionError(
                f"Failed to wait for target workflow: {e}",
                workflow_id=config.target_workflow_id,
                interaction_id=context.id,
                cause=e,
            )

    async def cancel_interaction(self, context_id: str) -> None:
        """Cancel a workflow interaction.

        Args:
            context_id: ID of the interaction context.

        Raises:
            InteractionError: If the interaction is not found or cannot be canceled.
        """
        # Get the interaction context
        context = self.get_interaction_context(context_id)

        # Check if the interaction is already completed
        if context.status in [
            InteractionStatus.COMPLETED,
            InteractionStatus.FAILED,
            InteractionStatus.CANCELED,
            InteractionStatus.TIMEOUT,
        ]:
            return

        # Cancel the interaction
        context.status = InteractionStatus.CANCELED
        context.updated_at = datetime.now()
        context.completed_at = datetime.now()

        # Cancel the interaction task
        task = self._active_interactions.get(context_id)
        if task:
            task.cancel()
            del self._active_interactions[context_id]

        # Cancel the target workflow execution if it exists
        if context.target_execution_id:
            try:
                await orchestrator.cancel_execution(context.target_execution_id)
            except Exception as e:
                logger.warning(f"Failed to cancel target workflow execution: {e}")

        logger.info(f"Canceled workflow interaction: {context_id}")

    def register_event_handler(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None],
    ) -> None:
        """Register an event handler.

        Args:
            event_type: Type of event to handle.
            handler: Event handler function.
        """
        if event_type not in self._event_handlers:
            self._event_handlers[event_type] = []
        self._event_handlers[event_type].append(handler)
        logger.info(f"Registered event handler for {event_type}")

    def unregister_event_handler(
        self,
        event_type: str,
        handler: Callable[[Dict[str, Any]], None],
    ) -> None:
        """Unregister an event handler.

        Args:
            event_type: Type of event.
            handler: Event handler function.
        """
        if event_type in self._event_handlers:
            if handler in self._event_handlers[event_type]:
                self._event_handlers[event_type].remove(handler)
                logger.info(f"Unregistered event handler for {event_type}")

    async def _trigger_event(
        self,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> None:
        """Trigger event handlers for an event.

        Args:
            event_type: Type of event.
            event_data: Event data.
        """
        handlers = self._event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event_data)
                else:
                    handler(event_data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")

    def get_shared_data(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get shared data from the cache.

        Args:
            cache_key: Cache key.

        Returns:
            Shared data if found, None otherwise.
        """
        return self._data_cache.get(cache_key)

    def set_shared_data(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Set shared data in the cache.

        Args:
            cache_key: Cache key.
            data: Data to store.
        """
        self._data_cache[cache_key] = data

    def clear_shared_data(self, cache_key: str) -> None:
        """Clear shared data from the cache.

        Args:
            cache_key: Cache key.
        """
        if cache_key in self._data_cache:
            del self._data_cache[cache_key]

    def clear_all_shared_data(self) -> None:
        """Clear all shared data from the cache."""
        self._data_cache.clear()


# Create a global interaction manager
interaction_manager = WorkflowInteractionManager()


# Helper functions for common interaction patterns
async def share_data(
    source_workflow_id: str,
    source_execution_id: str,
    data_mapping: Dict[str, str],
) -> str:
    """Share data between workflows.

    Args:
        source_workflow_id: ID of the source workflow.
        source_execution_id: ID of the source workflow execution.
        data_mapping: Mapping of target keys to source paths.

    Returns:
        Cache key for the shared data.

    Raises:
        InteractionError: If the data sharing fails.
    """
    # Create a unique ID for the interaction
    config_id = f"data_sharing:{source_workflow_id}:{uuid.uuid4()}"

    # Register the interaction configuration
    config = InteractionConfig(
        id=config_id,
        type=InteractionType.DATA_SHARING,
        source_workflow_id=source_workflow_id,
        target_workflow_id="*",  # Any workflow can access the data
        data_mapping=data_mapping,
    )
    interaction_manager.register_interaction(config)

    # Start the interaction
    context_id = await interaction_manager.start_interaction(
        config_id=config_id,
        source_execution_id=source_execution_id,
    )

    # Wait for the interaction to complete
    while True:
        context = interaction_manager.get_interaction_context(context_id)
        if context.status in [
            InteractionStatus.COMPLETED,
            InteractionStatus.FAILED,
            InteractionStatus.CANCELED,
            InteractionStatus.TIMEOUT,
        ]:
            break
        await asyncio.sleep(0.1)

    # Check if the interaction completed successfully
    if context.status != InteractionStatus.COMPLETED:
        raise InteractionError(
            f"Data sharing failed: {context.error}",
            workflow_id=source_workflow_id,
            interaction_id=context_id,
        )

    # Return the cache key
    return context.result["cache_key"]


async def get_shared_data(cache_key: str) -> Dict[str, Any]:
    """Get shared data.

    Args:
        cache_key: Cache key for the shared data.

    Returns:
        Shared data.

    Raises:
        InteractionError: If the shared data is not found.
    """
    data = interaction_manager.get_shared_data(cache_key)
    if data is None:
        raise InteractionError(f"Shared data not found: {cache_key}")
    return data


async def trigger_workflow(
    source_workflow_id: str,
    source_execution_id: str,
    target_workflow_id: str,
    inputs: Dict[str, Any],
    wait_for_completion: bool = True,
    timeout: Optional[int] = None,
) -> Optional[str]:
    """Trigger another workflow.

    Args:
        source_workflow_id: ID of the source workflow.
        source_execution_id: ID of the source workflow execution.
        target_workflow_id: ID of the target workflow.
        inputs: Input data for the target workflow.
        wait_for_completion: Whether to wait for the target workflow to complete.
        timeout: Timeout in seconds for waiting.

    Returns:
        ID of the target workflow execution if wait_for_completion is False,
        otherwise None.

    Raises:
        InteractionError: If the workflow triggering fails.
    """
    # Create a unique ID for the interaction
    config_id = f"delegation:{source_workflow_id}:{target_workflow_id}:{uuid.uuid4()}"

    # Create data mapping
    data_mapping = {}
    for key, value in inputs.items():
        data_mapping[key] = f"custom.{key}"

    # Register the interaction configuration
    config = InteractionConfig(
        id=config_id,
        type=InteractionType.DELEGATION,
        source_workflow_id=source_workflow_id,
        target_workflow_id=target_workflow_id,
        data_mapping=data_mapping,
        timeout=timeout,
    )
    interaction_manager.register_interaction(config)

    # Start the interaction
    context_id = await interaction_manager.start_interaction(
        config_id=config_id,
        source_execution_id=source_execution_id,
        data={"custom": inputs},
    )

    # Return immediately if not waiting for completion
    if not wait_for_completion:
        context = interaction_manager.get_interaction_context(context_id)
        return context.target_execution_id

    # Wait for the interaction to complete
    while True:
        context = interaction_manager.get_interaction_context(context_id)
        if context.status in [
            InteractionStatus.COMPLETED,
            InteractionStatus.FAILED,
            InteractionStatus.CANCELED,
            InteractionStatus.TIMEOUT,
        ]:
            break
        await asyncio.sleep(0.1)

    # Check if the interaction completed successfully
    if context.status != InteractionStatus.COMPLETED:
        raise InteractionError(
            f"Workflow triggering failed: {context.error}",
            workflow_id=source_workflow_id,
            interaction_id=context_id,
        )

    return None


async def coordinate_workflows(
    workflow_id: str,
    execution_id: str,
    coordination_point: str,
    data: Dict[str, Any],
    required_participants: int,
    target_workflow_id: Optional[str] = None,
    timeout: Optional[int] = None,
) -> Dict[str, Any]:
    """Coordinate multiple workflows.

    Args:
        workflow_id: ID of the participating workflow.
        execution_id: ID of the workflow execution.
        coordination_point: Name of the coordination point.
        data: Data to share with other participants.
        required_participants: Number of participants required.
        target_workflow_id: Optional ID of a workflow to trigger when all participants are ready.
        timeout: Timeout in seconds.

    Returns:
        Coordination result.

    Raises:
        InteractionError: If the coordination fails.
    """
    # Create a unique ID for the interaction
    config_id = f"coordination:{coordination_point}:{workflow_id}:{uuid.uuid4()}"

    # Create data mapping
    data_mapping = {}
    for key, value in data.items():
        data_mapping[key] = f"custom.{key}"

    # Register the interaction configuration
    config = InteractionConfig(
        id=config_id,
        type=InteractionType.COORDINATION,
        source_workflow_id=workflow_id,
        target_workflow_id=target_workflow_id or "*",
        data_mapping=data_mapping,
        timeout=timeout,
        metadata={
            "coordination_point": coordination_point,
            "required_participants": required_participants,
        },
    )
    interaction_manager.register_interaction(config)

    # Start the interaction
    context_id = await interaction_manager.start_interaction(
        config_id=config_id,
        source_execution_id=execution_id,
        data={"custom": data},
    )

    # Wait for the interaction to complete
    max_wait = timeout or 300  # Default to 5 minutes
    start_time = time.time()
    while time.time() - start_time < max_wait:
        context = interaction_manager.get_interaction_context(context_id)
        if context.status in [
            InteractionStatus.COMPLETED,
            InteractionStatus.FAILED,
            InteractionStatus.CANCELED,
            InteractionStatus.TIMEOUT,
        ]:
            break
        await asyncio.sleep(1)
    else:
        await interaction_manager.cancel_interaction(context_id)
        raise InteractionError(
            f"Coordination timed out: {coordination_point}",
            workflow_id=workflow_id,
            interaction_id=context_id,
        )

    # Check if the interaction completed successfully
    if context.status != InteractionStatus.COMPLETED:
        raise InteractionError(
            f"Coordination failed: {context.error}",
            workflow_id=workflow_id,
            interaction_id=context_id,
        )

    return context.result