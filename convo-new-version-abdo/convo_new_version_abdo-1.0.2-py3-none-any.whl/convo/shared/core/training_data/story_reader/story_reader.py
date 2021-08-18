import logging
from typing import Optional, Dict, Text, List, Any

import convo.shared.utils.common
import convo.shared.utils.io
from convo.shared.constants import NEXT_MAJOR_DEPRECATION_VERSION
from convo.shared.core.constants import (
    DEACTIVATE_LOOP_LEGACY_ACTION_NAME  ,
    DEACTIVATE_LOOP_ACTION_NAME  ,
)
from convo.shared.core.domain import Domain
from convo.shared.core.events import SetofSlot, ActionExecuted, Event
from convo.shared.exceptions import CoreException 
from convo.shared.core.training_data.story_reader.story_step_builder import (
    StoryStageBuilder,
)
from convo.shared.core.training_data.structures import StoryStage

log = logging.getLogger(__name__)


class storyReviewer:
    """Helper class to read a story file."""

    def __init__(
        self,
        domain: Optional[Domain] = None,
        template_vars: Optional[Dict] = None,
        use_e2e: bool = False,
        source_name: Optional[Text] = None,
        is_used_for_conversion: bool = False,
    ) -> None:
        """Constructor for the storyReviewer.

        Args:
            domain: Domain object.
            template_vars: Template variables to be replaced.
            use_e2e: Specifies whether to use the e2e parser or not.
            source_name: Name of the training data source.
            is_used_for_conversion: Identifies if the user utterances should be parsed
              (entities are extracted and removed from the original text) and
              OR statements should be unfolded . This parameter is used only to
              simplify the conversation from MD story files. Don't use it others ways,
              because it ends up in a invalid story that cannot be user for real
              training. Default value is `False`, which preserves the expected behavior
              of the reader.
        """
        self.story_steps = []
        self.current_step_builder: Optional[StoryStageBuilder] = None
        self.domain = domain
        self.template_variables = template_vars if template_vars else {}
        self.use_e2e = use_e2e
        self.source_name = source_name
        self.is_used_for_conversion = is_used_for_conversion
        self._is_parsing_conditions = False

    def readFromFile(self, filename: Text) -> List[StoryStage]:
        raise NotImplementedError

    @staticmethod
    def isTestStoriesFile(filename: Text) -> bool:
        """Checks if the specified file is a test story file.

        Args:
            filename: File to check.

        Returns:
            `True` if specified file is a test story file, `False` otherwise.
        """
        raise NotImplementedError

    @staticmethod
    def isStoriesFile(filename: Text) -> bool:
        """Checks if the specified file is a story file.

        Args:
            filename: File to check.

        Returns:
            `True` if specified file is a story file, `False` otherwise.
        """
        raise NotImplementedError

    def addCurrentStoriesToResult(self):
        if self.current_step_builder:
            self.current_step_builder.clean()
            self.story_steps.extend(self.current_step_builder.story_steps)

    def newStoryPart(self, name: Text, source_name: Optional[Text]):
        self.addCurrentStoriesToResult()
        self.current_step_builder = StoryStageBuilder(name, source_name)

    def newRulePart(self, name: Text, source_name: Optional[Text]):
        self.addCurrentStoriesToResult()
        self.current_step_builder = StoryStageBuilder(name, source_name, is_rule=True)

    def addEvent(self, event_name: Text, parameters: Dict[Text, Any]) -> None:
        # add 'name' only if event is not a SetofSlot,
        # because there might be a slot with slot_key='name'
        if "name" not in parameters and event_name != SetofSlot.type_name:
            parameters["name"] = event_name

        parsedEvents = Event.from_story_str(
            event_name, parameters, default=ActionExecuted
        )
        if parsedEvents is None:
            raise StoryAnalysedError(
                "Unknown event '{}'. It is Neither an event "
                "nor an action).".format(event_name)
            )
        if self.current_step_builder is None:
            raise StoryAnalysedError(
                "Failed to handle event '{}'. There is no "
                "started story block available. "
                "".format(event_name)
            )

        for p in parsedEvents:
            mapLegacyEventNames(p)
            if self._is_parsing_conditions:
                self.current_step_builder.addEventAsCondition(p)
            else:
                self.current_step_builder.addEvent(p)

    def addCheckpoint(
        self, name: Text, conditions: Optional[Dict[Text, Any]]
    ) -> None:

        # Ensure story part already has a name
        if not self.current_step_builder:
            raise StoryAnalysedError(
                "Inspection '{}' is at an invalid location. "
                "Expected a story start.".format(name)
            )

        self.current_step_builder.addCheckpoint(name, conditions)


def mapLegacyEventNames(event: Event) -> None:
    if (
        isinstance(event, ActionExecuted)
        and event.action_name == DEACTIVATE_LOOP_LEGACY_ACTION_NAME
    ):
        convo.shared.utils.io.rasing_deprecate_warning(
            f"Using action '{event.action_name}' is deprecated. Please use "
            f"'{DEACTIVATE_LOOP_ACTION_NAME  }' instead. Support for "
            f"'{event.action_name}' will be removed in Convo Open Source version "
            f"{NEXT_MAJOR_DEPRECATION_VERSION}."
        )
        event.action_name = DEACTIVATE_LOOP_ACTION_NAME


class StoryAnalysedError(CoreException , ValueError):
    """Raised if there is an error while parsing a story file."""

    def __init__(self, message) -> None:
        self.message = message
        super(StoryAnalysedError, self).__init__()
