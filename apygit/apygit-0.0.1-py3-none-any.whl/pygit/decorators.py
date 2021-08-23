
class cached(object):
    def __init__(self, obj, attr: str = None):
        self._attr = attr or obj.__name__
        self._obj = obj

    def __get__(self, instance, owner):
        attr = self._obj(instance)
        setattr(instance, self._attr, attr)
        return attr
