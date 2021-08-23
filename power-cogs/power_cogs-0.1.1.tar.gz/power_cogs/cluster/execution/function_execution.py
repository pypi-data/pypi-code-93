import typing

from power_cogs.cluster.execution.execution import Execution


class FunctionExecution(Execution):
    def __init__(
        self,
        f: typing.Callable[[typing.Any], typing.Any],
        async_data: typing.Any = None,
    ):
        self.f = f
        self.async_data = async_data

    def execute(self, *args, **kwargs) -> typing.Any:
        return self.f(*args, **kwargs)
