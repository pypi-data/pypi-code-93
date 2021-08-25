from typing import Callable, TypeVar, Union

K = TypeVar('K')
T = TypeVar('T')
def Switch(arg: K, options: dict[K, Callable[[], T]], default: Callable[[], T] = lambda: None) -> Union[T, None]:
    enter = False
    for key, fn in options.items():
        if arg == key:
            return fn()
    return default()
