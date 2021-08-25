from typing import (
    Callable,
    Tuple,
    Type,
    TypeVar,
)

from applipy.application.apphandle import RegisterFunction


T = TypeVar('T', covariant=True)


BindFunction = Callable[..., None]


class Module:

    def configure(self, bind: BindFunction, register: RegisterFunction) -> None:
        pass

    @classmethod
    def depends_on(cls) -> Tuple[Type['Module'], ...]:
        return ()
