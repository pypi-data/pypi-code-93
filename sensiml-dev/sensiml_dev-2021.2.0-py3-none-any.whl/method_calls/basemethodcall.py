class BaseMethodCall(object):
    """The base class for calls to functions.
    Child classes have their own additional properties and overwrite this docstring.
    """

    def __init__(self, name="", function_type=""):
        self._name = name
        self._type = function_type

    def _public_properties(self):
        """Returns the object's public properties, i.e. those that do not start with _"""
        return (name for name in dir(self) if not name.startswith("_"))

    def _to_dict(self):
        prop_dict = {}
        prop_dict["inputs"] = {}
        for prop in self._public_properties():
            if getattr(self, prop) is not None:
                prop_dict["inputs"][prop] = getattr(self, prop)
        prop_dict["name"] = self._name
        return prop_dict
