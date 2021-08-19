import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.exceptions import NotFittedError
import xgboost

from fathom_lib.utils import ClassAsNameMixin
from fathom_lib.metrics.aft_concordance_index import AftConcordanceIndex


class XGBoostAFT(BaseEstimator, ClassAsNameMixin):
    """
    Inspired by https://github.com/dmlc/xgboost/blob/master/python-package/xgboost/sklearn.py
    To implement complete sklearn wrapper understand the wrapper from above link first.

    Description of parameters: https://xgboost.readthedocs.io/en/latest/parameter.html

    Parameters
    ----------
    aft_loss_distribution: string

    aft_loss_distribution_scale: float

    tree_method: string

    learning_rate: float

    max_depth: int

    num_boost_round: int

    n_jobs: int
    """

    def __init__(
        self,
        aft_loss_distribution="normal",
        aft_loss_distribution_scale=1.20,
        tree_method="hist",
        learning_rate=0.05,
        max_depth=2,
        num_boost_round=100,
        n_jobs=None,
    ):
        self.aft_loss_distribution = aft_loss_distribution
        self.aft_loss_distribution_scale = aft_loss_distribution_scale
        self.tree_method = tree_method
        self.learning_rate = learning_rate
        self.max_depth = max_depth
        self.num_boost_round = num_boost_round
        self.n_jobs = n_jobs
        self.missing = np.nan
        self._model = None
        self._columns = None

    def fit(self, X: pd.DataFrame, y: pd.DataFrame):
        self._validate_y(y)
        params = self._get_model_params()
        dtrain = self._to_dmatrix(X, y)
        self._model = xgboost.train(
            params, dtrain, num_boost_round=self.num_boost_round
        )
        self._columns = X.columns.tolist()
        return self

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        if not self._model:
            raise NotFittedError
        if not isinstance(
            X, pd.DataFrame
        ):  # if X is not a dataframe then it must have proper column names to work
            X = pd.DataFrame(X, columns=self._columns)
        dm = self._to_dmatrix(X)
        prediction: np.array = self._model.predict(dm)
        return pd.DataFrame(prediction, columns=[self.name()], index=X.index)

    @staticmethod
    def _validate_y(y: pd.DataFrame):
        if not isinstance(y, pd.DataFrame):
            raise TypeError("y must be a DataFrame")
        _, ncols = y.shape
        if ncols != 2:
            raise ValueError(f"y should have 2 columns, not {ncols}")
        if y.isna().values.any():
            raise ValueError("y should not contain NaNs")
        first_col, second_col = y.iloc[:, 0], y.iloc[:, 1]
        if any(first_col > second_col):
            raise ValueError(
                "Values of the first column should be less or equal "
                "to values in the second"
            )

    def _get_model_params(self):
        return {
            "objective": "survival:aft",
            "eval_metric": "aft-nloglik",
            "aft_loss_distribution": self.aft_loss_distribution,
            "aft_loss_distribution_scale": self.aft_loss_distribution_scale,
            "tree_method": self.tree_method,
            "learning_rate": self.learning_rate,
            "max_depth": self.max_depth,
        }

    def _to_dmatrix(self, X: pd.DataFrame, y: pd.DataFrame = None) -> xgboost.DMatrix:
        dm = xgboost.DMatrix(
            data=X,
            missing=self.missing,
            nthread=self.n_jobs,
        )
        if y is not None:
            dm.set_float_info("label_lower_bound", y.iloc[:, 0])
            dm.set_float_info("label_upper_bound", y.iloc[:, 1])
        return dm

    def score(self, X_test, y_test):
        y_test_pred = self.predict(X_test)
        return AftConcordanceIndex.concordance_index(y_test, y_test_pred)
