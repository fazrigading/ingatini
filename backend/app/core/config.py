"""Application configuration using environment variables."""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    database_url: str = "postgresql://user:password@localhost:5432/ingatini_db"

    # Google Gemini
    google_api_key: str = ""
    gemini_embedding_model: str = "models/embedding-001"
    gemini_llm_model: str = "gemini-pro"

    # Application
    debug: bool = True
    log_level: str = "INFO"
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173"]

    # Server
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000

    class Config:
        """Pydantic config."""

        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
