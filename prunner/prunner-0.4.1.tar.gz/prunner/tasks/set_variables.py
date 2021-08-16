from .base import TaskStrategy


class SetVariablesTask(TaskStrategy):
    @classmethod
    def task_name(cls):
        return "set_variables"

    def execute(self, new_variables, variables=None):
        if type(new_variables) != dict:
            raise TypeError(
                "Expecting to receive a flat dict of new variables. Instead received:",
                new_variables,
            )
        return new_variables
