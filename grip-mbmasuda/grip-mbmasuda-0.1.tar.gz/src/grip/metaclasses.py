import threading


class ThreadSafeSingleton(type):
    """
    Metaclass to create an instance if one does not yet exist, otherwise return the singleton
    """
    # the leading "__" is on purpose for Python name mangling
    # https://www.python.org/dev/peps/pep-0008/#method-names-and-instance-variables
    # https://www.python.org/dev/peps/pep-0008/#designing-for-inheritance
    # name mangling is important to not get stuff mixed up between objects when
    # inheritance happens
    __instance = None

    def __init__(self, *args, **kwargs):
        with threading.Lock():
            if self.__instance is None:
                self.__instance = super().__init__(*args, **kwargs)
            return self.__instance


class CallableStartMetaclass(type):
    """
    Metaclass to check if a start() method is implemented
    """
    def __instancecheck__(self, instance):
        """
        Check whether the thing passed in as the instance is considered to be an instanceof self

        We use this to ensure a callable start() method is defined by
        returning True if instance implements such a method anywhere in its
        MRO and False otherwise. If instance does implement a callable start(),
        whether it is through being a subclass of threading.Thread, or
        just a "regularly" defined start() method, then the instance
        is considered an instance of GenericItem.
        """
        if not isinstance(instance, type):
            for parent in instance.__class__.mro():
                for attr in parent.__dict__:
                    if attr == 'start' and callable(parent.__dict__[attr]):
                        return True

        return False
