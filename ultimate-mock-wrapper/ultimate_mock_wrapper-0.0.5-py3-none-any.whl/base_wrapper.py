from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Union
from unittest.mock import PropertyMock

if TYPE_CHECKING:
    from unittest.mock import Mock

from .cacheable_meta_type import CacheableType


class IdMixin:
    __id_property: PropertyMock
    __id: Union[int, str]

    def __init__(self: MockWrapper, model_id: Union[int, str] = None):
        def side_effect(id_: Optional[int] = None) -> Union[int, str, None]:
            if id_ is None:
                return self.id
            else:
                self.id = id_
                self.modified = True

        self.__id_property = PropertyMock(side_effect=side_effect)
        self._set_id_property_on_mock()
        self.__id = model_id if model_id else self.__class__.get_next_id()
        self.__id_property.return_value = model_id

    def _set_id_property_on_mock(self: MockWrapper) -> None:
        type(self._mock).id = self.__id_property

    def set_id(self: MockWrapper, new_id: Union[int, str]) -> MockWrapper:
        old_id = self.__id
        self.__id = new_id
        if old_id is None:
            self.__class__.add_instance(self)
        else:
            self.__class__.change_id(old_id, new_id)
        self.__id_property.return_value = new_id
        return self

    @property
    def id(self: MockWrapper) -> Union[int, str]:
        return self.__id

    @id.setter
    def id(self: MockWrapper, id: Union[int, str]) -> None:
        self.set_id(id)

    @property
    def id_property_mock(self: MockWrapper) -> PropertyMock:
        return self.__id_property


class MockWrapper(IdMixin, metaclass=CacheableType):
    _mock: Mock
    _modified: bool

    def __init__(self, mock: Mock, id: Union[int, str] = None):
        self._mock = mock
        IdMixin.__init__(self, model_id=id)
        self._modified = False

    @property
    def modified(self):
        return self._modified

    @modified.setter
    def modified(self, new_value: bool):
        self._modified = new_value

    @property
    def mock(self) -> Mock:
        return self._mock

    def __getattr__(self, item):
        return getattr(self._mock, item)
