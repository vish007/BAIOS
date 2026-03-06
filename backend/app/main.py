from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import agents, health, workflows
from app.core.config import get_settings
from app.core.database import Base, engine
from app.observability.telemetry import configure_telemetry, instrument_fastapi

settings = get_settings()
configure_telemetry(service_name="baos-control-plane", otel_endpoint=settings.otel_endpoint)

app = FastAPI(title=settings.app_name, version="0.2.0", description="Enterprise Agentic Control Plane for banking workflows.")

origins = [origin.strip() for origin in settings.cors_origins.split(",") if origin.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_methods=["GET", "POST", "PUT"], allow_headers=["Authorization", "Content-Type"])

app.include_router(health.router, prefix=settings.api_prefix)
app.include_router(agents.router, prefix=settings.api_prefix)
app.include_router(workflows.router, prefix=settings.api_prefix)
instrument_fastapi(app)


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)
