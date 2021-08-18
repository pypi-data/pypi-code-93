try:
    from .Event import Event
    from .StaticHandler import StaticHandler
except ImportError:
    from Event import Event
    from StaticHandler import StaticHandler
from inspect import getmembers


def RecursiveHandler(orig):
    """
    Dekorator, der das Einbinden einer Unterklasse in einen StaticHandler ermoeglicht.
    :param orig: Dekorierte Klasse
    :return: Veraenderte Klasse
    """
    def __init__(self):
        super(self.__class__, self).__init__()
        for i in getmembers(self):
            try:
                if issubclass(i[1], StaticHandler):
                    object.__setattr__(self, i[0], object.__getattribute__(orig, i[0])())
            except TypeError:
                pass

    orig.__init__ = __init__
    return orig
