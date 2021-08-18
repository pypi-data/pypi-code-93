from collections import OrderedDict
from pathlib import Path
from typing import Any, Dict, List, Text, Union, Optional

from ruamel import yaml
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarstring import DoubleQuotedScalarString, LiteralScalarString

import convo.shared.utils.io
import convo.shared.core.constants
from convo.shared.constants import TRAINING_DATA_LATEST_FORMAT_VERSION 
from convo.shared.core.events import (  # pytype: disable=pyi-error
    UserUttered,
    ActionExecuted,
  SetofSlot,
    OperationalLoop,
    Event,
)

from convo.shared.core.training_data.story_reader.yaml_story_reader import (  # pytype: disable=pyi-error
    Key_Stories,
    Key_Stories_Name,
    KEY_USERS_INTENT,
    ENTITIES_KEY,
    KEY_ACTIONS,
    Key_Steps,
    KEY_CHECK_POINT,
    KEY_SLOTS_NAME,
    KEY_CHECK_POINT_SLOTS,
    KEY_OR_RULE,
    KEY_USER_MSG,
    KEY_CURRENT_ACTIVE_VALUE,
    Key_Rules,
    KEY_RULE_FOR_CONVERSATION_BEGIN,
    KEY_WAIT_FOR_USER_INPUT_AFTER_RULE,
    KEY_RULE_CONDITIONS,
    Key_Rules_Name,
)

from convo.shared.core.training_data.story_writer.story_writer import StoryWriter
from convo.shared.core.training_data.structures import (
    StoryStage,
    Inspection,
    storyStart,
    RuleStage,
)


class YAMLStoryAuthor(StoryWriter):
    """Writes Core training data into a file in a YAML format. """

    def data_dumps(
        self,
        story_steps: List[StoryStage],
        is_appendable: bool = False,
        is_test_story: bool = False,
    ) -> Text:
        """Turns Story steps into an YAML string.

        Args:
            story_steps: Original story steps to be converted to the YAML.
            is_appendable: Specify if result should not contain
                           high level keys/definitions and can be appended to
                           the existing story file.
            is_test_story: Identifies if the stories should be exported in test stories
                           format.
        Returns:
            String with story steps in the YAML format.
        """
        data_stream = yaml.StringIO()
        self.dump(data_stream, story_steps, is_appendable, is_test_story)
        return data_stream.getvalue()

    def dump(
        self,
        target: Union[Text, Path, yaml.StringIO],
        story_steps: List[StoryStage],
        is_appendable: bool = False,
        is_test_story: bool = False,
    ) -> None:
        """Writes Story steps into a target file/stream.

        Args:
            target: name of the target file/stream to write the YAML to.
            story_steps: Original story steps to be converted to the YAML.
            is_appendable: Specify if res should not contain
                           high level keys/definitions and can be appended to
                           the existing story file.
            is_test_story: Identifies if the stories should be exported in test stories
                           format.
        """
        res = self.story_to_yaml(story_steps, is_test_story)
        if is_appendable and Key_Stories in res:
            res = res[Key_Stories]

        convo.shared.utils.io.writing_yaml(res, target, True)

    def story_to_yaml(
        self, story_steps: List[StoryStage], is_test_story: bool = False
    ) -> Dict[Text, Any]:
        """Converts a sequence of story steps into yaml format.

        Args:
            story_steps: Original story steps to be converted to the YAML.
        """
        from convo.shared.utils.validation import KEY_TRAINING_DATA_FORMAT_VER

        self._is_test_story = is_test_story

        story = []
        protocol = []
        for story_step in story_steps:
            if isinstance(story_step, RuleStage):
                protocol.append(self.processing_rule_step(story_step))
            else:
                story.append(self.processing_story_step(story_step))

        res = OrderedDict()
        res[KEY_TRAINING_DATA_FORMAT_VER] = DoubleQuotedScalarString(
            TRAINING_DATA_LATEST_FORMAT_VERSION
        )

        if story:
            res[Key_Stories] = story
        if protocol:
            res[Key_Rules] = protocol
        return res

    def processing_story_step(self, story_step: StoryStage) -> OrderedDict:
        """Converts a single story step into an ordered dict.

        Args:
            story_step: A single story step to be converted to the dict.

        Returns:
            Dict with a story step.
        """
        result = OrderedDict()
        result[Key_Stories_Name] = story_step.block_name
        steps = self.process_check_points(story_step.start_checkpoints)

        for event in story_step.events:
            if not self.filter_event(event):
                continue
            processed = self.processing_event(event)
            if processed:
                steps.append(processed)

        steps.extend(self.process_check_points(story_step.end_checkpoints))

        result[Key_Steps] = steps

        return result

    def processing_event(self, event: Event) -> Optional[OrderedDict]:
        if isinstance(event, list):
            return self.process_or_utterance(event)
        if isinstance(event, UserUttered):
            return self.processing_user_utterance(event, self._is_test_story)
        if isinstance(event, ActionExecuted):
            return self.processing_action(event)
        if isinstance(event, SetofSlot):
            return self.processing_slot(event)
        if isinstance(event, OperationalLoop):
            return self.processing_active_loop(event)
        return None

    @staticmethod
    def story_contain_loops(stories: List[StoryStage]) -> bool:
        """Checks if the stories contain at least one active loop.

        Args:
            stories: Stories steps.

        Returns:
            `True` if the `stories` contain at least one active loop.
            `False` otherwise.
        """
        return any(
            [
                [event for event in story_step.events if isinstance(event, OperationalLoop)]
                for story_step in stories
            ]
        )

    @staticmethod
    def text_is_real_msg(user_utterance: UserUttered) -> bool:
        return (
            not user_utterance.intent
            or user_utterance.text != user_utterance.as_story_string()
        )

    @staticmethod
    def processing_user_utterance(
        user_utterance: UserUttered, is_test_story: bool = False
    ) -> OrderedDict:
        """Converts a single user utterance into an ordered dict.

        Args:
            user_utterance: Original user utterance object.
            is_test_story: Identifies if the user utterance should be added
                           to the final YAML or not.

        Returns:
            Dict with a user utterance.
        """
        res = CommentedMap()
        res[KEY_USERS_INTENT] = user_utterance.intent["name"]

        if hasattr(user_utterance, "inline_comment"):
            res.yaml_add_eol_comment(
                user_utterance.in_line_comment(), KEY_USERS_INTENT
            )

        if (
            is_test_story
            and YAMLStoryAuthor.text_is_real_msg(user_utterance)
            and user_utterance.text
        ):
            res[KEY_USER_MSG] = LiteralScalarString(user_utterance.text)

        if len(user_utterance.entities):
            entities = []
            for entity in user_utterance.entities:
                if entity["value"]:
                    entities.append(OrderedDict([(entity["entity"], entity["value"])]))
                else:
                    entities.append(entity["entity"])
            res[ENTITIES_KEY] = entities

        return res

    @staticmethod
    def processing_action(action: ActionExecuted) -> Optional[OrderedDict]:
        """Converts a single action into an ordered dict.

        Args:
            action: Original action object.

        Returns:
            Dict with an action.
        """
        if action.action_name == convo.shared.core.constants.RULE_SNIPPET_ACTIONS_NAME   :
            return None

        res = CommentedMap()
        res[KEY_ACTIONS] = action.action_name

        if hasattr(action, "inline_comment"):
            res.yaml_add_eol_comment(action.in_line_comment(), KEY_ACTIONS)

        return res

    @staticmethod
    def processing_slot(event: SetofSlot):
        """Converts a single `SetofSlot` event into an ordered dict.

        Args:
            event: Original `SetofSlot` event.

        Returns:
            Dict with an `SetofSlot` event.
        """
        return OrderedDict([(KEY_SLOTS_NAME, [{event.key: event.value}])])

    @staticmethod
    def process_check_points(checkpoints: List[Inspection]) -> List[OrderedDict]:
        """Converts checkpoints event into an ordered dict.

        Args:
            checkpoints: List of original checkpoint.

        Returns:
            List of converted checkpoints.
        """
        res = []
        for checkpoint in checkpoints:
            if checkpoint.name == storyStart:
                continue
            next_check_point = OrderedDict([(KEY_CHECK_POINT, checkpoint.name)])
            if checkpoint.conditions:
                next_check_point[KEY_CHECK_POINT_SLOTS] = [
                    {key: value} for key, value in checkpoint.conditions.items()
                ]
            res.append(next_check_point)
        return res

    def process_or_utterance(self, utterances: List[UserUttered]) -> OrderedDict:
        """Converts user utterance containing the `OR` statement.

        Args:
            utterances: User utterances belonging to the same `OR` statement.

        Returns:
            Dict with converted user utterances.
        """
        return OrderedDict(
            [
                (
                    KEY_OR_RULE,
                    [
                        self.processing_user_utterance(utterance, self._is_test_story)
                        for utterance in utterances
                    ],
                )
            ]
        )

    @staticmethod
    def processing_active_loop(event: OperationalLoop) -> OrderedDict:
        """Converts OperationalLoop event into an ordered dict.

        Args:
            event: OperationalLoop event.

        Returns:
            Converted event.
        """
        return OrderedDict([(KEY_CURRENT_ACTIVE_VALUE, event.name)])

    def processing_rule_step(self, rule_step: RuleStage) -> OrderedDict:
        """Converts a RuleStage into an ordered dict.

        Args:
            rule_step: RuleStage object.

        Returns:
            Converted rule step.
        """
        res = OrderedDict()
        res[Key_Rules_Name] = rule_step.block_name

        conditional_steps = []
        conditional_events = rule_step.getRulesCondition()
        for event in conditional_events:
            processed = self.processing_event(event)
            if processed:
                conditional_steps.append(processed)
        if conditional_steps:
            res[KEY_RULE_CONDITIONS] = conditional_steps

        normal_event = rule_step.getRulesEvents()
        if normal_event and not (
            isinstance(normal_event[0], ActionExecuted)
            and normal_event[0].action_name
            == convo.shared.core.constants.RULE_SNIPPET_ACTIONS_NAME   
        ):
            res[KEY_RULE_FOR_CONVERSATION_BEGIN] = True

        normal_step = []
        for event in normal_event:
            processed = self.processing_event(event)
            if processed:
                normal_step.append(processed)
        if normal_step:
            res[Key_Steps] = normal_step

        if len(normal_event) > 1 and (
            isinstance(normal_event[len(normal_event) - 1], ActionExecuted)
            and normal_event[len(normal_event) - 1].action_name
            == convo.shared.core.constants.RULE_SNIPPET_ACTIONS_NAME   
        ):
            res[KEY_WAIT_FOR_USER_INPUT_AFTER_RULE] = False

        return res
