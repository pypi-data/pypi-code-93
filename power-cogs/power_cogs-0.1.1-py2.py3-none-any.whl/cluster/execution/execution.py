from __future__ import annotations

import abc
import typing

import attr


@attr.s(repr=False)
class Execution(metaclass=abc.ABCMeta):

    # optional placeholder used to save some data for asynchronous operations
    async_data: typing.Any = attr.ib(default=None)

    @abc.abstractmethod
    def execute(self, *args, **kwargs) -> typing.Any:
        """
            Main execution function
        """

    @classmethod
    def create(cls, *args, **kwargs) -> Execution:
        """Return an Execution from args + kwargs

        Returns:
            Execution
        """
        return cls(*args, **kwargs)
