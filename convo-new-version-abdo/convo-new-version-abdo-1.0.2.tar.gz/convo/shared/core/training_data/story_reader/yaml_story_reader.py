import logging
from pathlib import Path
from typing import Dict, Text, List, Any, Optional, Union

import convo.shared.data
from convo.shared.exceptions import YamlExceptions 
import convo.shared.utils.io
from convo.shared.core.constants import LOOPNAME  
from convo.shared.nlu.constants import ENTITIES_NAME, KEY_INTENT_NAME
from convo.shared.nlu.training_data import entities_parser
import convo.shared.utils.validation

from convo.shared.constants import (
    INTENT_MSG_PREFIX ,
    STORIES_DOCUMENTS_URL,
    TEST_STORIES_FILES_PREFIX,
    RULES_DOCUMENTS_URL,
)

from convo.shared.core.constants import RULE_SNIPPET_ACTIONS_NAME   
from convo.shared.core.events import UserUttered, SetofSlot, OperationalLoop
from convo.shared.core.training_data.story_reader.story_reader import storyReviewer
from convo.shared.core.training_data.structures import StoryStage

log = logging.getLogger(__name__)

Key_Stories = "stories"
Key_Stories_Name = "story"
Key_Rules = "rules"
Key_Rules_Name = "rule"
Key_Steps = "steps"
ENTITIES_KEY = "entities"
KEY_USERS_INTENT = "intent"
KEY_USER_MSG = "user"
KEY_SLOTS_NAME = "slot_was_set"
KEY_SLOT_VALUES = "value"
KEY_CURRENT_ACTIVE_VALUE = "active_loop"
KEY_ACTIONS = "action"
KEY_CHECK_POINT = "checkpoint"
KEY_CHECK_POINT_SLOTS = "slot_was_set"
KEY_META_DATA = "metadata"
KEY_OR_RULE = "or"
KEY_RULE_CONDITIONS = "condition"
KEY_WAIT_FOR_USER_INPUT_AFTER_RULE = "wait_for_user_input"
KEY_RULE_FOR_CONVERSATION_BEGIN = "conversation_start"


CORE_SCHEMAS_FILE = "utils/schemas/stories.yml"


class YAMLStoryReviewer(storyReviewer):
    """Class that reads Core training data and rule data in YAML format."""

    @classmethod
    def from_reviewer(cls, reader: "YAMLStoryReviewer") -> "YAMLStoryReviewer":
        """Create a reader from another reader.

        Args:
            reader: Another reader.

        Returns:
            A new reader instance.
        """
        return cls(
            reader.domain,
            reader.template_variables,
            reader.use_e2e,
            reader.source_name,
            reader.is_used_for_conversion,
        )

    def readFromFile(self, filename: Union[Text, Path]) -> List[StoryStage]:
        """Read stories or rules from file.

        Args:
            filename: Path to the story/rule file.

        Returns:
            `StoryStage`s read from `filename`.
        """
        self.source_name = filename
        try:
            return self.reading_from_string(
                convo.shared.utils.io.read_file(
                    filename, convo.shared.utils.io.ENCODING_DEFAULT
                )
            )
        except YamlExceptions  as e:
            e.filename = filename
            raise e

    def reading_from_string(self, string: Text) -> List[StoryStage]:
        """Read stories or rules from a string.

        Args:
            string: Unprocessed YAML file content.

        Returns:
            `StoryStage`s read from `string`.
        """
        convo.shared.utils.validation.validating_yaml_schema(string, CORE_SCHEMAS_FILE)
        content_from_yaml = convo.shared.utils.io.reading_yaml(string)

        return self.reading_from_parsed_yaml(content_from_yaml)

    def reading_from_parsed_yaml(
        self, parsed_content: Dict[Text, Union[Dict, List]]
    ) -> List[StoryStage]:
        """Read stories from parsed YAML.

        Args:
            parsed_content: The parsed YAML as a dictionary.

        Returns:
            The parsed stories or rules.
        """

        if not convo.shared.utils.validation.validating_training_data_format_version(
            parsed_content, self.source_name
        ):
            return []

        for key, parser_class in {
            Key_Stories: StoryAnalyser,
            Key_Rules: RuleAnalyser,
        }.items():
            data = parsed_content.get(key) or []
            parser = parser_class.from_reviewer(self)
            parser.parse_data(data)
            self.story_steps.extend(parser.fetch_steps())

        return self.story_steps

    @classmethod
    def isStoriesFile(cls, file_path: Text) -> bool:
        """Check if file contains Core training data or rule data in YAML format.

        Args:
            file_path: Path of the file to check.

        Returns:
            `True` in case the file is a Core YAML training data or rule data file,
            `False` otherwise.

        Raises:
            YamlExceptions : if the file seems to be a YAML file (extension) but
                can not be read / parsed.
        """
        return convo.shared.data.is_yaml_file (file_path) and cls.is_key_in_yaml_data(
            file_path, Key_Stories, Key_Rules
        )

    @classmethod
    def is_key_in_yaml_data(cls, file_path: Text, *keys: Text) -> bool:
        """Check if all keys are contained in the parsed dictionary from a yaml file.

        Arguments:
            file_path: path to the yaml file
            keys: keys to look for

        Returns:
              `True` if all the keys are contained in the file, `False` otherwise.

        Raises:
            YamlExceptions : if the file seems to be a YAML file (extension) but
                can not be read / parsed.
        """
        content = convo.shared.utils.io.reading_yaml_file(file_path)
        return any(key in content for key in keys)

    @classmethod
    def has_test_prefix(cls, file_path: Text) -> bool:
        """Check if the filename of a file at a path has a certain prefix.

        Arguments:
            file_path: path to the file

        Returns:
            `True` if the filename starts with the prefix, `False` otherwise.
        """
        return Path(file_path).name.startswith(TEST_STORIES_FILES_PREFIX)

    @classmethod
    def isTestStoriesFile(cls, file_path: Union[Text, Path]) -> bool:
        """Checks if a file is a test conversations file.

        Args:
            file_path: Path of the file which should be checked.

        Returns:
            `True` if it's a conversation test file, otherwise `False`.
        """

        return cls.has_test_prefix(file_path) and cls.isStoriesFile(file_path)

    def fetch_steps(self) -> List[StoryStage]:
        self.addCurrentStoriesToResult()
        return self.story_steps

    def parse_data(self, data: List[Dict[Text, Any]]) -> None:
        item_title_name = self.fetch_item_title()

        for item in data:
            if not isinstance(item, dict):
                convo.shared.utils.io.raising_warning(
                    f"Unexpected block found in '{self.source_name}':\n"
                    f"{item}\nItems under the "
                    f"'{self.fetch_plural_item_title()}' key must be YAML "
                    f"dictionaries. It will be skipped.",
                    docs=self.get_documents_link(),
                )
                continue

            if item_title_name in item.keys():
                self.parsing_plain_item(item)

    def parsing_plain_item(self, item: Dict[Text, Any]) -> None:
        item__name = item.get(self.fetch_item_title(), "")

        if not item__name:
            convo.shared.utils.io.raising_warning(
                f"Issue found in '{self.source_name}': \n"
                f"{item}\n"
                f"The {self.fetch_item_title()} has an empty name. "
                f"{self.fetch_plural_item_title().capitalize()} should "
                f"have a name defined under '{self.fetch_item_title()}' "
                f"key. It will be skipped.",
                docs=self.get_documents_link(),
            )

        steps: List[Union[Text, Dict[Text, Any]]] = item.get(Key_Steps, [])

        if not steps:
            convo.shared.utils.io.raising_warning(
                f"Issue found in '{self.source_name}': "
                f"The {self.fetch_item_title()} has no steps. "
                f"It will be skipped.",
                docs=self.get_documents_link(),
            )
            return

        self.new_part(item__name, item)

        for step in steps:
            self.parse_step(step)

        self.closing_part(item)

    def new_part(self, item_name: Text, item: Dict[Text, Any]) -> None:
        raise NotImplementedError()

    def closing_part(self, item: Dict[Text, Any]) -> None:
        pass

    def parse_step(self, step: Union[Text, Dict[Text, Any]]) -> None:
        if isinstance(step, str):
            convo.shared.utils.io.raising_warning(
                f"Issue found in '{self.source_name}':\n"
                f"Found an unexpected step in the {self.fetch_item_title()} "
                f"description:\n{step}\nThe step is of type `str` "
                f"which is only allowed for the rule snippet action "
                f"'{RULE_SNIPPET_ACTIONS_NAME   }'. It will be skipped.",
                docs=self.get_documents_link(),
            )
        elif KEY_USERS_INTENT in step.keys() or KEY_USER_MSG in step.keys():
            self.parsing_user_utterance(step)
        elif KEY_OR_RULE in step.keys():
            self.parsing_or_statement(step)
        elif KEY_ACTIONS in step.keys():
            self.parsing_action(step)
        elif KEY_CHECK_POINT in step.keys():
            self.parsing_checkpoint(step)
        # This has to be after the checkpoint test as there can be a slot key within
        # a checkpoint.
        elif KEY_SLOTS_NAME in step.keys():
            self.parsing_slot(step)
        elif KEY_CURRENT_ACTIVE_VALUE in step.keys():
            self.parsing_active_loop(step[KEY_CURRENT_ACTIVE_VALUE])
        elif KEY_META_DATA in step.keys():
            pass
        else:
            convo.shared.utils.io.raising_warning(
                f"Issue found in '{self.source_name}':\n"
                f"Found an unexpected step in the {self.fetch_item_title()} "
                f"description:\n{step}\nIt will be skipped.",
                docs=self.get_documents_link(),
            )

    def fetch_item_title(self) -> Text:
        raise NotImplementedError()

    def fetch_plural_item_title(self) -> Text:
        raise NotImplementedError()

    def get_documents_link(self) -> Text:
        raise NotImplementedError()

    def parsing_user_utterance(self, step: Dict[Text, Any]) -> None:
        change = self.parsing_raw_user_utterance(step)
        if change:
            self.utterance_in_domain_validation(change)
            self.current_step_builder.addUserMessages([change])

    def utterance_in_domain_validation(self, utterance: UserUttered) -> None:
        name_of_intent = utterance.intent.get(KEY_INTENT_NAME)

        if not self.domain:
            log.debug(
                "Skipped validating if intent is in domain as domain " "is `None`."
            )
            return

        if name_of_intent not in self.domain.fetch_intents:
            convo.shared.utils.io.raising_warning(
                f"Issue found in '{self.source_name}': \n"
                f"Found intent '{name_of_intent}' in stories which is not part of the "
                f"domain.",
                docs=STORIES_DOCUMENTS_URL,
            )

    def parsing_or_statement(self, step: Dict[Text, Any]) -> None:
        changes = []

        for change in step.get(KEY_OR_RULE):
            if KEY_USERS_INTENT in change.keys():
                change = self.parsing_raw_user_utterance(change)
                if change:
                    changes.append(change)
            else:
                convo.shared.utils.io.raising_warning(
                    f"Issue found in '{self.source_name}': \n"
                    f"`OR` statement can only have '{KEY_USERS_INTENT}' "
                    f"as a sub-element. This step will be skipped:\n"
                    f"'{change}'\n",
                    docs=self.get_documents_link(),
                )
                return

        self.current_step_builder.addUserMessages(changes)

    def users_intent_from_step(self, step: Dict[Text, Any]) -> Text:
        uses_intent = step.get(KEY_USERS_INTENT, "").strip()

        if not uses_intent:
            convo.shared.utils.io.raising_warning(
                f"Issue found in '{self.source_name}':\n"
                f"User utterance cannot be empty. "
                f"This {self.fetch_item_title()} step will be skipped:\n"
                f"{step}",
                docs=self.get_documents_link(),
            )

        if uses_intent.startswith(INTENT_MSG_PREFIX ):
            convo.shared.utils.io.raising_warning(
                f"Issue found in '{self.source_name}':\n"
                f"User intent '{uses_intent}' starts with "
                f"'{INTENT_MSG_PREFIX }'. This is not required.",
                docs=self.get_documents_link(),
            )
            # Remove leading slash
            uses_intent = uses_intent[1:]
        return uses_intent

    def parsing_raw_user_utterance(self, step: Dict[Text, Any]) -> Optional[UserUttered]:
        from convo.shared.nlu.interpreter import RegexInterpreter

        name_of_intent = self.users_intent_from_step(step)
        intention = {"name": name_of_intent, "confidence": 1.0}

        if KEY_USER_MSG in step:
            user_msg = step[KEY_USER_MSG].strip()
            entities = entities_parser.search_entities_in_training_example(user_msg)
            plain_text = entities_parser.replacing_entities(user_msg)

            if plain_text.startswith(INTENT_MSG_PREFIX ):
                entities = (
                    RegexInterpreter().synch_parsing(plain_text).get(ENTITIES_NAME, [])
                )
        else:
            raw_entity = step.get(ENTITIES_KEY, [])
            entities = self.parse_raw_entity(raw_entity)
            # set plain_text to None because only intent was provided in the stories
            plain_text = None
        return UserUttered(plain_text, intention, entities)

    @staticmethod
    def parse_raw_entity(
        raw_entities: Union[List[Dict[Text, Text]], List[Text]]
    ) -> List[Dict[Text, Text]]:
        final_entity = []
        for entity in raw_entities:
            if isinstance(entity, dict):
                for key, value in entity.items():
                    final_entity.append({"entity": key, "value": value})
            else:
                final_entity.append({"entity": entity, "value": ""})

        return final_entity

    def parsing_slot(self, step: Dict[Text, Any]) -> None:

        for slot in step.get(KEY_CHECK_POINT_SLOTS, []):
            if isinstance(slot, dict):
                for key, value in slot.items():
                    self.addEvent(SetofSlot.type_name, {key: value})
            elif isinstance(slot, str):
                self.addEvent(SetofSlot.type_name, {slot: None})
            else:
                convo.shared.utils.io.raising_warning(
                    f"Issue found in '{self.source_name}':\n"
                    f"Invalid slot: \n{slot}\n"
                    f"Items under the '{KEY_CHECK_POINT_SLOTS}' key must be "
                    f"YAML dictionaries or Strings. The checkpoint will be skipped.",
                    docs=self.get_documents_link(),
                )
                return

    def parsing_action(self, step: Dict[Text, Any]) -> None:

        actions_name = step.get(KEY_ACTIONS, "")
        if not actions_name:
            convo.shared.utils.io.raising_warning(
                f"Issue found in '{self.source_name}': \n"
                f"Action name cannot be empty. "
                f"This {self.fetch_item_title()} step will be skipped:\n"
                f"{step}",
                docs=self.get_documents_link(),
            )
            return

        self.addEvent(actions_name, {})

    def parsing_active_loop(self, active_loop_name: Optional[Text]) -> None:
        self.addEvent(OperationalLoop.type_name, {LOOPNAME  : active_loop_name})

    def parsing_checkpoint(self, step: Dict[Text, Any]) -> None:

        check_point_name = step.get(KEY_CHECK_POINT, "")
        slots_name= step.get(KEY_CHECK_POINT_SLOTS, [])

        slots_dictionary = {}

        for slot in slots_name:
            if not isinstance(slot, dict):
                convo.shared.utils.io.raising_warning(
                    f"Issue found in '{self.source_name}':\n"
                    f"Inspection '{check_point_name}' has an invalid slot: "
                    f"{slots_name}\nItems under the '{KEY_CHECK_POINT_SLOTS}' key must be "
                    f"YAML dictionaries. The checkpoint will be skipped.",
                    docs=self.get_documents_link(),
                )
                return

            for key, value in slot.items():
                slots_dictionary[key] = value

        self._add_checkpoint(check_point_name, slots_dictionary)


class StoryAnalyser(YAMLStoryReviewer):
    """Encapsulate story-specific parser behavior."""

    def new_part(self, item_name: Text, item: Dict[Text, Any]) -> None:
        self.newStoryPart(item_name, self.source_name)

    def fetch_item_title(self) -> Text:
        return Key_Stories_Name

    def fetch_plural_item_title(self) -> Text:
        return Key_Stories

    def get_documents_link(self) -> Text:
        return STORIES_DOCUMENTS_URL


class RuleAnalyser(YAMLStoryReviewer):
    """Encapsulate rule-specific parser behavior."""

    def new_part(self, item_name: Text, item: Dict[Text, Any]) -> None:
        self.newRulePart(item_name, self.source_name)
        condition = item.get(KEY_RULE_CONDITIONS, [])
        self.parsing_rule_conditions(condition)
        if not item.get(KEY_RULE_FOR_CONVERSATION_BEGIN):
            self.parsing_rule_snippet_action()

    def parsing_rule_conditions(
        self, conditions: List[Union[Text, Dict[Text, Any]]]
    ) -> None:
        self._is_parsing_conditions = True
        for condition in conditions:
            self.parse_step(condition)
        self._is_parsing_conditions = False

    def closing_part(self, item: Dict[Text, Any]) -> None:
        if item.get(KEY_WAIT_FOR_USER_INPUT_AFTER_RULE) is False:
            self.parsing_rule_snippet_action()

    def fetch_item_title(self) -> Text:
        return Key_Rules_Name

    def fetch_plural_item_title(self) -> Text:
        return Key_Rules

    def get_documents_link(self) -> Text:
        return RULES_DOCUMENTS_URL

    def parsing_rule_snippet_action(self) -> None:
        self.addEvent(RULE_SNIPPET_ACTIONS_NAME   , {})
