import json
import logging
import re
from json.decoder import JSONDecodeError
from typing import Text, Optional, Dict, Any, Union, List, Tuple

import convo.shared
from convo.shared.core.trackers import DialogueStateTracer
from convo.shared.constants import INTENT_MSG_PREFIX , STORIES_DOCUMENTS_URL
from convo.shared.nlu.constants import KEY_INTENT_NAME
from convo.shared.nlu.training_data.message import Msg


log = logging.getLogger(__name__)


class NaturalLangInterpreter:
    async def parse(
        self,
        text: Text,
        message_id: Optional[Text] = None,
        tracker: Optional[DialogueStateTracer] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[Text, Any]:
        raise NotImplementedError(
            "Interpreter needs to be able to parse messages into structured output."
        )
    def featurize_msg(self, message: Msg) -> Optional[Msg]:
        pass


class RegexInterpreter(NaturalLangInterpreter):

    @staticmethod
    def prefixes_allowed() -> Text:
        return INTENT_MSG_PREFIX

    @staticmethod
    def creating_entities(
        parsed_entities: Dict[Text, Union[Text, List[Text]]], sidx: int, eidx: int
    ) -> List[Dict[Text, Any]]:
        entities = []
        for k, sv in parsed_entities.items():
            if not isinstance(sv, list):
                sv = [sv]
            for value in sv:
                entities.append(
                    {
                        "entity": k,
                        "start": sidx,
                        "end": eidx,  # can't be more specific
                        "value": value,
                    }
                )
        return entities

    @staticmethod
    def parse_params(
        entity_str: Text, sidx: int, eidx: int, user_input: Text
    ) -> List[Dict[Text, Any]]:
        if entity_str is None or not entity_str.strip():
            # if there is nothing to parse we will directly exit
            return []
        try:
            parsed_entity = json.loads(entity_str)
            if isinstance(parsed_entity, dict):
                return RegexInterpreter.creating_entities(parsed_entity, sidx, eidx)
            else:
                raise ValueError(
                    f"Parsed value isn't a json object "
                    f"(instead parser found '{type(parsed_entity)}')"
                )
        except (JSONDecodeError, ValueError) as e:
            convo.shared.utils.io.raising_warning(
                f"Failed to parse arguments in line "
                f"'{user_input}'. Failed to decode parameters "
                f"as a json object. Make sure the intent "
                f"is followed by a proper json object. "
                f"Error: {e}",
                docs=STORIES_DOCUMENTS_URL,
            )
            return []

    @staticmethod
    def parsed_confidence(confidence_str: Text) -> float:
        if confidence_str is None:
            return 1.0
        try:
            return float(confidence_str.strip()[1:])
        except ValueError as e:
            convo.shared.utils.io.raising_warning(
                f"Invalid to parse confidence value in line "
                f"'{confidence_str}'. Make sure the intent confidence is an "
                f"@ followed by a decimal number. "
                f"Error: {e}",
                docs=STORIES_DOCUMENTS_URL,
            )
            return 0.0

    def begins_with_intent_prefix(self, text: Text) -> bool:
        for c in self.prefixes_allowed():
            if text.startswith(c):
                return True
        return False

    @staticmethod
    def intent_and_entities_extraction(
        user_input: Text,
    ) -> Tuple[Optional[Text], float, List[Dict[Text, Any]]]:
        """Parse the user input using regexes to extract intent & entities."""
        appended_prefixes = re.escape(RegexInterpreter.prefixes_allowed())
        # the regex matches "slot{"a": 1}"
        n = re.search("^[" + appended_prefixes + "]?([^{@]+)(@[0-9.]+)?([{].+)?", user_input)
        if n is not None:
            interpreter_event_name = n.group(1).strip()
            conf = RegexInterpreter.parsed_confidence(n.group(2))
            entities = RegexInterpreter.parse_params(
                n.group(3), n.start(3), n.end(3), user_input
            )

            return interpreter_event_name, conf, entities
        else:
            log.warning(f"Failed to parse intent end entities from '{user_input}'.")
            return None, 0.0, []

    async def parse(
        self,
        text: Text,
        message_id: Optional[Text] = None,
        tracker: Optional[DialogueStateTracer] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict[Text, Any]:
        """Parse a text message."""

        return self.synch_parsing(text)

    def synch_parsing(self, text: Text) -> Dict[Text, Any]:
        """Parse a text message."""

        intention, conf, entities = self.intent_and_entities_extraction(text)

        if self.begins_with_intent_prefix(text):
            msg_text = text
        else:
            msg_text = INTENT_MSG_PREFIX + text

        return {
            "text": msg_text,
            "intent": {KEY_INTENT_NAME: intention, "conf": conf},
            "intent_ranking": [{KEY_INTENT_NAME: intention, "conf": conf}],
            "entities": entities,
        }
