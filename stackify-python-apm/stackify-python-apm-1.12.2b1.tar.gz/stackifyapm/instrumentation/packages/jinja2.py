from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils import get_method_name
from stackifyapm.utils.helper import is_async_span


class Jinja2Instrumentation(AbstractInstrumentedModule):
    name = "jinja2"

    instrument_list = [("jinja2", "Template.render")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            context = {
                'CATEGORY': 'Template',
                'SUBCATEGORY': get_method_name(method).title(),
                'COMPONENT_CATEGORY': 'Template',
                'COMPONENT_DETAIL': 'Template',
                'TEMPLATE': instance.name or instance.filename or "<template string>",
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("template.jinja2", context, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
