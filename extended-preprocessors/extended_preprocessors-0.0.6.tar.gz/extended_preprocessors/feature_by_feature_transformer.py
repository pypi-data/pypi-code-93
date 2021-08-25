import numpy as np
from sklearn.base import TransformerMixin


class FeatureByFeatureTransformer(TransformerMixin):
    def __init__(self):
        self.transformers = []

    def _get_transformer(self, i: int) -> TransformerMixin:
        return TransformerMixin()

    def fit(self, X: np.ndarray, y: np.ndarray):
        for i in range(X.shape[1]):
            transformer = self._get_transformer(i)
            transformer.fit(X[:, i].reshape((-1, 1)), y)
            self.transformers.append(transformer)
        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        result = np.empty(X.shape)
        for i in range(X.shape[1]):
            transformer = self.transformers[i]
            x_tmp = X[:, i].flatten()
            tmp_res = transformer.transform(x_tmp.reshape((-1, 1)))
            result[:, i] = tmp_res
        return result
