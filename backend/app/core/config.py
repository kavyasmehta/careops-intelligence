"""Centralized application configuration, loaded from environment variables.

Every setting has a sensible local-dev default so the app runs out of the
box with `docker compose up`; production deployments override via real
environment variables (never by editing this file).
"""
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "CareOps Intelligence API"
    environment: str = "development"
    log_level: str = "INFO"

    mongo_uri: str = "mongodb://mongo:27017"
    mongo_db: str = "careops"

    neo4j_uri: str = "bolt://neo4j:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "careops-dev-password"

    # Comma-separated list of allowed frontend origins (kept as a plain string
    # because pydantic-settings expects JSON syntax for list-typed env vars).
    cors_origins_raw: str = Field(default="http://localhost:3000", validation_alias="CORS_ORIGINS")

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins_raw.split(",") if origin.strip()]

    # AI case-summary feature: disabled (template-only) unless explicitly enabled.
    enable_llm_summary: bool = False
    llm_api_key: str | None = None

    seed_random_seed: int = 42


@lru_cache
def get_settings() -> Settings:
    return Settings()
