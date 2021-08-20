import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.exceptions import NotFittedError
import autokeras as ak

from fathom_lib.utils import ClassAsNameMixin
from fathom_lib.metrics.aft_concordance_index import AftConcordanceIndex


class AutoKerasClassifier(BaseEstimator, ClassAsNameMixin):
    """
    Sklearn wrapper for https://autokeras.com/structured_data_classifier/

    Check the mentioned link for a description of the parameters.

    Parameters
    ----------
    column_names:

    column_types:

    num_classes: int

    multi_label: bool

    loss: string

    metrics: string

    project_name: string

    max_trials: int

    directory: string

    objective: string

    tuner:

    overwrite: bool

    seed: float
    """

    def __init__(
        self,
        column_names=None,
        column_types=None,
        num_classes=None,
        multi_label=False,
        loss=None,
        metrics=None,
        project_name="structured_data_classifier",
        max_trials=100,
        directory=None,
        objective="val_accuracy",
        tuner=None,
        overwrite=False,
        seed=None,
    ):
        self.column_names = column_names
        self.column_types = column_types
        self.num_classes = num_classes
        self.multi_label = multi_label
        self.loss = loss
        self.metrics = metrics
        self.project_name = project_name
        self.max_trials = max_trials
        self.directory = directory
        self.objective = objective
        self.tuner = tuner
        self.overwrite = overwrite
        self.seed = seed
        self._fitted = False

    def fit(self, X: pd.DataFrame, y: pd.DataFrame, **kwargs):
        self._model = ak.StructuredDataClassifier(
            self.column_names,
            self.column_types,
            self.num_classes,
            self.multi_label,
            self.loss,
            self.metrics,
            self.project_name,
            self.max_trials,
            self.directory,
            self.objective,
            self.tuner,
            self.overwrite,
            self.seed,
        )
        self._columns = X.columns.tolist()
        self._model.fit(x=X, y=y, **kwargs)
        self._fitted = True
        return self

    def predict(self, X: pd.DataFrame, batch_size=32, **kwargs) -> pd.DataFrame:
        return self._predict(X, batch_size, method="predict", **kwargs)

    def predict_proba(self, X: pd.DataFrame, batch_size=32, **kwargs) -> pd.DataFrame:
        return self._predict(X, batch_size, method="predict_proba", **kwargs)

    def _predict(self, X: pd.DataFrame, batch_size, method, **kwargs) -> pd.DataFrame:
        if not self._fitted:
            raise NotFittedError
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=self._columns)
        if method == "predict_proba":
            prediction: np.array = self._model.predict(X, batch_size, **kwargs)
        elif method == "predict":
            if self.multi_label == False:
                prediction: np.array = (
                    self._model.predict(X, batch_size, **kwargs) >= 0.5
                ).astype(int)
            else:
                prediction: np.array = np.argmax(
                    self._model.predict(X, batch_size, **kwargs), axis=1
                )
        return pd.DataFrame(prediction, columns=[self.name()], index=X.index)

    def score(self, X_test, y_test):
        return self._model.evaluate(X_test, y_test)[1]


class AutoKerasRegressor(BaseEstimator, ClassAsNameMixin):
    """
    Sklearn wrapper for https://autokeras.com/structured_data_regressor/

    Check the mentioned link for a description of the parameters.

    Parameters
    ----------
    column_names:

    column_types:

    output_dim: int

    loss: string

    metrics: string

    project_name: string

    max_trials: int

    directory: string

    objective: string

    tuner:

    overwrite: bool

    seed: float
    """

    def __init__(
        self,
        column_names=None,
        column_types=None,
        output_dim=None,
        loss="mean_squared_error",
        metrics=None,
        project_name="structured_data_regressor",
        max_trials=100,
        directory=None,
        objective="val_loss",
        tuner=None,
        overwrite=False,
        seed=None,
    ):
        self.column_names = column_names
        self.column_types = column_types
        self.output_dim = output_dim
        self.loss = loss
        self.metrics = metrics
        self.project_name = project_name
        self.max_trials = max_trials
        self.directory = directory
        self.objective = objective
        self.tuner = tuner
        self.overwrite = overwrite
        self.seed = seed
        self._fitted = False

    def fit(self, X: pd.DataFrame, y: pd.DataFrame, **kwargs):
        self._model = ak.StructuredDataRegressor(
            self.column_names,
            self.column_types,
            self.output_dim,
            self.loss,
            self.metrics,
            self.project_name,
            self.max_trials,
            self.directory,
            self.objective,
            self.tuner,
            self.overwrite,
            self.seed,
        )
        self._columns = X.columns.tolist()
        self._model.fit(x=X, y=y, **kwargs)
        self._fitted = True
        return self

    def predict(self, X: pd.DataFrame, batch_size=32, **kwargs) -> pd.DataFrame:
        if not self._fitted:
            raise NotFittedError
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=self._columns)
        prediction: np.array = self._model.predict(X, batch_size, **kwargs)
        return pd.DataFrame(prediction, columns=[self.name()], index=X.index)

    def score(self, X_test, y_test):
        return self._model.evaluate(X_test, y_test)[1]
