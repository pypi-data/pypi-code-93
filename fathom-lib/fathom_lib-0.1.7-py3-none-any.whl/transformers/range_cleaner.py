import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class RangeCleaner(BaseEstimator, TransformerMixin):
    """
    Clips the values

    Parameters
    ----------
    min_value: float
        Minimum value that will be clipped
    max_value: float
        Maximum value that will be clipped
    """

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def fit(self, X, y=None):
        return self

    def transform(self, X: np.array):
        if self.min_value is None and self.max_value is None:
            return X
        else:
            return X.clip(self.min_value, self.max_value)
