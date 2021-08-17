from sensiml.method_calls.basemethodcall import BaseMethodCall


class ClassifierCall(BaseMethodCall):
    """The base class for a classifier call"""

    def __init__(self, name, function_type="classifier"):
        super(ClassifierCall, self).__init__(name=name, function_type=function_type)
