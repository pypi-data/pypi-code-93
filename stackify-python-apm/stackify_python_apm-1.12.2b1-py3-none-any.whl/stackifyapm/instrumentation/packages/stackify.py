import uuid

from stackifyapm.exceptions import StackifyAPMException
from stackifyapm.instrumentation.decorators import call_exception_handler
from stackifyapm.instrumentation.packages.base import AbstractInstrumentedModule
from stackifyapm.traces import CaptureSpan
from stackifyapm.traces import execution_context
from stackifyapm.utils.helper import is_async_span


class StackifyInstrumentation(AbstractInstrumentedModule):
    # instrumentation for stackify-api-python module
    # we add trans_id and log_id in the logging api for trace/log integration

    name = "stackify"

    # monkeypatched enqueue method of StackifyHandler class
    # where we add trans_id and log_id into the record object
    # which is the first argument of args
    instrument_list = [("stackify.handler", "StackifyHandler.enqueue")]

    @call_exception_handler
    def call(self, module, method, wrapped, instance, args, kwargs):
        try:
            log_id = str(uuid.uuid4())
            if args:
                args[0].log_id = log_id

                transaction = execution_context.get_transaction()
                if transaction:
                    args[0].trans_id = transaction.get_id()

            context = {
                'CATEGORY': 'Stackify',
                'SUBCATEGORY': 'Log',
                'ID': log_id,
            }
        except Exception as e:
            raise StackifyAPMException(e)

        with CaptureSpan("stackify.log", context, leaf=True, is_async=is_async_span()):
            return wrapped(*args, **kwargs)
