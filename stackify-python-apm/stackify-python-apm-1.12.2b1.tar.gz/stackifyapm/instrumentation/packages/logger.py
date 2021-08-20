import json
import sys
import traceback

from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.utils.helper import is_async_span


def get_stack_trace(exc_info):
    if not exc_info:
        type_, value, tb = sys.exc_info()
    else:
        type_, value, tb = exc_info

    stacks = traceback.extract_tb(tb)
    new_stacks = []

    for filename, lineno, method, text in reversed(stacks):
        new_stacks.append("file {}, line {} in {}: {}".format(filename, lineno, method, text))

    return json.dumps(new_stacks)


class LoggerInstrumentation(AbstractInstrumentedModule):
    name = "Logger"

    instrument_list = [("logging", "Logger.handle")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            record = args[0]
            context = {
                'CATEGORY': 'Log',
                'SUBCATEGORY': self.name,
                'LEVEL': record.levelname.upper(),
                'MESSAGE': record.getMessage(),
                'PREFIX': 'TRUE',
            }

            if record.exc_info:
                context['EXCEPTION'] = get_stack_trace(record.exc_info)
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("cpython.logging", context, leaf=True, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
