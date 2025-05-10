"""
Configuration module for the Prompt MCP Server.

This module loads configuration from environment variables and provides
a settings object that can be imported by other modules.
"""

import os
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings for the Prompt MCP Server."""

    # Project metadata
    PROJECT_NAME: str = "Prompt MCP Server"
    PROJECT_DESCRIPTION: str = "A Master Control Program (MCP) server for prompt engineering with templates, memory, and pre-prompts"
    VERSION: str = "0.1.0"

    # Server settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS settings
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]

    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    # LLM settings
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    USE_LOCAL_MODELS: bool = False
    LOCAL_MODEL_ENDPOINT: Optional[str] = None
    LOCAL_MODELS: List[str] = Field(default_factory=list)

    # Memory settings
    MEMORY_TYPE: str = "in_memory"  # in_memory, redis, chroma
    REDIS_URL: Optional[str] = None
    CHROMA_PERSIST_DIRECTORY: Optional[str] = None

    # Template settings
    TEMPLATES_DIRECTORY: str = "templates"

    # Logging settings
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Validate CORS origins."""
        if isinstance(v, str) and v != "*":
            return [i.strip() for i in v.split(",")]
        if isinstance(v, str) and v == "*":
            return ["*"]
        return v

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Create settings instance
settings = Settings()