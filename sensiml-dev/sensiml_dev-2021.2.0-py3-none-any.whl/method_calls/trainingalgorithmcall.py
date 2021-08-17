from sensiml.method_calls.basemethodcall import BaseMethodCall


class TrainingAlgorithmCall(BaseMethodCall):
    """The base class for a training algorithm call.

    Child classes have their own additional properties and overwrite this docstring."""

    def __init__(self, name, function_type="Training Algorithm"):
        super(TrainingAlgorithmCall, self).__init__(
            name=name, function_type=function_type
        )
        self._refinement = {}
