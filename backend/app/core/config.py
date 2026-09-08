from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or backend/.env."""

    app_name: str = "govmesh-backend"
    environment: str = "development"
    database_url: str = "postgresql://govmesh:govmesh@localhost:5432/govmesh"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-before-production"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
