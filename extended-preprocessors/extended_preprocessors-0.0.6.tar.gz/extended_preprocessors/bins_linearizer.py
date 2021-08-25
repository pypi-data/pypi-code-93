import numpy as np
from scipy import stats, optimize
from sklearn.base import TransformerMixin


class BinsLinearizer(TransformerMixin):
    def __init__(self):
        self.lmbda = 0

    def _get_lmbda(self, X: np.ndarray, y: np.ndarray):
        minimization_func = lambda l: -abs(stats.pearsonr(stats.yeojohnson(X, l), y)[0])

        try:
            res = optimize.minimize(
                minimization_func, x0=np.array([self.lmbda]), method="Nelder-Mead"
            )
        except:
            res = optimize.minimize(
                minimization_func, x0=np.array([self.lmbda]), method="BFGS"
            )

        return res["x"][0]

    def fit(self, X: np.ndarray, y: np.ndarray):
        self.lmbda = self._get_lmbda(X.flatten(), y)

        return self

    def transform(self, X: np.ndarray) -> np.ndarray:
        return stats.yeojohnson(X.flatten(), self.lmbda)
