import abc
import typing

import attr

from power_cogs.base.base import Base
from power_cogs.cluster.execution import Execution


@attr.s(repr=False)
class Cluster(Base, metaclass=abc.ABCMeta):

    config: typing.Any = attr.ib(default={})
    cache: typing.Dict[str, typing.Any] = attr.ib(default={}, init=False)

    ALLOWED_EXECUTIONS = [Execution]

    def __attrs_post_init__(self):
        self._setup()

    def _setup(self) -> typing.Any:
        self.join_cluster = self.config.get("join_cluster", False)
        if self.join_cluster:
            self.connect()
        else:
            self.setup()
            self.connect()

    @abc.abstractmethod
    def setup(self) -> typing.Any:
        """Sets up the cluster
        """

    @abc.abstractmethod
    def shutdown(self) -> typing.Any:
        """Tears down the cluster
        """

    @abc.abstractmethod
    def execute(self, execution: Execution, *args, **kwargs) -> typing.Any:
        """Executes an Execution object execution function

        Args:
            execution (Execution): function that defines an execution

        Returns:
            typing.Any: [description]
        """

    def execute_list(
        self,
        executions: typing.List[Execution],
        execution_args: typing.List[typing.Any],
    ) -> typing.Any:
        """Executes an Execution object execution function

        Args:
            execution (Execution): function that defines an execution

        Returns:
            typing.Any: [description]
        """
        return [
            self.execute(execution, **execution_arg)
            for execution, execution_arg in zip(executions, execution_args)
        ]

    def create_execution(
        self, execution_class: typing.Callable, *args, **kwargs
    ) -> Execution:
        return execution_class(*args, **kwargs)

    def connect(self):
        """Connect without starting the cluster
        """
        pass

    def async_execute(self, execution: Execution) -> Execution:
        """Executes an Execution object execution function asynchronously

        Args:
            execution (Execution): function that defines an execution

        Returns:
            typing.Any: [description]
        """
        pass

    def get(self, execution: Execution) -> typing.Any:
        """gets result after async execution

        Args:
            execution (Execution): [description]

        Returns:
            typing.Any: [description]
        """
        pass

    def put(self, *args, **kwargs):
        """Optional function for putting data into a cache in the cluster

        Args:
            self ([type]): [description]
        """
        pass

    def __call__(self, execution: Execution, *args, **kwargs) -> typing.Any:
        if execution.__class__ not in self.__class__.ALLOWED_EXECUTIONS:
            raise ValueError(
                "Execution class {} not in allowlist {}".format(
                    execution.__class__, self.__class__.ALLOWED_EXECUTIONS
                )
            )
        return self.execute(execution, *args, **kwargs)
