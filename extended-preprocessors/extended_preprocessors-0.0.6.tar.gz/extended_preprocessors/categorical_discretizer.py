import numpy as np
from extended_preprocessors.preprocessors.feature_discretizer import FeatureDiscretizer


class CategoricalFeatureDiscretizer(FeatureDiscretizer):
    def __init__(self, use_median: bool = False):
        max_bins = -1
        super().__init__(max_bins, use_median)
        self.max_bins = max_bins
        self.bins_map = {}
        self.use_median = use_median

    def fit(self, X, y, **fit_params) -> FeatureDiscretizer:
        assert len(X.shape) == 2
        assert X.shape[1] == 1
        bins = X
        self.bins_map = self._make_bins_map(bins, y)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        assert len(X.shape) == 2
        assert X.shape[1] == 1
        mapped_bins = np.array([self.bins_map.get(v) for v in X.flatten()])
        return mapped_bins
