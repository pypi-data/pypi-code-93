from __future__ import annotations
from typing import TYPE_CHECKING, Any, Callable, Iterable, List, Union
from unittest.mock import MagicMock, Mock

if TYPE_CHECKING:
    from .base_wrapper import MockWrapper
    from .cacheable_meta_type import CacheableType

OnWriteCallback = Callable[[str, Any], None]


class ListMockIterator:
    def __init__(self, it):
        self.it = it

    def __next__(self):
        return next(self.it).mock


class ListMock(list):
    def __init__(
        self,
        *,
        real_list: List[MockWrapper],
        items_type: CacheableType,
        on_write_callback: OnWriteCallback = None
    ) -> None:
        self.real_list = real_list
        self.items_type = items_type
        self.mock = MagicMock()
        self.on_write_callback = (
            on_write_callback if on_write_callback else lambda *x, **y: None
        )
        self.setup_mock()

    def setup_mock(self):
        def __iter___side_effect(_):
            return ListMockIterator(self.real_list.__iter__())

        self.mock.__iter__ = __iter___side_effect

        def __next___side_effect(_):
            return next(self.real_list).mock

        self.mock.__next__ = __next___side_effect

        def append_side_effect(item: Mock):
            self.real_list.append(self.items_type.get_by_mock(item))
            self.on_write_callback("append", item)

        self.mock.append = append_side_effect

        def clear_side_effect() -> None:
            self.real_list.clear()
            self.on_write_callback("clear")

        self.mock.clear = clear_side_effect

        def extend_side_effect(__iterable: Iterable[Mock]) -> None:
            self.real_list.extend(
                map(lambda m: self.items_type.get_by_mock(m), __iterable)
            )
            self.on_write_callback("extend", __iterable)

        self.mock.extend = extend_side_effect

        def pop_side_effect(__index: int = ...) -> Mock:
            wrapper = self.real_list.pop(__index)
            self.on_write_callback("pop", wrapper)
            return wrapper.mock

        self.mock.pop = pop_side_effect

        def insert_side_effect(__index: int, __object: Mock) -> None:
            self.real_list.insert(__index, self.items_type.get_by_mock(__object))
            self.on_write_callback("insert", __object)
            self.mock_holder.modified = True

        self.mock.insert = insert_side_effect

        def remove_side_effect(__value: Mock) -> None:
            self.real_list.remove(self.items_type.get_by_mock(__value))
            self.on_write_callback("remove", role=__value)

        self.mock.remove = remove_side_effect

        def reverse_side_effect() -> None:
            self.real_list.reverse()

        self.mock.reverse = reverse_side_effect

        def __len___side_effect(_) -> int:
            return self.real_list.__len__()

        self.mock.__len__ = __len___side_effect

        def __getitem___side_effect(_, item: Union[int, slice]):
            return self.real_list.__getitem__(item).mock

        self.mock.__getitem__ = __getitem___side_effect

        def __delitem___side_effect(_, i: Union[int, slice]) -> None:
            self.real_list.__delitem__(i)
            self.on_write_callback("__delitem__", i)

        self.mock.__delitem__ = __delitem___side_effect

        def __add___side_effect(self, x: List[Mock]) -> List[Mock]:
            self.real_list.__add__(
                list(map(lambda mock: self.items_type.get_by_mock(mock), x))
            )
            self.on_write_callback("__add__", x)
            return self

        self.mock.__add__ = __add___side_effect

        def __contains___side_effect(_, o: object) -> bool:
            return self.real_list.__contains__(self.items_type.get_by_mock(o))

        self.mock.__contains__ = __contains___side_effect

        def __setitem___side_effect(_, index: int, value: Mock):
            wrapper = self.items_type.get_by_mock(value)
            self.real_list[index] = wrapper
            self.on_write_callback("__setitem__", value)

        self.mock.__setitem__ = __setitem___side_effect
