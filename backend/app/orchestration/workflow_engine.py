"""Workflow engine for BAOS trade-finance execution paths."""

from uuid import uuid4

from app.services.llm_providers import InferenceRequest
from app.services.model_router import ModelRouter
from app.services.policy_engine import PolicyEngine


class WorkflowEngine:
    def __init__(self, router: ModelRouter, policy_engine: PolicyEngine) -> None:
        self.router = router
        self.policy_engine = policy_engine

    async def run(self, workflow_id: str, payload: dict, provider: str | None) -> dict:
        allowed, reasons = self.policy_engine.evaluate(payload)
        if not allowed:
            return {
                "run_id": str(uuid4()),
                "status": "blocked_by_policy",
                "provider": provider or "n/a",
                "output": {"violations": reasons},
            }

        model = self.router.resolve(provider_override=provider)
        result = await model.infer(
            InferenceRequest(
                prompt=f"Execute workflow {workflow_id} with banking-grade explainability.",
                context=payload,
            )
        )

        # Simplified workflow output object.
        return {
            "run_id": str(uuid4()),
            "status": "completed",
            "provider": result.provider,
            "output": {
                "summary": result.output_text,
                "confidence": result.confidence,
                "metadata": result.metadata,
            },
        }
