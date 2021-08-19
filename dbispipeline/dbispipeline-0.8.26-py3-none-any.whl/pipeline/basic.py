"""
Contains helper classes that can be used with the scikit-learn machine
learning tools. They are primarily meant for NLP tasks, but should generalize
well.

The main contribution of these helper files are scikit pipeline elements and
the transformer picker element.
"""
from sklearn.base import BaseEstimator
from sklearn.base import TransformerMixin


class DictFieldTransformer(BaseEstimator, TransformerMixin):
    """
    Extracts a field from a dictionary object.
    """

    def __init__(self, field_name):
        """
        Args:
            field_name: the field to extract from the string
        """
        self.field_name = field_name

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        ret = []
        for document in X:
            ret.append(document[self.field_name])
        return ret


class CallbackTransformer(BaseEstimator, TransformerMixin):
    """
    Calls a predefined function on each document or on the entire data.
    """

    def __init__(self, callback, per_document=True):
        """
        Args:
            callback: the function to be called. Lambdas work well.
            per_document: if true, the function is called on each document.
                if false, the function is alled on the entirety of X in fit().
        """
        self.callback = callback
        self.per_document = per_document

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        if not self.per_document:
            return self.callback(X)
        ret = []
        for document in X:
            ret.append(self.callback(document))
        return ret
