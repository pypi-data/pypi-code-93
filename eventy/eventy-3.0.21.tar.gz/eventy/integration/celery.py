# Copyright (c) Qotto, 2021

"""
Celery integration utilities

Utility functions to integrate the eventy protocol in celery apps

You need to install celery optional dependencies ("pip install eventy[celery]")
"""

import logging
from contextvars import copy_context
from functools import wraps
from typing import Callable, List, Dict, Any

from celery import shared_task as celery_shared_task
from celery.execute import send_task as celery_send_task
from celery.result import AsyncResult

from eventy.trace_id import correlation_id_var, request_id_var
from eventy.trace_id.generator import gen_trace_id

logger = logging.getLogger(__name__)

__all__ = [
    'send_task',
    'shared_task',
]


def send_task(name: str, args: List = None, kwargs: Dict = None, **options) -> AsyncResult:
    """
    Modified version of celery.execute.send_task adding context in task kwargs

    options ar propagated as celery send_task named arguments and keyword arguments

    Usage::

        from eventy.integration.celery import send_task

        send_task(
            'service.task.name', [],
            {
                'param': 'value',
            }
        )

    If a correlation_id is defined in the current context, it is equivalent to::

        from celery.execute import send_task
        from eventy.trace_id import correlation_id_var

        send_task(
            'service.task.name', [],
            {
                'correlation_id': correlation_id_var.get(),
                'param': 'value',
            }
        )
    """
    if args is None:
        args = []
    if kwargs is None:
        kwargs = {}

    if correlation_id_var.get():
        kwargs.update(correlation_id=correlation_id_var.get())

    return celery_send_task(name, args, kwargs, **options)


def shared_task(_func: Callable = None, **kwargs) -> Callable:
    """
    Modified version of celery.shared_task adding traces in the task keyword arguments

    ``correlation_id`` is fetched from context, or generated. ``request_id`` is always generated

    Usage::

        from eventy.integration.celery import shared_task

    Instead of::

        from celery import shared_task

    And then::

        @shared_task(options...)
        def my_task(param):
            ...


    :param _func: if used as a decorator with no args, decorated function will be first arg
    :param kwargs: options are propagated to celery's shared_task
    :return: new version of shared_task
    """

    def _shared_task_decorator(func: Callable) -> Callable:
        def _run_and_extract_trace_id(*func_args, **func_kwargs) -> Any:
            if 'correlation_id' in func_kwargs:
                correlation_id_var.set(func_kwargs.pop('correlation_id'))
            else:
                correlation_id_var.set(gen_trace_id(func))
            request_id_var.set(gen_trace_id(func))
            return func(*func_args, **func_kwargs)

        @wraps(func)
        def _run_inside_context(*func_args, **func_kwargs) -> Any:
            context = copy_context()
            return context.run(_run_and_extract_trace_id, *func_args, **func_kwargs)

        return celery_shared_task(**kwargs)(_run_inside_context)

    if _func:
        return _shared_task_decorator(_func)
    else:
        return _shared_task_decorator
