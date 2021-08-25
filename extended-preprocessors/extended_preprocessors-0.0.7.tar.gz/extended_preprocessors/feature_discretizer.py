import numpy as np
from sklearn.base import TransformerMixin


class FeatureDiscretizer(TransformerMixin):
    def __init__(self, max_bins: int, use_median: bool = False):
        self.max_bins = max_bins
        self.bins_map = {}
        self.use_median = use_median

    def transform(self, X):
        pass

    def fit(self, X, y, **fit_params):
        pass

    def fit_transform(self, X, y=None, **fit_params):
        self.fit(X, y)
        return self.transform(X)

    def _define_n_bins(self, X: np.ndarray) -> int:
        unique_values = np.unique(X).shape[0]
        return min(self.max_bins, unique_values)

    def _make_bins_map(self, bins: np.ndarray, y: np.ndarray) -> dict:
        unique_bins = np.unique(bins)
        means = []
        for bin_value in unique_bins:
            if self.use_median:
                means.append((bin_value, np.median(y[bins.flatten() == bin_value])))
            else:
                means.append((bin_value, y[bins.flatten() == bin_value].mean()))
        means = sorted(means, key=lambda x: x[1])
        result = {
            m[0]: i + 1 for i, m in enumerate(means)
        }  # +1 to make mapped bin number always be > 0
        return result
