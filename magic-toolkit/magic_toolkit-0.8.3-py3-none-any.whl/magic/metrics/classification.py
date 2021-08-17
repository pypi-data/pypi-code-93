import numpy as np
import collections

class ConfusionMatrix:
    def __init__(self, labels):
        self.labels = labels
        self.num_class = len(self.labels)
        self.tp = np.zeros(self.num_class)
        self.fn = np.zeros(self.num_class)
        self.fp = np.zeros(self.num_class)

    def count(self, y_true, y_pred):
        assert isinstance(y_true, collections.Iterable)
        assert isinstance(y_pred, collections.Iterable)
        for i, cls in enumerate(self.labels):
            if cls in y_true and cls in y_pred:
                self.tp[i] += 1
            if cls in y_true and cls not in y_pred:
                self.fn[i] += 1
            if cls not in y_true and cls in y_pred:
                self.fp[i] += 1

    def precision_score(self):
        return self.tp / (self.tp + self.fp)

    def recall_score(self):
        return self.tp / (self.tp + self.fn)

    def f1_score(self):
        precision = self.precision_score()
        recall = self.recall_score()
        return 2 * (precision * recall) / (precision + recall)
