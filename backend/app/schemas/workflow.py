"""Schemas for workflow orchestration APIs."""

from pydantic import BaseModel


class WorkflowRunRequest(BaseModel):
    workflow_id: str
    input_payload: dict
    provider: str | None = None


class WorkflowRunResponse(BaseModel):
    run_id: str
    status: str
    provider: str
    output: dict
