import asyncio
from functools import reduce
from typing import Text, Optional, List, Dict, Set, Any, Tuple
import logging

import convo.shared.constants
import convo.shared.utils.common
import convo.shared.core.constants
import convo.shared.utils.io
from convo.shared.core.domain import Domain
from convo.shared.core.events import ActionExecuted, UserUttered
from convo.shared.nlu.interpreter import NaturalLangInterpreter, RegexInterpreter
from convo.shared.core.training_data.structures import StoryPlot
from convo.shared.nlu.training_data.message import Msg
from convo.shared.nlu.training_data.training_data import TrainingDataSet
from convo.shared.nlu.constants import ENTITIES_NAME, ACT_NAME
from convo.shared.importers.autoconfig import TrainingClassification
from convo.shared.core.domain import RETRIEVAL_INTENT_KEY_CHECK

log = logging.getLogger(__name__)


class TrainingDataImporter:
    """Common interface for different mechanisms to load training data."""

    async def domain(self) -> Domain:
        """Retrieves the domain of the bot.

        Returns:
            Loaded `Domain`.
        """
        raise NotImplementedError()

    async def fetch_stories(
        self,
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryPlot:
        """Retrieves the stories that should be used for training.

        Args:
            template_variables: Values of templates that should be replaced while
                                reading the story files.
            use_e2e: Specifies whether to parse end to end learning annotations.
            exclusion_percentage: Amount of training data that should be excluded.

        Returns:
            `StoryPlot` containing all loaded stories.
        """

        raise NotImplementedError()

    async def get_config(self) -> Dict:
        """Retrieves the configuration that should be used for the training.

        Returns:
            The configuration as dictionary.
        """

        raise NotImplementedError()

    async def fetch_nlu_data(self, language: Optional[Text] = "en") -> TrainingDataSet:
        """Retrieves the NLU training data that should be used for training.

        Args:
            language: Can be used to only load training data for a certain language.

        Returns:
            Loaded NLU `TrainingDataSet`.
        """

        raise NotImplementedError()

    @staticmethod
    def load_from_configuration(
        config_path: Text,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[List[Text]] = None,
        training_type: Optional[TrainingClassification] = TrainingClassification.TWO,
    ) -> "TrainingDataImporter":
        """Loads a `TrainingDataImporter` instance from a configuration file."""

        configuration = convo.shared.utils.io.read_configuration_file(config_path)
        return TrainingDataImporter.load_from_dictionary(
            configuration, config_path, domain_path, training_data_paths, training_type
        )

    @staticmethod
    def load_core_importer_from_configuration(
        config_path: Text,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[List[Text]] = None,
    ) -> "TrainingDataImporter":
        """Loads core `TrainingDataImporter` instance.

        Instance loaded from configuration file will only read Core training data.
        """

        importer = TrainingDataImporter.load_from_configuration(
            config_path, domain_path, training_data_paths, TrainingClassification.CORE
        )

        return CoreDataSetImporter(importer)

    @staticmethod
    def load_nlu_importer_from_configuration(
        config_path: Text,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[List[Text]] = None,
    ) -> "TrainingDataImporter":
        """Loads nlu `TrainingDataImporter` instance.

        Instance loaded from configuration file will only read NLU training data.
        """

        bring_in = TrainingDataImporter.load_from_configuration(
            config_path, domain_path, training_data_paths, TrainingClassification.NLU
        )

        if isinstance(bring_in, EToEImporter):
            # When we only train NLU then there is no need to enrich the data with
            # E2E data from Core training data.
            bring_in = bring_in.importer

        return NluDataSetImporter(bring_in)

    @staticmethod
    def load_from_dictionary(
        configuration: Optional[Dict],
        config_path: Text,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[List[Text]] = None,
        training_type: Optional[TrainingClassification] = TrainingClassification.TWO,
    ) -> "TrainingDataImporter":
        """Loads a `TrainingDataImporter` instance from a dictionary."""

        from convo.shared.importers.convo import FileImporter

        configuration = configuration or {}
        bring_in = configuration.get("importers", [])
        bring_in = [
            TrainingDataImporter.importer_from_dictionary(
                importer, config_path, domain_path, training_data_paths, training_type
            )
            for importer in bring_in
        ]
        bring_in = [importer for importer in bring_in if importer]
        if not bring_in:
            bring_in = [
                FileImporter(
                    config_path, domain_path, training_data_paths, training_type
                )
            ]

        return EToEImporter(RetrievalModelsDataSetImporter(CombinedDataSetImporter(bring_in)))

    @staticmethod
    def importer_from_dictionary(
        importer_configuration: Dict,
        config_path: Text,
        domain_path: Optional[Text] = None,
        training_data_paths: Optional[List[Text]] = None,
        training_type: Optional[TrainingClassification] = TrainingClassification.TWO,
    ) -> Optional["TrainingDataImporter"]:
        from convo.shared.importers.multi_project import MannyProjectImporter
        from convo.shared.importers.convo import FileImporter

        path_of_module = importer_configuration.pop("name", None)
        if path_of_module == FileImporter.__name__:
            class_importer = FileImporter
        elif path_of_module == MannyProjectImporter.__name__:
            class_importer = MannyProjectImporter
        else:
            try:
                class_importer = convo.shared.utils.common.class_name_from_module_path(
                    path_of_module
                )
            except (AttributeError, ImportError):
                logging.warning(f"Importer '{path_of_module}' not found.")
                return None

        importer_configuration = dict(training_type=training_type, **importer_configuration)

        contructor_args = convo.shared.utils.common.min_kwargs(
            importer_configuration, class_importer
        )

        return class_importer(
            config_path, domain_path, training_data_paths, **contructor_args
        )


class NluDataSetImporter(TrainingDataImporter):
    """Importer that skips any Core-related file reading."""

    def __init__(self, actual_importer: TrainingDataImporter):
        self._importer = actual_importer

    async def domain(self) -> Domain:
        return Domain.empty()

    async def fetch_stories(
        self,
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryPlot:
        return StoryPlot([])

    async def get_config(self) -> Dict:
        return await self._importer.get_config()

    async def fetch_nlu_data(self, language: Optional[Text] = "en") -> TrainingDataSet:
        return await self._importer.fetch_nlu_data(language)


class CoreDataSetImporter(TrainingDataImporter):
    """Importer that skips any NLU related file reading."""

    def __init__(self, actual_importer: TrainingDataImporter):
        self._importer = actual_importer

    async def domain(self) -> Domain:
        return await self._importer.domain()

    async def fetch_stories(
        self,
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryPlot:
        return await self._importer.fetch_stories(
            template_variables, use_e2e, exclusion_percentage
        )

    async def get_config(self) -> Dict:
        return await self._importer.get_config()

    async def fetch_nlu_data(self, language: Optional[Text] = "en") -> TrainingDataSet:
        return TrainingDataSet()


class CombinedDataSetImporter(TrainingDataImporter):
    """A `TrainingDataImporter` that combines multiple importers.
    Uses multiple `TrainingDataImporter` instances
    to load the data as if they were a single instance.
    """

    def __init__(self, importers: List[TrainingDataImporter]):
        self._importers = importers

    @convo.shared.utils.common.caching_method
    async def get_config(self) -> Dict:
        configs = [importer.get_config() for importer in self._importers]
        configs = await asyncio.gather(*configs)

        return reduce(lambda merged, others: {**merged, **(others or {})}, configs, {})

    @convo.shared.utils.common.caching_method
    async def domain(self) -> Domain:
        domain_name = [importer.domain() for importer in self._importers]
        domain_name = await asyncio.gather(*domain_name)

        return reduce(
            lambda merged, others: merged.merge(others), domain_name, Domain.empty()
        )

    @convo.shared.utils.common.caching_method
    async def fetch_stories(
        self,
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryPlot:
        story = [
            importer.fetch_stories(template_variables, use_e2e, exclusion_percentage)
            for importer in self._importers
        ]
        story = await asyncio.gather(*story)

        return reduce(
            lambda merged, others: merged.merge(others), story, StoryPlot([])
        )

    @convo.shared.utils.common.caching_method
    async def fetch_nlu_data(self, language: Optional[Text] = "en") -> TrainingDataSet:
        data_nlu = [importer.fetch_nlu_data(language) for importer in self._importers]
        data_nlu = await asyncio.gather(*data_nlu)

        return reduce(
            lambda merged, others: merged.merge(others), data_nlu, TrainingDataSet()
        )


class RetrievalModelsDataSetImporter(TrainingDataImporter):
    """A `TrainingDataImporter` that sets up the data for training retrieval models.

    Synchronizes response templates between Domain and NLU
    and adds retrieval intent properties from the NLU training data
    back to the Domain.
    """

    def __init__(self, importer: TrainingDataImporter):
        self._importer = importer

    async def get_config(self) -> Dict:
        return await self._importer.get_config()

    @convo.shared.utils.common.caching_method
    async def domain(self) -> Domain:
        """Merge existing domain with properties of retrieval convo_intents in NLU data."""

        domain_existing = await self._importer.domain()
        nlu_data_existing = await self._importer.fetch_nlu_data()

        # Check if NLU data has any retrieval convo_intents, if yes
        # add corresponding retrieval actions with `utter_` prefix automatically
        # to an empty domain, update the properties of existing retrieval convo_intents
        # and merge response templates
        if nlu_data_existing.retrieval_intents:

            retrieval_intents_domain = self.get_domain_with_retrieval_intents(
                nlu_data_existing.retrieval_intents,
                nlu_data_existing.responses,
                domain_existing,
            )

            domain_existing = domain_existing.merge(retrieval_intents_domain)

        return domain_existing

    @staticmethod
    def construct_retrieval_action_names(retrieval_intents: Set[Text]) -> List[Text]:
        """List names of all retrieval actions corresponding to passed retrieval convo_intents.

        Args:
            retrieval_intents: List of retrieval convo_intents defined in the NLU training data.

        Returns: Names of corresponding retrieval actions
        """

        return [
            f"{convo.shared.constants.CONVO_UTTER_PREFIX }{intent}"
            for intent in retrieval_intents
        ]

    @staticmethod
    def get_domain_with_retrieval_intents(
        retrieval_intents: Set[Text],
        response_templates: Dict[Text, List[Dict[Text, Any]]],
        existing_domain: Domain,
    ) -> Domain:
        """Construct a domain consisting of retrieval convo_intents listed in the NLU training data.

        Args:
            retrieval_intents: Set of retrieval convo_intents defined in NLU training data.
            existing_domain: Domain which is already loaded from the domain file.

        Returns: Domain with retrieval actions added to action names and properties
        for retrieval convo_intents updated.
        """

        # Get all the properties already defined
        # for each retrieval intent in others domains
        # and add the retrieval intent property to them
        retrieval_intent_props = []
        for intent in retrieval_intents:
            intent_props = (
                existing_domain.intent_props[intent]
                if intent in existing_domain.intent_props
                else {}
            )
            intent_props[RETRIEVAL_INTENT_KEY_CHECK] = True
            retrieval_intent_props.append({intent: intent_props})

        return Domain(
            retrieval_intent_props,
            [],
            [],
            response_templates,
            RetrievalModelsDataSetImporter.construct_retrieval_action_names(
                retrieval_intents
            ),
            [],
        )

    async def fetch_stories(
        self,
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryPlot:

        return await self._importer.fetch_stories(
            template_variables, use_e2e, exclusion_percentage
        )

    @convo.shared.utils.common.caching_method
    async def fetch_nlu_data(self, language: Optional[Text] = "en") -> TrainingDataSet:
        """Update NLU data with response templates for retrieval convo_intents defined in the domain"""

        nlu_data_existing = await self._importer.fetch_nlu_data(language)
        domain_existing = await self._importer.domain()

        return nlu_data_existing.merge(
            self.get_nlu_data_with_response(
                domain_existing.retrieve_intent_template
            )
        )

    @staticmethod
    def get_nlu_data_with_response(
        response_templates: Dict[Text, List[Dict[Text, Any]]]
    ) -> TrainingDataSet:
        """Construct training data object with only the response templates supplied.

        Args:
            response_templates: Response templates the NLU data should
            be initialized with.

        Returns: TrainingDataSet object with response templates.

        """

        return TrainingDataSet(responses=response_templates)


class EToEImporter(TrainingDataImporter):
    """Importer which
    - enhances the NLU training data with actions / user messages from the stories.
    - adds potential end-to-end bot messages from stories as actions to the domain
    """

    def __init__(self, importer: TrainingDataImporter) -> None:
        self.importer = importer

    @convo.shared.utils.common.caching_method
    async def domain(self) -> Domain:
        original, e2e_domain = await asyncio.gather(
            self.importer.domain(), self.get_domain_with_e2e_actions()
        )
        return original.merge(e2e_domain)

    async def get_domain_with_e2e_actions(self) -> Domain:
        from convo.shared.core.events import ActionExecuted

        fetch_story = await self.fetch_stories()

        addon_e2e_action_names = set()
        for story_step in fetch_story.story_steps:
            addon_e2e_action_names.update(
                {
                    event.action_text
                    for event in story_step.events
                    if isinstance(event, ActionExecuted) and event.action_text
                }
            )

        addon_e2e_action_names = list(addon_e2e_action_names)

        return Domain(
            [], [], [], {}, action_names=addon_e2e_action_names, forms=[]
        )

    async def fetch_stories(
        self,
        interpreter: "NaturalLangInterpreter" = RegexInterpreter(),
        template_variables: Optional[Dict] = None,
        use_e2e: bool = False,
        exclusion_percentage: Optional[int] = None,
    ) -> StoryPlot:
        return await self.importer.fetch_stories(
            template_variables, use_e2e, exclusion_percentage
        )

    async def get_config(self) -> Dict:
        return await self.importer.get_config()

    @convo.shared.utils.common.caching_method
    async def fetch_nlu_data(self, language: Optional[Text] = "en") -> TrainingDataSet:
        training_data_sets = [addon_training_data_from_default_actions()]

        training_data_sets += await asyncio.gather(
            self.importer.fetch_nlu_data(language),
            self.addon_training_data_from_stories(),
        )

        return reduce(
            lambda merged, others: merged.merge(others), training_data_sets, TrainingDataSet()
        )

    async def addon_training_data_from_stories(self) -> TrainingDataSet:
        fetch_story = await self.fetch_stories()

        changes, act = unique_event_from_stories(fetch_story)

        # Sort events to guarantee deterministic behavior and to avoid that the NLU
        # model has to be retrained due to changes in the event order within
        # the stories.
        utterances_sorted = sorted(
            changes, key=lambda user: user.name_of_intent or user.text
        )
        sorted_actions = sorted(
            act, key=lambda action: action.action_name or action.action_text
        )

        addon_msgs_from_stories = [
            msgs_from_action(action) for action in sorted_actions
        ] + [msgs_from_user_utterance(user) for user in utterances_sorted]

        log.debug(
            f"Added {len(addon_msgs_from_stories)} training data examples "
            f"from the story training data."
        )
        return TrainingDataSet(addon_msgs_from_stories)


def unique_event_from_stories(
    stories: StoryPlot,
) -> Tuple[Set[UserUttered], Set[ActionExecuted]]:
    events_for_action = set()
    events_for_user = set()

    for story_step in stories.story_steps:
        for event in story_step.events:
            if isinstance(event, ActionExecuted):
                events_for_action.add(event)
            elif isinstance(event, UserUttered):
                events_for_user.add(event)

    return events_for_user, events_for_action


def msgs_from_user_utterance(event: UserUttered) -> Msg:
    # sub state correctly encodes intent vs text
    data_set = event.as_substate()
    # sub state stores entities differently
    if data_set.get(ENTITIES_NAME) and event.entities:
        data_set[ENTITIES_NAME] = event.entities

    return Msg(data=data_set)


def msgs_from_action(event: ActionExecuted) -> Msg:
    # sub state correctly encodes action_name vs action_text
    return Msg(data=event.as_substate())


def addon_training_data_from_default_actions() -> TrainingDataSet:
    addon_msgs_from_default_actions = [
        Msg(data={ACT_NAME: action_name})
        for action_name in convo.shared.core.constants.DEFAULT_ACTION_NAME   
    ]

    return TrainingDataSet(addon_msgs_from_default_actions)
