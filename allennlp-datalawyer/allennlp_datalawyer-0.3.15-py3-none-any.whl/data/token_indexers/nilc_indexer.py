from typing import Dict, List
import itertools, re

from overrides import overrides

from allennlp.data.vocabulary import Vocabulary
from allennlp.data.tokenizers import Token
from allennlp.data.token_indexers.token_indexer import TokenIndexer, IndexedTokenList

# Punctuation list
punctuations = re.escape('!"#%\'()*+,./:;<=>?@[\\]^_`{|}~')

# ##### #
# Regex #
# ##### #
re_remove_brackets = re.compile(r'\{.*\}')
re_remove_html = re.compile(r'<(\/|\\)?.+?>', re.UNICODE)
re_transform_numbers = re.compile(r'\d', re.UNICODE)
re_transform_doc_ids = re.compile(r'\d', re.UNICODE)
re_transform_emails = re.compile(r'[^\s]+@[^\s]+', re.UNICODE)
re_transform_url = re.compile(r'(http|https)://[^\s]+', re.UNICODE)
# Different quotes are used.
re_quotes_1 = re.compile(r"(?u)(^|\W)[‘’′`']", re.UNICODE)
re_quotes_2 = re.compile(r"(?u)[‘’`′'](\W|$)", re.UNICODE)
re_quotes_3 = re.compile(r'(?u)[‘’`′“”]', re.UNICODE)
re_dots = re.compile(r'(?<!\.)\.\.(?!\.)', re.UNICODE)
re_punctuation = re.compile(r'([,";:]){2},', re.UNICODE)
re_hiphen = re.compile(r' -(?=[^\W\d_])', re.UNICODE)
re_tree_dots = re.compile(u'…', re.UNICODE)
# Differents punctuation patterns are used.
re_changehyphen = re.compile(u'–')
re_doublequotes_1 = re.compile(r'(\"\")')
re_doublequotes_2 = re.compile(r'(\'\')')
re_trim = re.compile(r' +', re.UNICODE)


@TokenIndexer.register("nilc_indexer")
class NILCTokenIndexer(TokenIndexer):
    """
    This :class:`TokenIndexer` represents tokens as single integers.

    Parameters
    ----------
    namespace : ``str``, optional (default=``tokens``)
        We will use this namespace in the :class:`Vocabulary` to map strings to indices.
    lowercase_tokens : ``bool``, optional (default=``False``)
        If ``True``, we will call ``token.lower()`` before getting an index for the token from the
        vocabulary.
    start_tokens : ``List[str]``, optional (default=``None``)
        These are prepended to the tokens provided to ``tokens_to_indices``.
    end_tokens : ``List[str]``, optional (default=``None``)
        These are appended to the tokens provided to ``tokens_to_indices``.
    token_min_padding_length : ``int``, optional (default=``0``)
        See :class:`TokenIndexer`.
    """
    # pylint: disable=no-self-use
    def __init__(self,
                 namespace: str = 'tokens',
                 nilc_preprocess: bool = True,
                 start_tokens: List[str] = None,
                 end_tokens: List[str] = None,
                 token_min_padding_length: int = 0) -> None:
        super().__init__(token_min_padding_length)
        self.namespace = namespace
        self.nilc_preprocess = nilc_preprocess

        self._start_tokens = [Token(st) for st in (start_tokens or [])]
        self._end_tokens = [Token(et) for et in (end_tokens or [])]

    def clean_text(self, text):
        """Apply all regex above to a given string."""
        text = text.lower()
        text = text.replace('\xa0', ' ')
        text = re_tree_dots.sub('...', text)
        text = re.sub('\.\.\.', '', text)
        text = re_remove_brackets.sub('', text)
        text = re_changehyphen.sub('-', text)
        text = re_remove_html.sub(' ', text)
        text = re_transform_numbers.sub('0', text)
        text = re_transform_url.sub('URL', text)
        text = re_transform_emails.sub('EMAIL', text)
        text = re_quotes_1.sub(r'\1"', text)
        text = re_quotes_2.sub(r'"\1', text)
        text = re_quotes_3.sub('"', text)
        text = re.sub('"', '', text)
        text = re_dots.sub('.', text)
        text = re_punctuation.sub(r'\1', text)
        text = re_hiphen.sub(' - ', text)
        text = re_doublequotes_1.sub('\"', text)
        text = re_doublequotes_2.sub('\'', text)
        text = re_trim.sub(' ', text)
        return text.strip()

    @overrides
    def count_vocab_items(self, token: Token, counter: Dict[str, Dict[str, int]]):
        # If `text_id` is set on the token (e.g., if we're using some kind of hash-based word
        # encoding), we will not be using the vocab for this token.
        if getattr(token, 'text_id', None) is None:
            text = token.text
            if self.nilc_preprocess:
                text = self.clean_text(text)
            counter[self.namespace][text] += 1

    @overrides
    def tokens_to_indices(self,
                          tokens: List[Token],
                          vocabulary: Vocabulary) -> IndexedTokenList:
        indices: List[int] = []

        for token in itertools.chain(self._start_tokens, tokens, self._end_tokens):
            if getattr(token, 'text_id', None) is not None:
                # `text_id` being set on the token means that we aren't using the vocab, we just use
                # this id instead.
                indices.append(token.text_id)
            else:
                text = token.text
                if self.nilc_preprocess:
                    text = self.clean_text(text)
                indices.append(vocabulary.get_token_index(text, self.namespace))

        return {"tokens": indices}

    @overrides
    def get_empty_token_list(self) -> IndexedTokenList:
        return {"tokens": []}