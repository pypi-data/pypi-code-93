try:
    from .Event import Event
    from .TypeEvent import TypeEvent
except ImportError:
    from Event import Event
    from TypeEvent import TypeEvent
from inspect import getmembers


class StaticHandler:
    def __init__(self, event_names: list[str] = None):
        """
        Oberklasse von der abgeleitet werden kann.
        Die Attribute der Unterklassen werden zu Events.
        TypeEvents funktionieren.
        Näheres zur Notation in der Dokumentation.
        """
        if event_names is not None:
            self.__add_attribute(event_names)
        self.__add_attrs_for_instance()

        pass

    def __add_attrs_for_instance(self):
        """ Durchsucht die Attribute, die den Unterklassen gegeben werden und macht daraus Events. """
        for i in getmembers(self):
            if isinstance(i[1], TypeEvent):
                self.__add_type_event(i)
            elif i[0] == "__annotations__":
                self.__add_attribute(list(i[1].keys()))
            elif (i[1] is None or type(i[1]) == Event) and ((i[0].startswith("__") and i[0].endswith("__")) is False):
                self.__add_attribute(i[0])
        pass

    def __add_attribute(self, attrs):
        """ Fuegt Attribute hinzu. Nimmt entweder eine Liste oder einen einzelnen String. """
        if type(attrs) == list:
            for attr in attrs:
                self.__add_attribute(attr)
            return None

        object.__setattr__(self, str(attrs), Event())
        pass

    def __add_type_event(self, t: tuple[str, TypeEvent]):
        """ Fuegt ein im Typ statisches Attribut hinzu. """

        object.__setattr__(self, str(t[0]), t[1].__copy__())
        pass

    def __setattr__(self, key, value):
        return None

    def __delattr__(self, item):
        return None

    pass
