#!/usr/bin/env python
import abc

import codefast as cf
import numpy as np
import pandas as pd
from codefast.logger import test
from optuna.integration import XGBoostPruningCallback
from sklearn.ensemble import VotingRegressor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import (GridSearchCV, RandomizedSearchCV,
                                     RepeatedKFold, cross_val_score,
                                     train_test_split)
from xgboost import XGBRegressor

import premium as pm
from premium.preprocess import any_cn, jb_cut

from .base import BaseModel


class BaseRegressor(metaclass=abc.ABCMeta):
    def __init__(self, X, y, test_size: float = 0.2):
        self.X = jb_cut(X) if any_cn(X) else X
        self.y = y
        self.test_size = test_size
        self.model_type = 'basemodel'
        self.model = None
        self.stop_words = []
        self.cv = None
        self.scoring = None
        self.n_iter = 100


class LR(BaseRegressor):
    def __init__(self, X, y, test_size: float = 0.2):
        super(LR, self).__init__(X, y, test_size)
        self.parameters = {}

    def build_model(self):
        self.model = LinearRegression()


class XgboostRegressor(BaseModel):
    def __init__(self, X, y, test_size: float = 0.2):
        super(XgboostRegressor, self).__init__(X, y, test_size)

    def objective(self, trial):
        param = {
            'objective': 'reg:squarederror',
            "lambda": trial.suggest_loguniform("lambda", 1e-8, 10.0), \
            "gamma": trial.suggest_loguniform("lambda", 1e-8, 10.0),\
            "min_child_weight": trial.suggest_loguniform("min_child_weight", 10, 1000), \
            'alpha': trial.suggest_loguniform('alpha', 1e-3, 10.0), \
            "subsample": trial.suggest_loguniform("subsample", 0.4, 0.8),\
            "learning_rate": trial.suggest_loguniform("learning_rate", 0.005, 0.05), \
            "colsample_bytree": trial.suggest_loguniform("colsample_bytree", 0.2, 0.8),\
            'n_estimators': 1000,
            'max_depth': trial.suggest_int('max_depth', 3, 30),\
            'random_state': trial.suggest_categorical('random_state', [24, 48, 2020]),
            'n_jobs': self.extra_parameters.get('n_jobs', 4),
            # 'tree_method': 'gpu_hist',
        }
        model = XGBRegressor(**param)
        # pruning_callback = XGBoostPruningCallback(trial, "validation_0-rmse")
        n_splits = self.extra_parameters.get('n_splits', 3)
        n_repeats = self.extra_parameters.get('n_repeats', 2)
        random_state = self.extra_parameters.get('random_state', 28947)

        rkf = RepeatedKFold(n_splits=n_splits,
                            n_repeats=n_repeats,
                            random_state=random_state)
        scores = cross_val_score(model,
                                 self.X_train,
                                 self.y_train,
                                 cv=rkf,
                                 scoring='neg_root_mean_squared_error')
        return -1 * np.mean(scores)

    def build_model(self):
        self.model = XGBRegressor(max_depth=3,
                                  min_child_weight=5,
                                  n_estimators=1000,
                                  learning_rate=0.008,
                                  subsample=0.4,
                                  booster='gbtree',
                                  colsample_bytree=0.6,
                                  reg_lambda=5,
                                  reg_alpha=32,
                                  n_jobs=13,
                                  alpha=0.5,
                                  random_state=123)
        cf.info('Model is: ', self.model)
        return self.model
