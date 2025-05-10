"""
OpenHands AI integration connector.

This module provides a connector for integrating with OpenHands AI services.
"""

import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Union

from src.connectors.base import ConnectorConfig, ConnectorError, HttpConnector
from src.core.logging import get_logger
from src.core.performance import async_cached, async_profiled, async_timed

# Set up logging
logger = get_logger(__name__)


class OpenHandsConnector(HttpConnector):
    """Connector for OpenHands AI services."""

    def __init__(self, config: ConnectorConfig):
        """Initialize the OpenHands connector.

        Args:
            config: Connector configuration.
        """
        super().__init__(config)
        
        # Ensure API key is set
        if not config.api_key and "OPENHANDS_API_KEY" in os.environ:
            config.api_key = os.environ["OPENHANDS_API_KEY"]
        
        if not config.api_key:
            raise ConnectorError(
                "OpenHands API key is required",
                connector_type=self.connector_type,
                service_name=self.service_name,
            )
        
        # Set default base URL if not provided
        if not config.base_url:
            config.base_url = "https://api.openhands.ai/v1"
        
        # Set default headers
        config.headers.update({
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    async def _test_connection(self) -> None:
        """Test the connection to OpenHands.

        Raises:
            ConnectorError: If the connection test fails.
        """
        try:
            # Make a simple request to test the connection
            await self.request("GET", "models")
        except Exception as e:
            raise ConnectorError(
                f"Failed to connect to OpenHands: {e}",
                connector_type=self.connector_type,
                service_name=self.service_name,
                cause=e,
            )

    @async_timed
    async def list_models(self) -> List[Dict[str, Any]]:
        """List available models.

        Returns:
            List of model information.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", "models")
        return response["data"]["data"]

    @async_timed
    async def get_model(self, model_id: str) -> Dict[str, Any]:
        """Get information about a specific model.

        Args:
            model_id: ID of the model.

        Returns:
            Model information.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", f"models/{model_id}")
        return response["data"]

    @async_timed
    async def generate_text(
        self,
        model: str,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate text using a language model.

        Args:
            model: Model ID to use.
            prompt: Text prompt to generate from.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            frequency_penalty: Frequency penalty parameter.
            presence_penalty: Presence penalty parameter.
            stop: Stop sequences to end generation.
            **kwargs: Additional parameters.

        Returns:
            Generated text and metadata.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "model": model,
            "prompt": prompt,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            **kwargs
        }
        
        if stop:
            payload["stop"] = stop
        
        response = await self.request("POST", "completions", json=payload)
        return response["data"]

    @async_timed
    async def generate_chat(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 1.0,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate a chat response.

        Args:
            model: Model ID to use.
            messages: List of message objects with role and content.
            max_tokens: Maximum number of tokens to generate.
            temperature: Sampling temperature.
            top_p: Nucleus sampling parameter.
            frequency_penalty: Frequency penalty parameter.
            presence_penalty: Presence penalty parameter.
            stop: Stop sequences to end generation.
            **kwargs: Additional parameters.

        Returns:
            Generated chat response and metadata.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            **kwargs
        }
        
        if stop:
            payload["stop"] = stop
        
        response = await self.request("POST", "chat/completions", json=payload)
        return response["data"]

    @async_timed
    async def generate_embeddings(
        self,
        model: str,
        input_texts: Union[str, List[str]],
        **kwargs
    ) -> Dict[str, Any]:
        """Generate embeddings for text.

        Args:
            model: Model ID to use.
            input_texts: Text or list of texts to embed.
            **kwargs: Additional parameters.

        Returns:
            Text embeddings and metadata.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "model": model,
            "input": input_texts if isinstance(input_texts, list) else [input_texts],
            **kwargs
        }
        
        response = await self.request("POST", "embeddings", json=payload)
        return response["data"]

    @async_timed
    async def moderate_content(
        self,
        input_text: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Check content for policy violations.

        Args:
            input_text: Text to moderate.
            **kwargs: Additional parameters.

        Returns:
            Moderation results.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "input": input_text,
            **kwargs
        }
        
        response = await self.request("POST", "moderations", json=payload)
        return response["data"]

    @async_timed
    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate an image from a text prompt.

        Args:
            prompt: Text prompt to generate from.
            model: Model ID to use.
            size: Image size (e.g., "1024x1024").
            quality: Image quality.
            n: Number of images to generate.
            **kwargs: Additional parameters.

        Returns:
            Generated image data and metadata.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "prompt": prompt,
            "model": model,
            "size": size,
            "quality": quality,
            "n": n,
            **kwargs
        }
        
        response = await self.request("POST", "images/generations", json=payload)
        return response["data"]

    @async_timed
    async def edit_image(
        self,
        image: str,
        prompt: str,
        model: str = "dall-e-2",
        size: str = "1024x1024",
        n: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """Edit an image based on a prompt.

        Args:
            image: Base64-encoded image data or URL.
            prompt: Text prompt for editing.
            model: Model ID to use.
            size: Image size (e.g., "1024x1024").
            n: Number of images to generate.
            **kwargs: Additional parameters.

        Returns:
            Edited image data and metadata.

        Raises:
            ConnectorError: If the request fails.
        """
        import aiohttp
        
        # Prepare form data
        form = aiohttp.FormData()
        form.add_field("prompt", prompt)
        form.add_field("model", model)
        form.add_field("size", size)
        form.add_field("n", str(n))
        
        # Add image data
        if image.startswith(("http://", "https://")):
            async with aiohttp.ClientSession() as session:
                async with session.get(image) as response:
                    image_data = await response.read()
                    form.add_field("image", image_data, filename="image.png", content_type="image/png")
        else:
            # Assume base64 encoded
            import base64
            from io import BytesIO
            
            # Remove data URL prefix if present
            if image.startswith("data:image"):
                image = image.split(",")[1]
            
            image_data = base64.b64decode(image)
            form.add_field("image", image_data, filename="image.png", content_type="image/png")
        
        # Add additional parameters
        for key, value in kwargs.items():
            form.add_field(key, str(value))
        
        # Make the request
        response = await self.request("POST", "images/edits", data=form)
        return response["data"]

    @async_timed
    async def create_variation(
        self,
        image: str,
        model: str = "dall-e-2",
        size: str = "1024x1024",
        n: int = 1,
        **kwargs
    ) -> Dict[str, Any]:
        """Create variations of an image.

        Args:
            image: Base64-encoded image data or URL.
            model: Model ID to use.
            size: Image size (e.g., "1024x1024").
            n: Number of variations to generate.
            **kwargs: Additional parameters.

        Returns:
            Variation image data and metadata.

        Raises:
            ConnectorError: If the request fails.
        """
        import aiohttp
        
        # Prepare form data
        form = aiohttp.FormData()
        form.add_field("model", model)
        form.add_field("size", size)
        form.add_field("n", str(n))
        
        # Add image data
        if image.startswith(("http://", "https://")):
            async with aiohttp.ClientSession() as session:
                async with session.get(image) as response:
                    image_data = await response.read()
                    form.add_field("image", image_data, filename="image.png", content_type="image/png")
        else:
            # Assume base64 encoded
            import base64
            from io import BytesIO
            
            # Remove data URL prefix if present
            if image.startswith("data:image"):
                image = image.split(",")[1]
            
            image_data = base64.b64decode(image)
            form.add_field("image", image_data, filename="image.png", content_type="image/png")
        
        # Add additional parameters
        for key, value in kwargs.items():
            form.add_field(key, str(value))
        
        # Make the request
        response = await self.request("POST", "images/variations", data=form)
        return response["data"]

    @async_timed
    async def transcribe_audio(
        self,
        audio: str,
        model: str = "whisper-1",
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        language: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Transcribe audio to text.

        Args:
            audio: Base64-encoded audio data or URL.
            model: Model ID to use.
            prompt: Optional prompt to guide transcription.
            response_format: Format of the response.
            temperature: Sampling temperature.
            language: Language code (e.g., "en").
            **kwargs: Additional parameters.

        Returns:
            Transcription data.

        Raises:
            ConnectorError: If the request fails.
        """
        import aiohttp
        
        # Prepare form data
        form = aiohttp.FormData()
        form.add_field("model", model)
        form.add_field("response_format", response_format)
        form.add_field("temperature", str(temperature))
        
        if prompt:
            form.add_field("prompt", prompt)
        
        if language:
            form.add_field("language", language)
        
        # Add audio data
        if audio.startswith(("http://", "https://")):
            async with aiohttp.ClientSession() as session:
                async with session.get(audio) as response:
                    audio_data = await response.read()
                    form.add_field("file", audio_data, filename="audio.mp3", content_type="audio/mpeg")
        else:
            # Assume base64 encoded
            import base64
            
            # Remove data URL prefix if present
            if audio.startswith("data:audio"):
                audio = audio.split(",")[1]
            
            audio_data = base64.b64decode(audio)
            form.add_field("file", audio_data, filename="audio.mp3", content_type="audio/mpeg")
        
        # Add additional parameters
        for key, value in kwargs.items():
            form.add_field(key, str(value))
        
        # Make the request
        response = await self.request("POST", "audio/transcriptions", data=form)
        return response["data"]

    @async_timed
    async def translate_audio(
        self,
        audio: str,
        model: str = "whisper-1",
        prompt: Optional[str] = None,
        response_format: str = "json",
        temperature: float = 0.0,
        **kwargs
    ) -> Dict[str, Any]:
        """Translate audio to English text.

        Args:
            audio: Base64-encoded audio data or URL.
            model: Model ID to use.
            prompt: Optional prompt to guide translation.
            response_format: Format of the response.
            temperature: Sampling temperature.
            **kwargs: Additional parameters.

        Returns:
            Translation data.

        Raises:
            ConnectorError: If the request fails.
        """
        import aiohttp
        
        # Prepare form data
        form = aiohttp.FormData()
        form.add_field("model", model)
        form.add_field("response_format", response_format)
        form.add_field("temperature", str(temperature))
        
        if prompt:
            form.add_field("prompt", prompt)
        
        # Add audio data
        if audio.startswith(("http://", "https://")):
            async with aiohttp.ClientSession() as session:
                async with session.get(audio) as response:
                    audio_data = await response.read()
                    form.add_field("file", audio_data, filename="audio.mp3", content_type="audio/mpeg")
        else:
            # Assume base64 encoded
            import base64
            
            # Remove data URL prefix if present
            if audio.startswith("data:audio"):
                audio = audio.split(",")[1]
            
            audio_data = base64.b64decode(audio)
            form.add_field("file", audio_data, filename="audio.mp3", content_type="audio/mpeg")
        
        # Add additional parameters
        for key, value in kwargs.items():
            form.add_field(key, str(value))
        
        # Make the request
        response = await self.request("POST", "audio/translations", data=form)
        return response["data"]

    @async_timed
    async def create_assistant(
        self,
        name: str,
        instructions: str,
        model: str = "gpt-4",
        tools: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create an assistant.

        Args:
            name: Name of the assistant.
            instructions: Instructions for the assistant.
            model: Model ID to use.
            tools: List of tools for the assistant.
            **kwargs: Additional parameters.

        Returns:
            Assistant data.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "name": name,
            "instructions": instructions,
            "model": model,
            **kwargs
        }
        
        if tools:
            payload["tools"] = tools
        
        response = await self.request("POST", "assistants", json=payload)
        return response["data"]

    @async_timed
    async def list_assistants(
        self,
        limit: int = 20,
        order: str = "desc",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List assistants.

        Args:
            limit: Maximum number of assistants to return.
            order: Sort order.
            **kwargs: Additional parameters.

        Returns:
            List of assistants.

        Raises:
            ConnectorError: If the request fails.
        """
        params = {
            "limit": str(limit),
            "order": order,
            **kwargs
        }
        
        response = await self.request("GET", "assistants", params=params)
        return response["data"]["data"]

    @async_timed
    async def get_assistant(
        self,
        assistant_id: str
    ) -> Dict[str, Any]:
        """Get an assistant.

        Args:
            assistant_id: ID of the assistant.

        Returns:
            Assistant data.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", f"assistants/{assistant_id}")
        return response["data"]

    @async_timed
    async def update_assistant(
        self,
        assistant_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Update an assistant.

        Args:
            assistant_id: ID of the assistant.
            **kwargs: Fields to update.

        Returns:
            Updated assistant data.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("POST", f"assistants/{assistant_id}", json=kwargs)
        return response["data"]

    @async_timed
    async def delete_assistant(
        self,
        assistant_id: str
    ) -> Dict[str, Any]:
        """Delete an assistant.

        Args:
            assistant_id: ID of the assistant.

        Returns:
            Deletion status.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("DELETE", f"assistants/{assistant_id}")
        return response["data"]

    @async_timed
    async def create_thread(
        self,
        messages: Optional[List[Dict[str, Any]]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a thread.

        Args:
            messages: Initial messages for the thread.
            **kwargs: Additional parameters.

        Returns:
            Thread data.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {**kwargs}
        
        if messages:
            payload["messages"] = messages
        
        response = await self.request("POST", "threads", json=payload)
        return response["data"]

    @async_timed
    async def get_thread(
        self,
        thread_id: str
    ) -> Dict[str, Any]:
        """Get a thread.

        Args:
            thread_id: ID of the thread.

        Returns:
            Thread data.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", f"threads/{thread_id}")
        return response["data"]

    @async_timed
    async def delete_thread(
        self,
        thread_id: str
    ) -> Dict[str, Any]:
        """Delete a thread.

        Args:
            thread_id: ID of the thread.

        Returns:
            Deletion status.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("DELETE", f"threads/{thread_id}")
        return response["data"]

    @async_timed
    async def create_message(
        self,
        thread_id: str,
        role: str,
        content: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a message in a thread.

        Args:
            thread_id: ID of the thread.
            role: Role of the message sender.
            content: Message content.
            **kwargs: Additional parameters.

        Returns:
            Message data.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "role": role,
            "content": content,
            **kwargs
        }
        
        response = await self.request("POST", f"threads/{thread_id}/messages", json=payload)
        return response["data"]

    @async_timed
    async def list_messages(
        self,
        thread_id: str,
        limit: int = 20,
        order: str = "desc",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List messages in a thread.

        Args:
            thread_id: ID of the thread.
            limit: Maximum number of messages to return.
            order: Sort order.
            **kwargs: Additional parameters.

        Returns:
            List of messages.

        Raises:
            ConnectorError: If the request fails.
        """
        params = {
            "limit": str(limit),
            "order": order,
            **kwargs
        }
        
        response = await self.request("GET", f"threads/{thread_id}/messages", params=params)
        return response["data"]["data"]

    @async_timed
    async def get_message(
        self,
        thread_id: str,
        message_id: str
    ) -> Dict[str, Any]:
        """Get a message.

        Args:
            thread_id: ID of the thread.
            message_id: ID of the message.

        Returns:
            Message data.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", f"threads/{thread_id}/messages/{message_id}")
        return response["data"]

    @async_timed
    async def create_run(
        self,
        thread_id: str,
        assistant_id: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a run.

        Args:
            thread_id: ID of the thread.
            assistant_id: ID of the assistant.
            **kwargs: Additional parameters.

        Returns:
            Run data.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "assistant_id": assistant_id,
            **kwargs
        }
        
        response = await self.request("POST", f"threads/{thread_id}/runs", json=payload)
        return response["data"]

    @async_timed
    async def get_run(
        self,
        thread_id: str,
        run_id: str
    ) -> Dict[str, Any]:
        """Get a run.

        Args:
            thread_id: ID of the thread.
            run_id: ID of the run.

        Returns:
            Run data.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("GET", f"threads/{thread_id}/runs/{run_id}")
        return response["data"]

    @async_timed
    async def list_runs(
        self,
        thread_id: str,
        limit: int = 20,
        order: str = "desc",
        **kwargs
    ) -> List[Dict[str, Any]]:
        """List runs in a thread.

        Args:
            thread_id: ID of the thread.
            limit: Maximum number of runs to return.
            order: Sort order.
            **kwargs: Additional parameters.

        Returns:
            List of runs.

        Raises:
            ConnectorError: If the request fails.
        """
        params = {
            "limit": str(limit),
            "order": order,
            **kwargs
        }
        
        response = await self.request("GET", f"threads/{thread_id}/runs", params=params)
        return response["data"]["data"]

    @async_timed
    async def cancel_run(
        self,
        thread_id: str,
        run_id: str
    ) -> Dict[str, Any]:
        """Cancel a run.

        Args:
            thread_id: ID of the thread.
            run_id: ID of the run.

        Returns:
            Run data.

        Raises:
            ConnectorError: If the request fails.
        """
        response = await self.request("POST", f"threads/{thread_id}/runs/{run_id}/cancel")
        return response["data"]

    @async_timed
    async def wait_for_run(
        self,
        thread_id: str,
        run_id: str,
        poll_interval: float = 1.0,
        timeout: float = 300.0
    ) -> Dict[str, Any]:
        """Wait for a run to complete.

        Args:
            thread_id: ID of the thread.
            run_id: ID of the run.
            poll_interval: Interval between polls in seconds.
            timeout: Maximum time to wait in seconds.

        Returns:
            Final run data.

        Raises:
            ConnectorError: If the request fails or times out.
        """
        start_time = asyncio.get_event_loop().time()
        
        while True:
            run = await self.get_run(thread_id, run_id)
            
            if run["status"] in ["completed", "failed", "cancelled", "expired"]:
                return run
            
            # Check timeout
            elapsed = asyncio.get_event_loop().time() - start_time
            if elapsed > timeout:
                raise ConnectorError(
                    f"Timeout waiting for run to complete: {run_id}",
                    connector_type=self.connector_type,
                    service_name=self.service_name,
                )
            
            # Wait before polling again
            await asyncio.sleep(poll_interval)

    @async_timed
    async def create_thread_and_run(
        self,
        assistant_id: str,
        thread: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Create a thread and run in one request.

        Args:
            assistant_id: ID of the assistant.
            thread: Thread configuration.
            **kwargs: Additional parameters.

        Returns:
            Run data.

        Raises:
            ConnectorError: If the request fails.
        """
        payload = {
            "assistant_id": assistant_id,
            **kwargs
        }
        
        if thread:
            payload["thread"] = thread
        
        response = await self.request("POST", "threads/runs", json=payload)
        return response["data"]