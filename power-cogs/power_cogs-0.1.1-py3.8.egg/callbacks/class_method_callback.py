# internal
from power_cogs.callbacks.callback import Callback


class ClassMethodCallback(Callback):
    def __init__(self, method_name: str):
        super(ClassMethodCallback, self).__init__()
        self.method_name = method_name

    def run_function(self, wrapped_obj, *args, **kwargs):
        fn = getattr(wrapped_obj, self.method_name, None)
        if fn is None:
            raise ValueError(
                "{} does not have method {}".format(
                    wrapped_obj.__class__.__name__, self.method_name
                )
            )
        return fn(*args, **kwargs)

    def before(self, wrapped_obj, f, *args, **kwargs) -> None:
        self.run_function(wrapped_obj)

    def after(self, prev_output, wrapped_obj, f, *args, **kwargs):
        return self.run_function(wrapped_obj, prev_output)
