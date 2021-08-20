from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils.helper import is_async_span


class ZLibInstrumentation(AbstractInstrumentedModule):
    name = 'zlib'

    instrument_list = [("zlib", "compress"), ("zlib", "decompress")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            context = {
                'CATEGORY': 'Compression',
                'SUBCATEGORY': 'Compression',
                'COMPONENT_CATEGORY': 'Compression',
                'COMPONENT_DETAIL': 'Compression',
                'OPERATION': method,
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("compression.zlib", context, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
