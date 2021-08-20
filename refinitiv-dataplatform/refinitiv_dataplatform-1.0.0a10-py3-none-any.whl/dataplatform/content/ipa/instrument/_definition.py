# coding: utf8

__all__ = ["ObjectDefinition"]

import abc

from refinitiv.dataplatform.tools._common import is_all_same_type


class ObjectDefinition(abc.ABC):
    """
    This class is designed to represent the instrument definition templates for QPS request.
    """

    @classmethod
    def from_json(cls, json_params):
        o = ObjectDefinition()
        for key, value in json_params.items():
            o._set_parameter(key, value)
        return o

    def __init__(self):
        self._definition = {}

    def __eq__(self, other):
        if hasattr(other, "_definition"):
            return self._definition == other._definition
        return False

    def get_json(self):
        return self._definition

    ####################################################
    # Get parameter values
    ####################################################
    def _get_parameter(self, name):
        return self._definition.get(name, None)

    def _get_enum_parameter(self, enum_type, name):
        value = self._definition.get(name, None)
        return enum_type(value) if value is not None else None

    def _get_object_parameter(self, object_type, name):
        value = self._definition.get(name, None)
        return object_type.from_json(value) if value is not None else None

    def _get_list_parameter(self, item_type, name):
        value = self._definition.get(name, None)
        return (
            [
                item_type.from_json(item) if hasattr(item_type, "from_json") else item
                for item in value
            ]
            if value is not None
            else None
        )

    ####################################################
    # Set parameter values
    ####################################################

    def _set_parameter(self, name, value):
        if value:
            self._definition[name] = value
        elif self._definition.get(name):
            self._definition.pop(name)

    def _set_enum_parameter(self, enum_type, name, value):
        if value is None:
            if self._definition.get(name):
                self._definition.pop(name)
        elif isinstance(value, enum_type):
            self._definition[name] = value.value
        elif value in [v.value for v in enum_type]:
            self._definition[name] = value
        else:
            raise TypeError(
                f"{name} : {value}, must be in {enum_type}{[v.value for v in enum_type]}"
            )

    def _set_object_parameter(self, object_type, name, value):
        if value is None:
            if self._definition.get(name):
                self._definition.pop(name)
        elif isinstance(value, object_type):
            self._definition[name] = value.get_json()
        else:
            self._definition[name] = value

    def _set_list_parameter(self, item_type, name, value):
        if value is None:
            if self._definition.get(name):
                self._definition.pop(name)
        elif isinstance(value, list):
            if is_all_same_type(item_type, value):
                self._definition[name] = [
                    item.get_json() if hasattr(item, "get_json") else item
                    for item in value
                ]
            else:
                raise TypeError(f"Not all values are type of {item_type}")
        else:
            raise TypeError(f"{name} value must be a list of {item_type}")
