class Event:
    def __init__(self, *funcs):
        """
        Klasse für eventbasierte Kommunikation.

        :param funcs: Eine Aufzählung von Funktionspointern, die an das Event gebunden werden sollen.
        """
        self.__functions: list = []
        self.add_function(funcs)
        pass

    def add_function(self, function_ptr):
        """ Bindet neue Funktion(-en)

        :param function_ptr: Entweder ein Funktionspointer oder eine Liste von diesen
        :return: None
        """
        if type(function_ptr) == tuple:
            return self.add_function([*function_ptr])
        if type(function_ptr) == list:
            for f in function_ptr:
                self.add_function(f)
            return
        self.__functions.append(function_ptr)
        pass

    def remove_function(self, function_ptr):
        """ Entfernt gebundene Funktionen wieder

        :param function_ptr: Entweder ein Funktionspointer oder eine Liste von diesen
        :return None
        """
        if type(function_ptr) == tuple:
            return self.remove_function([*function_ptr])
        if type(function_ptr) == list:
            for f in function_ptr:
                self.remove_function(f)
            return
        self.__functions = [f for f in self.functions if f != function_ptr]

    def emit(self, *args):
        """
        Löst das Event aus und ruft alle gebundenen Funktionen mit den dieser Funktion gegebenen Argumenten auf.

        :raise AttributeError: Wenn ungültige Argumente für eine der gebundenen Funktionen existieren
        :param args: Die Argumente für die gebundenen Funktionen
        :return: None
        """
        for f in self.__functions:
            try:
                f(*args)
            except AttributeError as e:
                raise AttributeError(f"Die Funktion {str(f)} nimmt die Argumente {str(args)} nicht") from e
        pass

    @property
    def functions(self) -> list:
        """ Die gebundenen Funktionen des Events """
        return self.__functions

    def __iadd__(self, other):
        self.add_function(other)
        return self

    def __isub__(self, other):
        self.remove_function(other)
        return self

    def __call__(self, *args, **kwargs):
        self.emit(*args)

    def __repr__(self):
        return f"<{self.__class__.__name__} targets={str(self.functions)}>"
    pass
