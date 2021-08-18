from typing import Any, Dict, List, Text

import regex
import re

import convo.shared.utils.io
from convo.shared.constants import COMPONENTS_DOCUMENTS_URL
from convo.nlu.tokenizers.tokenizer import Tkn, Tokenizer
from convo.shared.nlu.training_data.message import Msg


class WhitespaceTokenizer(Tokenizer):

    defaults = {
        # Flag to check whether to split convo_intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
        # Regular expression to detect tokens
        "token_pattern": None,
    }

    # the following language should not be tokenized using the WhitespaceTokenizer
    not_supported_language_list = ["zh", "ja", "th"]

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        self.emoji_pattern = self.fetch_emoji_regular_expression()

        if "case_sensitive" in self.component_config:
            convo.shared.utils.io.raising_warning(
                "The option 'case_sensitive' was moved from the tokenizers to the "
                "featurizers.",
                docs=COMPONENTS_DOCUMENTS_URL,
            )

    @staticmethod
    def fetch_emoji_regular_expression():
        return re.compile(
            "["
            "\U0001F600-\U0001F64F"  # emoticons
            "\U0001F300-\U0001F5FF"  # symbols & pictographs
            "\U0001F680-\U0001F6FF"  # transport & map symbols
            "\U0001F1E0-\U0001F1FF"  # flags (iOS)
            "\U00002702-\U000027B0"
            "\U000024C2-\U0001F251"
            "\u200d"  # zero width joiner
            "\u200c"  # zero width non-joiner
            "]+",
            flags=re.UNICODE,
        )

    def delete_emoticon(self, text: Text) -> Text:
        """Remove emoji if the full text, aka token, matches the emoji regex."""
        matched = self.emoji_pattern.fullmatch(text)

        if matched is not None:
            return ""

        return text

    def tokenize(self, message: Msg, attribute: Text) -> List[Tkn]:
        txt = message.get(attribute)

        # we need to use regex instead of re, because of
        # https://stackoverflow.com/questions/12746458/python-unicode-regular-expression-matching-failing-with-some-unicode-characters

        # remove 'not a word character' if
        word = regex.sub(
            # there is a space or an end of a string after it
            r"[^\w#@&]+(?=\s|$)|"
            # there is a space or beginning of a string before it
            # not followed by a number
            r"(\s|^)[^\w#@&]+(?=[^0-9\s])|"
            # not in between numbers and not . or @ or & or - or #
            # e.g. 10'000.00 or blabla@gmail.com
            # and not url characters
            r"(?<=[^0-9\s])[^\w._~:/?#\[\]()@!$&*+,;=-]+(?=[^0-9\s])",
            " ",
            txt,
        ).split()

        word = [self.delete_emoticon(w) for w in word]
        word = [w for w in word if w]

        # if we removed everything like smiles `:)`, use the whole txt as 1 token
        if not word:
            word = [txt]

        token = self._convert_to_word_tkns(word, txt)

        return self._token_apply_pattern(token)
