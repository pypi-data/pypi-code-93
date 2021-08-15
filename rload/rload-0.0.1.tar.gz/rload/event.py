import enum


class EventType(enum.Enum):
    """
    EventType for the Rload.
    """

    ADDED = 0
    MODIFIED = 1
    REMOVED = 2


class Event:
    """
    A simple event handler that based on `on` and `emit`.

    Example:
    ---

        >>> event = Event()
        >>> @event.on('test')
        >>> def test_handler(num):
        >>>     print(num)
        >>> ...
        >>> event.emit('test', 10)

    """

    def __init__(self):
        self.handlers = {}

    def emit(self, type, *args, **kwargs):
        if type in self.handlers:
            for handler in self.handlers[type]:
                handler(*args, **kwargs)

    def on(self, type, handler):
        _type = type

        def decorator(handler):
            type = _type or handler.__name__
            if type in self.handlers:
                self.handlers[type].append(handler)
            else:
                self.handlers[type] = [handler]
            return handler

        return decorator(handler) if handler else decorator

    def remove(self, type):
        try:
            self.handlers.pop(type)
        except Exception:
            raise ValueError("It looks like the handler is not yet registered?")

    def __len__(self):
        return len(self.handlers)
