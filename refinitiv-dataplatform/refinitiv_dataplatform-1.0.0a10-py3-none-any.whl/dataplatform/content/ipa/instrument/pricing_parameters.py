# coding: utf8


__all__ = ["InstrumentCalculationParams"]

import abc
from ._definition import ObjectDefinition


class InstrumentCalculationParams(ObjectDefinition, abc.ABC):
    class Params(abc.ABC):
        def __init__(self):
            self._pricing_parameters = {}

        def _with_key_parameter(self, key_name, value):
            if value:
                self._pricing_parameters[key_name] = value
            elif self._pricing_parameters.get(key_name):
                self._pricing_parameters.pop(key_name)

        @property
        def parameters(self):
            return self._pricing_parameters

    def __init__(self):
        super().__init__()
