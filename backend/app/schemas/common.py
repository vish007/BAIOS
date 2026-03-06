from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str = "baos-control-plane"


class ApiResponse(BaseModel):
    message: str
    detail: dict = Field(default_factory=dict)
