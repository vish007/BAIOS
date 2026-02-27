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

    # Provider selected by default at runtime.
    default_provider: Literal["llama_vision", "openai", "claude"] = "llama_vision"

    # Model aliases keep frontend/API decoupled from provider model naming.
    llama_vision_model: str = "meta-llama/Llama-3.2-11B-Vision-Instruct"
    openai_model: str = "gpt-4o-mini"
    claude_model: str = "claude-3-5-sonnet-latest"

    openai_api_key: str | None = None
    claude_api_key: str | None = None

    otel_endpoint: str | None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
