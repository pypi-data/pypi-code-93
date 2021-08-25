#!/usr/bin/python3
# encoding: utf-8
from __future__ import print_function

from simple_event_bus.core import EVENT, EVENT_TYPE, AsyncEventBus, Event, EventBus
from simple_event_bus.event_source import (
    run_simple_event_source,
    run_simple_event_source_async,
)

from ._version import get_versions

__author__ = "AngusWG"
__email__ = "z740713651@outlook.com"
__version__ = get_versions()["version"]

del get_versions

__all__ = [
    __version__,
    # obj
    EVENT,
    EVENT_TYPE,  # for typing
    Event,
    EventBus,
    AsyncEventBus,
    # event_source
    run_simple_event_source,
    run_simple_event_source_async,
]
