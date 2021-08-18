import asyncio
import inspect
import warnings
from typing import Awaitable

from idem.exec.init import ExecReturn


def _create_exec_return(ret, ref: str):
    try:
        return ExecReturn(
            **ret,
            ref=ref,
        )
    except TypeError:
        # TODO For now, log a warning when exec module output doesn't conform to this format.
        #  later, remove this try/except
        warnings.warn(
            "Exec modules must return a dictionary {'result': True|False, 'comment': Any, 'ret': Any}",
            DeprecationWarning,
        )
        return ret


async def _create_exec_return_coro(ret: Awaitable, ref: str):
    return _create_exec_return(await ret, ref)


def post(hub, ctx):
    """
    Convert the dict return to an immutable namespace addressable format
    """
    # TODO this isn't happening
    ref = ctx.func.__module__
    if asyncio.iscoroutine(ctx.ret):
        return _create_exec_return_coro(ctx.ret, ref)
    else:
        return _create_exec_return(ctx.ret, ref)


def _format_error(hub, ctx, exc: Exception):
    ret_str = f"{exc.__class__.__name__}: {inspect.getfile(ctx.func)}:{ctx.func.__name__}: {exc}"
    hub.log.error(ret_str)
    return {"result": False, "ret": None, "comment": ret_str}
