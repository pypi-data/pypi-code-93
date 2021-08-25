# encoding: utf-8
# @Time   : 2021/8/4 12:02
# @author : zza
# @Email  : z740713651@outlook.com
# @File   : event.py
from typing import TYPE_CHECKING, Any, Dict, Optional, TypeVar, Union

from simple_event_bus.errors import EVENTNameError

if TYPE_CHECKING:  # pragma: no cover
    # https://stackoverflow.com/questions/39740632/python-type-hinting-without-cyclic-imports
    from simple_event_bus.core import AsyncEventBus, EventBus


class EVENT(str):
    event_map: Dict[str, "EVENT"] = dict()

    def __new__(cls, name: str):
        if " " in name:
            raise EVENTNameError
        elif name in cls.event_map:
            return cls.event_map[name]
        else:
            item = super(EVENT, cls).__new__(cls, name)
            cls.event_map[name] = item
            return item


EVENT_TYPE = TypeVar("EVENT_TYPE", str, EVENT)


class Event(object):
    def __init__(self, event_type: EVENT_TYPE, **kwargs: Any):
        if isinstance(event_type, str):
            event_type = EVENT(event_type)
        self.__dict__: Dict[EVENT:Any] = kwargs
        self.event_type = event_type
        self.current_app: Optional[Union["EventBus", "AsyncEventBus"]] = None

    def __repr__(self) -> str:
        _attr = ", ".join(
            "{}={}".format(k, repr(v))
            for k, v in self.__dict__.items()
            if k != "event_type"
        )
        return f"Event({self.event_type}, {_attr})"

    def __getattribute__(self, *args, **kwargs) -> Any:  # for typing check
        return super(Event, self).__getattribute__(*args, **kwargs)
