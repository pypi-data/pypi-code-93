class Printable:
    def __str__(self) -> str:
        return f"{self.__class__.__name__}<{self.__dict__}>"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}<{self.__dict__!r}>"
