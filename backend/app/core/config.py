from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime configuration loaded from environment variables or backend/.env."""

    app_name: str = "govmesh-backend"
    environment: str = "development"
    database_url: str = "postgresql://govmesh:govmesh@localhost:5432/govmesh"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "change-me-before-production"
    
    identity_url: str = "http://localhost:8101"
    municipality_url: str = "http://localhost:8102"
    property_url: str = "http://localhost:8103"
    tax_url: str = "http://localhost:8104"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
