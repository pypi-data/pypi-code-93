from __future__ import annotations
from typing import TYPE_CHECKING, Dict, List, Union, Tuple

if TYPE_CHECKING:
    from unittest.mock import Mock
    from .base_wrapper import MockWrapper


class CacheableType(type):
    __created_classes: List[CacheableType] = []
    __next_id: Union[int, str]
    __all_instances_by_id: Dict[Union[int, str], MockWrapper]
    __all_instances_by_name: Dict[str, MockWrapper]
    __all_instances_by_mock: Dict[Mock, MockWrapper]

    @classmethod
    def clear_all_cache(mcs) -> None:
        for clazz in mcs.__created_classes:
            clazz.clear_cache()

    def clear_cache(cls) -> None:
        cls.__next_id = 1
        cls.__all_instances_by_id.clear()
        cls.__all_instances_by_name.clear()
        cls.__all_instances_by_mock.clear()

    def add_instance(cls, instance: MockWrapper) -> None:
        if not (hasattr(instance, "id") and isinstance(instance.id, int)):
            instance.id = cls.get_next_id()
        cls.__all_instances_by_id.setdefault(instance.id, instance)
        cls.__next_id = cls._calc_next_id(instance)
        if hasattr(instance, "name"):
            cls.__all_instances_by_name.setdefault(instance.name, instance)
        if hasattr(instance, "mock"):
            cls.__all_instances_by_mock.setdefault(instance.mock, instance)

    def all_instances(cls) -> List[MockWrapper]:
        return list(cls.__all_instances_by_mock.values())

    def get_by_name(cls, name: str) -> Union[MockWrapper, None]:
        return cls.__all_instances_by_name.get(name, None)

    def get_by_id(cls, id_: Union[int, str]) -> Union[MockWrapper, None]:
        return cls.__all_instances_by_id.get(id_, None)

    def get_by_mock(cls, mock: Mock) -> Union[MockWrapper, None]:
        return cls.__all_instances_by_mock.get(mock, None)

    def change_id(cls, old_id: Union[int, str], new_id: Union[int, str]) -> None:
        if not cls.is_id_exist(new_id):
            cls.__all_instances_by_id[new_id] = cls.__all_instances_by_id.pop(old_id)

    def is_id_exist(cls, id_: Union[int, str]) -> bool:
        return id_ in cls.__all_instances_by_id

    def get_next_id(cls) -> Union[int, str]:
        return cls.__next_id

    def _calc_next_id(self, instance: MockWrapper) -> Union[int, str]:
        next_int_id: int = int(instance.id) + 1
        return next_int_id if (type(instance.id) is int) else ""

    def __init__(cls, *args: Tuple[str, ...], **kwargs: Dict[str, int]) -> None:
        CacheableType.__created_classes.append(cls)
        super(CacheableType, cls).__init__(*args, **kwargs)
        cls.__all_instances_by_id = {}
        cls.__all_instances_by_name = {}
        cls.__all_instances_by_mock = {}
        cls.__next_id = 1

    def __call__(cls, *args: Tuple[str, ...], **kwargs: Dict[str, int]) -> MockWrapper:
        instance = super().__call__(*args, **kwargs)
        cls.add_instance(instance)
        return instance
