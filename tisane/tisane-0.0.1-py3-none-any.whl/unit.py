from tisane.data import Dataset, DataVector

import pandas as pd
from enum import Enum
from typing import Any, List
import typing  # for typing.Unit

class Unit(AbstractVariable):
    def __init__(self, name: str):
        super(Unit, self).__init__(name)

    # def nominal(self, name: str, cardinality=None,exactly: int = 0, up_to: int = None):
    #     return Nominal(unit=self, name=name, cardinality=cardinality, exactly=exactly, up_to=up_to)

    def has(self, measure: AbstractVariable, exactly: int = 0, up_to: int = None):
        repet = 0
        if exactly == 0:
            assert up_to is not None
            repet = up_to
        else:  # exactly!=0
            assert up_to is None
            repet = exactly

        has_relat = Has(variable=self, measure=measure, repetitions=repet)
        self.relationships.append(has_relat)
        measure.relationships.append(has_relat)