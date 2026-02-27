from fastapi import APIRouter, Depends

from app.core.config import Settings, get_settings
from app.orchestration.workflow_engine import WorkflowEngine
from app.schemas.workflow import WorkflowRunRequest, WorkflowRunResponse
from app.services.model_router import ModelRouter
from app.services.policy_engine import PolicyEngine

router = APIRouter(prefix="/workflow-runs", tags=["workflow-runs"])


def get_engine(settings: Settings = Depends(get_settings)) -> WorkflowEngine:
    return WorkflowEngine(router=ModelRouter(settings), policy_engine=PolicyEngine())


@router.post("", response_model=WorkflowRunResponse)
async def create_workflow_run(
    request: WorkflowRunRequest,
    engine: WorkflowEngine = Depends(get_engine),
) -> WorkflowRunResponse:
    result = await engine.run(
        workflow_id=request.workflow_id,
        payload=request.input_payload,
        provider=request.provider,
    )
    return WorkflowRunResponse(**result)
