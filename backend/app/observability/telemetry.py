import logging

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import Counter, Histogram

INFERENCE_LATENCY_MS = Histogram("baos_inference_latency_ms", "Inference latency in ms", buckets=(20, 50, 100, 200, 500, 1000, 2000))
WORKFLOW_RUNS = Counter("baos_workflow_runs_total", "Total workflow runs", ["status"])
GUARDRAIL_VIOLATIONS = Counter("baos_guardrail_violations_total", "Guardrail violations", ["type"])


def configure_telemetry(service_name: str, otel_endpoint: str | None) -> None:
    provider = TracerProvider(resource=Resource.create({"service.name": service_name}))
    trace.set_tracer_provider(provider)
    if otel_endpoint:
        exporter = OTLPSpanExporter(endpoint=otel_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
    LoggingInstrumentor().instrument(set_logging_format=True)


def instrument_fastapi(app) -> None:
    FastAPIInstrumentor.instrument_app(app)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
