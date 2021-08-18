from typing import Text, List, Any, Dict, Type

from convo.nlu.tokenizers.tokenizer import Tkn, Tokenizer
from convo.nlu.components import Element
from convo.nlu.utils.hugging_face.hf_transformers import HF_Transformers_NLP
from convo.shared.nlu.training_data.message import Msg

from convo.nlu.constants import LANG_MODEL_DOCUMENTS, TKNS


class Lang_Model_Tokenizer(Tokenizer):
    """Tokenizer using transformer based language models.

    Uses the output of HF_Transformers_NLP component to set the tokens
    for dense featurizable attributes of each message object.
    """

    @classmethod
    def required_components(cls) -> List[Type[Element]]:
        return [HF_Transformers_NLP]

    defaults = {
        # Flag to check whether to split convo_intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
    }

    def get_documents(self, message: Msg, attribute: Text) -> Dict[Text, Any]:
        return message.get(LANG_MODEL_DOCUMENTS[attribute])

    def tokenize(self, message: Msg, attribute: Text) -> List[Tkn]:
        documents = self.get_documents(message, attribute)

        return documents[TKNS]
