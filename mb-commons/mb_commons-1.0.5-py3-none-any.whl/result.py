from __future__ import annotations

from typing import Any, Generic, Optional, TypeVar, cast

T = TypeVar("T")


class Result(Generic[T]):
    def __init__(self, ok: Optional[T] = None, error: Optional[str] = None, data: Optional[Any] = None) -> None:
        self._ok = ok
        self._error = error
        self._data = data

    def is_ok(self):
        return self._error is None

    def is_error(self):
        return self._error is not None

    def dict(self) -> dict:
        return {"ok": self.ok, "error": self._error, "data": self.data}

    @property
    def ok(self) -> T:
        return cast(T, self._ok)  # type:ignore

    @ok.setter
    def ok(self, ok: T) -> None:
        self._ok = ok

    @property
    def error(self) -> str:
        return cast(str, self._error)

    @error.setter
    def error(self, error: str) -> None:
        self._error = error

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, data: Any) -> None:
        self._data = data

    @property
    def ok_or_error(self):
        return self.ok if self._error is None else self._error

    def new_ok(self, new_value: Any) -> Result:
        return Result(ok=new_value, data=self._data)

    def new_error(self, new_error: str) -> Result:
        return Result(error=new_error, data=self._data)

    def __str__(self):
        return str(self.dict())
