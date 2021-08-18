from typing import List, Text

from convo.nlu.tokenizers.tokenizer import Tkn, Tokenizer
from convo.shared.nlu.training_data.message import Msg

from convo.shared.utils.io import ENCODING_DEFAULT


class Mitie_Tokenized(Tokenizer):

    defaults = {
        # Flag to check whether to split convo_intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
        # Regular expression to detect tokens
        "token_pattern": None,
    }

    @classmethod
    def req_package(cls) -> List[Text]:
        return ["mitie"]

    def tokenize(self, message: Msg, attribute: Text) -> List[Tkn]:
        import mitie

        txt = message.get(attribute)

        sentence_encode = txt.encode(ENCODING_DEFAULT)
        tokenize = mitie.tokenize_with_offsets(sentence_encode)
        token = [
            self._tkn_from_off_set(token, offset, sentence_encode)
            for token, offset in tokenize
        ]

        return self._token_apply_pattern(token)

    def _tkn_from_off_set(
        self, text: bytes, offset: int, encoded_sentence: bytes
    ) -> Tkn:
        return Tkn(
            text.decode(ENCODING_DEFAULT),
            self._byte_char_to_offset(encoded_sentence, offset),
        )

    @staticmethod
    def _byte_char_to_offset(text: bytes, byte_offset: int) -> int:
        return len(text[:byte_offset].decode(ENCODING_DEFAULT))
