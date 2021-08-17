from sensiml.method_calls.basemethodcall import BaseMethodCall


class GeneratorCall(BaseMethodCall):
    """The base class for a generator call.

    Child classes have their own additional properties and overwrite this docstring."""

    def __init__(self, name, function_type="Feature Generator"):
        super(GeneratorCall, self).__init__(name=name, function_type=function_type)

    def _to_dict(self):
        prop_dict = {}
        if not hasattr(self, "_subtype"):
            prop_dict["function_name"] = self._name
        else:
            prop_dict["subtype"] = self._subtype

        prop_dict["inputs"] = {}
        for prop in self._public_properties():
            prop_dict["inputs"][prop] = getattr(self, prop)
        return prop_dict
