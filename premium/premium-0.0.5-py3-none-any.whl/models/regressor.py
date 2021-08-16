#!/usr/bin/env python
import abc

import codefast as cf
import numpy as np
from codefast.logger import test
from sklearn.ensemble import VotingRegressor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import (GridSearchCV, RandomizedSearchCV,
                                     train_test_split)
from xgboost import XGBRegressor

import premium as pm
from premium.preprocess import any_cn, jb_cut


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
        self.n_iter=100

    def preprocess(self):
        ...

    def build_model(self):
        ...

    def fit(self):
        self.model.fit(self.X_train, self.y_train)

    def predict(self, X_test: list) -> list:
        return self.model.predict(X_test)

    def grid_search(self):
        '''GridSearchCV the best parameters.
        Be careful about the scoring metric, the default might not be what you want.
        '''
        cf.info('Data info', len(self.X_train))
        self.grid = GridSearchCV(self.model,
                                 self.parameters,
                                 cv=2,
                                 n_jobs=15,
                                 verbose=True,
                                 scoring=self.scoring)
        self.grid.fit(self.X_train, self.y_train)
        cf.info('best parameters:', self.grid.best_params_)
        cf.info('best score:', self.grid.best_score_)

    def random_search(self):
        '''Random Grid Search
        '''
        cf.info('Data info', len(self.X_train))
        self.grid_random = RandomizedSearchCV(self.model,
                                              self.parameters,
                                              cv=2,
                                              n_jobs=13,
                                              n_iter=self.n_iter,
                                              verbose=True,
                                              scoring=self.scoring)
        self.grid_random.fit(self.X_train, self.y_train)
        cf.info('best parameters:', self.grid_random.best_params_)
        cf.info('best score:', self.grid_random.best_score_)


class LR(BaseRegressor):
    def __init__(self, X, y, test_size: float = 0.2):
        super(LR, self).__init__(X, y, test_size)
        self.parameters = {}

    def build_model(self):
        self.model = LinearRegression()


class XgboostRegressor(BaseRegressor):
    def __init__(self, X, y, test_size: float = 0.2):
        super(XgboostRegressor, self).__init__(X, y, test_size)
        self.parameters = {
            'min_child_weight': [3, 4, 5, 6],
            'gamma': [i / 10.0 for i in range(1, 11)],
            'subsample': [i / 10.0 for i in range(1, 11)],
            'colsample_bytree': [i / 10.0 for i in range(3, 11)],
            'max_depth': [2, 3, 5, 7, 11],
            'n_estimators': [500],
        }

        self.params_mini = {}

    def build_model(self):
        self.model = XGBRegressor(max_depth=3,
                                    min_child_weight=5,
                                  n_estimators=1000,
                                  learning_rate=0.008,
                                  subsample=0.4,
                                  booster='gbtree',
                                  tree_method='gpu_hist',
                                  colsample_bytree=0.6,
                                  reg_lambda=5,
                                  reg_alpha=32,
                                  n_jobs=13,
                                  alpha=0.5,
                                  random_state=123)
        return self.model
