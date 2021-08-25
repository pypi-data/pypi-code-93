"""Transformers calculating string kernels."""
from __future__ import annotations

import logging
from collections import Counter
from typing import Dict, List

import numpy as np

logger = logging.getLogger(__name__)


def presence_kernel(x: np.array, y: np.array) -> np.array:
    """
    Calculate the presence kernel, Ionescu & Popescu 2017.

    x and y are lists of documents. Each document must be an iterable of features that
    can be compared using ==.

    Returns:
        a matrix where each entry [i, j] represents the number of features that document
        x[i] and y[j] have in common.
    """
    result = np.zeros((len(x), len(y)), dtype=int)
    x_counts: List[Dict] = [Counter(d) for d in x]
    y_counts: List[Dict] = [Counter(d) for d in y]
    for i, xc in enumerate(x_counts):
        keys_x = set(xc.keys())
        for j, yc in enumerate(y_counts):
            keys_y = set(yc.keys())
            result[i, j] = len(keys_x.intersection(keys_y))
    return result


def spectrum_kernel(x: np.array, y: np.array) -> np.array:
    """
    Calculate the spectrum kernel, Ionescu & Popescu 2017.

    x and y are lists of documents. Each document must be an iterable of features that
    can be compared using ==.

    Returns:
        a matrix where each entry [i, j] = sum(
           xc * yc for all xc, yc in (common features in x[i] and y[j])
        )
    """
    result = np.zeros((len(x), len(y)), dtype=int)
    x_counts: List[Dict] = [Counter(d) for d in x]
    y_counts: List[Dict] = [Counter(d) for d in y]
    for i, xc in enumerate(x_counts):
        keys_x = set(xc.keys())
        for j, yc in enumerate(y_counts):
            keys_y = set(yc.keys())
            all_ngrams = set(keys_x).intersection(set(keys_y))
            result[i, j] = sum([xc[ngram] * yc[ngram] for ngram in all_ngrams])
    return result


def intersection_kernel(x: np.array, y: np.array) -> np.array:
    """
    Calculate the intersection kernel, Ionescu & Popescu 2017.

    x and y are lists of documents. Each document must be an iterable of features that
    can be compared using ==.

    Returns:
        a matrix where each entry [i, j] = sum(
            min(xc, yc) for all xc, yc in (common features in x[i] and y[j])
        )
    """
    result = np.zeros((len(x), len(y)), dtype=int)
    x_counts: List[Dict] = [Counter(d) for d in x]
    y_counts: List[Dict] = [Counter(d) for d in y]
    for i, xc in enumerate(x_counts):
        keys_x = set(xc.keys())
        for j, yc in enumerate(y_counts):
            keys_y = set(yc.keys())
            common_ngrams = set(keys_x).intersection(set(keys_y))
            result[i, j] = sum(
                [min(xc[ngram], yc[ngram]) for ngram in common_ngrams]
            )
    return result
