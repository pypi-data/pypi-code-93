# encoding: utf-8
# @Time   : 2021/8/4 12:04
# @author : zza
# @Email  : z740713651@outlook.com
# @File   : async_event_bus.py
import inspect
from typing import Callable, Union

from simple_event_bus.core.event import EVENT_TYPE, Event
from simple_event_bus.core.event_bus import EventBus


class AsyncEventBus(EventBus):
    async def _run_listener(
        self, event: Union[Event, EVENT_TYPE], listener: Callable
    ) -> Union[bool, None]:
        if inspect.iscoroutinefunction(listener):
            if self._need_event_param(listener):
                res = await listener(event)
            else:
                res = await listener()
        else:
            if self._need_event_param(listener):
                res = listener(event)
            else:
                res = listener()
        return res

    async def publish_event(self, event: Union[Event, EVENT_TYPE]) -> None:
        """Trigger the event list function.

        Both synchronous and asynchronous functions will trigger.
        if function return True, Other functions in the queue will not be triggered.

        Args:
            event: str, EVENT or instance of Event

        Returns:
            None
        """
        event = self.event_format(event)
        self.logger.debug(f"Get {event}")
        for listener in self._listeners[event.event_type]:
            res = await self._run_listener(event, listener)
            if res:
                # if listener return true. will break the loop
                self.logger.debug(f"{listener.__name__} break the loop")
                break
