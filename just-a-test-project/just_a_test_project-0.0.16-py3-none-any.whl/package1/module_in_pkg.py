def function() -> None:
    """This does not do anything"""
    ...


class MyClass:
    """Docstring for MyClass"""

    def __init__(self) -> None:
        """Dummy class with dummy init"""
        ...

    def method(self, var1: int, var2: str) -> str:
        """Docstring for method"""
        return "foo"

    def _private_method(self) -> None:
        """This is private"""
