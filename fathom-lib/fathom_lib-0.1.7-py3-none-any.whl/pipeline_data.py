from typing import Callable, Dict, Hashable, Iterable, List, Tuple

import numpy as np
import pandas as pd


class PipelineData:
    def __init__(
        self,
        data: pd.DataFrame = None,
        X_columns: List[str] = [],
        y_columns: List[str] = [],
        additional_columns: List[str] = [],
    ):
        self.data = data
        self.X_columns = X_columns
        self.y_columns = y_columns
        self.additional_columns = additional_columns

    def get_X_data(self):
        if self.X_columns == []:
            return self.data
        else:
            return self.data[self.X_columns]

    def get_new_X_data(self, new_X_columns):
        if set(new_X_columns).issubset(set(self.X_columns)):
            return self.data[new_X_columns]
        else:
            raise Exception(
                "Requested columns "
                + str(new_X_columns)
                + " are not a subset of "
                + str(self.X_columns)
                + " !"
            )

    def get_y_data(self):
        return self.data[self.y_columns]

    def get_additional_column(self, additional_column):
        if additional_column in self.additional_columns:
            return self.data[additional_column]
        else:
            raise Exception("Requested column is not in additional_columns field!")
