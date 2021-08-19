from appyx.layers.application.exception_handler import AddExceptionToResult


class Application:
    """
    Models an application.
    It holds resources and interactions that allow the logic and business rule to operate.

    An application defines external resources, how to handle the exceptions those might rise for each interaction.
    In the future it may hold workflows, which in turn would hold interactions.
    Interactions should obtain the resources they need from this object. Maybe passing them onto the domain.
    """

    def __init__(self, exception_handler=None) -> None:
        super().__init__()
        self._general_exception_handler = exception_handler or self._default_exception_handler()

    def general_exception_handler(self):
        return self._general_exception_handler

    def set_general_exception_handler(self, exception_handler):
        self._general_exception_handler = exception_handler

    def _default_exception_handler(self):
        return AddExceptionToResult()
