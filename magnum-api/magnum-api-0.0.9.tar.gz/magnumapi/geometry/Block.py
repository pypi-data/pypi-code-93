from abc import ABC, abstractmethod

import pandas as pd

from magnumapi.geometry.roxie.CableDefinition import CableDefinition
from magnumapi.geometry.roxie.ConductorDefinition import ConductorDefinition
from magnumapi.geometry.roxie.InsulationDefinition import InsulationDefinition
from magnumapi.geometry.roxie.StrandDefinition import StrandDefinition


class Block(ABC):

    def __init__(self,
                 cable_def: CableDefinition,
                 insul_def: InsulationDefinition,
                 strand_def: StrandDefinition,
                 conductor_def: ConductorDefinition):
        self.cable_def = cable_def
        self.insul_def = insul_def
        self.strand_def = strand_def
        self.conductor_def = conductor_def
        self.areas = []

    @abstractmethod
    def plot_block(self, ax):
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def build_block(self):
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def to_roxie_df(self):
        raise NotImplementedError('This method is not implemented for this class')

    def to_df(self):
        return pd.concat([area.to_df() for area in self.areas], axis=0)
