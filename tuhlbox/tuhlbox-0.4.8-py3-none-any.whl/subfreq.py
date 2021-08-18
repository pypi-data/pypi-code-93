"""Transformer computing second-order attributes."""
from __future__ import annotations

import logging
import math
from collections import defaultdict
from typing import Any, Dict, Iterable, List

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

logger = logging.getLogger(__name__)


class SubFrequencyVectorizer(BaseEstimator, TransformerMixin):
    """Transformer computing second-order attributes."""

    def __init__(self) -> None:
        """Initialize the model."""
        self.t: Dict[str, np.array] = defaultdict(np.array)

    def fit(
        self, X: List[str], y: Iterable[str], **_fit_params: Any
    ) -> SubFrequencyVectorizer:
        """Fit data to model."""
        words = set()

        logger.info("starting phase 0")
        documents = defaultdict(list)
        for document, target in zip(X, y):
            documents[target].append(document)
            for word in document.split():
                words.add(word)

        targets = set(y)
        tp: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))
        weights: Dict[str, Dict[str, float]] = defaultdict(lambda: defaultdict(float))

        # equation 1: weight calculation
        for target, target_docs in documents.items():
            for document in target_docs:
                doc_words = document.split()
                for doc_word in doc_words:
                    tf = doc_words.count(doc_word)
                    length = len(doc_words)
                    weights[target][doc_word] += math.log2(1 + tf / length)

        # equation 2.2: normalization
        for target in targets:
            for word in words:
                norm_term = 0.0
                for k in targets:
                    norm_term += weights[k][word]
                tp[target][word] = weights[target][word] / norm_term

        for word in words:
            self.t[word] = np.array([tp[target][word] for target in targets])

        return self

    def transform(self, X: Iterable[str], _y: Any = None) -> np.array:
        """Transform data due to previously learned frequencies."""
        result = []
        for k in X:
            document_sum = 0
            doc_words = k.split()
            for j in doc_words:
                if j not in self.t:
                    continue
                tf = doc_words.count(j)
                document_sum += self.t[j] * tf / len(doc_words)
            result.append(document_sum)
        return np.array(result)
