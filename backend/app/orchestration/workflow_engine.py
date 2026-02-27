from uuid import uuid4

from sqlalchemy.orm import Session

from app.models import MakerCheckerTask, WorkflowRun
from app.services.event_bus import get_event_bus
from app.services.llm_providers import InferenceRequest
from app.services.model_router import ModelRouter
from app.services.policy_engine import PolicyEngine


class WorkflowEngine:
    def __init__(self, router: ModelRouter, policy_engine: PolicyEngine, settings) -> None:
        self.router = router
        self.policy_engine = policy_engine
        self.event_bus = get_event_bus(settings)
        self.settings = settings

    async def run(self, db: Session, workflow_id: str, payload: dict, provider: str | None, user) -> dict:
        run_id = str(uuid4())
        allowed, reasons = self.policy_engine.evaluate(payload, user=user)
        if not allowed:
            output = {"violations": reasons}
            row = WorkflowRun(id=run_id, workflow_id=workflow_id, status="blocked_by_policy", provider=provider or "n/a", confidence=0.0, output=output)
            db.add(row)
            db.commit()
            await self.event_bus.publish("baos.workflow.blocked", {"run_id": run_id, "reasons": reasons})
            return {"run_id": run_id, "status": "blocked_by_policy", "provider": provider or "n/a", "output": output}

        model = self.router.resolve(provider_override=provider)
        result = await model.infer(InferenceRequest(prompt=f"Execute workflow {workflow_id}", context=payload))

        status = "completed"
        if result.confidence < self.settings.confidence_threshold:
            status = "pending_maker_checker"

        output = {"summary": result.output_text, "confidence": result.confidence, "metadata": result.metadata}
        row = WorkflowRun(id=run_id, workflow_id=workflow_id, status=status, provider=result.provider, confidence=result.confidence, output=output)
        db.add(row)

        if status == "pending_maker_checker":
            task = MakerCheckerTask(id=str(uuid4()), run_id=run_id, reason="Low confidence score")
            db.add(task)
            await self.event_bus.publish("baos.maker_checker.requested", {"run_id": run_id, "reason": "Low confidence"})

        db.commit()
        await self.event_bus.publish("baos.workflow.completed", {"run_id": run_id, "status": status})
        return {"run_id": run_id, "status": status, "provider": result.provider, "output": output}
