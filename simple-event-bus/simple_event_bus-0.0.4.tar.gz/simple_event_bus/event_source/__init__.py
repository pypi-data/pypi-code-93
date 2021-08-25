# encoding: utf-8
# @Time   : 2021/8/9 15:00
# @author : zza
# @Email  : z740713651@outlook.com
# @File   : __init__.py

import asyncio
import datetime
import time
from typing import Union

from simple_event_bus.core import EVENT, EVENT_TYPE, AsyncEventBus, Event, EventBus


class _LoopStatus:
    def __init__(self):
        self.loop_enable: bool = True


def run_simple_event_source(
    event_bus: EventBus,
    time_interval: Union[int, float] = 1,
    loop_event: EVENT_TYPE = EVENT("HeartBeat"),
    close_loop_event: EVENT_TYPE = EVENT("close_loop"),
) -> None:
    """
    A simple event source

    Args:
        event_bus: instance of EventBus.
        time_interval: loop gap interval(seconds).
        loop_event: the default loop event type.
        close_loop_event: close loop event type.

    Returns:
        None
    """
    loop_config = _LoopStatus()

    def close_loop(_: Event = None) -> None:
        """close loop"""
        loop_config.loop_enable = False

    event_bus.add_listener(close_loop_event, close_loop)
    loop_event = event_bus.event_type_format(loop_event)

    while loop_config.loop_enable:
        event_bus.publish_event(Event(loop_event, now=datetime.datetime.now()))
        time.sleep(time_interval)
    event_bus.remove_listener(close_loop_event, close_loop)
    return


async def run_simple_event_source_async(
    event_bus: AsyncEventBus,
    time_interval: Union[int, float] = 1,
    loop_event: EVENT_TYPE = EVENT("HeartBeat"),
    close_loop_event: EVENT_TYPE = EVENT("close_loop"),
) -> None:
    """
    A simple event source for async.

    Args:
        event_bus: instance of EventBus.
        time_interval: loop gap interval(seconds).
        loop_event: the default loop event type.
        close_loop_event: close loop event type.

    Returns:
        None
    """
    loop_config = _LoopStatus()

    def close_loop(_: Event = None) -> None:
        """close loop"""
        loop_config.loop_enable = False

    loop_config.loop_enable = True
    event_bus.add_listener(close_loop_event, close_loop)
    loop_event = event_bus.event_type_format(loop_event)

    while loop_config.loop_enable:
        await event_bus.publish_event(Event(loop_event, now=datetime.datetime.now()))
        await asyncio.sleep(time_interval)
    event_bus.remove_listener(close_loop_event, close_loop)
    return


__all__ = [run_simple_event_source, run_simple_event_source_async]
