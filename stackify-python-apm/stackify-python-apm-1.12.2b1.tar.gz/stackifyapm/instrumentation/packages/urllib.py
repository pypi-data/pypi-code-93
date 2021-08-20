import json
import logging

from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import execution_context
from stackifyapm.utils.helper import is_async_span
from stackifyapm.utils.helper import safe_bytes_to_string

logger = logging.getLogger("stackifyapm.instrument")


class UrllibInstrumentation(AbstractInstrumentedModule):
    name = "urllib"

    instrument_list = [
        ("urllib", "URLopener.open"),
        ("urllib.request", "AbstractHTTPHandler.do_open"),
    ]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            if method == "URLopener.open":
                url = args[0]
                request_method = len(args) > 1 and 'POST' or 'GET'
            else:
                request_object = args[1] if len(args) > 1 else kwargs["req"]
                request_method = request_object.get_method()
                url = request_object.get_full_url()

            context = {
                'CATEGORY': 'Web External',
                'SUBCATEGORY': 'Execute',
                'COMPONENT_CATEGORY': 'Web External',
                'COMPONENT_DETAIL': 'Execute',
                'METHOD': request_method,
                'URL': url,
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("ext.http.urllib", context, leaf=True, is_async=is_async_span()) as span:
            response = wrapped(*args, **kwargs)

            try:
                if not isinstance(span, DroppedSpan):
                    span.context['STATUS'] = str(response.code)

                    if self.client and self.client.config.prefix_enabled:
                        if method == "URLopener.open":
                            request_body = safe_bytes_to_string(len(args) > 1 and args[1] or "")
                            request_headers = json.dumps([{key: value} for key, value in instance.addheaders])
                        else:
                            request_body = safe_bytes_to_string(request_object.data)
                            request_headers = json.dumps([{key: value} for key, value in request_object.header_items()])

                        response_body = ""  # unable to get response context coz it will alter the return data cStringIO.StringO
                        response_headers = json.dumps([{key: value} for key, value in response.headers.items()])

                        span.context['PREFIX_REQUEST_BODY'] = request_body
                        span.context['PREFIX_REQUEST_SIZE_BYTES'] = str(len(request_body))
                        span.context['PREFIX_REQUEST_HEADERS'] = request_headers
                        span.context['PREFIX_RESPONSE_BODY'] = response_body
                        span.context['PREFIX_RESPONSE_SIZE_BYTES'] = str(len(response_body))
                        span.context['PREFIX_RESPONSE_HEADERS'] = response_headers

                    transaction = execution_context.get_transaction()
                    transaction.update_span_context(span.id, span.context)
            except Exception as e:
                logger.debug("Error while parsing response data. Error: {}.".format(e))

            return response
