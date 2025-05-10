"""
Konfigurationsmodul für den LLM Cost Analyzer.

Dieses Modul lädt die Konfiguration aus Umgebungsvariablen und stellt
ein Settings-Objekt bereit, das von anderen Modulen importiert werden kann.
"""

import os
from typing import List, Optional, Union

from pydantic import AnyHttpUrl, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Einstellungen für den LLM Cost Analyzer."""

    # Projektmetadaten
    PROJECT_NAME: str = "LLM Cost Analyzer"
    PROJECT_DESCRIPTION: str = "Ein Modul zur Analyse der Komplexität von Aufgaben und Berechnung der Kosten für verschiedene LLM-Modelle"
    VERSION: str = "0.1.0"

    # Server-Einstellungen
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    DEBUG: bool = False

    # CORS-Einstellungen
    CORS_ORIGINS: List[Union[str, AnyHttpUrl]] = ["*"]

    # API-Keys
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    COHERE_API_KEY: Optional[str] = None

    # LLM-Einstellungen
    DEFAULT_MODEL: str = "gpt-3.5-turbo"
    USE_LOCAL_MODELS: bool = False
    LOCAL_MODEL_ENDPOINT: Optional[str] = None
    LOCAL_MODELS: List[str] = Field(default_factory=list)

    # Logging-Einstellungen
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    @field_validator("CORS_ORIGINS")
    @classmethod
    def validate_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        """Validiere CORS-Origins."""
        if isinstance(v, str) and v != "*":
            return [i.strip() for i in v.split(",")]
        if isinstance(v, str) and v == "*":
            return ["*"]
        return v

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )


# Erstelle Settings-Instanz
settings = Settings()