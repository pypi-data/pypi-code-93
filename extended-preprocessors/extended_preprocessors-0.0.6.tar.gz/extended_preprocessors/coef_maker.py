from typing import List, Union
import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin


class CoefficientMaker(TransformerMixin):
    def __init__(
        self, columns_to_use: List,
    ):

        self.columns_to_use = columns_to_use
        self.n_columns = len(columns_to_use)

    def fit(
        self, X: pd.DataFrame, y: Union[pd.Series, np.ndarray] = None, *args, **kwargs
    ):
        return self

    def transform(self, X, y=None, **kwargs):
        tmp = X.copy()
        cnames_generated = []
        for i in range(self.n_columns - 1):
            for j in range(i + 1, self.n_columns):
                c1 = self.columns_to_use[i]
                c2 = self.columns_to_use[j]
                cname = f"{c1}_div_{c2}"
                tmp[cname] = X[c1].fillna(1) / X[c2].fillna(1).map(
                    lambda x: 1 if x == 0 else x
                )
                cnames_generated.append(cname)
        return tmp
