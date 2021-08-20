import json
import logging

from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import execution_context
from stackifyapm.utils import default_ports
from stackifyapm.utils.compat import urlparse
from stackifyapm.utils.compat import iteritems
from stackifyapm.utils.helper import is_async_span
from stackifyapm.utils.helper import safe_bytes_to_string

logger = logging.getLogger("stackifyapm.instrument")


def get_host_from_url(url):
    parsed_url = urlparse.urlparse(url)
    host = parsed_url.hostname or " "

    if parsed_url.port and default_ports.get(parsed_url.scheme) != parsed_url.port:
        host += ":" + str(parsed_url.port)

    return host


class RequestsInstrumentation(AbstractInstrumentedModule):
    name = "requests"

    instrument_list = [("requests.sessions", "Session.send")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            if "request" in kwargs:
                request = kwargs["request"]
            else:
                request = args[0]

            context = {
                'CATEGORY': 'Web External',
                'SUBCATEGORY': 'Execute',
                'COMPONENT_CATEGORY': 'Web External',
                'COMPONENT_DETAIL': 'Execute',
                'METHOD': request.method,
                'URL': request.url,
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("ext.http.requests", context, leaf=True, is_async=is_async_span()) as span:
            response = wrapped(*args, **kwargs)

            try:
                if not isinstance(span, DroppedSpan):
                    span.context['STATUS'] = str(response.status_code)

                    if self.client and self.client.config.prefix_enabled:
                        request_body = safe_bytes_to_string(request.body)
                        response_body = safe_bytes_to_string(response.content)
                        span.context['PREFIX_REQUEST_BODY'] = request_body
                        span.context['PREFIX_REQUEST_SIZE_BYTES'] = str(len(request_body))
                        span.context['PREFIX_REQUEST_HEADERS'] = json.dumps([{key: value} for key, value in iteritems(request.headers)])
                        span.context['PREFIX_RESPONSE_BODY'] = response_body
                        span.context['PREFIX_RESPONSE_SIZE_BYTES'] = str(len(response_body))
                        span.context['PREFIX_RESPONSE_HEADERS'] = json.dumps([{key: value} for key, value in iteritems(response.headers)])

                    transaction = execution_context.get_transaction()
                    transaction.update_span_context(span.id, span.context)
            except Exception as e:
                logger.debug("Error while parsing response data. Error: {}.".format(e))

            return response
