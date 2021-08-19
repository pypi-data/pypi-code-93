from __future__ import absolute_import

from warden_sdk import Hub
from warden_sdk.integrations import Integration, DidNotEnable
from warden_sdk.tracing import Span

from warden_sdk._functools import partial

from typing import Any
from typing import Dict
from typing import Optional
from typing import Type

try:
    from botocore import __version__ as BOTOCORE_VERSION  # type: ignore
    from botocore.client import BaseClient  # type: ignore
    from botocore.response import StreamingBody  # type: ignore
    from botocore.awsrequest import AWSRequest  # type: ignore
except ImportError:
    raise DidNotEnable("botocore is not installed")


class Boto3Integration(Integration):
    identifier = "boto3"

    @staticmethod
    def setup_once() -> None:
        try:
            version = tuple(map(int, BOTOCORE_VERSION.split(".")[:3]))
        except (ValueError, TypeError):
            raise DidNotEnable(
                "Unparsable botocore version: {}".format(BOTOCORE_VERSION)
            )
        if version < (1, 12):
            raise DidNotEnable("Botocore 1.12 or newer is required.")
        orig_init = BaseClient.__init__

        def sentry_patched_init(self, *args, **kwargs) -> None:
            orig_init(self, *args, **kwargs)
            meta = self.meta
            service_id = meta.service_model.service_id.hyphenize()
            meta.events.register(
                "request-created",
                partial(_sentry_request_created, service_id=service_id),
            )
            meta.events.register("after-call", _sentry_after_call)
            meta.events.register("after-call-error", _sentry_after_call_error)

        BaseClient.__init__ = sentry_patched_init


def _sentry_request_created(service_id, request, operation_name, **kwargs) -> None:
    hub = Hub.current
    if hub.get_integration(Boto3Integration) is None:
        return

    description = "aws.%s.%s" % (service_id, operation_name)
    span = hub.start_span(
        hub=hub,
        op="aws.request",
        description=description,
    )
    span.set_tag("aws.service_id", service_id)
    span.set_tag("aws.operation_name", operation_name)
    span.set_data("aws.request.url", request.url)

    # We do it in order for subsequent http calls/retries be
    # attached to this span.
    span.__enter__()

    # request.context is an open-ended data-structure
    # where we can add anything useful in request life cycle.
    request.context["_sentrysdk_span"] = span


def _sentry_after_call(context: Dict[str, Any], parsed: Dict[str, Any], **kwargs) -> None:
    span: Optional[Span] = context.pop("_sentrysdk_span", None)

    # Span could be absent if the integration is disabled.
    if span is None:
        return
    span.__exit__(None, None, None)

    body = parsed.get("Body")
    if not isinstance(body, StreamingBody):
        return

    streaming_span = span.start_child(
        op="aws.request.stream",
        description=span.description,
    )

    orig_read = body.read
    orig_close = body.close

    def sentry_streaming_body_read(*args, **kwargs) -> bytes:
        try:
            ret = orig_read(*args, **kwargs)
            if not ret:
                streaming_span.finish()
            return ret
        except Exception:
            streaming_span.finish()
            raise

    body.read = sentry_streaming_body_read

    def sentry_streaming_body_close(*args, **kwargs) -> None:
        streaming_span.finish()
        orig_close(*args, **kwargs)

    body.close = sentry_streaming_body_close


def _sentry_after_call_error(context: Dict[str, Any], exception: Type[BaseException], **kwargs) -> None:
    span: Optional[Span] = context.pop("_sentrysdk_span", None) 

    # Span could be absent if the integration is disabled.
    if span is None:
        return
    span.__exit__(type(exception), exception, None)
