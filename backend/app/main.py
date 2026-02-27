"""FastAPI application entrypoint for BAOS backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, health, workflows
from app.core.config import get_settings
from app.observability.telemetry import configure_telemetry

settings = get_settings()
configure_telemetry(service_name="baos-control-plane", otel_endpoint=settings.otel_endpoint)

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Enterprise Agentic Control Plane for banking workflows.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in production
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(agents.router, prefix=settings.api_prefix)
app.include_router(workflows.router, prefix=settings.api_prefix)
