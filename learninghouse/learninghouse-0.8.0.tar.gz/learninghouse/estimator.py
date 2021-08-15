#coding: utf-8

from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier

class EstimatorFactory():
    @staticmethod
    def get_estimator(estimatorcfg):
        options = estimatorcfg['options']

        ESTIMATORS = {
            "DecisionTreeClassifier": DecisionTreeClassifier,
            "RandomForestClassifier": RandomForestClassifier
        }

        return ESTIMATORS[estimatorcfg['class']](**options)
