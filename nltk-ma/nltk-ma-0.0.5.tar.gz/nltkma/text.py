# Natural Language Toolkit: Texts
#
# Copyright (C) 2001-2021 NLTK Project
# Author: Steven Bird <stevenbird1@gmail.com>
#         Edward Loper <edloper@gmail.com>
# URL: <http://nltk.org/>
# For license information, see LICENSE.TXT

"""
This module brings together a variety of NLTK functionality for
text analysis, and provides simple, interactive interfaces.
Functionality includes: concordancing, collocation discovery,
regular expression search over tokenized strings, and
distributional similarity.
"""
from collections import namedtuple
from nltkma.util import map_cleaned_corpus
from nltkma.collocations import BigramCollocationFinder
from nltkma.probability import FreqDist

ConcordanceLine = namedtuple(
    "ConcordanceLine",
    ["left_context", "left_span", "query", "right_span", "right_context", "left_print", "right_print", "line",
     "collocation", "dist"],
)

def join_punctuation(seq, characters='.,;?!'):
    characters = set(characters)
    seq = iter(seq)
    current = next(seq)

    for nxt in seq:
        if nxt in characters:
            current += nxt
        else:
            yield current
            current = nxt

    yield current

def find_concordance(pivot_tokens, target_tokens, span, context, original_tokens, cleaned_tokens, tokens_no_stamming, allow_self_reference,
                     ignore_punctuation, tokens_are_lowercase):
    """
    Find all concordance lines given the query word.

    Provided with a list of words, these will be found as a phrase.
    """

    b = BigramCollocationFinder.from_words(pivot_tokens, target_tokens, cleaned_tokens, span, allow_self_reference, )

    index_mapping = map_cleaned_corpus(original_tokens, tokens_no_stamming,tokens_are_lowercase)
    # Find the instances of the word to create the ConcordanceLine
    concordance_list = []

    for collocation in b.pos:
        for i in range(len(b.pos[collocation])):
            pos = b.pos[collocation][i]
            query_word = cleaned_tokens[pos]

            # Find the context of query word.
            # i- context = contex left span
            context_left_exists = True
            context_right_exists = True

            left_span = original_tokens[max(0, max(0,index_mapping[pos]- span[0])): index_mapping[pos]]

            try:
                right_span = original_tokens[
                             min(len(original_tokens)-1, index_mapping[pos] + 1):
                             min(len(original_tokens)-1,index_mapping[pos + 1]+ span[1])]
            except IndexError:
                right_span = original_tokens[
                             min(len(original_tokens) - 1, index_mapping[pos] + 1):
                             len(original_tokens)]
                context_right_exists = False

            if ignore_punctuation:
                try:
                    index = left_span.index('.')
                    left_span = left_span[:max(0,index + 1)]
                    context_left_exists = False
                except ValueError:
                    pass

                try:
                    index = right_span.index('.')
                    right_span = right_span[:min(len(right_span)-1,index + 1)]
                    context_right_exists = False
                except ValueError:
                    pass

            # get additional context

            if pos - span[0] > 0 and context_left_exists:
                try:
                    left_context = original_tokens[
                                   max(0,max(0, index_mapping[pos - span[0]] - context[0])): index_mapping[max(0,pos - span[0])]]
                except IndexError:
                    left_context = original_tokens[max(0, original_tokens[0]): index_mapping[pos - span[0]]]
            else:
                left_context = []
            if pos + span[1] < len(original_tokens) - 1 and context_right_exists:
                try:
                    right_context = original_tokens[
                                    index_mapping[min(len(original_tokens),pos + span[1]) + 1]:
                                    min(len(original_tokens),index_mapping[pos + span[1]]+context[1]+2)]
                except IndexError:
                    right_context = original_tokens[
                                    index_mapping[min(len(original_tokens), pos + span[1])] + 1:
                                    len(original_tokens)]
            else:
                right_context = []

            if ignore_punctuation:
                try:
                    index = left_context.index('.')
                    left_context = left_context[:max(0,index + 1)]
                except ValueError:
                    pass

                try:
                    index = right_context.index('.')
                    right_context = right_context[:min(len(right_context),index + 1)]
                except ValueError:
                    pass

            # Create the pretty lines with the query_word in the middle.
            left_span_print = " ".join(left_span)
            right_span_print = " ".join(right_span)

            if context_left_exists:
                left_context_print = " ".join(left_context)
            else:
                left_context_print = " "

            if context_right_exists:
                right_context_print = " ".join(right_context)
            else:
                right_context_print = " "

            left_print = " ".join([left_context_print, left_span_print])
            right_print = " ".join([right_span_print, right_context_print])
            # The WYSIWYG line of the concordance.
            line_print = " ".join([left_print, query_word, right_print])

            coll_fd = FreqDist()
            coll_fd[collocation] = b.ngram_fd[collocation]

            word_fd = FreqDist()
            word_fd[collocation[0]] = b.word_fd[collocation[0]]
            word_fd[collocation[1]] = b.word_fd[collocation[1]]

            b_line = BigramCollocationFinder(word_fd,coll_fd,b.pos,b.dist,b.window_size)


            # Create the ConcordanceLine
            concordance_line = ConcordanceLine(
                left_context_print,
                left_span_print,
                query_word,
                right_span_print,
                right_context_print,
                left_print,
                right_print,
                line_print,
                b_line,
                b.dist[collocation][i]

            )
            concordance_list.append(concordance_line)
    return concordance_list
