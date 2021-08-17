from sensiml.method_calls.basemethodcall import BaseMethodCall


class OptimizerCall(BaseMethodCall):
    """The base class for an optimizer call.

    Child classes have their own additional properties and overwrite this docstring."""

    def __init__(self, name, function_type="optimizer"):
        super(OptimizerCall, self).__init__(name=name, function_type=function_type)
        self._refinement = {}
