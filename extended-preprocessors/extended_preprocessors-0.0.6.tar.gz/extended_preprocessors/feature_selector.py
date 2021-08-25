from typing import Union

import numpy as np
import pandas as pd
from sklearn.base import TransformerMixin


class FeatureSelector(TransformerMixin):
    def __init__(self, features_list, return_dataframe=True):
        self.features_list = list(features_list)
        self.return_dataframe = return_dataframe

    def transform(
        self, X: pd.DataFrame, y: Union[pd.Series, np.ndarray] = None
    ) -> pd.DataFrame:
        result = X[self.features_list].copy()
        return result if self.return_dataframe else result.values

    def fit(
        self, X: pd.DataFrame, y: Union[pd.Series, np.ndarray] = None, *args, **kwargs
    ):
        return self

    def fit_transform(self, X, y=None, **fit_params):
        self.fit(X, y, **fit_params)
        return self.transform(X)
