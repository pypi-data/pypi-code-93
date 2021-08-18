import os
import logging
import re
from typing import Any, Dict, Optional, Text

from convo.shared.constants import COMPONENTS_DOCUMENTS_URL
from convo.nlu import utils
from convo.nlu.classifiers.classifier import IntentionClassifier
from convo.shared.nlu.constants import INTENTION, TXT
import convo.shared.utils.io
from convo.nlu.config import ConvoNLUModelConfiguration
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.training_data.message import Msg
from convo.nlu.model import Metadataset

log = logging.getLogger(__name__)


class KeywordIntentClassifier(IntentionClassifier):
    """Intent classifier using simple keyword matching.


    The classifier takes a list of keywords and associated convo_intents as an input.
    An input sentence is checked for the keywords and the intent is returned.

    """

    defaults = {"case_sensitive": True}

    def __init__(
        self,
        component_config: Optional[Dict[Text, Any]] = None,
        intent_keyword_map: Optional[Dict] = None,
    ) -> None:

        super(KeywordIntentClassifier, self).__init__(component_config)

        self.case_sensitive = self.component_config.get("case_sensitive")
        self.intent_keyword_map = intent_keyword_map or {}

    def train(
        self,
        training_data: TrainingDataSet,
        config: Optional[ConvoNLUModelConfiguration] = None,
        **kwargs: Any,
    ) -> None:

        duplicate_eg = set()
        for ex in training_data.intent_exp:
            if (
                ex.get(TXT) in self.intent_keyword_map.keys()
                and ex.get(INTENTION) != self.intent_keyword_map[ex.get(TXT)]
            ):
                duplicate_eg.add(ex.get(TXT))
                convo.shared.utils.io.raising_warning(
                    f"Keyword '{ex.get(TXT)}' is a keyword to trigger intent "
                    f"'{self.intent_keyword_map[ex.get(TXT)]}' and also "
                    f"intent '{ex.get(INTENTION)}', it will be removed "
                    f"from the list of keywords for both of them. "
                    f"Remove (one of) the duplicates from the training data.",
                    docs=COMPONENTS_DOCUMENTS_URL + "#keyword-intent-classifier",
                )
            else:
                self.intent_keyword_map[ex.get(TXT)] = ex.get(INTENTION)
        for keyword in duplicate_eg:
            self.intent_keyword_map.pop(keyword)
            log.debug(
                f"Removed '{keyword}' from the list of keywords because it was "
                "a keyword for more than one intent."
            )

        self._verify_keyword_map()

    def _verify_keyword_map(self) -> None:
        repeat_flag = 0 if self.case_sensitive else re.IGNORECASE

        maping_ambiguous = []
        for keyword1, intent1 in self.intent_keyword_map.items():
            for keyword2, intent2 in self.intent_keyword_map.items():
                if (
                    re.search(r"\b" + keyword1 + r"\b", keyword2, flags=repeat_flag)
                    and intent1 != intent2
                ):
                    maping_ambiguous.append((intent1, keyword1))
                    convo.shared.utils.io.raising_warning(
                        f"Keyword '{keyword1}' is a keyword of intent '{intent1}', "
                        f"but also a substring of '{keyword2}', which is a "
                        f"keyword of intent '{intent2}."
                        f" '{keyword1}' will be removed from the list of keywords.\n"
                        f"Remove (one of) the conflicting keywords from the"
                        f" training data.",
                        docs=COMPONENTS_DOCUMENTS_URL + "#keyword-intent-classifier",
                    )
        for intent, keyword in maping_ambiguous:
            self.intent_keyword_map.pop(keyword)
            log.debug(
                f"Removed keyword '{keyword}' from intent '{intent}' because it matched a "
                "keyword of another intent."
            )

    def process(self, message: Msg, **kwargs: Any) -> None:
        get_intent_name = self._keyword_to_intent_mapping(message.get(TXT))

        confident = 0.0 if get_intent_name is None else 1.0
        intentions = {"name": get_intent_name, "confidence": confident}

        if message.get(INTENTION) is None or intentions is not None:
            message.put(INTENTION, intentions, add_to_output=True)

    def _keyword_to_intent_mapping(self, text: Text) -> Optional[Text]:
        repeat_flag = 0 if self.case_sensitive else re.IGNORECASE

        for keyword, intent in self.intent_keyword_map.items():
            if re.search(r"\b" + keyword + r"\b", text, flags=repeat_flag):
                log.debug(
                    f"KeywordClassifier matched keyword '{keyword}' to"
                    f" intent '{intent}'."
                )
                return intent

        log.debug("KeywordClassifier did not find any keywords in the message.")
        return None

    def persist(self, filename: Text, model_dir: Text) -> Dict[Text, Any]:
        """Persist this model into the passed dir.

        Return the metadata necessary to load the model again.
        """

        filename = filename + ".json"
        file_keyword = os.path.join(model_dir, filename)
        utils.write_json_to_file(file_keyword, self.intent_keyword_map)

        return {"file": filename}

    @classmethod
    def load(
        cls,
        meta: Dict[Text, Any],
        model_dir: Optional[Text] = None,
        model_metadata: Metadataset = None,
        cached_component: Optional["KeywordIntentClassifier"] = None,
        **kwargs: Any,
    ) -> "KeywordIntentClassifier":

        if model_dir and meta.get("file"):
            filename = meta.get("file")
            file_keyword = os.path.join(model_dir, filename)
            if os.path.exists(file_keyword):
                mapping_intent_keyword = convo.shared.utils.io.reading_json_file(file_keyword)
            else:
                convo.shared.utils.io.raising_warning(
                    f"Failed to load key word file for `IntentKeywordClassifier`, "
                    f"maybe {file_keyword} does not exist?"
                )
                mapping_intent_keyword = None
            return cls(meta, mapping_intent_keyword)
        else:
            raise Exception(
                f"Failed to load keyword intent classifier model. "
                f"Path {os.path.abspath(meta.get('file'))} doesn't exist."
            )
