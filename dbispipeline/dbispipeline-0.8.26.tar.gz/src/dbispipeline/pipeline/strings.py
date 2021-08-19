"""Provides transformers that work and modify strings."""
import string

from sklearn.base import BaseEstimator
from sklearn.base import TransformerMixin


class FlatteningTransformer(BaseEstimator, TransformerMixin):
    """
    Input Document Format: arbitrarily deep nested list of strings
    Output Document Format: string
    """

    def __init__(self, join_symbol=' '):
        self.join_symbol = join_symbol

    def fit(self, X, y=None):
        return self

    def _flatten(self, document):
        if type(document) != list:
            return document
        return self.join_symbol.join([self._flatten(x) for x in document])

    def transform(self, X, y=None):
        ret = []
        for document in X:
            ret.append(self._flatten(document))
        return ret


class TextCleaner(BaseEstimator, TransformerMixin):
    """
    removes all characters provided from strings.

    Input Document Format: string
    Output Document Format: string (cleaned)
    """

    def __init__(self, remove=string.punctuation):
        """
        Args:
            remove: a string containing all characters that should be removed.
                This defaults to the string.punctuation characters.
        """
        self.remove = remove

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        ret = []
        for document in X:
            ret.append(''.join([c for c in document if c not in self.remove]))
        return ret


class NgramTransformer(BaseEstimator, TransformerMixin):
    """
    input: list of strings
    output: list of ngrams found
    """

    def __init__(self, analyzer, ngram_range):
        """
        The arguments are loosely oriented to the scikit CountVectorizer
        Args:
            analyzer: 'word' or 'char'
            ngram_range: tuple
        """
        self.analyzer = analyzer
        self.ngram_range = ngram_range

    def fit(self, X, y=None):
        return self

    def transform(self, X, y=None):
        ret = []
        for document in X:
            tmp = []
            if self.analyzer == 'word':
                words = document.split()
            elif self.analyzer == 'char':
                words = document
            for ngram_size in range(self.ngram_range[0],
                                    self.ngram_range[1] + 1):
                for i in range(len(words) - ngram_size + 1):
                    if self.analyzer == 'word':
                        tmp.append(' '.join(words[i:i + ngram_size]))
                    elif self.analyzer == 'char':
                        tmp.append(''.join(words[i:i + ngram_size]))
            ret.append(tmp)
        return ret
