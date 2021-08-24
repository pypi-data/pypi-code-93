from datetime import datetime
from typing import List, Dict
import json
import abc


class DomainEvent(metaclass=abc.ABCMeta):
    def __init__(self):
        self._occurred_on = datetime.now()

    def event_name(self) -> str:
        return self.__class__.__name__

    @property
    def occurred_on(self):
        return self._occurred_on

    def _serialize(self) -> str:
        def json_converter(o):
            if isinstance(o, datetime):
                return o.__str__()

        return json.dumps(self.__dict__, ensure_ascii=False, default=json_converter)

    def __str__(self) -> str:
        return self._serialize()

    def __repr__(self) -> str:
        return "DomainEvent <{}>".format(self.event_name())


class DomainEventPublisher:
    def __init__(self, event_handlers: Dict):
        self._event_handlers = event_handlers

    def publish(self, domain_events: List[DomainEvent]) -> None:
        for domain_event in domain_events:
            self._publish_event(domain_event)

    def _publish_event(self, domain_event: DomainEvent) -> None:
        domain_event_name = _classname(domain_event)

        event = self._event_handlers.get(domain_event_name)
        subscribers = event.get('subscribers')

        for subscriber in subscribers:
            subscriber_class = subscriber()
            subscriber_class.handle(domain_event)


def _classname(obj):
    cls = type(obj)
    module = cls.__module__
    name = cls.__qualname__
    if module is not None and module != "__builtin__":
        name = "{}.{}".format(module, name)

    return name
