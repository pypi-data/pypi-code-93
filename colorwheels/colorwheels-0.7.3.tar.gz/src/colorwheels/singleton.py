# singleton.py

"""Definition of a Singleton Meta-class. A class which attaches this metaclass
starts behaving as a singleton instance.

Borrowed from: https://stackoverflow.com/questions/6760685/creating-a-singleton-in-python
"""

#using in Python 2
# class MyClass(BaseClass):
#     __metaclass__ = Singleton

#using in Python 3
# class MyClass(BaseClass, metaclass=Singleton):
#     pass

class Singleton(type):
    """Singleton metaclass"""

    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
