from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or backend/.env."""

    app_name: str = "govmesh-backend"
    environment: str = "development"

    # Default to local zero-latency SQLite; easily overridden by DATABASE_URL in .env or environment
    database_url: str = "sqlite:///./govmesh.db"

    database_url_unpooled: str | None = None

    redis_url: str = "redis://localhost:6379/0"

    secret_key: str = "change-me-before-production"

    identity_url: str = "http://localhost:8101"
    municipality_url: str = "http://localhost:8102"
    property_url: str = "http://localhost:8103"
    tax_url: str = "http://localhost:8104"

    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    workflow_execution_mode: Literal["sync"] = "sync"

    demo_controls_enabled: bool = True
    demo_control_key: str | None = "govmesh-demo-control-2026"

    execution_payload_limit_bytes: int = 16_384

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()