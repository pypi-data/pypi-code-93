import json
import logging

from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import execution_context
from stackifyapm.utils import default_ports
from stackifyapm.utils.compat import iteritems
from stackifyapm.utils.helper import is_async_span
from stackifyapm.utils.helper import safe_bytes_to_string

logger = logging.getLogger("stackifyapm.instrument")


class Urllib3Instrumentation(AbstractInstrumentedModule):
    name = "urllib3"

    instrument_list = [
        ("urllib3.connectionpool", "HTTPConnectionPool.urlopen"),
        ("requests.packages.urllib3.connectionpool", "HTTPConnectionPool.urlopen"),
    ]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            if "method" in kwargs:
                request_method = kwargs["method"]
            else:
                request_method = args[0]

            host = instance.host

            if instance.port != default_ports.get(instance.scheme):
                host += ":" + str(instance.port)

            if "url" in kwargs:
                url = kwargs["url"]
            else:
                url = args[1]

            url = instance.scheme + "://" + host + url
            context = {
                'CATEGORY': 'Web External',
                'SUBCATEGORY': 'Execute',
                'COMPONENT_CATEGORY': 'Web External',
                'COMPONENT_DETAIL': 'Execute',
                'METHOD': request_method.upper(),
                'URL': url,
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("ext.http.urllib3", context, leaf=True, is_async=is_async_span()) as span:
            leaf_span = span
            while isinstance(leaf_span, DroppedSpan):
                leaf_span = leaf_span.parent

            response = wrapped(*args, **kwargs)

            try:
                if not isinstance(span, DroppedSpan):
                    span.context['STATUS'] = str(response.status)

                    if self.client and self.client.config.prefix_enabled:
                        request_body = safe_bytes_to_string(kwargs.get('body', ''))
                        response_body = safe_bytes_to_string(response.data)

                        span.context['PREFIX_REQUEST_BODY'] = request_body
                        span.context['PREFIX_REQUEST_SIZE_BYTES'] = str(len(request_body))
                        span.context['PREFIX_REQUEST_HEADERS'] = json.dumps([{key: value} for key, value in iteritems(kwargs.get('headers', {}))])
                        span.context['PREFIX_RESPONSE_BODY'] = response_body
                        span.context['PREFIX_RESPONSE_SIZE_BYTES'] = str(len(response_body))
                        span.context['PREFIX_RESPONSE_HEADERS'] = json.dumps([{key: value} for key, value in iteritems(response.headers)])

                    transaction = execution_context.get_transaction()
                    transaction.update_span_context(span.id, span.context)
            except Exception as e:
                logger.debug("Error while parsing response data. Error: {}.".format(e))

            return response
