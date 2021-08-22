#!/usr/bin/env python3

from collections import Counter
import re

from bs4 import BeautifulSoup

import spacy
from spacy.tokenizer import Tokenizer
from spacy.lang.en import English

__nlp = English()
__tokenizer = Tokenizer(__nlp.vocab)

def set_nlp(custom_nlp):
    """
        By default this module uses `spacy.lang.en.English()` for its nlp.
        If you'd like to use a custom module, for example:
        spacy.load("en_core_web_lg")
        You can set it here.
    """
    global __nlp, __tokenizer
    __nlp = custom_nlp
    __tokenizer = Tokenizer(custom_nlp.vocab)


def simple_tokenize(doc):
    """
        Takes a document and returns a list of tokens (simplified lowercase words).
        This version of the method assumes the doc is already relatively clean
        and will not handle html tags or extraneous characters.

        @type doc: str
        @rtype: List[str]
    """
    return [
        re.sub(r"[^a-z0-9]", "", t.lemma_.lower()).strip() for t in __tokenizer(doc)
        if not t.is_stop and not t.is_punct and t.text.strip()
    ]


def html_tokenize(doc):
    """
        Takes a document and returns a list of tokens (simplified lowercase words).

        @type doc: str
        @rtype: List[str]
    """
    stripped = " ".join(BeautifulSoup(doc).stripped_strings)
    return simple_tokenize(stripped)


class Scrubber:
    """
        Tokenizes text and optionally removes words that are above or below a certain
        threshold.
    """

    def __init__(self, no_below=0.05, no_above=0.95):
        """
            Inits the object.

            @type no_below: int or float, tokens that appear less frequently than this will
                be discarded.
                If it is a float it will be taken as a percentage, if it is an int it will be taken as the total count.
            @type no_above: int or float, tokens that appear more frequently than this
                will be discarded.
                If it is a float it will be taken as a percentage, if it is an int it will be taken as the total count.
        """
        assert isinstance(no_below, (float, int))
        assert isinstance(no_above, (float, int))

        self.__counter = None

        if type(no_below) is int:
            self.__min_count = no_below
            self.__min_pct = 0.0
        else:
            self.__min_count = 0
            self.__min_pct = no_below

        if type(no_above) is int:
            self.__max_count = no_above
            self.__max_pct = 1.0
        else:
            self.__max_count = 2**31-1
            self.__max_pct = no_above


    def fit_transform(self, docs):
        """
            Trains on and then transforms text.

            @type docs: List[str]
            @rtype: List[List[str]]
        """
        cleaned = self.__fit(docs)
        return self.__transform(cleaned)


    def transform(self, docs):
        """
            Applies transformation.
            Throws an error if Scrubber.fit() was not
            run prior to this.

            @type docs: List[str]
            @rtype: List[List[str]]
        """
        cleaned = [simple_tokenize(doc) for doc in docs]
        return self.__transform(cleaned)


    def fit(self, docs):
        """
            Trains the scrubber. Makes no changes to the text.

            @type docs: List[str]
        """
        self.__fit(docs)


    def __transform(self, cleaned):
        """
            Private utility method.
        """
        total = len(cleaned)
        vocab = set()
        for word, count in  self.__counter.items():
            if count < self.__min_count or self.__max_count < count:
                continue
            pct = count/total
            if pct < self.__min_pct or self.__max_pct < pct:
                continue
            vocab.add(word)

        return [[s for s in doc if s in vocab]
                for doc in cleaned if doc]


    def __fit(self, docs):
        """
            Private utility method.
        """
        cleaned = [simple_tokenize(doc) for doc in docs]

        self.__counter = Counter()
        [self.__counter.update(s) for s in cleaned]
        return cleaned
