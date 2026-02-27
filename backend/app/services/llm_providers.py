from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed

from app.core.config import Settings
from app.services.reliability import CircuitBreaker


@dataclass
class InferenceRequest:
    prompt: str
    context: dict


@dataclass
class InferenceResult:
    provider: str
    model: str
    output_text: str
    confidence: float
    metadata: dict


class LLMProvider(Protocol):
    name: str

    async def infer(self, request: InferenceRequest) -> InferenceResult: ...


class BaseHTTPProvider:
    name: str

    def __init__(self, settings: Settings, model: str) -> None:
        self.settings = settings
        self.model = model
        self.breaker = CircuitBreaker(
            failure_threshold=settings.circuit_breaker_threshold,
            reset_seconds=settings.circuit_breaker_reset_seconds,
        )

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0.25), reraise=True)
    async def _post(self, url: str, headers: dict, payload: dict) -> dict:
        if not self.breaker.allow_request():
            raise RuntimeError(f"Circuit open for provider {self.name}")

        try:
            async with httpx.AsyncClient(timeout=self.settings.request_timeout_seconds) as client:
                response = await client.post(url, headers=headers, json=payload)
                response.raise_for_status()
            self.breaker.on_success()
            return response.json()
        except Exception:
            self.breaker.on_failure()
            raise


class LlamaVisionProvider(BaseHTTPProvider):
    name = "llama_vision"

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        payload = {"model": self.model, "messages": [{"role": "user", "content": request.prompt}]}
        data = await self._post(self.settings.llama_vision_url, headers={}, payload=payload)
        output = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return InferenceResult(self.name, self.model, output, 0.86, {"source": "llama-service"})


class OpenAIProvider(BaseHTTPProvider):
    name = "openai"

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        payload = {"model": self.model, "messages": [{"role": "user", "content": request.prompt}]}
        headers = {"Authorization": f"Bearer {self.settings.openai_api_key}"}
        data = await self._post("https://api.openai.com/v1/chat/completions", headers=headers, payload=payload)
        output = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return InferenceResult(self.name, self.model, output, 0.85, {"source": "openai"})


class ClaudeProvider(BaseHTTPProvider):
    name = "claude"

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        payload = {"model": self.model, "max_tokens": 512, "messages": [{"role": "user", "content": request.prompt}]}
        headers = {
            "x-api-key": self.settings.claude_api_key or "",
            "anthropic-version": "2023-06-01",
        }
        data = await self._post("https://api.anthropic.com/v1/messages", headers=headers, payload=payload)
        output = ""
        if data.get("content"):
            output = data["content"][0].get("text", "")
        return InferenceResult(self.name, self.model, output, 0.85, {"source": "anthropic"})
