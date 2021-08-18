try:
    from .Event import Event
except ImportError:
    from Event import Event


class Handler:
    def __init__(self):
        """ Handler für die Verwaltung von Events. Nur fuer die Klasse "Event" funktionsfaehig."""
        self.__events = {}
        pass

    def new(self, name, *values):
        """ Fügt ein neues Event dem Handler hinzu.

        :param name: Der Name des Events
        :param values: Die Funktionen, die an das Event gebunden werden sollen
        """
        e = Event()
        values = [*values]
        if len(values) != 0:
            e += values
        self.__events[name] = e
        pass

    def get_event_names(self):
        """ Liste der Nammen aller diesem Handler zugehörigen Events """
        return list(self.__events.keys())

    def remove(self, name):
        """ Entfernt ein Event vom Handler """
        del self.__events[name]

    def __setitem__(self, key, value):
        self.new(key, value)
        pass

    def __getitem__(self, item) -> Event:
        return self.__events[item]

    def __delitem__(self, key):
        self.remove(key)
        pass

    def __getattr__(self, item) -> Event:
        return object.__getattribute__(self, "_Handler__events")[item]

    def __delattr__(self, item):
        self.remove(item)
        pass

    def __repr__(self):
        return f"<Handler events={str(self.get_event_names())}>"
    pass
