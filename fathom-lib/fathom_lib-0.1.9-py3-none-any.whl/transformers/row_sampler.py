import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class RowModifier:
    pass


class RowSampler(RowModifier, BaseEstimator, TransformerMixin):
    """
    Samples data.

    Parameters
    ----------
    amount: float
        Amount of data that will be sampled.
    """

    def __init__(self, amount=0.8):
        self.amount = amount

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        sampled_X = X.sample(frac=self.amount, axis=0)
        if sampled_X.shape[0] == 0:  # Returns always at least one element
            sampled_X = X.sample(n=1, axis=0)
        return sampled_X
