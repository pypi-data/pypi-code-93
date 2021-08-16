import os

from .base import TaskStrategy
from ..util import shellexpand


class SetFromEnvTask(TaskStrategy):
    def __init__(self, overrides=None):
        if overrides is None:
            overrides = {}
        self.overrides = overrides

    @classmethod
    def task_name(cls):
        return "set_from_env"

    def modify_params(self, params, variables=None):
        # passthrough params unmodified
        return params

    def execute(self, new_variables, variables=None):
        if type(new_variables) != dict:
            raise TypeError(
                "Expecting to receive a flat dict of new variables. Instead received:",
                new_variables,
            )
        # in order of precedence
        overrides = {
            **variables,
            **os.environ,
            **self.overrides,
        }
        return shellexpand(new_variables, overrides)
