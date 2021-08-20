"""
This module contains reference models that can be used for comparison with feyn models.
"""
from abc import ABCMeta, abstractmethod
import numpy as np
import typing

from .._base_reporting_mixin import BaseReportingMixin

class BaseReferenceModel(BaseReportingMixin, metaclass=ABCMeta):
    @abstractmethod
    def predict(self, X: typing.Iterable):
        raise NotImplementedError()


class ConstantModel(BaseReferenceModel):
    def __init__(self, target, const):
        self.const = const
        self.target = target

    def predict(self, data: typing.Iterable):
        return np.full(len(data), self.const)


class SKLearnClassifier(BaseReferenceModel):
    def __init__(self, sklearn_classifier:type, data, target, **kwargs):
        self.features = list(data.columns)
        if target in self.features:
            self.features.remove(target)

        self.target = target

        self._model = sklearn_classifier(**kwargs)
        self._model.fit(X=data[self.features], y=data[self.target])

    def predict(self, X: typing.Iterable):
        if type(X).__name__ == "DataFrame":
            X = X[self.features].values

        elif type(X).__name__ == "dict":
            X = np.array([X[col] for col in self.features]).T

        pred = self._model.predict_proba(X)[:, 1]
        return pred


class LogisticRegressionClassifier(SKLearnClassifier):
    def __init__(self, data, target, **kwargs):
        import sklearn.linear_model
        if "penalty" not in kwargs:
            kwargs["penalty"]="none"
        super().__init__(sklearn.linear_model.LogisticRegression, data, target, **kwargs)

    def summary(self, ax=None):
        import pandas as pd
        return pd.DataFrame(data={"coeff": self._model.coef_[0]}, index=self.features)


class RandomForestClassifier(SKLearnClassifier):
    def __init__(self, data, target, **kwargs):
        import sklearn.ensemble
        super().__init__(sklearn.ensemble.RandomForestClassifier, data, target, **kwargs)


class GradientBoostingClassifier(SKLearnClassifier):
    def __init__(self, data, target, **kwargs):
        import sklearn.ensemble
        super().__init__(sklearn.ensemble.GradientBoostingClassifier, data, target, **kwargs)



class SKLearnRegressor(BaseReferenceModel):
    def __init__(self, sklearn_regressor:type, data, target, **kwargs):
        self.features = list(data.columns)
        if target in self.features:
            self.features.remove(target)

        self.target = target

        self._model = sklearn_regressor(**kwargs)
        self._model.fit(X=data[self.features], y=data[self.target])

    def predict(self, X: typing.Iterable):
        if type(X).__name__ == "DataFrame":
            X = X[self.features].values

        elif type(X).__name__ == "dict":
            X = np.array([X[col] for col in self.features]).T

        pred = self._model.predict(X)
        return pred


class LinearRegression(SKLearnRegressor):
    def __init__(self, data, target, **kwargs):
        import sklearn.linear_model
        super().__init__(sklearn.linear_model.LinearRegression, data, target, **kwargs)
