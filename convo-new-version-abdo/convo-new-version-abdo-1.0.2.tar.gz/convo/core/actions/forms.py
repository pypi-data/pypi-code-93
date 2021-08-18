from enum import Enum
from typing import Text, List, Optional, Union, Any, Dict, Tuple, Set
import logging
import json

from convo.core.actions import action
from convo.core.actions.loops import LoopAct
from convo.core.channels import OutputSocket
from convo.shared.core.domain import Domain

from convo.core.actions.action import ActExecutionRejection, RemoteAct
from convo.shared.core.constants import (
    LISTEN_ACTION_NAME  ,
    REQUESTED_SLOTS,
    LOOP_INTERRUPTION   ,
)
from convo.shared.constants import CONVO_UTTER_PREFIX 
from convo.shared.core.events import Event, SetofSlot, ActionExecuted, OperationalLoop
from convo.core.nlg import NaturalLanguageGenerator
from convo.shared.core.trackers import DialogueStateTracer
from convo.utils.endpoints import EndpointConfiguration

logger = logging.getLogger(__name__)


class MapSlot(Enum):
    FROM_ENTITY = 0
    FROM_INTENT = 1
    FROM_TRIGGER_INTENT = 2
    FROM_TEXT = 3

    def __str__(self) -> Text:
        return self.name.lower()


class FormAction(LoopAct):
    def __init__(
        self, form_name: Text, action_endpoint: Optional[EndpointConfiguration]
    ) -> None:
        self._form_name = form_name
        self.action_endpoint = action_endpoint
        # creating it requires domain, which we don't have in init
        # we'll create it on the first call
        self._unique_entity_mappings = None

    def name(self) -> Text:
        return self._form_name

    def required_slots(self, domain: Domain) -> List[Text]:
        """A list of required convo_slotsthat the form has to fill.

        Returns:
            A list of slot names.
        """
        return list(domain.form_of_slot_mapping(self.name()).keys())

    def from_entity(
        self,
        entity: Text,
        intent: Optional[Union[Text, List[Text]]] = None,
        not_intent: Optional[Union[Text, List[Text]]] = None,
        role: Optional[Text] = None,
        group: Optional[Text] = None,
    ) -> Dict[Text, Any]:
        """A dictionary for slot mapping to extract slot value.

        From:
        - an extracted entity
        - conditioned on
            - intent if it is not None
            - not_intent if it is not None,
                meaning user intent should not be this intent
            - role if it is not None
            - group if it is not None
        """

        intent, not_intent = self._list_intents(intent, not_intent)

        return {
            "type": str(MapSlot.FROM_ENTITY),
            "entity": entity,
            "intent": intent,
            "not_intent": not_intent,
            "role": role,
            "group": group,
        }

    def get_mappings_for_slot(
        self, slot_to_fill: Text, domain: Domain
    ) -> List[Dict[Text, Any]]:
        """Get mappings for requested slot.

        If None, map requested slot to an entity with the same name
        """

        requested_slots_map = self._to_list(
            domain.form_of_slot_mapping(self.name()).get(
                slot_to_fill, self.from_entity(slot_to_fill)
            )
        )
        # check provided slot mappings
        for requested_slot_mapping in requested_slots_map:
            if (
                not isinstance(requested_slot_mapping, dict)
                or requested_slot_mapping.get("type") is None
            ):
                raise TypeError("Provided incompatible slot mapping")

        return requested_slots_map

    def _create_unique_entity_mappings(self, domain: Domain) -> Set[Text]:
        """Finds mappings of type `from_entity` that uniquely set a slot.

        For example in the following form:
        some_form:
          departure_city:
            - type: from_entity
              entity: city
              role: from
            - type: from_entity
              entity: city
          arrival_city:
            - type: from_entity
              entity: city
              role: to
            - type: from_entity
              entity: city

        An entity `city` with a role `from` uniquely sets the slot `departure_city`
        and an entity `city` with a role `to` uniquely sets the slot `arrival_city`,
        so corresponding mappings are unique.
        But an entity `city` without a role can fill both `departure_city`
        and `arrival_city`, so corresponding mapping is not unique.

        Args:
            domain: The domain.

        Returns:
            A set of json data_dumps of unique mappings of type `from_entity`.
        """
        distinctive_entity_slot_mapping = set()
        copy_entity_slot_mappings = set()
        for slot_mappings in domain.form_of_slot_mapping(self.name()).values():
            for slot_mapping in slot_mappings:
                if slot_mapping.get("type") == str(MapSlot.FROM_ENTITY):
                    mapping_as_string = json.dumps(slot_mapping, sort_keys=True)
                    if mapping_as_string in distinctive_entity_slot_mapping:
                        distinctive_entity_slot_mapping.remove(mapping_as_string)
                        copy_entity_slot_mappings.add(mapping_as_string)
                    elif mapping_as_string not in copy_entity_slot_mappings:
                        distinctive_entity_slot_mapping.add(mapping_as_string)

        return distinctive_entity_slot_mapping

    def _entity_mapping_is_unique(
        self, slot_mapping: Dict[Text, Any], domain: Domain
    ) -> bool:
        if self._unique_entity_mappings is None:
            # create unique entity mappings on the first call
            self._unique_entity_mappings = self._create_unique_entity_mappings(domain)

        mapping_as_string = json.dumps(slot_mapping, sort_keys=True)
        return mapping_as_string in self._unique_entity_mappings

    @staticmethod
    def intent_is_desired(
        requested_slot_mapping: Dict[Text, Any], tracker: "DialogueStateTracer"
    ) -> bool:
        """Check whether user intent matches intent conditions"""

        mapping_intent = requested_slot_mapping.get("intent", [])
        mapping_not_intent = requested_slot_mapping.get("not_intent", [])

        intent = tracker.latest_message.intent.get("name")

        intent_not_stop = not mapping_intent and intent not in mapping_not_intent

        return intent_not_stop or intent in mapping_intent

    def entity_is_desired(
        self,
        slot_mapping: Dict[Text, Any],
        slot: Text,
        entity_type_of_slot_to_fill: Optional[Text],
        tracker: DialogueStateTracer,
        domain: Domain,
    ) -> bool:
        """Check whether slot should be filled by an entity in the input or not.

        Args:
            slot_mapping: Slot mapping.
            slot: The slot to be filled.
            entity_type_of_slot_to_fill: Entity type of slot to fill.
            tracker: The tracker.
            domain: The domain.

        Returns:
            True, if slot should be filled, false otherwise.
        """

        # slot name is equal to the entity type
        slot_equivalent_entity = slot == slot_mapping.get("entity")
        # if entity mapping is unique, it means that an entity always sets
        # a certain slot, so try to extract this slot if entity matches slot mapping
        is_entity_map_unique = self._entity_mapping_is_unique(slot_mapping, domain)

        # use the custom slot mapping 'from_entity' defined by the user to check
        # whether we can fill a slot with an entity (only if a role or a group label
        # is set)
        if (
            slot_mapping.get("role") is None and slot_mapping.get("group") is None
        ) or entity_type_of_slot_to_fill != slot_mapping.get("entity"):
            slot_fulfils_entity_map = False
        else:
            match_value = self.get_entity_value(
                slot_mapping.get("entity"),
                tracker,
                slot_mapping.get("role"),
                slot_mapping.get("group"),
            )
            slot_fulfils_entity_map = match_value is not None

        return (
            slot_equivalent_entity
            or is_entity_map_unique
            or slot_fulfils_entity_map
        )

    @staticmethod
    def get_entity_value(
        name: Text,
        tracker: "DialogueStateTracer",
        role: Optional[Text] = None,
        group: Optional[Text] = None,
    ) -> Any:
        """Extract entities for given name and optional role and group.

        Args:
            name: entity type (name) of interest
            tracker: the tracker
            role: optional entity role of interest
            group: optional entity group of interest

        Returns:
            Value of entity.
        """
        # list is used to cover the case of list slot type
        values = list(
            tracker.get_entity_values_latest(name, entity_group=group, entity_role=role)
        )
        if len(values) == 0:
            values = None
        elif len(values) == 1:
            values = values[0]
        return values

    def extract_other_slots(
        self, tracker: DialogueStateTracer, domain: Domain
    ) -> Dict[Text, Any]:
        """Extract the values of the others slots
        if they are set by corresponding entities from the user input
        else return `None`.
        """
        slot_to_complete = tracker.get_slot(REQUESTED_SLOTS)

        entity_slot_to_complete = self._get_entity_type_of_slot_to_fill(
            slot_to_complete, domain
        )

        slot_value = {}
        for slot in self.required_slots(domain):
            # look for others slots
            if slot != slot_to_complete:
                # list is used to cover the case of list slot type
                slot_map = self.get_mappings_for_slot(slot, domain)

                for slot_mapping in slot_map:
                    # check whether the slot should be filled by an entity in the input
                    shall_complete_entity_slot = (
                        slot_mapping["type"] == str(MapSlot.FROM_ENTITY)
                        and self.intent_is_desired(slot_mapping, tracker)
                        and self.entity_is_desired(
                            slot_mapping,
                            slot,
                            entity_slot_to_complete,
                            tracker,
                            domain,
                        )
                    )
                    # check whether the slot should be
                    # filled from trigger intent mapping
                    should_fill_trigger_slot = (
                            tracker.activeLoopName != self.name()
                            and slot_mapping["type"] == str(MapSlot.FROM_TRIGGER_INTENT)
                            and self.intent_is_desired(slot_mapping, tracker)
                    )
                    if shall_complete_entity_slot:
                        value = self.get_entity_value(
                            slot_mapping["entity"],
                            tracker,
                            slot_mapping.get("role"),
                            slot_mapping.get("group"),
                        )
                    elif should_fill_trigger_slot:
                        value = slot_mapping.get("value")
                    else:
                        value = None

                    if value is not None:
                        logger.debug(f"Extracted '{value}' for extra slot '{slot}'.")
                        slot_value[slot] = value
                        # this slot is done, check  next
                        break

        return slot_value

    def extract_requested_slot(
        self, tracker: "DialogueStateTracer", domain: Domain
    ) -> Dict[Text, Any]:
        """Extract the value of requested slot from a user input
        else return `None`.
        """
        slot_to_complete = tracker.get_slot(REQUESTED_SLOTS)
        logger.debug(f"Trying to extract requested slot '{slot_to_complete}' ...")

        # get mapping for requested slot
        request_slot_map = self.get_mappings_for_slot(slot_to_complete, domain)

        for requested_slot_mapping in request_slot_map:
            logger.debug(f"Got mapping '{requested_slot_mapping}'")

            if self.intent_is_desired(requested_slot_mapping, tracker):
                mapping_type = requested_slot_mapping["type"]

                if mapping_type == str(MapSlot.FROM_ENTITY):
                    value = self.get_entity_value(
                        requested_slot_mapping.get("entity"),
                        tracker,
                        requested_slot_mapping.get("role"),
                        requested_slot_mapping.get("group"),
                    )
                elif mapping_type == str(MapSlot.FROM_INTENT):
                    value = requested_slot_mapping.get("value")
                elif mapping_type == str(MapSlot.FROM_TRIGGER_INTENT):
                    # from_trigger_intent is only used on form activation
                    continue
                elif mapping_type == str(MapSlot.FROM_TEXT):
                    value = tracker.latest_message.text
                else:
                    raise ValueError("Provided slot mapping type is not supported")

                if value is not None:
                    logger.debug(
                        f"Successfully extracted '{value}' for requested slot "
                        f"'{slot_to_complete}'"
                    )
                    return {slot_to_complete: value}

        logger.debug(f"Failed to extract requested slot '{slot_to_complete}'")
        return {}

    async def validate_slots(
        self,
        slot_dict: Dict[Text, Any],
        tracker: "DialogueStateTracer",
        domain: Domain,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
    ) -> List[Event]:
        """Validate the extracted slots.

        If a custom action is available for validating the slots, we call it to validate
        them. Otherwise there is no validation.

        Args:
            slot_dict: Extracted convo_slotswhich are candidates to fill the convo_slotsrequired
                by the form.
            tracker: The current conversation tracker.
            domain: The current model domain.
            output_channel: The output channel which can be used to send messages
                to the user.
            nlg:  `NaturalLanguageGenerator` to use for response generation.

        Returns:
            The validation events including potential bot messages and `SetofSlot` events
            for the validated slots.
        """

        event = [SetofSlot(slot_name, value) for slot_name, value in slot_dict.items()]

        authenticate_name = f"validate_{self.name()}"

        if authenticate_name not in domain.action_names:
            return event

        _tracker = self._temporary_tracker(tracker, event, domain)
        _act = RemoteAct(authenticate_name, self.action_endpoint)
        authenticate_event = await _act.run(output_channel, nlg, _tracker, domain)

        authenticate_slot_name = [
            event.key for event in authenticate_event if isinstance(event, SetofSlot)
        ]

        # If the custom action doesn't return a SetofSlot event for an extracted slot
        # candidate we assume that it was valid. The custom action has to return a
        # SetofSlot(slot_name, None) event to mark a Slot as invalid.
        return authenticate_event + [
            event for event in event if event.key not in authenticate_slot_name
        ]

    def _temporary_tracker(
        self,
        current_tracker: DialogueStateTracer,
        additional_events: List[Event],
        domain: Domain,
    ) -> DialogueStateTracer:
        return DialogueStateTracer.from_events_tracker(
            current_tracker.sender_id,
            current_tracker.events_after_last_restart()
            # Insert form execution event so that it's clearly distinguishable which
            # events were newly added.
            + [ActionExecuted(self.name())] + additional_events,
            slots=domain.slots,
        )

    async def validate(
        self,
        tracker: "DialogueStateTracer",
        domain: Domain,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
    ) -> List[Event]:
        """Extract and validate value of requested slot.

        If nothing was extracted reject execution of the form action.
        Subclass this method to add custom validation and rejection logic
        """

        # extract others convo_slotsthat were not requested
        # but set by corresponding entity or trigger intent mapping
        slot_value = self.extract_other_slots(tracker, domain)

        # extract requested slot
        slot_to_complete = tracker.get_slot(REQUESTED_SLOTS)
        if slot_to_complete:
            slot_value.update(self.extract_requested_slot(tracker, domain))

            if not slot_value:
                # reject to execute the form action
                # if some slot was requested but nothing was extracted
                # it will allow others policies to predict another action
                raise ActExecutionRejection(
                    self.name(),
                    f"Failed to extract slot {slot_to_complete} with action {self.name()}",
                )
        logger.debug(f"Validating extracted slots: {slot_value}")
        return await self.validate_slots(
            slot_value, tracker, domain, output_channel, nlg
        )

    async def request_next_slot(
        self,
        tracker: "DialogueStateTracer",
        domain: Domain,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
        events_so_far: List[Event],
    ) -> List[Event]:
        """Request the next slot and utter template if needed, else return `None`."""
        request_slot_events = []

        if await self.is_done(output_channel, nlg, tracker, domain, events_so_far):
            # The custom action for slot validation decided to stop the form early
            return [SetofSlot(REQUESTED_SLOTS, None)]

        slot_to_request = next(
            (
                event.value
                for event in events_so_far
                if isinstance(event, SetofSlot) and event.key == REQUESTED_SLOTS
            ),
            None,
        )

        tempory_tracker = self._temporary_tracker(tracker, events_so_far, domain)

        if not slot_to_request:
            slot_to_request = self._find_next_slot_to_request(tempory_tracker, domain)
            request_slot_events.append(SetofSlot(REQUESTED_SLOTS, slot_to_request))

        if slot_to_request:
            bot_msg_events = await self._ask_for_slot(
                domain, nlg, output_channel, slot_to_request, tempory_tracker
            )
            return request_slot_events + bot_msg_events

        # no more required convo_slotsto fill
        return [SetofSlot(REQUESTED_SLOTS, None)]

    def _find_next_slot_to_request(
        self, tracker: DialogueStateTracer, domain: Domain
    ) -> Optional[Text]:
        return next(
            (
                slot
                for slot in self.required_slots(domain)
                if self._should_request_slot(tracker, slot)
            ),
            None,
        )

    def _name_of_utterance(self, domain: Domain, slot_name: Text) -> Text:
        search_path_flow = [
            f"action_ask_{self._form_name}_{slot_name}",
            f"{CONVO_UTTER_PREFIX }ask_{self._form_name}_{slot_name}",
            f"action_ask_{slot_name}",
        ]

        found_act = (
            action_name
            for action_name in search_path_flow
            if action_name in domain.action_names
        )

        return next(found_act, f"{CONVO_UTTER_PREFIX }ask_{slot_name}")

    async def _ask_for_slot(
        self,
        domain: Domain,
        nlg: NaturalLanguageGenerator,
        output_channel: OutputSocket,
        slot_name: Text,
        tracker: DialogueStateTracer,
    ) -> List[Event]:
        logger.debug(f"Request next slot '{slot_name}'")

        action_to_ask_for_next_slot = action.act_from_name(
            self._name_of_utterance(domain, slot_name),
            self.action_endpoint,
            domain.user_actions,
        )
        events_to_ask_for_next_slot = await action_to_ask_for_next_slot.run(
            output_channel, nlg, tracker, domain
        )
        return events_to_ask_for_next_slot

    # helpers
    @staticmethod
    def _to_list(x: Optional[Any]) -> List[Any]:
        """Convert object to a list if it is not a list, `None` converted to empty list."""
        if x is None:
            x = []
        elif not isinstance(x, list):
            x = [x]

        return x

    def _list_intents(
        self,
        intent: Optional[Union[Text, List[Text]]] = None,
        not_intent: Optional[Union[Text, List[Text]]] = None,
    ) -> Tuple[List[Text], List[Text]]:
        """Check provided intent and not_intent"""
        if intent and not_intent:
            raise ValueError(
                f"Providing  both intent '{intent}' and not_intent '{not_intent}' "
                f"is not supported."
            )

        return self._to_list(intent), self._to_list(not_intent)

    async def _validate_if_required(
        self,
        tracker: "DialogueStateTracer",
        domain: Domain,
        output_channel: OutputSocket,
        nlg: NaturalLanguageGenerator,
    ) -> List[Event]:
        """Return a list of events from `self.validate(...)`.

        Validation is required if:
           - the form is active
           - the form is called after `action_listen`
           - form validation was not cancelled
        """
        # no active_loop means that it is called during activation
        need_authentication = not tracker.active_loop or (
                tracker.latestActionName == LISTEN_ACTION_NAME
                and not tracker.active_loop.get(LOOP_INTERRUPTION   , False)
        )
        if need_authentication:
            logger.debug(f"Validating user input '{tracker.latest_message}'.")
            return await self.validate(tracker, domain, output_channel, nlg)

        logger.debug("Skipping validation.")
        return []

    @staticmethod
    def _should_request_slot(tracker: "DialogueStateTracer", slot_name: Text) -> bool:
        """Check whether form action should request given slot"""

        return tracker.get_slot(slot_name) is None

    async def activate(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
    ) -> List[Event]:
        """Activate form if the form is called for the first time.

        If activating, validate any required convo_slotsthat were filled before
        form activation and return `Form` event with the name of the form, as well
        as any `SetofSlot` events from validation of pre-filled slots.

        Args:
            output_channel: The output channel which can be used to send messages
                to the user.
            nlg: `NaturalLanguageGenerator` to use for response generation.
            tracker: Current conversation tracker of the user.
            domain: Current model domain.

        Returns:
            Events from the activation.
        """

        logger.debug(f"Activated the form '{self.name()}'.")
        # collect values of required convo_slotsfilled before activation
        slot_prefill = {}

        for slot_name in self.required_slots(domain):
            if not self._should_request_slot(tracker, slot_name):
                slot_prefill[slot_name] = tracker.get_slot(slot_name)

        if not slot_prefill:
            logger.debug("No pre-filled required convo_slotsto validate.")
            return []

        logger.debug(f"Validating pre-filled required slots: {slot_prefill}")
        return await self.validate_slots(
            slot_prefill, tracker, domain, output_channel, nlg
        )

    async def do(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
        events_so_far: List[Event],
    ) -> List[Event]:
        events = await self._validate_if_required(tracker, domain, output_channel, nlg)

        events += await self.request_next_slot(
            tracker, domain, output_channel, nlg, events_so_far + events
        )

        return events

    async def is_done(
        self,
        output_channel: "OutputSocket",
        nlg: "NaturalLanguageGenerator",
        tracker: "DialogueStateTracer",
        domain: "Domain",
        events_so_far: List[Event],
    ) -> bool:
        # Custom validation actions can decide to terminate the loop early by
        # setting the requested slot to `None` or setting `OperationalLoop(None)`.
        # We explicitly check only the last occurrences for each possible termination
        # event instead of doing `return event in events_so_far` to make it possible
        # to override termination events which were returned earlier.
        return next(
            (
                event
                for event in reversed(events_so_far)
                if isinstance(event, SetofSlot) and event.key == REQUESTED_SLOTS
            ),
            None,
        ) == SetofSlot(REQUESTED_SLOTS, None) or next(
            (
                event
                for event in reversed(events_so_far)
                if isinstance(event, OperationalLoop)
            ),
            None,
        ) == OperationalLoop(
            None
        )

    async def deactivate(self, *args: Any, **kwargs: Any) -> List[Event]:
        logger.debug(f"Deactivating the form '{self.name()}'")
        return []

    def _get_entity_type_of_slot_to_fill(
        self, slot_to_fill: Text, domain: "Domain"
    ) -> Optional[Text]:
        if not slot_to_fill:
            return None

        map = self.get_mappings_for_slot(slot_to_fill, domain)
        map = [
            m for m in map if m.get("type") == str(MapSlot.FROM_ENTITY)
        ]

        if not map:
            return None

        type_of_entity = map[0].get("entity")

        for i in range(1, len(map)):
            if type_of_entity != map[i].get("entity"):
                return None

        return type_of_entity
