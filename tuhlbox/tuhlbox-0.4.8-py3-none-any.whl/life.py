"""Implementation of Llorens 2016."""
from __future__ import annotations

import random
from collections import defaultdict
from typing import List, Union, Dict

import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


def get_features_for_sample(sample: List[str]) -> List[int]:
    """
    Calculate statistical features from samples.

    First, the occurrence of all words is counted.
    Then, this method returns the number of words that are between pre-set
    frequency thresholds.
    Args:
        sample: a list of words to calculate metrics from.

    Returns: a list of four threshold counts: [
            1. total number of words,
            2. number of words that occur once,
            3. number of words that occur 2-4 times,
            4. number of words that occur 5-10 times
        ].

    """
    counts: Dict[str, int] = defaultdict(int)
    for word in sample:
        counts[word] += 1
    v0 = len(counts.keys())
    v1, v2, v3 = 0, 0, 0
    for occurrences in counts.values():
        if occurrences <= 1:
            v1 += 1
        elif occurrences <= 4:
            v2 += 1
        elif occurrences <= 10:
            v3 += 1

    return [v0, v1, v2, v3]


class LifeVectorizer(BaseEstimator, TransformerMixin):
    """Implementation of Llorens 2016."""

    def __init__(
        self,
        fragment_sizes: List[int] = None,
        samples: int = 200,
        sample_type: str = "bow",
        force: bool = True,
    ):
        """
        Initialize the transformer.

        Args:
            fragment_sizes: which sizes to use as window sizes
            samples: how many samples per window size are captured
            sample_type: how the samples are created
            force: if true, calculates samples of too-short texts.
        """
        if fragment_sizes is None:
            fragment_sizes = [200, 500, 800, 1000, 1500, 2000, 3000, 4000]
        valid_sample_types = ["bow", "fragment", "both"]
        if sample_type not in valid_sample_types:
            raise ValueError(
                f"unknown sample type: {sample_type}. valid values: "
                f"{valid_sample_types}"
            )
        self.fragment_sizes = fragment_sizes
        self.samples = samples
        self.sample_type = sample_type
        self.force = force

    def fit(self, _x: List[str], _y: Union[List, np.array] = None) -> LifeVectorizer:
        """Fit the model."""
        return self

    def sample(
        self,
        words: Union[List[str], np.array],
        fragment_size: int,
        method: str,
    ) -> List[List[str]]:
        """
        Take <self.samples> samples of <fragment_size> elements from <words>.

        Args:
            words: a sequence of words to sample from
            fragment_size: size of the window
            method: either "fragment" or "bow" (see paper)

        Returns:
            a list of <self.samples> samples.
        """
        ret = []
        wordcount = len(words)
        if wordcount < fragment_size:
            if self.force:
                fragment_size = wordcount
            else:
                raise ValueError(
                    f"fragment size ({fragment_size}) is larger than document "
                    f"size ({wordcount}) for document starting with: \n\n"
                    f'{" ".join(words[:50])}\n\n'
                )
        for _ in range(self.samples):
            if method == "fragment":
                left = random.randint(0, wordcount - fragment_size)
                right = left + fragment_size
                ret.append(words[left:right])
            if method == "bow":
                ret.append(random.sample(words, fragment_size))
        return ret

    def get_features(
        self,
        document: List[str],
        sample_size: int,
    ) -> np.array:
        """Extract features from a document given a sample size."""
        if self.sample_type == "both":
            return np.concatenate(
                [
                    self._get_features(document, sample_size, "bow"),
                    self._get_features(document, sample_size, "fragment"),
                ]
            )
        else:
            return self._get_features(document, sample_size, self.sample_type)

    def _get_features(
        self,
        document: List[str],
        fragment_size: int,
        method: str,
    ) -> np.array:
        samples = self.sample(document, fragment_size, method)
        features = []
        for sample in samples:
            features.append(get_features_for_sample(sample))
        features = np.array(features)
        means = np.mean(features, axis=0)
        stds = np.std(features, axis=0)
        return np.concatenate(
            [means, np.divide(means, stds, out=np.zeros_like(means), where=stds != 0)]
        )

    def transform(
        self, x: List[List[str]], _y: Union[List, np.array] = None
    ) -> np.array:
        """Calculate samples and extracts features from documents."""
        ret = []
        for document in x:
            doc = [self.get_features(document, size) for size in self.fragment_sizes]
            ret.append(np.concatenate(doc))

        # some classifiers like XGBoost require a numpy array if nested
        return np.array(ret)
