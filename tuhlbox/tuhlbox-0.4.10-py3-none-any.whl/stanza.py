"""Transformers that use stanza documents."""
from __future__ import annotations

import json
import logging
import os
import warnings
from typing import Any, Dict, Iterable, List, Union

import nltk
from sklearn.base import BaseEstimator, TransformerMixin
from tqdm import tqdm

import stanza
from stanza.models.common.doc import Document, Sentence, Word

logger = logging.getLogger(__name__)

UNKNOWN_KEY = "UNK"
WORD_FEATURES_JSON = os.path.join("resources", "word_features.json")


def _get_word_attribute(
    word: Word,
    attribute: str,
    fallback: str = "_",
) -> Union[str]:
    if fallback is None:
        raise ValueError("Fallback can't be None")
    if hasattr(word, attribute):
        a = getattr(word, attribute)
        if a is not None:
            return a
    if not hasattr(word, "_feats"):
        return fallback

    feats = word.feats
    if not feats or feats == "_":
        return fallback
    pairs = feats.split("|")
    features = {k: v for (k, v) in [x.split("=") for x in pairs]}
    if attribute not in features or features[attribute] is None:
        return fallback
    return features[attribute]


def _get_features_per_word(document: Document) -> List[Dict[str, str]]:
    result = []
    words = []
    for sentence in document.sentences:
        words += sentence.words
    for word in words:
        features = word.feats
        if not features or features == "_":
            continue
        pairs = features.split("|")
        result.append({k: v for (k, v) in [x.split("=") for x in pairs]})
    return result


class StanzaWordFeatureFrequencyTransformer(BaseEstimator, TransformerMixin):
    """
    Return a frequency matrix for all features for each word of each document.

    This transformer looks for the file resources/word_features.json, where all
    possible values should be stored (unfortunately, stanfordnlp does not offer
    a comprehensive list of possible values for each model).

    If this transformer encounters an element not in that file, it will add one
    """

    def __init__(self) -> None:
        """Initialize class."""
        super().__init__()
        with open(WORD_FEATURES_JSON) as i_fh:
            self.features = json.load(i_fh)
            self.features.append(UNKNOWN_KEY)  # for unknown keys

    def fit(
        self, _x: Any, _y: Any = None, **_fit_kwargs: Any
    ) -> StanzaWordFeatureFrequencyTransformer:
        """Fit the model."""
        return self

    def transform(
        self, x: Iterable[Document], _y: Iterable = None
    ) -> List[Dict[str, int]]:
        """Transform documents."""
        result = []
        for document in x:
            doc = {}
            for feature in self.features:
                doc[feature] = 0
            for features_dict in _get_features_per_word(document):
                for k, v in features_dict.items():
                    key = f"{k}__{v}"
                    if key not in doc:
                        key = UNKNOWN_KEY
                        warnings.warn(f"key {key} not found during fit, returning UNK")
                    doc[key] += 1
            result.append(doc)
        return result


class StanzaNlpToFieldTransformer(BaseEstimator, TransformerMixin):
    """
    Flattens a stanford document in the same order as the parsed text.

    Input (Document | Sentence):
        each document is expected to be a StanfordNLP document or sentence.
    Output: each document is returned as a single string, where each word is
        represented as the field that is to be extracted, separated by spaces.
        Sentences are separated by newlines.
    """

    def __init__(self, field: str):
        """
        Initialize class.

        Args:
            field: which part of a word (token) to use as representative.
        """
        self.field = field

    def fit(self, _x: Any, _y: Any = None) -> StanzaNlpToFieldTransformer:
        """Fit the model."""
        return self

    def transform(
        self, x: Iterable[Union[str, Document, Sentence]], _y: Any = None
    ) -> List[str]:
        """Transform documents."""
        result = []
        for document in x:
            document_result: List[str] = []
            sentences: List[Sentence] = []
            if isinstance(document, Sentence):
                sentences = [document]
            elif isinstance(document, Document):
                sentences = document.sentences
            for sentence in sentences:
                new_sentence = []
                for word in sentence.words:
                    label = _get_word_attribute(word, self.field, fallback="_")
                    if label is None:
                        raise ValueError(f"label is None for word: {word}")
                    new_sentence.append(label)
                document_result.append(" ".join(new_sentence))
            result.append("\n".join(document_result))
        return result


class StanzaParserTransformer(BaseEstimator, TransformerMixin):
    """
    Parses text using the stanza parser.

    This transformer takes text and parses it using the stanza python
    package, which uses theano and various neural models to parse different
    features from natural text.
    """

    def __init__(self, language: str, silent: bool = False, cpu: bool = False):
        """
        Initialize class.

        Args:
            language: which language to use for parsing.
            silent: if true, don't show a progress bar
            cpu: if true, use cpu instead of gpu. Useful for memory-intensive
                parse tasks.
        """
        self.language = language
        self.silent = silent
        self.cpu = cpu
        if cpu:
            logger.info("using CPU for stanford parsing")
            os.environ["CUDA_VISIBLE_DEVICES"] = ""
        self.nlp = stanza.Pipeline(lang=self.language, use_gpu=not cpu)

    def fit(self, _x: Any, _y: Any = None) -> StanzaParserTransformer:
        """Fit the model."""
        return self

    def transform(self, x: Iterable[str], _y: Any = None) -> List[Document]:
        """Transform documents."""
        result = []
        if self.silent:
            pbar = x
        else:
            pbar = tqdm(x)
        for document in pbar:
            with open("/tmp/stanford_parsing", "a") as log_fh:
                log_fh.write(document + "/n")
                result.append(self.nlp(document))
        return result


class StanzaToNltkTreesTransformer(BaseEstimator, TransformerMixin):
    """
    Transform Stanza Documents into NLTK trees.

    This transformer takes documents created by the stanza python package
    and transforms them into dependency trees in nltk format.

    Input: each document is either a stanza Document or Sentence.
    Output: each document is a list of NLTK Trees, one for each sentence.
        If the input document is a sentence, than the result is a list with
        a single entry.

    """

    node_labels: List[str]

    def __init__(self, node_labels: Union[str, List[str]] = None):
        """
        Initialize transformer.

        Args:
            node_labels (list of str): how each word is represented. Provide a
                list of ['lemma', 'upos', 'xpos', 'dependency'], e.g.:
                node_contents=['upos', 'dependency']
        """
        if isinstance(node_labels, str):
            self.node_labels = [node_labels]
        elif isinstance(node_labels, list):
            self.node_labels = node_labels
        if not node_labels:
            self.node_labels = ["upos"]

    def fit(self, _x: Any, _y: Any = None) -> StanzaToNltkTreesTransformer:
        """Fit the model."""
        return self

    def transform(
        self, x: Iterable[Union[Document, Sentence]], _y: Any = None
    ) -> List[List[nltk.Tree]]:
        """Transform documents."""
        result = []
        for document in x:
            sentences = []
            if isinstance(document, Document):
                sentences = document.sentences
            elif isinstance(document, Sentence):
                sentences = [document]
            doc = []
            for sentence in sentences:
                dependency_tree = self.parse(sentence)
                labeled_tree = self.get_symbols(dependency_tree)
                doc.append(labeled_tree)
            if not doc:
                raise ValueError(f"coud not parse anything from input {document}")
            result.append(doc)
        return result

    def get_symbols(self, tree: nltk.Tree) -> nltk.Tree:
        """Extract the symbol from the dependency relationship."""
        dependency = tree.label()
        if isinstance(dependency, str):
            return nltk.Tree(dependency, [self.get_symbols(c) for c in tree])
            # root case

        # the dependency consists of three parts:
        _, relationship, word_2 = dependency
        # the first word is already handled in other iterations of this method
        labels = []
        if "dependency" in self.node_labels:
            labels.append(relationship)
        labels += [
            _get_word_attribute(word_2, label, fallback="_")
            for label in self.node_labels
            if label != "dependency"
        ]
        label = "#".join(labels)
        result = nltk.Tree(label, [self.get_symbols(c) for c in tree])
        return result

    def get_nodes(self, tree: nltk.Tree) -> List[nltk.Tree]:
        """Extract the leaf nodes from a tree."""
        leaves = []
        if isinstance(tree, nltk.Tree):
            if not isinstance(tree.label(), str):
                leaves.append(tree)
            for child in tree:
                leaves += self.get_nodes(child)
        return leaves

    def parse(self, sentence: Sentence) -> nltk.Tree:
        """Construct a NLTK tree from stanza dependencies."""
        roots = [d for d in sentence.dependencies if d[1] == "root"]
        unprocessed = [d for d in sentence.dependencies if d not in roots]
        # it is possible that multiple words have a root relationship
        tree = nltk.Tree("root", [nltk.Tree(x, []) for x in roots])

        while True:
            changed = False
            added_dependencies = []
            nodes = self.get_nodes(tree)
            for d in unprocessed:
                for leaf in nodes:
                    if hasattr(d[0], "id"):
                        if leaf.label()[2].id == d[0].id:
                            leaf.append(nltk.Tree(d, []))
                            added_dependencies.append(d)
                            changed = True
                    elif hasattr(d[0], "index"):
                        if leaf.label()[2].index == d[0].index:
                            leaf.append(nltk.Tree(d, []))
                            added_dependencies.append(d)
                            changed = True
            unprocessed = [x for x in unprocessed if x not in added_dependencies]
            if len(unprocessed) == 0 or not changed:
                break

        return tree
