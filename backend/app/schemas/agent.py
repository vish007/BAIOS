"""Schemas for agent governance endpoints."""

from pydantic import BaseModel, Field


class AgentCreateRequest(BaseModel):
    name: str = Field(..., min_length=3)
    description: str
    owner_team: str
    guardrail_bundle: str


class AgentResponse(BaseModel):
    id: str
    name: str
    status: str
    version: str
