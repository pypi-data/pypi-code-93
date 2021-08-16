from prunner.loaders import FunctionLoader
from prunner.util import split_file_component
from .base import TaskStrategy


class ParamsNotDefined(Exception):
    def __init__(self, not_set, variables):
        super().__init__(
            f'These params have not been set: {", ".join(not_set)}',
            "If this is okay, give the params a default value."
            f"Here is dump of the variables that exist as of this point.",
            variables,
        )


def generate_args_from_function_signature(fn, variables):
    param_names = fn.__code__.co_varnames[: fn.__code__.co_argcount]
    param_default_values = fn.__defaults__ if fn.__defaults__ is not None else []
    param_defaults = dict(
        zip(param_names[-len(param_default_values) :], param_default_values)
    )
    overall_vars = {**param_defaults, **variables}

    # Make sure none of the arguments are missing, else throw error
    missing = [param for param in param_names if param not in overall_vars]
    if len(missing) != 0:
        raise ParamsNotDefined(missing, variables)

    args = [overall_vars[v] for v in param_names]
    return args


class FunctionTask(TaskStrategy):
    def __init__(self, default_filename):
        self.loader = FunctionLoader(default_filename)

    @classmethod
    def from_settings(cls, settings):
        return FunctionTask(f"{settings['PRUNNER_CONFIG_DIR']}/functions.py")

    @classmethod
    def task_name(cls):
        return "function"

    def execute(self, params, variables=None):
        if type(params) != str:
            raise TypeError(
                "Expecting a string with the set of variables to load. Instead received: ",
                params,
            )
        function_name, filename = split_file_component(params)
        fn = self.loader.get_function(function_name, filename)
        args = generate_args_from_function_signature(fn, variables)
        return fn(*args)
