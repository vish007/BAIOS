from uuid import uuid4

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import UserContext, evaluate_abac, require_permission
from app.models import Agent
from app.schemas.agent import AgentCreateRequest, AgentResponse
from app.services.audit import append_audit_log

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse)
async def create_agent(
    request: AgentCreateRequest,
    db: Session = Depends(get_db),
    user: UserContext = Depends(require_permission("agents:create")),
) -> AgentResponse:
    evaluate_abac(user, {"lob": request.owner_team})
    row = Agent(
        id=str(uuid4()),
        name=request.name,
        description=request.description,
        owner_team=request.owner_team,
        guardrail_bundle=request.guardrail_bundle,
    )
    db.add(row)
    db.commit()
    append_audit_log(db, actor_id=user.sub, action="agents:create", resource=row.id, details={"name": row.name})
    return AgentResponse(id=row.id, name=row.name, status="active", version="v1.0.0")
