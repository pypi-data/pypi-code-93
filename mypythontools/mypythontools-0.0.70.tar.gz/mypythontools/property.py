"""Module contains MyProperty class that edit normal python property to add new features.

There is default setter, it's possible to auto init values on class init and values in setter can be
validated.

It's possible to set function as a value and it's evaluated during call.

Example of how can it be used is in module config.

Examples:
=========

    >>> class MyClass:
    ...     # Init all default values of defined properties
    ...     def __init__(self):
    ...        for j in vars(type(self)).values():
    ...            if type(j) is MyProperty:
    ...                setattr(self, j.private_name, j.init_function)
    ...
    ...     @MyProperty(int)  # New value will be validated whether it's int
    ...     def var() -> int:  # This is for type hints in IDE.
    ...         '''
    ...         Type:
    ...             int
    ...
    ...         Default:
    ...             123
    ...
    ...         This is docstrings (also visible in IDE, because not defined dynamically).'''
    ...
    ...         return 123  # This is initial value that can be edited.
    ...
    ...     @MyProperty()  # Even if you don't need any params, use empty brackets
    ...     def var2():
    ...         return 111
    ...
    >>> myobject = MyClass()
    >>> myobject.var
    123
    >>> myobject.var = 124
    >>> myobject.var
    124
"""

import types as types_lib
from .misc import validate

import mylogging


class MyProperty(property):
    """Python property on steroids. Check module docstrings for more info."""

    def __init__(self, types=None, options=None, fget=None, fset=None, doc=None):

        if isinstance(types, types_lib.FunctionType):
            raise SyntaxError(
                mylogging.return_str("@MyProperty decorator has to be called (parentheses at the end).")
            )
        self.fget_new = fget if fget else self.default_fget
        self.fset_new = fset if fset else self.default_fset
        self.__doc__ = doc
        self.types = types
        self.options = options

    def __call__(self, init_function):
        self.init_function = init_function
        self.__doc__ = init_function.__doc__

        return self

    def default_fget(self, object):
        return getattr(object, self.private_name)

    def default_fset(self, object, content):
        setattr(object, self.private_name, content)

    def __set_name__(self, _, name):
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, object, objtype=None):
        # If getting MyProperty class, not object, return MyProperty itself
        if not object:
            return self

        # Expected value can be nominal value or function, that return that value
        content = self.fget_new(object)
        if callable(content):
            if not len(content.__code__.co_varnames):
                value = content()
            else:
                value = content(object)
        else:
            value = content

        return value

    def __set__(self, object, content):

        # You can setup value or function, that return that value
        if callable(content):
            result = content(object)
        else:
            result = content

        validate(result, self.types, self.options, self.public_name)

        # Method defined can be pass as static method
        try:
            self.fset_new(object, content)
        except TypeError:
            self.fset_new(self, object, content)
