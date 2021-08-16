#!/usr/bin/env python
import abc

import codefast as cf
import joblib
import numpy as np
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC

import premium as pm
from premium.preprocess import any_cn, jb_cut


class Text:
    @classmethod
    def process(cls, X, y, test_size: float):
        cv = CountVectorizer(min_df=1, max_df=1.0, token_pattern='\\b\\w+\\b')
        X_train, X_test, y_train, y_test, ids_train, ids_test = train_test_split(
            X, y, np.arange(len(X)), random_state=63, test_size=test_size)

        X_train = cv.fit_transform(X_train)
        X_test = cv.transform(X_test)
        f_vocabulary = cf.io.tmpfile('cv', 'json')
        cf.js.write(cv.vocabulary_, f_vocabulary)
        return X_train, X_test, y_train, y_test, ids_train, ids_test


class BaseModel(metaclass=abc.ABCMeta):
    def __init__(self, X, y, test_size: float = 0.2):
        self.X = jb_cut(X) if any_cn(X) else X
        self.y = y
        self.test_size = test_size
        self.model_type = 'basemodel'
        self.stop_words = []
        self.cv = None
        self.save_model = False
        self.scoring = None

    def preprocess(self):
        cf.info('stop word is setting to ', repr(self.stop_words))
        cv = CountVectorizer(min_df=1,
                             max_df=1.0,
                             token_pattern='\\b\\w+\\b',
                             stop_words=self.stop_words)
        X_train, X_test, y_train, y_test, idx1, idx2 = train_test_split(
            self.X,
            self.y,
            np.arange(len(self.X)),
            random_state=2017,
            test_size=self.test_size)

        X_train = cv.fit_transform(X_train)
        X_test = cv.transform(X_test)

        self.cv = cv
        f_vocabulary = cf.io.tmpfile('cv', 'json')
        cf.js.write(cv.vocabulary_, f_vocabulary)

        self.X_train = X_train
        self.X_test = X_test
        self.y_test = y_test
        self.y_train = y_train
        self.indices = [idx1, idx2]
        return X_train, X_test, y_train, y_test, idx1, idx2

    def postprocess_prediction(self, y_pred: list) -> list:
        # Post process prediction, e.g., regression result to classification result
        return y_pred

    def build_model(self):
        ...

    def fit(self):
        self.preprocess()
        self.indices = {'train': self.indices[0], 'val': self.indices[1]}

        self.build_model()

        self.model.fit(self.X_train, self.y_train)
        cf.info(f'train completes with {self.model}.')

        if self.save_model:
            model_name = cf.io.tmpfile(self.model_type, 'joblib')
            joblib.dump(self.model, model_name, compress=9)
            cf.info('model saved to {}'.format(model_name))

        y_pred = self.model.predict(self.X_test)
        y_pred = self.postprocess_prediction(y_pred)
        cf.info('validation metrics:')
        pm.libra.metrics(self.y_test, y_pred)
        return self.X_train, self.X_test, self.y_train, self.y_test, y_pred

    def predict(self, X_test: list) -> list:
        y_pred = self.model.predict(X_test)
        cf.info('prediction completes')
        return y_pred

    def grid_search(self):
        self.grid = GridSearchCV(estimator=self.model,
                                 param_grid=self.parameters,
                                 refit=True,
                                 verbose=1,
                                 n_jobs=15,
                                 scoring=self.scoring)
        self.grid.fit(self.X_train, self.y_train)
        cf.info('best parameters:', self.grid.best_params_)
        cf.info('best score:', self.grid.best_score_)
        
        cf.info('Validating on test dataset.')
        y_pred = self.grid.predict(self.X_test)
        pm.libra.metrics(self.y_test, y_pred)


class LR(BaseModel):
    '''wrapper of linear regression model'''
    def __init__(self, X, y):
        super(LR, self).__init__(X, y)
        cf.info('First item of X:', self.X[0])
        self.model = LinearRegression()
        self.model_type = 'LinearRegression'

    def postprocess_prediction(self, y_pred) -> list:
        return [1 if e >= 0.5 else 0 for e in y_pred]


class SVM(BaseModel):
    '''wrapper of svm model'''
    def __init__(self, X, y, test_size: float = 0.2):
        super(SVM, self).__init__(X, y, test_size)
        self.model_type = 'svm'
        self.model = SVC(kernel='rbf', C=10, gamma=0.01, random_state=63)
        self.parameters = {
            'C': [0.01, 0.1, 1, 10, 100],
            'gamma': [1, 0.1, 0.01, 0.001],
            'kernel': ['rbf', 'poly', 'sigmoid']
        }


class Bayes(BaseModel):
    '''wrapper of Bayes model'''
    def __init__(self, X, y, test_size: float = 0.2):
        super(Bayes, self).__init__(X, y, test_size)
        self.model = MultinomialNB()
        self.model_type = 'bayes'


class Forest(BaseModel):
    '''wrapper of random forest model'''
    def __init__(self, X, y, test_size: float = 0.2):
        super(Forest, self).__init__(X, y, test_size)
        self.model = RandomForestClassifier()
        self.model_type = 'random_forest'


class Ensemble(BaseModel):
    ''' wrapper '''
    def __init__(self, X, y, test_size: float = 0.2):
        super(Ensemble, self).__init__(X, y, test_size)
        rf = RandomForestClassifier(n_estimators=50, random_state=1)
        svm = SVC(kernel='rbf', C=0.025)
        bayes = MultinomialNB()
        self.model = VotingClassifier(estimators=[('svm', svm), ('rf', rf),
                                                  ('bayes', bayes),
                                                  ('svm2', svm),
                                                  ('bayes2', bayes)],
                                      voting='hard')
