#!/usr/bin/env python
import codefast as cf
import numpy
from codefast.utils import deprecated
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             mean_squared_error, recall_score)

red = cf.fp.red
green = cf.fp.green


class Libra:
    '''Metrics'''
    def rmse(self, y_true, y_pred) -> float:
        return mean_squared_error(y_true, y_pred, squared=False)

    def mse(self, y_true, y_pred) -> float:
        return mean_squared_error(y_true, y_pred)

    def f1_score(self, y_true, y_pred) -> float:
        return f1_score(y_true, y_pred)

    def accuracy_score(self, y_true, y_pred) -> float:
        return accuracy_score(y_true, y_pred)

    def metrics(self, y_true, y_pred):
        print('{:<20}: {}'.format('Accuracy score',
                                  accuracy_score(y_true, y_pred)))
        print('{:<20}: {}'.format('Recall score', recall_score(y_true, y_pred)))
        print('{:<20}: \n{}'.format('Confusion matrix',
                                    confusion_matrix(y_true, y_pred)))
        print('{:<20}: {}'.format('f1_score', f1_score(y_true, y_pred)))


libra = Libra()


@deprecated(cf.fp.red('Use pm.libra.metrics(y_true, y_pred) instead.'))
def metrics(y_true, y_pred):
    print('{:<20}: {}'.format('Accuracy score', accuracy_score(y_true, y_pred)))
    print('{:<20}: {}'.format('Recall score', recall_score(y_true, y_pred)))
    print('{:<20}: \n{}'.format('Confusion matrix',
                                confusion_matrix(y_true, y_pred)))
    print('{:<20}: {}'.format('f1_score', f1_score(y_true, y_pred)))


def cer(r: str, h: str):
    '''Character Error Rate
    (S + D + I) /N 
    S: substitution
    D: Deletion
    I: Insertion
    '''
    d = numpy.zeros((len(r) + 1) * (len(h) + 1), dtype=numpy.uint16)
    d = d.reshape((len(r) + 1, len(h) + 1))
    for i in range(len(r) + 1):
        for j in range(len(h) + 1):
            if i == 0:
                d[0][j] = j
            elif j == 0:    
                d[i][0] = i

    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            if r[i - 1] == h[j - 1]:
                d[i][j] = d[i - 1][j - 1]
            else:
                substitution = d[i - 1][j - 1] + 1
                insertion = d[i][j - 1] + 1
                deletion = d[i - 1][j] + 1
                d[i][j] = min(substitution, insertion, deletion)
    return d[len(r)][len(h)] / float(len(r))
