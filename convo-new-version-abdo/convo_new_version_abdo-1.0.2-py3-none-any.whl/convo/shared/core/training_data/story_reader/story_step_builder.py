import logging
from typing import Text, Optional, Dict, Any, List

import convo.shared.core.training_data.structures
import convo.shared.utils.io
from convo.shared.constants import STORIES_DOCUMENTS_URL
from convo.shared.core.events import UserUttered, Event
from convo.shared.core.training_data.structures import (
    Inspection,
    generatedCheckpointPrefix,
    generatedHashLength,
    storyStart,
    StoryStage,
    RuleStage,
)

log = logging.getLogger(__name__)


class StoryStageBuilder:
    def __init__(
        self, name: Text, source_name: Optional[Text], is_rule: bool = False
    ) -> None:
        self.name = name
        self.source_name = source_name
        self.story_steps = []
        self.current_steps = []
        self.start_checkpoints = []
        self.is_rule = is_rule

    def addCheckpoint(self, name: Text, conditions: Optional[Dict[Text, Any]]) -> None:

        # Depending on the state of the story part this
        # is either a start or an end check point
        if not self.current_steps:
            self.start_checkpoints.append(Inspection(name, conditions))
        else:
            if conditions:
                convo.shared.utils.io.raising_warning(
                    f"End or intermediate checkpoints "
                    f"do not support conditions! "
                    f"(checkpoint: {name})",
                    docs=STORIES_DOCUMENTS_URL + "#checkpoints",
                )
            additionalSteps = []
            for t in self.current_steps:
                if t.end_checkpoints:
                    tcp = t.createCopy(use_new_id=True)
                    tcp.end_checkpoints = [Inspection(name)]
                    additionalSteps.append(tcp)
                else:
                    t.end_checkpoints = [Inspection(name)]
            self.current_steps.extend(additionalSteps)

    def prevEndCheckpoints(self) -> List[Inspection]:
        if not self.current_steps:
            return self.start_checkpoints
        else:
            # makes sure we got each end name only once
            endNames = {e.name for s in self.current_steps for e in s.end_checkpoints}
            return [Inspection(name) for name in endNames]

    def addUserMessages(
        self, messages: List[UserUttered], is_used_for_conversion: bool = False
    ) -> None:
        """Adds next story steps with the user's utterances.

        Args:
            messages: User utterances.
            is_used_for_conversion: Identifies if the user utterance is a part of
              OR statement. This parameter is used only to simplify the conversation
              from MD story files. Don't use it others ways, because it ends up
              in a invalid story that cannot be user for real training.
              Default value is `False`, which preserves the expected behavior
              of the reader.
        """
        self.esureCurrentSteps()

        if len(messages) == 1:
            # If there is only one possible intent, we'll keep things simple
            for t in self.current_steps:
                t.addUserMessage(messages[0])
        else:
            # this simplifies conversion between formats, but breaks the logic
            if is_used_for_conversion:
                for t in self.current_steps:
                    t.addEvents(messages)
                return

            # If there are multiple different convo_intents the
            # user can use the express the same thing
            # we need to copy the blocks and create one
            # copy for each possible message
            affix = generatedCheckpointPrefix + "OR_"
            generatedCheckpoint = convo.shared.core.training_data.structures.generateId(
                affix, generatedHashLength
            )
            updatedSteps = []
            for t in self.current_steps:
                for m in messages:
                    cloned = t.createCopy(use_new_id=True)
                    cloned.addUserMessage(m)
                    cloned.end_checkpoints = [Inspection(generatedCheckpoint)]
                    updatedSteps.append(cloned)
            self.current_steps = updatedSteps

    def addEventAsCondition(self, event: Event) -> None:
        self.addEvent(event, True)

    def addEvent(self, event, is_condition: bool = False) -> None:
        self.esureCurrentSteps()
        for t in self.current_steps:
            # conditions are supported only for the RuleSteps
            if isinstance(t, RuleStage) and is_condition:
                t.addEventAsCondition(event)
            else:
                t.addEvent(event)

    def esureCurrentSteps(self) -> None:
        finished = [step for step in self.current_steps if step.end_checkpoints]
        unFinished = [step for step in self.current_steps if not step.end_checkpoints]
        self.story_steps.extend(finished)
        if unFinished:
            self.current_steps = unFinished
        else:
            self.current_steps = self.nextStorySteps()

    def clean(self) -> None:
        if self.current_steps:
            self.story_steps.extend(self.current_steps)
            self.current_steps = []

    def nextStorySteps(self) -> List[StoryStage]:
        startCheckpoints = self.prevEndCheckpoints()
        if not startCheckpoints:
            startCheckpoints = [Inspection(storyStart)]
        stepClass = RuleStage if self.is_rule else StoryStage
        currentTurns = [
            stepClass(
                block_name=self.name,
                start_checkpoints=startCheckpoints,
                source_name=self.source_name,
            )
        ]
        return currentTurns
