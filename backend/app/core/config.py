from functools import lru_cache
from typing import Literal

from pydantic import Field
"""Application configuration and provider routing.

This file centralizes environment-driven settings so operators can switch
between Llama Vision, OpenAI, and Claude without touching service code.
"""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "BAOS Control Plane"
    env: Literal["dev", "qa", "prod"] = "dev"
    api_prefix: str = "/api/v1"

    database_url: str = "postgresql+psycopg://baos:baos@localhost:5432/baos"
    event_bus_backend: Literal["memory", "nats"] = "memory"
    nats_url: str = "nats://localhost:4222"

    default_provider: Literal["llama_vision", "openai", "claude"] = "llama_vision"
    llama_vision_url: str = "http://localhost:8080/v1/chat/completions"
    # Provider selected by default at runtime.
    default_provider: Literal["llama_vision", "openai", "claude"] = "llama_vision"

    # Model aliases keep frontend/API decoupled from provider model naming.
    llama_vision_model: str = "meta-llama/Llama-3.2-11B-Vision-Instruct"
    openai_model: str = "gpt-4o-mini"
    claude_model: str = "claude-3-5-sonnet-latest"

    openai_api_key: str | None = None
    claude_api_key: str | None = None
    request_timeout_seconds: float = 12.0
    retry_attempts: int = 3
    circuit_breaker_threshold: int = 5
    circuit_breaker_reset_seconds: int = 60

    jwt_issuer: str = "https://issuer.bank.local"
    jwt_audience: str = "baos-api"
    jwt_secret: str = Field(default="dev-insecure-secret", description="HS256 for local/dev")

    otel_endpoint: str | None = None
    cors_origins: str = "http://localhost:3000"
    confidence_threshold: float = 0.85

    otel_endpoint: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
