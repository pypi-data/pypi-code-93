"""Transformers calculating string kernels."""
from __future__ import annotations

import logging
from collections import defaultdict
from typing import Any, Callable, Dict, List, Tuple, Generator

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

logger = logging.getLogger(__name__)


def iterate_ngrams(
    string: str, ngram_min: int, ngram_max: int
) -> Generator[str, None, None]:
    for ngram_size in range(ngram_min, ngram_max + 1):
        for index in range(len(string) - ngram_size + 1):
            yield string[index : index + ngram_size].lower()


def get_all_ngram_counts(string: str, ngram_min: int, ngram_max: int) -> Dict[str, int]:
    result: Dict[str, int] = defaultdict(int)
    for ngram in iterate_ngrams(string, ngram_min, ngram_max):
        result[ngram] += 1
    return result


def presence_kernel(ngram_min: int, ngram_max: int) -> Callable:
    """
    Calculate the presence kernel, Ionescu & Popescu 2017.

    the result is a matrix, where each point [x, y] is the number of different n-grams
    that both documents x and y share.
    """

    def internal_presence_kernel(x: np.array, y: np.array) -> np.array:
        result = np.zeros((len(x), len(y)), dtype=int)
        x_counts = [get_all_ngram_counts(d, ngram_min, ngram_max) for d in x]
        y_counts = [get_all_ngram_counts(d, ngram_min, ngram_max) for d in y]
        for i, xc in enumerate(x_counts):
            xkeys = set(xc.keys())
            for j, yc in enumerate(y_counts):
                ykeys = set(yc.keys())
                result[i, j] = len(xkeys.intersection(ykeys))
        return result

    return internal_presence_kernel


def legacy_presence_kernel(ngram_min: int, ngram_max: int) -> Callable:
    """Old implementation. Slower."""

    def internal_legacy_presence_kernel(x: np.array, y: np.array) -> np.array:
        result = np.zeros((len(x), len(y)), dtype=int)
        for i, string in enumerate(x):
            ngrams1 = set()
            for ngram in iterate_ngrams(string, ngram_min, ngram_max):
                ngrams1.add(ngram)
            for j, counterstring in enumerate(y):
                ngrams2 = set()
                for ngram in iterate_ngrams(counterstring, ngram_min, ngram_max):
                    ngrams2.add(ngram)
                result[i, j] = len(ngrams1.intersection(ngrams2))
        return result

    return internal_legacy_presence_kernel


def spectrum_kernel(ngram_min: int, ngram_max: int) -> Callable:
    """Calculate the spectrum kernel, Ionescu & Popescu 2017."""

    def internal_spectrum_kernel(x: np.array, y: np.array) -> np.array:
        result = np.zeros((len(x), len(y)), dtype=int)
        x_counts = [get_all_ngram_counts(d, ngram_min, ngram_max) for d in x]
        y_counts = [get_all_ngram_counts(d, ngram_min, ngram_max) for d in y]
        for i, xc in enumerate(x_counts):
            xkeys = set(xc.keys())
            for j, yc in enumerate(y_counts):
                ykeys = set(yc.keys())
                all_ngrams = set(xkeys).intersection(set(ykeys))
                result[i, j] = sum([xc[ngram] * yc[ngram] for ngram in all_ngrams])
        return result

    return internal_spectrum_kernel


def legacy_spectrum_kernel(ngram_min: int, ngram_max: int) -> Callable:
    """Old implementation. Slower."""

    def internal_legacy_spectrum_kernel(x: np.array, y: np.array) -> np.array:
        result = np.zeros((len(x), len(y)), dtype=int)
        for i, string in enumerate(x):
            ngrams: Dict[str, int] = defaultdict(int)
            for ngram in iterate_ngrams(string, ngram_min, ngram_max):
                ngrams[ngram] += 1
            for j, counterstring in enumerate(y):
                for ngram in iterate_ngrams(counterstring, ngram_min, ngram_max):
                    result[i, j] += ngrams[ngram]
        return result

    return internal_legacy_spectrum_kernel


def intersection_kernel(ngram_min: int, ngram_max: int) -> Callable:
    """Calculate the intersection kernel, Ionescu & Popescu 2017."""

    def internal_intersection_kernel(x: np.array, y: np.array) -> np.array:
        result = np.zeros((len(x), len(y)), dtype=int)
        x_counts = [get_all_ngram_counts(d, ngram_min, ngram_max) for d in x]
        y_counts = [get_all_ngram_counts(d, ngram_min, ngram_max) for d in y]
        for i, xc in enumerate(x_counts):
            xkeys = set(xc.keys())
            for j, yc in enumerate(y_counts):
                ykeys = set(yc.keys())
                common_ngrams = set(xkeys).intersection(set(ykeys))
                result[i, j] = sum(
                    [min(xc[ngram], yc[ngram]) for ngram in common_ngrams]
                )
        return result

    return internal_intersection_kernel


def legacy_intersection_kernel(ngram_min: int, ngram_max: int) -> Callable:
    """Old implementation. Slower."""

    def internal_legacy_intersection_kernel(x: np.array, y: np.array) -> np.array:
        result = np.zeros((len(x), len(y)), dtype=int)
        for i, string in enumerate(x):
            ngrams: Dict[str, int] = defaultdict(int)
            for ngram in iterate_ngrams(string, ngram_min, ngram_max):
                ngrams[ngram] += 1
            for j, counterstring in enumerate(y):
                ngrams2 = dict(ngrams)
                for ngram in iterate_ngrams(counterstring, ngram_min, ngram_max):
                    if ngram in ngrams2 and ngrams2[ngram] > 0:
                        result[i, j] += 1
                        ngrams2[ngram] -= 1
        return result

    return internal_legacy_intersection_kernel


kernel_map = {
    "presence": presence_kernel,
    "spectrum": spectrum_kernel,
    "intersection": intersection_kernel,
}


class StringKernelTransformer(BaseEstimator, TransformerMixin):
    """
    DEPRECATED: you should probably use the Scikit SVC instead.

    Converts (string) documents to a similarity matrix (kernel).

    Input (fit): List of m strings
    Input (transform): List of n strings
    Output: m x n matrix containing the kernel similarities between the strings
    """

    def __init__(
        self,
        kernel_type: str = "intersection",
        ngram_range: Tuple[int, int] = None,
        normalize: bool = True,
    ):
        """
        Initialize the model.

        Args:
            kernel_type: one of 'intersection', 'spectrum' or 'presence'.
            ngram_range: range of n_grams to include
            normalize: whether to normalize the output across the corpus.
        """
        if ngram_range is None:
            ngram_range = (5, 10)
        self.ngram_range = ngram_range
        self.normalize = normalize
        self.kernel_type = kernel_type
        if kernel_type not in kernel_map:
            raise ValueError(f"unknown kernel: {kernel_type}")
        self._kernel = kernel_map[kernel_type]
        self._train_data = None
        self._train_kernel: np.array = None

    def fit(self, X: List[str], _y: Any = None) -> StringKernelTransformer:
        """Fit model."""
        self._train_data = np.array(X)
        self._train_kernel = self._kernel(*self.ngram_range)(X, X)
        for i in range(len(X)):
            if self._train_kernel[i, i] == 0:
                logger.error(f"zeros in diagonal at ({i},{i}) for {X[i]}")
        return self

    def transform(self, X: List[str], _y: Any = None) -> np.array:
        """Transform data."""
        X = np.array(X)
        _st = self._kernel(*self.ngram_range)(X, self._train_data)

        if not self.normalize:
            return _st

        _ss = self._train_kernel
        _tt = self._kernel(*self.ngram_range)(X, X)

        result = np.copy(_st)
        for i in range(_st.shape[0]):
            if _tt[i, i] == 0:
                logger.error(f"zeros in diagonal at ({i},{i}) for {X[i]}")
            for j in range(_st.shape[1]):
                if _tt[i, i] != 0 and _ss[j, j] != 0:
                    result[i, j] /= np.sqrt(_tt[i, i] * _ss[j, j])

        return result
