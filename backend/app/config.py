import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables or .env file.
    Designed for clean configuration management and easy explainability.
    """
    # Database Configuration (Neon Cloud PostgreSQL)
    DATABASE_URL: str = (
        "postgresql://neondb_owner:npg_vaXZ35wxMQGi@ep-gentle-cake-azij2y8q-pooler.c-3.ap-southeast-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"
    )

    # OpenRouter LLM Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "google/gemma-4-26b-a4b-it:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Application Configuration
    APP_NAME: str = "AI-Powered English Learning Chatbot (Under 7)"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "*"

    # Latency Budget SLA (in milliseconds)
    MAX_LATENCY_SLA_MS: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton to avoid re-reading files on every request."""
    return Settings()
