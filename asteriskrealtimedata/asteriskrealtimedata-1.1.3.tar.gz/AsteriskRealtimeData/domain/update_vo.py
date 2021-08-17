from abc import ABC
from typing import Any


class UpdateVo(ABC):
    _update_keys: str = ""

    def get_update_fields(self):
        updates: dict = {}
        for attribute in dir(self):
            if (
                not attribute.startswith("__")
                and not attribute.startswith("_")
                and not callable(getattr(self, attribute))
                and getattr(self, attribute) is not None
                and not attribute == self._update_keys
            ):
                updates[attribute] = getattr(self, attribute)
        return updates

    def get_key_field(self):
        update_key: dict = {}
        for attribute in dir(self):
            if attribute == self._update_keys:
                update_key[attribute] = getattr(self, attribute)
        return update_key

    def set_key_field_name(self, key_field_name: str) -> None:
        self._update_keys = key_field_name

    def set_key_field_value(self, key_field_value: Any) -> None:
        setattr(self, self._update_keys, key_field_value)
