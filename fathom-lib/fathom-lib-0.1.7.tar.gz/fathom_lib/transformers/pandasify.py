from typing import Union

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from scipy.sparse import issparse


def ncols(x: Union[np.ndarray, pd.DataFrame]) -> int:
    try:
        return x.shape[1]
    except IndexError:
        return 1


class Pandasify(BaseEstimator, TransformerMixin):
    def __init__(self, model):
        self.model = model

    def __getattr__(self, item):
        return getattr(self.model, item)

    def get_model_params(self, deep=True):
        return self.model.get_params(deep)

    def fit(self, X, y=None, **fit_params):
        if y is None:  # unsupervised
            return self.model.fit(X=X, **fit_params)
        else:  # supervised
            return self.model.fit(X=X, y=y, **fit_params)

    def transform(self, X, **kwargs) -> pd.DataFrame:
        transformed = self.model.transform(X, **kwargs)
        return self._transformed_to_df(X, transformed)

    def fit_transform(self, X, y=None, **kwargs) -> pd.DataFrame:
        if y is None:
            transformed = self.model.fit_transform(X, **kwargs)
        else:
            transformed = self.model.fit_transform(X=X, y=y, **kwargs)
        return self._transformed_to_df(X, transformed)

    def predict(self, X, **kwargs) -> pd.DataFrame:
        return self._predict(X=X, method="predict", **kwargs)

    def predict_proba(self, X, **kwargs) -> pd.DataFrame:
        return self._predict(X=X, method="predict_proba", **kwargs)

    def predict_log_proba(self, X, **kwargs) -> pd.DataFrame:
        return self._predict(X=X, method="predict_log_proba", **kwargs)

    def _predict(self, X, method, **kwargs) -> pd.DataFrame:
        compute_func = getattr(self.model, method)
        y = compute_func(X, **kwargs)
        name = f"{self._get_model_name()}.{method}"
        if ncols(y) == 1:
            columns = [name]
            y = np.array(y)
        else:
            columns = [f"{name}_{cls}" for cls in self.model.classes_]
            y = np.array(
                y[:, : len(self.model.classes_)]
            )  # XGBClassifier return 2 columns, even though there was 1 class
        return pd.DataFrame(y, columns=columns)

    def _transformed_to_df(
        self, X: pd.DataFrame, transformed: Union[pd.DataFrame, np.ndarray]
    ) -> pd.DataFrame:
        if isinstance(transformed, pd.DataFrame):
            return transformed
        try:
            feature_names = self.model.get_feature_names(input_features=X.columns)
        except TypeError:  # no input_features argument
            feature_names = self.model.get_feature_names()
            # will this ever be used? Such signature is only for vectorizers atm
        except AttributeError:  # no get_feature_names method
            if transformed.shape[1] == X.shape[1]:
                feature_names = [
                    f"{self._get_model_name()}({col})" for col in X.columns
                ]
            else:
                cols = ", ".join(X.columns)
                feature_names = [
                    f"{self._get_model_name()}({cols})_{i}"
                    for i in range(transformed.shape[1])
                ]
        if issparse(transformed):
            return pd.DataFrame.sparse.from_spmatrix(transformed, columns=feature_names)
        else:
            return pd.DataFrame(transformed, columns=feature_names)

    def _get_model_name(self):
        return self.model.__class__.__name__
