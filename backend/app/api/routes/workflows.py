from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.database import get_db
from app.core.security import UserContext, require_permission
from app.models import MakerCheckerTask
from app.orchestration.workflow_engine import WorkflowEngine
from app.schemas.workflow import MakerCheckerResolveRequest, WorkflowRunRequest, WorkflowRunResponse
from app.services.audit import append_audit_log
from app.services.model_router import ModelRouter
from app.services.policy_engine import PolicyEngine

router = APIRouter(prefix="/workflow-runs", tags=["workflow-runs"])


def get_engine(settings: Settings = Depends(get_settings)) -> WorkflowEngine:
    return WorkflowEngine(router=ModelRouter(settings), policy_engine=PolicyEngine(), settings=settings)


@router.post("", response_model=WorkflowRunResponse)
async def create_workflow_run(
    request: WorkflowRunRequest,
    db: Session = Depends(get_db),
    engine: WorkflowEngine = Depends(get_engine),
    user: UserContext = Depends(require_permission("workflow:run")),
) -> WorkflowRunResponse:
    result = await engine.run(db=db, workflow_id=request.workflow_id, payload=request.input_payload, provider=request.provider, user=user)
    append_audit_log(db, actor_id=user.sub, action="workflow:run", resource=result["run_id"], details={"status": result["status"]})
    return WorkflowRunResponse(**result)


@router.post("/maker-checker/{task_id}/resolve")
async def resolve_maker_checker(
    task_id: str,
    request: MakerCheckerResolveRequest,
    db: Session = Depends(get_db),
    user: UserContext = Depends(require_permission("maker_checker:resolve")),
):
    task = db.query(MakerCheckerTask).filter(MakerCheckerTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = request.checker_decision
    task.checker_id = user.sub
    task.resolved = True
    db.commit()
    append_audit_log(db, actor_id=user.sub, action="maker_checker:resolve", resource=task.id, details={"decision": request.checker_decision, "note": request.checker_note})
    return {"task_id": task.id, "status": task.status}
