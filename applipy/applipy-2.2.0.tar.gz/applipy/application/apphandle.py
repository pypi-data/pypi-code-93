from typing import (
    Callable,
    Union,
    Type,
)


class AppHandle:

    async def on_init(self) -> None:
        pass

    async def on_start(self) -> None:
        pass

    async def on_shutdown(self) -> None:
        pass


AppHandleProvider = Union[Type[AppHandle], Callable[..., AppHandle]]
RegisterFunction = Callable[[AppHandleProvider], None]
