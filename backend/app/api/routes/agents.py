from uuid import uuid4

from fastapi import APIRouter

from app.schemas.agent import AgentCreateRequest, AgentResponse

router = APIRouter(prefix="/agents", tags=["agents"])


@router.post("", response_model=AgentResponse)
async def create_agent(request: AgentCreateRequest) -> AgentResponse:
    # Placeholder persistence. Replace with repository + DB transaction.
    return AgentResponse(
        id=str(uuid4()),
        name=request.name,
        status="active",
        version="v1.0.0",
    )
