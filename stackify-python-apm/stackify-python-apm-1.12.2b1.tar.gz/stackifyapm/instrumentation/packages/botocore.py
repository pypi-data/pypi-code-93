import logging

from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import DroppedSpan
from stackifyapm.traces import execution_context
from stackifyapm.utils.compat import urlparse
from stackifyapm.utils.helper import is_async_span

logger = logging.getLogger("stackifyapm.instrument")


class BotocoreInstrumentation(AbstractInstrumentedModule):
    name = "botocore"

    instrument_list = [("botocore.client", "BaseClient._make_api_call")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            if "operation_name" in kwargs:
                operation_name = kwargs["operation_name"]
            else:
                operation_name = args[0]

            target_endpoint = instance._endpoint.host
            parsed_url = urlparse.urlparse(target_endpoint)
            if "." in parsed_url.hostname:
                service, region = parsed_url.hostname.split(".", 2)[:2]
            else:
                service, region = parsed_url.hostname, None

            context = {
                'CATEGORY': 'Http',
                'SUBCATEGORY': 'Execute',
                'COMPONENT_CATEGORY': 'Web External',
                'COMPONENT_DETAIL': 'Execute',
                'URL': instance.meta.endpoint_url,
                'OPERATION': operation_name,
                'SERVICE': service,
                'REGION': region,
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("ext.http.aws", context, leaf=True, is_async=is_async_span()) as span:
            request = wrapped(*args, **kwargs)

            try:
                if not isinstance(span, DroppedSpan):
                    span.context['STATUS'] = str(request.get('ResponseMetadata', {}).get('HTTPStatusCode', 500))
                    transaction = execution_context.get_transaction()
                    transaction.update_span_context(span.id, span.context)
            except Exception as e:
                logger.debug("Error while parsing response data. Error: {}.".format(e))

            return request
