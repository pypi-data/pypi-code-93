import copy
import collections
import json
import logging
import os
from typing import (
    Any,
    Dict,
    List,
    NamedTuple,
    Optional,
    Set,
    Text,
    Tuple,
    Union,
    NoReturn,
    TYPE_CHECKING,
)
from pathlib import Path

from ruamel.yaml import YAMLError

import convo.shared.constants
import convo.shared.core.constants
from convo.shared.exceptions import ConvoExceptions , YamlExceptions 
from convo.shared.utils.validation import YamlValidationExceptionRaise
import convo.shared.nlu.constants
import convo.shared.utils.validation
import convo.shared.utils.io
import convo.shared.utils.common
from convo.shared.core.events import SetofSlot, UserUttered
from convo.shared.core.slots import Slot, CategoricalSlot, TextSlot
from convo.shared.utils.validation import KEY_TRAINING_DATA_FORMAT_VER


if TYPE_CHECKING:
    from convo.shared.core.trackers import DialogueStateTracer

CARRY_OVER_SLOT_KEY = "carry_over_slots_to_new_session"
SESSION_EXPIRY_TIME_KEY = "session_expiration_time"
SESSION_CONFIGURATION_KEY = "session_configuration"
CONVO_USED_ENTITIES_KEY = "entities_used"
CONVO_USE_ENTITIES_KEY = "use_entities"
CONVO_IGNORE_ENTITIES_KEY = "ignore_entities"
RETRIEVAL_INTENT_KEY_CHECK = "is_retrieval_intent"

SLOTS_KEY = "slots"
convo_intents_KEY = "intents"
ENTITIES_KEY = "entities"
RESPONSES_KEY = "responses"
ACTIONS_KEY = "actions"
FORMS_KEY = "forms"
E2E_ACTIONS_KEY = "e2e_actions"

DOMAIN_KEYS = [
    SLOTS_KEY,
    FORMS_KEY,
    ACTIONS_KEY,
    ENTITIES_KEY,
    convo_intents_KEY,
    RESPONSES_KEY,
    E2E_ACTIONS_KEY,
]

PREVIOUS_PREFIX  = "prev_"

# fetch_state is a dictionary with keys (CONVO_USER, PRECEDING_ACTION   , CONVO_SLOTS, CURRENT_LOOP   )
# representing the origin of a Sub_State;
# the values are SubStates, that contain the information needed for featurization
Sub_State = Dict[Text, Union[Text, Tuple[Union[float, Text]]]]
fetch_state = Dict[Text, Sub_State]

log = logging.getLogger(__name__)


class InvalidDomain(ConvoExceptions ):
    """Exception that can be raised when domain is not valid."""


class ActionNotFoundException(ValueError, ConvoExceptions ):
    """Raised when an action name could not be found."""


class SessionConfiguration(NamedTuple):
    session_expiration_time: float  # in minutes
    carry_over_slots: bool

    @staticmethod
    def by_default() -> "SessionConfiguration":
        return SessionConfiguration(
            convo.shared.constants.DEFAULT_SESSION_EXPIRE_IN_MINS,
            convo.shared.constants.DEFAULT_CARRY_OVER_SLOT_TO_NEW_SESSION,
        )

    def sessions_enabled(self) -> bool:
        return self.session_expiration_time > 0


class Domain:
    """The domain specifies the universe in which the bot's policy acts.

    A Domain subclass provides the actions the bot can take, the convo_intents
    and entities it can recognise."""

    @classmethod
    def empty(cls) -> "Domain":
        return cls([], [], [], {}, [], [])

    @classmethod
    def load(cls, path: Union[List[Union[Path, Text]], Text, Path]) -> "Domain":
        if not path:
            raise InvalidDomain(
                "No domain file was specified. Please specify a path "
                "to a valid domain file."
            )
        elif not isinstance(path, list) and not isinstance(path, set):
            path = [path]

        domain = Domain.empty()
        for path in path:
            others = cls.from_path(path)
            domain = domain.merge(others)

        return domain

    @classmethod
    def from_path(cls, path: Union[Text, Path]) -> "Domain":
        path = os.path.abspath(path)

        if os.path.isfile(path):
            domain = cls.from_file(path)
        elif os.path.isdir(path):
            domain = cls.from_directory(path)
        else:
            raise InvalidDomain(
                "Failed to load domain specification from '{}'. "
                "File not found!".format(os.path.abspath(path))
            )

        return domain

    @classmethod
    def from_file(cls, path: Text) -> "Domain":
        return cls.from_yaml(convo.shared.utils.io.read_file(path), path)

    @classmethod
    def from_yaml(cls, yaml: Text, original_filename: Text = "") -> "Domain":
        try:
            convo.shared.utils.validation.validating_yaml_schema(
                yaml, convo.shared.constants.DOMAINS_SCHEMA_FILE
            )

            data_set = convo.shared.utils.io.reading_yaml(yaml)
            if not convo.shared.utils.validation.validating_training_data_format_version(
                data_set, original_filename
            ):
                return Domain.empty()

            return cls.from_dict(data_set)
        except YamlExceptions  as e:
            e.filename = original_filename
            raise e

    @classmethod
    def from_dict(cls, data: Dict) -> "Domain":
        utter_template = data.get(RESPONSES_KEY, {})
        slots_name= cls.collect_slots(data.get(SLOTS_KEY, {}))
        add_on_arguments = data.get("config", {})
        session_configuration = cls._get_session_config(data.get(SESSION_CONFIGURATION_KEY, {}))
        fetch_intents = data.get(convo_intents_KEY, {})

        return cls(
            fetch_intents,
            data.get(ENTITIES_KEY, []),
            slots_name,
            utter_template,
            data.get(ACTIONS_KEY, []),
            data.get(FORMS_KEY, []),
            data.get(E2E_ACTIONS_KEY, []),
            session_configuration=session_configuration,
            **add_on_arguments,
        )

    @staticmethod
    def _get_session_config(session_configuration: Dict) -> SessionConfiguration:
        session_expiry_time_minutes = session_configuration.get(SESSION_EXPIRY_TIME_KEY)

        if session_expiry_time_minutes is None:
            session_expiry_time_minutes = (
                convo.shared.constants.DEFAULT_SESSION_EXPIRE_IN_MINS
            )

        carry_over_slots = session_configuration.get(
            CARRY_OVER_SLOT_KEY,
            convo.shared.constants.DEFAULT_CARRY_OVER_SLOT_TO_NEW_SESSION,
        )

        return SessionConfiguration(session_expiry_time_minutes, carry_over_slots)

    @classmethod
    def from_directory(cls, path: Text) -> "Domain":
        """Loads and merges multiple domain files recursively from a dir tree."""

        domain = Domain.empty()
        for root, _, files in os.walk(path, followlinks=True):
            for file in files:
                convo_full_path = os.path.join(root, file)
                if Domain.domain_file_check(complete_path):
                    others = Domain.from_file(complete_path)
                    domain = others.merge(domain)

        return domain

    def merge(self, domain: Optional["Domain"], override: bool = False) -> "Domain":
        """Merge this domain with another one, combining their attributes.

        List attributes like ``convo_intents`` and ``actions`` will be deduped
        and merged. Single attributes will be taken from `self` unless
        override is `True`, in which case they are taken from `domain`."""

        if not domain or domain.is_empty():
            return self

        if self.is_empty():
            return domain

        domain_dictionary = domain.as_dictionary()
        merge = self.as_dictionary()

        def merge_dictionaries(
            d1: Dict[Text, Any],
            d2: Dict[Text, Any],
            override_existing_values: bool = False,
        ) -> Dict[Text, Any]:
            if override_existing_values:
                a, b = d1.copy(), d2.copy()
            else:
                a, b = d2.copy(), d1.copy()
            a.update(b)
            return a

        def merge_lists_data(l1: List[Any], l2: List[Any]) -> List[Any]:
            return sorted(list(set(l1 + l2)))

        def merge_lists_of_dictionaries(
            dict_list1: List[Dict],
            dict_list2: List[Dict],
            override_existing_values: bool = False,
        ) -> List[Dict]:
            dictionary1 = {list(i.keys())[0]: i for i in dict_list1}
            dictionary2 = {list(i.keys())[0]: i for i in dict_list2}
            merged_dictionaries = merge_dictionaries(dictionary1, dictionary2, override_existing_values)
            return list(merged_dictionaries.values())

        if override:
            configuration = domain_dictionary["config"]
            for key, val in configuration.items():  # pytype: disable=attribute-error
                merge["config"][key] = val

        if override or self.session_configuration == SessionConfiguration.by_default():
            merge[SESSION_CONFIGURATION_KEY] = domain_dictionary[SESSION_CONFIGURATION_KEY]

        merge [convo_intents_KEY] = merge_lists_of_dictionaries(
            merge[convo_intents_KEY], domain_dictionary[convo_intents_KEY], override
        )

        # remove existing forms from new actions
        for form in merge[FORMS_KEY]:
            if form in domain_dictionary[ACTIONS_KEY]:
                domain_dictionary[ACTIONS_KEY].remove(form)

        for key in [ENTITIES_KEY, ACTIONS_KEY, E2E_ACTIONS_KEY]:
            merge[key] = merge_lists_data(merge[key], domain_dictionary[key])

        for key in [FORMS_KEY, RESPONSES_KEY, SLOTS_KEY]:
            merge [key] = merge_dictionaries(merge[key], domain_dictionary[key], override)

        return self.__class__.from_dict(merge)

    @staticmethod
    def collect_slots(slot_dict: Dict[Text, Any]) -> List[Slot]:
        slots= []
        # make a copy to not alter the input dictionary
        slot_dict = copy.deepcopy(slot_dict)
        # Sort the convo_slotsso that the order of the slot states is consistent
        for slot_name in sorted(slot_dict):
            slots_type = slot_dict[slot_name].pop("type", None)
            slots_class = Slot.resolved_by_type(slots_type)

            slot = slots_class(slot_name, **slot_dict[slot_name])
            slots.append(slot)
        return slots

    @staticmethod
    def _transform_intent_properties_for_internal_use(
        intent: Dict[Text, Any], entities: List
    ) -> Dict[Text, Any]:
        """Transform intent properties coming from a domain file for internal use.

        In domain files, `use_entities` or `ignore_entities` is used. Internally, there
        is a property `entities_used` instead that lists all entities to be used.

        Args:
            intent: The convo_intents as provided by a domain file.
            entities: All entities as provided by a domain file.

        Returns:
            The convo_intents as they should be used internally.
        """
        name, properties = list(intent.items())[0]

        properties.setdefault(CONVO_USE_ENTITIES_KEY, True)
        properties.setdefault(CONVO_IGNORE_ENTITIES_KEY, [])
        if not properties[CONVO_USE_ENTITIES_KEY]:  # this covers False, None and []
            properties[CONVO_USE_ENTITIES_KEY] = []

        # `use_entities` is either a list of explicitly included entities
        # or `True` if all should be included
        if properties[CONVO_USE_ENTITIES_KEY] is True:
            entities_included = set(entities)
        else:
            entities_included = set(properties[CONVO_USE_ENTITIES_KEY])
        entities_excluded = set(properties[CONVO_IGNORE_ENTITIES_KEY])
        entities_used = list(entities_included - entities_excluded)
        entities_used.sort()

        # Only print warning for ambiguous configurations if entities were included
        # explicitly.
        included_explicitly = isinstance(properties[CONVO_USE_ENTITIES_KEY], list)
        entities_ambiguous = entities_included.intersection(entities_excluded)
        if included_explicitly and entities_ambiguous:
            convo.shared.utils.io.raising_warning(
                f"Entities: '{entities_ambiguous}' are explicitly included and"
                f" excluded for intent '{name}'."
                f"Excluding takes precedence in this case. "
                f"Please resolve that ambiguity.",
                docs=f"{convo.shared.constants.DOMAIN_DOCUMENTS_URL}",
            )

        properties[CONVO_USED_ENTITIES_KEY] = entities_used
        del properties[CONVO_USE_ENTITIES_KEY]
        del properties[CONVO_IGNORE_ENTITIES_KEY]

        return intent

    @convo.shared.utils.common.lazy_property
    def retrieval_intents(self) -> List[Text]:
        """List retrieval convo_intents present in the domain."""
        return [
            intent
            for intent in self.intent_props
            if self.intent_props[intent].get(RETRIEVAL_INTENT_KEY_CHECK)
        ]

    @classmethod
    def collect_intent_props(
        cls, convo_intents: List[Union[Text, Dict[Text, Any]]], entities: List[Text]
    ) -> Dict[Text, Dict[Text, Union[bool, List]]]:
        """Get intent properties for a domain from what is provided by a domain file.

        Args:
            convo_intents: The convo_intents as provided by a domain file.
            entities: All entities as provided by a domain file.

        Returns:
            The intent properties to be stored in the domain.
        """
        # make a copy to not alter the input argument
        convo_intents = copy.deepcopy(convo_intents)
        intent_props = {}
        identical = set()

        for intent in convo_intents:
            name_of_intent, properties = cls._intent_props(intent, entities)

            if name_of_intent in intent_props.keys():
                identical.add(name_of_intent)

            intent_props.update(properties)

        if identical:
            raise InvalidDomain(
                f"convo_intents are not unique! Found multiple convo_intents with name(s) {sorted(identical)}. "
                f"Either rename or remove the duplicate ones."
            )

        cls._add_default_convo_intents(intent_props, entities)

        return intent_props

    @classmethod
    def _intent_props(
        cls, intent: Union[Text, Dict[Text, Any]], entities: List[Text]
    ) -> Tuple[Text, Dict[Text, Any]]:
        if not isinstance(intent, dict):
            name_of_intent = intent
            intent = {name_of_intent: {CONVO_USE_ENTITIES_KEY: True, CONVO_IGNORE_ENTITIES_KEY: []}}
        else:
            name_of_intent = list(intent.keys())[0]

        return (
            name_of_intent,
            cls._transform_intent_properties_for_internal_use(intent, entities),
        )

    @classmethod
    def _add_default_convo_intents(
        cls,
        intent_props: Dict[Text, Dict[Text, Union[bool, List]]],
        entities: List[Text],
    ) -> None:
        for name_of_intent in convo.shared.core.constants.DEFAULT_INTENT  :
            if name_of_intent not in intent_props:
                _, properties = cls._intent_props(name_of_intent, entities)
                intent_props.update(properties)

    def __init__(
        self,
        convo_intents: Union[Set[Text], List[Text], List[Dict[Text, Any]]],
        entities: List[Text],
        slots: List[Slot],
        templates: Dict[Text, List[Dict[Text, Any]]],
        action_names: List[Text],
        forms: Union[Dict[Text, Any], List[Text]],
        action_texts: Optional[List[Text]] = None,
        store_entities_as_slots: bool = True,
        session_configuration: SessionConfiguration = SessionConfiguration.by_default(),
    ) -> None:

        self.intent_props = self.collect_intent_props(convo_intents, entities)
        self.overriden_default_convo_intents = self.collect_default_intents(
            convo_intents
        )
        self.entities = entities

        self.forms: Dict[Text, Any] = {}
        self.form_names: List[Text] = []
        self.initialize_forms(forms)

        self.slots= slots
        self.templates = templates
        self.action_texts = action_texts or []
        self.session_configuration = session_configuration

        self._custom_actions = action_names

        # only includes custom actions and utterance actions
        self.user_actions = self.merge_with_templates(action_names, templates)

        # includes all actions (custom, utterance, default actions and forms)
        self.action_names = (
            self.merge_user_with_default_actions(self.user_actions)
            + self.form_names
            + self.action_texts
        )

        self.store_entities_as_slots = store_entities_as_slots
        self.domain_sanity_check()

    def __deepcopy__(self, memo: Optional[Dict[int, Any]]) -> "Domain":
        """Enables making a deep copy of the `Domain` using `copy.deepcopy`.

        See https://docs.python.org/3/library/copy.html#copy.deepcopy
        for more implementation.

        Args:
            memo: Optional dictionary of objects already copied during the current
            copying pass.

        Returns:
            A deep copy of the current domain.
        """
        domain_dictionary = self.as_dictionary()
        return self.__class__.from_dict(copy.deepcopy(domain_dictionary, memo))

    @staticmethod
    def collect_default_intents(
        convo_intents: Union[Set[Text], List[Text], List[Dict[Text, Any]]]
    ) -> List[Text]:
        """Collects the default convo_intents overridden by the user.

        Args:
            convo_intents: User-provided convo_intents.

        Returns:
            User-defined convo_intents that are default convo_intents.
        """
        name_of_intents: Set[Text] = {
            list(intent.keys())[0] if isinstance(intent, dict) else intent
            for intent in convo_intents
        }
        return sorted(name_of_intents & set(convo.shared.core.constants.DEFAULT_INTENT  ))

    def initialize_forms(self, forms: Union[Dict[Text, Any], List[Text]]) -> None:
        """Initialize the domain's `self.form` and `self.form_names` attributes.

        Args:
            forms: Form names (if forms are a list) or a form dictionary. Forms
                provided in dictionary format have the form names as keys, and either
                empty dictionaries as values, or objects containing
                `SlotMapping`s.
        """
        if not forms:
            # empty dict or empty list
            return
        elif isinstance(forms, dict):
            # dict with slot mappings
            self.forms = forms
            self.form_names = list(forms.keys())
        elif isinstance(forms, list) and isinstance(forms[0], str):
            # list of form names
            self.forms = {form_name: {} for form_name in forms}
            self.form_names = forms
        else:
            convo.shared.utils.io.raising_warning(
                f"The `forms` section in the domain needs to contain a dictionary. "
                f"Instead found an object of type '{type(forms)}'.",
                docs=convo.shared.constants.FORMS_DOCUMENTS_URL,
            )

    def __hash__(self) -> int:
        self_dictionary = self.as_dictionary()
        self_dictionary[
            convo_intents_KEY
        ] = convo.shared.utils.common.sort_list_of_dictionaries_by_first_key(
            self_dictionary[convo_intents_KEY]
        )
        self_dictionary[ACTIONS_KEY] = self.action_names
        self_string= json.dumps(self_dictionary, sort_keys=True)
        text_hashcode= convo.shared.utils.io.fetch_text_hashcode(self_string)

        return int(text_hashcode, 16)

    @convo.shared.utils.common.lazy_property
    def user_forms_and_actions(self):
        """Returns combination of user actions and forms."""

        return self.user_actions + self.form_names

    @convo.shared.utils.common.lazy_property
    def number_of_actions(self):
        """Returns the number of available actions."""

        # noinspection PyTypeChecker
        return len(self.action_names)

    @convo.shared.utils.common.lazy_property
    def num_of_states(self):
        """Number of used input states for the action prediction."""

        return len(self.states_input)

    @convo.shared.utils.common.lazy_property
    def retrieve_intent_template(self) -> Dict[Text, List[Dict[Text, Any]]]:
        """Return only the templates which are defined for retrieval convo_intents"""

        return dict(
            filter(
                lambda x: self.retrieval_intent_template_check(x), self.templates.items()
            )
        )

    @staticmethod
    def retrieval_intent_template_check(
        template: Tuple[Text, List[Dict[Text, Any]]]
    ) -> bool:
        """Check if the response template is for a retrieval intent.

        These templates have a `/` symbol in their name. Use that to filter them from the rest.
        """
        return convo.shared.nlu.constants.RESP_IDENTIFIER_DELIMITER in template[0]

    def add_category_wise_slot_default_value(self) -> None:
        """Add a default value to all categorical slots.

        All unseen values found for the slot will be mapped to this default value
        for featurization.
        """
        for slot in [s for s in self.slots if isinstance(s, CategoricalSlot)]:
            slot.adding_default_value()

    def add_new_requested_slot(self) -> None:
        """Add a slot called `requested_slot` to the list of slots.

        The value of this slot will hold the name of the slot which the user
        needs to fill in next (either explicitly or implicitly) as part of a form.
        """
        if self.form_names and convo.shared.core.constants.REQUESTED_SLOTS not in [
            s.name for s in self.slots
        ]:
            self.slots.append(
                TextSlot(
                    convo.shared.core.constants.REQUESTED_SLOTS,
                    influence_conversation=False,
                )
            )

    def add_knowledge_base_slot(self) -> None:
        """
        Add convo_slotsfor the knowledge base action to the list of slots, if the
        default knowledge base action name is present.

        As soon as the knowledge base action is not experimental anymore, we should
        consider creating a new section in the domain file dedicated to knowledge
        base slots.
        """
        if (
            convo.shared.core.constants.CONVO_DEFAULT_KNOWLEDGE_BASE_ACTION 
            in self.action_names
        ):
            log.warning(
                "You are using an experiential feature: Action '{}'!".format(
                    convo.shared.core.constants.CONVO_DEFAULT_KNOWLEDGE_BASE_ACTION 
                )
            )
            slot_names = [s.name for s in self.slots]
            knowledge_base_slots = [
                convo.shared.core.constants.SLOT_LIST_ITEMS,
                convo.shared.core.constants.SLOT_LAST_OBJ,
                convo.shared.core.constants.SLOT_LAST_OBJ_TYPE,
            ]
            for s in knowledge_base_slots:
                if s not in slot_names:
                    self.slots.append(TextSlot(s, influence_conversation=False))

    def actions_index(self, action_name: Text) -> Optional[int]:
        """Look up which action index corresponds to this action name."""

        try:
            return self.action_names.index(action_name)
        except ValueError:
            self.not_found_exception_rasie_action(action_name)

    def not_found_exception_rasie_action(self, action_name) -> NoReturn:
        action_names = "\n".join([f"\t - {a}" for a in self.action_names])
        raise ActionNotFoundException(
            f"Cannot access action '{action_name}', "
            f"as that name is not a registered "
            f"action for this domain. "
            f"Available actions are: \n{action_names}"
        )

    def random_template(self, utter_action: Text) -> Optional[Dict[Text, Any]]:
        import numpy as np

        if utter_action in self.templates:
            return np.random.choice(self.templates[utter_action])
        else:
            return None

    # noinspection PyTypeChecker
    @convo.shared.utils.common.lazy_property
    def states_slot(self) -> List[Text]:
        """Returns all available slot state strings."""

        return [
            f"{slot.name}_{feature_index}"
            for slot in self.slots
            for feature_index in range(0, slot.feature_dimensions())
        ]

    @convo.shared.utils.common.lazy_property
    def state_map_input(self) -> Dict[Text, int]:
        """Provide a mapping from state names to indices."""
        return {f: i for i, f in enumerate(self.states_input)}

    @convo.shared.utils.common.lazy_property
    def states_input(self) -> List[Text]:
        """Returns all available states."""

        return (
            self.fetch_intents
            + self.entities
            + self.states_slot
            + self.action_names
            + self.form_names
        )

    def get_featured_entities(self, latest_message: UserUttered) -> Set[Text]:
        name_of_intent = latest_message.intent.get(
            convo.shared.nlu.constants.KEY_INTENT_NAME
        )
        intent_configuration = self.intent_configuration(name_of_intent)
        fetch_entities = latest_message.entities
        name_entity = set(
            entity["entity"] for entity in fetch_entities if "entity" in entity.keys()
        )

        required_entities = set(intent_configuration.get(CONVO_USED_ENTITIES_KEY, name_entity))

        return name_entity.intersection(required_entities)

    def get_user_sub_state(
        self, tracker: "DialogueStateTracer"
    ) -> Dict[Text, Union[Text, Tuple[Text]]]:
        """Turn latest UserUttered event into a substate containing intent,
        text and set entities if present
        Args:
            tracker: dialog state tracker containing the dialog so far
        Returns:
            a dictionary containing intent, text and set entities
        """
        # proceed with values only if the user of a bot have done something
        # at the previous step i.e., when the state is not empty.
        latest_msg = tracker.latest_message
        if not latest_msg or latest_msg.is_empty_check():
            return {}

        SubState = latest_msg.as_substate()

        # filter entities based on intent config
        # sub_state will be transformed to frozenset therefore we need to
        # convert the list to the tuple
        # sub_state is transformed to frozenset because we will later hash it
        # for deduplication
        fetch_entities = tuple(self.get_featured_entities(latest_msg))
        if fetch_entities:
            SubState[convo.shared.nlu.constants.ENTITIES_NAME] = fetch_entities
        else:
            SubState.pop(convo.shared.nlu.constants.ENTITIES_NAME, None)

        return SubState

    @staticmethod
    def get_slot_substate(
        tracker: "DialogueStateTracer",
    ) -> Dict[Text, Union[Text, Tuple[float]]]:
        """Set all set convo_slotswith the featurization of the stored value
        Args:
            tracker: dialog state tracker containing the dialog so far
        Returns:
            a dictionary mapping slot names to their featurization
        """
        slots= {}
        for slot_name, slot in tracker.slots.items():
            if slot is not None and slot.as_features():
                if slot.value == convo.shared.core.constants.NOT_SET   :
                    slots[slot_name] = convo.shared.core.constants.NOT_SET
                elif any(slot.as_features()):
                    # only add slot if some of the features are not zero
                    slots[slot_name] = tuple(slot.as_features())

        return slots

    @staticmethod
    def get_previous_action_sub_state(
        tracker: "DialogueStateTracer",
    ) -> Dict[Text, Text]:
        """Turn the previous taken action into a state name.
        Args:
            tracker: dialog state tracker containing the dialog so far
        Returns:
            a dictionary with the information on latest action
        """
        return tracker.latest_action

    @staticmethod
    def get_current_loop_sub_state(
        tracker: "DialogueStateTracer",
    ) -> Dict[Text, Text]:
        """Turn tracker's active loop into a state name.
        Args:
            tracker: dialog state tracker containing the dialog so far
        Returns:
            a dictionary mapping "name" to active loop name if present
        """

        # we don't use tracker.active_loop_name
        # because we need to keep should_not_be_set
        current_loop = tracker.active_loop.get(convo.shared.core.constants.LOOPNAME  )
        if current_loop:
            return {convo.shared.core.constants.LOOPNAME  : current_loop}
        else:
            return {}

    @staticmethod
    def clean_slate(state: fetch_state) -> fetch_state:
        return {
            state_type: sub_state
            for state_type, sub_state in state.items()
            if sub_state
        }

    def get_current_active_states(self, tracker: "DialogueStateTracer") -> fetch_state:
        """Return a bag of active states from the tracker state."""
        state = {
            convo.shared.core.constants.CONVO_USER: self.get_user_sub_state(tracker),
            convo.shared.core.constants.CONVO_SLOTS: self.get_slot_substate(tracker),
            convo.shared.core.constants.PRECEDING_ACTION   : self.get_previous_action_sub_state(
                tracker
            ),
            convo.shared.core.constants.CURRENT_LOOP   : self.get_current_loop_sub_state(
                tracker
            ),
        }
        return self.clean_slate(state)

    def states_tracker_history(
        self, tracker: "DialogueStateTracer"
    ) -> List[fetch_state]:
        """Array of states for each state of the trackers history."""
        return [
            self.get_current_active_states(tr) for tr in tracker.generates_all_priority_trackers()
        ]

    def entities_slots(self, entities: List[Dict[Text, Any]]) -> List[SetofSlot]:
        if self.store_entities_as_slots:
            slot_events = []
            for s in self.slots:
                if s.auto_fill:
                    matching_entities = [
                        e["value"] for e in entities if e["entity"] == s.name
                    ]
                    if matching_entities:
                        if s.type_name == "list":
                            slot_events.append(SetofSlot(s.name, matching_entities))
                        else:
                            slot_events.append(SetofSlot(s.name, matching_entities[-1]))
            return slot_events
        else:
            return []

    def persist_specs(self, model_path: Text) -> None:
        """Persist the domain specification to storage."""
        domain_spec_path = os.path.join(model_path, "domain.json")
        convo.shared.utils.io.create_dir_from_file(domain_spec_path)

        meta_data = {"states": self.states_input}
        convo.shared.utils.io.dump_object_as_json_to_file(domain_spec_path, meta_data)

    @classmethod
    def load_specs(cls, path: Text) -> Dict[Text, Any]:
        """Load a domains specification from a dumped model dir."""
        path_metadata = os.path.join(path, "domain.json")

        return json.loads(convo.shared.utils.io.read_file(path_metadata))

    def compare_with_specs(self, path: Text) -> bool:
        """Compare the domain spec of the current and the loaded domain.

        Throws exception if the loaded domain specification is different
        to the current domain are different.
        """
        load_domain_specification = self.load_specs(path)
        fetch_states = load_domain_specification["states"]

        if set(fetch_states) != set(self.states_input):
            missing = ",".join(set(fetch_states) - set(self.states_input))
            additional = ",".join(set(self.states_input) - set(fetch_states))
            raise InvalidDomain(
                f"Domain specification has changed. "
                f"You MUST retrain the policy. "
                f"Detected mismatch in domain specification. "
                f"The following states have been \n"
                f"\t - removed: {missing} \n"
                f"\t - added:   {additional} "
            )
        else:
            return True

    def slot_difinition(self) -> Dict[Any, Dict[str, Any]]:
        return {slot.name: slot.persistence_information() for slot in self.slots}

    def as_dictionary(self) -> Dict[Text, Any]:
        return {
            "config": {"store_entities_as_slots": self.store_entities_as_slots},
            SESSION_CONFIGURATION_KEY: {
                SESSION_EXPIRY_TIME_KEY: self.session_configuration.session_expiration_time,
                CARRY_OVER_SLOT_KEY: self.session_configuration.carry_over_slots,
            },
            convo_intents_KEY: self.transform_file_intents(),
            ENTITIES_KEY: self.entities,
            SLOTS_KEY: self.slot_difinition(),
            RESPONSES_KEY: self.templates,
            ACTIONS_KEY: self._custom_actions,  # class names of the actions
            FORMS_KEY: self.forms,
            E2E_ACTIONS_KEY: self.action_texts,
        }

    def transform_file_intents(self) -> List[Union[Text, Dict[Text, Any]]]:
        """Transform intent properties for displaying or writing into a domain file.

        Internally, there is a property `entities_used` that lists all entities to be
        used. In domain files, `used_entities` or `entities_ignored` is used instead to
        list individual entities to ex- or include, because this is easier to read.

        Returns:
            The intent properties as they are used in domain files.
        """
        intent_props = copy.deepcopy(self.intent_props)
        convo_intents_for_file = []

        for name_of_intent, intent_props in intent_props.items():
            if (
                name_of_intent in convo.shared.core.constants.DEFAULT_INTENT  
                and name_of_intent not in self.overriden_default_convo_intents
            ):
                # Default convo_intents should be not dumped with the domain
                continue
            used_entities = set(intent_props[CONVO_USED_ENTITIES_KEY])
            entities_ignored = set(self.entities) - used_entities
            if len(used_entities) == len(self.entities):
                intent_props[CONVO_USE_ENTITIES_KEY] = True
            elif len(used_entities) <= len(self.entities) / 2:
                intent_props[CONVO_USE_ENTITIES_KEY] = list(used_entities)
            else:
                intent_props[CONVO_IGNORE_ENTITIES_KEY] = list(entities_ignored)
            intent_props.pop(CONVO_USED_ENTITIES_KEY)
            convo_intents_for_file.append({name_of_intent: intent_props})

        return convo_intents_for_file

    def clean_domain(self) -> Dict[Text, Any]:
        """Fetch cleaned domain to display or write into a file.

        The internal `entities_used` property is replaced by `use_entities` or
        `ignore_entities` and redundant keys are replaced with default values
        to make the domain easier readable.

        Returns:
            A cleaned dictionary version of the domain.
        """
        domain_data_set = self.as_dictionary()
        # remove e2e actions from domain before we display it
        domain_data_set.pop(E2E_ACTIONS_KEY, None)

        for idx, intent_info in enumerate(domain_data_set[convo_intents_KEY]):
            for name, intent in intent_info.items():  # pytype: disable=attribute-error
                if intent.get(CONVO_USE_ENTITIES_KEY) is True:
                    del intent[CONVO_USE_ENTITIES_KEY]
                if not intent.get(CONVO_IGNORE_ENTITIES_KEY):
                    intent.pop(CONVO_IGNORE_ENTITIES_KEY, None)
                if len(intent) == 0:
                    domain_data_set[convo_intents_KEY][idx] = name

        for slot in domain_data_set[SLOTS_KEY].values():  # pytype: disable=attribute-error
            if slot["initial_value"] is None:
                del slot["initial_value"]
            if slot["auto_fill"]:
                del slot["auto_fill"]
            if slot["type"].startswith("convo.shared.core.slots"):
                slot["type"] = Slot.resolved_by_type(slot["type"]).type_name

        if domain_data_set["config"]["store_entities_as_slots"]:
            del domain_data_set["config"]["store_entities_as_slots"]

        # clean empty keys
        return {
            k: v
            for k, v in domain_data_set.items()
            if v != {} and v != [] and v is not None
        }

    def persist(self, filename: Union[Text, Path]) -> None:
        """Write domain to a file."""
        as_yaml = self.yaml_as(clean_before_dump=False)
        convo.shared.utils.io.writing_text_file(as_yaml, filename)

    def persist_trash(self, filename: Union[Text, Path]) -> None:
        """Write cleaned domain to a file."""
        as_yaml = self.yaml_as(clean_before_dump=True)
        convo.shared.utils.io.writing_text_file(as_yaml, filename)

    def yaml_as(self, clean_before_dump: bool = False) -> Text:
        if clean_before_dump:
            domain_data: Dict[Text, Any] = self.clean_domain()
        else:
            domain_data: Dict[Text, Any] = self.as_dictionary()

        domain_data[
            KEY_TRAINING_DATA_FORMAT_VER
        ] = f"{convo.shared.constants.TRAINING_DATA_LATEST_FORMAT_VERSION }"

        return convo.shared.utils.io.dump_object_as_yaml_to_str(
            domain_data, should_preserve_key_order=True
        )

    def intent_configuration(self, name_of_intent: Text) -> Dict[Text, Any]:
        """Return the configuration for an intent."""
        return self.intent_props.get(name_of_intent, {})

    @convo.shared.utils.common.lazy_property
    def fetch_intents(self):
        return sorted(self.intent_props.keys())

    @property
    def slot_for_doman_warnings(self) -> List[Text]:
        """Fetch names of convo_slotsthat are used in domain warnings.

        Excludes convo_slotswhich aren't featurized.
        """

        return [s.name for s in self.slots if s.influence_conversation]

    @property
    def action_for_domain_warnings(self) -> List[Text]:
        """Fetch names of actions that are used in domain warnings.

        Includes user and form actions, but excludes those that are default actions.
        """

        return [
            a
            for a in self.user_forms_and_actions
            if a not in convo.shared.core.constants.DEFAULT_ACTION_NAME   
        ]

    @staticmethod
    def get_symmetrical_diff(
        domain_elements: Union[List[Text], Set[Text]],
        elements_for_training_data: Optional[Union[List[Text], Set[Text]]],
    ) -> Dict[Text, Set[Text]]:
        """Get symmetric difference between a set of domain elements and a set of
        training data elements.

        Returns a dictionary containing a list of items found in the `domain_elements`
        but not in `training_data_elements` at key `in_domain`, and a list of items
        found in `training_data_elements` but not in `domain_elements` at key
        `in_training_data_set`.
        """

        if elements_for_training_data is None:
            elements_for_training_data = set()

        in_domain_difference = set(domain_elements) - set(elements_for_training_data)
        in_training_data_difference = set(elements_for_training_data) - set(domain_elements)

        return {"in_domain": in_domain_difference, "in_training_data": in_training_data_difference}

    @staticmethod
    def merge_with_templates(
        actions: List[Text], templates: Dict[Text, Any]
    ) -> List[Text]:
        """Combines actions with utter actions listed in responses section."""
        unique_template_names = [
            a for a in sorted(list(templates.keys())) if a not in actions
        ]
        return actions + unique_template_names

    @staticmethod
    def merge_user_with_default_actions(user_actions: List[Text]) -> List[Text]:
        # remove all user actions that overwrite default actions
        # this logic is a bit reversed, you'd think that we should remove
        # the action name from the default action names if the user overwrites
        # the action, but there are some locations in the code where we
        # implicitly assume that e.g. "action_listen" is always at location
        # 0 in this array. to keep it that way, we remove the duplicate
        # action names from the users list instead of the defaults
        distict_user_actions = [
            a
            for a in user_actions
            if a not in convo.shared.core.constants.DEFAULT_ACTION_NAME   
        ]
        return convo.shared.core.constants.DEFAULT_ACTION_NAME    + distict_user_actions

    def warnings_for_domain(
        self,
        convo_intents: Optional[Union[List[Text], Set[Text]]] = None,
        entities: Optional[Union[List[Text], Set[Text]]] = None,
        actions: Optional[Union[List[Text], Set[Text]]] = None,
        slots: Optional[Union[List[Text], Set[Text]]] = None,
    ) -> Dict[Text, Dict[Text, Set[Text]]]:
        """Generate domain warnings from convo_intents, entities, actions and slots.

        Returns a dictionary with entries for `warnings_for_intent`,
        `warnings_for_entity`, `warnings_for_action` and `warnings_for_slot`. Excludes domain slots
        from domain warnings in case they are not featurized.
        """

        warnings_for_intent= self.get_symmetrical_diff(self.fetch_intents, convo_intents)
        warnings_for_entity = self.get_symmetrical_diff(self.entities, entities)
        warnings_for_action = self.get_symmetrical_diff(
            self.action_for_domain_warnings, actions
        )
        warnings_for_slot = self.get_symmetrical_diff(
            self.slot_for_doman_warnings, slots
        )

        return {
            "warnings_for_intent": warnings_for_intent,
            "warnings_for_entity": warnings_for_entity,
            "warnings_for_action": warnings_for_action,
            "warnings_for_slot": warnings_for_slot,
        }

    def domain_sanity_check(self) -> None:
        """Make sure the domain is properly configured.
        If the domain contains any duplicate slots, convo_intents, actions
        or entities, an InvalidDomain error is raised.  This error
        is also raised when intent-action mappings are incorrectly
        named or an utterance template is missing."""

        def get_identical(my_items):
            """Returns a list of duplicate items in my_items."""

            return [
                item
                for item, count in collections.Counter(my_items).items()
                if count > 1
            ]

        def mappings_check(
            intent_props: Dict[Text, Dict[Text, Union[bool, List]]]
        ) -> List[Tuple[Text, Text]]:
            """Check whether intent-action mappings use proper action names."""

            not_coorect = []
            for intent, properties in intent_props.items():
                if "triggers" in properties:
                    triggered_action = properties.get("triggers")
                    if triggered_action not in self.action_names:
                        not_coorect.append((intent, str(triggered_action)))
            return not_coorect

        def get_exception_msg(
            identical: Optional[List[Tuple[List[Text], Text]]] = None,
            mappings: List[Tuple[Text, Text]] = None,
        ):
            """Return a msg given a list of error locations."""

            msg = ""
            if identical:
                msg += get_duplicate_exception_msg(identical)
            if mappings:
                if msg:
                    msg += "\n"
                msg += get_mapping_exception_msg(mappings)
            return msg

        def get_mapping_exception_msg(mappings: List[Tuple[Text, Text]]):
            """Return a msg given a list of identical."""

            msg = ""
            for name, action_name in mappings:
                if msg:
                    msg += "\n"
                msg += (
                    "Intent '{}' is set to trigger action '{}', which is "
                    "not defined in the domain.".format(name, action_name)
                )
            return msg

        def get_duplicate_exception_msg(
            identical: List[Tuple[List[Text], Text]]
        ) -> Text:
            """Return a msg given a list of identical."""

            message = ""
            for d, name in identical:
                if d:
                    if message:
                        message += "\n"
                    message += (
                        f"Duplicate {name} in domain. "
                        f"These {name} occur more than once in "
                        f"the domain: '{', '.join(d)}'."
                    )
            return message

        identical_actions = get_identical(self.action_names)
        duplicate_slots = get_identical([s.name for s in self.slots])
        identical_entities = get_identical(self.entities)
        mappings_incorrect = mappings_check(self.intent_props)

        if (
            identical_actions
            or duplicate_slots
            or identical_entities
            or mappings_incorrect
        ):
            raise InvalidDomain(
                get_exception_msg(
                    [
                        (identical_actions, ACTIONS_KEY),
                        (duplicate_slots, SLOTS_KEY),
                        (identical_entities, ENTITIES_KEY),
                    ],
                    mappings_incorrect,
                )
            )

    def missing_templates_check(self) -> None:
        """Warn user of utterance names which have no specified template."""

        utter = [
            a
            for a in self.action_names
            if a.startswith(convo.shared.constants.CONVO_UTTER_PREFIX )
        ]

        templates_missing = [t for t in utter if t not in self.templates.keys()]

        if templates_missing:
            for template in templates_missing:
                convo.shared.utils.io.raising_warning(
                    f"Action '{template}' is listed as a "
                    f"response action in the domain file, but there is "
                    f"no matching response defined. Please "
                    f"check your domain.",
                    docs=convo.shared.constants.RESPONSE_DOCUMENTS_URL,
                )

    def is_empty(self) -> bool:
        """Check whether the domain is empty."""
        return self.as_dictionary() == Domain.empty().as_dictionary()

    @staticmethod
    def domain_file_check(filename: Text) -> bool:
        """Checks whether the given file path is a Convo domain file.

        Args:
            filename: Path of the file which should be checked.

        Returns:
            `True` if it's a domain file, otherwise `False`.

        Raises:
            YamlExceptions : if the file seems to be a YAML file (extension) but
                can not be read / parsed.
        """
        from convo.shared.data import is_yaml_file 

        if not is_yaml_file (filename):
            return False

        data_content = convo.shared.utils.io.reading_yaml_file(filename)
        return any(key in data_content for key in DOMAIN_KEYS)

    def form_of_slot_mapping(self, form_name: Text) -> Dict[Text, Any]:
        """Retrieve the slot mappings for a form which are defined in the domain.

        Options:
        - an extracted entity
        - intent: value pairs
        - trigger_intent: value pairs
        - a whole message
        or a list of them, where the first match will be picked

        Args:
            form_name: The name of the form.

        Returns:
            The slot mapping or an empty dictionary in case no mapping was found.
        """
        return self.forms.get(form_name, {})
