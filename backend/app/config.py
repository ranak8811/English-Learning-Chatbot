import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application Settings loaded from environment variables or .env file.
    Designed for clean configuration management and easy explainability.
    """
    # Database Configuration (Loaded strictly from .env / environment)
    DATABASE_URL: str = ""

    # OpenRouter LLM Configuration
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_MODEL: str = "nvidia/nemotron-3.5-super-vl:free"
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Native Google Gemini LLM Configuration
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-3.5-flash-lite"
    GEMINI_BASE_URL: str = "https://generativelanguage.googleapis.com/v1beta"

    # Application Configuration
    APP_NAME: str = "AI-Powered English Learning Chatbot (Under 7)"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    CORS_ORIGINS: str = "*"

    # Latency Budget SLA (in milliseconds)
    MAX_LATENCY_SLA_MS: int = 2000

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton to avoid re-reading files on every request."""
    return Settings()
