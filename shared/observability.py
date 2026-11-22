import os
from openinference.instrumentation.anthropic import AnthropicInstrumentor
from phoenix.otel import register


def init_tracing(project_name: str = "agent-design-patterns-playbook") -> None:
    """Register Arize Phoenix OpenTelemetry tracing and instrument Anthropic calls."""
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://localhost:4317")
    tracer_provider = register(project_name=project_name, endpoint=endpoint)
    AnthropicInstrumentor().instrument(tracer_provider=tracer_provider)
