from functools import wraps

from stackifyapm import set_transaction_context
from stackifyapm.contrib import _BaseServerlessStackifyAPM
from stackifyapm.instrumentation.control import instrument
from stackifyapm.utils import wrapt


class StackifyAPM(_BaseServerlessStackifyAPM):
    """
    Application class for AWS Lambda.
    """
    def __call__(self, func):

        @wraps(func)
        def wrapper(event, context, *args, **kwargs):
            # get data need from event and context
            self.func_name = context.function_name
            self.context = {
                "invoked_function_arn": context.invoked_function_arn,
            }

            with self:
                return func(event, context, *args, **kwargs)

        return wrapper

    def __enter__(self):
        self.client.begin_transaction("lambda", client=self.client)

    def __exit__(self, exc_type, exc_val, exc_tb):
        set_transaction_context(self.context, "lambda")
        super(StackifyAPM, self).__exit__(exc_type, exc_val, exc_tb)


def _resolve_path(module_string):
    module_string_list = module_string.split('.')
    module_path = '.'.join(module_string_list[:-1])
    function_name = module_string_list[-1]
    _, _, original = wrapt.resolve_path(module_path, function_name)

    return original


class HandlerWrapper(object):
    def __init__(self, **defaults):
        self.apm = StackifyAPM()
        instrument(self.apm.client)

    def __call__(self, func, *args, **kwargs):

        @wraps(func)
        def wrapper(event, context, *args, **kwargs):
            try:
                function_handler = _resolve_path(self.apm.client.config.lambda_handler)
            except Exception as e:
                raise Exception('Unable to find lambda handler. Error: {}'.format(e))

            return self.apm(function_handler)(event, context)

        return wrapper
