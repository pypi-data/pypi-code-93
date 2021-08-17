from sensiml.method_calls.basemethodcall import BaseMethodCall


class SelectorCall(BaseMethodCall):
    """The base class for a selector call.

    Child classes have their own additional properties and overwrite this docstring."""

    def __init__(self, name, function_type="Feature Selector"):
        super(SelectorCall, self).__init__(name=name, function_type=function_type)

    def _to_dict(self):
        prop_dict = {}
        prop_dict["inputs"] = {}
        for prop in self._public_properties():
            prop_dict["inputs"][prop] = getattr(self, prop)
        prop_dict["function_name"] = self._name
        return prop_dict
