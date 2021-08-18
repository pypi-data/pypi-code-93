import logging
from collections import defaultdict
from typing import Set, Text, Optional

import convo.core.training.story_conflict
import convo.shared.nlu.constants
from convo.shared.constants import (
    DOCUMENTS_BASE_URL,
    DOMAIN_DOCUMENTS_URL,
    CONVO_UTTER_PREFIX ,
    ACTIONS_DOCUMENTS_URL,
)
from convo.shared.core.domain import Domain
from convo.shared.core.events import ActionExecuted
from convo.shared.core.events import UserUttered
from convo.shared.core.generator import TrainingDataSetGenerator
from convo.shared.core.training_data.structures import StoryPlot
from convo.shared.importers.importer import TrainingDataImporter
from convo.shared.nlu.training_data.training_data import TrainingDataSet
import convo.shared.utils.io

logger = logging.getLogger(__name__)


class Validate:
    """A class used to verify usage of convo_intents and utterances."""

    def __init__(
        self, domain: Domain, convo_intents: TrainingDataSet, story_graph: StoryPlot
    ) -> None:
        """Initializes the Validate object. """

        self.domain = domain
        self.convo_intents = convo_intents
        self.story_graph = story_graph

    @classmethod
    async def importers(cls, importer: TrainingDataImporter) -> "Validate":
        """Create an instance from the domain, nlu and story files."""

        domain = await importer.domain()
        story_graph = await importer.fetch_stories()
        convo_intents = await importer.fetch_nlu_data()

        return cls(domain, convo_intents, story_graph)

    def intents_verification(self, ignore_warnings: bool = True) -> bool:
        """Compares list of intents in domain with intents in NLU training data."""

        all_is_right = True

        nlu_data_convo_intents = {e.data["intent"] for e in self.convo_intents.intent_exp}

        for intent in self.domain.fetch_intents:
            if intent not in nlu_data_convo_intents:
                logger.debug(
                    f"The intent '{intent}' is listed in the domain file, but "
                    f"is not found in the NLU training data."
                )
                all_is_right = ignore_warnings and all_is_right

        for intent in nlu_data_convo_intents:
            if intent not in self.domain.fetch_intents:
                convo.shared.utils.io.raising_warning(
                    f"There is a message in the training data labeled with intent "
                    f"'{intent}'. This intent is not listed in your domain. You "
                    f"should need to add that intent to your domain file!",
                    docs=DOMAIN_DOCUMENTS_URL,
                )
                all_is_right = False

        return all_is_right

    def eg_repetition_in_intents_verification(
        self, ignore_warnings: bool = True
    ) -> bool:
        """Checks if there is no duplicated example in different convo_intents."""

        everything_is_alright = True

        duplication_hash = defaultdict(set)
        for example in self.convo_intents.intent_exp:
            text = example.get(convo.shared.nlu.constants.TXT)
            duplication_hash[text].add(example.get("intent"))

        for text, convo_intents in duplication_hash.items():

            if len(duplication_hash[text]) > 1:
                everything_is_alright = ignore_warnings and everything_is_alright
                convo_intents_string = ", ".join(sorted(convo_intents))
                convo.shared.utils.io.raising_warning(
                    f"The example '{text}' was found labeled with multiple "
                    f"different convo_intents in the training data. Each annotated message "
                    f"should only appear with one intent. You should fix that "
                    f"conflict The example is labeled with: {convo_intents_string}."
                )
        return everything_is_alright

    def intents_in_story_verification(self, ignore_warnings: bool = True) -> bool:
        """Checks intents used in stories.

        Verifies if the convo_intents used in the stories are valid, and whether
        all valid convo_intents are used in the stories."""

        everything_is_alright = self.intents_verification(ignore_warnings)

        stories_convo_intents = {
            event.intent["name"]
            for story in self.story_graph.story_steps
            for event in story.events
            if type(event) == UserUttered
        }

        for story_intent in stories_convo_intents:
            if story_intent not in self.domain.fetch_intents:
                convo.shared.utils.io.raising_warning(
                    f"The intent '{story_intent}' is used in your stories, but it "
                    f"is not listed in the domain file. You should add it to your "
                    f"domain file!",
                    docs=DOMAIN_DOCUMENTS_URL,
                )
                everything_is_alright = False

        for intent in self.domain.fetch_intents:
            if intent not in stories_convo_intents:
                logger.debug(f"The intent '{intent}' is not used in any story.")
                everything_is_alright = ignore_warnings and everything_is_alright

        return everything_is_alright

    def _gather_utterance_activity(self) -> Set[Text]:
        """Return all utterances which are actions."""

        responses = {
            response.split(convo.shared.nlu.constants.RESP_IDENTIFIER_DELIMITER)[0]
            for response in self.convo_intents.responses.keys()
        }
        return responses | {
            utterance
            for utterance in self.domain.templates.keys()
            if utterance in self.domain.action_names
        }

    def utterances_verification(self, ignore_warnings: bool = True) -> bool:
        """Compares list of utterances in actions with utterances in responses."""

        actions = self.domain.action_names
        utterance_templates = set(self.domain.templates)
        everything_is_alright = True

        for utterance in utterance_templates:
            if utterance not in actions:
                logger.debug(
                    f"The utterance '{utterance}' is not listed under 'actions' in the "
                    f"domain file. It can only be used as a template."
                )
                everything_is_alright = ignore_warnings and everything_is_alright

        for action in actions:
            if action.startswith(CONVO_UTTER_PREFIX ):
                if action not in utterance_templates:
                    convo.shared.utils.io.raising_warning(
                        f"There is no template for the utterance action '{action}'. "
                        f"The action is listed in your domains action list, but "
                        f"there is no template defined with this name. You should "
                        f"add a template with this key.",
                        docs=ACTIONS_DOCUMENTS_URL + "#utterance-actions",
                    )
                    everything_is_alright = False

        return everything_is_alright

    def utterances_in_story_verification(self, ignore_warnings: bool = True) -> bool:
        """Verifies usage of utterances in stories.

        Checks whether utterances used in the stories are valid,
        and whether all valid utterances are used in stories."""

        everything_is_alright = self.utterances_verification()

        utterance_activity = self._gather_utterance_activity()
        story_utterances = set()

        for story in self.story_graph.story_steps:
            for event in story.events:
                if not isinstance(event, ActionExecuted):
                    continue
                if not event.action_name.startswith(CONVO_UTTER_PREFIX):
                    # we are only interested in utter actions
                    continue

                if event.action_name in story_utterances:
                    # we already processed this one before, we only want to warn once
                    continue

                if event.action_name not in utterance_activity:
                    convo.shared.utils.io.raising_warning(
                        f"The action '{event.action_name}' is used in the stories, "
                        f"but is not a valid utterance action. Please make sure "
                        f"the action is listed in your domain and there is a "
                        f"template defined with its name.",
                        docs=ACTIONS_DOCUMENTS_URL + "#utterance-actions",
                    )
                    everything_is_alright = False
                story_utterances.add(event.action_name)

        for utterance in utterance_activity:
            if utterance not in story_utterances:
                logger.debug(f"The utterance '{utterance}' is not used in any story.")
                everything_is_alright = ignore_warnings and everything_is_alright

        return everything_is_alright

    def story_structure_varification(
        self, ignore_warnings: bool = True, max_history: Optional[int] = None
    ) -> bool:
        """Verifies that the bot behaviour in stories is deterministic.

        Args:
            ignore_warnings: When `True`, return `True` even if conflicts were found.
            max_history: Maximal number of events to take into account for conflict identification.

        Returns:
            `False` is a conflict was found and `ignore_warnings` is `False`.
            `True` otherwise.
        """

        logger.info("Story structure validation...")

        trackers = TrainingDataSetGenerator(
            self.story_graph,
            domain=self.domain,
            remove_identical=False,
            augmentation_factor=0,
        ).create()

        # Create a list of `StoryConflict` objects
        conflicts = convo.core.training.story_conflict.find_story_difference(
            trackers, self.domain, max_history
        )

        if not conflicts:
            logger.info("No story structure conflicts found.")
        else:
            for conflict in conflicts:
                logger.warning(conflict)

        return ignore_warnings or not conflicts

    def nlu_verification(self, ignore_warnings: bool = True) -> bool:
        """Runs all the validations on intents and utterances."""

        logger.info("Validating intents...")
        intents_validated = self.intents_in_story_verification(ignore_warnings)

        logger.info("Validating uniqueness of intents and stories...")
        no_duplication_present = self.eg_repetition_in_intents_verification(
            ignore_warnings
        )

        logger.info("Validating utterances...")
        valid_story = self.utterances_in_story_verification(ignore_warnings)
        return intents_validated and valid_story and no_duplication_present

    def domain_validity_verification(self) -> bool:
        """Checks whether the domain returned by the importer is empty.

        An empty domain is invalid."""

        return not self.domain.is_empty()
