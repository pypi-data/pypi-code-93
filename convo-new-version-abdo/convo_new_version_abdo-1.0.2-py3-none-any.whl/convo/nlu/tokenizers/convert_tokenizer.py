from typing import Any, Dict, List, Optional, Text

from convo.core.utils import get_dict_hash
from convo.nlu.constants import SUB_TOKENS_NUM
from convo.nlu.model import Metadataset
from convo.nlu.tokenizers.tokenizer import Tkn
from convo.nlu.tokenizers.whitespace_tokenizer import WhitespaceTokenizer
from convo.shared.nlu.training_data.message import Msg
from convo.utils import common
import convo.utils.train_utils as train_utils
import tensorflow as tf


TF_MODULE_URL_HUB_ = (
    "https://github.com/PolyAI-LDN/polyai-models/releases/download/v1.0/model.tar.gz"
)


class ConveRTTokenizer(WhitespaceTokenizer):
    """Tokenizer using ConveRT model.
    Loads the ConveRT(https://github.com/PolyAI-LDN/polyai-models#convert)
    model from TFHub and computes sub-word tokens for dense
    featurizable attributes of each message object.
    """

    defaults = {
        # Flag to check whether to split convo_intents
        "intent_tokenization_flag": False,
        # Symbol on which intent should be split
        "intent_split_symbol": "_",
        # Regular expression to detect tokens
        "token_pattern": None,
        # Remote URL of hosted model
        "model_url": TF_MODULE_URL_HUB_,
    }

    def __init__(self, component_config: Dict[Text, Any] = None) -> None:
        """Construct a new tokenizer using the WhitespaceTokenizer framework."""

        super().__init__(component_config)

        self.model_url = self.component_config.get("model_url", TF_MODULE_URL_HUB_)

        self.module = train_utils.tf_hub_model_loaded(self.model_url)

        self.tokenize_signature = self.module.signatures["tokenize"]

    @classmethod
    def cache_key(
        cls, component_meta: Dict[Text, Any], model_metadata: Metadataset
    ) -> Optional[Text]:
        _configuration = common.updating_existing_keys(cls.defaults, component_meta)
        return f"{cls.name}-{get_dict_hash(_configuration)}"

    def context_provide(self) -> Dict[Text, Any]:
        return {"tf_hub_module": self.module}

    def _token(self, sentence: Text) -> Any:

        return self.tokenize_signature(tf.convert_to_tensor([sentence]))[
            "default"
        ].numpy()

    def tokenizer(self, message: Msg, attribute: Text) -> List[Tkn]:
        """Tokenize the text using the ConveRT model.
        ConveRT adds a special char in front of (some) words and splits words into
        sub-words. To ensure the entity start and end values matches the token values,
        tokenize the text first using the whitespace tokenizer. If individual tokens
        are split up into multiple tokens, add this information to the
        respected tokens.
        """

        # perform whitespace tokenization
        in_token = super().tokenize(message, attribute)

        outer_token = []

        for token in in_token:
            # use ConveRT model to tokenize the text
            tkn_split_str = self._token(token.text)[0]

            # clean tokens (remove special chars and empty tokens)
            tkn_split_str = self._fresh_token(tkn_split_str)

            token.put(SUB_TOKENS_NUM, len(tkn_split_str))

            outer_token.append(token)

        return outer_token

    @staticmethod
    def _fresh_token(tkn: List[bytes]) -> List[Text]:
        """Encode tokens and remove special char added by ConveRT."""

        tkn = [string.decode("utf-8").replace("﹏", "") for string in tkn]
        return [string for string in tkn if string]
