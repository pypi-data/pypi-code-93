"""Custom models."""
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.base import ClassifierMixin
from sklearn.utils import check_array


class RandomClassifier(BaseEstimator, ClassifierMixin):
    """
    Classifier for 'checking' random baselines.

    Random classifier that computes the classes and their distribution from the
    trainings data. Predicts classes according to calculated probabilities or
    with uniform distribution.
    """

    def __init__(self, uniform=False):
        """
        Constructor for random classifier.

        Args:
            uniform: if False, uses class distribution in training data as
            probability for prediction.
        """
        self.classes = [0, 1, 2]
        self.probabilites = []
        self.uniform = uniform

    def fit(self, x, y, **fit_args):
        """
        Learn probabilities from training data distribution.

        Uses the unique targets as classes and calculates the distribution in
        the data, and stores that in form of probabilities.

        Args:
            x: the training data
            y: the target values, corresponding to X
            **fit_args:

        Returns: self
        """
        # figure out distribution of classes in the data
        self.classes, counts = np.unique(y, return_counts=True)
        self.probabilites = counts / len(y)
        return self

    def predict(self, documents):
        """
        Predicts the output classes of X.

        Args:
             documents: the documents to be predicted.
        """
        documents = check_array(documents, ensure_2d=False, allow_nd=True)
        if self.uniform:
            return [np.random.choice(self.classes) for x in documents]
        else:
            return [
                np.random.choice(self.classes, p=self.probabilites)
                for x in documents
            ]
