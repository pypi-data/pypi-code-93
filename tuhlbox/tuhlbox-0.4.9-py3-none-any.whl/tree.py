"""Transformers working on NLTK tree objects."""
from __future__ import annotations

from typing import Any, Iterable, List, Union

import nltk
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin


class StringToTreeTransformer(BaseEstimator, TransformerMixin):
    """
    Parses tree representations into their nltk.Tree object form.

    input: list of list of strings
    output: list of list of nltk.Tree objects
    """

    def fit(self, _x: Any, _y: Any = None) -> StringToTreeTransformer:
        """Fit the model."""
        return self

    def transform(self, x: List[List[str]], _y: Any = None) -> List[List[nltk.Tree]]:
        """Transform the data."""
        result = []
        for document in x:
            ret = []
            if isinstance(document, str):
                raise Exception(
                    "this transformer only takes document which "
                    "are already split into sentences. Please use a sentence "
                    "splitter before (e.g., by using stanfordnlp)"
                )
            for line in document:
                if line and line.strip():
                    tree = nltk.Tree.fromstring(line)
                    ret.append(tree)
            result.append(ret)
        return result


class WordToPosTransformer(BaseEstimator, TransformerMixin):
    """
    Creates a POS-only representation of a tree sentence.

    input: list of list of trees
    output: list of list of strings
    """

    def fit(self, _x: Any, _y: Any = None) -> WordToPosTransformer:
        """Fit the model."""
        return self

    def transform(self, x: List[List[nltk.Tree]], _y: Any = None) -> List[List[str]]:
        """Transform the data."""
        ret = []
        for document in x:
            tmp = []
            for tree in document:
                tmp += [x[1] for x in tree.pos()]
            ret.append(tmp)
        return ret


class TreeChainTransformer(BaseEstimator, TransformerMixin):
    """
    Create chains of strings with an optional max length from tree structures.

    For each leaf node, its path to the root node is called a chain.
    This transformer returns every subchain with a certain length from every
    chain. Common ancester subchains are only returned once.
    For example, in the tree (1 (2 (3, 4))) and max_lenth=2, the subchain 1-2
    is only returned once, although it is part of both chains 1-2-3 and 1-2-4.

    input document: list of nltk.Tree objects (one for each sentence)

    output document: the format of the output documents depend on the
    combination parameters.




    """

    def __init__(
        self,
        max_length: int = None,
        combine_chain_elements: str = None,
        combine_chains: str = None,
        combine_strings: str = None,
    ):
        """
        Initialize class.

        Args:
            max_length (int): the maximum length of the produced chains.
                If set to None, full chains of any length will be returned.

        combine_chain_elements (str): if set to any string other than None,
                each chain will be returned as a string
                (e.g., "PRON VERB NOUN")
                instead of a list. The parameter is used to join the chains.
                Defaults to None.

        combine_chains (str|None):  if set to true, return each document as the
                concatenation of all chains for all trees in the document. If
                set to None, returns a list of sentences for each document,
                where each sentence consists of a list of chains. The parameter
                 is used to join the chains. Defaults to None.

        combine_strings (str|None): if set, it will be used to join the tree
                chains together to a single string per document. The parameter
                is used to join the chains. Defaults to None.
        """
        if combine_strings is not None and combine_chains is None:
            raise ValueError(
                "if combine_strings is set, both combine_chains and "
                "combine_chain_elementsmust be set too."
            )
        if combine_chains is not None and combine_chain_elements is None:
            raise ValueError(
                "if combine_chains is set, combine_chain_elements must be set " "too."
            )

        self.max_length = max_length
        self.combine_chain_elements = combine_chain_elements
        self.combine_chains = combine_chains
        self.combine_strings = combine_strings

    def fit(self, _x: Any, _y: Any = None) -> TreeChainTransformer:
        """Fit the model."""
        return self

    # please be careful, it is dangerous in here!
    def _find_chains(self, tree: nltk.Tree, prev_labels: List[str]) -> List[List[str]]:
        ret_full = []
        if isinstance(tree, str) or len(tree) == 0:
            # the leaf nodes of nltk trees are strings
            if not self.max_length or len(prev_labels) < self.max_length:
                ret_full.append(prev_labels[:])
            return ret_full
        if self.max_length and len(prev_labels) == self.max_length:
            # case: intermediary subchain that stops before the root
            prev_labels = prev_labels[1:]

        prev_labels.append(tree.label())
        if len(prev_labels) == self.max_length:
            # by adding this node, we have completed a subchain
            ret_full.append(prev_labels[:])
        for child in tree:
            ret_full += self._find_chains(child, prev_labels[:])
        return ret_full

    def transform(
        self, documents: List[List[nltk.Tree]], _y: Any = None
    ) -> Union[List[str], List[List[str]]]:
        """Transform the data."""
        result = []
        for document in documents:
            #  a document consists of a list of nltk.Tree objects
            #  one tree represents one sentence.
            new_document: Any = []
            for tree in document:
                #  every tree is split into a list of chains, whereas
                #  every chain is a list of symbols.
                chains: Any = self._find_chains(tree, [])

                if self.combine_chain_elements is not None:
                    chains = [self.combine_chain_elements.join(x) for x in chains]
                if self.combine_chains is not None:
                    new_document.append(self.combine_chains.join(chains))
                else:
                    new_document.append(chains)

            if self.combine_strings is not None:
                new_document = self.combine_strings.join(new_document)
            result.append(new_document)
        return result


def _get_average_height(document: List[nltk.Tree]) -> np.array:
    """Calculate the average height of all trees in a document."""
    return np.average([tree.height() for tree in document])


def _calculate_average_children(tree: nltk.Tree) -> List[int]:
    result = []
    if type(tree) != nltk.tree.Tree or not tree:
        result.append(0)
    else:
        result.append(len(tree))
        for child in tree:
            result += _calculate_average_children(child)
    return result


def _get_average_children(document: List[nltk.Tree]) -> np.array:
    result = []
    for tree in document:
        result += _calculate_average_children(tree)
    return np.average(result)


def _get_average_inner_to_leaf_ratio(document: List[nltk.Tree]) -> np.array:
    result = []
    for tree in document:
        num_leaves = len(tree.leaves())
        num_total = len(tree.treepositions()) - 1  # root node
        result.append(num_leaves / num_total)
    return np.average(result)


def _get_max_tree_width(tree: nltk.Tree) -> int:
    maximum = 0
    if type(tree) == nltk.tree.Tree:
        for child in tree:
            maximum = max(maximum, _get_max_tree_width(child), len(tree))
    return maximum


def _get_max_child_width(document: List[nltk.Tree]) -> np.array:
    result = []
    for tree in document:
        result.append(_get_max_tree_width(tree))
    return np.average(result)


class TreeStatsVectorizer(TransformerMixin, BaseEstimator):
    """
    Calculate high-level, low-complexity tree features.

    This transformer creates aggregated high-level features that are not
    dependent on the content of the tree.

    input: list of list of trees
    output: list of list of numbers/floats
    """

    def fit(self, _x: Any, _y: Any = None) -> TreeStatsVectorizer:
        """Fit the model."""
        return self

    def transform(self, x: List[List[nltk.Tree]], _y: Any = None) -> List[List[float]]:
        """Transform the data."""
        result = []
        for document in x:
            result.append(
                [
                    _get_average_height(document),
                    _get_average_children(document),
                    _get_average_inner_to_leaf_ratio(document),
                    _get_max_child_width(document),
                ]
            )
        return result


class TreeToStringTransformer(BaseEstimator, TransformerMixin):
    """
    Transforms nltk trees into strings that can be parsed later.

    input: list of list of trees
    output: list of list of strings
    """

    def fit(self, _x: Any, _y: Any = None) -> TreeToStringTransformer:
        """Fit the model."""
        return self

    def transform(self, x: List[List[nltk.Tree]], _y: Any = None) -> List[List[str]]:
        """Transform the data."""
        ret = []
        for document in x:
            doc = []
            for tree in document:
                doc.append(tree.pformat(margin=1000000))
            ret.append(doc)
        return ret


class TreeToFlatStringTransformer(TransformerMixin, BaseEstimator):
    """
    Transforms NLTK trees into Strings by traversing the tree post-order.

    Input: Every document is a list of NLTK trees, one representing each
        sentence.
    Output: Every document is a single string.
    """

    def fit(self, _x: Any, _y: Any = None) -> TreeToFlatStringTransformer:
        """Fit the model."""
        return self

    def parse(self, tree: nltk.Tree) -> str:
        """Convert a string to a NLTK tree."""
        result = [tree.label()]
        result += [self.parse(child) for child in tree]
        return " ".join(result)

    def transform(self, documents: List[List[nltk.Tree]]) -> List[str]:
        """Transform the data."""
        result = []
        for document in documents:
            parses = [self.parse(sentence) for sentence in document]
            result.append(". ".join(parses))
        return result
