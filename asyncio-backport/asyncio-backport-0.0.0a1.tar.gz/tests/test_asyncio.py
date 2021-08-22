import asyncio
from typing import Dict, Type, Union

import pytest

import asyncio_backport


def test_run() -> None:
    async def demo() -> int:
        return 1

    assert asyncio_backport.run(demo()) == 1


def test_get_coro() -> None:
    async def demo() -> int:
        task = asyncio_backport.current_task()
        assert task is not None
        assert str(asyncio_backport.get_coro(task)).startswith(
            "<coroutine object test_get_coro.<locals>.demo at 0x"
        )
        return 6

    assert asyncio_backport.run(demo()) == 6


def test_get_running_loop() -> None:
    with pytest.raises(RuntimeError, match=r"no running event loop"):
        asyncio_backport.get_running_loop()


def test_run_cancel() -> None:
    done = False

    async def was_cancelled() -> None:
        nonlocal done
        with pytest.raises(asyncio.CancelledError):
            await asyncio.sleep(5)
        done = True

    async def demo() -> int:
        asyncio_backport.create_task(was_cancelled())
        await asyncio.sleep(0)
        return 3

    assert asyncio_backport.run(demo()) == 3
    assert done


def test_all_tasks_no_loop() -> None:
    with pytest.raises(RuntimeError, match=r"no running event loop"):
        asyncio_backport.all_tasks()


def test_run_nested() -> None:
    async def run() -> int:
        with pytest.raises(
            RuntimeError,
            match=r"asyncio\.run\(\) cannot be called from a running event loop",
        ):
            return asyncio_backport.run("ham")  # type: ignore[arg-type]

        return 4

    assert asyncio_backport.run(run()) == 4


def test_run_not_coro() -> None:
    with pytest.raises(ValueError, match=r"a coroutine was expected, got 'ham'"):
        asyncio_backport.run("ham")  # type: ignore[arg-type]


class MyError(Exception):
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, MyError):
            return NotImplemented

        return self.args == other.args

    def __hash__(self) -> int:
        return hash(self.args)


def test_myerror() -> None:
    assert MyError() == MyError()
    assert MyError() != object()
    assert hash(MyError()) == hash(MyError())


@pytest.mark.parametrize(
    "exc,logs_event", [(asyncio.CancelledError, False), (MyError, True)]
)
def test_run_cancel_raised(
    exc: Union[Type[asyncio.CancelledError], Type[MyError]], logs_event: bool
) -> None:
    done = False

    async def was_cancelled() -> None:
        nonlocal done
        with pytest.raises(asyncio.CancelledError):
            await asyncio.sleep(5)
        done = True
        raise exc()

    events = []

    def handler(loop: asyncio.AbstractEventLoop, context: Dict[str, object]) -> None:
        events.append((loop, context))

    loop = None
    task = None

    async def demo() -> int:
        nonlocal loop, task
        loop = asyncio_backport.get_running_loop()
        loop.set_exception_handler(handler)
        task = asyncio_backport.create_task(was_cancelled())
        await asyncio.sleep(0)
        return 3

    assert asyncio_backport.run(demo()) == 3
    assert done

    if logs_event:
        assert events == [
            (
                loop,
                {
                    "exception": MyError(),
                    "message": "unhandled exception during asyncio.run() shutdown",
                    "task": task,
                },
            )
        ]
    else:
        assert events == []


def test_get_current_task_loop_arg() -> None:
    async def demo() -> int:
        task = asyncio_backport.current_task(loop=asyncio_backport.get_running_loop())
        assert task is not None
        assert str(asyncio_backport.get_coro(task)).startswith(
            "<coroutine object test_get_current_task_loop_arg.<locals>.demo at 0x"
        )
        return 10

    assert asyncio_backport.run(demo()) == 10
