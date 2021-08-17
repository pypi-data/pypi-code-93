from sensiml.method_calls.basemethodcall import BaseMethodCall


class ValidationMethodCall(BaseMethodCall):
    """The base class for a validation method call.

    Child classes have their own additional properties and overwrite this docstring."""

    def __init__(self, name, function_type="Validation Method"):
        super(ValidationMethodCall, self).__init__(
            name=name, function_type=function_type
        )
