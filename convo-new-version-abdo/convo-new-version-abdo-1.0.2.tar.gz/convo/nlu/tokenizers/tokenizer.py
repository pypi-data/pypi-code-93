import logging
import re

from typing import Text, List, Optional, Dict, Any

from convo.nlu.config import ConvoNLUModelConfiguration
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.components import Element
from convo.nlu.constants import NAMES_OF_TOKENS, MSG_ATTRS
from convo.shared.nlu.constants import (
    INTENTION,
    KEY_INTENT_RESPONSE,
    RESP_IDENTIFIER_DELIMITER,
    ACT_NAME,
)

log = logging.getLogger(__name__)


class Tkn:
    def __init__(
        self,
        text: Text,
        start: int,
        end: Optional[int] = None,
        data: Optional[Dict[Text, Any]] = None,
        lemma: Optional[Text] = None,
    ) -> None:
        self.text = text
        self.start = start
        self.end = end if end else start + len(text)

        self.data = data if data else {}
        self.lemma = lemma or text

    def set(self, prop: Text, info: Any) -> None:
        self.data[prop] = info

    def get(self, prop: Text, default: Optional[Any] = None) -> Any:
        return self.data.get(prop, default)

    def __eq__(self, others):
        if not isinstance(others, Tkn):
            return NotImplemented
        return (self.start, self.end, self.text, self.lemma) == (
            others.start,
            others.end,
            others.text,
            others.lemma,
        )

    def __lt__(self, others):
        if not isinstance(others, Tkn):
            return NotImplemented
        return (self.start, self.end, self.text, self.lemma) < (
            others.start,
            others.end,
            others.text,
            others.lemma,
        )


class Tokenizer(Element):
    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        # flag to check whether to split convo_intents
        self.intent_tokenization_flag = self.component_config.get(
            "intent_tokenization_flag", False
        )
        # split symbol for convo_intents
        self.intent_split_symbol = self.component_config.get("intent_split_symbol", "_")
        # token pattern to further split tokens
        pattern_tkn = self.component_config.get("pattern_tkn", None)
        self.token_pattern_regex = None
        if pattern_tkn:
            self.token_pattern_regex = re.compile(pattern_tkn)

    def tokenize(self, message: Msg, attribute: Text) -> List[Tkn]:
        """Tokenizes the text of the provided attribute of the incoming message."""

        raise NotImplementedError

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:
        """Tokenize all training data."""

        for example in training_data.training_examples:
            for attribute in MSG_ATTRS:
                if (
                    example.get(attribute) is not None
                    and not example.get(attribute) == ""
                ):
                    if attribute in [INTENTION, ACT_NAME, KEY_INTENT_RESPONSE]:
                        token = self._spliting_name(example, attribute)
                    else:
                        token = self.tokenize(example, attribute)
                    example.put(NAMES_OF_TOKENS[attribute], token)

    def process(self, message: Msg, **kwargs: Any) -> None:
        """Tokenize the incoming message."""
        for attribute in MSG_ATTRS:
            if isinstance(message.get(attribute), str):
                if attribute in [INTENTION, ACT_NAME, RESP_IDENTIFIER_DELIMITER]:
                    tokens = self._spliting_name(message, attribute)
                else:
                    tokens = self.tokenize(message, attribute)

                message.put(NAMES_OF_TOKENS[attribute], tokens)

    def _spliting_tokenizer_on_symbol(self, text: Text) -> List[Text]:

        word = (
            text.split(self.intent_split_symbol)
            if self.intent_tokenization_flag
            else [text]
        )

        return word

    def _spliting_name(self, message: Msg, attribute: Text = INTENTION) -> List[Tkn]:
        txt = message.get(attribute)

        # for KEY_INTENT_RESPONSE attribute,
        # first split by RESP_IDENTIFIER_DELIMITER
        if attribute == KEY_INTENT_RESPONSE:
            token_intent, resp_key = txt.split(RESP_IDENTIFIER_DELIMITER)
            word = self._spliting_tokenizer_on_symbol(
                token_intent
            ) + self._spliting_tokenizer_on_symbol(resp_key)

        else:
            word = self._spliting_tokenizer_on_symbol(txt)

        return self._convert_to_word_tkns(word, txt)

    def _token_apply_pattern(self, tokens: List[Tkn]) -> List[Tkn]:
        """Apply the token pattern to the given tokens.

        Args:
            tokens: list of tokens to split

        Returns:
            List of tokens.
        """
        if not self.token_pattern_regex:
            return tokens

        token_final = []
        for token in tokens:
            token_new = self.token_pattern_regex.findall(token.text)
            token_new = [t for t in token_new if t]

            if not token_new:
                token_final.append(token)

            run_off_set = 0
            for new_token in token_new:
                off_set_word = token.text.index(new_token, run_off_set)
                length_word = len(new_token)
                run_off_set = off_set_word + length_word
                token_final.append(
                    Tkn(
                        new_token,
                        token.start + off_set_word,
                        data=token.data,
                        lemma=token.lemma,
                    )
                )

        return token_final

    @staticmethod
    def _convert_to_word_tkns(words: List[Text], text: Text) -> List[Tkn]:
        run_off_set = 0
        token = []

        for word in words:
            off_set_word = text.index(word, run_off_set)
            length_word = len(word)
            run_off_set = off_set_word + length_word
            token.append(Tkn(word, off_set_word))

        return token
