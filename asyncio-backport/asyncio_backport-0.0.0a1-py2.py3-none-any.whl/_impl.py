"""
This module backports `asyncio.run` to Python 3.6.
You can check the original implementation on:
https://github.com/python/cpython/blob/3.7/Lib/asyncio/runners.py
"""

__all__ = [
    "run",
    "get_running_loop",
    "all_tasks",
    "current_task",
    "create_task",
    "get_coro",
]

import asyncio
import sys
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Coroutine,
    Generator,
    Optional,
    Set,
    TypeVar,
    Union,
    cast,
)

_T = TypeVar("_T")
_TaskYieldType = Optional["asyncio.Future[object]"]

if TYPE_CHECKING:  # pragma: no cover
    from typing_extensions import Protocol

    class HasCoro(Protocol[_T]):
        _coro: Union[Generator[_TaskYieldType, None, _T], Awaitable[_T]]


if sys.version_info >= (3, 8):  # pragma: py-lt-38
    get_coro = asyncio.Task.get_coro
else:  # pragma: py-gte-38

    def get_coro(
        task: "asyncio.Task[_T]",
    ) -> Union[Generator[_TaskYieldType, None, _T], Awaitable[_T]]:
        return cast("HasCoro[_T]", task)._coro


if sys.version_info >= (3, 7):  # pragma: py-lt-37
    from asyncio import all_tasks, current_task, get_running_loop, run
else:  # pragma: py-gte-37
    from asyncio import coroutines, events, tasks

    def get_running_loop() -> asyncio.AbstractEventLoop:
        """Return the running event loop.  Raise a RuntimeError if there is none.
        This function is thread-specific.
        """
        # NOTE: this function is implemented in C (see _asynciomodule.c)
        loop = events._get_running_loop()
        if loop is None:
            raise RuntimeError("no running event loop")
        return loop

    def all_tasks(
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> "Set[asyncio.Task[object]]":
        """Return a set of all tasks for the loop."""
        if loop is None:
            loop = get_running_loop()
        return asyncio.Task.all_tasks(loop)

    def run(main: Coroutine[Any, Any, _T], *, debug: bool = False) -> _T:
        """Execute the coroutine and return the result.
        This function runs the passed coroutine, taking care of
        managing the asyncio event loop and finalizing asynchronous
        generators.
        This function cannot be called when another asyncio event loop is
        running in the same thread.
        If debug is True, the event loop will be run in debug mode.
        This function always creates a new event loop and closes it at the end.
        It should be used as a main entry point for asyncio programs, and should
        ideally only be called once.
        Example:
            async def main():
                await asyncio.sleep(1)
                print('hello')
            asyncio.run(main())
        """
        if events._get_running_loop() is not None:
            raise RuntimeError(
                "asyncio.run() cannot be called from a running event loop"
            )

        if not coroutines.iscoroutine(main):
            raise ValueError(f"a coroutine was expected, got {main!r}")

        loop = events.new_event_loop()
        try:
            events.set_event_loop(loop)
            loop.set_debug(debug)
            return loop.run_until_complete(main)
        finally:
            try:
                _cancel_all_tasks(loop)
                loop.run_until_complete(loop.shutdown_asyncgens())
            finally:
                events.set_event_loop(None)
                loop.close()

    def _cancel_all_tasks(loop: asyncio.AbstractEventLoop) -> None:
        to_cancel = all_tasks(loop)
        if not to_cancel:
            return

        for task in to_cancel:
            task.cancel()

        loop.run_until_complete(
            tasks.gather(*to_cancel, loop=loop, return_exceptions=True)
        )

        for task in to_cancel:
            if task.cancelled():
                continue
            if task.exception() is not None:
                loop.call_exception_handler(
                    {
                        "message": "unhandled exception during asyncio.run() shutdown",
                        "exception": task.exception(),
                        "task": task,
                    }
                )

    def current_task(
        loop: Optional[asyncio.AbstractEventLoop] = None,
    ) -> "Optional[asyncio.Task[Any]]":
        if loop is None:
            loop = get_running_loop()

        return asyncio.Task.current_task(loop)


if sys.version_info >= (3, 8):  # pragma: py-lt-38
    from asyncio import create_task
elif sys.version_info >= (3, 7):  # pragma: py-lt-37 pragma: py-gte-38

    def create_task(
        coro: Union[Generator[_TaskYieldType, None, _T], Awaitable[_T]],
        *,
        name: Optional[str] = None,
    ) -> "asyncio.Task[_T]":
        """Schedule the execution of a coroutine object in a spawn task.
        Return a Task object.
        """
        return asyncio.create_task(coro)


else:  # pragma: py-gte-37

    def create_task(
        coro: Union[Generator[_TaskYieldType, None, _T], Awaitable[_T]],
        *,
        name: Optional[str] = None,
    ) -> "asyncio.Task[_T]":
        """Schedule the execution of a coroutine object in a spawn task.
        Return a Task object.
        """
        loop = get_running_loop()
        return loop.create_task(coro)
