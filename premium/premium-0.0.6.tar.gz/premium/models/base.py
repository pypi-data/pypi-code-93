#!/usr/bin/env python
import abc
from math import gamma

import codefast as cf
import joblib
import numpy as np
import optuna
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from xgboost import XGBClassifier

import premium as pm
from premium.preprocess import any_cn


class BaseModel(metaclass=abc.ABCMeta):
    def __init__(self, X, y, test_size: float = 0.2):
        self.X = pm.once.jb_cut(X) if any_cn(X) else X
        self.y = y
        self.X_train = None
        self.y_train = None
        self.test_size = test_size
        self.model_type = 'basemodel'
        self.stop_words = []
        self.countervectorize = False
        self.cv = None
        self.save_model = False
        self.metrics = pm.libra.rmse
        self.n_trials = 100
        self.extra_parameters = {} # For other more parameters

    def preprocess(self):
        cf.info('stop word is set to ', repr(self.stop_words))
        X_train, X_test, y_train, y_test, idx1, idx2 = train_test_split(
            self.X,
            self.y,
            np.arange(len(self.X)),
            random_state=6363,
            test_size=self.test_size)

        if self.countervectorize:
            cv = CountVectorizer(min_df=1,
                                 max_df=1.0,
                                 token_pattern='\\b\\w+\\b',
                                 stop_words=self.stop_words)
            X_train = cv.fit_transform(X_train)
            X_test = cv.transform(X_test)
            self.cv = cv

            if self.save_model:
                f_vocabulary = cf.io.tmpfile('cv', 'json')
                cf.js.write(cv.vocabulary_, f_vocabulary)

        self.X_train = X_train
        self.X_test = X_test
        self.y_test = y_test
        self.y_train = y_train
        self.indices = [idx1, idx2]
        self.indices = {'train': idx1, 'val': idx2}
        cf.info('Preprocess completed.')
        return X_train, X_test, y_train, y_test, idx1, idx2

    def postprocess_prediction(self, y_pred: list) -> list:
        # Post process prediction, e.g., regression result to classification result
        return y_pred

    def build_model(self):
        cf.info('build model completed.')

    def fit(self):
        if self.X_train is None:
            self.preprocess()

        self.build_model()
        self.model.fit(self.X_train, self.y_train)
        cf.info(f'Training completed')

        if self.save_model:
            model_name = cf.io.tmpfile(self.model_type, 'joblib')
            joblib.dump(self.model, model_name, compress=9)
            cf.info('model saved to {}'.format(model_name))

        y_pred = self.model.predict(self.X_test)
        y_pred = self.postprocess_prediction(y_pred)
        _score = self.metrics(self.y_test, y_pred)
        cf.info('Score:', _score)
        return self.X_train, self.X_test, self.y_train, self.y_test, y_pred

    def predict(self, X_test: list) -> list:
        y_pred = self.model.predict(X_test)
        cf.info('prediction completes')
        return y_pred

    def ensure_process(self):
        if not self.X_train:
            self.preprocess()

    def optuna(self, objective, n_trials, _direction: str):
        self.ensure_process()
        study = optuna.create_study(direction=_direction)
        study.optimize(objective, n_trials)

        best_trial = study.best_trial
        cf.info("Number of finished trials: {}".format(len(study.trials)))
        cf.info("Best trial: {}".format(best_trial.value))
        cf.info(best_trial.params)
        return best_trial.params

