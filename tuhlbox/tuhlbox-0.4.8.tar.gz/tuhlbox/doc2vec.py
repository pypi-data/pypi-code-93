"""Transformers that calculate Doc2Vec embeddings using GenSim."""
from __future__ import annotations

import logging
from collections.abc import Iterable
from typing import Any, List, Union

import numpy as np
from gensim.models.doc2vec import Doc2Vec, TaggedDocument  # type: ignore
from sklearn.base import BaseEstimator, TransformerMixin  # type: ignore

logging.getLogger("gensim").setLevel(logging.WARNING)
logging.getLogger("gensim").propagate = False


def _sanity_check(documents: List[List[str]]) -> None:
    """
    Check data for basic properties.

    Checks if the data is not-empty, and each document is a list of strings
    representing sentences.
    """
    if len(documents) < 1:
        raise ValueError("empty document set provided")

    if type(documents[0]) == str or not isinstance(documents[0], Iterable):
        raise TypeError("this transformer only works on pre-split data.")


class Doc2VecTransformer(TransformerMixin, BaseEstimator):
    """
    Transforms documents/sentences into a fixed-dimensional vector space.

    input: a list of list of strings
        each document is represented as a list of strings - those can be
        sentences, or tweets, or ...
    output: a list of list of numbers
        each document ist returned as the embedding vector.
    """

    def __init__(
        self,
        learning_rate: float = 0.02,
        epochs: int = 20,
        vector_size: int = 100,
        alpha: float = 0.025,
        min_alpha: float = 0.00025,
        min_count: int = 2,
        distributed_memory: int = 1,
        workers: int = 1,
    ):
        """
        Initialize Doc2Vec Transformer.

        Args:
            learning_rate: Learning rate of gensim model
            epochs: number of epochs to train the gensim model
            vector_size: final vector size
            alpha: alpha of the gensim model
            min_alpha: min_alpha of the gensim model
            min_count: min number of occurrences for each word
            distributed_memory: whether to use distributed memory model or not
            workers: number of threads
        """
        self.learning_rate = learning_rate
        self.epochs = epochs
        self.vector_size = vector_size
        self.alpha = alpha
        self.min_alpha = min_alpha
        self.min_count = min_count
        self.distributed_memory = distributed_memory
        self.workers = workers

        self.model = Doc2Vec(
            vector_size=vector_size,
            alpha=alpha,
            min_alpha=min_alpha,
            min_count=min_count,
            dm=distributed_memory,
            workers=workers,
        )

    def fit(
        self,
        documents: List[List[str]],
        labels: Union[List[str], np.array] = None,
        **fit_params: Any
    ) -> Doc2VecTransformer:
        """Fit the model by learning the training corpus."""
        documents = [[str(x) for x in document] for document in documents]

        _sanity_check(documents)
        tagged_x = [
            TaggedDocument(words=row, tags=[]) for _, row in enumerate(documents)
        ]
        self.model.build_vocab(tagged_x)
        self.model.train(
            tagged_x, total_examples=self.model.corpus_count, epochs=self.epochs
        )
        return self

    def transform(self, documents: List[List[str]]) -> np.array:
        """Infer the vectors for documents."""
        documents = [[str(x) for x in document] for document in documents]
        _sanity_check(documents)
        vectors = [self.model.infer_vector(doc) for doc in documents]
        return np.array(vectors)
