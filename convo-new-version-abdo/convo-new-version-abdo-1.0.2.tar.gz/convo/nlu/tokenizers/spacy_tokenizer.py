import typing
from typing import Text, List, Any, Type, Optional

from convo.nlu.tokenizers.tokenizer import Tkn, Tokenizer
from convo.nlu.components import Element
from convo.nlu.utils.spacy_utils import SpacyNLP
from convo.shared.nlu.training_data.message import Msg

from convo.nlu.constants import SPACY_DOCUMENTS

if typing.TYPE_CHECKING:
    from spacy.tokens.doc import Doc  # pytype: disable=import-error


TAG_POS_KEY = "pos"


class SpacyTokenizer(Tokenizer):
    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [SpacyNLP]

    defaults = {
        # Flag to check whether to split convo_intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
        # Regular expression to detect tokens
        "token_pattern": None,
    }

    def get_documents(self, message: Msg, attribute: Text) -> Optional["Doc"]:
        return message.get(SPACY_DOCUMENTS[attribute])

    def tokenize(self, message: Msg, attribute: Text) -> List[Tkn]:
        documents = self.get_documents(message, attribute)
        if not documents:
            return []

        tkn = [
            Tkn(
                t.text, t.idx, lemma=t.lemma_, data={TAG_POS_KEY: self._label_of_tkn(t)}
            )
            for t in documents
            if t.text and t.text.strip()
        ]

        return self._token_apply_pattern(tkn)

    @staticmethod
    def _label_of_tkn(token: Any) -> Text:
        import spacy

        if spacy.about.__version__ > "2" and token._.has("tag"):
            return token._.get("tag")
        else:
            return token.tag_
