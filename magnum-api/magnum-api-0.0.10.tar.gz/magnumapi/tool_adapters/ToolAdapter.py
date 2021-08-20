from abc import ABC, abstractmethod

import pandas as pd


class ToolAdapter(ABC):

    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError('This method is not implemented for this class')

    @staticmethod
    @abstractmethod
    def convert_figures_of_merit_to_dict(fom_df: pd.DataFrame) -> dict:
        raise NotImplementedError('This method is not implemented for this class')

    @abstractmethod
    def read_figures_of_merit_table(self) -> pd.DataFrame:
        raise NotImplementedError('This method is not implemented for this class')