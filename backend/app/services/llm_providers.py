"""LLM provider adapters.

A light-weight abstraction layer to support enterprise routing policies across
Llama Vision (default private deployment), OpenAI, and Anthropic Claude.

In production, each adapter should include robust auth, retries, rate limits,
and circuit breakers. Here we keep it intentionally clear and extensible.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


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


class LlamaVisionProvider:
    def __init__(self, model: str) -> None:
        self.name = "llama_vision"
        self.model = model

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        return InferenceResult(
            provider=self.name,
            model=self.model,
            output_text=(
                "[Llama Vision] Structured response for trade-finance scrutiny "
                f"on prompt: {request.prompt[:100]}"
            ),
            confidence=0.87,
            metadata={"reasoning_style": "document-grounded", "vision": True},
        )


class OpenAIProvider:
    def __init__(self, model: str) -> None:
        self.name = "openai"
        self.model = model

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        return InferenceResult(
            provider=self.name,
            model=self.model,
            output_text=f"[OpenAI] Policy-aware answer: {request.prompt[:100]}",
            confidence=0.84,
            metadata={"reasoning_style": "general", "vision": False},
        )


class ClaudeProvider:
    def __init__(self, model: str) -> None:
        self.name = "claude"
        self.model = model

    async def infer(self, request: InferenceRequest) -> InferenceResult:
        return InferenceResult(
            provider=self.name,
            model=self.model,
            output_text=f"[Claude] Guardrail-constrained output: {request.prompt[:100]}",
            confidence=0.85,
            metadata={"reasoning_style": "constitutional", "vision": False},
        )
