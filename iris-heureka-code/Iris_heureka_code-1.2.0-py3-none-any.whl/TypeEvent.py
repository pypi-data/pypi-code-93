try:
    from .Event import Event
except ImportError:
    from Event import Event


class TypeEvent(Event):
    def __init__(self, *typen: type):
        """
        Klasse für eventbasierte Kommunikation mit statischen Typen.

        :param funcs: Eine Aufzählung der Typen, die fuer das Event gueltig sein sollen.
        """
        self.__typen: list[type] = [*typen]

        super(TypeEvent, self).__init__([])
        pass

    def emit(self, *args):
        """
        Löst das Event aus und ruft alle gebundenen Funktionen mit den dieser Funktion gegebenen Argumenten auf.

        :raise AttributeError: Wenn ungültige Argumente für eine der gebundenen Funktionen existieren (von Event)
        :raise TypeError: Wenn ungueltige Typen gegeben wurden. (Nicht im Konstruktor angegebene)
        :param args: Die Argumente für die gebundenen Funktionen
        :return: None
        """
        geg_typen = [type(arg) for arg in args]
        if not all([t1 == t2 for t1, t2 in zip(geg_typen, self.typen)]):
            raise TypeError(
                f"Die Argumente {args} haben die falschen Typen ({geg_typen}). Die richtigen sind {self.typen}")
        if len(geg_typen) != len(self.typen):
            raise AttributeError(f"Ungueltige Anzahl an Argumenten. "
                                 f"Gegeben sind {len(geg_typen)} aber {len(self.typen)} werden benoetigt.")
        return Event.emit(self, *args)

    @property
    def typen(self) -> list[type]:
        """ Die Typen, die fuer das Event gueltig sind. """
        return self.__typen

    def __repr__(self):
        return f"<TypeEvent {self.typen} {self.functions}>"

    def __copy__(self):
        return TypeEvent(*self.typen)
    pass
