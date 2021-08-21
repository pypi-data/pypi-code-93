from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from microservice_template_core.settings import TracerConfig, ServiceConfig
tracer = None


def get_tracer():
    global tracer
    if not tracer:
        resource = Resource(attributes={
            "service.name": ServiceConfig.SERVICE_NAME
        })

        trace.set_tracer_provider(
            TracerProvider(resource=resource)
        )

        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{TracerConfig.AGENT_HOSTNAME}:{TracerConfig.AGENT_PORT}",
            insecure=True
        )

        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(otlp_exporter))

        tracer = trace.get_tracer(__name__)

    return tracer
