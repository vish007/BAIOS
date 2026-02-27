"""Model router picks provider/model based on runtime config + request override."""

from app.core.config import Settings
from app.services.llm_providers import (
    ClaudeProvider,
    LlamaVisionProvider,
    LLMProvider,
    OpenAIProvider,
)


class ModelRouter:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def resolve(self, provider_override: str | None = None) -> LLMProvider:
        provider = provider_override or self.settings.default_provider

        if provider == "openai":
            return OpenAIProvider(model=self.settings.openai_model)
        if provider == "claude":
            return ClaudeProvider(model=self.settings.claude_model)

        # Default enterprise-safe path: private model on bank-owned infra.
        return LlamaVisionProvider(model=self.settings.llama_vision_model)
